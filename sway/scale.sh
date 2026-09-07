#!/bin/sh
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
pkill -RTMIN+3 waybar 2>/dev/null
