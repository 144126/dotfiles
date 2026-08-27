# Pi — response format (Pi-specific, TTS only)

For longer replies, start with a short WhatsApp-style TLDR for TTS, then a separator, then the normal reply. For short replies, skip the TLDR entirely.

- Longer reply: 1-2 plain sentences before ` ||| ` as TLDR, fluid speech, under ~200 chars, no markdown. Do not label it TLDR. Must extremely concisely touch every issue and section covered in the full response, even if just a few words per section, while staying really short. Then ` ||| ` separator, then normal reply with full markdown and formatting.
- Short reply: no TLDR, no separator, just the reply as normal. Pi decides based on length; if the whole reply is already 1-2 short sentences, don't add a TLDR.
- TTS reads only the part before ` ||| ` if present, otherwise the whole reply.
- Example long: "fixed the wireguard mtu and blue tmux thing, all good now - plus mantle models showing and dotfiles updated ||| Full details below with code..."
- Example short: "all synced, ready to go"

# Session auto-rename

After the first user message, as the last step before finishing your first response, rename the session to a short suitable name (3-6 words) based on that first message and your answer. Use `PI_SESSION_FILE` env var — edit the `.jsonl` and update the `{"type":"session_info","name":"..."}` line via python json. Keep it short, lowercase or Title Case, no filler.

# Condensed output

HTML only, dark theme, no markdown. Auto-open only if display then Chrome: `{ [ -n "$DISPLAY" ] || [ -n "$WAYLAND_DISPLAY" ]; } && command -v google-chrome-stable >/dev/null && nohup google-chrome-stable "file://$html" >/dev/null 2>&1 &`.
