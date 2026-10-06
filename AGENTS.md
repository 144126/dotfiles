TS, pnpm (never npm/npx), pipx (never pip). Add-ons: prettier, eslint, vitest, playwright, tailwindcss, sveltekit-adapter.
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
- Forms: fill facts; write prose fields from Ed's real facts. Rich text: click, `Control+a`, `Delete`, fill. Other pages in new tab.

# Facts
- Sway: edit live `~/.config/sway/config` and repo copy. `source ~/.bashrc` after alias changes.
- `cf` = Cloudflare CLI. `fc` = copy to pilotspan `~/fc`.
- Portfolio ed.apexlinks.org. Resume calm.apexlinks.org/144126 (gist `70cba709`, `resume.json`). Dump dump.apexlinks.org = `~/i/dump`.
- CF token `opencode-token-manager` has `API Tokens Edit`: add missing permissions yourself.
- STT: only Whistle, `stt <file>`. Links: `cobalt <url>` then `stt`. Save to `~/Downloads`.
- Music: only `yue2` skill. Lightning: org `144126-org`, teamspace `default-project`, key only in `~/.lightning/credentials.json`.
- OpenRouter real balance: `/api/v1/credits` (`total_credits - total_usage`), not `/key`. Models: `/api/v1/models?output_modalities=text`, `/api/v1/videos/models` (check durations/ratios/resolutions).
- `HF_TOKEN` in shell rc files for `MuScriptor/muscriptor-large`.

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
- Webapps deploy on push only. Never `wrangler deploy`. New Worker: GitHub repo (private) → `curl -X POST .../accounts/<acct>/workers/workers -d '{"name":"<app>","subdomain":{"enabled":true}}'` → copy ids from `cf builds workers get <tag>` → `cf builds workers create ...` (build `pnpm run build`, deploy `pnpm exec wrangler deploy`) → commit `pnpm-workspace.yaml` (`packages: ['.']`, `allowBuilds: {workerd: true, esbuild: true}`) → push → `cf builds list --external-script-id <tag>`.
- Pages: `cf pages create ... --source-type github`, then push. Alias `<name>-xxxx.pages.dev`.
- SvelteKit+CF: `private` cache on auth pages; one robots.txt; SPA fallback needs no root `404.html`.
- Workers Builds fails `wrangler types --check` when local `.dev.vars` adds bindings: build script is `vite build` only.

# Browser
`ab-1440fl` (headless, 9223). Visible `chrome-1440fl` only if Ed asks, then `ab-1440fl-sync`. Google login: `1440fl@gmail.com`. Open built media in Chrome if a display exists.

# Memory
Start: `~/.optmem/memo wake`. Note: `memo note "<≤280 chars>"`. Recall: `memo recall <regex>`. Never edit `~/.optmem/memory`. Subagents: "You are a subagent. Don't run memo."
