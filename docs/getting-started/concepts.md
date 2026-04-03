---
title: "Core Concepts"
section: getting-started
skills-affected: [implement, memory-sync, load-standards, standards-check]
last-updated: 2026-04-03
---

# Core Concepts

A mental model of how the toolkit works, before you start using it.

## Sessions

Every Claude Code session starts cold — no memory of past work. The toolkit fixes
this by reading your project's context files at session start (via a shell hook)
and printing a one-line summary. From that point, Claude knows the project, stack,
and what was being worked on last time.

This happens automatically. You don't trigger it.

## Memory

The toolkit stores project context in Markdown files in your vault, not inside the
project repo. There are two layers:

- **Per-project** (`vault/02-projects/<project>/memory/`) — what the project is,
  what stack it uses, what's been built, what's next, and what was learned
- **Global** (`vault/05-areas/claude-memory/`) — cross-project learnings, model
  preferences, and the active project pointer

Memory is read once at session start, in parallel. Within a session, Claude works from
one-line summaries. Files are never re-read unless a specific section is explicitly needed.

See [Memory](../user-guide/memory.md) for the full protocol.

## Routing

You don't need to memorize slash commands. The toolkit detects intent from plain English
and routes to the right workflow automatically:

| You say | What runs |
|---|---|
| `"add [feature]"` | `/implement` — full 5-phase workflow |
| `"fix [bug]"` | `superpowers:systematic-debugging` |
| `"push this"` | `/git-push` |
| `"new project"` | `/new-project` |
| `"review this"` | `/standards-check` |

See [Routing](../user-guide/routing.md) for the full table.

## Standards Gate

Before Claude can write any code in a session, the standards for your stack must be
loaded. A shell hook (`pre-tool-standards-gate.sh`) enforces this — it blocks file edits
until a session flag is set by `/load-standards`.

This means it is structurally impossible to write code in a session without having
loaded the applicable standards first.

## Sub-agent Architecture

Long workflows (like `/implement`) run as orchestrated sub-agents. The main session
acts as a coordinator — it holds file paths and one-line summaries, not file content.
Each phase runs as a fresh sub-agent that reads only the files it needs, does its work,
and writes a bounded output file. The main session reads only the status line.

This keeps the main context window clean across long sessions and makes workflows
fully resumable — if Claude is interrupted after Phase 2, the next session reads the
existing `plan.md` and picks up at Phase 3.
