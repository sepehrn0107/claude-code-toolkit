# Toolbox

Standards, memory, and lifecycle skills for all projects.
Source: https://github.com/sepehrn0107/toolbox (local clone: {{TOOLBOX_PATH}})

## Session Start (automatic)

At the start of every session, before responding to the first message, do all of this silently:

1. Check if `.claude/memory/MEMORY.md` exists in the current project
2. If yes: read all memory files in parallel — `project_context.md`, `stack.md`, `architecture.md`, `progress.md`, `lessons.md`
3. Also read `{{TOOLBOX_PATH}}/memory/MEMORY.md` to load global cross-project learnings
4. Note whether `.claude/index/README.md` exists — if it does, it is available for code navigation
5. Do not announce any of this — just have the context ready before responding

## Automatic Skill Routing

Detect user intent from the first message and route automatically — do not wait to be asked:

| User says…                                                              | Auto-trigger                          |
|-------------------------------------------------------------------------|---------------------------------------|
| "add [X]", "implement [X]", "build [X]", "create [feature]", "work on [ticket]", "ticket [X]" | Read and follow `/add-feature` skill  |
| "fix [X]", "debug [X]", "something is broken", "not working"            | Invoke `superpowers:systematic-debugging` |
| "check this", "review [X]", "ready to merge", "before PR"              | Read and follow `/standards-check`    |
| "new project", "starting fresh", "scaffold this"                        | Read and follow `/new-project`        |
| Any code edit request (none of the above matched)                       | Run `/load-standards` then proceed    |

Read the skill file from `{{TOOLBOX_PATH}}/skills/<skill>.md` before following it. Do not ask the user to run the skill — just do it.

## Standards

Before writing or editing any code, standards must be loaded. Two modes:

- **Orchestrating via `/add-feature`**: read only `{{TOOLBOX_PATH}}/standards/universal/DIGEST.md`
  (the compact 1-page reference). Full standards are loaded by sub-agents per phase.
  Do not read all 9 standards files into the main session.
- **Direct one-off edits**: invoke `{{TOOLBOX_PATH}}/skills/load-standards.md` and wait for
  the confirmation line. This is a blocking requirement — do not proceed without it.

## Before Any PR (automatic)

When preparing to push code or open a PR — even if the user does not ask — automatically run `/standards-check` first. Do not skip this.

## Lifecycle Skills

Skills are loaded from the local toolbox clone. Read the skill file before following it.

- /new-project      → {{TOOLBOX_PATH}}/skills/new-project.md
- /add-feature      → {{TOOLBOX_PATH}}/skills/add-feature.md
- /standards-check  → {{TOOLBOX_PATH}}/skills/standards-check.md
- /retrospective    → {{TOOLBOX_PATH}}/skills/retrospective.md
- /add-stack-standards → {{TOOLBOX_PATH}}/skills/add-stack-standards.md
- /index-repo       → {{TOOLBOX_PATH}}/skills/index-repo.md

## Memory
- Global memory: {{TOOLBOX_PATH}}/memory/MEMORY.md
- Project memory: .claude/memory/MEMORY.md (when present)

## Code Navigation

When you need to find files, understand code structure, or answer questions about the codebase:

1. If `.claude/index/` exists in the current project, **use it before Grep or Glob**:
   - Read `{{TOOLBOX_PATH}}/skills/query-index.md`, then launch a **sub-agent** with the specific question
   - The sub-agent reads only the relevant index files and returns precise, synthesized results
   - This is faster than grep and keeps the main context clean
2. Fall back to Grep/Glob only if:
   - `.claude/index/` does not exist — remind the user they can run `/index-repo` to build it
   - The question is about specific string content within a file (not structure or relations)
3. Never re-read files that the index already summarizes — use the index answer and read source only when editing

## Always Apply
- Read project memory before starting any task
- Follow active stack standards
- Write session summary to progress.md when stopping work
- When starting a new project with no context, run /new-project
- When two or more steps have no data dependency between them, run them in parallel using multiple tool calls in a single message
- When using /add-feature: act as orchestrator only — hold file paths and one-line summaries, not content. All reasoning, file reading, and code writing happens inside sub-agents.
