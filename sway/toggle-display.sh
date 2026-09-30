#!/bin/sh
w=$(swaymsg -t get_outputs -r | jq -r '.[] | select(.name == "eDP-1") | .rect.width')

if pgrep -x wl-mirror >/dev/null; then
  pkill -x wl-mirror
  swaymsg "output HDMI-A-1 disable"
elif swaymsg -t get_outputs -r | jq -e '.[] | select(.name == "HDMI-A-1" and .active)' >/dev/null; then
  focus=$(swaymsg -t get_workspaces -r | jq -r '.[] | select(.focused) | .name')
  swaymsg -t get_workspaces -r | jq -r '.[] | select(.output == "HDMI-A-1" and .name != "mirror") | .name' | while read -r ws; do
    swaymsg "workspace $ws; move workspace to output eDP-1"
  done
  # A named workspace keeps the number keys for the laptop.
  # sway exec opens the mirror on the focused workspace, so it can't steal focus.
  # The gap stops the pointer from sliding onto the projector.
  swaymsg "focus output HDMI-A-1; rename workspace to mirror; exec wl-mirror --fullscreen-output HDMI-A-1 eDP-1; workspace $focus; output HDMI-A-1 position $((w * 2)) 0; output eDP-1 position 0 0"
else
  swaymsg "output HDMI-A-1 enable position 0 0; output eDP-1 enable position $w 0"
fi
pkill -RTMIN+2 waybar 2>/dev/null
