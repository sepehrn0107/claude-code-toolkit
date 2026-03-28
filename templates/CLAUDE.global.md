# Toolbox

Standards, memory, and lifecycle skills for all projects.
Source: https://github.com/sepehrn0107/toolbox (local clone: {{TOOLBOX_PATH}})

## Standards

Before writing or editing any code, invoke `{{TOOLBOX_PATH}}/skills/load-standards.md`.
This is a blocking requirement — wait for the confirmation line before proceeding.

The skill reads all universal standards and any stack-specific standards for the project.
Do not read them manually or skip this step.

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
