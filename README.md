<div align="center">
  <img src="logo.svg" width="80" alt="claude-code-toolkit" />

  # claude-code-toolkit

  Give Claude Code a permanent memory, consistent rules, and a structured way to work —<br>across every project, every session.

  ![License](https://img.shields.io/badge/license-MIT-green)
  ![Version](https://img.shields.io/badge/version-1.7.0-purple)
  ![Claude Code](https://img.shields.io/badge/Claude%20Code-compatible-blue)
</div>

---

## The problem

Every Claude Code session starts cold.

It doesn't know your project, your tech stack, your past decisions, or how you like to work. You re-explain everything. Every time. And the moment you close the window, it's gone.

---

## The fix

This toolkit installs once and runs silently in the background every time you open Claude Code.

It gives Claude:
- **A persistent memory** — reads your project context, stack, and past decisions at the start of every session automatically
- **Rules it always follows** — coding standards, security practices, git hygiene — loaded per project, never forgotten
- **A built-in workflow** — the right process for every task, triggered by plain English

You open a project. Claude already knows what it is, what stack it uses, and what you were working on. No setup. No re-explaining.

---

## Who is this for?

| | |
|---|---|
| **🙋 I don't write code** | You use Claude to help you write, research, plan, or build things — and you're tired of explaining your project from scratch every session. This toolkit makes Claude remember. Setup takes 5 minutes and you never touch it again. |
| **👩‍💻 I'm a developer** | You use Claude Code daily but work without structured workflows — no consistent standards, no memory between sessions, no automatic routing to the right process. This toolkit fixes all three. One install, every project. |

---

## See it in action

> **Session without the toolkit:**
> You: *"I'm working on a Next.js app with Drizzle ORM, here's what we built last time..."*
> *(re-explains the whole project, every single session)*

> **Session with the toolkit:**
> Claude: *"Active project: my-app | Stack: Next.js + Drizzle + TypeScript | Last session: implemented auth middleware, next up: dashboard route. Ready to continue."*
> You: *"add the dashboard route"*
> Claude: *(reads plan, loads Next.js standards, runs TDD implementation, opens PR — no prompting)*

---

## Install

**Requirements:** [Claude Code](https://claude.ai/code), Git, Python 3

```bash
# 1. Create a workspace folder and clone
mkdir -p ~/Documents/workspace
git clone https://github.com/sepehrn0107/claude-code-toolkit ~/Documents/workspace/toolbox

# 2. Open the toolbox folder in Claude Code, then say:
Set up the toolbox
```

That's it. Claude handles the rest — it writes the config files, installs the hooks, and sets up your memory system.

> **Already have a workspace?** Clone the toolkit as a subfolder named `toolbox` inside your existing workspace folder, then say `Set up the toolbox`.

---

## What it does

### Claude remembers your project

At the start of every session, the toolkit reads your project's memory files — what the project is, what stack you're using, what decisions you've made, and what you were working on last time. You never re-explain.

**Example:**
> You open Claude Code in your project
> Claude: *"Loaded: my-app | Stack: Python + FastAPI | Last session: finished user auth, next: build the API endpoints for profiles"*

---

### Say what you want — it knows what to do

You don't need to know slash commands or workflows. The toolkit detects your intent and routes to the right process automatically.

| You say | What happens |
|---|---|
| `"add [feature]"` | Full implementation workflow: brainstorm → plan → TDD → PR |
| `"fix [bug]"` | Systematic debugging process |
| `"push this"` | Groups commits logically, writes conventional commit messages, opens PR |
| `"new project"` | Full scaffold: memory files, stack detection, design system, git init |
| `"review this"` | Standards check across architecture, security, testing, git hygiene |
| `"switch project"` | Loads a different repo from your workspace |

---

### Coding standards, automatically

The toolkit ships with standards for common stacks. When you work on a project, the right standards load automatically — your code is reviewed against them before every commit.

**Available stacks:** TypeScript + React, Next.js, Go, Python + FastAPI, Drizzle + PostgreSQL

**What standards cover:** architecture patterns, naming conventions, security rules, testing expectations, git hygiene

> No more *"Claude, please follow our naming conventions"* — it just does.

Add standards for a new stack anytime: say `"add standards for [stack]"`.

---

### Full feature implementation, start to finish

Say `"add [feature]"` and the toolkit runs a 5-phase workflow end to end:

| Phase | What happens |
|---|---|
| **1. Understand** | Reads your memory and standards, writes a context doc |
| **2. Plan** | Brainstorms scope, risks, edge cases; produces a file-level plan |
| **3. Build** | TDD implementation, red-green-refactor, follows your stack standards |
| **4. Verify** | Checks tests pass, edge cases covered, error paths handled |
| **5. Ship** | Standards check, conventional commit, opens PR via GitHub CLI |

All state saves to `.claude/tickets/` — if interrupted, it resumes from where it left off.

---

### Code index for large projects

Run `/index-repo` once and the toolkit builds a structural map of your codebase — every file, its symbols, imports, and call relationships. Claude uses this map automatically instead of grepping, keeping searches fast and context usage low.

---

### Web design audit

Before any PR that touches UI, the toolkit automatically audits your design for 9 areas: design tokens, typography, spacing, color contrast, accessibility (WCAG 2.1 AA), responsive layout, page flow, component consistency, and token adherence. Outputs a prioritized fix list with exact file references.

---

### Fetch any URL cleanly

Routes web fetches through a local [Crawl4AI](https://github.com/unclecode/crawl4ai) container — clean markdown output, 24-hour cache. Never fetches the same page twice in a day. Requires Docker.

---

### Delegate to Codex (optional)

When [Codex CLI](https://github.com/openai/codex-plugin-cc) is installed, implementation tasks in Phase 3 are automatically delegated to it. Falls back to direct Claude silently if unavailable.

---

## Memory

The toolkit remembers things in two places:

**Per-project memory** (`.claude/memory/` in each project):

| File | What's stored |
|---|---|
| `project_context.md` | What the project is and who it's for |
| `stack.md` | Tech stack and why it was chosen |
| `architecture.md` | High-level structure, key modules |
| `progress.md` | What's done, what's next |
| `lessons.md` | Patterns and anti-patterns discovered |

**Global memory** (`<workspace>/memory/`): cross-project learnings, model preferences, active project pointer.

Memory is read at the start of every session. It's written at the end. It grows as you work.

---

## How it works (for developers)

Four layers load in order:

```
~/.claude/CLAUDE.md              ← your global config (a single @import — never overwritten by upgrades)
~/.claude/CLAUDE.global.md       ← toolbox routing, skills, session rules
<workspace>/toolbox/standards/   ← universal + stack-specific coding standards
<project>/.claude/memory/        ← project context, loaded each session
```

Two shell hooks run automatically:
- **`session-start.sh`** — detects the active project, prints status, loads context
- **`pre-tool-standards-gate.sh`** — blocks file edits until standards are loaded for the session

Sub-agents spawned during `/implement`, code reviews, etc. inherit all rules automatically via the global `CLAUDE.md` — no explicit context injection needed.

### Stack standards included

| Stack | What's covered |
|---|---|
| `typescript-react` | Components, naming, styling, testing, TypeScript conventions |
| `typescript-nextjs` | Routing, rendering (SSR/SSG/ISR), API routes — inherits React standards |
| `go` | Package design, error handling, testing, toolchain |
| `python-fastapi` | Route structure, dependency injection, validation, testing |
| `drizzle-postgres` | Schema design, migrations, query patterns, type safety |

---

## Optional setup

### Codex delegation

```bash
npm install -g @openai/codex
codex   # authenticate once via browser
```

Implementation tasks in `/implement` Phase 3 are then delegated to Codex automatically. Falls back to direct Claude if Codex is unavailable.

### Web fetching via Crawl4AI

```bash
docker run -d -p 11235:11235 --name crawl4ai --shm-size=1g unclecode/crawl4ai:latest
```

### Local LLM (Tier 0 — zero API cost)

Routes mechanical tasks (boilerplate, docstrings, simple refactors) to a local LLM via LM Studio. See [`skills/local-llm.md`](skills/local-llm.md).

---

## Contributing

All changes go through PRs. The `/retrospective` skill handles this automatically — it creates a branch, commits the proposed change, and opens a PR from within Claude Code.

To contribute manually:

```bash
git checkout -b feat/your-feature
git commit -m "feat: description"
gh pr create
```

---

## License

MIT
