#!/usr/bin/env -S uv run --script --quiet
# /// script
# requires-python = ">=3.11"
# dependencies = ["onnx-asr[cpu]==0.12.0", "numpy"]
# ///
# stt.py <wav>: speech to text on this machine. Text to stdout. voice-stream and voice.py import load() from here.
# Fluid Speech Pro int8 (~/models/fluid-speech-pro, Parakeet TDT 0.6B v3 fine-tune, CC-BY-4.0, FluidVoice Labs):
# 1.39% WER on Ed's 18 clips (Conformer-small 11.57%), about 3x faster than real time on this CPU.
# Long takes are cut at the quietest 20 ms between 15 and 25 s: attention cost grows with the square of length.
import os, sys, subprocess
import numpy as np

D = os.path.expanduser("~/models/fluid-speech-pro")


def pieces(x):
    at, F = 0, 320
    while len(x) - at > 25 * 16000:
        e = x[at + 15 * 16000 : at + 25 * 16000].astype(np.float32) ** 2
        e = e[: len(e) // F * F].reshape(-1, F).sum(1)
        cut = at + 15 * 16000 + int(e.argmin()) * F + F // 2
        yield x[at:cut]
        at = cut
    yield x[at:]


# returns transcribe(16 kHz int16 pcm) -> text
def load():
    import onnx_asr, onnxruntime as ort

    so = ort.SessionOptions()
    so.intra_op_num_threads = 4
    m = onnx_asr.load_model("nemo-parakeet-tdt-0.6b-v3", D, quantization="int8", sess_options=so)
    one = lambda p: m.recognize(p.astype(np.float32) / 32768, sample_rate=16000).strip()
    return lambda pcm: " ".join(w for w in (one(p) for p in pieces(pcm) if len(p) >= 1600) if w)


if __name__ == "__main__":
    # any input format; Mod+Ctrl+E already records 16 kHz mono
    pcm = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", sys.argv[1], "-ar", "16000", "-ac", "1", "-f", "s16le", "-"], capture_output=True, check=True).stdout, np.int16)
    print(load()(pcm))
