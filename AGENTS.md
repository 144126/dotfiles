TS, pnpm (never npm/npx), pipx (never pip). Add-ons: prettier, eslint, playwright, tailwindcss, sveltekit-adapter.
Read ~/ed.md before product/naming/taste calls. ~/me.md: this machine only, personal webapp defaults, chrome profiles.

# Elder

The main agent is the student. Claude uses `elder`: Opus at max effort. Codex runs the elder in a separate `codex exec` session: `gpt-6.1-sol` at max effort, with explicit read-only permissions and approval disabled. Reuse that session for planning and review. Do not spawn the Codex elder as a native child of a student with write access: Codex can carry the student's permissions into that child. Using the elder is Ed's standing request. Necessity and Speed never cut it.

The elder plans, writes prose, and critiques. It may read relevant files and search during planning and review. Codex may run inspection commands within its enforced read-only sandbox. Every Codex start and resume must keep those permissions and the disabled action tools. The elder never changes files or services, installs tools, contacts people, commits, pushes, or deploys. The student does the work that changes anything.

Codex uses `~/.codex/elder.config.toml`. Start with `codex -p elder -s read-only -a never exec --skip-git-repo-check --json -`. Resume with `codex -p elder -s read-only -a never exec resume --skip-git-repo-check --json <ID> -`. Pass the brief through stdin. Keep the ID from `thread.started` and read the completed answer before acting.

**When.** Call it before anything beyond a typo, a rename, one config line, or a plain fact in a form. New code always needs it. Call it for:
- Text for people: form answers, emails, messages, cover letters, resumes, stories, and scripts. It writes the words.
- Research: ask for the angle, search terms, focus, what to skip, and when to stop.
- Job and freelance work; product, naming, and taste decisions; costly or hard-to-undo work.
- Being stuck: a fix failed, facts conflict, or the approach needs to change.

Skip when you are the elder, already Opus, Fable, or `gpt-6-astra`, on `dtjd`, or inside a `plan` step.

**Brief.** Look first: read relevant files and run needed checks. Give the elder:
- Ed's exact request and what counts as done.
- Relevant facts, excerpts, errors, check results, and rules.
- Your proposed next step and a clear question.

In the first brief, write: `You are a subagent. Don't run memo.` Keep the elder's agent or session ID and reuse it for the task.

**After.** Wait until the elder returns a complete answer before doing the work it is planning. A timeout, a session ID, or a running status is not an answer. Keep waiting. It may inspect anything relevant that the brief lacks. If it replies `NEED:`, get those facts and reply to the same elder. Follow its advice. If facts contradict it, return the facts; never quietly override it. Use its prose word for word.

**Review.** After doing the work, return to the same elder for strict critique. Send the result, diff, every changed or created path, check results, and any relevant screenshots. It may read the work but cannot change it. Fix every must-fix item and return for review. Stop when it approves or after three review rounds. If anything remains open, tell Ed exactly what.

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
- Portfolio 54.apexlinks.org (ed.apexlinks.org 301s there). Resume calm.apexlinks.org/144126 (gist `70cba709`, `resume.json`). Dump dump.apexlinks.org = `~/i/dump`.
- CF token `opencode-token-manager` has `API Tokens Edit`: add missing permissions yourself.
- STT: only Whistle, `stt <file>`. Links: `cobalt <url>` then `stt`. Save to `~/Downloads`.
- Music: only `yue2` skill. Lightning: org `gold144216-org` (user gold144216, scoped `sk-lit` key; credentials.json holds only `api_key`), teamspace `default-project`, key only in `~/.lightning/credentials.json`; old 144126-org creds in `~/.lightning/*.144126-org.bak`.
- OpenRouter real balance: `/api/v1/credits` (`total_credits - total_usage`), not `/key`. Models: `/api/v1/models?output_modalities=text`, `/api/v1/videos/models` (check durations/ratios/resolutions).
- `HF_TOKEN` in shell rc files for `MuScriptor/muscriptor-large`.
- `orc` = Opus 5.5 max orchestrating Haiku 5.5 workers (`~/.claude/orc.md`, agents `worker` + `Explore`). Claude's default for every task: `# Orchestrate` in `~/.claude/CLAUDE.md`. Traps: a subagent with no `effort` inherits max; `CLAUDE_CODE_EFFORT_LEVEL=max` forces max on every worker; built-in Explore ignores `CLAUDE_CODE_SUBAGENT_MODEL`. Why: `~/search/opus55-haiku55-orchestration-root.md`.

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
Google Cloud console (OAuth clients, redirect URIs) is always the 1440ir profile (`google-chrome-stable --profile-directory="Profile 16" <url>`, drive via the visible CDP port); everything else uses 1440fl.

# Memory
Start: `~/.optmem/memo wake`. Note: `memo note "<≤280 chars>"`. Recall: `memo recall <regex>`. Never edit `~/.optmem/memory`. Subagents: "You are a subagent. Don't run memo."
