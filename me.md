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
- agent-browser drives Ed's real running Chrome (default profile, all logins). `~/.agent-browser/config.json` sets `autoConnect`, `pinTab`, `idleTimeout: "0"`; the toggle at `chrome://inspect/#remote-debugging` is on. Use plain `agent-browser <cmd>`, no flags.
- Each new daemon connection makes Chrome show one "Allow" pop-up for Ed. Keep the default session; do not `close` it or start new `--session` names without need.
- Never pass `--profile`, `AGENT_BROWSER_PROFILE`, or `chrome-profile-clone` (copies launch with `--password-store=basic`, so cookies cannot decrypt).
- Never `tab new`: it opens in Chrome's last-used profile (e.g. Gold), not Default (1440fl). Use `open <url>` in the session's pinned tab. On `tab_gone`: `tab` to Ed's Gmail or X tab, `eval` an `<a id=abx target=_blank href=URL>`, `click '#abx'`, remove it, then `tab` to the new tab. Never navigate or close Ed's tabs.
- "No running Chrome instance found": ask Ed to open Chrome. Isolated headless run: `--auto-connect false`.

## Compliant providers (HIPAA/SOC 2, GLM-5.3-Flash)

- Atlas Cloud
- Baseten
- FriendliAI
- Together AI
