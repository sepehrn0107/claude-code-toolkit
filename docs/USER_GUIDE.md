# Toolbox User Guide

A complete reference for getting the most out of the toolbox in your daily development workflow.

---

## Table of Contents

1. [What the Toolbox Does](#1-what-the-toolbox-does)
2. [Installation](#2-installation)
3. [The Four-Layer System](#3-the-four-layer-system)
4. [Lifecycle Skills](#4-lifecycle-skills)
   - [/new-project](#new-project)
   - [/implement](#implement)
   - [/standards-check](#standards-check)
   - [/retrospective](#retrospective)
   - [/index-repo](#index-repo)
   - [/add-stack-standards](#add-stack-standards)
5. [Standards](#5-standards)
6. [Memory System](#6-memory-system)
7. [Model Selection](#7-model-selection)
8. [Hooks and Automation](#8-hooks-and-automation)
9. [Day-to-Day Workflow](#9-day-to-day-workflow)
10. [Contributing to the Toolbox](#10-contributing-to-the-toolbox)

---

## 1. What the Toolbox Does

The toolbox is a cross-repository development assistant that runs inside Claude Code. Every time you open a project:

- **Standards are loaded automatically** — universal rules (architecture, security, git, testing) plus stack-specific rules for your tech stack
- **Project memory is read** — Claude knows your project's goals, decisions, and current phase without you re-explaining anything
- **Workflow is guided** — you invoke a skill and Claude follows the right process for that phase of development

The result: consistent, high-quality development across every project you work on.

---

## 2. Installation

**Requirements:** Claude Code, Git.

### Step 1 — Clone the toolbox

```bash
git clone https://github.com/sepehrn0107/toolbox ~/Documents/toolbox
```

Clone it anywhere permanent. The path you choose becomes `TOOLBOX_PATH`.

### Step 2 — Run setup

Open the toolbox directory in Claude Code and say:

```
Set up the toolbox
```

Claude will:
1. Detect the cloned directory path
2. Write `~/.claude/CLAUDE.md` with your `TOOLBOX_PATH` substituted in
3. Install hooks to `~/.claude/hooks/`
4. Merge hook configuration into `~/.claude/settings.json`

That's the only manual step. All projects pick up the toolbox automatically from that point on.

### Verifying installation

Open any project directory in Claude Code. You should see a session-start summary printed automatically:

```
Stack: typescript-nextjs
Phase: In Progress — implement auth feature
Next: Write tests for /api/auth/login
Index: up to date
```

If this appears, the toolbox is active.

---

## 3. The Four-Layer System

The toolbox loads context in four layers, from broadest to narrowest:

```
Layer 1 — Global preferences     ~/.claude/CLAUDE.md
                                  toolbox/memory/MEMORY.md

Layer 2 — Stack standards        toolbox/standards/universal/
                                  toolbox/standards/stacks/<your-stack>/

Layer 3 — Project context        <project>/.claude/memory/
                                  (project_context, architecture, decisions, progress, lessons)

Layer 4 — Session context        <project>/.claude/memory/progress.md
                                  (written and read each session)
```

**Layer 1** contains your personal preferences and cross-project learnings captured by `/retrospective`.

**Layer 2** contains the coding standards Claude enforces for your stack. These are enforced via a pre-tool gate — Claude cannot write code until standards are loaded for the session.

**Layer 3** is the project's long-term memory. Once written, Claude never asks you to re-explain project goals, architectural choices, or past decisions.

**Layer 4** is ephemeral but persistent within a project. It tracks what phase you're in, what was done last session, and what's next — so every session picks up exactly where you left off.

---

## 4. Lifecycle Skills

Skills are invoked with a `/skill-name` command inside Claude Code. Each skill is a structured workflow that chains together sub-agents, standards loading, and superpowers capabilities.

---

### /new-project

Use this when starting a project from scratch with no existing codebase.

**What it does:**
1. Loads global context and preferences
2. Collects your project idea through structured questions
3. Confirms the tech stack
4. Runs brainstorming and planning via sub-agents
5. Scaffolds the directory structure
6. Initializes Git and writes the project's `.claude/memory/` structure

**When to use it:** First session of any new project. Do not manually scaffold — let `/new-project` do it so all memory files are created correctly from the start.

**Example:**
```
/new-project
```
Claude will ask: what is the project? Who is it for? What does success look like? Answer naturally — it extracts what it needs.

---

### /implement

Use this to add features or complete development tasks in an existing project.

**What it does (5 phases):**
1. **Intake** — clarifies scope, reads project memory and architecture
2. **Ideation** — brainstorms the right approach via sub-agent
3. **Plan** — creates a numbered implementation plan, standards-checked before proceeding
4. **Implement** — writes code in TDD style (test first, then implementation)
5. **Verify** — runs tests, checks standards, opens a PR

State for each ticket is written to `.claude/tickets/<ticket-id>/` so work can be resumed if interrupted.

**When to use it:** Every time you add a feature, fix a bug, or make a significant change.

**Example:**
```
/implement
```
Claude will ask what you want to implement and confirm scope before touching any code.

**Resuming interrupted work:**
If a session is cut short, run `/implement` again. Claude reads the saved ticket state and continues from the last completed phase.

---

### /standards-check

Use this before opening a PR or when you want a structured quality review.

**What it does:**
1. Loads standards and the codebase index
2. Reviews changed files against universal and stack-specific standards
3. Runs a code review using the superpowers code review skill
4. Runs the simplify skill to remove unnecessary complexity
5. Outputs a checklist: what passed, what needs attention

**What it checks:**
- Architecture (SOLID, separation of concerns, no god objects)
- Security (input validation, secrets handling, auth)
- Git (commit message format, scope)
- Testing (coverage, test pyramid, no testing internals)
- Documentation (README, inline comments, ADRs for decisions)

**When to use it:** Before every PR. The `/implement` skill runs this automatically in Phase 5, but you can invoke it independently at any time.

**Example:**
```
/standards-check
```

---

### /retrospective

Use this at the end of a project phase or when you notice a recurring pattern worth capturing.

**What it does:**
1. Reads project memory and the session's work
2. Extracts learnings and patterns
3. Proposes additions or changes to toolbox standards or memory
4. Creates a branch and PR in the toolbox repo with the proposed changes
5. Appends the learning to `toolbox/memory/MEMORY.md`

**When to use it:** End of a sprint, after a significant bug, or whenever you learn something that should apply to all future projects.

**Example:**
```
/retrospective
```
Claude will surface what it noticed (e.g., "we consistently structured API errors the same way — should this become a standard?") and ask for your input before proposing anything.

---

### /index-repo

Use this to build or refresh a structural index of the codebase.

**What it does:**
- Runs `tools/indexer/indexer.py` on the project
- Generates JSON files in `.claude/index/`: `files.json`, `symbols.json`, `graph-imports.json`, `graph-calls.json`, `graph-clusters.json`
- Optionally generates semantic vectors via `semantic.py` (tfidf or Ollama mode)
- Writes `.claude/memory/architecture.md` with index metadata
- Writes `.claude/index/README.md` as an index manifest

**When to use it:**
- After cloning an existing codebase for the first time
- When the codebase has grown significantly
- When the session-start hook reports "index stale"

**Example:**
```
/index-repo
```

For incremental updates (faster):
```
/index-repo incremental
```

Once indexed, Claude can answer structural questions precisely — "what imports this module?", "what calls this function?", "what cluster does this file belong to?" — without scanning the codebase manually.

---

### /add-stack-standards

Use this to create standards for a tech stack not yet covered by the toolbox.

**What it does:**
1. Identifies the stack from conversation or project context
2. Asks clarifying questions (framework conventions, patterns to enforce, anti-patterns to avoid)
3. Generates a complete set of standards files: `components.md`, `naming.md`, `testing.md`, `typescript.md`, etc.
4. Creates `_base.md` if the stack inherits from another (e.g., Next.js inherits from React)
5. Opens a PR to the toolbox repo

**When to use it:** When starting work in a stack that has no existing standards in `toolbox/standards/stacks/`.

**Example:**
```
/add-stack-standards
```
Claude will detect your stack and guide the rest.

---

## 5. Standards

### Universal Standards

Loaded for every project regardless of stack. Found in `standards/universal/`:

| File | What it covers |
|---|---|
| `architecture.md` | Clean architecture, SOLID, anti-patterns |
| `security.md` | Input validation, secrets, auth |
| `git.md` | Conventional commits, branching, what not to commit |
| `testing.md` | Test pyramid, TDD, what not to test |
| `documentation.md` | Why over what, README essentials, ADRs |
| `error-handling.md` | Fail fast, structured errors, boundary mapping |
| `code-review.md` | Self-review, PR size, review order |
| `debugging.md` | Systematic process, failing test first, root cause |
| `observability.md` | Structured logging, four golden signals, alerting |

### Stack-Specific Standards

Loaded on top of universal standards when Claude detects your stack. Current stacks:

| Stack | Directory |
|---|---|
| TypeScript + React | `standards/stacks/typescript-react/` |
| TypeScript + Next.js | `standards/stacks/typescript-nextjs/` (extends React) |
| Python + FastAPI | `standards/stacks/python-fastapi/` |
| Go | `standards/stacks/go/` |

Stack standards inherit from each other via `_base.md`. For example, `typescript-nextjs/_base.md` declares that it inherits `typescript-react`, so both are loaded when you're in a Next.js project.

### The Standards Gate

A pre-tool hook blocks Claude from editing files until standards are loaded for the session. This happens automatically — you won't usually notice it. If you see a message like "standards not loaded", run `/load-standards` manually.

### DIGEST.md

`standards/universal/DIGEST.md` is a compact one-page summary of all universal standards. The main Claude session uses this for fast reference; sub-agents load the full standards files for detailed work.

---

## 6. Memory System

### Global Memory (Layer 1)

`toolbox/memory/MEMORY.md` stores cross-project learnings. Each entry is written by `/retrospective` with your approval. Example entries:

- "Always branch and PR — never commit to master directly"
- "Prefer explicit error types at module boundaries over generic exceptions"

These apply to every project you open.

### Project Memory (Layer 3)

Created by `/new-project` or `/implement` (first run) in `<project>/.claude/memory/`:

| File | What it stores |
|---|---|
| `project_context.md` | Name, goal, stakeholders, deadline, success criteria |
| `architecture.md` | Components, boundaries, key decisions, updated by index |
| `stack.md` | Stack choice and rationale |
| `progress.md` | Current phase, last session summary, next task |
| `lessons.md` | Project-specific learnings |
| `decisions/` | ADR files (one per architectural decision) |

Claude reads all of these at session start. You never need to explain your project again.

### Progress File (Layer 4)

`progress.md` is updated at the end of every session. It records:
- What phase the project is in
- What was accomplished last session
- What should happen next

The session-start hook reads this and prints a brief summary so you know exactly where you are.

### Architectural Decision Records (ADRs)

When you make a significant architectural decision (choosing a database, picking an auth strategy, etc.), Claude creates an ADR in `decisions/YYYY-MM-DD-<slug>.md` using the template in `templates/ADR.md`. These are permanent records of why decisions were made, not just what was decided.

---

## 7. Model Selection

When the toolbox launches a sub-agent for a complex task, it selects the most appropriate model based on task complexity.

### Default routing

| Task type | Model |
|---|---|
| File search, pattern matching, simple lookups | haiku |
| Code reading, summarization, straightforward edits | haiku |
| Multi-step implementation, TDD, planning | sonnet |
| Architecture decisions, brainstorming | sonnet |
| Novel problems, ambiguous tasks | opus |
| Security review, high-stakes analysis | opus |

### Saving a preference

When Claude presents model options, add "save this config" to your response:

```
1 save this config
```

Your preference is stored in `memory/model-config.md` and applied silently to all future agent launches.

### Resetting

Delete `memory/model-config.md`. The selection prompt reappears on the next agent launch.

---

## 8. Hooks and Automation

### Session Start Hook

`~/.claude/hooks/session-start.sh` runs when you open any project in Claude Code.

It prints a project brief:
```
Stack: typescript-nextjs
Phase: In Progress — implement auth feature
Next: Write tests for /api/auth/login
Index: up to date
```

If the index is stale (the codebase has changed since the last index run), it warns you to run `/index-repo`.

### Pre-Tool Standards Gate

`~/.claude/hooks/pre-tool-standards-gate.sh` intercepts every Edit/Write/MultiEdit tool call.

It checks for the flag `/tmp/toolbox-standards-loaded-<SESSION_KEY>`. If standards were not loaded this session, it blocks the tool call and prompts you to run `/load-standards` first. This ensures no code is written without the relevant standards in context.

### Stop Hook

Runs on session end. Performs Git hygiene checks (uncommitted changes, unpushed branches) and surfaces anything that needs attention before you close the session.

---

## 9. Day-to-Day Workflow

### Starting a brand-new project

```
1. Create a directory for the project
2. Open it in Claude Code
3. Run: /new-project
4. Answer Claude's questions about the project
5. Claude scaffolds, initializes git, and writes memory files
6. You're ready to start implementing
```

### Adding a feature to an existing project

```
1. Open the project in Claude Code
2. Session start hook prints your current phase and next task
3. Run: /implement
4. Describe what you want to build
5. Claude reads project memory, plans the work, and implements it TDD-style
6. Standards are checked automatically before the PR opens
```

### Preparing a PR

```
1. Run: /standards-check
2. Review the checklist Claude produces
3. Address any issues flagged
4. Run /standards-check again to confirm
5. Claude opens the PR (or you run: gh pr create)
```

### After finishing a phase or noticing a pattern

```
1. Run: /retrospective
2. Review what Claude proposes to add to the toolbox
3. Approve or edit the proposed standards/memory entry
4. Claude opens a PR to the toolbox repo
```

### Onboarding to an existing codebase

```
1. Clone the project
2. Open it in Claude Code
3. Run: /index-repo  (builds the structural index)
4. Ask Claude structural questions: "what calls the auth middleware?", "show me the dependency graph for UserService"
5. Run: /implement when ready to work on a feature
```

---

## 10. Contributing to the Toolbox

All changes to the toolbox go through GitHub PRs — never commit to `master` directly.

### Automatic contribution (preferred)

The `/retrospective` skill creates branches and opens PRs automatically. Use it whenever you want to propose a new standard, update an existing one, or add a cross-project learning.

### Manual contribution

```bash
git checkout -b feat/<your-feature>
# make changes
git commit -m "feat: description of change"
git push -u origin feat/<your-feature>
# open a PR on GitHub
```

### Adding standards for a new stack

Run `/add-stack-standards` inside Claude Code. It asks questions, generates the files, and opens a PR.

### Editing existing standards

Standards files are plain Markdown in `standards/`. Edit them directly, then open a PR. Keep entries:
- Actionable (what to do, not vague advice)
- Specific (concrete examples where helpful)
- Concise (each rule fits in 1-3 lines)

### Adding a new skill

Skills are Markdown files in `skills/` that describe a workflow for Claude to follow. To add one:
1. Create `skills/<skill-name>.md`
2. Add an entry to `CLAUDE.md` under "Lifecycle Skills"
3. Open a PR

---

## Quick Reference

| Command | When to use |
|---|---|
| `Set up the toolbox` | One-time installation in the toolbox directory |
| `/new-project` | Starting a project from scratch |
| `/implement` | Adding a feature or fixing a bug |
| `/standards-check` | Before opening a PR |
| `/retrospective` | Capturing learnings, proposing toolbox improvements |
| `/index-repo` | After cloning an existing codebase or when index is stale |
| `/add-stack-standards` | Adding standards for a new tech stack |
| `/load-standards` | Manual standards load if the pre-tool gate fires |
