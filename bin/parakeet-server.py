#!/home/ed/.venvs/parakeet-redux/bin/python
# POST raw audio to :8081, get plain text back. moondream/parakeet-redux, loaded once.
# Runs as runit service /etc/sv/whisper-server. One request at a time.
# venv: python3 -m venv ~/.venvs/parakeet-redux; pip install torch --index-url https://download.pytorch.org/whl/cpu; pip install 'moondream>=2.4.0'
import os, tempfile
from http.server import HTTPServer, BaseHTTPRequestHandler

# runit gives no shell env: use the same model cache as the shell, and plain HTTP (xet downloads stall here)
os.environ.setdefault("HF_HOME", "/home/ed/models/huggingface")
os.environ["HF_HUB_DISABLE_XET"] = "1"
import moondream as md


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.reply(200, "ok")

    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav") as f:
                f.write(body)
                f.flush()
                self.reply(200, speech.transcribe(audio=f.name)["text"].strip())
        except Exception as e:
            self.reply(500, repr(e))

    def reply(self, code, text):
        b = text.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)


with md.photon("moondream/parakeet-redux", device="cpu") as speech:
    HTTPServer(("127.0.0.1", 8081), H).serve_forever()
