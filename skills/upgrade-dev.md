# /upgrade-dev — Apply Template to Live Install

Re-renders all toolbox section templates into `~/.claude/toolbox-sections/`, updates
`~/.claude/CLAUDE.global.md`, and ensures `~/.claude/CLAUDE.md` has the single @import line.

Use this when iterating on templates during toolbox development.
Does **not** bump the version or add an upgrade migration — those are only required when shipping to users.

---

## When to run

Triggered automatically when user says: "upgrade-dev", "/upgrade-dev", "apply template", "sync live install", or "render template"

Always run from within the toolbox repo directory.

---

## Steps

### 1. Resolve paths

`TOOLBOX_PATH` = the absolute path to the toolbox repo root (the directory containing this skill file's parent `skills/` folder).

Derive `WORKSPACE_PATH` = the parent directory of `TOOLBOX_PATH`.

`CLAUDE_PATH` = the user's `~/.claude` directory (e.g. `C:/Users/<name>/.claude` on Windows, `/home/<name>/.claude` on Linux/Mac). Derive from `HOME` env var or equivalent.

If any paths are already known from the current session context (e.g. from `CLAUDE.md`), use those directly.

### 2. Render section files

For each of the 9 section templates in `<TOOLBOX_PATH>/templates/sections/`:

- `session-start.md`
- `skill-routing.md`
- `standards.md`
- `before-pr.md`
- `lifecycle-skills.md`
- `memory.md`
- `code-navigation.md`
- `codex-integration.md`
- `always-apply.md`

Do for each:
1. Read the template file
2. Replace every occurrence of `{{TOOLBOX_PATH}}`, `{{WORKSPACE_PATH}}`, and `{{CLAUDE_PATH}}` with their resolved values
3. **Before writing any file**, ensure the directory exists:
   ```bash
   mkdir -p <CLAUDE_PATH>/toolbox-sections
   ```
   This is required on first run — the directory does not exist by default.
4. Write the rendered content to `<CLAUDE_PATH>/toolbox-sections/<filename>.md`

### 3. Render CLAUDE.global.md

1. Read `<TOOLBOX_PATH>/templates/CLAUDE.global.md`
2. Replace every occurrence of `{{TOOLBOX_PATH}}`, `{{WORKSPACE_PATH}}`, and `{{CLAUDE_PATH}}`
3. Write the rendered content to `<CLAUDE_PATH>/CLAUDE.global.md`

### 4. Ensure CLAUDE.md has the @import line

The expected @import line is:
```
@<CLAUDE_PATH>/CLAUDE.global.md
```

- If `<CLAUDE_PATH>/CLAUDE.md` does not exist: create it with just that line
- If it exists and already contains the @import line: do nothing
- If it exists but does **not** contain the @import line: **prepend** the line followed by a blank line — do not overwrite any existing content

### 5. Output

> Live install updated. Section files written to `~/.claude/toolbox-sections/`.
> To ship this change to other users: add a migration in `skills/upgrade.md` and bump `"version"` in `package.json`.

---

## Notes

- `~/.claude/CLAUDE.md` is **user-owned** — only the @import line is managed by the toolbox. Never overwrite content beyond prepending the @import.
- `~/.claude/CLAUDE.global.md` and `~/.claude/toolbox-sections/` are **toolbox-managed** — always safe to overwrite.
- The templates in `templates/sections/` are the single source of truth. Never edit rendered files directly.
