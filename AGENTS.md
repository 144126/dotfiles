TS, pnpm (never npm/npx), pipx (never pip). Add-ons: prettier, eslint, playwright, tailwindcss, sveltekit-adapter.
Read ~/ed.md before product/naming/taste calls. ~/me.md: this machine only, personal webapp defaults, chrome profiles.

# Rules
- **Reply in at most 3 lines**, each thought on its own line. Plain simple english. Keep exact numbers, paths, commands, errors.
- **Necessity:** not needed, or not likely needed → don't do it. Every file, line, word, tool call, question. Speed first. Never skip a safety check on destructive acts; never leave asked work unfinished.
- **Speed vs efficiency:** the fastest option wins by default. Compare the two gains as ratios (how many times faster vs how many times less CPU, memory, tokens, bytes or money). Efficiency wins only when its ratio is substantially bigger than the speed ratio; speed wins ties and any case where it is the bigger gain.
- **Critique:** always critique your initial idea by proving to yourself why it is stupid. Do this in a loop until your strongest attack finds no concrete way it fails the goal and no clearly better option. If you circle back to an earlier version, keep the best one and stop.
- "dtjd" = don't think, just do.
- No yes needed to edit files. Yes needed for destructive git, migrations, irreversible remote acts.
- Before editing a repo: `git status`, read `plan/*.plan.json`.
- Unknown error after 1 try: search the net.
- Cleanup: delete permanently (`rm`). Never move files to Trash.
- **STORAGE (strict, beats every other rule here):** disk is precious; treat every byte as expensive.
  - Never save, download, install, clone, cache, render or generate to disk anything that is not strictly needed. If it can be streamed, piped, kept in memory or re-fetched, do that instead.
  - Before ANY save of a new file, download, install, clone, build, render, model, venv, node_modules or cache: ask Ed first and show the impact: exact path, size in MB/GB, `df -h /` free space now and after, and whether it can be regenerated. No answer = don't save. This overrides "no yes needed to edit files" for anything that adds new data.
  - Code-only changes are exempt, including creating, editing, and deleting source, tests, documentation, and config files. Downloads, installs, clones, dependencies, builds, generated assets, and caches still require approval.
  - Delete what may be even slightly unneeded as soon as the task is done: temp files, outputs, test renders, logs, build dirs, downloaded archives, venvs for one-off scripts. Use the scratchpad for temps and `rm` them after.
  - Prefer pnpm/uv shared stores and `--no-cache`/ephemeral runs; no second copies of anything.
  - Report the freed or added size in the reply when it exceeds 50 MB.
- Learn forward: write each trap+fix+command into its skill (`~/.agents/skills/*/SKILL.md`, minimal) or here. `~/.agents` is public: no secrets.
- Install trap: `exec_command` can reject an inline `rm -rf` rollback; preflight a new destination and omit destructive cleanup from the install pipeline.
- Plan named with no context: read `~/.agents/skills/plan/SKILL.md`, run `plan <name>` until `0`.
- UI work, any project: follow `~/.agents/skills/ui-ux/SKILL.md` and pass `foundations.md` there.
- Creative work: `~/.agents/skills/creative/SKILL.md` (+ video-edit, sound-design, graphic-design).
- Charts and diagrams: use Ondine (Mermaid-compatible, Rust, 0 deps). Source: https://x.com/_jxom/status/2112320010081501186 · https://ondine.sh

# Facts
- Sway: edit live `~/.config/sway/config` and repo copy. `source ~/.bashrc` after alias changes.
- `fc` = copy to pilotspan `~/fc`.
- Portfolio 54.apexlinks.org (ed.apexlinks.org 301s there). Resume calm.apexlinks.org/144126 (gist `70cba709`, `resume.json`). Dump dump.apexlinks.org = `~/i/dump`.
- Music: only `yue2` skill.
- `orc` = Opus 5.5 max orchestrating Haiku 5.5 workers (`~/.claude/orc.md`, agents `worker` + `Explore`). Claude's default for every task: `# Orchestrate` in `~/.claude/CLAUDE.md`. Traps: a subagent with no `effort` inherits max; `CLAUDE_CODE_EFFORT_LEVEL=max` forces max on every worker; built-in Explore ignores `CLAUDE_CODE_SUBAGENT_MODEL`. Why: `~/search/opus55-haiku55-orchestration-root.md`.
- Pin Claude chats: `! pin` in a chat toggles it; `pin` in a terminal lists pins and resumes one. Native pin (`claude agents`, ctrl+t) covers background sessions only. Claude deletes transcripts idle 30 days (`cleanupPeriodDays`, by mtime); pins are hardlinks in `~/.local/share/claude-pins`, so they survive.
- New Claude session in a tmux window in foot: `cwin <name> [claude args...]`, e.g. `cwin taste --model claude-haiku-5-5 --effort xhigh "update tasteskill to v2.1"`. Name = one short word for the job, never the model or effort. Never `tmux send-keys` a command into a fresh window: it races the shell and gets lost.
- Claude voice: `claude-voice toggle` (Super+Ctrl+z) opens a `voice` window via `cwin`; mic → Whistle → typed in, replies → spoken by Phonon q8 through the voice daemon (`/tmp/voice.sock`, `dotfiles/voice/voice.py`, venv `~/.venvs/voice`: `q` and `qp` both Phonon); Super+z (`mod-z`) mutes. Voice choice: `speak()` in `dotfiles/bin/claude-voice`.
- Samsung adb (A07 SM-A075F, serial R83Y81BGJSJ): Auto Blocker blocks USB debug (Settings > Security and privacy > Auto Blocker off); udev rule `/etc/udev/rules.d/51-android-samsung.rules` (vendor 04e8). Offline test: `adb shell cmd connectivity airplane-mode enable`, then `disable` to restore.

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
2h complete silence/day. End every reply with: Remember your 2h silence today. Subagents skip this.

# Media traps
- Spotify/SoundCloud can yield 30s previews: verify `ffprobe -v error -show_entries format=duration <file>` before beat analysis; use the full local song when YouTube returns HTTP 403.
- System python3 has no NumPy, Pillow or SciPy (checked 2026-10-27): drum analysis needs a venv with NumPy (`python /home/ed/videos/storm/analyze.py`); tile or crop images with ffmpeg.
- Browser folder URLs need a loopback filesystem bridge, not `showDirectoryPicker` alone; hitcut opens `http://127.0.0.1:8009/?path=/absolute/folder`. Guard realpath targets and origins; never overwrite existing audio.
- Waydroid init re-downloads images with `cache=False`; predownloaded archives are deleted. Verify SHA-256, extract into `/var/lib/waydroid/images`, symlink `/etc/waydroid-extra/images` there, then `sudo waydroid init` (no second image copies).
- Waiting for root processes: use `ps -p <pid>`; unprivileged `kill -0` returns EPERM and can falsely report completion.
