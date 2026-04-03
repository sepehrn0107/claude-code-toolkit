---
title: "Memory"
section: user-guide
skills-affected: [memory-sync, new-project, retrospective]
last-updated: 2026-04-03
---

# Memory

## What gets stored

### Per-project memory (`.claude/memory/` inside the project repo)

| File | Contents |
|---|---|
| `project_context.md` | What the project is, who it's for, the core problem it solves |
| `stack.md` | Tech stack and why it was chosen |
| `architecture.md` | High-level structure, key modules, code index metadata |
| `progress.md` | What's done, what's in progress, what's next |
| `lessons.md` | Patterns and anti-patterns discovered during development |

### Global memory (`vault/05-areas/claude-memory/`)

Cross-project learnings, model preferences, plans, specs, and the active project pointer.
Organized as topic files (one file per concern), indexed by `MEMORY.md`.

The `MEMORY.md` index is capped at 200 lines. Memory files are organized by topic —
stale entries are replaced, not accumulated.

## What never goes in memory

Even if you ask Claude to save these, it won't — and will explain why:

- Code patterns derivable from reading the codebase
- Git history (`git log` is authoritative)
- In-progress task state or current conversation context
- Anything already documented in `CLAUDE.md`
- Debugging solutions (the fix is in the code; the commit message has the context)

## How memory stays lean

Before writing anything to memory, the `/memory-sync` skill applies a
read-classify-write protocol:

| Classification | Action |
|---|---|
| Already captured (same fact, different words) | Skip |
| Update to existing entry | Edit that line in place |
| Correction of stale content | Replace the old entry |
| Genuinely new information | Append only the new entry |

A "move Phase 2 to Done" operation becomes two targeted line edits — not a full
file rewrite.

## Architectural Decision Records

Write an ADR whenever a significant architectural decision is made. `/implement`
Phase 5 and `/retrospective` both create ADRs automatically when flagged.

ADRs live at `vault/02-projects/<project>/memory/decisions/YYYY-MM-DD-<slug>.md`
and follow the template at `toolbox/templates/ADR.md`.
