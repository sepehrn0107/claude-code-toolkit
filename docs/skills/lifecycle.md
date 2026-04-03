---
title: "Lifecycle Skills"
section: skills
skills-affected: [implement, new-project, retrospective, standards-check, git-push, update-docs]
last-updated: 2026-04-03
---

# Lifecycle Skills

## `/implement` — full feature workflow

The primary entry point for any non-trivial feature. Orchestrates five phases via
sub-agents, writing state files to `.claude/tickets/<ticket-id>/` after each phase.

**Trigger:** `"add [X]"`, `"implement [X]"`, `"build [X]"`, `"work on [ticket]"`

### Phases

| Phase | What happens | Output file |
|---|---|---|
| 0 — Intake | Reads memory and standards digest, writes ticket context | `context.md` |
| 1 — Ideate | Brainstorms scope, risks, edge cases via sub-agent | `ideation.md` |
| 2 — Plan | Produces file-level implementation plan via sub-agent | `plan.md` |
| 3 — Implement | TDD implementation per component via sub-agents | `implementation.md` |
| 4 — Verify | Code review, test verification | `verification.md` |
| 5 — PR | Standards check, docs update, commit, open PR | `pr.md` |

### Resuming interrupted work

If a ticket already has state files in `.claude/tickets/<ticket-id>/`, `/implement`
resumes from the latest complete phase. Interrupt at any phase and continue later —
no work is lost.

### Component routing in Phase 3

Each component is classified before implementation:
- **Simple** (single file, ≤ ~100 LOC, no cross-file deps) → local LLM + Haiku review
- **Complex** (multiple files, cross-cutting logic) → full Sonnet sub-agent

### Codex delegation

If Codex CLI is installed, Phase 3 complex components are delegated to Codex
automatically. Falls back to direct Claude silently.

---

## `/new-project` — scaffold from scratch

Runs when starting a project with no existing context.

**Trigger:** `"new project"`, `"starting fresh"`, `"scaffold this"`

1. Checks prerequisites (Docker, Codex availability)
2. Invokes `superpowers:brainstorming` to explore the project
3. Detects or asks about the stack
4. Creates vault memory files (`project_context.md`, `stack.md`, etc.)
5. Initializes git, creates initial commit
6. Runs `/new-project` standards check

---

## `/retrospective` — capture and improve

Runs at project completion or after significant milestones. Reads all memory files
and ADRs, then proposes toolbox improvements.

**Trigger:** `"retrospective"`, suggested automatically after `/implement` completes

For each learning found, classifies it into:
- New universal standard → PR to `standards/universal/`
- Stack-specific convention → PR to `standards/stacks/<stack>/`
- Recurring workflow not yet a skill → new skill file PR
- Personal/workspace learning → writes to global memory directly (no PR)

Each approved change becomes its own branch and PR to the toolbox repo.

---

## `/standards-check` — pre-PR verification

Verifies the codebase meets all toolbox standards. Runs automatically before any PR.

**Trigger:** `"check this"`, `"review [X]"`, `"before PR"`, `"ready to merge"`

Checks: architecture, security, git hygiene, testing, documentation, and doc freshness.
Outputs a pass/fail checklist with file references for failures. All failures must be
addressed before merging.

---

## `/git-push` — commit and open PR

Groups changed files into logical commits, writes conventional commit messages, pushes
the branch, and opens a PR with a structured body.

**Trigger:** `"push this"`, `"open a PR"`, `"commit and push"`, `"ship this"`

Never pushes directly to `main`/`master` — always branches + PR.

---

## `/update-docs` — keep docs in sync

Updates `/docs` files after any skill, standard, or tool change.

**Trigger:** auto (end of `/implement` Phase 5), `"update docs"`, `"docs are stale"`

Reads `implementation.md` from the ticket state, maps changed items to their doc files
via `skills-affected` frontmatter, makes surgical edits, and writes a `docs.md` artifact
to the ticket state. Creates stubs for new items with no existing doc.
