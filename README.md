# claude-code-toolkit

Standards, memory, and lifecycle skills for Claude Code — loads automatically across every project.

Every Claude Code session starts cold: no memory of your stack, your decisions, or what you built last week. This toolkit fixes that. It loads your coding standards, reads project memory so you never repeat context, and guides each phase of development with the right workflow. You run one command; it handles the rest.

---

## Who Is This For

Developers who use Claude Code regularly and want it to behave consistently across projects — following the same standards, remembering past decisions, and running the right workflow for each task (new feature, bug fix, PR review) without being told each time.

---

## Getting Started

**Requirements:** Claude Code installed, Git, Python 3, Docker (for `/web-fetch` and `/local-llm`).

### 1. Clone the toolkit

Clone into a workspace directory — the toolkit must live **one level below** the workspace root, because memory and Claude settings are installed at the workspace level (not inside the repo).

```bash
mkdir -p ~/Documents/workspace
git clone https://github.com/sepehrn0107/claude-code-toolkit ~/Documents/workspace/toolbox
```

### 2. Run setup

Open the toolbox directory in Claude Code and say:

```
Set up the toolbox
```

Claude will:
- Write `~/.claude/CLAUDE.md` pointing to your local clone
- Install hooks into `~/.claude/hooks/`
- Create `<workspace>/.claude/settings.json` with plugins and hooks config
- Create `<workspace>/memory/` for global cross-project memory

That's the only manual step.

### 3. Start using it

In any project directory, open Claude Code and use the skills below.

---

## How It Works

The toolkit is organized as 4 layers:

```
Layer 1 — Global preferences     ~/.claude/CLAUDE.md + <workspace>/memory/
Layer 2 — Stack standards        <workspace>/toolbox/standards/
Layer 3 — Project context        <project>/.claude/memory/
Layer 4 — Session context        progress.md (written each session)
```

**Standards** live in `standards/universal/` (applies everywhere) and `standards/stacks/<stack>/` (loaded per project automatically).

**Skills** in `skills/` orchestrate the right workflow for each phase of development. They chain together Claude Code superpowers skills — brainstorming, TDD, code review, etc. — so the right process is always followed without you having to ask.

**Memory** persists context across sessions — project goals, stack decisions, architectural choices, lessons learned. Nothing is re-explained from scratch.

---

## Skills

Skills are triggered by saying what you want to do — the toolkit detects intent and routes to the right skill automatically. You can also invoke them directly with `/skill-name`.

### `/new-project` — Start a new project from scratch

**Trigger phrases:** "new project", "starting fresh", "scaffold this"

Handles everything from idea to first commit:

1. Reads global memory and detects stack signals (`package.json`, `go.mod`, etc.)
2. Asks about the project — goal, users, constraints, success criteria
3. Confirms or detects the stack; loads stack standards; drafts new standards if the stack is unknown
4. If the project has a UI, invokes the `ui-ux-pro-max` skill to establish the design system first
5. Runs brainstorming (`superpowers:brainstorming`) and produces an implementation plan
6. Scaffolds `.claude/memory/` with filled templates: `project_context.md`, `stack.md`, `architecture.md`, `progress.md`, `lessons.md`
7. Runs `git init` and makes the initial commit

After this, run `/implement` to start building.

---

### `/implement` — Add a feature to an existing project

**Trigger phrases:** "add [X]", "implement [X]", "build [X]", "work on ticket [X]"

Full lifecycle from ticket to open PR, orchestrated across 5 phases. Each phase runs as a focused sub-agent; the main session holds only file paths, not content.

**Phase 0 — Intake:** reads memory and standards, writes `.claude/tickets/<ticket-id>/context.md`

**Phase 1 — Ideate:** brainstorms the feature — scope, edge cases, risks, what's out of scope. Writes `ideation.md`. If a code index exists, queries it for relevant files.

**Phase 2 — Plan:** produces a file-level implementation plan — numbered steps, test strategy, component breakdown, ADR draft if needed. Writes `plan.md`.

**Phase 3 — Implement:** TDD implementation per component. Reads stack standards before touching any code. Follows red-green-refactor. Appends to `implementation.md`.

**Phase 4 — Verify:** checks that tests pass, edge cases are covered, error paths are handled. Writes `verification.md`. If issues found, loops back to Phase 3 (max 2 retries).

**Phase 5 — PR:** full standards check, conventional commit, opens PR via `gh`. Writes `pr.md` with the PR URL.

All state lives in `.claude/tickets/<ticket-id>/` — if interrupted, the skill resumes from the last completed phase.

---

### `/standards-check` — Review code before merging

**Trigger phrases:** "check this", "review", "ready to merge", "before PR"

Runs automatically before any push or PR — you don't need to ask. Checks:

- **Architecture** — separation of concerns, clean layer boundaries, no business logic in controllers
- **Security** — input validation at boundaries, no hardcoded secrets, no OWASP violations
- **Git** — conventional commit messages, no secrets committed
- **Testing** — business logic covered, tests test behavior not implementation
- **Documentation** — README present, ADRs written for key decisions, non-obvious code commented

Also invokes `code-simplifier` for a quality and clarity pass on recently changed code.

If a code index exists, uses it to determine the blast radius — changed files plus their direct importers — so the review scope is accurate.

Outputs a checklist with pass/fail and file references for failures. All failures must be addressed before merging.

---

### `/retrospective` — Capture learnings and improve the toolkit

**Trigger phrases:** "retrospective", "retro", "capture learnings", "what did we learn"

Also offered automatically after `/implement` completes.

1. Reads all project memory files and decisions
2. Identifies what worked, what didn't, new reusable patterns, stack-specific learnings
3. Proposes updates to the toolkit — existing standards, new stack standards, universal promotions, new skills — one at a time
4. For each approved change: creates a branch in the toolbox clone, commits, and opens a PR to the toolkit repo
5. Writes key learnings to global memory (`<workspace>/memory/`)

This is how the toolkit improves itself from real work.

---

### `/web-fetch` — Fetch any external URL via Crawl4AI

**Auto-trigger:** whenever Claude is about to use `WebFetch` to read a page's full content

Routes outbound URL fetches through a local [Crawl4AI](https://github.com/unclecode/crawl4ai) container for clean markdown output and automatic caching.

1. Runs `tools/crawl4ai/fetch.py --url "<URL>"` via Bash
2. Returns clean markdown on stdout; stderr carries status messages (`cache hit`, `fetching`, etc.)
3. Caches results in `<workspace>/vault/07-web-cache/<domain>/<path>.md` with a 24-hour TTL
4. Falls back to the built-in `WebFetch` tool if the container is not running, with a setup reminder

**Requires Docker:** start the container once with:
```bash
docker run -d -p 11235:11235 --name crawl4ai --shm-size=1g unclecode/crawl4ai:latest
```

---

### `/git-push` — Stage, commit, and open a PR

**Trigger phrases:** "push to git", "push this", "commit and push", "open a PR", "ship this", "lets push"

Enforces clean git hygiene:

1. Inspects `git status` and `git diff`
2. If on `main`/`master`, asks for a branch name and checks out
3. Groups changed files into logical commits by what they accomplish together (not by file type)
4. Shows the proposed commit grouping for confirmation if non-obvious
5. Commits each group with a [Conventional Commits](https://www.conventionalcommits.org/) message
6. Pushes and opens a PR with what/why/how/test-plan body

Never uses `git add .` — always adds specific files. Never pushes directly to `main`/`master`.

---

### `/index-repo` — Build a structural code index

**Trigger phrases:** "index this repo", `/index-repo`

Also suggested automatically when Claude is struggling to navigate a large codebase.

Runs the Python indexer (`tools/indexer/indexer.py`) to produce JSON files in `.claude/index/`:

- `files.json` — every file with its symbols, imports, and tags
- `graph-imports.json` — import relationships
- `graph-calls.json` — call relationships
- `graph-clusters.json` — domain clusters (logical groupings of related files)
- `README.md` — human-readable summary with entry points and cluster descriptions

Supports an optional semantic layer for similarity queries:
- **none** — structural index only
- **tfidf** — algorithmic similarity (requires scikit-learn)
- **ollama** — local LLM embeddings via Ollama

Supports incremental re-runs — only changed files are re-processed.

Once built, Claude uses the index automatically before falling back to grep/glob, keeping searches fast and context usage low.

---

### `/add-stack-standards` — Add standards for a new stack

**Trigger phrases:** "add standards for [stack]", "document my stack", "add [Go/TypeScript/etc] conventions"

1. Detects or asks for the stack name
2. Asks clarifying questions: state management, testing framework, styling, build tooling, team conventions
3. Generates standards files under `standards/stacks/<stack>/` — components/modules, naming, testing, and any stack-specific topics
4. If the stack extends another (e.g., Next.js extends React), creates `_base.md` for inheritance
5. Commits and opens a PR to the toolkit repo

---

### `/project` — Switch active project

**Trigger phrases:** "switch project", "change project", "work on [repo]"

Manages which project is active when Claude Code is opened at the workspace root.

- `/project switch` — shows all repos in the workspace, lets you pick one, loads its memory
- `/project list` — shows all repos and marks the currently active one
- `/project status` — shows active project name, stack, current phase, and next task

The active choice is persisted in `<workspace>/memory/active-project.md` — future sessions auto-load the right context.

---

## Standards

### Universal Standards

Applied to every project regardless of stack. Located in `standards/universal/`:

| File | What it covers |
|------|----------------|
| `architecture.md` | Separation of concerns, layer boundaries, dependency direction, module design |
| `security.md` | Input validation, secrets management, OWASP top 10, auth patterns |
| `testing.md` | TDD approach, what to test, test structure, coverage expectations |
| `error-handling.md` | Fail fast, error context, validation at boundaries, retry logic, anti-patterns |
| `debugging.md` | Scientific method for debugging, binary search, layer-specific tools, when to escalate |
| `code-review.md` | What PR authors and reviewers should look for, how to give and receive feedback |
| `observability.md` | Logging, metrics, health checks, distributed tracing, alerting |
| `documentation.md` | README standards, ADRs, inline comments, API docs |
| `git.md` | Conventional commits, branch naming, PR hygiene |

### Stack Standards

Located in `standards/stacks/<stack>/`. Currently available:

- **`typescript-react`** — components, naming, styling, testing, TypeScript conventions
- **`typescript-nextjs`** — routing, rendering (SSR/SSG/ISR), API routes, base React conventions
- **`go`** — package design, error handling, testing, toolchain
- **`python-fastapi`** — route structure, dependency injection, validation, testing
- **`drizzle-postgres`** — schema design, migrations, query patterns, type safety

Stacks can extend each other: `typescript-nextjs` declares `base: typescript-react` in `_base.md`, so React standards are inherited automatically.

To add standards for a new stack, run `/add-stack-standards`.

---

## Memory System

Memory is organized into layers:

```
<workspace>/memory/           ← global, cross-project
<project>/.claude/memory/    ← per-project
```

**Per-project memory files** (in `.claude/memory/`):

| File | What's stored |
|------|---------------|
| `project_context.md` | What the project is, who uses it, key constraints |
| `stack.md` | Active stack and why it was chosen |
| `architecture.md` | High-level structure, key modules, code index summary |
| `progress.md` | Current phase, what's done, what's next |
| `lessons.md` | Patterns and anti-patterns discovered during development |
| `decisions/` | ADRs — one file per architectural decision |

**Global memory** (`<workspace>/memory/`) stores cross-project learnings, model preferences, and the active project pointer.

Memory is read at the start of every session automatically — you never need to re-explain what a project is.

---

## Model Selection

When the toolkit launches a sub-agent, it picks the most cost-effective model for the task — including a Tier 0 local LLM path for mechanical tasks.

| Tier | Task type | Model |
|------|-----------|-------|
| 0 | Single-function codegen, unit test scaffolding, docstrings, simple refactors, boilerplate | local LLM (LM Studio) |
| 1 | File search, pattern matching, simple lookups | haiku |
| 1 | Code reading, summarization, straightforward edits | haiku |
| 2 | Multi-step implementation, TDD, code generation | sonnet |
| 2 | Architecture decisions, brainstorming, planning | sonnet |
| 2 | Security review, high-stakes analysis | sonnet |

**Tier 0** runs fully automatically when LM Studio is running locally — no prompt shown to the user. If LM Studio is unreachable, routing falls through to haiku/sonnet as normal. See `skills/local-llm.md` for setup.

### Saving a preference

To persist a model choice, respond to any model selection prompt with your choice and add **"save this config"**:

```
2 save this config
```

Your preference is stored in `<workspace>/memory/model-config.md` and applied to all future agent launches. To reset, delete that file.

---

## Session Hooks

Two shell hooks run automatically:

- **`session-start.sh`** — runs at the start of every Claude Code session. Detects the active project (from `active-project.md`) and prints a status line so you know which project is loaded.
- **`pre-tool-standards-gate.sh`** — blocks file edits until standards have been loaded for the session. Prevents accidental code changes that bypass standards.

Hooks are installed to `~/.claude/hooks/` during setup.

---

## Automatic Skill Routing

You don't need to remember slash commands. The toolkit detects what you're trying to do:

| You say… | What runs |
|----------|-----------|
| "add [X]", "implement [X]", "build [X]" | `/implement` |
| "fix [X]", "debug [X]", "not working" | `superpowers:systematic-debugging` |
| "check this", "review", "ready to merge" | `/standards-check` |
| "new project", "starting fresh", "scaffold" | `/new-project` |
| "switch project", "work on [repo]" | `/project` |
| "push to git", "open a PR", "ship this" | `/git-push` |
| "add standards for [stack]" | `/add-stack-standards` |
| About to call `WebFetch` to read a page | `/web-fetch` |
| Any code edit (none of the above) | loads standards, then edits |

---

## Contributing

All changes go through GitHub PRs — nothing is committed to `master` directly.

The `/retrospective` skill handles this automatically: it creates a branch, commits the proposed change, and opens a PR for review.

To contribute manually:

```bash
git checkout -b feat/<your-feature>
# make changes
git commit -m "feat: description"
gh pr create
```
