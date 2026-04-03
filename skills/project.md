---
name: project
description: Workspace-level project context switcher for managing which repo is active across sessions. Use this when the user says "switch project", "change project", "work on [repo]", "what project am I on?", or wants to see available projects. Supports /project switch (change active project and load its memory), /project list (show all repos), and /project status (show active project summary). The active choice persists so future sessions auto-load the right context.
---

# /project

Workspace-level project context switcher. Use when Claude Code is open at the workspace root
(`{{WORKSPACE_PATH}}/`) and you need to load, inspect, or change the active project context.

Active project is persisted at `{{VAULT_PATH}}/05-areas/claude-memory/active-project.md` (global, shared across
sessions) and at `/tmp/toolbox-session-${CLAUDE_SESSION_ID}.md` (session-local, this window only).
The session file takes precedence within a session; the global file seeds new sessions.

---

## /project switch

Switch which repo is the active project for this and future sessions.

**Steps:**
1. Scan `{{WORKSPACE_PATH}}/` for git repos:
   ```bash
   for d in {{WORKSPACE_PATH}}/*/; do
     [ -d "${d}.git" ] && [ "$(basename $d)" != "toolbox" ] && echo "$(basename $d)"
   done
   ```
2. Read current active from `{{VAULT_PATH}}/05-areas/claude-memory/active-project.md` (field `active:`)
3. Show the list to the user and ask which to switch to (mark current active)
4. Write the choice to both files:
   a. Global file `{{VAULT_PATH}}/05-areas/claude-memory/active-project.md`:
      ```
      active: <chosen-repo>
      updated: <YYYY-MM-DD>
      ```
   b. Session file (if `CLAUDE_SESSION_ID` is available — run via Bash):
      ```bash
      SESSION_KEY="${CLAUDE_SESSION_ID:-}"
      TODAY=$(date +%Y-%m-%d)
      [ -n "$SESSION_KEY" ] && printf "active: <chosen-repo>\nupdated: %s\n" "$TODAY" > "/tmp/toolbox-session-${SESSION_KEY}.md"
      ```
5. Load the new project's memory files in parallel (if they exist):
   - `{{VAULT_PATH}}/02-projects/<chosen>/memory/project_context.md`
   - `{{VAULT_PATH}}/02-projects/<chosen>/memory/stack.md`
   - `{{VAULT_PATH}}/02-projects/<chosen>/memory/architecture.md`
   - `{{VAULT_PATH}}/02-projects/<chosen>/memory/progress.md`
   - `{{VAULT_PATH}}/02-projects/<chosen>/memory/lessons.md`
6. Announce: "Switched to `<chosen>`. Context loaded. Future sessions will auto-load this project."

---

## /project list

Show all available repos and which is currently active.

**Steps:**
1. Scan `{{WORKSPACE_PATH}}/` for git repos (same as switch step 1)
2. Read `{{VAULT_PATH}}/05-areas/claude-memory/active-project.md` for current active
3. Output a formatted list:
   ```
   Projects in workspace:
     * gymbro   ← active
       vault
   ```

---

## /project status

Show the active project and a brief context summary.

**Steps:**
1. Read `{{VAULT_PATH}}/05-areas/claude-memory/active-project.md`
2. If no active project: output "No active project. Run /project switch to choose one."
3. If active project set:
   - Read `{{VAULT_PATH}}/02-projects/<active>/memory/progress.md` (current phase + next)
   - Read `{{VAULT_PATH}}/02-projects/<active>/memory/stack.md` (primary stack line only)
   - Output:
     ```
     Active project: <name>
     Stack: <primary>
     Phase: <current phase>
     Next: <next item>
     ```
