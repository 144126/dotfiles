#!/bin/sh
IFACE=""
WIFI_IFACE="wlp0s20f3"
if ip link show enp0s31f6 2>/dev/null | grep -q "state UP"; then
    IFACE="enp0s31f6"
else
    for f in /sys/class/net/enp*s*; do
        [ -d "$f" ] || continue
        name=$(basename "$f")
        [ "$name" = "enp0s31f6" ] && continue
        ip link show "$name" 2>/dev/null | grep -q "state UP" && IFACE="$name" && break
    done
fi
[ -z "$IFACE" ] && iw dev "$WIFI_IFACE" link 2>/dev/null | grep -q "SSID" && IFACE="$WIFI_IFACE"
[ -z "$IFACE" ] && exit 1
~/.local/bin/netspeed "$IFACE" 2>/dev/null || exit 1
