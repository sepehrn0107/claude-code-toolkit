---
title: "Documentation"
section: getting-started
skills-affected: [implement, new-project, retrospective, standards-check, git-push, update-docs, memory-sync, project, auto-switch, set-vault, read-section, grep, diff-summary, git-ctx, env-check, pkg-info, index-repo, web-fetch, upgrade, upgrade-dev, add-stack-standards, load-standards]
last-updated: 2026-04-03
---

# claude-code-toolkit Documentation

## Getting Started

| Page | What it covers |
|---|---|
| [Install](getting-started/install.md) | Requirements, clone, vault setup, first run |
| [Your First Session](getting-started/first-session.md) | Status line, memory load, new vs. existing project |
| [Core Concepts](getting-started/concepts.md) | Sessions, memory, routing, standards gate, sub-agents |

## User Guide

| Page | What it covers |
|---|---|
| [Memory](user-guide/memory.md) | Per-project + global memory, what is/isn't stored, sync protocol |
| [Routing](user-guide/routing.md) | Full routing table — user-triggered and automatic |
| [Standards](user-guide/standards.md) | How standards load, available stacks, adding one |
| [Working Across Projects](user-guide/multi-project.md) | Workspace layout, switch project, vault path |
| [Optional Setup](user-guide/optional-setup.md) | Codex, Crawl4AI, local LLM |

## Skills Reference

| Page | What it covers |
|---|---|
| [All Skills](skills/README.md) | Quick-reference table of all skills with trigger phrases |
| [Lifecycle Skills](skills/lifecycle.md) | `/implement`, `/new-project`, `/retrospective`, `/standards-check`, `/git-push`, `/update-docs` |
| [Memory Skills](skills/memory-skills.md) | `/memory-sync`, `/project`, `/auto-switch`, `/set-vault` |
| [Code Tool Skills](skills/code-tools.md) | `/read-section`, `/grep`, `/diff-summary`, `/git-ctx`, `/env-check`, `/pkg-info`, `/index-repo`, `/web-fetch` |
| [Upgrade Skills](skills/upgrade.md) | `/upgrade`, `/upgrade-dev`, `/add-stack-standards` |

## Standards Reference

| Page | What it covers |
|---|---|
| [Standards Overview](standards/README.md) | What standards are, how the gate enforces them |
| [Universal Standards](standards/universal.md) | All 9 universal standards — purpose and key rules |
| [Stack Standards](standards/stacks.md) | Each stack, what it covers, inheritance model, how to add |

## Tools Reference

| Page | What it covers |
|---|---|
| [Python Tools](tools/README.md) | All tools — purpose, invocation, config |

## Contributing

| Page | What it covers |
|---|---|
| [Overview](contributing/overview.md) | Workflow, branch conventions, PR rules, context architecture |
| [Adding a Skill](contributing/adding-a-skill.md) | Write, route, migrate, doc, PR |
| [Adding Standards](contributing/adding-standards.md) | Universal rules, new stacks, file format |
| [Upgrade Migrations](contributing/upgrade-migrations.md) | Migration pattern, idempotency, version bump |
| [Writing Documentation](contributing/documentation.md) | Doc standard, frontmatter schema, freshness rules |
