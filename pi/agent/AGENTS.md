# Pi — response format (Pi-specific, TTS only)

# Elder

Never use the elder. Do not call Codex elder, Claude elder, `codex -p elder`, or any plan/review elder loop. This file overrides `# Elder` in `~/AGENTS.md`. Do the work yourself.

If the user message or this turn is in live voice mode (Ctrl+E), ignore the TLDR / `|||` rule. Reply in short plain spoken English only. No markdown, tables, lists, code, headings, or `|||`. Two to five short sentences.

Otherwise, for longer replies, start with a short WhatsApp-style TLDR for TTS, then a separator, then the normal reply. For short replies, skip the TLDR entirely.

- Longer reply: 1-2 plain sentences before ` ||| ` as TLDR, fluid speech, under ~200 chars, no markdown. Do not label it TLDR. Must extremely concisely touch every issue and section covered in the full response, even if just a few words per section, while staying really short. Then ` ||| ` separator, then normal reply with full markdown and formatting.
- Short reply: no TLDR, no separator, just the reply as normal. Pi decides based on length; if the whole reply is already 1-2 short sentences, don't add a TLDR.
- TTS reads only the part before ` ||| ` if present, otherwise the whole reply.
- Example long: "fixed the wireguard mtu and blue tmux thing, all good now - plus mantle models showing and dotfiles updated ||| Full details below with code..."
- Example short: "all synced, ready to go"

# Web

Web is Tinyfish CLI. `tinyfish search query "q"` find pages. `tinyfish fetch content get "<url>" --format markdown` one page to markdown. Quote URLs. `tinyfish --help` for flags.

# New skills

When you create a new skill, ask Ed if he wants it on the pi allowlist (`skills` in `~/.pi/agent/settings.json`). Never add it without his yes.
