"""Kitten TTS 2 Pico (voice Eleanor), the on-device voice. int4 ONNX, 24 kHz, CPU, no torch.
Text front end (clauses, espeak-ng, Kokoro symbols) is leokani_onnx's; the model is Kitten's:
input_ids [0, *ids, 10, 0], style row = token count, speed -> waveform, durations; end token frames cut, 5 ms fades."""
import json, os, sys

import numpy as np
import onnxruntime as ort

DIR = os.path.expanduser("~/models/kitten-tts-2-pico")
LEOKANI = os.path.expanduser("~/models/leokani-tts-4.5M")
END = 10
if LEOKANI not in sys.path:
    sys.path.insert(0, LEOKANI)
import leokani_onnx as fe


class Kitten:
    def __init__(self, threads=1):
        with open(os.path.join(DIR, "vocab.json"), encoding="utf-8") as f:
            self.vocab = json.load(f)
        o = ort.SessionOptions()
        o.intra_op_num_threads = threads
        o.inter_op_num_threads = 1
        self.session = ort.InferenceSession(os.path.join(DIR, "kitten_tts_2_pico_en_int4.onnx"), o, providers=["CPUExecutionProvider"])
        self.style = np.load(os.path.join(DIR, "eleanor.npy"))
        self._esp = None

    def esp(self):
        if self._esp is None:
            self._esp = fe.make_espeak()
        return self._esp

    def ids(self, text):
        """Text -> token id lists, one per clause (split near the middle past 400)."""
        out = []
        for c in fe.prepare(text, self.esp()):
            ids = [self.vocab[ch] for ch in fe.clusters(fe.phonemize(c, self.esp())) if ch in self.vocab]
            out.extend(self.split(ids))
        return out

    def split(self, ids):
        if len(ids) <= fe.MAX_IDS:
            return [ids] if ids else []
        mid = len(ids) // 2
        for mark in (self.vocab[","], self.vocab[" "]):
            cut = [i for i, x in enumerate(ids) if x == mark]
            if cut:
                k = min(cut, key=lambda i: abs(i - mid)) + 1
                if 0 < k < len(ids):
                    return self.split(ids[:k]) + self.split(ids[k:])
        return self.split(ids[:mid]) + self.split(ids[mid:])

    def run(self, ids, first, speed=1.0):
        tok = [0, *ids, END, 0]
        style = self.style[min(len(tok) - 1, len(self.style) - 1)][None]
        wav, dur = self.session.run(None, {"input_ids": np.array([tok], dtype=np.int64), "style": style,
                                           "speed": np.array([speed], dtype=np.float32)})
        w = np.clip(wav.astype(np.float32).reshape(-1), -1, 1)
        spf = max(1, round(len(w) / max(int(dur.sum()), 1)))
        lead = 0 if first else max(0, int(dur.reshape(-1)[0]) - 1) * spf
        tail = max(0, int(dur.reshape(-1)[-1]) - 1) * spf
        if lead + tail + spf < len(w):
            w = w[lead:len(w) - tail]
        w = np.ascontiguousarray(w)
        f = min(120, len(w) // 8)
        if f:
            w[:f] *= np.linspace(0, 1, f, dtype=np.float32)
            w[-f:] *= np.linspace(1, 0, f, dtype=np.float32)
        return w

    def chunks(self, text):
        first = True
        for c in fe.chunks(fe.clean(text)):
            for ids in self.ids(c):
                yield self.run(ids, first)
                first = False
