TS, pnpm (never npm/npx), pipx (never pip). Add-ons: prettier, eslint, playwright, tailwindcss, sveltekit-adapter.
Read ~/ed.md before product/naming/taste calls. ~/me.md: this machine only, personal webapp defaults, chrome profiles.

# Rules
- **Reply in 1 line.** Plain simple english. Keep exact numbers, paths, commands, errors.
- **Necessity:** not needed, or not likely needed → don't do it. Every file, line, word, tool call, question. Speed first. Never skip a safety check on destructive acts; never leave asked work unfinished.
- "dtjd" = don't think, just do.
- No yes needed to edit files. Yes needed for destructive git, migrations, irreversible remote acts.
- Before editing a repo: `git status`, read `plan/*.plan.json`.
- Unknown error after 1 try: search the net.
- Cleanup: drafts to Trash. `/tmp` files: `mv` to `~/.local/share/Trash/files/` + `info/<name>.trashinfo` (`Path=`, `DeletionDate=`).
- Learn forward: write each trap+fix+command into its skill (`~/.agents/skills/*/SKILL.md`, minimal) or here. `~/.agents` is public: no secrets.
- Plan named with no context: read `~/.agents/skills/plan/SKILL.md`, run `plan <name>` until `0`.
- Creative work: `~/.agents/skills/creative/SKILL.md` (+ video-edit, sound-design, graphic-design).

# Facts
- Sway: edit live `~/.config/sway/config` and repo copy. `source ~/.bashrc` after alias changes.
- `fc` = copy to pilotspan `~/fc`.
- Portfolio 54.apexlinks.org (ed.apexlinks.org 301s there). Resume calm.apexlinks.org/144126 (gist `70cba709`, `resume.json`). Dump dump.apexlinks.org = `~/i/dump`.
- Music: only `yue2` skill.
- `orc` = Opus 5.5 max orchestrating Haiku 5.5 workers (`~/.claude/orc.md`, agents `worker` + `Explore`). Claude's default for every task: `# Orchestrate` in `~/.claude/CLAUDE.md`. Traps: a subagent with no `effort` inherits max; `CLAUDE_CODE_EFFORT_LEVEL=max` forces max on every worker; built-in Explore ignores `CLAUDE_CODE_SUBAGENT_MODEL`. Why: `~/search/opus55-haiku55-orchestration-root.md`.
- Pin Claude chats: `! pin` in a chat toggles it; `pin` in a terminal lists pins and resumes one. Native pin (`claude agents`, ctrl+t) covers background sessions only. Claude deletes transcripts idle 30 days (`cleanupPeriodDays`, by mtime); pins are hardlinks in `~/.local/share/claude-pins`, so they survive.

# Commits
Conventional Commits: `<type>(<scope>): <imperative, ≤50, lowercase, no period>`, blank line, body at 72 (what+why, `- ` bullets), trailers last. Body required for breaking, security, migration, revert.

# Code
- snake_case. Single-letter keys for db/types/JSON/load returns, commented at definition. Stored enums single chars.
- No comments except non-obvious why. No single-use vars. Extreme simplicity.
- One owner module per domain; grep before writing, never duplicate; no business logic in templates/routes. Refactor first, then change.
- Dev server only if none running. Tail `.log` first. UI change: look with agent-browser.
- App tests: TesterArmy `e2e` (`pnpm add -D e2e @e2e-dev/web`, `pnpm exec e2e init`, `pnpm exec e2e run`). Docs `node_modules/e2e/docs`.

# Git & deploy
- Commit+push done work without asking. Never commit `.env` or unrelated changes.

# Memory
Start: `~/.optmem/memo wake`. Note: `memo note "<≤280 chars>"`. Recall: `memo recall <regex>`. Never edit `~/.optmem/memory`. Subagents: "You are a subagent. Don't run memo."
Nap (main agent only): when a memo command prints `Run: ~/.optmem/memo nap <lo>-<hi> "<line>"`, run that command with a one-line summary. Ed's standing order.
2h complete silence/day. After every `memo wake`, run `silence`. If it exits 1 (missing file, or date ≠ today), end every reply with: 2h silence done today? If Ed says done/yes, run `silence done` and stop asking that calendar day. Subagents skip this.

# Media traps
- Spotify/SoundCloud can yield 30s previews: verify `ffprobe -v error -show_entries format=duration <file>` before beat analysis; use the full local song when YouTube returns HTTP 403.
- System Python has NumPy/Pillow but no SciPy: drum analysis can use NumPy FFT; `python /home/ed/videos/storm/analyze.py`.
- Browser folder URLs need a loopback filesystem bridge, not `showDirectoryPicker` alone; hitcut opens `http://127.0.0.1:8009/?path=/absolute/folder`. Guard realpath targets and origins; never overwrite existing audio.
