import collections, io, os, queue, re, signal, socket, subprocess, sys, threading, time, urllib.request, wave

import numpy as np

SOCK = "/tmp/paradee.sock"
VAD_MODEL = os.path.expanduser("~/i/paradee/silero_vad.onnx")
STT_URL = os.environ.get("PI_VOICE_URL", "http://127.0.0.1:8081/")
TOKEN_FILE = os.path.expanduser("~/.config/jot-stt.token")
TOKEN = os.environ.get("WHISTLE_TOKEN") or (open(TOKEN_FILE).read().strip() if os.path.exists(TOKEN_FILE) else "")
REC_CMD = os.environ.get("PI_VOICE_REC_CMD", "")
SILENCE_S = float(os.environ.get("PI_VOICE_SILENCE_S") or 1.0)
OUT_RATE = 24000
FRAME = 512  # Silero's window: 32 ms at 16 kHz
FRAME_S = FRAME / 16000

lock = threading.Lock()
tts_lock = threading.Lock()
st = {"gen": 0, "out": None, "until": 0.0, "busy": False, "sink": None, "call": None}
texts, pcms = queue.Queue(), queue.Queue()
tts = None


def end(p, now=False):
    try:
        if now:
            p.kill()
        p.stdin.close()
    except (OSError, ValueError):
        pass
    p.wait()


def stop_audio():
    with lock:
        st["gen"] += 1
        st["until"] = 0.0
        out, st["out"] = st["out"], None
    if out:
        end(out, now=True)


def playing():
    return st["busy"] or not texts.empty() or not pcms.empty() or time.time() < st["until"]


def synth():
    while True:
        gen, text = texts.get()
        if gen != st["gen"]:
            continue
        st["busy"] = True
        try:
            with tts_lock:
                pcm = tts(text)
            if len(pcm):
                pcms.put((gen, pcm.astype("<f4").tobytes(), len(pcm) / OUT_RATE))
        except Exception:
            pass
        st["busy"] = False


def play():
    # one pacat stream per burst of speech keeps sentences gapless; killing it cuts audio at once
    while True:
        try:
            gen, pcm, secs = pcms.get(timeout=0.3)
        except queue.Empty:
            with lock:
                out = st["out"] if time.time() > st["until"] + 0.3 else None
                if out:
                    st["out"] = None
            if out:
                end(out)
            continue
        with lock:
            if gen != st["gen"]:
                continue
            if not st["out"]:
                sink = [f"--device={st['sink']}"] if st["sink"] else []
                st["out"] = subprocess.Popen(
                    ["pacat", "--raw", "--format=float32le", f"--rate={OUT_RATE}", "--channels=1", "--latency-msec=100", "--client-name=pi", "--stream-name=voice"] + sink,
                    stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                )
            out = st["out"]
            st["until"] = max(st["until"], time.time()) + secs
        try:
            out.stdin.write(pcm)
            out.stdin.flush()
        except (OSError, ValueError):
            with lock:
                if st["out"] is out:
                    st["out"] = None


def run(*args):
    return subprocess.run(args, capture_output=True, text=True).stdout


def aec_on():
    if REC_CMD:
        return False
    return "pi_aec_src" in run("pactl", "list", "short", "sources") or run(
        "pactl", "load-module", "module-echo-cancel", "aec_method=webrtc", "source_name=pi_aec_src", "sink_name=pi_aec_sink"
    ).strip().isdigit()


def aec_off():
    for line in run("pactl", "list", "short", "modules").splitlines():
        if "pi_aec_src" in line:
            run("pactl", "unload-module", line.split()[0])


def mic(source=None):
    args = ["sh", "-c", REC_CMD] if REC_CMD else [
        "parec", "--raw", "--format=s16le", "--rate=16000", "--channels=1", "--latency-msec=30", "--client-name=pi", "--stream-name=mic"
    ] + ([f"--device={source}"] if source else [])
    return subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, start_new_session=True)


def kill(p):
    # the whole group: a shell's child would keep the pipe open
    try:
        os.killpg(p.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def transcribe(pcm):
    b = io.BytesIO()
    with wave.open(b, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        w.writeframes(pcm)
    req = urllib.request.Request(STT_URL, b.getvalue(), {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {})
    with urllib.request.urlopen(req, timeout=600) as r:
        text = re.sub(r"\[[^\]]*\]|\([^)]*\)", "", r.read().decode()).strip().strip('"“”')
    return text if re.search(r"\w", text) else ""


class Vad:
    def __init__(self):
        import onnxruntime as ort

        so = ort.SessionOptions()
        so.intra_op_num_threads = so.inter_op_num_threads = 1
        self.s = ort.InferenceSession(VAD_MODEL, so, providers=["CPUExecutionProvider"])
        self.reset()

    def reset(self):
        self.state = np.zeros((2, 1, 128), np.float32)
        self.ctx = np.zeros((1, 64), np.float32)

    def __call__(self, pcm):
        x = (np.frombuffer(pcm, "<i2").astype(np.float32) / 32768)[None]
        out, self.state = self.s.run(None, {"input": np.concatenate([self.ctx, x], 1), "state": self.state, "sr": np.array(16000, np.int64)})
        self.ctx = x[:, -64:]
        return out[0][0]


def call(c, f):
    with lock:
        old, st["call"] = st["call"], c
    if old:
        try:
            old.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
    aec = aec_on()
    st["sink"] = "pi_aec_sink" if aec else None
    p = mic("pi_aec_src" if aec else None)
    vad = Vad()
    muted = [False]
    jobs = queue.Queue()
    send_lock = threading.Lock()

    def emit(line):
        with send_lock:
            try:
                c.sendall(f"{line}\n".encode())
            except OSError:
                kill(p)

    def commands():
        for line in f:
            muted[0] = {"mute": True, "unmute": False}.get(line.strip(), muted[0])
        kill(p)

    def stt():
        while (pcm := jobs.get()) is not None:
            try:
                text = transcribe(pcm)
                emit(f"text {text}" if text else "drop")
            except Exception as e:
                emit(f"error speech-to-text failed: {e}")

    threading.Thread(target=commands, daemon=True).start()
    threading.Thread(target=stt, daemon=True).start()
    emit("ready" if aec else "ready noaec")
    pre = collections.deque(maxlen=16)
    hits = collections.deque(maxlen=10)
    speech = None
    while len(buf := p.stdout.read(FRAME * 2)) == FRAME * 2:
        # pi's echo lingers a moment after its audio ends
        talking = time.time() < st["until"] + 0.5
        # without echo cancel, pi's own voice would reach the mic, so stay deaf while it talks
        if muted[0] or (not aec and talking):
            if speech is not None:
                emit("drop")
            speech = None
            pre.clear()
            hits.clear()
            vad.reset()
            continue
        prob = vad(buf)
        if speech is None:
            pre.append(buf)
            # talking over pi needs surer speech: echo leftovers must not cut it off
            hits.append(prob >= (0.7 if talking else 0.5))
            if sum(hits) < (8 if talking else 4):
                continue
            speech, voiced, silent = list(pre), sum(hits), 0
            if talking:
                stop_audio()
            emit("speech")
            continue
        speech.append(buf)
        voiced += prob >= 0.5
        silent = 0 if prob >= 0.35 else silent + 1
        if silent * FRAME_S < SILENCE_S and len(speech) * FRAME_S < 120:
            continue
        if voiced >= 5:
            emit("heard")
            jobs.put(b"".join(speech[: len(speech) - max(silent - 8, 0)]))
        else:
            emit("drop")
        speech = None
        pre.clear()
        hits.clear()
    jobs.put(None)
    kill(p)
    p.wait()
    with lock:
        mine = st["call"] is c
        if mine:
            st["call"] = st["sink"] = None
    if mine and aec:
        aec_off()
    # shutdown, not just close: it wakes the commands thread and tells pi the call is over
    try:
        c.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass
    f.close()
    c.close()


def dictate(c, f):
    stop_audio()
    p = mic()
    keep = [False]

    def commands():
        keep[0] = f.readline().strip() == "stop"
        time.sleep(0.3)  # the last word is still on its way from the mic
        kill(p)

    threading.Thread(target=commands, daemon=True).start()
    pcm = p.stdout.read()
    p.wait()
    try:
        text = transcribe(pcm) if keep[0] and len(pcm) > 16000 else ""
        c.sendall(f"text {text}\n".encode() if text else b"drop\n")
    except Exception as e:
        try:
            c.sendall(f"error speech-to-text failed: {e}\n".encode())
        except OSError:
            pass
    f.close()
    c.close()


def to_file(c, f, path):
    import soundfile

    try:
        text = f.read()
        with tts_lock:
            pcm = tts(text)
        soundfile.write(path, pcm, OUT_RATE)
        c.sendall(b"ok")
    except Exception:
        pass
    f.close()
    c.close()


def serve():
    global tts
    from paradee_tts import Paradee

    tts = Paradee()
    try:
        send("ping\n")
        sys.exit()  # another server already owns the socket
    except OSError:
        pass
    threading.Thread(target=synth, daemon=True).start()
    threading.Thread(target=play, daemon=True).start()
    if os.path.exists(SOCK):
        os.unlink(SOCK)
    s = socket.socket(socket.AF_UNIX)
    s.bind(SOCK)
    s.listen()
    while True:
        c, _ = s.accept()
        c.settimeout(5)
        f = c.makefile("r", encoding="utf-8")
        try:
            cmd = f.readline().strip()
            session = {"listen": call, "rec": dictate}.get(cmd)
            if session or cmd.startswith("/"):
                c.settimeout(None)
                args = (c, f) if session else (c, f, cmd)
                threading.Thread(target=session or to_file, args=args, daemon=True).start()
                continue
            text = f.read().strip()
            if cmd == "q":
                texts.put((st["gen"], text))
            elif cmd == "stop":
                stop_audio()
            elif cmd == "status":
                c.sendall(b"1" if playing() else b"0")
        except OSError:
            pass
        f.close()
        c.close()


def send(msg):
    c = socket.socket(socket.AF_UNIX)
    c.connect(SOCK)
    c.sendall(msg.encode())
    c.shutdown(socket.SHUT_WR)
    return c.recv(2)


if sys.argv[1] == "--serve":
    serve()
if sys.argv[1] == "--stop":
    try:
        send("stop\n")
    except OSError:
        pass
    sys.exit()
wav, text = sys.argv[1], sys.stdin.read()
try:
    sys.exit(send(f"{wav}\n{text}") != b"ok")
except OSError:
    # first call: start the warm server for next time, speak this one cold
    subprocess.Popen([sys.executable, __file__, "--serve"], start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    import soundfile
    from paradee_tts import Paradee

    soundfile.write(wav, Paradee()(text), OUT_RATE)
