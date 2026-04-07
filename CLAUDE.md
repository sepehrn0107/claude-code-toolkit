# Toolbox

Development standards, memory, and lifecycle skills for all projects.
Source: https://github.com/sepehrn0107/claude-code-toolkit

## Setup

The toolbox must live inside a **dedicated workspace folder**. That folder should be empty at first — other project repos are added alongside `toolbox/` later. The folder name does not matter; setup infers `WORKSPACE_PATH` from the parent of wherever this repo is cloned.

Once the repo is cloned into the workspace folder, install it so Claude Code uses it in every project:

1. Open the toolbox directory in Claude Code
2. Tell Claude: **"Set up the toolbox"**

Claude will detect the current directory, substitute the correct path into `templates/CLAUDE.global.md`, and write it to `~/.claude/CLAUDE.md`. That's the only manual step — no re-cloning or path configuration needed.

## What This Is

When working in this repo, you are maintaining the standards, skills, and templates
that power all other projects. All changes go through GitHub PRs — nothing is written
back directly from project sessions.

## Development Workflow

### RULE: Never edit `~/.claude/CLAUDE.md` directly

`~/.claude/CLAUDE.md` is a **generated file** — produced by rendering `templates/CLAUDE.global.md` with resolved path tokens. **Direct edits are forbidden** because they will be silently overwritten the next time `/upgrade` or `/upgrade-dev` runs.

- All changes must be made in `templates/CLAUDE.global.md`
- To sync the live install immediately (during development), run `/upgrade-dev`
- To ship to other users, also add a migration in `skills/upgrade.md` and bump `"version"` in `package.json`

### For ANY change that affects installed behavior (routing, session start, skill routing table, etc.)

Three steps — all required, in order:

1. Edit `templates/CLAUDE.global.md` — this is the source of truth (the only file you touch)
2. Run `/upgrade-dev` to re-render the template into `~/.claude/CLAUDE.md` — never edit that file by hand
3. Add a migration in `skills/upgrade.md` + bump `"version"` in `package.json` — so existing users receive the change

### Upgrade migration pattern

- Add a new `#### vX.Y.Z — <Title>` block **above** the `### 3. Write updated version` line in `skills/upgrade.md`
- Use Python string replacement for `.md` file patches, Python JSON ops for `settings.json` patches
- Skip silently if the target pattern is not found (already patched or newer install)
- Bump `"version"` in `package.json` to match the new migration version

### Branch & PR

- Default branch is `master` — PRs target `master`
- Never commit directly to `master`
- Commits follow Conventional Commits: `feat`, `fix`, `chore`, `docs`, `refactor`

## Standards

- Universal: `standards/universal/`
- Stack-specific: `standards/stacks/`

## Lifecycle Skills

Read each skill file before following it. The `{{TOOLBOX_PATH}}` placeholder in skill
files resolves to the actual toolbox path defined in `~/.claude/CLAUDE.md`.

- /new-project → `skills/new-project.md`
- /implement → `skills/implement.md`
- /standards-check → `skills/standards-check.md`
- /retrospective → `skills/retrospective.md`
- /add-stack-standards → `skills/add-stack-standards.md`
- /index-repo → `skills/index-repo.md`
- /upgrade → `skills/upgrade.md`

## Memory

- Global memory (Layer 1): `../memory/MEMORY.md` (lives in the workspace root, outside this repo)
- Project memory (Layer 3): `.claude/memory/MEMORY.md` (when present in a project)

## Prerequisites

- Claude Code installed
- Git
- Python 3
- Docker (for `/web-fetch` and `/local-llm`)
- [codex-plugin-cc](https://github.com/openai/codex-plugin-cc) — optional; enables Codex delegation in `/implement` Phase 3. If not installed, all tasks fall back to direct Claude implementation.

## Setup Skill

When the user opens the toolbox directory in Claude Code and says "set up the toolbox":

1. `TOOLBOX_PATH` is the absolute path to the directory containing **this CLAUDE.md file** — not the shell's current working directory, not the workspace root. Resolve it by finding where this file lives (e.g. if this file is at `/home/alice/workspace/toolbox/CLAUDE.md`, then `TOOLBOX_PATH = /home/alice/workspace/toolbox`).
2. `WORKSPACE_PATH` is the **parent directory** of `TOOLBOX_PATH` (e.g. `/home/alice/workspace`). The workspace folder name is inferred from this path — it is never hardcoded and can be anything the user chose when creating the folder.
2a. Warn (but do not abort) if `WORKSPACE_PATH` looks like a home directory (`~`, `/home/<user>`, `C:\Users\<user>`) or a system path — the toolbox should be one level inside a dedicated workspace folder, not cloned directly into the home directory.
3. Read `templates/CLAUDE.global.md`
4. Replace every `{{TOOLBOX_PATH}}` with the detected path and every `{{WORKSPACE_PATH}}` with the detected workspace path
5. Write the result to `~/.claude/CLAUDE.md`
6. Create `~/.claude/hooks/` if it does not exist
7. Copy `templates/hooks/session-start.sh` to `~/.claude/hooks/session-start.sh`
7a. Verify that `.toolbox-marker` exists in `TOOLBOX_PATH`. If missing, create it with the standard content (see `.toolbox-marker` in the repo root). This file allows the session-start hook to identify the toolbox directory by marker rather than by name.
8. Copy `templates/hooks/pre-tool-standards-gate.sh` to `~/.claude/hooks/pre-tool-standards-gate.sh`
9. Run `chmod +x ~/.claude/hooks/session-start.sh ~/.claude/hooks/pre-tool-standards-gate.sh`
10. Read `~/.claude/settings.json` (or start from `{}` if absent), merge in the `hooks` block from `templates/workspace-settings.json`, and write it back
11. Write `templates/workspace-settings.json` to `{{WORKSPACE_PATH}}/.claude/settings.json` (create `{{WORKSPACE_PATH}}/.claude/` if it does not exist)
12. Create `{{WORKSPACE_PATH}}/memory/` if it does not exist, and write `templates/memory/MEMORY.md` to `{{WORKSPACE_PATH}}/memory/MEMORY.md`
13. Read `templates/workspace-CLAUDE.md`, replace every `{{TOOLBOX_PATH}}` and `{{WORKSPACE_PATH}}`, and write the result to `{{WORKSPACE_PATH}}/CLAUDE.md` — this file is auto-loaded by Claude Code for every session in the workspace and states the always-on defaults (Crawl4AI for fetches, Codex for delegation).
14. Copy `templates/claude-sessions/statusline-command.js` to `~/.claude/statusline-command.js`
15. In `~/.claude/settings.json`, also merge `"statusLine": {"type": "command", "command": "node ~/.claude/statusline-command.js"}` (alongside the hooks block from step 10)
16. Read the `"version"` field from `{{TOOLBOX_PATH}}/package.json` and write it (plain text, one line) to `~/.claude/toolbox-version.txt`
17. Ask for vault path:
   > "Enter your vault path (absolute path, forward slashes). Press Enter to use the default: `<WORKSPACE_PATH>/vault/`"
   - Non-empty input → use as `VAULT_PATH`
   - Empty/whitespace input → `VAULT_PATH = <WORKSPACE_PATH>/vault/`
   - Normalize: strip trailing slashes. Do not validate existence yet.
18. Render 10 section templates into `~/.claude/toolbox-sections/`:
   - `mkdir -p ~/.claude/toolbox-sections`
   - For each of the 10 files in `templates/sections/`: read, replace `{{TOOLBOX_PATH}}`, `{{WORKSPACE_PATH}}`, `{{CLAUDE_PATH}}`, `{{VAULT_PATH}}`, write to `~/.claude/toolbox-sections/<filename>.md`
   - Read/render/write `templates/CLAUDE.global.md` → `~/.claude/CLAUDE.global.md`
   - Ensure `~/.claude/CLAUDE.md` contains `@<CLAUDE_PATH>/CLAUDE.global.md` (prepend if absent; do not overwrite existing user content)
19. Scaffold vault memory:
   - `mkdir -p "<VAULT_PATH>/05-areas/claude-memory"`
   - Copy `templates/memory/global/MEMORY.md` → `<VAULT_PATH>/05-areas/claude-memory/MEMORY.md` (skip if exists)
   - Copy `templates/memory/global/active-project.md` → `<VAULT_PATH>/05-areas/claude-memory/active-project.md` (skip if exists)
20. Confirm with a summary block:
   ```
   Toolbox installed.
     TOOLBOX_PATH   = <path>
     WORKSPACE_PATH = <path>
     VAULT_PATH     = <path>
   Section files written to ~/.claude/toolbox-sections/.
   Vault memory scaffolded at <VAULT_PATH>/05-areas/claude-memory/.
   You're ready. Open any project folder in Claude Code and start a session.
   ```

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
