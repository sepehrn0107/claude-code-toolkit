---
title: "Routing"
section: user-guide
skills-affected: [implement, git-push, new-project, standards-check, project, auto-switch, memory-sync, web-fetch, git-ctx, diff-summary, read-section, pkg-info, grep, env-check, codex-delegate, codex-review, upgrade, upgrade-dev, set-vault, update-docs]
last-updated: 2026-04-03
---

# Routing

The toolkit detects intent from plain English and routes to the right skill automatically.
You don't need slash commands for any of these.

## User-triggered routing

| You say | What runs |
|---|---|
| `"add [X]"`, `"implement [X]"`, `"build [X]"` | `/implement` — full 5-phase workflow |
| `"fix [X]"`, `"debug [X]"`, `"not working"` | `superpowers:systematic-debugging` |
| `"check this"`, `"review [X]"`, `"before PR"` | `/standards-check` |
| `"new project"`, `"starting fresh"`, `"scaffold this"` | `/new-project` |
| `"switch project"`, `"change project"` | `/project` |
| `"push to git"`, `"push this"`, `"open a PR"` | `/git-push` |
| `"upgrade toolbox"`, `"update toolbox"`, `"/upgrade"` | `/upgrade` |
| `"set vault"`, `"change vault path"` | `/set-vault` |
| `"delegate to codex"`, `"use codex for"` | `/codex-delegate` |
| `"review with codex"`, `"codex review"` | `/codex-review` |
| `"update docs"`, `"docs are stale"`, `"/update-docs"` | `/update-docs` |

## Automatic routing (no user prompt needed)

These fire based on Claude's own internal actions — no user message required:

| Claude is about to… | Skill that fires first |
|---|---|
| Call `WebFetch` or open a URL | `/web-fetch` — routes through Crawl4AI |
| Run multiple git commands | `/git-ctx` |
| Read a `git diff` to draft a commit or PR | `/diff-summary` |
| Read one section from a file > 100 lines | `/read-section` |
| Look up an npm or PyPI package | `/pkg-info` |
| Check runtime versions, ports, Docker, or `.env` | `/env-check` |
| Search code with Grep | `/grep` |
| Write to any memory file | `/memory-sync` |

## How routing works internally

The routing table lives in `~/.claude/CLAUDE.global.md`. Each row is a phrase pattern
and a skill file path. When a user message matches, the skill is read and followed before
any response. See [Contributing / Adding a Skill](../contributing/adding-a-skill.md) to
add a new routing row.
