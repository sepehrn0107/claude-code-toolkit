---
title: "Skills Reference"
section: skills
skills-affected: [implement, new-project, retrospective, standards-check, git-push, memory-sync, project, auto-switch, set-vault, read-section, grep, diff-summary, git-ctx, env-check, pkg-info, index-repo, web-fetch, update-docs, upgrade, upgrade-dev, add-stack-standards]
last-updated: 2026-04-03
---

# Skills Reference

Skills are Markdown files that Claude reads and follows at runtime. Each skill is a
sequence of steps — tool calls, sub-agent prompts, output formats, and fallback logic.

## All Skills

### Lifecycle

| Skill | Trigger | Purpose |
|---|---|---|
| `/implement` | `"add [X]"`, `"implement [X]"`, `"build [X]"` | Full 5-phase feature workflow |
| `/new-project` | `"new project"`, `"scaffold this"` | Scaffold a project from scratch |
| `/retrospective` | `"retrospective"`, after `/implement` | Capture learnings, propose toolbox improvements |
| `/standards-check` | `"review"`, `"before PR"`, `"check this"` | Verify code meets all standards |
| `/git-push` | `"push this"`, `"open a PR"`, `"commit and push"` | Commit, push, open PR |
| `/update-docs` | auto (end of `/implement` Phase 5), `"update docs"` | Update `/docs` after skill/standard changes |

### Memory

| Skill | Trigger | Purpose |
|---|---|---|
| `/memory-sync` | auto (before any memory write) | Write only the delta — prevent duplicates |
| `/project` | `"switch project"` | Load a different project's context |
| `/auto-switch` | auto (project name detected in message) | Switch project without user prompt |
| `/set-vault` | `"set vault"`, `"change vault path"` | Update vault path and re-render config |

### Code Tools (auto-triggered)

| Skill | Trigger | Purpose |
|---|---|---|
| `/read-section` | auto (one symbol from file > 100 lines) | Extract one function/class/section |
| `/grep` | auto (before any code search) | Two-phase search: paths first, then content |
| `/diff-summary` | auto (before reading git diff) | Structured diff summary for commits/PRs |
| `/git-ctx` | auto (multiple git commands) | Batch git state into one context pass |
| `/env-check` | auto (runtime/env questions) | Check versions, ports, Docker, .env |
| `/pkg-info` | auto (npm/PyPI package questions) | Version, types, license, popularity |
| `/index-repo` | `"/index-repo"` | Build structural code index for the project |
| `/web-fetch` | auto (before any WebFetch call) | Route fetch through Crawl4AI with caching |

### Upgrade

| Skill | Trigger | Purpose |
|---|---|---|
| `/upgrade` | `"upgrade toolbox"` | Apply pending migrations to existing install |
| `/upgrade-dev` | `"/upgrade-dev"` | Sync live install from template (dev use) |
| `/add-stack-standards` | `"add standards for [stack]"` | Add standards for a new tech stack |

## Skill file format

```yaml
---
name: skill-name
description: When this applies and what it does — used for automatic routing
---

# /skill-name

Step-by-step instructions...
```

The `description` field is what the routing system matches. The body contains the
steps Claude follows — tool calls, sub-agent prompts, output formats, fallback logic.

All first-party skills live in `toolbox/skills/`. See
[Contributing / Adding a Skill](../contributing/adding-a-skill.md) to add your own.
