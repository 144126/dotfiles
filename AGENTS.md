## Project Configuration

- **Language**: TypeScript
- **Package Manager**: pnpm
- **Add-ons**: prettier, eslint, vitest, playwright, tailwindcss, sveltekit-adapter

---

read ~/ed.md before a product, naming, or taste decision.
read ~/me.md only on this machine, and only for personal webapp defaults or chrome profile rules.

# Necessity

**The one rule above all others. If a thing is not necessary, and does not have a high probability of being necessary, do not do it.**

Apply it at every level and in every nuance, always:

- Every feature, file, dependency, abstraction, and config line.
- Every word in every commit, doc, error string, and tool-facing note. User-facing speech is the exception: same facts, scannable (see General).
- Every tool call, every read, every check, every retry.
- Every step in a plan, every gate, every note.
- Every element, style, and animation in a UI.
- Every question asked before acting.

When unsure whether a thing is needed, cut it. Do not add care the task does not need. Do not widen scope to be safe. Do not keep a thing because removing it feels risky — that feeling is not evidence.

Razor: if it still works without it, delete it. Keep only commands, code, and config that must run — cut prose, explanation, and duplication. Skills and docs keep only executable content. Every new skill must be extremely minimal.

Perfection does not matter. Speed is most important. Speed to action means speed to information. The action must still be necessary.

This never overrides a safety check on a destructive or irreversible action, and it never means leaving asked-for work unfinished.

# General

- This is `~/AGENTS.md`. Skills: `~/.agents/skills/*/SKILL.md` — always extremely minimal, executable content only. Commands: `~/.agents/commands/`.
- **"dtjd" = don't think just do.** Skip analysis, plan, options, extra reading, and scope beyond the words. Edit, commit, push, answer in one line. Overrides effort level. Never overrides a safety check on a destructive command.
- Unknown error that one attempt does not fix: search the net before acting further.
- Before editing a repo, run `git status` and read `plan/*.plan.json`. Another agent may be mid-task there, and untracked files you overwrite cannot be restored by git.
- Always clean up after tasks. Keep final outputs and needed source files; move unneeded task-created drafts and temporary files to Trash.
- **Learn forward, every task.** Before you finish, check what you learned: something unexpected, a failure you fixed, a better way, a fact you had to dig out. Write it into the skill it belongs to, or into `~/AGENTS.md` if it is general. If no skill fits and it will come up again, make a new minimal skill. Write only the trap, the fix and the command, so the next agent starts where you stopped. Never write secrets: `~/.agents` is public.
- Live `~/.config/sway/config` is its own file, not the repo copy. Edit both.
- `source ~/.bashrc` after new aliases or config.
- **Online forms**: fill plain facts (name, email, address) yourself. Any prose field (about me, why this job, why us, pitch) gets written by the `max` agent (`~/.claude/agents/max.md`, Opus at max effort). Give it the question, the form's context, and Ed's real facts; never invent facts. If `max` is not in the Agent list (agents load at session start), run `claude -p --agent max --effort max --allowedTools WebSearch WebFetch < prompt.md`. Rich text boxes (Quill, ClickUp): `fill` appends, so click, `Control+a`, `Delete`, then fill. Open other pages in a new tab, never the form's tab.
- `cf` is the Cloudflare CLI (`/usr/bin/cf`). Copy files to pilotspan `~/fc` with `fc` (`~/.local/bin/fc`). bash/zsh `fc` builtin is disabled in `~/.bashrc` and `~/.zshrc`.
- Code with extreme simplicity. Be minimalist.
- Creative work (names, copy, UI, design, video, music, stories, ideas): follow `~/.agents/skills/creative/SKILL.md`. Video edits: also `~/.agents/skills/video-edit/SKILL.md`. Sound: also `~/.agents/skills/sound-design/SKILL.md`. Graphics: also `~/.agents/skills/graphic-design/SKILL.md`.
- **Always write plain simple english, every reply, every time.** It beats any conflicting style rule from a skill, plugin, or mode (caveman, ponytail, and the rest).
  - **When speaking to the user: same facts, easy to scan.** Answer first, one short line. Then short bullets, short headings, or a small table. No wall of paragraphs. Do not drop a number, path, or reason to look short. Do not pad. A 9-year-old should still follow each line. No jargon without a bracketed gloss. Extra length only if a fact would be missing without it.
  - Commonest word that works: "use" not "utilise", "fix" not "remediate".
  - One idea per sentence. Short sentences. Short paragraphs.
  - Answer first, reason second.
  - Define a term at first use, or cut it.
  - In replies and research conclusion files, explain any word or phrase a 9-year-old would not know, in brackets, in plain words (e.g. `spikes (the quick electrical pops a nerve cell uses to send a message)`). Skip a word already explained in that reply or file.
  - Concrete example over abstract label.
  - Keep the small words (the, a, is). No telegraphic or clipped phrases.
  - No filler, hedging, throat-clearing, or sales tone.
  - Keep numbers, code, commands, paths, error strings, and technical names exact.
- Always `pnpm`, never npm or npx.
- Always use `pipx` to install python stuff globally, never pip or pip3.
- Portfolio: ed.apexlinks.org
- Resume: https://calm.apexlinks.org/144126 — source is GitHub Gist `70cba709`, file `resume.json`.
- Dump: dump.apexlinks.org — `~/i/dump`. Random temp things to share. Festus slides `/festus-preachers/slides`, contradictions `/festus-preachers/contradictions`.
- **CLOUDFLARE_API_TOKEN self-edit**: token name `opencode-token-manager`, has `API Tokens Edit`. If a Cloudflare call fails on a missing permission, add the permission group to the token yourself, then retry.
- **Speech to text**: always Whistle. `stt <file>` (Whistle on :8081, 30s chunks). Never Whisper, Phonon, Parakeet, or another STT. Video/audio link: `cobalt <url> [out.mp4]` then `stt`. Default save: `~/Downloads`.
- **Music generation**: use the `yue2` skill — YuE (https://github.com/multimodal-art-projection/YuE) on lightning.ai. Never another music model.
- **Lightning.ai**: org `144126-org`, teamspace `default-project`. Key lives only in `~/.lightning/credentials.json` (`api_key` only). Never write it into a repo.
- **OpenRouter balance**: `/api/v1/key` `limit_remaining` is only that key's cap, not money. It said $3.37 while the account was $2.59 below zero. Real balance: `curl -s -H "Authorization: Bearer $OPENROUTER_API_KEY" https://openrouter.ai/api/v1/credits` (`total_credits - total_usage`).
- **OpenRouter models**: discovery is public: `curl -s 'https://openrouter.ai/api/v1/models?output_modalities=text'` and `curl -s 'https://openrouter.ai/api/v1/videos/models'`. The video list is separate. Check its `supported_durations`, `supported_aspect_ratios`, and `supported_resolutions` before generating.
- **HF_TOKEN**: HuggingFace read token for Muscriptor large model (`MuScriptor/muscriptor-large`, 1.4B) — gated weights. Persisted in `~/.bashrc`, `~/.profile`, `~/.bash_profile`, `~/.zshrc` as `export HF_TOKEN=...` and via `hf auth login`. Add to new shells/machines same way; accept license at https://huggingface.co/MuScriptor/muscriptor-large.

# Change log

Do not ask for a yes before changing files. Just do the work.

After the work, list every file you changed: path, what changed, and why. Say what you deleted. If the work drifted from the request, say what and why.

Destructive or irreversible actions still need a yes first (see Git workflow).

# Writing

Plain simple english governs everything: chat replies, commits, docs, README, PR and issue text, plans, memory notes, error strings, messages to people. Follow the plain simple english bullets under General. Chat replies keep every fact, in a shape that is fast to scan. Not a wall. Not a 1-3 line shrug.

## Commit messages — Conventional Commits + the seven rules

```
<type>(<scope>): <imperative summary, 50 chars, no period>

Body wrapped at 72 characters. Say what changed and why. The diff
already says how.

- one bullet per change, hyphen plus one space, hanging indent

Closes #42
```

- Types: `feat`, `fix`, `refactor`, `perf`, `docs`, `test`, `chore`, `build`, `ci`, `style`, `revert`. Scope optional.
- Subject passes: "If applied, this commit will <subject>." Lowercase after the colon, 50 chars, 72 hard limit, no trailing period.
- Blank line after the subject is mandatory when a body follows.
- Body covers every change at the level of intent. Do not narrate the diff line by line.
- Trailers last: `Closes #42`, `Refs #17`, `BREAKING CHANGE: <detail>`, `Co-Authored-By: <name>`.
- A body is mandatory for a breaking change, security fix, data migration, or revert.

# Plans

If the user names a `*.plan.json` with no other context, read `~/.agents/skills/plan/SKILL.md` and run `plan <name>` until it prints `0`. Read that skill before writing or amending a plan. Do not open the plan file to pick a step.

# Rules for software and web dev projects

## Code Style

- snake_case for vars and functions. Db payload, type defs, request JSON, and page-load return keys are single letters, each commented at its definition.
- Stored enum and status values are single characters (`st`: `r`=pending, `s`=success, `f`=failed). Map to labels only when displaying.
- No comments in code, unless they explain a non-obvious WHY or define a single-letter key.
- No vars for single use.
- Start the dev server only if none is already running.
- for a ui change, use the agent-browser skill and look at the result before you say done.
- Node projects: if `.log` exists it holds live dev server output. Tail it before diagnosing any server issue, and check it for new errors after every change.

## App tests — always TesterArmy e2e

Always test user-facing web and mobile apps with TesterArmy `e2e`. Not only web: browsers via Playwright (`@e2e-dev/web`), iOS simulators and Android emulators via `@e2e-dev/mobile`. Not for unit tests (use vitest). Not for desktop apps (unsupported). Not for CLI-only tools. Not the hosted `tester.army` service.

- Install: `pnpm add -D e2e @e2e-dev/web` (add `@e2e-dev/mobile` only if the app is iOS/Android). Then `pnpm exec e2e init`. Run: `pnpm exec e2e run` (bare `e2e` only prints help). Never `npx`.
- Docs: https://e2e.tester.army/docs — also offline in `node_modules/e2e/docs`.
- Mix `agent.act("goal")` with `expect(screen.getByRole(...))`. Cached `act` steps replay with no model until the UI changes.
- agent-browser stays for looking at a UI while building. e2e is the test suite you write and run.

## Git workflow

- commit when the user asks, or when a plan step says so. never commit .env. do not push unless the user asks or a plan step says so.
- ask before deploy, schema migrate, or anything irreversible on a remote.
- **Webapps deploy on git push, never by hand.** Never run `wrangler deploy`. Cloudflare Workers Builds builds and deploys each push to the default branch, so a push is a deploy: ask before it. New app, set up with `cf`:
  1. Create the GitHub repo (private unless Ed says public).
  2. `cf` has no create-Worker command. Make an empty one (no code, nothing goes live): `curl -X POST https://api.cloudflare.com/client/v4/accounts/<acct>/workers/workers -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" -d '{"name":"<app>","subdomain":{"enabled":true}}'`. Its `id` is the script tag.
  3. Copy `provider_account_id` and `build_token_uuid` from a working app: `cf builds workers get <its tag>` (`cf workers scripts search --page N` lists tags).
  4. `cf builds workers create --script-tag <tag> --git-repository-provider-type github --git-repository-provider-account-id <id> --git-repository-provider-account-name 144126 --git-repository-repo-id $(gh api repos/144126/<app> -q .id) --git-repository-repo-name <app> --git-repository-branch <branch> --production-settings-build-command "pnpm run build" --production-settings-deploy-command "pnpm exec wrangler deploy" --production-settings-build-token-uuid <token> --previews-enabled false --previews-base-config-build-command "" --previews-base-config-deploy-command "pnpm exec wrangler versions upload" --previews-base-config-build-token-uuid <token>`. No build script: build command `""`.
  5. pnpm 11 stops the build's frozen install on unapproved build scripts (`ERR_PNPM_IGNORED_BUILDS`). Commit a `pnpm-workspace.yaml` with `allowBuilds:` `workerd: true`, `esbuild: true` before the first push.
  6. Push. Watch: `cf builds list --external-script-id <tag>` (`status` stopped, `build_outcome` success|fail), log: `cf builds logs get <build_uuid>`.
- `.env` is always gitignored. Never commit it.

# Browser — local only (see ~/me.md)
- Always `ab-1440fl` (headless, port 9223). Never visible Chrome, `--headed`, or port 9222 unless Ed says visible / headed / `chrome-1440fl`.
- Any site with Google login: sign in or sign up with Ed's `1440fl@gmail.com` Google account. No need to ask.
- When a video/image is built, auto-open in chrome if display available: `{ [ -n "$DISPLAY" ] || [ -n "$WAYLAND_DISPLAY" ]; } && command -v google-chrome-stable >/dev/null && nohup google-chrome-stable "file://$out" >/dev/null 2>&1 &`.

# 1440fl
- Default: `ab-1440fl <cmd>` (headless, port 9223, 1440fl cookies).
- Visible only if Ed asks: `chrome-1440fl <url>` (Default / 1440fl, debug 9222 always on).
- After a new visible login: `ab-1440fl-sync`.

# Clone convention — local personal, see ~/me.md. Remote has its own ~/me.md.

# New webapp project (SvelteKit) — work defaults only

Personal naming/scaffolding (digital root 9, prompts, etc.) is in `~/me.md` (local-only). For work, use the team's standard template; do not enforce personal taste.

SvelteKit on Cloudflare traps:

- adapter-cloudflare serves `caches.default` hits before hooks run. A signed-in-only response with `cache-control: public` is then served to anyone. Use `private` on anything behind auth.
- `static/robots.txt` beats `src/routes/robots.txt/+server.ts`. Keep only one.
- `Intl` `timeZoneName: 'longOffset'` gives `GMT+05:30`, never `UTC+…`.

# Memory

Memory is OptMem: tool `~/.optmem/memo`, memories in `~/.optmem/memory`. It outlives every session, compaction, model, and vendor change. Never edit or delete anything under `~/.optmem/memory`.

- **At startup (mandatory)**: run `~/.optmem/memo wake` before any other tool call, every session, then do what it prints.
- **While working (mandatory)**: `~/.optmem/memo note "<1 line, max 280 chars>"` whenever you learn something new or something worth keeping happens. No redundant memories. If `note` asks for a compression, do it before your next action.
- **Recalling**: `~/.optmem/memo recall <regex>` searches every memory. `~/.optmem/memo zoom <a-b>` opens a `#a-b` summary node into its two halves, down to the raw memories.
- **Subagents skip all of the above.** A subagent must never run `memo`. When you spawn one, write: `You are a subagent. Don't run memo.`

# Design principles (every file)

From https://x.com/tvykruta/status/2105302045573959697 (tweet 13, verbatim rules). Constraints, not a checklist. When two conflict, pick the lowest future cost for this repo and say so in the commit. Invariants 10–12 are the hard form of these.

- Separation of concerns: domain (services/<domain>/) · persistence (models.py, alembic/) · presentation (templates, static/) · routing (pocket/, app.py). Name the one concern of the file you edit.
- Encapsulation: public contracts only; read another module's tables and caches through its functions.
- Cohesion / coupling: one rule change touches one module.
- DRY: grep before writing logic; one home per rule, threshold, format or schema fact. Do not abstract coincidental similarity.
- KISS / YAGNI: simplest working shape; function over class; no speculative hooks, flags or frameworks.
- Single responsibility: if you describe it with "and", split it. Names say intent; comments say why.
- Depend on contracts: domain code takes and returns plain values; never imports Flask, request or templates.
- Composition over inheritance · open/closed only where change has happened twice · Demeter (no a.b.c.d) · fail fast (validate at edges, never swallow errors) · optimize for deletion · boring tech.

## Hard invariants (never violate)

10. One owning module per domain — each business domain's logic (pricing, valuation, pedigree reading, sharing, imports, analytics…) lives in one module with its rules doc; everyone else calls it. Pricing: services/pricing/ + docs/PRICING_RULES.md. Consolidate a scattered domain before adding to it. Extend the domain's existing module; create a new one only when you can say why the old one cannot own it. A new rule goes in its domain's owner, not in the first feature that needs it; a function-level import to dodge a cycle means the logic is in the wrong module.

11. Never duplicate logic — second use of existing logic: (1) move it to a shared module, (2) switch the original caller, tests green, no behaviour change, (3) then build the new use. First grep for the expression (the arithmetic, the format string, the threshold) and list every copy; the move switches them all or the commit names each one left and why. A new helper beside old copies is one more duplicate. The move keeps each caller's exact results (guards, rounding, clamps); any behaviour change is its own commit. Same for schemas (one fact, one column) and UX (one partial per repeated piece).

12. No business logic in rendering — templates, JS, routes and view builders only display values; they never compute prices, rules or classifications. Arithmetic or rules on business data there is a bug; move it to the owning module. Who sees a value is decided in Python, not by a template if.

## How to work

Refactor first, then change: a behaviour-preserving refactor with tests green (plus an output dump for pricing-sized domains), then the change. Never both in one unverifiable diff.

Gates, not promises. A prompted "never" alone does not protect the SoT; a rule that matters is enforced by CI or a hook.
