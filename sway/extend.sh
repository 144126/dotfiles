#!/bin/sh
sway-mirror --stop 2>/dev/null
LAPTOP=$(swaymsg -t get_outputs -r | jq -r '.[] | select(.name == "eDP-1")')
LAPTOP_W=$(echo "$LAPTOP" | jq -r '.rect.width')
swaymsg "output HDMI-A-1 enable position 0,0; output eDP-1 enable position ${LAPTOP_W},0"
pkill -RTMIN+2 waybar 2>/dev/null
