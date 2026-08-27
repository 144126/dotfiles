#!/bin/bash
# sway-voice-global — system-wide Mod+Ctrl+R voice toggle, same engine as pi's Ctrl+R.
# First press: start recording via sox -> /tmp/sway-voice.wav
# Second press: stop, transcribe via local whisper.cpp (127.0.0.1:8081), wl-copy + Ctrl+V.
set -uo pipefail
WAV="/tmp/sway-voice.wav"
PIDFILE="/tmp/sway-voice.pid"
LOG="/tmp/sway-voice.log"
URL="${PI_VOICE_URL:-${VIBEVOICE_ASR_URL:-http://127.0.0.1:8081/v1/audio/transcriptions}}"
MODEL="${VIBEVOICE_ASR_MODEL:-${PI_VOICE_MODEL:-base}}"
GRACE_MS="${PI_VOICE_STOP_GRACE_MS:-1500}"

log() { echo "[$(date -Iseconds)] $*" >> "$LOG" 2>/dev/null || true; }
notify() { notify-send -t 3500 "voice" "$*" 2>/dev/null || true; log "$*"; }

is_recording() {
  if [ -f "$PIDFILE" ]; then
    local pid; pid=$(cat "$PIDFILE" 2>/dev/null || echo "")
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then return 0; fi
    rm -f "$PIDFILE"
  fi
  return 1
}

if is_recording; then
  pid=$(cat "$PIDFILE")
  log "stop requested pid=$pid grace=${GRACE_MS}ms"
  notify "stopping — capturing trailing audio…"
  sleep "$(awk "BEGIN{print $GRACE_MS/1000}")"
  kill -INT "$pid" 2>/dev/null || true
  for _ in 1 2 3 4 5 6 7 8 9 10 15 20; do
    kill -0 "$pid" 2>/dev/null || break
    sleep 0.15
  done
  kill -KILL "$pid" 2>/dev/null || true
  rm -f "$PIDFILE"
  notify "transcribing…"
  if [ ! -f "$WAV" ] || [ "$(stat -c%s "$WAV" 2>/dev/null || echo 0)" -le 44 ]; then
    notify "no speech detected"
    log "no speech wav missing or too small"
    exit 0
  fi
  log "transcribing $(stat -c%s "$WAV") bytes to $URL"
  resp=$(curl -s -m 45 -X POST "$URL" -F "model=$MODEL" -F "file=@$WAV;type=audio/wav" -F "response_format=json" 2>&1 || true)
  log "resp: ${resp:0:600}"
  text=$(printf "%s" "$resp" | python3 -c "import sys,json; d=json.load(sys.stdin); print((d.get('text') or '').strip())" 2>/dev/null || echo "")
  if [ -z "$text" ]; then
    err=$(printf "%s" "$resp" | head -c 400)
    if echo "$err" | grep -qi "ECONNREFUSED\|Failed to connect\|Connection refused"; then
      notify "whisper not reachable at $URL — is whisper-server running?"
    elif echo "$resp" | grep -q '"text"'; then
      notify "no speech detected"
    else
      notify "transcription failed"
    fi
    log "transcription failed resp=$resp"
    exit 0
  fi
  # copy to clipboard (wl-copy forks, stays alive)
  printf "%s" "$text" | wl-copy 2>/dev/null || printf "%s" "$text" | wl-copy -n 2>/dev/null || true
  # also push through cliphist via wl-paste watch, give it a moment
  sleep 0.2
  # paste blindly via Ctrl+V as requested — works for most apps. wtype synthesizes virtual keyboard.
  if command -v wtype >/dev/null 2>&1; then
    wtype -M ctrl -k v -m ctrl 2>/dev/null || wtype -- "$text" 2>/dev/null || true
    # fallback: if ctrl+v didn't paste (e.g. terminal needs shift), also type directly after short delay
    # we don't double-type: wtype ctrl+v already pasted, so only fallback if user wants raw type.
    # Uncomment next line to always type as fallback:
    # sleep 0.05; wtype -- "$text" 2>/dev/null || true
  elif command -v ydotool >/dev/null 2>&1; then
    ydotool key 29:1 47:1 47:0 29:0 2>/dev/null || true
  elif command -v xdotool >/dev/null 2>&1; then
    xdotool key ctrl+v 2>/dev/null || true
  fi
  notify "${text:0:80}"
  log "done text=${text:0:120}"
  exit 0
else
  rm -f "$WAV"
  log "starting recording"
  notify "recording — press Mod+Ctrl+R again to stop"
  # same sox invocation pi uses: 16kHz mono, silence trim to avoid leading silence file header issues
  sox -d -r 16000 -c 1 -b 16 "$WAV" silence 1 0.1 1% >>"$LOG" 2>&1 &
  pid=$!
  echo "$pid" > "$PIDFILE"
  sleep 0.35
  if ! kill -0 "$pid" 2>/dev/null; then
    notify "recording failed — check mic / sox"
    log "sox died immediately"
    rm -f "$PIDFILE"
    exit 1
  fi
  log "recording pid=$pid"
fi
