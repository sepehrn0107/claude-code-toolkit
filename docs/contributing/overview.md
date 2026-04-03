---
title: "Contributing Overview"
section: contributing
skills-affected: [implement, git-push, standards-check, upgrade, upgrade-dev]
last-updated: 2026-04-03
---

# Contributing Overview

## Workflow

All changes go through PRs. Never commit directly to `master`.

```bash
git checkout -b feat/your-feature
# make changes
git commit -m "feat: description"
gh pr create
```

The `/retrospective` skill handles this automatically for improvements discovered
during project work — it creates a branch, commits the proposed change, and opens
a PR from within Claude Code.

## Branch naming

| Type | Pattern | Example |
|---|---|---|
| Feature | `feat/<slug>` | `feat/add-python-standards` |
| Fix | `fix/<slug>` | `fix/session-hook-windows` |
| Docs | `docs/<slug>` | `docs/add-tools-reference` |
| Retrospective | `retro/<slug>-YYYY-MM-DD` | `retro/auth-pattern-2026-04-01` |

## Commit messages

Conventional Commits format: `type(scope): imperative summary ≤72 chars`

Types: `feat`, `fix`, `chore`, `docs`, `refactor`

## What changes need a migration

Any change to installed behavior — routing table, session start, skill routing,
hook files, settings structure — requires:

1. Edit `templates/sections/` (the source of truth — never edit `~/.claude/` directly)
2. Run `/upgrade-dev` to sync the live install
3. Add a migration block in `skills/upgrade.md` and bump `"version"` in `package.json`

See [Upgrade Migrations](upgrade-migrations.md) for the migration pattern.

## Context architecture (for contributors)

The toolkit's core principle: the main session is an orchestrator, never a worker.

Four context layers load in order:
1. `~/.claude/CLAUDE.md` — global config (single `@import`, never overwritten by upgrades)
2. `~/.claude/CLAUDE.global.md` — routing, skills, session rules (rendered from template)
3. `toolbox/standards/` — universal + stack-specific standards (loaded per session)
4. `vault/02-projects/<name>/` — global memory, plans, specs

Sub-agents inherit all routing rules and memory protocols automatically via the global
`CLAUDE.md` — the orchestrator passes only ticket state paths and task description.

## Token efficiency principles

- Main session holds file paths and one-line summaries — never file content
- Standards: main session loads the digest; sub-agents load full files they need
- `/read-section` for single functions from large files
- Grep: paths first, content second
- Index queries answered by Haiku sub-agents reading specific JSON files only
- Memory read once at session start, never re-read in the same session
