#!/bin/sh
# Focus the window (and its workspace) that produced a clicked mako notification.
# mako only exports the notification id as $id, so resolve the app name via
# `makoctl list -j`, find the matching sway window, and focus it. sway's
# `focus` automatically switches to the workspace the window lives on.

set -u

id="${id:-}"
[ -z "$id" ] && exit 0

app=$(makoctl list -j 2>/dev/null | jq -r --argjson id "$id" '
  .[] | select(.id == $id) | (.app_name // .desktop_entry // "")' 2>/dev/null)

[ -z "$app" ] && { makoctl dismiss -n "$id" 2>/dev/null; exit 0; }

con=$(swaymsg -t get_tree 2>/dev/null | jq -r --arg app "$app" '
  .. | objects
  | select(.type? == "con" and ((.app_id? // "") != ""))
  | (.app_id | ascii_downcase | gsub("[^a-z0-9]"; "")) as $aid
  | select($aid == ($app | ascii_downcase | gsub("[^a-z0-9]"; "")))
  | .id' 2>/dev/null | head -n1)

if [ -n "$con" ]; then
  swaymsg "[con_id=$con] focus"
fi

makoctl dismiss -n "$id" 2>/dev/null
