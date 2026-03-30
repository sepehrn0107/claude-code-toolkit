# Toolbox

Development standards, memory, and lifecycle skills for all projects.
Source: https://github.com/sepehrn0107/claude-code-toolkit

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

- /new-project      → `skills/new-project.md`
- /implement      → `skills/implement.md`
- /standards-check  → `skills/standards-check.md`
- /retrospective    → `skills/retrospective.md`
- /add-stack-standards → `skills/add-stack-standards.md`
- /index-repo       → `skills/index-repo.md`

## Memory

- Global memory (Layer 1): `../memory/MEMORY.md` (lives in the workspace root, outside this repo)
- Project memory (Layer 3): `.claude/memory/MEMORY.md` (when present in a project)

## Setup Skill

When the user says "set up the toolbox":
1. `TOOLBOX_PATH` is the absolute path to the directory containing **this CLAUDE.md file** — not the shell's current working directory, not the workspace root. Resolve it by finding where this file lives (e.g. if this file is at `/home/alice/workspace/toolbox/CLAUDE.md`, then `TOOLBOX_PATH = /home/alice/workspace/toolbox`).
2. `WORKSPACE_PATH` is the **parent directory** of `TOOLBOX_PATH` (e.g. `/home/alice/workspace`).
3. Read `templates/CLAUDE.global.md`
4. Replace every `{{TOOLBOX_PATH}}` with the detected path and every `{{WORKSPACE_PATH}}` with the detected workspace path
5. Write the result to `~/.claude/CLAUDE.md`
6. Create `~/.claude/hooks/` if it does not exist
7. Copy `templates/hooks/session-start.sh` to `~/.claude/hooks/session-start.sh`
8. Copy `templates/hooks/pre-tool-standards-gate.sh` to `~/.claude/hooks/pre-tool-standards-gate.sh`
9. Run `chmod +x ~/.claude/hooks/session-start.sh ~/.claude/hooks/pre-tool-standards-gate.sh`
10. Read `~/.claude/settings.json` (or start from `{}` if absent), merge in the `hooks` block from `templates/workspace-settings.json`, and write it back
11. Write `templates/workspace-settings.json` to `{{WORKSPACE_PATH}}/.claude/settings.json` (create `{{WORKSPACE_PATH}}/.claude/` if it does not exist)
12. Create `{{WORKSPACE_PATH}}/memory/` if it does not exist, and write `templates/memory/MEMORY.md` to `{{WORKSPACE_PATH}}/memory/MEMORY.md`
13. Confirm: "Toolbox installed. TOOLBOX_PATH = <path>, WORKSPACE_PATH = <path>"

## When Creating or Modifying a Skill

Whenever a new skill file is added to `skills/` or an existing one is changed in a way that affects routing or the lifecycle skills list, **also update `templates/CLAUDE.global.md`**:

1. If the skill has an auto-trigger condition → add a row to the `## Automatic Skill Routing` table
2. If it is a named lifecycle skill → add an entry under `## Lifecycle Skills`
3. Keep both sections in sync with `~/.claude/CLAUDE.md` (the installed version)

This ensures the template stays canonical so that a fresh `"set up the toolbox"` produces a correct install.

## Always Apply

- **Before touching any file**: checkout a new branch. Never commit to master directly.
- All changes go through GitHub PRs — never push to master directly
- Never write back to this repo directly from project sessions — use PRs
- When starting a new project with no context, run /new-project
- When working in this repo, run /standards-check before committing
