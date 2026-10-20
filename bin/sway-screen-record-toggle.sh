#!/bin/bash
set -eu

record_state="${XDG_RUNTIME_DIR:?}/screen-record"
mkdir -p "$record_state"
exec 9>"$record_state/lock"
flock -n 9 || exit 0

unmix() { for m in $record_mods; do pactl unload-module "$m"; done; }

if [ -f "$record_state/state" ]; then
  read -r record_pid record_file record_mods < "$record_state/state"
  if [ "$(cat "/proc/$record_pid/comm" 2>/dev/null || true)" = wf-recorder ]; then
    kill -INT "$record_pid"
    rm "$record_state/state"
    unmix
    notify-send 'screen recording stopped' "$record_file"
    exit 0
  fi
  unmix
  rm "$record_state/state"
fi

mode="${1:-screen}"
record_file="$HOME/screen-rec/$mode-$(date +%Y-%m-%d-%H-%M-%S).mp4"
mkdir -p "$HOME/screen-rec"
if [ "$mode" = window ]; then
  record_area=(-g "$(swaymsg -t get_tree | jq -r '.. | select(.focused? == true) | "\(.rect.x),\(.rect.y) \(.rect.width)x\(.rect.height)"')")
else
  record_area=(-o "$(swaymsg -t get_outputs | jq -r '[.[] | select(.active)] | (map(select(.focused))[0] // .[0]).name')")
fi
record_mods="$(pactl load-module module-null-sink sink_name=rec_mix) $(pactl load-module module-loopback source="$(pactl get-default-source)" sink=rec_mix latency_msec=20) $(pactl load-module module-loopback source="$(pactl get-default-sink).monitor" sink=rec_mix latency_msec=20)"
wf-recorder "${record_area[@]}" --audio=rec_mix.monitor -f "$record_file" > "$record_state/log" 2>&1 9>&- &
record_pid=$!
sleep 0.5
if ! kill -0 "$record_pid" 2>/dev/null; then
  unmix
  notify-send -u critical 'screen recording failed' "see $record_state/log"
  exit 1
fi
printf '%s %s %s\n' "$record_pid" "$record_file" "$record_mods" > "$record_state/state"
notify-send "$mode recording started" 'mod+shift+q stops and saves it'
