#!/bin/sh
CACHE="$HOME/.cache/battery-notify-last"
BEEP_PID="$HOME/.cache/battery-beep.pid"
BEEP_WAV="$HOME/.cache/soft-beep.wav"
CAP=$(cat /sys/class/power_supply/BAT0/capacity 2>/dev/null)
STATUS=$(cat /sys/class/power_supply/BAT0/status 2>/dev/null)
[ -z "$CAP" ] && exit 1

if [ ! -f "$BEEP_WAV" ]; then
  sox -n "$BEEP_WAV" synth 0.32 sine 660 vol 0.10 fade 0.05 0.22 0.06 2>/dev/null || true
fi

stop_beep() {
  if [ -f "$BEEP_PID" ]; then
    pid=$(cat "$BEEP_PID" 2>/dev/null)
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null
      pkill -P "$pid" 2>/dev/null || true
    fi
    rm -f "$BEEP_PID"
  fi
  pkill -f "battery-beep-loop" 2>/dev/null || true
}

start_beep() {
  if [ -f "$BEEP_PID" ]; then
    pid=$(cat "$BEEP_PID" 2>/dev/null)
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
      return 0
    fi
    rm -f "$BEEP_PID"
  fi
  sh -c '
    trap "exit 0" TERM INT
    while :; do
      cap=$(cat /sys/class/power_supply/BAT0/capacity 2>/dev/null)
      sta=$(cat /sys/class/power_supply/BAT0/status 2>/dev/null)
      case "$sta" in Charging|Full) exit 0;; esac
      [ -z "$cap" ] && exit 0
      [ "$cap" -ge 27 ] && exit 0
      wav="$1"
      if [ -f "$wav" ]; then
        paplay "$wav" 2>/dev/null || pw-play "$wav" 2>/dev/null || play -qn synth 0.32 sine 660 vol 0.10 fade 0.05 0.22 0.06 2>/dev/null || true
      else
        play -qn synth 0.32 sine 660 vol 0.10 fade 0.05 0.22 0.06 2>/dev/null || paplay /usr/share/sounds/freedesktop/stereo/bell.oga 2>/dev/null || true
      fi
      sleep 11
    done
  ' battery-beep-loop "$BEEP_WAV" &
  echo $! > "$BEEP_PID"
}

case "$STATUS" in
  Charging|Full) stop_beep ;;
  *) if [ "$CAP" -lt 27 ]; then start_beep; else stop_beep; fi ;;
esac

LAST=$(cat "$CACHE" 2>/dev/null)
[ -z "$LAST" ] && echo "$CAP" > "$CACHE" && exit 0

case "$STATUS" in
  Charging|Full)
    if [ "$CAP" -ge 90 ] && [ "$CAP" != "$LAST" ]; then
      notify-send -u normal "Battery at ${CAP}%" "Consider unplugging"
      echo "$CAP" > "$CACHE"
    fi
    [ "$CAP" -gt "$LAST" ] && echo "$CAP" > "$CACHE"
    ;;
  *)
    [ "$CAP" -gt "$LAST" ] && echo "$CAP" > "$CACHE" && exit 0
    DIFF=$(( LAST - CAP ))
    if [ "$DIFF" -ge 9 ]; then
      notify-send -u critical "Battery at ${CAP}%" "Consider charging soon"
      echo "$CAP" > "$CACHE"
    fi
    if [ "$CAP" -lt 27 ] && [ "$LAST" -ge 27 ]; then
      notify-send -u critical "Battery at ${CAP}%" "plug in soon — battery is low"
      echo "$CAP" > "$CACHE"
    fi
    ;;
esac
