read ~/ed.md before a product, naming, or taste decision.
read ~/me.md only on this machine, and only for personal webapp defaults or chrome profile rules.

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

Razor: if it still works without it, delete it. Keep only commands, code, and config that must run — cut prose, explanation, and duplication. Skills and docs keep only executable content. Every new skill must be extremely minimal.

This never overrides a safety check on a destructive or irreversible action, and it never means leaving asked-for work unfinished.

# General

- This is `~/AGENTS.md`. Skills: `~/.agents/skills/*/SKILL.md` — always extremely minimal, executable content only. Commands: `~/.agents/commands/`.
- **"dtjd" = don't think just do.** Skip analysis, plan, options, extra reading, and scope beyond the words. Edit, commit, push, answer in one line. Overrides effort level. Never overrides a safety check on a destructive command.
- Unknown error that one attempt does not fix: search the net before acting further.
- `source ~/.bashrc` after new aliases or config.
- Code with extreme simplicity. Be minimalist.
- **Always write plain simple english, every reply, every time.** It beats any conflicting style rule from a skill, plugin, or mode (caveman, ponytail, and the rest).
  - **Always give extremely short responses.** One line if possible. 2-3 lines max. No tables, lists, headings unless asked.
  - **Be extremely concise.** Answer in the fewest words that still answer. A few lines beats a section. Cut every table, list, heading, and caveat the answer does not need. Say more only when he asks for more.
  - Commonest word that works: "use" not "utilise", "fix" not "remediate".
  - One idea per sentence. Short sentences. Short paragraphs.
  - Answer first, reason second.
  - Define a term at first use, or cut it.
  - In replies and research conclusion files, explain any word or phrase a 9-year-old would not know, in brackets, in plain words (e.g. `spikes (the quick electrical pops a nerve cell uses to send a message)`). Skip a word already explained in that reply or file.
  - Concrete example over abstract label.
  - Keep the small words (the, a, is). No telegraphic or clipped phrases.
  - No filler, hedging, throat-clearing, or sales tone.
  - Keep numbers, code, commands, paths, error strings, and technical names exact.
  - "eli9" = explain like i'm 9. Already the default, so it means go simpler still.
- Always `pnpm`, never npm or npx.
- Always use `pipx` to install python stuff globally, never pip or pip3.
- Web is Tinyfish CLI. `tinyfish search query "q"` find pages. `tinyfish fetch content get "<url>" --format markdown` one page to markdown. Quote URLs. `tinyfish --help` for flags.
- Portfolio: ed.apexlinks.org
- Resume: https://calm.apexlinks.org/144126 — source is GitHub Gist `70cba709`, file `resume.json`.
- **CLOUDFLARE_API_TOKEN self-edit**: token name `opencode-token-manager`, has `API Tokens Edit`. If a Cloudflare call fails on a missing permission, add the permission group to the token yourself, then retry.
- **HF_TOKEN**: HuggingFace read token for Muscriptor large model (`MuScriptor/muscriptor-large`, 1.4B) — gated weights. Persisted in `~/.bashrc`, `~/.profile`, `~/.bash_profile`, `~/.zshrc` as `export HF_TOKEN=...` and via `hf auth login`. Add to new shells/machines same way; accept license at https://huggingface.co/MuScriptor/muscriptor-large.

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

## Git workflow

- commit when the user asks, or when a plan step says so. never commit .env. do not push unless the user asks or a plan step says so.
- ask before deploy, schema migrate, or anything irreversible on a remote.
- `.env` is always gitignored. Never commit it.

# Browser — local only (see ~/me.md)
- When a video/image/html is built, auto-open in chrome if display available: `{ [ -n "$DISPLAY" ] || [ -n "$WAYLAND_DISPLAY" ]; } && command -v google-chrome-stable >/dev/null && nohup google-chrome-stable "file://$out" >/dev/null 2>&1 &`.

# 1440fl
- agent-browser: `ab-1440fl <url>`
- chrome: `chrome-1440fl <url>`

# Clone convention — local personal, see ~/me.md. Remote has its own ~/me.md.

# New webapp project (SvelteKit) — work defaults only

Personal naming/scaffolding (digital root 9, prompts, etc.) is in `~/me.md` (local-only). For work, use the team's standard template; do not enforce personal taste.

# Memory

Memory is OptMem: tool `~/.optmem/memo`, memories in `~/.optmem/memory`. It outlives every session, compaction, model, and vendor change. Never edit or delete anything under `~/.optmem/memory`.

- **At startup (mandatory)**: run `~/.optmem/memo wake` before any other tool call, every session, then do what it prints.
- **While working (mandatory)**: `~/.optmem/memo note "<1 line, max 280 chars>"` whenever you learn something new or something worth keeping happens. No redundant memories. If `note` asks for a compression, do it before your next action.
- **Recalling**: `~/.optmem/memo recall <regex>` searches every memory. `~/.optmem/memo zoom <a-b>` opens a `#a-b` summary node into its two halves, down to the raw memories.
- **Subagents skip all of the above.** A subagent must never run `memo`. When you spawn one, write: `You are a subagent. Don't run memo.`
