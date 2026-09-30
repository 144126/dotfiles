#!/bin/sh
if ! swaymsg -t get_outputs -r | jq -e '.[] | select(.name == "HDMI-A-1" and .active)' >/dev/null 2>&1; then
  echo '{"text": "only", "class": "only"}'
elif pgrep -x wl-mirror >/dev/null; then
  echo '{"text": "duplicated", "class": "duplicated"}'
else
  echo '{"text": "extended", "class": "extended"}'
fi
