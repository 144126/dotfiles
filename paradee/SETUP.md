# Paradee voice for pi

Pi reads its replies out loud while they stream in, using Paradee
(`sahilmahendrakar/Paradee-8M-v1.0`, Kokoro-82M distilled to 8M params, CPU only).

Agent: follow these steps in order. Done = step 6 plays speech.

## Files

- `say.py` — warm TTS server on `/tmp/paradee.sock` + CLI. Queues sentences, synths the next while one plays.
- `paradee_tts.py` — Paradee inference, vendored from github.com/sahilmahendrakar/paradee (Apache-2.0).
- `requirements.txt` — exact pinned deps (`pip freeze`).
- `speak.ts` — pi extension: streams finished sentences to the server; `/speak` toggles, `ctrl+s` stops.
- `say` — `say "text"` CLI: Paradee, piper fallback; `say --stop`.

## Steps

1. Needs: Python 3.11 or 3.12 (misaki has no wheel for 3.13+), `paplay` (PulseAudio/PipeWire), pi (`@earendil-works/pi-coding-agent`), internet for step 3.
2. Paths are hardcoded to `/home/ed`. If `$HOME` differs:
   `sed -i "s|/home/ed|$HOME|g" speak.ts say`
3. Install Paradee:
   ```
   mkdir -p ~/i/paradee && cp say.py paradee_tts.py requirements.txt ~/i/paradee/
   cd ~/i/paradee && python3.11 -m venv .venv   # or python3.12
   .venv/bin/pip install -r requirements.txt
   .venv/bin/python -c "from paradee_tts import Paradee; Paradee()"   # downloads the 9 MB model
   ```
4. Install the pi extension and CLI:
   ```
   mkdir -p ~/.pi/agent/extensions ~/.local/bin
   cp speak.ts ~/.pi/agent/extensions/speak.ts
   cp say ~/.local/bin/say && chmod +x ~/.local/bin/say
   echo on > ~/.pi/speak
   ```
5. Restart pi (or `/reload`).
6. Check: `~/.local/bin/say --force "Paradee is working."` speaks (first call ~6s while the model loads, then ~0.6s).
   Then ask pi anything; it should start talking after the first sentence.

## Notes

- The server starts itself on first use and stays running. Restart it after editing `say.py`: `pkill -f "say.py --[s]erve"`.
- `~/.pi/voice-mode` containing `on` mutes speech.
- With `PI_TTS_URL` set, pi sends whole replies to a remote bridge instead.
