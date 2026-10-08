# Pi voice

Pi speaks its replies as they stream in and takes hands-free voice calls.
Speech: Paradee (`sahilmahendrakar/Paradee-8M-v1.0`, Kokoro-82M distilled to 8M params, CPU).
Listening: Silero VAD, PipeWire's webrtc echo canceller, and a speech-to-text server
that takes a WAV body and returns plain text (here: Whistle, `whistle-server.py`).

Agent: follow these steps in order. Done = every check in step 7 passes.

## Keys in pi

- `ctrl+e` voice call: talk any time, ~1 s of quiet sends it, talking over pi cuts it off.
- `ctrl+r` dictate a message; `ctrl+r` again sends it (text already typed goes first), `ctrl+alt+r` puts it in the editor instead.
- `ctrl+s` stop pi talking; when quiet, read aloud the part of the last reply after `|||`; in a call, mute your mic.
- `/speak on|off` speak replies outside calls.

## Files

- `voice.py` — daemon on `/tmp/paradee.sock`: speech queue (Paradee → `pacat`), mic (`parec`) with VAD, echo cancel and speech-to-text for calls and dictation. Also the backend of `say`.
- `paradee_tts.py` — Paradee inference, vendored from github.com/sahilmahendrakar/paradee (Apache-2.0).
- `requirements.txt` — exact pinned deps.
- `voice.ts` — the pi extension.
- `say` — `say "text"` CLI (Paradee, piper fallback); `say --stop`.
- `keybindings.json` — moves pi's own ctrl+s, ctrl+e and ctrl+alt+r actions aside so the voice keys raise no warnings.
- `whistle-server.py`, `whisper-server.run` — the speech-to-text server used here (zip only).

## Steps

1. Needs: Python 3.11 or 3.12 (misaki has no wheel for 3.13+), PipeWire or PulseAudio with `pacat`, `parec`, `pactl` (pulseaudio-utils), pi (`@earendil-works/pi-coding-agent`), internet.
2. Paths are hardcoded to `/home/ed`. If `$HOME` differs:
   `sed -i "s|/home/ed|$HOME|g" voice.ts say whistle-server.py whisper-server.run`
3. Install the daemon:
   ```
   mkdir -p ~/i/paradee && cp voice.py paradee_tts.py requirements.txt ~/i/paradee/
   cd ~/i/paradee && python3.11 -m venv .venv   # or python3.12
   .venv/bin/pip install -r requirements.txt
   curl -fL -o silero_vad.onnx https://raw.githubusercontent.com/snakers4/silero-vad/v5.1.2/src/silero_vad/data/silero_vad.onnx
   sha256sum silero_vad.onnx   # 2623a2953f6ff3d2c1e61740c6cdb7168133479b267dfef114a4a3cc5bdd788f
   .venv/bin/python -c "from paradee_tts import Paradee; Paradee()"   # downloads the 9 MB model
   ```
4. Speech-to-text: skip if `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8081/` prints 200. Otherwise:
   ```
   python3 -m venv ~/.venvs/whistle && ~/.venvs/whistle/bin/pip install cactus-needle
   cp whistle-server.py ~/.local/bin/ && chmod +x ~/.local/bin/whistle-server.py
   ```
   Run it at boot: runit uses `whisper-server.run` as `/etc/sv/whisper-server/run` (fix its script path to `~/.local/bin/whistle-server.py`); with systemd, a user service with `ExecStart=%h/.local/bin/whistle-server.py`.
   A token is optional: if `~/.config/jot-stt.token` exists, both sides use it.
   Another server works too: set `PI_VOICE_URL` (POST WAV, plain text back).
5. Install the pi extension and CLI (remove old `speak.ts` and `voice-input.ts` from the extensions folder if present):
   ```
   mkdir -p ~/.pi/agent/extensions ~/.local/bin
   cp voice.ts ~/.pi/agent/extensions/voice.ts
   cp keybindings.json ~/.pi/agent/keybindings.json   # or merge its keys into an existing one
   cp say ~/.local/bin/say && chmod +x ~/.local/bin/say
   echo on > ~/.pi/speak
   ```
6. Restart pi (or `/reload`).
7. Checks:
   - `~/.local/bin/say --force "Paradee is working."` speaks (first call ~6 s while the model loads, then ~0.6 s).
   - Ask pi anything: it starts talking after the first sentence.
   - `ctrl+e`: the footer shows `voice: listening`. Say something: it is sent, and pi answers out loud. `ctrl+e` again ends the call.

## Notes

- The daemon starts itself and stays running. Restart it after editing `voice.py`: `pkill -f "voice.py --[s]erve"`.
- During a call the daemon loads PipeWire's `module-echo-cancel` (`pi_aec_sink`, `pi_aec_src`) and unloads it after. Without it, pi can't hear you while it talks; headphones avoid echo either way.
- The echo canceller adapts in pi's first seconds of speech in a call, so cutting in that early is slower.
- Env: `PI_VOICE_URL` speech-to-text URL, `PI_VOICE_SILENCE_S` quiet that ends your turn (default 1.0), `PI_VOICE_REC_CMD` custom mic command printing raw 16 kHz mono s16le.
