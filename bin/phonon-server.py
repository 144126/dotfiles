#!/home/ed/.venvs/phonon-2/bin/python
# POST raw audio to :8081, get plain text back. FermionResearch/Phonon-2, loaded once.
# Runs as runit service /etc/sv/whisper-server. One request at a time.
# venv: python3 -m venv ~/.venvs/phonon-2; pip install torch --index-url https://download.pytorch.org/whl/cpu; pip install 'fermion-research>=0.2.3' soundfile scipy zstandard safetensors
import os, tempfile
from http.server import HTTPServer, BaseHTTPRequestHandler

os.environ.setdefault("HF_HOME", "/home/ed/models/huggingface")
os.environ["HF_HUB_DISABLE_XET"] = "1"
os.environ.setdefault("FERMION_CPU_THREADS", "4")

from fermion._speech import backends
from fermion.transcribe import _resolve

repo, key, pin, local_dir = _resolve("phonon-2")
engine_kind = backends.resolve("phonon-server")
from fermion._speech import fetch
model_dir = local_dir if local_dir is not None else fetch.ensure(repo, key, pin)
speech = backends.load(engine_kind, model_dir, profile=key, backend=pin["backend"], quiet=True)

TOKEN = os.environ.get("PHONON_TOKEN", "").strip()


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
                text, _, _ = speech.transcribe(f.name)
                self.reply(200, (text or "").strip())
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
