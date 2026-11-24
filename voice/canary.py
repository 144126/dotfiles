#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys
import tempfile
import wave

ROOT = Path.home() / "models/audiocpp"
MODEL = ROOT / "Canary-180M-Flash-GGUF/canary-180m-flash-q8_0.gguf"


def transcribe_wav(audio):
    with tempfile.TemporaryDirectory(prefix="canary-") as directory:
        transcript = Path(directory) / "text"
        run = subprocess.run(
            [ROOT / "audiocpp_cli", "--task", "asr", "--family", "canary_asr",
             "--model", MODEL, "--backend", "cpu", "--threads", "2",
             "--audio", audio, "--text-out", transcript],
            capture_output=True, text=True, timeout=90,
        )
        if run.returncode:
            lines = run.stderr.strip().splitlines()
            raise RuntimeError(lines[-1] if lines else "canary could not transcribe")
        return " ".join(transcript.read_text(encoding="utf-8").split())


def transcribe(pcm):
    with tempfile.NamedTemporaryFile(suffix=".wav") as audio:
        with wave.open(audio.name, "wb") as wav:
            wav.setparams((1, 2, 16000, 0, "NONE", "not compressed"))
            wav.writeframes(pcm)
        return transcribe_wav(audio.name)


if __name__ == "__main__":
    try:
        print(transcribe_wav(sys.argv[1]))
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
        sys.exit(str(error))
