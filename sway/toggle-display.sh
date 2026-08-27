#!/bin/sh
HDMI=$(swaymsg -t get_outputs -r | jq -r '.[] | select(.name == "HDMI-A-1")')
ACTIVE=$(echo "$HDMI" | jq -r '.active')
X=$(echo "$HDMI" | jq -r '.rect.x')
Y=$(echo "$HDMI" | jq -r '.rect.y')
EDP_X=$(swaymsg -t get_outputs -r | jq -r '.[] | select(.name == "eDP-1") | .rect.x')

if [ "$ACTIVE" = "true" ] && [ "$X" = "$EDP_X" ]; then
  swaymsg "output HDMI-A-1 disable"
elif [ "$ACTIVE" = "true" ]; then
  swaymsg "output HDMI-A-1 position 0,0; output eDP-1 position 0,0"
else
  LAPTOP_W=$(swaymsg -t get_outputs -r | jq -r '.[] | select(.name == "eDP-1") | .rect.width')
  swaymsg "output HDMI-A-1 enable position 0,0; output eDP-1 enable position ${LAPTOP_W},0"
fi
pkill -RTMIN+2 waybar 2>/dev/null
