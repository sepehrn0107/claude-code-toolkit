## Session Start (automatic)

> **Sub-agent check:** If `WORKSPACE_MODE:` does not appear anywhere in your context, you are
> running as a sub-agent — skip this entire block. Sub-agents do not receive session-start hook
> output; project context is injected via the project-level `CLAUDE.md` or the orchestrator prompt.
> Proceed directly to your task.

At the start of every session, before responding to the first message, do all of this:

1. Check if `{{VAULT_PATH}}/02-projects/<name>/memory/MEMORY.md` exists in the vault for the current project
2. If yes: read all memory files in parallel — `project_context.md`, `stack.md`, `architecture.md`, `progress.md`, `lessons.md`
3. Also read `{{VAULT_PATH}}/05-areas/claude-memory/MEMORY.md` to load global cross-project learnings, plus any individual memory files listed in its index
4. Note whether `.claude/index/README.md` exists — if it does, it is available for code navigation
5. Invoke `codex:setup` — store the result as session flag `CODEX_AVAILABLE` (true/false). Do not re-check during the session; use this flag everywhere.
6. Output a single status line (before answering the user's message) in this format:
   `Toolbox: active | Skills: ready | Codex: <available if CODEX_AVAILABLE is true, else unavailable> | Standards: auto-load on first edit`
   Then, if a project is loaded, append on the same line: ` | Project: <name> | Stack: <stack>`
7. If the session-start hook output includes `WORKSPACE_MODE`:
   - Parse the `SESSION_ID=` field from the `WORKSPACE_MODE:` line. Store it as `CURRENT_SESSION_ID`.
     Construct `SESSION_FILE = /tmp/toolbox-session-<CURRENT_SESSION_ID>.md`.
     All "which project is active" checks within this session use this session file, not the global
     `active-project.md` directly. If `SESSION_ID` was absent from hook output, fall back to the
     global file.
   - If the line starts with `WORKSPACE_MODE:ACTIVE=<name>`: load
     `{{VAULT_PATH}}/02-projects/<name>/memory/` files in parallel
     (project_context.md, stack.md, architecture.md, progress.md, lessons.md — skip missing).
     Output: `Active project: <name>. Context loaded.`
   - If the line starts with `WORKSPACE_MODE:CHOOSE`: the hook has already shown a numbered list.
     Treat the user's FIRST message as their project choice (name or number).
     Resolve number → name using the `Projects:` list in the hook line.
     Then: write the choice to both `{{VAULT_PATH}}/05-areas/claude-memory/active-project.md` AND
     `/tmp/toolbox-session-<CURRENT_SESSION_ID>.md` as `active: <choice>` / `updated: <YYYY-MM-DD>`,
     load that project's memory files, and output: `Active project: <choice>. Context loaded.`
     If the user's first message is not a valid project name/number, re-show the list and wait.
