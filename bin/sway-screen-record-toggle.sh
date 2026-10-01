#!/bin/bash
set -eu

record_state="${XDG_RUNTIME_DIR:?}/screen-record"
mkdir -p "$record_state"
exec 9>"$record_state/lock"
flock -n 9 || exit 0

if [ -f "$record_state/state" ]; then
  read -r record_pid record_file < "$record_state/state"
  if [ "$(cat "/proc/$record_pid/comm" 2>/dev/null || true)" = wf-recorder ]; then
    kill -INT "$record_pid"
    rm "$record_state/state"
    notify-send 'screen recording stopped' "$record_file"
    exit 0
  fi
  rm "$record_state/state"
fi

record_file="$HOME/screen-rec/screen-$(date +%Y-%m-%d-%H-%M-%S).mp4"
mkdir -p "$HOME/screen-rec"
record_output=$(swaymsg -t get_outputs | jq -r '[.[] | select(.active)] | (map(select(.focused))[0] // .[0]).name')
record_audio="$(pactl get-default-sink).monitor"
wf-recorder -o "$record_output" --audio="$record_audio" -f "$record_file" > "$record_state/log" 2>&1 9>&- &
record_pid=$!
sleep 0.5
if ! kill -0 "$record_pid" 2>/dev/null; then
  notify-send -u critical 'screen recording failed' "see $record_state/log"
  exit 1
fi
printf '%s %s\n' "$record_pid" "$record_file" > "$record_state/state"
notify-send 'screen recording started' 'mod+shift+q stops and saves it'
