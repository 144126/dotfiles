#!/home/ed/.venvs/whistle/bin/python
# POST raw audio to :8081, get plain text back. Cactus Whistle, loaded once.
# Runs as runit service /etc/sv/whisper-server. One request at a time.
# venv: python3 -m venv ~/.venvs/whistle; ~/.venvs/whistle/bin/pip install cactus-needle
# 16 kHz WAV, at most 30 s per pass; longer audio is split here.
import os, tempfile, wave
from http.server import HTTPServer, BaseHTTPRequestHandler

os.environ.setdefault("HF_HOME", "/home/ed/models/huggingface")
os.environ["HF_HUB_DISABLE_XET"] = "1"
os.environ.setdefault("NEEDLE_TELEMETRY", "0")
os.environ.setdefault("DO_NOT_TRACK", "1")

import needle

speech = needle.Whistle()

TOKEN = os.environ.get("WHISTLE_TOKEN", "").strip()
LIMIT_S = 30


def one(path):
    return (speech.transcribe(path).get("text") or "").strip()


def transcribe_wav(path):
    try:
        with wave.open(path, "rb") as src:
            nch, sw, rate, nframes = src.getnchannels(), src.getsampwidth(), src.getframerate(), src.getnframes()
            raw = src.readframes(nframes)
    except wave.Error:
        return one(path)
    if not rate or nframes / rate <= LIMIT_S:
        return one(path)
    step = rate * LIMIT_S
    frame = nch * sw
    parts = []
    with tempfile.TemporaryDirectory() as d:
        for i, start in enumerate(range(0, nframes, step)):
            chunk = raw[start * frame : (start + step) * frame]
            if len(chunk) < frame * max(1, rate // 10):
                continue
            p = os.path.join(d, f"{i:04d}.wav")
            with wave.open(p, "wb") as out:
                out.setnchannels(nch)
                out.setsampwidth(sw)
                out.setframerate(rate)
                out.writeframes(chunk)
            t = one(p)
            if t:
                parts.append(t)
    return " ".join(parts)


class H(BaseHTTPRequestHandler):
    def allowed(self):
        if not TOKEN:
            return True
        auth = self.headers.get("Authorization", "")
        if auth == "Bearer " + TOKEN:
            return True
        if self.headers.get("X-Stt-Token") == TOKEN:
            return True
        if self.headers.get("X-Bridge-Token") == TOKEN:
            return True
        return False

    def do_GET(self):
        self.reply(200, "ok")

    def do_POST(self):
        if not self.allowed():
            self.reply(401, "unauthorized")
            return
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav") as f:
                f.write(body)
                f.flush()
                self.reply(200, transcribe_wav(f.name))
        except Exception as e:
            self.reply(500, repr(e))

    def reply(self, code, text):
        b = text.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)


HTTPServer(("127.0.0.1", 8081), H).serve_forever()
