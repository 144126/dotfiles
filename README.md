# dotfiles — exact replica of this laptop's sway/waybar/appsearch + pi + bluetooth

Public configs to replicate sway, waybar, app launcher, foot, tmux, bluetooth and Pi on another Void Linux laptop.

## What's in here (all symlinked, no copy)

- `sway/` → `~/.config/sway/` — `config` (Mod4, `swaybar_command waybar`, `set $menu combined-menu`, `Mod4+d`, pip-remember, clip-multi), `commands.txt`, `clip-multi.sh`, `toggle-display.sh`, `status.sh`, `extend.sh`, `pip-remember.py`
- `waybar/` → `~/.config/waybar/` — `config.jsonc` ( `sway/workspaces` left, `tray | custom/display | custom/speed | custom/data | network | cpu | memory | temperature | disk | battery | custom/gemini | clock` right, height 24), `style.css` (#323232), `display-mode.sh`, `speed.sh`
- `mako/` → `~/.config/mako/` — `config` (top-right, border, `on-button-left` focus)
- `foot/` → `~/.config/foot/` — `foot.ini` (OSC8 underline, `launch=xdg-open`)
- `tmux/` → `~/.tmux.conf`
- `ssh/` → `~/.ssh/config` (LocalForward 3000/3001/3690, RemoteForward 18082/18083, ControlMaster)
- `bluetooth/` → `/etc/bluetooth/main.conf` (reference, default) + pipewire bluetooth via `libspa-bluetooth`
- `bin/` → `~/.local/bin/` — `combined-menu` (appsearch: `j4-dmenu-desktop` + `commands.txt` → `wmenu -i -l 12`, `Mod4+d`), `battery-notify.sh`, `netspeed`, `datacount`, `sway-voice-global.sh`, `mako-focus-notification.sh`, `say` (TTS), `pisync` (Pi sync)
- `AGENTS.md` → `~/AGENTS.md`, `ed.md` → `~/ed.md`, `me.md` → `~/me.md`, `pi/` → `~/.pi/agent/` (Pi TTS `|||`)

All originals are `ln -sf ~/i/144126/dotfiles/...` so editing `~/.config/sway/config` edits the repo directly.

## Packages to install on the new laptop (Void Linux)

```bash
xbps-install -S sway Waybar swaybg autotiling python3-i3ipc \
  wmenu mako foot foot-terminfo \
  wl-clipboard cliphist grim slurp flameshot \
  light playerctl jq CopyQ \
  blueman bluez libspa-bluetooth pipewire wireplumber \
  jq playerctl light
```

For appsearch to work: `wmenu` is the menu, `j4-dmenu-desktop` is used by `combined-menu` to index `/usr/share/applications` — install it:

```bash
xbps-install -S j4-dmenu-desktop wmenu
```

Wallpaper: `~/pics/dreamy_nostalgic_720p.png` (used in `sway/config` `output "*" bg ... fill`) — copy `~/pics/` too.

## Bluetooth

Needed for `blueman-applet` in sway (`exec blueman-applet`) and pipewire audio:

- Packages: `bluez`, `blueman`, `libspa-bluetooth` (pipewire bluetooth plugin), `pipewire`, `wireplumber`
- Services (runit, Void):
  ```bash
  sudo ln -s /etc/sv/bluetoothd /var/service/      # bluetooth daemon
  sudo ln -s /etc/sv/dbus /var/service/            # if not already
  # pipewire is user service, sway does `exec pipewire` via config, plus `wireplumber`
  ```
- No custom `~/.config/blueman` needed; `libspa-bluetooth` + `blueman-applet` + `waybar` tray gives the icon. `bluetooth/main.conf` in repo is the default `/etc/bluetooth/main.conf` for reference.

Also in sway: `exec blueman-applet`, `exec CopyQ`, `exec wl-paste --watch cliphist store`, `exec mako`.

## Replicate on new laptop

```bash
git clone https://github.com/144126/dotfiles ~/i/144126/dotfiles
# symlinks (or run install script if you add one):
ln -sf ~/i/144126/dotfiles/sway/config ~/.config/sway/config
ln -sf ~/i/144126/dotfiles/sway/commands.txt ~/.config/sway/commands.txt
ln -sf ~/i/144126/dotfiles/sway/clip-multi.sh ~/.config/sway/clip-multi.sh
ln -sf ~/i/144126/dotfiles/sway/toggle-display.sh ~/.config/sway/toggle-display.sh
ln -sf ~/i/144126/dotfiles/sway/status.sh ~/.config/sway/status.sh
ln -sf ~/i/144126/dotfiles/sway/extend.sh ~/.config/sway/extend.sh
ln -sf ~/i/144126/dotfiles/sway/pip-remember.py ~/.config/sway/pip-remember.py
ln -sf ~/i/144126/dotfiles/waybar/config.jsonc ~/.config/waybar/config.jsonc
ln -sf ~/i/144126/dotfiles/waybar/style.css ~/.config/waybar/style.css
ln -sf ~/i/144126/dotfiles/waybar/display-mode.sh ~/.config/waybar/display-mode.sh
ln -sf ~/i/144126/dotfiles/waybar/speed.sh ~/.config/waybar/speed.sh
ln -sf ~/i/144126/dotfiles/mako/config ~/.config/mako/config
ln -sf ~/i/144126/dotfiles/foot/foot.ini ~/.config/foot/foot.ini
ln -sf ~/i/144126/dotfiles/tmux/tmux.conf ~/.tmux.conf
ln -sf ~/i/144126/dotfiles/ssh/config ~/.ssh/config
ln -sf ~/i/144126/dotfiles/bin/combined-menu ~/.local/bin/combined-menu
ln -sf ~/i/144126/dotfiles/bin/battery-notify.sh ~/.local/bin/battery-notify.sh
ln -sf ~/i/144126/dotfiles/bin/netspeed ~/.local/bin/netspeed
ln -sf ~/i/144126/dotfiles/bin/datacount ~/.local/bin/datacount
ln -sf ~/i/144126/dotfiles/AGENTS.md ~/AGENTS.md
ln -sf ~/i/144126/dotfiles/ed.md ~/ed.md
ln -sf ~/i/144126/dotfiles/me.md ~/me.md
# then reload
swaymsg reload; pkill -USR2 waybar; makoctl reload
```

Bar will be identical: `Mod4+d` → `combined-menu` (desktop apps + commands.txt) via `wmenu`, waybar shows workspaces, tray, display/speed/data, network, cpu, ram, temp, disk, battery, gemini, clock.

## foot + tmux clickable hyperlinks (OSC 8) 2026-08-25

- `tmux/tmux.conf`: `allow-passthrough on`, `terminal-features hyperlinks`, `C-MouseUp1Pane` → `xdg-open '#{mouse_hyperlink}'`
- `foot/foot.ini`: `[url] osc8-underline=always, launch=xdg-open`

Test: `printf '\033]8;;https://example.com\033\\CLICK ME\033]8;;\033\\\n'` → `Ctrl+Click`
