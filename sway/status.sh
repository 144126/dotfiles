#!/bin/bash

# sway status command - inspired by bspwm lemonbar panel

WIFI_IFACE="wlp0s20f3"
CPU_STAT="/tmp/sway-cpu-stat"

# helpers for JSON output
block() {
    printf '{"full_text":"%s","color":"%s","separator":false,"separator_block_width":4},' "$1" "$2"
}
block_named() {
    printf '{"full_text":"%s","color":"%s","name":"%s","separator":false,"separator_block_width":4},' "$1" "$2" "$3"
}
null() {
    printf '{"full_text":"","separator":false,"separator_block_width":0,"min_width":0},'
}

get_battery() {
    if [ ! -d /sys/class/power_supply/BAT0 ]; then
        echo ""; return
    fi
    cap=$(cat /sys/class/power_supply/BAT0/capacity 2>/dev/null) || return
    sta=$(cat /sys/class/power_supply/BAT0/status 2>/dev/null)
    icon=""
    if [ "$sta" = "Charging" ]; then
        icon="^"
    elif [ "$cap" -lt 20 ]; then
        icon="!"
    fi
    echo "${icon}${cap}%"
}

get_network() {
    ssid=$(iw dev "$WIFI_IFACE" link 2>/dev/null | sed -n 's/.*SSID: //p')
    eth_up=false; usb_up=false
    ip link show enp0s31f6 2>/dev/null | grep -q "state UP" && eth_up=true
    for iface in /sys/class/net/enp*s*; do
        [ -d "$iface" ] || continue
        name=$(basename "$iface")
        [ "$name" = "enp0s31f6" ] && continue
        ip link show "$name" 2>/dev/null | grep -q "state UP" && usb_up=true
    done

    parts=""
    if [ -n "$ssid" ]; then
        parts="w:${ssid}"
    fi
    if $usb_up; then
        parts="${parts:+${parts}|}usb"
    fi
    if $eth_up; then
        parts="${parts:+${parts}|}eth"
    fi
    [ -n "$parts" ] && echo "$parts" || echo "none"
}

get_speed() {
    iface=""
    if ip link show enp0s31f6 2>/dev/null | grep -q "state UP"; then
        iface="enp0s31f6"
    else
        for f in /sys/class/net/enp*s*; do
            [ -d "$f" ] || continue
            name=$(basename "$f")
            [ "$name" = "enp0s31f6" ] && continue
            ip link show "$name" 2>/dev/null | grep -q "state UP" && iface="$name" && break
        done
    fi
    if [ -z "$iface" ] && iw dev "$WIFI_IFACE" link 2>/dev/null | grep -q "SSID"; then
        iface="$WIFI_IFACE"
    fi
    [ -z "$iface" ] && echo "" && return
    ~/.local/bin/netspeed "$iface" 2>/dev/null || echo ""
}

get_data() {
    [ -d "/sys/class/net/${WIFI_IFACE}/statistics" ] || { echo ""; return; }
    val=$(~/.local/bin/datacount 2>/dev/null) || return
    echo "${val}KB"
}

get_ram() {
    total=$(awk '/^MemTotal:/{print $2}' /proc/meminfo 2>/dev/null) || return
    avail=$(awk '/^MemAvailable:/{print $2}' /proc/meminfo 2>/dev/null) || return
    used_kb=$(( total - avail ))
    used_mb=$(( used_kb / 1024 ))
    used_pct=$(( used_kb * 100 / total ))
    echo "${used_mb}M(${used_pct}%)"
}

get_cpu() {
    if [ ! -f "$CPU_STAT" ]; then
        awk '/^cpu /{for(i=2;i<=NF;i++) t+=$i; print $5, t}' /proc/stat > "$CPU_STAT"
        echo ""; return
    fi
    read -r prev_idle prev_total < "$CPU_STAT"
    cur=$(awk '/^cpu /{for(i=2;i<=NF;i++) t+=$i; print $5, t}' /proc/stat)
    cur_idle=$(echo "$cur" | cut -d' ' -f1)
    cur_total=$(echo "$cur" | cut -d' ' -f2)
    idle_diff=$((cur_idle - prev_idle))
    total_diff=$((cur_total - prev_total))
    if [ "$total_diff" -gt 0 ]; then
        pct=$(( (100 * (total_diff - idle_diff)) / total_diff ))
        echo "${pct}%"
    fi
    awk '/^cpu /{for(i=2;i<=NF;i++) t+=$i; print $5, t}' /proc/stat > "$CPU_STAT"
}

get_temp() {
    t=$(cat /sys/class/thermal/thermal_zone13/temp 2>/dev/null) || return
    echo "$((t / 1000))°C"
}

get_disk() {
    df / 2>/dev/null | awk 'NR==2{sub(/%/,""); print $5"%"}' || echo ""
}

# main loop using i3bar JSON protocol
printf '{"version":1,"click_events":true}\n'
printf '[\n'

first=true
while :; do
    bat=$(get_battery)
    data=$(get_data)
    net=$(get_network)
    speed=$(get_speed)
    ram=$(get_ram)
    cpu=$(get_cpu)
    temp=$(get_temp)
    disk=$(get_disk)

    line="["
    [ -n "$speed" ] && line="${line}$(block_named " ${speed} " "#aaaaaa" "speed")"
    [ -n "$bat" ] && line="${line}$(block_named " ${bat} " "#ffffff" "bat")"
    [ -n "$data" ] && line="${line}$(block_named " d:${data} " "#aaaaaa" "data")"
    line="${line}$(block_named " ${net} " "#88c0d0" "net")"
    [ -n "$ram" ] && line="${line}$(block_named " ${ram} " "#a3be8c" "ram")"
    [ -n "$cpu" ] && line="${line}$(block_named " cpu:${cpu} " "#b48ead" "cpu")"
    [ -n "$temp" ] && line="${line}$(block_named " ${temp} " "#d08770" "temp")"
    [ -n "$disk" ] && line="${line}$(block_named " dsk:${disk} " "#ebcb8b" "disk")"

    # remove trailing comma, close array
    line="${line%,}]"

    if $first; then
        printf '%s\n' "$line"
        first=false
    else
        printf ',%s\n' "$line"
    fi

    # wait for click events from sway (replaces sleep)
    if read -t 2 -r click; then
        case "$click" in
            *'"name":"data"'*) ~/.local/bin/datacount reset 2>/dev/null ;;
            *'"name":"bat"'*)  notify-send "Battery" "$(acpi 2>/dev/null || cat /sys/class/power_supply/BAT0/capacity 2>/dev/null)%" & ;;
            *'"name":"net"'*)  notify-send "Network" "$(iw dev "$WIFI_IFACE" link 2>/dev/null | head -5)" & ;;
            *'"name":"ram"'*)  notify-send "Memory" "$(free -h | awk '/^Mem:/{print $3\"/\"$2}')" & ;;
            *'"name":"cpu"'*)  notify-send "CPU" "$(top -bn1 | awk '/^%Cpu/{print $2}')%" & ;;
            *'"name":"temp"'*) notify-send "Temperature" "$(cat /sys/class/thermal/thermal_zone*/temp 2>/dev/null | head -1 | awk '{printf \"%.1f°C\", $1/1000}')" & ;;
            *'"name":"disk"'*) notify-send "Disk" "$(df -h / | awk 'NR==2{print $3\"/\"$2\" (\"$5\")\"}')" & ;;
            *'"name":"speed"'*) notify-send "Speed" "${speed}" & ;;
        esac
    fi
done
