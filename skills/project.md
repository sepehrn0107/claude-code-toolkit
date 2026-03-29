# /project

Workspace-level project context switcher. Use when Claude Code is open at the workspace root
(`{{WORKSPACE_PATH}}/`) and you need to load, inspect, or change the active project context.

Active project is persisted at `{{WORKSPACE_PATH}}/memory/active-project.md` and is shared across
all sessions — switching in one chat means the next chat auto-loads the new choice.

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
2. Read current active from `{{WORKSPACE_PATH}}/memory/active-project.md` (field `active:`)
3. Show the list to the user and ask which to switch to (mark current active)
4. Write the choice:
   ```
   active: <chosen-repo>
   updated: <YYYY-MM-DD>
   ```
   to `{{WORKSPACE_PATH}}/memory/active-project.md`
5. Load the new project's memory files in parallel (if they exist):
   - `{{WORKSPACE_PATH}}/<chosen>/.claude/memory/project_context.md`
   - `{{WORKSPACE_PATH}}/<chosen>/.claude/memory/stack.md`
   - `{{WORKSPACE_PATH}}/<chosen>/.claude/memory/architecture.md`
   - `{{WORKSPACE_PATH}}/<chosen>/.claude/memory/progress.md`
   - `{{WORKSPACE_PATH}}/<chosen>/.claude/memory/lessons.md`
6. Announce: "Switched to `<chosen>`. Context loaded. Future sessions will auto-load this project."

---

## /project list

Show all available repos and which is currently active.

**Steps:**
1. Scan `{{WORKSPACE_PATH}}/` for git repos (same as switch step 1)
2. Read `{{WORKSPACE_PATH}}/memory/active-project.md` for current active
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
1. Read `{{WORKSPACE_PATH}}/memory/active-project.md`
2. If no active project: output "No active project. Run /project switch to choose one."
3. If active project set:
   - Read `{{WORKSPACE_PATH}}/<active>/.claude/memory/progress.md` (current phase + next)
   - Read `{{WORKSPACE_PATH}}/<active>/.claude/memory/stack.md` (primary stack line only)
   - Output:
     ```
     Active project: <name>
     Stack: <primary>
     Phase: <current phase>
     Next: <next item>
     ```
