#!/bin/sh
s=$(swaymsg -t get_outputs -r | jq -r '[.[] | select(.focused == true)][0].scale // .[0].scale')
printf '{"text":"%sx"}\n' "$(awk -v s="$s" 'BEGIN { printf "%g", s }')"
