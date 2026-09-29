#!/bin/bash
# Mod+Ctrl+E toggles recording. Mod+Ctrl+R mutes/unmutes the live take so
# side talk never enters the wav. Each stop queues a transcription that pastes
# when done, so a new recording can start while older ones transcribe.
# Args: status (waybar json), cancel (drop the current recording), mute (toggle).
D="${XDG_RUNTIME_DIR:-/tmp}/voice"
URL="${PI_VOICE_URL:-http://127.0.0.1:8081/}"
GRACE_MS="${PI_VOICE_STOP_GRACE_MS:-1500}"
LOG="$D/log"
mkdir -p "$D"

log() { echo "[$(date -Iseconds)] $*" >> "$LOG"; }
notify() { notify-send -t 3500 voice "$*"; log "$*"; }
bar() { pkill -RTMIN+4 waybar; }
# rec holds "pid start_epoch" of the live sox
rec_pid() { read -r p t 2>/dev/null < "$D/rec" && kill -0 "$p" 2>/dev/null && echo "$p $t"; }
clock() { echo "$(( $1 / 60 )):$(printf %02d $(( $1 % 60 )))"; }
next_part() {
  n=0
  while [ -e "$D/part-$(printf %03d $n).wav" ]; do n=$((n+1)); done
  echo "$D/part-$(printf %03d $n).wav"
}
# INT sox and wait; $1 = pid
stop_sox() {
  local pid=$1
  kill -INT "$pid" 2>/dev/null
  for _ in $(seq 20); do kill -0 "$pid" 2>/dev/null || return; sleep 0.15; done
  kill -KILL "$pid" 2>/dev/null
}
# park the open rec.wav as the next part (sox still holds the inode)
park() {
  local part
  part=$(next_part)
  mv "$D/rec.wav" "$part" 2>/dev/null || : > "$part"
  echo "$part"
}

case "$1" in
status)
  n=$(find "$D" -name 'job-*.wav' | wc -l)
  out="" cls=""
  if r=$(rec_pid); then
    s=$(( $(date +%s) - ${r#* } ))
    out="● recording $(clock $s)" cls=rec
  elif [ -f "$D/muted" ]; then
    out="○ muted" cls=muted
  fi
  if [ "$n" -gt 0 ]; then
    t="transcribing"; [ "$n" -gt 1 ] && t="$t $n"
    out="${out:+$out · }$t" cls=${cls:-busy}
  fi
  printf '{"text":"%s","class":"%s"}\n' "$out" "$cls"
  exit ;;
cancel)
  exec 9>"$D/lock"; flock 9
  had=
  if r=$(rec_pid); then
    rm -f "$D/rec"; kill -INT "${r% *}"; sleep 0.3
    had=1
  fi
  [ -f "$D/muted" ] && had=1
  compgen -G "$D/part-*.wav" >/dev/null && had=1
  rm -f "$D/rec" "$D/rec.wav" "$D/muted" "$D"/part-*.wav
  [ -n "$had" ] && notify "recording cancelled"
  bar; exit ;;
mute)
  exec 9>"$D/lock"; flock 9
  if r=$(rec_pid); then
    part=$(park)
    echo "${r#* }" > "$D/muted"
    rm -f "$D/rec"
    bar
    stop_sox "${r% *}"
    [ "$(stat -c%s "$part" 2>/dev/null || echo 0)" -le 44 ] && rm -f "$part"
    exit
  fi
  if [ -f "$D/muted" ]; then
    start=$(cat "$D/muted")
    rm -f "$D/rec.wav"
    sox -q -d -r 16000 -c 1 -b 16 "$D/rec.wav" silence 1 0.1 1% 2>>"$LOG" 9>&- &
    echo "$! $start" > "$D/rec"
    rm -f "$D/muted"
    bar
    sleep 0.35
    if ! kill -0 $! 2>/dev/null; then
      rm -f "$D/rec"
      echo "$start" > "$D/muted"
      bar
      notify "unmute failed — check mic / sox"
    fi
  fi
  exit ;;
esac

exec 9>"$D/lock"; flock 9
if ! r=$(rec_pid) && [ ! -f "$D/muted" ]; then
  rm -f "$D/rec.wav" "$D/muted" "$D"/part-*.wav
  sox -q -d -r 16000 -c 1 -b 16 "$D/rec.wav" silence 1 0.1 1% 2>>"$LOG" 9>&- &
  echo "$! $(date +%s)" > "$D/rec"
  bar
  sleep 0.35
  kill -0 $! 2>/dev/null || { rm -f "$D/rec"; bar; notify "recording failed — check mic / sox"; }
  exit
fi

# sox keeps writing through its open fd, so renaming now is safe.
# parts from earlier mute/unmute cycles move aside so a new take can start.
id=$(date +%s%N)
job="$D/job-$id.wav"
stk="$D/stk-$id"
mkdir -p "$stk"
mv "$D"/part-*.wav "$stk"/ 2>/dev/null || :
if r=$(rec_pid); then
  mv "$D/rec.wav" "$stk/part-zzz.wav" 2>/dev/null || : > "$stk/part-zzz.wav"
  pid=${r% *}
else
  pid=
fi
rm -f "$D/rec" "$D/muted"
trap 'rm -rf "$stk"; rm -f "$job"; bar' EXIT
bar
exec 9>&-

if [ -n "$pid" ]; then
  sleep "$(awk "BEGIN{print $GRACE_MS/1000}")"
  stop_sox "$pid"
fi

files=()
for f in "$stk"/part-*.wav; do
  [ -f "$f" ] && [ "$(stat -c%s "$f")" -gt 44 ] && files+=("$f")
done
if [ ${#files[@]} -eq 0 ]; then notify "no speech detected"; exit; fi
if [ ${#files[@]} -eq 1 ]; then
  mv "${files[0]}" "$job"
else
  sox "${files[@]}" "$job" 2>>"$LOG" || { notify "could not join recording parts"; exit; }
fi
rm -rf "$stk"

if [ "$(stat -c%s "$job")" -le 44 ]; then notify "no speech detected"; exit; fi
# the server handles one request at a time, so queued jobs finish and paste in the order they stopped
for try in 1 2 3; do
  text=$(curl -sSf -m 1620 --data-binary @"$job" "$URL" 2>>"$LOG") && break
  if [ $try = 3 ]; then
    keep=~/voice-failed/$(date +%F-%H%M%S).wav
    mkdir -p ~/voice-failed; mv "$job" "$keep"
    notify "transcription failed — audio kept at $keep"; exit
  fi
  sleep 3
done
text=$(printf %s "$text" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
[ -z "$text" ] && { notify "no speech detected"; exit; }

# trailing space so back-to-back dictations don't glue words together
printf '%s ' "$text" | wl-copy
sleep 0.2
app=$(swaymsg -t get_tree | jq -r '.. | select(.focused? == true) | .app_id // empty')
# foot pastes on Ctrl+Shift+V, not Ctrl+V
case "$app" in
foot*) wtype -M ctrl -M shift -k v -m shift -m ctrl ;;
*) wtype -M ctrl -k v -m ctrl ;;
esac
notify "${text:0:80}"
