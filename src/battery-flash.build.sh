#!/bin/sh
# rebuild ../bin/battery-flash (needs wayland-scanner, wayland-protocols, gcc)
set -e
d=$(mktemp -d); trap 'rm -rf "$d"' EXIT
cp "$(dirname "$0")"/../../../../.cargo/registry/src/index.crates.io-*/wayland-protocols-wlr-*/wlr-protocols/unstable/wlr-layer-shell-unstable-v1.xml "$d" 2>/dev/null \
  || cp /usr/share/wlr-protocols/unstable/wlr-layer-shell-unstable-v1.xml "$d"
cp /usr/share/wayland-protocols/stable/viewporter/viewporter.xml \
   /usr/share/wayland-protocols/staging/single-pixel-buffer/single-pixel-buffer-v1.xml \
   /usr/share/wayland-protocols/stable/xdg-shell/xdg-shell.xml "$d"
for p in wlr-layer-shell-unstable-v1 viewporter single-pixel-buffer-v1 xdg-shell; do
  wayland-scanner client-header "$d/$p.xml" "$d/$p-client-protocol.h"
  wayland-scanner private-code "$d/$p.xml" "$d/$p.c"
done
cc -O2 -Wall -Wextra -I"$d" "$(dirname "$0")/battery-flash.c" "$d"/*.c -lwayland-client \
   -o "$(dirname "$0")/../bin/battery-flash"
