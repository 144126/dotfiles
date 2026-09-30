#!/bin/sh
base=${XDG_RUNTIME_DIR:-/run/user/$(id -u)}
store=$base/sway-ws-scale
pidfile=$base/sway-ws-scale.pid

ws_key() {
  swaymsg -t get_workspaces -r | jq -r '.[] | select(.focused == true) | if .num >= 0 then (.num | tostring) else .name end'
}

ws_out() {
  swaymsg -t get_workspaces -r | jq -r '.[] | select(.focused == true) | .output'
}

poke() {
  pkill -RTMIN+3 waybar 2>/dev/null
}

save() {
  mkdir -p "$store"
  printf '%s\n' "$2" > "$store/$1"
}

load() {
  if [ -f "$store/$1" ]; then
    cat "$store/$1"
  else
    echo "1"
  fi
}

apply() {
  key=$(ws_key) || return 1
  [ -n "$key" ] || return 1
  out=$(ws_out) || return 1
  [ -n "$out" ] || return 1
  want=$(load "$key")
  json=$(swaymsg -t get_outputs -r) || return 1
  cur=$(echo "$json" | jq -r --arg n "$out" '.[] | select(.name == $n) | .scale')
  same=$(awk -v a="$cur" -v b="$want" 'BEGIN { d = a - b; if (d < 0) d = -d; print (d < 0.002) ? 1 : 0 }')
  [ "$same" = 1 ] && return 0
  swaymsg output "$out" scale "$want"
  poke
}

step() {
  dir=$1
  json=$(swaymsg -t get_outputs -r) || exit 1
  name=$(echo "$json" | jq -r '[.[] | select(.focused == true)][0].name // .[0].name')
  cur=$(echo "$json" | jq -r --arg n "$name" '.[] | select(.name == $n) | .scale')
  new=$(awk -v c="$cur" -v d="$dir" 'BEGIN {
    n = (d == "up") ? c + 0.25 : c - 0.25
    if (n < 1) n = 1
    if (n > 2) n = 2
    printf "%.2f", n
  }')
  swaymsg output "$name" scale "$new"
  poke
  key=$(ws_key)
  [ -n "$key" ] && save "$key" "$new"
}

reset() {
  key=$(ws_key) || exit 1
  [ -n "$key" ] || exit 1
  rm -f "$store/$key"
  apply
}

listen() {
  if [ -f "$pidfile" ]; then
    old=$(cat "$pidfile")
    if [ -n "$old" ] && [ "$old" != "$$" ]; then
      pkill -P "$old" 2>/dev/null
      kill "$old" 2>/dev/null
    fi
  fi
  echo $$ > "$pidfile"
  drop() { [ "$(cat "$pidfile" 2>/dev/null)" = "$$" ] && rm -f "$pidfile"; }
  trap 'drop; exit' INT TERM HUP
  trap drop EXIT
  apply
  swaymsg -t subscribe -m '["workspace"]' | while read -r line; do
    change=$(echo "$line" | jq -r '.change')
    [ "$change" = focus ] && apply
  done
}

case $1 in
  up|down) step "$1" ;;
  apply) apply ;;
  reset) reset ;;
  listen) listen ;;
  *) exit 1 ;;
esac
