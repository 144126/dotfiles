# shrink_phonon.py [out_dir]: rebuild Phonon 31m (gradium/phonon-31m-en) as a 43 MB GGUF from its original weights, streamed from Hugging Face
import json, os, re, struct, sys, urllib.request
import numpy as np

REV = '8c64b55ec301728e2d1695bfea87a08a267d0c2d'
HUB = f'https://huggingface.co/gradium/phonon-31m-en/resolve/{REV}/'
SNAP = os.path.expanduser(f'~/models/huggingface/hub/models--gradium--phonon-31m-en/snapshots/{REV}/')
# first match wins; the lowest bits that keep the voice inside the original's take-to-take spread (~/search/shrink-voice-models-weight-space-root.md)
RULES = [(r'flow_lm\.transformer\.', 'Q8_0'), (r'res_blocks', 'Q5_K'), (r'flow_net\.(time_embed|final_layer|cond_embed)', 'Q8_0'),
         (r'conditioners', 'Q8_0'), (r'decoder_transformer', 'Q6_K')]
f32, f16 = np.float32, np.float16


def inv(a):
    return np.divide(1, a, out=np.zeros_like(a), where=a != 0)


def q8_0(x):
    b = x.reshape(-1, 32)
    d = (np.abs(b).max(1) / 127).astype(f16)
    q = np.clip(np.rint(b * inv(d.astype(f32))[:, None]), -127, 127).astype(np.int8)
    return np.concatenate([d.view(np.uint8).reshape(-1, 2), q.view(np.uint8)], 1).tobytes()


def sym_scales(b, nmax):
    # llama.cpp make_qx_quants(rmse_type=1): signed scale per row, q in [-nmax, nmax-1]
    mx = b[np.arange(len(b)), np.abs(b).argmax(1)]
    w = b * b
    best, scale = np.full(len(b), -1.0), np.zeros(len(b))
    for k in [0] + [i for i in range(-9, 10) if i]:
        l = np.clip(np.rint((-(nmax + 0.1 * k) * inv(mx))[:, None] * b), -nmax, nmax - 1)
        slx, sl2 = (w * b * l).sum(1), (w * l * l).sum(1)
        s = slx * inv(sl2)
        upd = (sl2 > 0) & (s * slx > best)
        best, scale = np.where(upd, s * slx, best), np.where(upd, s, scale)
    return scale


def asym_scales(b, nmax, rmin, rdelta, nstep):
    # llama.cpp make_qkx2_quants: x ~ s*q - m per row, s >= 0, m >= 0, q in [0, nmax]
    w = np.sqrt((b * b).mean(1, keepdims=True)) + np.abs(b)
    mn, mx = np.minimum(b.min(1), 0), b.max(1)
    sw, sx, rng = w.sum(1), (w * b).sum(1), inv(mx - mn)
    def err(s, m, l): return (w * (s[:, None] * l + m[:, None] - b) ** 2).sum(1)
    scale, minv = (mx - mn) / nmax, mn.copy()
    best = err(scale, minv, np.clip(np.rint(nmax * rng[:, None] * (b - mn[:, None])), 0, nmax))
    for k in range(nstep + 1):
        l = np.clip(np.rint(((rmin + rdelta * k + nmax) * rng)[:, None] * (b - mn[:, None])), 0, nmax)
        sl, sl2, sxl = (w * l).sum(1), (w * l * l).sum(1), (w * l * b).sum(1)
        D = sw * sl2 - sl * sl
        s, m = (sw * sxl - sx * sl) * inv(D), (sl2 * sx - sl * sxl) * inv(D)
        s, m = np.where(m > 0, sxl * inv(sl2), s), np.minimum(m, 0)
        e = err(s, m, l)
        upd = (D > 0) & (e < best)
        best, scale, minv = np.where(upd, e, best), np.where(upd, s, scale), np.where(upd, m, minv)
    return np.maximum(scale, 0), -minv


def q6_k(x):
    b = x.reshape(-1, 16, 16).astype(np.float64)
    s = sym_scales(b.reshape(-1, 16), 32).reshape(-1, 16)
    ms = s[np.arange(len(s)), np.abs(s).argmax(1)]
    d = (-ms / 128).astype(f16)
    ls = np.minimum(127, np.rint(-128 * inv(ms)[:, None] * s))
    U = (np.clip(np.rint(b * inv(d.astype(f32)[:, None] * ls)[..., None]), -32, 31) + 32).astype(np.uint8).reshape(-1, 2, 4, 32)
    ql = np.stack([U[:, :, j] & 15 | (U[:, :, j + 2] & 15) << 4 for j in (0, 1)], 2).reshape(-1, 128)
    qh = (U[:, :, 0] >> 4 | (U[:, :, 1] >> 4) << 2 | (U[:, :, 2] >> 4) << 4 | (U[:, :, 3] >> 4) << 6).reshape(-1, 64)
    return np.concatenate([ql, qh, ls.astype(np.int8).view(np.uint8), d.view(np.uint8).reshape(-1, 2)], 1).tobytes()


def q5_k(x):
    # 8 sub-blocks of 32 with 6-bit scales and mins
    b = x.reshape(-1, 8, 32).astype(np.float64)
    s, m = (a.reshape(-1, 8) for a in asym_scales(b.reshape(-1, 32), 31, -0.5, 0.1, 15))
    d, dm = (s.max(1) / 63).astype(f16), (m.max(1) / 63).astype(f16)
    ls = np.clip(np.rint(s * inv(d.astype(f32))[:, None]), 0, 63).astype(np.uint8)
    lm = np.clip(np.rint(m * inv(dm.astype(f32))[:, None]), 0, 63).astype(np.uint8)
    es, em = d.astype(f32)[:, None] * ls, dm.astype(f32)[:, None] * lm
    q = np.clip(np.rint((b + em[..., None]) * inv(es)[..., None]), 0, 31).astype(np.uint8).reshape(-1, 4, 2, 32)
    sc = np.concatenate([ls[:, :4] | (ls[:, 4:] >> 4) << 6, lm[:, :4] | (lm[:, 4:] >> 4) << 6, (ls[:, 4:] & 15) | (lm[:, 4:] & 15) << 4], 1)
    qh = sum((q[:, c, h] >> 4) << (2 * c + h) for c in range(4) for h in (0, 1)).astype(np.uint8)
    qs = (q[:, :, 0] & 15 | (q[:, :, 1] & 15) << 4).reshape(-1, 128)
    return np.concatenate([d.view(np.uint8).reshape(-1, 2), dm.view(np.uint8).reshape(-1, 2), sc, qh, qs], 1).tobytes()


# name: (ggml type id, block size, packer)
TYPES = {'F32': (0, 1, lambda x: x.astype('<f4').tobytes()), 'F16': (1, 1, lambda x: x.astype('<f2').tobytes()),
         'Q8_0': (8, 32, q8_0), 'Q6_K': (14, 256, q6_k), 'Q5_K': (13, 256, q5_k)}


def weights():
    b = urllib.request.urlopen(HUB + 'model.safetensors').read()
    n, = struct.unpack_from('<Q', b)
    h = json.loads(b[8:8 + n])
    h.pop('__metadata__', None)
    for k, v in h.items():
        raw = b[8 + n + v['data_offsets'][0]:8 + n + v['data_offsets'][1]]
        x = (np.frombuffer(raw, '<u2').astype(np.uint32) << 16).view(f32) if v['dtype'] == 'BF16' else np.frombuffer(raw, '<f4')
        yield k, x.reshape(v['shape'])


def pick(k, x):
    # the runtime dequantizes any GGUF type on load, but blocks run along the last dim, so convs (last dim = kernel) stay F16
    if not k.endswith('.weight') or x.size < 16384:
        return 'F32'
    t = next((t for r, t in RULES if re.search(r, k)), 'F16')
    return t if x.shape[-1] % TYPES[t][1] == 0 else 'F16'


def main():
    out = os.path.expanduser(sys.argv[1] if len(sys.argv) > 1 else '~/models/phonon-31m-en-small')
    os.makedirs(out, exist_ok=True)
    for f in ('config.json', 'tokenizer.json', 'default-voice.safetensors'):
        if not os.path.exists(os.path.join(out, f)):
            if os.path.exists(SNAP + f):
                try:
                    os.link(os.path.realpath(SNAP + f), os.path.join(out, f))
                except OSError:
                    os.symlink(os.path.realpath(SNAP + f), os.path.join(out, f))
            else:
                urllib.request.urlretrieve(HUB + f, os.path.join(out, f))
    ts = [(k, x.shape[::-1], TYPES[t][0], TYPES[t][2](x)) for k, x in weights() for t in [pick(k, x)]]
    hdr, off = bytearray(b'GGUF' + struct.pack('<IQQ', 3, len(ts), 0)), 0
    for k, ne, ty, raw in ts:
        hdr += struct.pack('<Q', len(k.encode())) + k.encode() + struct.pack(f'<I{len(ne)}Q', len(ne), *ne) + struct.pack('<IQ', ty, off)
        off += -(-len(raw) // 32) * 32
    path = os.path.join(out, 'model.q8.gguf')
    with open(path + '.tmp', 'wb') as f:
        f.write(hdr + bytes(-len(hdr) % 32))
        for *_, raw in ts:
            f.write(raw + bytes(-len(raw) % 32))
    os.replace(path + '.tmp', path)
    print(path, os.path.getsize(path))


main()
