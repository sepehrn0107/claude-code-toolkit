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

## Memory
- Global memory: {{TOOLBOX_PATH}}/memory/MEMORY.md
- Project memory: .claude/memory/MEMORY.md (when present)

## Always Apply
- Read project memory before starting any task
- Follow active stack standards
- Write session summary to progress.md when stopping work
- When starting a new project with no context, run /new-project
