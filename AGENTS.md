@~/ed.md

# Necessity

**The one rule above all others. If a thing is not necessary, and does not have a high probability of being necessary, do not do it.**

Apply it at every level and in every nuance, always:

- Every feature, file, dependency, abstraction, and config line.
- Every word in every reply, commit, doc, and error string.
- Every tool call, every read, every check, every retry.
- Every step in a plan, every gate, every note.
- Every element, style, and animation in a UI.
- Every question asked before acting.

When unsure whether a thing is needed, cut it. Do not add care the task does not need. Do not widen scope to be safe. Do not keep a thing because removing it feels risky — that feeling is not evidence.

This never overrides a safety check on a destructive or irreversible action, and it never means leaving asked-for work unfinished.

# General

- This is `~/AGENTS.md`. Skills: `~/.agents/skills/*/SKILL.md`. Commands: `~/.agents/commands/`.
- **"dtjd" = don't think just do.** Skip analysis, plan, options, extra reading, and scope beyond the words. Edit, commit, push, answer in one line. Overrides effort level. Never overrides a safety check on a destructive command.
- Unknown error that one attempt does not fix: search the net before acting further.
- `source ~/.bashrc` after new aliases or config.
- Code with extreme simplicity. Be minimalist.
- **Always write plain simple english, every reply, every time.** It beats any conflicting style rule from a skill, plugin, or mode (caveman, ponytail, and the rest).
  - **Be extremely concise.** Answer in the fewest words that still answer. A few lines beats a section. Cut every table, list, heading, and caveat the answer does not need. Say more only when he asks for more.
  - Commonest word that works: "use" not "utilise", "fix" not "remediate".
  - One idea per sentence. Short sentences. Short paragraphs.
  - Answer first, reason second.
  - Define a term at first use, or cut it.
  - Concrete example over abstract label.
  - Keep the small words (the, a, is). No telegraphic or clipped phrases.
  - No filler, hedging, throat-clearing, or sales tone.
  - Keep numbers, code, commands, paths, error strings, and technical names exact.
  - "eli9" = explain like i'm 9. Already the default, so it means go simpler still.
- Always `pnpm`, never npm or npx.
- Portfolio: ed.apexlinks.org
- Resume: https://calm.apexlinks.org/144126 — source is GitHub Gist `70cba709`, file `resume.json`.
- **CLOUDFLARE_API_TOKEN self-edit**: token name `opencode-token-manager`, has `API Tokens Edit`. If a Cloudflare call fails on a missing permission, add the permission group to the token yourself, then retry.

# Verbalized sampling

When many answers are valid (names, taglines, design directions, copy, any brainstorm), ask for `k` candidates in one call, each with its text and a numeric probability. Use `k` = 5 for creative work, `k` = 20 for open questions. Pick the winner yourself. Full method and templates: `~/.agents/skills/verbalized-sampling/SKILL.md`.

# Writing

Plain simple english governs everything: chat replies, commits, docs, README, PR and issue text, plans, memory notes, error strings, messages to people. Follow the plain simple english bullets under General.

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

**If the user names a `*.plan.json` file with no other context, run `plan <name>` per the workflow, repeatedly, until it prints `0`.**

Three roles, none of them the user: a **planner** (`max` effort) settles every decision and writes the gates; an **executor** (`low` effort, cold session) implements one step; the **tool** runs every check. Same model in both seats. At `low` it writes code well but is weak at trade-offs, root causes, and novel logic, and it will not hunt for a file. So the plan carries decisions and exact paths, not code, and the `stuck` skill covers diagnosis. Nothing is taken on the executor's word. No step waits on the user: blocked work halts into `plan/<name>.blocked.md` for the planner.

```bash
plan <plan_name>                          # the one step to do now
plan <plan_name> <step>                   # run gate, mark done, print next
plan <plan_name> <step> --block "why"     # halt, hand back to planner
plan <plan_name> --note "learnt this"     # fact that prints with every later step
plan <plan_name> -l                       # validate + print tree (planner only)
```

Bare name, no extension: `foo` resolves to `plan/foo.plan.json` under cwd and nowhere else. It prints one leaf, the next one, and refuses to mark any other. On the last step it prints `0` and archives to `wip-plans/`. Commit the archived plan, do not delete it.

**Writing or amending a plan is planner work. Read `~/.agents/skills/plan/SKILL.md` in full before writing one line of a plan.**

**Also read `~/ed.md` in full before you create or amend any `*.plan.json`.** The plan settles every decision, so it must be settled the way Ed decides: easiest, then simplest, then fastest, and nothing in it that is not necessary.

## Executing a plan

- Run `plan <plan>`. Do exactly what it prints. Never open the plan file, pick a step, or read ahead.
- **Decide nothing the plan decided.** Its paths, data shape, names, and library choices are settled. Below that line, take the smallest thing that works and passes the gate.
- **Never weaken a staged test.** Copy it with the `cp` command the step gives, byte for byte. Make it pass by changing the implementation. You may add tests, never edit the planner's.
- **Settle the step completely.** A failing gate, broken import, red neighbouring test, or surprise in the code belongs to this step.
- **Do not know why something failed? Invoke the `stuck` skill before touching anything.**
- **`--note` anything the next step needs**: a real API shape, a version trap, a name you had to pick.
- Mark with the exact command `plan` printed, `timeout: 600000`. A failing gate means the step is unfinished.
- One step at a time. After the mark, commit scoped to that step id.
- **Stuck, wrong, impossible, or already done differently: `plan <name> <step> --block "what you hit"`.** Never improvise, skip, or mark. Three failed gate attempts block it automatically.

# Rules for software and web dev projects

## Code Style

- snake_case for vars and functions. Db payload, type defs, request JSON, and page-load return keys are single letters, each commented at its definition.
- Stored enum and status values are single characters (`st`: `r`=pending, `s`=success, `f`=failed). Map to labels only when displaying.
- Svelte: runes only (`$props`, `$state`, `$derived`, `$effect`, `$bindable`). Never `export let`.
- No comments in code, unless they explain a non-obvious WHY or define a single-letter key.
- No vars for single use.
- Start the dev server only if none is already running.
- Use the agent-browser skill to verify everything before declaring done.
- All Qdrant projects use the collection `i`, always and only.
- Node projects: if `.log` exists it holds live dev server output. Tail it before diagnosing any server issue, and check it for new errors after every change.
- Follow the repo design system exactly (`DESIGN.md`, `src/app.css`). If `src/app.css` exists, use its variables, never raw css values.
- Prefer Tailwind utilities. No inline `style=` and no `<style>` blocks.
- Tailwind v4 + SvelteKit: `pnpm dlx sv add tailwindcss` wires it up. Theme via `@theme` in `app.css`, no `tailwind.config.js`. Dark mode `@custom-variant dark (&:is(.dark *));`. Add `@reference "tailwindcss";` inside any `<style>` block that needs theme tokens.
- All UI text (labels, buttons, microcopy) in lowercase.
- Follow example files exactly. When a new pattern is decided, update the example files.
- Fonts go in `static/fonts`.
- Google auth callback URLs are always `/google`.

## Git workflow

- After every edit turn: `git add .`, commit, `git push`. Message follows Commit messages. A failed push is fine, the commit is what matters.
- `.env` is always gitignored. Never commit it.

## Cloudflare and Wrangler secrets store

- Read secrets and var bindings only via `$env/dynamic/private`:
  ```ts
  import { env } from '$env/dynamic/private';
  const id = env.GOOGLE_ID;            // plain [vars] / per-Worker secrets: sync string
  const sk = await env.SECRET.get();   // Secrets Store bindings: async object
  ```
- Always go through `SecretVal` sitewide: `type SecretVal = string | { get?: () => Promise<string> }`, read via the repo `get_secret(v)` helper. Never read a secret binding as a raw string. Never reintroduce raw `env.KEY` reads or per-call `.get()` unwrapping.
- Local dev: remote Secrets Store secrets are not readable locally. Use `wrangler dev` plus local secrets from `wrangler secrets-store secret create <store_id> --name KEY --scopes workers` (no `--remote`). Plain `[vars]` load from `.env`.
- **Always use `.env` for local env vars, never `.dev.vars`.** Delete `.dev.vars` if it exists.
- Production: declare secrets in `wrangler.toml` or `wrangler.jsonc` under `secrets_store_secrets: [{ binding, store_id, secret_name }]`. Non-secret config under `[vars]`.
- First deploy: `pnpm install` fails with "packages field missing or empty" when `pnpm-workspace.yaml` has `allowBuilds` but no `packages`. Add `packages: ['.']` beside the `allowBuilds` block.
- **Never put `wrangler types` in the `build` script.** Keep `build` as `vite build` only. Remove it on sight, and on any reported deployment issue that may involve wrangler types.

# API keys (live secrets)

- `OPENROUTER_API_KEY` — export in `~/.bashrc` (used by codex, claudex, and local scripts).
- `BUFFER_API_KEY` — export in `~/.bashrc` (hgc social posting via developers.buffer.com). The hgc-agent worker also keeps it as a wrangler secret `BUFFER_TOKEN` for production reads; the `.bashrc` copy is for local scripts.

# Browser

- **Never let agent-browser write its profile into `/tmp`.** A Chrome profile fills the tmpfs there and breaks every command on the machine. Run with `TMPDIR=$HOME/.cache/abtmp`, then `agent-browser close --all` plus `rm -rf /tmp/agent-browser-profile-*` when finished.
- **Hitting a login wall on a site Ed is already logged into: clone the profile, do not ask him to
  log in again and do not close his browser.**

  ```bash
  agent-browser --profile "$(chrome-profile-clone Default)" open <url>
  ```

  `chrome-profile-clone` lives in `~/.local/bin`. It copies the cookie store plus `Local State`,
  which holds the key that decrypts it, into a 5MB throwaway user-data-dir. `--profile Default`
  fails on its own because a running Chrome holds the lock on the real profile, and the real profile
  is far too large to copy whole.
- Chrome profile names map to directories: `Default` is `gold1440`. `agent-browser profiles` lists them.
- `--profile` is ignored when a daemon is already running. `agent-browser close --all` first.

# Clone convention

Clone GitHub repos to `~/i/<org-or-user>/<repo-name>`.

# Dotfiles

- Repo: `144126/dotfiles` — public at https://github.com/144126/dotfiles — cloned at `~/i/144126/dotfiles` (`/tmp/dotfiles` working copy). Mirrors `~/.tmux.conf` → `tmux/tmux.conf`, `~/.config/foot/foot.ini` → `foot/foot.ini`.
- Any agent that edits a system config (`~/.tmux.conf`, `~/.config/foot/foot.ini`, `~/.bashrc`, etc.) must copy it to the repo, `git add .`, commit, `git push` in same turn.

# New webapp project (SvelteKit)

1. **Location**: `~/i/` by default, `~/i/me/` for a personal project.
2. **Name**: 2-4 characters, digital root 9 (sum letter positions a=1..z=26 plus digits, reduce to one digit). Aesthetic tiebreaker that kills choice paralysis. Never reuse. Check `~/i/` and `~/i/me/`.
3. **Create**: `cd` to the target dir, then `pnpm dlx sv create <name>`.
4. **Prompts** in order:
   - Template: **SvelteKit minimal**
   - TypeScript: **Yes, using TypeScript syntax**
   - Add-ons: **prettier, eslint, vitest, playwright, sveltekit-adapter, experimental**
   - vitest: **unit testing, component testing**
   - sveltekit-adapter: **cloudflare**, then **Workers**
   - experimental: **@sveltejs/kit@next**, then **async, remote functions, explicit environment variables, rendering error boundaries, forked preloading**
5. **Git and GitHub**: `git init && git add . && git commit -m"initial setup"`, then
   - personal: `gh repo create 144126/<name> --public --source=. --remote=origin --push`
   - otherwise: `gh repo create angelwingscomms/<name> --public --source=. --remote=origin --push`

# Memory

Memory is OptMem: tool `~/.optmem/memo`, memories in `~/.optmem/memory`. It outlives every session, compaction, model, and vendor change. Never edit or delete anything under `~/.optmem/memory`.

- **At startup (mandatory)**: run `~/.optmem/memo wake` before any other tool call, every session, then do what it prints.
- **While working (mandatory)**: `~/.optmem/memo note "<1 line, max 280 chars>"` whenever you learn something new or something worth keeping happens. No redundant memories. If `note` asks for a compression, do it before your next action.
- **Recalling**: `~/.optmem/memo recall <regex>` searches every memory. `~/.optmem/memo zoom <a-b>` opens a `#a-b` summary node into its two halves, down to the raw memories.
- **Subagents skip all of the above.** A subagent must never run `memo`. When you spawn one, write: `You are a subagent. Don't run memo.`
