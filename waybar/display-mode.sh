#!/bin/sh
OUTPUTS=$(swaymsg -t get_outputs -r 2>/dev/null)
HDMI=$(echo "$OUTPUTS" | jq -r '.[] | select(.name == "HDMI-A-1") | {active, x: .rect.x, y: .rect.y}' 2>/dev/null)
if [ -z "$HDMI" ] || [ "$(echo "$HDMI" | jq -r '.active')" != "true" ]; then
  echo '{"text": "only", "class": "only"}'
  exit 0
fi
HDMI_POS=$(echo "$HDMI" | jq -r '"\(.x),\(.y)"')
EDP_POS=$(echo "$OUTPUTS" | jq -r '.[] | select(.name == "eDP-1") | "\(.rect.x),\(.rect.y)"')
if [ "$HDMI_POS" = "$EDP_POS" ]; then
  echo '{"text": "duplicated", "class": "duplicated"}'
else
  echo '{"text": "extended", "class": "extended"}'
fi
