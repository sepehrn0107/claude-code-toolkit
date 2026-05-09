## Session Start (automatic)

> **Sub-agent check:** If `WORKSPACE_MODE:` does not appear anywhere in your context, you are
> running as a sub-agent — skip this entire block. Sub-agents do not receive session-start hook
> output; project context is injected via the project-level `CLAUDE.md` or the orchestrator prompt.
> Proceed directly to your task.

At the start of every session, before responding to the first message, do all of this:

1. Check if `{{VAULT_PATH}}/02-projects/<name>/memory/MEMORY.md` exists in the vault for the current project
2. If yes: read **only the first 3 lines** of each memory file — `project_context.md`, `stack.md`, `architecture.md`, `progress.md`, `lessons.md` — to build a one-line summary per file. Do NOT read full files yet.
   Full memory files are loaded on-demand when you actually need them (e.g., before writing code, during `/implement`, or when answering a question that requires project context).
3. Also read **only the first 5 lines** of `{{VAULT_PATH}}/05-areas/claude-memory/MEMORY.md` to get the global memory index. Load individual global memory files only when needed.
4. Note whether `.claude/index/README.md` exists — if it does, it is available for code navigation
5. Invoke `codex:setup` — store the result as session flag `CODEX_AVAILABLE` (true/false). Do not re-check during the session; use this flag everywhere.
6. Output a single status line (before answering the user's message) in this format:
   `Toolbox: active | Skills: ready | Standards: auto-load on first edit`
   Then, if a project is loaded, append on the same line: ` | Project: <name> | Stack: <stack>`
7. If the session-start hook output includes `WORKSPACE_MODE`:
   - Parse the `SESSION_ID=` field from the `WORKSPACE_MODE:` line. Store it as `CURRENT_SESSION_ID`.
     Construct `SESSION_FILE = /tmp/toolbox-session-<CURRENT_SESSION_ID>.md`.
     All "which project is active" checks within this session use this session file, not the global
     `active-project.md` directly. If `SESSION_ID` was absent from hook output, fall back to the
     global file.
   - If the line starts with `WORKSPACE_MODE:ACTIVE=<name>`: read **first 3 lines** of each memory file in
     `{{VAULT_PATH}}/02-projects/<name>/memory/` (project_context.md, stack.md, architecture.md, progress.md, lessons.md — skip missing).
     Output: `Active project: <name>. Context loaded (summaries). Full context loads on-demand.`
   - If the line starts with `WORKSPACE_MODE:CHOOSE`: the hook has already shown a numbered list.
     Treat the user's FIRST message as their project choice (name or number).
     Resolve number → name using the `Projects:` list in the hook line.
     Then: write the choice to both `{{VAULT_PATH}}/05-areas/claude-memory/active-project.md` AND
     `/tmp/toolbox-session-<CURRENT_SESSION_ID>.md` as `active: <choice>` / `updated: <YYYY-MM-DD>`,
     load that project's memory file summaries (first 3 lines each), and output: `Active project: <choice>. Context loaded (summaries).`
     If the user's first message is not a valid project name/number, re-show the list and wait.
