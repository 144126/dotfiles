# me — personal, local-only (not synced to work VM)

This file is referenced by `~/AGENTS.md` via `@~/me.md` so local Pi sees it. It is **not** mirrored by `pisync`, so the remote work VM silently skips it.

## Personal taste — how Ed likes his own webapps

These are Ed's personal webapp defaults. Keep them local; don't enforce at work.

- All UI text (labels, buttons, microcopy) in lowercase.
- Follow the repo design system exactly (`DESIGN.md`, `src/app.css`). If `src/app.css` exists, use its variables, never raw css values.
- Prefer Tailwind utilities. No inline `style=` and no `<style>` blocks.
- Tailwind v4 + SvelteKit: `pnpm dlx sv add tailwindcss` wires it up. Theme via `@theme` in `app.css`, no `tailwind.config.js`. Dark mode `@custom-variant dark (&:is(.dark *));`. Add `@reference "tailwindcss";` inside any `<style>` block that needs theme tokens.
- Fonts go in `static/fonts`.
- Google auth callback URLs are always `/google`.

- Svelte: runes only (`$props`, `$state`, `$derived`, `$effect`, `$bindable`). Never `export let`.
- Stored enum and status values are single characters (`st`: `r`=pending, `s`=success, `f`=failed). Map to labels only when displaying.
- Snake_case for vars and functions. Db payload, type defs, request JSON, and page-load return keys are single letters, each commented at its definition.

## Clone convention (personal)

Clone GitHub repos to `~/i/<org-or-user>/<repo-name>`.

## Personal project scaffolding

Personal naming and scaffolding prefs, not work policy.

- New webapp project name: 2-4 characters, digital root 9 (sum letter positions a=1..z=26 plus digits, reduce to one digit). Never reuse.
- Location `~/i/` by default, `~/i/me/` for personal. Create via `pnpm dlx sv create <name>` with SvelteKit minimal, TypeScript yes, add-ons prettier+eslint+vitest+playwright+sveltekit-adapter+experimental, etc. (full prompts in old AGENTS.md if needed).
- Portfolio: ed.apexlinks.org — Resume: https://calm.apexlinks.org/144126

## Personal machine setup

- Dotfiles mirrors and personal clone prefs are personal; work VM uses its own layout.

### Dotfiles (local only)

- Repo: `144126/dotfiles` — public at https://github.com/144126/dotfiles — cloned at `~/i/144126/dotfiles`. Mirrors `~/.tmux.conf` → `tmux/tmux.conf`, `~/.config/foot/foot.ini` → `foot/foot.ini`.
- Any agent that edits a system config (`~/.tmux.conf`, `~/.config/foot/foot.ini`, `~/.bashrc`, etc.) must copy it to the repo, `git add .`, commit, `git push` in same turn.

### Browser (local)

- Never let agent-browser write its profile into `/tmp` (tmpfs). Use `TMPDIR=$HOME/.cache/abtmp`, then `agent-browser close --all` plus `rm -rf /tmp/agent-browser-profile-*` when finished.
- Opening anything in chrome for Ed: always his default profile. Bare `google-chrome-stable <url/file>`, never another `--profile-directory` or `--user-data-dir`.
- Logged-in sites: agent-browser uses `~/.config/chrome-agent` via `AGENT_BROWSER_PROFILE` in `~/.bashrc`. Ed logs in there once per site. Never pass `--profile` and never use `chrome-profile-clone` (logins did not carry over).
- One agent at a time in that profile. If it is busy, ask Ed.
- New site login wall: close agent-browser, run plain `google-chrome-stable --user-data-dir=$HOME/.config/chrome-agent <login url>` (Google blocks sign-in in automated browsers), ask Ed to log in and close it.

## Compliant providers (HIPAA/SOC 2, GLM-5.3-Flash)

- Atlas Cloud
- Baseten
- FriendliAI
- Together AI
