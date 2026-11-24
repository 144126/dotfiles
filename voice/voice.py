import collections, io, os, queue, re, signal, socket, subprocess, sys, threading, time, wave

import numpy as np

SOCK = "/tmp/voice.sock"
VAD_MODEL = os.path.expanduser("~/.local/share/voice/silero_vad.onnx")
LEOKANI = os.path.expanduser("~/models/leokani-tts-4.5M")
REC_CMD = os.environ.get("PI_VOICE_REC_CMD", "")
TURN_MODEL = os.path.expanduser("~/models/kuroko/onnx/kuroko-stream.onnx")
# quiet that ends a turn even when Kuroko hears the speaker holding the floor
SILENCE_S = float(os.environ.get("PI_VOICE_SILENCE_S") or 2.0)
# after this much quiet, a turn ends once Kuroko's hold drops below TURN_HOLD.
# On LiveKit's eot-bench (400 English turns) this cut off 7% of mid-turn pauses at 0.74 s mean wait,
# where Smart Turn v3.2 at 256/768 ms cut off 18% at 0.65 s
TURN_AFTER_S = float(os.environ.get("PI_VOICE_TURN_AFTER_S") or 0.4)
TURN_HOLD = float(os.environ.get("PI_VOICE_TURN_HOLD") or 0.65)
OUT_RATE = 24000
FRAME = 512  # Silero's window: 32 ms at 16 kHz
FRAME_S = FRAME / 16000

lock = threading.Lock()
tts_lock = threading.Lock()
st = {"gen": 0, "out": None, "until": 0.0, "busy": False, "sink": None, "call": None, "paused": False, "rewind": False}
CHUNK = int(OUT_RATE * 0.02) * 4  # 20 ms of float32 per write, so a pause lands at once
REWIND = int(OUT_RATE * 0.4) * 4  # a resume replays pacat's 100 ms buffer plus 300 ms, so the words pick up cleanly
BARGE_S = 1.5  # talking this long over a paused reply is a real interruption, whatever the words
# a short utterance made only of these words is a backchannel ("mhm", "got it"): the reply resumes
BACKCHANNEL = set("mhm mm mmhmm hmm uh huh um ah oh yeah yes yep yup ok okay right sure alright all cool nice got it i see".split())
texts, pcms = queue.Queue(), queue.Queue()
leokani = None


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
        st["paused"] = st["rewind"] = False
        out, st["out"] = st["out"], None
    if out:
        end(out, now=True)


# barge-in: silence the reply now, keep its place; resume or stop once the words are known
def pause_audio():
    with lock:
        st["paused"] = st["rewind"] = True
        out, st["out"] = st["out"], None
    if out:
        end(out, now=True)


def resume_audio():
    st["paused"] = False


def backchannel(text):
    words = re.sub(r"[^a-z ]", " ", text.lower()).split()
    return len(words) <= 3 and all(w in BACKCHANNEL for w in words)


def playing():
    return st["paused"] or st["busy"] or not texts.empty() or not pcms.empty() or time.time() < st["until"]


def leokani_chunks(text):
    """The on-device voice: Kitten TTS 2 Pico, Eleanor (kitten.py). Name kept for the callers."""
    global leokani
    if leokani is None:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import kitten

        leokani = kitten.Kitten(threads=1)
    yield from leokani.chunks(text)


def leokani_pcm(text):
    parts = list(leokani_chunks(text)) if text.strip() else []
    return np.concatenate(parts) if parts else np.zeros(0, dtype=np.float32)


def synth():
    while True:
        gen, text, engine = texts.get()
        if gen != st["gen"]:
            continue
        st["busy"] = True
        try:
            with tts_lock:
                for pcm in leokani_chunks(text):
                    if gen != st["gen"]:
                        break
                    if len(pcm):
                        pcms.put((gen, pcm.astype("<f4").tobytes(), len(pcm) / OUT_RATE))
        except Exception:
            pass
        st["busy"] = False


def play():
    # one pacat stream per burst of speech keeps sentences gapless; killing it cuts audio at once
    cur = None  # [gen, pcm bytes, bytes written]
    while True:
        if st["paused"]:
            time.sleep(0.02)
            continue
        if cur is None or cur[2] >= len(cur[1]):
            try:
                gen, pcm, _ = pcms.get(timeout=0.3)
            except queue.Empty:
                with lock:
                    out = st["out"] if time.time() > st["until"] + 0.3 else None
                    if out:
                        st["out"] = None
                if out:
                    end(out)
                continue
            cur = [gen, pcm, 0]
        with lock:
            if cur[0] != st["gen"]:
                cur = None
                continue
            if st["paused"]:
                continue
            if st["rewind"]:
                cur[2], st["rewind"] = max(0, cur[2] - REWIND), False
            if not st["out"]:
                sink = [f"--device={st['sink']}"] if st["sink"] else []
                st["out"] = subprocess.Popen(
                    ["pacat", "--raw", "--format=float32le", f"--rate={OUT_RATE}", "--channels=1", "--latency-msec=100", "--client-name=pi", "--stream-name=voice"] + sink,
                    stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                )
            out = st["out"]
            chunk = cur[1][cur[2] : cur[2] + CHUNK]
            cur[2] += len(chunk)
            st["until"] = max(st["until"], time.time()) + len(chunk) / 4 / OUT_RATE
        try:
            out.stdin.write(chunk)
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
    # webrtc works in 10 ms blocks (480 at 48 kHz); any other quantum crackles the playback
    run("pw-metadata", "-n", "settings", "0", "clock.force-quantum", "480")
    ok = "pi_aec_src" in run("pactl", "list", "short", "sources") or run(
        "pactl", "load-module", "module-echo-cancel", "aec_method=webrtc", "source_name=pi_aec_src", "sink_name=pi_aec_sink"
    ).strip().isdigit()
    if not ok:
        run("pw-metadata", "-n", "settings", "0", "clock.force-quantum", "0")
    return ok


def aec_off():
    run("pw-metadata", "-n", "settings", "0", "clock.force-quantum", "0")
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


stt = None


# Conformer is shared with Mod+Ctrl+E (voice-text).
def transcribe(pcm):
    global stt
    if stt is None:
        import importlib.util

        spec = importlib.util.spec_from_file_location("conformer", os.path.join(os.path.dirname(os.path.abspath(__file__)), "conformer.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        stt = m.load()
    text = stt(np.frombuffer(pcm, np.int16)).strip()
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


class Turn:
    """Kuroko (PatientDesk AI, Apache-2.0): does the speaker still hold the floor, pauses included?
    One 40 ms step of the mic and the agent's channel; the agent's channel is a quiet room (floor 1e-2),
    as scored on eot-bench. Remembers the last 10 s, which scored the same as 40 s."""

    CONTEXT = 250

    def __init__(self):
        import onnxruntime as ort

        so = ort.SessionOptions()
        so.intra_op_num_threads = so.inter_op_num_threads = 1
        self.s = ort.InferenceSession(TURN_MODEL, so, providers=["CPUExecutionProvider"])
        self.turns = 1.0 / 10_000 ** (np.arange(32) / 32)
        self.floor = np.full((2, 2, 80), 1e-10, np.float32)
        self.floor[1] = 1e-2
        self.reset()

    def reset(self):
        self.k, self.hold, self.buf = 0, 1.0, np.zeros(0, np.float32)
        self.last = np.zeros((2, 320), np.float32)
        self.heard = np.zeros((2, 4, 80), np.float32)
        self.mask = np.full(self.CONTEXT, -1e30, np.float32)
        self.keys = [np.zeros((6, 64, self.CONTEXT), np.float32) for _ in range(8)]
        self.values = [np.zeros((6, self.CONTEXT, 64), np.float32) for _ in range(8)]

    def __call__(self, pcm):
        """Feed 16 kHz s16 mic audio; returns the latest chance the speaker holds the floor."""
        self.buf = np.concatenate([self.buf, np.frombuffer(pcm, "<i2").astype(np.float32) / 32768])
        while len(self.buf) >= 640:
            a = np.stack([self.buf[:640], np.zeros(640, np.float32)])
            self.buf = self.buf[640:]
            f = {"audio": np.concatenate([self.last, a], 1), "floor": self.floor, "heard": self.heard, "mask": self.mask,
                 "cos": np.cos(self.k * self.turns).astype(np.float32), "sin": np.sin(self.k * self.turns).astype(np.float32)}
            f |= {f"key{i}": self.keys[i] for i in range(8)}
            f |= {f"value{i}": self.values[i] for i in range(8)}
            ans, self.heard, keys, values = self.s.run(None, f)
            place = self.k % self.CONTEXT
            for i in range(8):
                self.keys[i][:, :, place] = keys[i]
                self.values[i][:, place] = values[i]
            self.mask[place] = 0.0
            self.last = a[:, -320:]
            self.k += 1
            self.hold = float(np.ravel(ans)[2])
        return self.hold


def call(c, f, model="conformer"):
    decode = transcribe
    if model == "canary":
        from canary import transcribe as decode

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
    turn = Turn() if os.path.exists(TURN_MODEL) else None
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
        while (job := jobs.get()) is not None:
            pcm, barge = job
            try:
                text = decode(pcm)
                if barge and backchannel(text):
                    resume_audio()
                    emit("drop")
                    continue
                if barge:
                    stop_audio()
                emit(f"text {text}" if text else "drop")
            except Exception as e:
                if barge:
                    resume_audio()
                emit(f"error speech-to-text failed: {e}")

    threading.Thread(target=commands, daemon=True).start()
    threading.Thread(target=stt, daemon=True).start()
    emit("ready" if aec else "ready noaec")
    pre = collections.deque(maxlen=16)
    hits = collections.deque(maxlen=10)
    speech = barge = None
    while len(buf := p.stdout.read(FRAME * 2)) == FRAME * 2:
        # pi's echo lingers a moment after its audio ends
        talking = st["paused"] or time.time() < st["until"] + 0.5
        # without echo cancel, pi's own voice would reach the mic, so stay deaf while it talks
        if muted[0] or (not aec and talking):
            if speech is not None:
                emit("drop")
            if barge:
                resume_audio()
            speech = barge = None
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
            if turn:
                turn.reset()
                turn(b"".join(speech))
            # talking over the reply pauses it; the words decide whether it stops
            if talking:
                pause_audio()
                barge = time.time()
            emit("speech")
            continue
        speech.append(buf)
        hold = turn(buf) if turn else 1.0
        if barge and time.time() - barge > BARGE_S:
            stop_audio()
            barge = None
        voiced += prob >= 0.5
        silent = 0 if prob >= 0.35 else silent + 1
        # a paused reply waits on this utterance, so a short pause ends it; otherwise Kuroko decides,
        # and a long enough quiet ends the turn regardless
        if barge:
            done = silent * FRAME_S >= 0.5
        else:
            done = silent * FRAME_S >= SILENCE_S or (silent * FRAME_S >= TURN_AFTER_S and voiced >= 5 and hold < TURN_HOLD)
        if not done and len(speech) * FRAME_S < 120:
            continue
        if voiced >= 5:
            emit("heard")
            jobs.put((b"".join(speech[: len(speech) - max(silent - 8, 0)]), barge is not None))
        else:
            if barge:
                resume_audio()
            emit("drop")
        speech = barge = None
        pre.clear()
        hits.clear()
    if barge:
        resume_audio()
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
            pcm = leokani_pcm(text)
        soundfile.write(path, pcm, OUT_RATE)
        c.sendall(b"ok")
    except Exception:
        pass
    f.close()
    c.close()


def serve():
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
            session = {"listen": call, "listen canary": call, "rec": dictate}.get(cmd)
            if session or cmd.startswith("/"):
                c.settimeout(None)
                args = (c, f, "canary") if cmd == "listen canary" else (c, f) if session else (c, f, cmd)
                threading.Thread(target=session or to_file, args=args, daemon=True).start()
                continue
            text = f.read().strip()
            if cmd in ("q", "qp"):
                texts.put((st["gen"], text, cmd))
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

    soundfile.write(wav, leokani_pcm(text), OUT_RATE)
