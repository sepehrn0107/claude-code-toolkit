# Toolbox Design Spec
**Date:** 2026-03-27
**Status:** Approved

---

## Overview

A cross-repo, OS-agnostic development toolbox that guides software projects from idea to production. Built on top of Claude Code's native config hierarchy and the superpowers skill suite. Language and stack agnostic — discovers or asks for the stack, then applies the right standards. Evolves over time by capturing learnings from completed projects.

---

## Architecture: Layered Doc System + Lifecycle Skills

The toolbox is organized as 4 layers. Each layer has a single clear owner and purpose.

```
Layer 1 — Global preferences     ~/.claude/CLAUDE.md + toolbox/memory/
Layer 2 — Stack standards        toolbox/standards/
Layer 3 — Project context        <project>/.claude/memory/
Layer 4 — Session context        auto-written to progress.md each session
```

### Distribution model
- The `toolbox/` repo is the **source of truth** — hosted at `https://github.com/sepehrn0107/toolbox`
- Each user clones their own copy; skills are loaded from their local clone path
- Projects pull templates from it at bootstrap time
- Nothing is written back to the toolbox directly — all changes go through GitHub PRs
- No symlinks, no submodules, no scripts — all markdown + git + Claude Code

---

## Directory Structure

### Toolbox repo (`~/Documents/toolbox/`)

```
toolbox/
├── CLAUDE.md                          # Toolbox identity + usage instructions
├── memory/                            # Layer 1 — global persistent memory
│   ├── MEMORY.md
│   └── *.md
│
├── standards/
│   ├── universal/                     # Applies to every project, every stack
│   │   ├── architecture.md            # SOLID, separation of concerns, clean architecture
│   │   ├── security.md                # OWASP, secrets management, input validation
│   │   ├── git.md                     # Commit conventions, branching strategy
│   │   ├── testing.md                 # Test pyramid, coverage expectations
│   │   └── documentation.md          # What to document and how
│   │
│   └── stacks/                        # Stack-specific standards, grows organically
│       ├── typescript-react/
│       ├── python-fastapi/
│       ├── go/
│       └── ...
│
├── skills/                            # Lifecycle skills — source of truth
│   ├── new-project.md
│   ├── add-feature.md
│   ├── standards-check.md
│   └── retrospective.md
│
├── templates/
│   ├── CLAUDE.md.template             # Base project CLAUDE.md
│   ├── CLAUDE.global.md               # Template for ~/.claude/CLAUDE.md (setup once)
│   ├── memory/                        # Starter memory files for new projects
│   │   ├── MEMORY.md
│   │   ├── project_context.md
│   │   ├── stack.md
│   │   ├── architecture.md
│   │   ├── progress.md
│   │   └── lessons.md
│   └── pipeline/                      # CI/CD templates per platform
│       └── github-actions/
│
└── docs/
    └── superpowers/
        └── specs/
            └── 2026-03-27-toolbox-design.md
```

Skills are loaded by absolute path from the local toolbox clone — not copied anywhere. `~/.claude/CLAUDE.md` tells Claude where to find each skill. Updating a skill in the toolbox takes effect immediately.

### New project structure (bootstrapped by `/new-project`)

```
<project>/
├── CLAUDE.md                          # Layer 3 — tailored from toolbox template
└── .claude/
    └── memory/
        ├── MEMORY.md
        ├── project_context.md         # Name, goal, stakeholders, constraints
        ├── stack.md                   # Chosen stack + why, best practice sources
        ├── architecture.md            # High-level structure, key components
        ├── progress.md                # Current phase, done, next (updated each session)
        ├── lessons.md                 # What's working, what isn't
        └── decisions/
            └── YYYY-MM-DD-<slug>.md   # One ADR per significant architectural decision
```

---

## Lifecycle Skills

Four custom skills are added to the toolbox. Each orchestrates the relevant superpowers skills so the correct workflow is always invoked automatically.

### `/new-project`
Entry point for starting anything from scratch.

1. Read Layer 1 (global memory) + Layer 2 universal standards
2. Collect idea — freeform input, existing spec, or guided prompts
3. Detect or ask for stack → load `standards/stacks/<stack>/`
4. Invoke `superpowers:brainstorming` → `superpowers:writing-plans`
5. Scaffold project: `CLAUDE.md`, `.claude/memory/` from templates, pipeline config
6. Initialize git, write first commit

### `/add-feature`
Entry point for adding anything to an existing project.

1. Read Layer 3 project memory (stack, architecture, decisions, progress)
2. Invoke `superpowers:brainstorming` for scoping
3. Invoke `superpowers:test-driven-development` for implementation
4. Invoke `superpowers:verification-before-completion` before declaring done
5. Write ADR to `.claude/memory/decisions/` if an architectural choice was made
6. Update `progress.md`

### `/standards-check`
Run at any point — before PR, after implementation, or on demand.

1. Read active stack standards from Layer 2
2. Check code against: style, architecture, security, documentation
3. Invoke `superpowers:requesting-code-review`
4. Invoke `code-simplifier` for quality and clarity pass
5. Output checklist of passes/failures with file references

### `/retrospective`
Run at project completion, a significant milestone, or automatically prompted on task completion (see Retrospective Triggers below).

1. Read full project memory (Layer 3)
2. Extract: what worked, what didn't, new patterns, stack-specific learnings
3. Draft proposed changes: updated standards, new skills, or promoted universal patterns
4. User approves each proposed change
5. For each approved change: create a branch in the local toolbox clone, commit the content, and open a PR to `https://github.com/sepehrn0107/toolbox` with a detailed description of what was learned and why it's being proposed
6. Write summary to toolbox global memory (Layer 1)

### Superpowers integration map

```
/new-project     → brainstorming → writing-plans → executing-plans
/add-feature     → brainstorming → TDD → verification-before-completion
/standards-check → requesting-code-review → code-simplifier
/retrospective   → reads memory, proposes toolbox updates
```

All other superpowers skills (`systematic-debugging`, `receiving-code-review`, `finishing-a-development-branch`, etc.) remain available independently alongside the lifecycle skills.

### Retrospective Triggers

The toolbox prompts for a retrospective at natural completion points rather than requiring the user to remember to run it manually.

**On feature completion** (`/add-feature` finishes):
> "Feature complete. Want to run `/retrospective` to capture any learnings before closing out?"

**On `superpowers:finishing-a-development-branch`:**
The `/retrospective` reminder is appended to the finishing checklist — it becomes a natural final step alongside merge/PR.

**On session end (stop hook):**
If `lessons.md` has been updated during the session, Claude prompts:
> "You've added notes to lessons.md this session. Run `/retrospective` now or save it for project completion?"

The retrospective is never forced — always a prompt with the option to defer. This is configured as a stop hook in `~/.claude/settings.json`.

---

## Memory System

### Global memory (Layer 1)
Personal preferences, recurring patterns, and cross-project learnings. Lives in `toolbox/memory/`. Written by `/retrospective` with user approval. Loaded in every repo via `~/.claude/CLAUDE.md`.

### Project memory schema (Layer 3)
Bootstrapped from `toolbox/templates/memory/` at project creation. Fixed schema for consistency:

| File | Purpose |
|---|---|
| `project_context.md` | Name, goal, stakeholders, deadline, constraints |
| `stack.md` | Chosen stack, why, best practice sources used |
| `architecture.md` | High-level structure, key components, boundaries |
| `decisions/*.md` | One ADR per significant architectural choice |
| `progress.md` | Current phase, what's done, what's next |
| `lessons.md` | What's working, what isn't (feeds `/retrospective`) |

### Session context (Layer 4)
At the end of each session, Claude writes a short summary to `progress.md`. The next session opens by reading it — no re-explaining context required.

---

## Standards Discovery (Stack-Agnostic)

When no stack is set, the following process runs automatically:

```
1. Check project files for signals (package.json, go.mod, requirements.txt, Cargo.toml, etc.)
2. If signals found → propose detected stack, ask to confirm
3. If no signals → ask: "What stack are you using?"
4. Load toolbox/standards/stacks/<stack>/ if it exists
5. If stack is new → Claude researches current best practices,
   drafts new standards file, user approves,
   saved to toolbox/standards/stacks/<new-stack>/
```

Standards files per stack cover: style/formatting, naming conventions, architectural patterns, security considerations, testing approach, tooling recommendations.

---

## The Feedback Loop

```
Project runs
    ↓
lessons.md captures learnings during development
    ↓
/retrospective extracts patterns, proposes toolbox updates
    ↓
User approves → PR opened to github.com/sepehrn0107/toolbox
    ↓
PR merged → all users inherit the improvement on next pull
    ↓
Universal patterns promoted to standards/universal/ via the same PR flow
```

Nothing is written back to the toolbox without explicit user approval. All changes go through GitHub PRs — the PR is the approval mechanism.

---

## `~/.claude/CLAUDE.md` — Global Activation File

This file makes the toolbox available in every repo automatically. It is maintained in the toolbox repo at `toolbox/templates/CLAUDE.global.md` and copied once to `~/.claude/CLAUDE.md` during initial setup (the only manual step in setup).

```markdown
# Toolbox

Standards, memory, and lifecycle skills for all projects.
Source: https://github.com/sepehrn0107/toolbox (local clone: C:/Users/<you>/Documents/toolbox)

## Standards
- Universal: C:/Users/<you>/Documents/toolbox/standards/universal/
- Stack-specific: loaded per project via .claude/memory/stack.md

## Lifecycle Skills
Skills are loaded from the local toolbox clone. Read the skill file before following it.
- /new-project      → C:/Users/<you>/Documents/toolbox/skills/new-project.md
- /add-feature      → C:/Users/<you>/Documents/toolbox/skills/add-feature.md
- /standards-check  → C:/Users/<you>/Documents/toolbox/skills/standards-check.md
- /retrospective    → C:/Users/<you>/Documents/toolbox/skills/retrospective.md

## Memory
- Global memory: C:/Users/<you>/Documents/toolbox/memory/MEMORY.md
- Project memory: .claude/memory/MEMORY.md (when present)

## Always apply
- Read project memory before starting any task
- Follow active stack standards
- Write session summary to progress.md when stopping work
- When starting a new project with no context, run /new-project
```

Users replace `<you>` with their username once during setup.

---

## What This Is Not

- Not a CLI tool or script — pure markdown + Claude Code
- Not a rigid framework — standards are guides, not hard blockers
- Not automated — nothing writes back to the toolbox without your approval
- Not a monorepo — each project is independent; the toolbox is just the source of templates and standards
