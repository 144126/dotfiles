#!/bin/sh
# Types the last N cliphist entries into the focused input, each followed by a space.
# order=normal  -> oldest-of-the-N first, most recent last (chronological)
# order=reverse -> most recent first, oldest-of-the-N last
count="$1"
order="$2"
lines=$(cliphist list | head -n "$count" | grep -v '\[\[ binary data')
[ "$order" = normal ] && lines=$(printf '%s\n' "$lines" | tac)
printf '%s\n' "$lines" | while IFS= read -r line; do
    [ -z "$line" ] && continue
    text=$(printf '%s\n' "$line" | cliphist decode)
    wtype -- "$text"
    wtype -- " "
done
