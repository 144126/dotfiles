#!/usr/bin/env python3
# Remembers position/size of Chrome's Document Picture-in-Picture windows
# (WhatsApp call mini-player, Spotify mini-player, etc) across reopenings,
# keyed by the window's app name (first word of its title).
import i3ipc
import json
import os
import re
import sys

STATE_FILE = os.path.expanduser("~/.config/sway/pip-state.json")
PID_FILE = os.path.expanduser("~/.config/sway/pip-remember.pid")
LOG_FILE = os.path.expanduser("~/.config/sway/pip-remember.log")
SUFFIX_RE = re.compile(r"Google Chrome")


def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")

# single-instance guard so `exec_always` on sway reload doesn't stack daemons
if os.path.exists(PID_FILE):
    try:
        with open(PID_FILE) as f:
            os.kill(int(f.read().strip()), 0)
        sys.exit(0)  # already running
    except (OSError, ValueError):
        pass
with open(PID_FILE, "w") as f:
    f.write(str(os.getpid()))


def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def is_pip(con):
    return con.app_id == "google-chrome" and con.name and not SUFFIX_RE.search(con.name)


def key_for(con):
    return con.name.split(" ")[0]


applied_ids = set()


def on_window(i3, event):
    try:
        con = event.container
        if not is_pip(con):
            return

        state = load_state()
        k = key_for(con)

        if event.change in ("new", "title") and con.id not in applied_ids:
            r = state.get(k)
            if r:
                i3.command(
                    f'[con_id={con.id}] floating enable, '
                    f'resize set {r["w"]} {r["h"]}, '
                    f'move position {r["x"]} {r["y"]}'
                )
            applied_ids.add(con.id)

        elif event.change in ("move", "floating"):
            rect = con.rect
            state[k] = {"x": rect.x, "y": rect.y, "w": rect.width, "h": rect.height}
            save_state(state)

        elif event.change == "close":
            applied_ids.discard(con.id)
    except Exception as e:
        log(f"on_window error: {e!r}")


while True:
    try:
        conn = i3ipc.Connection()
        conn.on("window", on_window)
        conn.main()
    except Exception as e:
        log(f"connection lost: {e!r}, reconnecting")
