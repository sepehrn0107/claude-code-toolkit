# /upgrade-dev — Apply Template to Live Install

Re-renders `templates/CLAUDE.global.md` into `~/.claude/CLAUDE.md` immediately.

Use this when iterating on `templates/CLAUDE.global.md` during toolbox development.
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

If the paths are already known from the current session context (e.g. from `CLAUDE.md`), use those directly.
Otherwise, read `~/.claude/CLAUDE.md` and extract the resolved path from any line like:
```
- /new-project      → <TOOLBOX_PATH>/skills/new-project.md
```

### 2. Render template

Read `<TOOLBOX_PATH>/templates/CLAUDE.global.md`.

Replace every occurrence of:
- `{{TOOLBOX_PATH}}` → the resolved toolbox path
- `{{WORKSPACE_PATH}}` → the resolved workspace path

### 3. Write live install

Write the rendered content to `~/.claude/CLAUDE.md`.

### 4. Output

> Live install updated from template (no version bump).
> To ship this change to other users: add a migration in `skills/upgrade.md` and bump `"version"` in `package.json`.

---

## Notes

- This skill is the **only sanctioned way** to update `~/.claude/CLAUDE.md` when working in the toolbox repo.
- Never edit `~/.claude/CLAUDE.md` directly — it is a generated file and will be overwritten.
- The template `templates/CLAUDE.global.md` is the single source of truth.
