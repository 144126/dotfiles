import os, queue, socket, subprocess, sys, threading

SOCK = "/tmp/paradee.sock"


def serve():
    import soundfile
    from paradee_tts import Paradee, SAMPLE_RATE
    tts = Paradee()
    texts, wavs = queue.Queue(), queue.Queue()
    state = {"gen": 0, "n": 0, "player": None}

    def synth():
        while True:
            gen, text = texts.get()
            if gen != state["gen"]:
                continue
            state["n"] += 1
            wav = f"/tmp/pi-tts-q{state['n']}.wav"
            soundfile.write(wav, tts(text), SAMPLE_RATE)
            wavs.put((gen, wav))

    def play():
        while True:
            gen, wav = wavs.get()
            if gen == state["gen"]:
                state["player"] = subprocess.Popen(["paplay", wav], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                state["player"].wait()
            os.remove(wav)

    threading.Thread(target=synth, daemon=True).start()
    threading.Thread(target=play, daemon=True).start()
    try:
        send("ping\n")
        sys.exit()  # another server already owns the socket
    except OSError:
        pass
    if os.path.exists(SOCK):
        os.unlink(SOCK)
    s = socket.socket(socket.AF_UNIX)
    s.bind(SOCK)
    s.listen()
    while True:
        c, _ = s.accept()
        with c:
            cmd, text = (c.makefile().read() + "\n").split("\n", 1)
            text = text.strip()
            if cmd == "stop":
                # bump gen so queued sentences are dropped, then cut the current one
                state["gen"] += 1
                if state["player"]:
                    state["player"].kill()
            elif cmd == "ping":
                pass
            elif cmd == "q":
                texts.put((state["gen"], text))
            else:
                try:
                    soundfile.write(cmd, tts(text), SAMPLE_RATE)
                    c.sendall(b"ok")
                except Exception:
                    pass


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
    from paradee_tts import Paradee, SAMPLE_RATE
    soundfile.write(wav, Paradee()(text), SAMPLE_RATE)
