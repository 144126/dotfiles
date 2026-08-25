# dotfiles

Public configs for foot + tmux clickable hyperlinks (OSC 8) fix.

## what was fixed 2026-08-25

**Problem:** markdown `[text](url)` links underlined but `Ctrl+Click` did nothing in foot+tmux.

**Root cause:**
- tmux `allow-passthrough` alone doesn't enable hyperlinks — needs `terminal-features hyperlinks`
- `mouse on` makes tmux eat clicks, foot never sees them — tmux must handle `#{mouse_hyperlink}` itself

**Fix:**
- `tmux/tmux.conf`:
  ```tmux
  set -g allow-passthrough on
  set -as terminal-features ",foot*:hyperlinks"
  set -as terminal-features ",*:hyperlinks"
  unbind-key -T root C-MouseDown1Pane
  bind-key -T root C-MouseUp1Pane if-shell -F "#{mouse_hyperlink}" "run-shell -b \"xdg-open '#{mouse_hyperlink}' >/dev/null 2>&1 &\"" ""
  ```
- `foot/foot.ini`:
  ```ini
  [url]
  osc8-underline=always
  launch=xdg-open ${url}
  protocols=http, https, ftp, ftps, file, gemini, gopher
  ```

**Usage:**
- plain url `https://example.com` → `Ctrl+Shift+u` → press label letter
- OSC8 `printf '\033]8;;https://example.com\033\\text\033]8;;\033\\\n'` → `Ctrl+Click` (no Shift), silent `xdg-open`

Test:
```bash
printf '\033]8;;https://example.com\033\\CLICK ME\033]8;;\033\\\n'
```
