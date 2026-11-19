#!/usr/bin/env -S uv run --script --quiet
# /// script
# requires-python = ">=3.11"
# dependencies = ["onnxruntime==1.23.2", "numpy", "kaldi-native-fbank==1.21.3"]
# ///
# conformer.py <wav>: speech to text on this machine. Text to stdout.
# NeMo Conformer-small CTC, 4-bit weights (~/models/conformer-small): the same model and features as rope's ai call
# and pilotspan dictation, 11.57% WER on Ed's 18 clips. Native onnxruntime: 71 s of audio in about 2 s.
# Long takes are cut at the quietest 20 ms between 15 and 25 s: attention cost grows with the square of length.
import os, sys, subprocess
import numpy as np, onnxruntime as ort, kaldi_native_fbank as knf

D = os.path.expanduser("~/models/conformer-small/")
# any input format; Mod+Ctrl+E already records 16 kHz mono
pcm = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", sys.argv[1], "-ar", "16000", "-ac", "1", "-f", "s16le", "-"], capture_output=True, check=True).stdout, np.int16)

def pieces(x):
    at, F = 0, 320
    while len(x) - at > 25 * 16000:
        e = (x[at + 15 * 16000 : at + 25 * 16000].astype(np.float32) ** 2)
        e = e[: len(e) // F * F].reshape(-1, F).sum(1)
        cut = at + 15 * 16000 + int(e.argmin()) * F + F // 2
        yield x[at:cut]
        at = cut
    yield x[at:]

o = knf.FbankOptions()
o.frame_opts.dither = 0
o.frame_opts.snip_edges = False
o.frame_opts.samp_freq = 16000
o.mel_opts.num_bins = 80
toks = {int(i): s for s, i in (l.rsplit(" ", 1) for l in open(D + "tokens.txt", encoding="utf-8") if " " in l.strip())}
blank = max(toks)
so = ort.SessionOptions()
so.intra_op_num_threads = 4
s = ort.InferenceSession(D + "conformer-small-w4g32.onnx", so, providers=["CPUExecutionProvider"])
words = []
for p in pieces(pcm):
    if len(p) < 1600:
        continue
    f = knf.OnlineFbank(o)
    f.accept_waveform(16000, p.astype(np.float32))  # kaldi scale: raw int16 values
    f.input_finished()
    F = np.stack([f.get_frame(i) for i in range(f.num_frames_ready)])
    F = ((F - F.mean(0)) / (F.std(0) + 1e-5)).T[None].astype(np.float32)
    ids = s.run(None, {"audio_signal": F, "length": np.array([F.shape[2]], np.int64)})[0][0].argmax(-1)
    # greedy ctc: repeats and blanks dropped
    words.append("".join(toks[int(i)] for j, i in enumerate(ids) if i != blank and (j == 0 or i != ids[j - 1])).replace("▁", " ").strip())
print(" ".join(w for w in words if w))
