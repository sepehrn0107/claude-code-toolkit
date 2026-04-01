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
| `project_context.md` | What the project is, who it's for, and the core problem it solves |
| `stack.md` | Tech stack and why it was chosen |
| `architecture.md` | High-level structure, key modules, code index metadata |
| `progress.md` | What's done, what's in progress, what's next |
| `lessons.md` | Patterns and anti-patterns discovered during development |

**Architectural Decision Records** (`.claude/memory/decisions/`): a separate file per decision, written during `/retrospective` or `/implement` Phase 5 when the plan flagged a decision worth recording. Each ADR is named `YYYY-MM-DD-<slug>.md` and follows the template at `templates/ADR.md`. They are read during `/retrospective` to feed the self-improvement cycle.

**Global memory** (`<workspace>/memory/`): cross-project learnings, model preferences, active project pointer. Organized as topic files (one file per concern) indexed by `MEMORY.md`.

### Session lifecycle

Memory is read once at the start of every session, in parallel — all five per-project files load simultaneously. The session then works from one-line summaries extracted from each file. The full file content is never re-read during the session unless a specific section is explicitly needed again. At the end of the session, any new or changed information is written back using the memory-sync protocol below.

### How memory stays efficient

Writing to memory follows a read-classify-write protocol. Before any write, the existing file is read and each intended entry is classified:

| Classification | Action |
|---|---|
| Already captured (same fact, different words) | Skip — do not duplicate |
| Update to an existing entry | Edit that line in place |
| Correction of stale content | Replace the old entry |
| Genuinely new information | Append only the new entry |

This means memory files grow only when there is something genuinely new to add. Updates happen as targeted edits — not full rewrites. A "move Phase 2 from In Progress to Done" operation becomes two surgical line edits, not a rewrite of the whole file.

The global `MEMORY.md` is an index, not a store. Each entry is a one-line pointer to a topic file. It is capped at 200 lines. Memory files are organized by topic and stale entries are replaced rather than accumulated.

**What is never stored in memory** — even if asked:
- Code patterns derivable from reading the codebase
- Git history (`git log` is authoritative)
- In-progress task state or current conversation context
- Anything already documented in `CLAUDE.md`
- Debugging solutions (the fix is in the code; the commit message has the context)

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

---

### Context architecture

The toolkit's core design principle is that the main session is an orchestrator, not a worker. It never loads file content, large JSON indexes, or full standards documents into its context window. This is enforced structurally, not just by convention.

**The four context layers**

Each layer loads only what its scope requires and exposes a summary to the layer above:

1. **Session hook** (`session-start.sh`) — runs before the first user message. It reads the active project name from a per-session temp file (not a global pointer, so multiple simultaneous sessions don't collide), loads only that project's five memory files in parallel, and prints a single status line. From that point, the session holds extracted one-line summaries — never the full file content.

2. **Routing layer** (`CLAUDE.global.md`) — maps plain-English phrases to skill files via a routing table. When a phrase matches, the skill is read and followed before any response. The routing table itself is compact — each row is a phrase pattern and a file path. No standards or memory content lives here.

3. **Standards gate** (PreToolUse hook) — before any file edit is allowed, the hook checks for a session flag: a zero-byte file at `/tmp/toolbox-standards-loaded-<session-id>`. If it doesn't exist, the edit is blocked. The flag is created by `/load-standards` after it confirms all applicable standards have been read. This makes it structurally impossible to write code without having loaded the relevant standards first.

4. **Sub-agent boundary** — the main session passes sub-agents only what they need: ticket state file paths, applicable standards file paths, and the component name. Sub-agents read the files themselves, do the reasoning, write their output to a bounded Markdown file (the ticket state), and return a one-line status. The main session reads only that status line — not the output content — and moves to the next phase.

**Ticket state files as context boundaries**

Each phase of `/implement` writes its output to a file in `.claude/tickets/<ticket-id>/`:

```
context.md        ← Phase 0: project snapshot
ideation.md       ← Phase 1: scope, risks, design decisions
plan.md           ← Phase 2: file-level implementation plan
implementation.md ← Phase 3: per-component summaries (appended)
verification.md   ← Phase 4: test results and verdict
pr.md             ← Phase 5: PR URL and standards check results
```

Each file is bounded — its format is defined, its size is controlled. The next phase reads only the files it needs from the previous phase. No phase's output ever enters the main session's context window directly. This also makes long workflows fully resumable: if Claude is interrupted after Phase 2, the next session reads the existing `plan.md` and picks up at Phase 3.

**How sub-agents inherit context**

Sub-agents spawned via the `Agent` tool automatically load `~/.claude/CLAUDE.global.md` because it is configured as a global instruction source. This means every sub-agent already knows the routing rules, memory protocols, standards gate behavior, and skill invocation conventions — without the orchestrator injecting any of it. The orchestrator only needs to pass the ticket state paths and task description.

---

### Token efficiency

Several mechanisms reduce API token consumption across the full workflow, operating at different layers.

**Compact standards digest**

When orchestrating `/implement`, the main session loads `standards/universal/DIGEST.md` — a one-page summary of all 9 universal standards files — rather than loading the full set. Sub-agents receive paths to only the specific full standards files they actually need for their phase. The digest is under 100 lines; the full standards set across all 9 files is several thousand lines. Stack standards are loaded by sub-agents only when the detected stack is active.

Stack inheritance is also lean: when a stack has a base (e.g., `typescript-nextjs` inherits `typescript-react`), a `_base.md` file declares the dependency. Only the relevant stack files are loaded — not the entire stacks directory.

**Surgical file reading**

When only one function, class, or section is needed from a large file, `tools/read-section/read_section.py` extracts it by name without loading the rest. The tool applies language-aware extraction:

| Language | Block detection |
|---|---|
| Python | Indentation-based (function/class boundaries from indent depth) |
| JS / TS / Go / Java / C# / Rust | Brace counting (tracks nesting depth to find the closing `}`) |
| Markdown | Heading hierarchy (extracts content under the specified heading) |
| Others | Brace → indent fallback |

It is triggered automatically when Claude needs one symbol from a file over 100 lines. Instead of loading a 400-line controller to read one handler, it extracts the 30-line function and nothing else.

**Two-phase code search**

The grep skill enforces a two-phase pattern: first retrieve only matching file paths (no content, minimal tokens), then read content from the specific files identified. Broad content searches across the full repo on the first attempt are prohibited. All content searches cap output with `head_limit` to prevent unbounded result sets from filling the context window.

**Structural index as context substitute**

After running `/index-repo`, structural questions about the codebase — "what calls X?", "what imports Y?", "which files are in the auth cluster?" — are answered by a haiku sub-agent that reads only the specific index JSON file relevant to the question:

| Question type | Index file read |
|---|---|
| What's in a cluster / what areas exist? | `graph-clusters.json` |
| What imports X / what does X depend on? | `graph-imports.json` |
| What calls X / what does X call? | `graph-calls.json` |
| What does function X do / its signature? | `symbols.json` — filtered to matching entries |
| What does file X export? | `files.json` — filtered to matching path |
| Files related to X (semantic) | `vectors.json` (when semantic layer is enabled) |

The sub-agent returns a structured answer of a few lines. Neither the raw JSON files nor the source files enter the main session's context window. The index also supports incremental re-runs — only changed files are re-processed, so large projects don't pay the full indexing cost after minor edits.

The semantic layer (optional) adds TF-IDF or Ollama embedding-based similarity, enabling "files related to X" queries. This is configured once and reused automatically on all subsequent queries.

**Tier 0 — local LLM**

Mechanical tasks are routed to a local LLM via LM Studio, bypassing the Claude API entirely. Before every sub-agent call, `select-model.md` checks if the task type maps to Tier 0:

| Tier 0 task type | Notes |
|---|---|
| Single-function code generation (signature given) | Fits in one prompt |
| Unit test scaffolding for a given function | Formulaic output |
| Code summarization (< 200 lines) | No standards required |
| Docstrings / inline documentation | Mechanical |
| Simple single-file refactoring (rename, extract, lint fix) | Deterministic |
| Boilerplate / CRUD skeleton generation | Template-driven |

Prompts are kept under 500 tokens — only the function signature, description, and constraints are included, never full files. Results are cached for 24 hours at `tools/local-llm/cache/` — identical prompts return in under 10ms without hitting the LLM at all. If LM Studio is unreachable, the task falls back to a haiku sub-agent silently.

For `/implement` Phase 3, each component is classified before routing: **simple** (single file, ≤ ~100 LOC, no cross-file dependencies) goes through the local LLM + haiku review path; **complex** (multiple files, cross-cutting logic) uses a full sonnet sub-agent.

**Web page cache**

External URLs fetched through Crawl4AI are cached for 24 hours as clean markdown files in `<workspace>/vault/07-web-cache/`. The same documentation page is never fetched twice in a day.

**Model tiering**

Sub-agents are assigned the cheapest model sufficient for the task. Before every Agent call, the `select-model` skill evaluates the task and recommends:

| Task type | Model |
|---|---|
| File search, pattern matching, simple lookups | haiku |
| Code reading, summarization, straightforward edits | haiku |
| Index queries (structural questions about the codebase) | haiku |
| Multi-step implementation, TDD, code generation | sonnet |
| Architecture decisions, brainstorming, planning | sonnet |
| Security review, high-stakes analysis | sonnet |

The user can save a model preference once; it is read from `memory/model-config.md` and reused across all sessions without prompting.

**Single-read memory**

Project memory files are read once at session start, in parallel. Within the session, Claude works from extracted one-line summaries per file. Memory files are never re-read during the same session unless a specific section is explicitly needed again.

---

### Stack standards included

| Stack | What's covered |
|---|---|
| `typescript-react` | Components, naming, styling, testing, TypeScript conventions |
| `typescript-nextjs` | Routing, rendering (SSR/SSG/ISR), API routes — inherits React standards |
| `go` | Package design, error handling, testing, toolchain |
| `python-fastapi` | Route structure, dependency injection, validation, testing |
| `drizzle-postgres` | Schema design, migrations, query patterns, type safety |

---

## Skills

Skills are the toolkit's unit of reusable behavior. Each skill is a plain Markdown file with YAML frontmatter and a sequence of steps. Claude reads the skill file at runtime and follows it exactly.

**Skill file format:**
```markdown
---
name: skill-name
description: When this skill applies and what it does — used for automatic routing
---

# /skill-name

Step-by-step instructions...
```

The `description` field is what the routing system matches against. The body contains the actual steps Claude follows — tool calls, sub-agent prompts, output formats, fallback logic.

### How routing works

`~/.claude/CLAUDE.global.md` contains an automatic routing table that maps plain-English phrases to skill files. When the user's message matches a row, the skill file is read and followed before any other response — no slash command required. The routing table covers intent patterns for every common workflow:

```
"fix [bug]"       → superpowers:systematic-debugging
"add [feature]"   → /implement skill
"push this"       → /git-push skill
"review this"     → /standards-check skill
```

Beyond explicit phrase matching, several skills trigger automatically on Claude's own internal actions: before any `WebFetch` call, before running multiple git commands, before writing to any memory file, before any code search, before reading one section from a large file. These automatic triggers require no user prompt — they fire whenever Claude is about to take the relevant action.

### First-party skills

Skills that ship with the toolkit live in `toolbox/skills/`. They use `{{TOOLBOX_PATH}}` as a placeholder for the install path, write structured output to ticket state files, and follow the toolkit's conventions for sub-agent orchestration and memory writes.

### Third-party skills via Claude Code plugins

Claude Code's plugin system allows any plugin to expose skills that are invocable via the `Skill` tool using a plugin-prefixed name (e.g., `superpowers:brainstorming`). The toolkit integrates several third-party plugins directly into its routing and lifecycle skills:

| Plugin | Skills used | Where invoked |
|---|---|---|
| `superpowers` | `brainstorming`, `systematic-debugging`, `test-driven-development`, `writing-plans`, `requesting-code-review`, `verification-before-completion` | Ideation, debugging, Phase 3 TDD, Phase 5 review |
| `codex` | `setup`, `rescue`, `codex-review`, `codex-delegate` | Session start (setup), Phase 3 delegation, Phase 4 review |
| `frontend-design` | `frontend-design` | UI component generation tasks |

These are invoked by path (`superpowers:brainstorming`) from within toolkit skills. No configuration is needed — if the plugin is installed, the skill is available. If a plugin is not installed, the toolkit detects the failure and falls back gracefully (e.g., Codex delegation falls back to direct Claude; `superpowers` skills fall back to Claude's built-in reasoning).

### Using skills from other users

Any Claude Code plugin can expose skills that the toolkit will route to automatically, as long as:

1. The plugin is installed in Claude Code
2. A routing row is added to the `## Automatic Skill Routing` table in `templates/CLAUDE.global.md`
3. `/upgrade-dev` is run to sync the live install

Because skills are plain Markdown files, they can be shared as GitHub repos, gists, or pull requests to this toolkit. The `/retrospective` skill can generate new skills from your own project learnings and open a PR to the toolkit — see [Self-improvement](#self-improvement) below.

### Adding your own skill

1. Create `toolbox/skills/<name>.md` with frontmatter and step-by-step instructions
2. Add a row to the `## Automatic Skill Routing` table in `templates/CLAUDE.global.md`
3. Run `/upgrade-dev` to sync the live install
4. Optionally open a PR to share it with other users

---

## Self-improvement

The `/retrospective` skill closes the feedback loop between working on a project and improving the toolkit itself. It runs at project completion or after any significant milestone, and is suggested automatically after `/implement` completes.

### What it reads

The skill reads all project memory files in full: `project_context.md`, `stack.md`, `architecture.md`, `progress.md`, `lessons.md`, and all architectural decision records in `decisions/`. This gives it the full history of what was built, what stack-specific patterns emerged, what decisions were made and why, and what was learned.

### What it produces

For each learning identified, the skill classifies it into one of four change types and proposes the appropriate update:

| Learning type | Proposed change |
|---|---|
| Universal pattern not yet in standards | Add to or update `standards/universal/<file>.md` |
| Stack-specific convention discovered | Add to `standards/stacks/<stack>/` |
| Recurring workflow not yet a skill | Write a new skill file in `skills/` |
| Pattern from another stack worth promoting | Promote to `standards/universal/` |

Each proposed change is presented to the user one at a time. Nothing is written or committed without explicit approval for that specific change.

### How approved changes reach the toolkit

For each approved change, the skill:

1. Creates a branch in the local toolbox clone: `retro/<slug>-YYYY-MM-DD`
2. Writes the content to the appropriate file under `standards/` or `skills/`
3. Commits with a descriptive message following Conventional Commits format
4. Opens a PR to the toolbox GitHub repository — the PR body describes what was learned, from which project, and why the change is proposed

This is not a bulk operation — each learning becomes its own branch and PR, so they can be reviewed and merged independently.

### Personal learnings (no PR)

Cross-project learnings that are personal — model preferences, workspace-level conventions, observations about your own workflow — are written directly to global memory (`<workspace>/memory/`) via the memory-sync protocol. These don't require a PR and take effect immediately in the next session.

### The compounding effect

Because standards and skills are updated from real project work rather than hypothetical best practices, they grow more accurate over time. Stack standards get richer with each project that uses them. New recurring workflows become skills. Cross-project patterns accumulate in global memory and inform future sessions. The toolkit you use a year from now will be shaped by the actual patterns that worked — not just the ones that seemed reasonable at install time.

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
