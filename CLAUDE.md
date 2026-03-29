# Toolbox

Development standards, memory, and lifecycle skills for all projects.
Source: https://github.com/sepehrn0107/toolbox

## Setup

When someone clones this repo, they need to install it once so Claude Code uses it in every project:

1. Open the toolbox directory in Claude Code
2. Tell Claude: **"Set up the toolbox"**

Claude will detect the current directory, substitute the correct path into `templates/CLAUDE.global.md`, and write it to `~/.claude/CLAUDE.md`. That's the only manual step.

## What This Is

When working in this repo, you are maintaining the standards, skills, and templates
that power all other projects. All changes go through GitHub PRs — nothing is written
back directly from project sessions.

## Standards

- Universal: `standards/universal/`
- Stack-specific: `standards/stacks/`

## Lifecycle Skills

Read each skill file before following it. The `{{TOOLBOX_PATH}}` placeholder in skill
files resolves to the actual toolbox path defined in `~/.claude/CLAUDE.md`.

- /work-ticket      → `skills/work-ticket.md`
- /new-project      → `skills/new-project.md`
- /add-feature      → `skills/add-feature.md`
- /standards-check  → `skills/standards-check.md`
- /retrospective    → `skills/retrospective.md`
- /add-stack-standards → `skills/add-stack-standards.md`
- /index-repo       → `skills/index-repo.md`

## Memory

- Global memory (Layer 1): `memory/MEMORY.md`
- Project memory (Layer 3): `.claude/memory/MEMORY.md` (when present in a project)

## Setup Skill

When the user says "set up the toolbox":
1. Detect the current working directory — this is `TOOLBOX_PATH`
2. Read `templates/CLAUDE.global.md`
3. Replace every `{{TOOLBOX_PATH}}` with the detected path
4. Write the result to `~/.claude/CLAUDE.md`
5. Create `~/.claude/hooks/` if it does not exist
6. Copy `templates/hooks/session-start.sh` to `~/.claude/hooks/session-start.sh`
7. Copy `templates/hooks/pre-tool-standards-gate.sh` to `~/.claude/hooks/pre-tool-standards-gate.sh`
8. Run `chmod +x ~/.claude/hooks/session-start.sh ~/.claude/hooks/pre-tool-standards-gate.sh`
9. Read `~/.claude/settings.json` (or start from `{}` if absent), merge in the `hooks` block from `.claude/settings.json`, and write it back
10. Confirm: "Toolbox installed. TOOLBOX_PATH = <path>"

## Always Apply

- **Before touching any file**: checkout a new branch. Never commit to master directly.
- All changes go through GitHub PRs — never push to master directly
- Never write back to this repo directly from project sessions — use PRs
- When starting a new project with no context, run /new-project
- When working in this repo, run /standards-check before committing
