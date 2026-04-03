---
name: set-vault
description: Update the vault path used for all memory, plans, and specs. Re-renders CLAUDE.md and CLAUDE.global.md with the new path. Run this when you move your vault or want to point the toolbox to a different location. Does NOT move existing files — user is responsible for migrating content.
---

# /set-vault

Update the vault path and re-render all toolbox config files.

## When to Use

Run when you want to change the vault path already configured during `/upgrade-dev`.

Trigger phrases: "set vault", "change vault path", "update vault path", "/set-vault"

---

## Steps

### 1. Show current vault path

Read `{{TOOLBOX_PATH}}/templates/sections/vault-paths.md` to extract the current rendered path, or
read `~/.claude/toolbox-sections/vault-paths.md` to see the currently active rendered value.

Output: `Current vault path: <path>`

### 2. Prompt for new path

Ask the user:
> "Enter your new vault path (absolute path, forward slashes):"

Wait for their input. Do not proceed without a value.

### 3. Re-render all toolbox sections

Follow the same render steps as `/upgrade-dev` Step 2 and Step 3, but substitute the new vault
path for `{{VAULT_PATH}}`. Keep `{{TOOLBOX_PATH}}`, `{{WORKSPACE_PATH}}`, and `{{CLAUDE_PATH}}`
as their currently rendered values (read them from `~/.claude/CLAUDE.global.md`).

Re-render:
- All 10 section files in `~/.claude/toolbox-sections/` (including the new `vault-paths.md`)
- `~/.claude/CLAUDE.global.md`

### 4. Confirm

Output:
```
Vault path updated to: <new-path>
Note: existing files at the old path have NOT been moved.
Run your file manager or shell to move content if needed.
```

---

## Notes

- This skill does not validate that the new path exists — the user may be setting up a new vault
- This skill does not modify any files inside the vault itself
- To move existing memory/plans/specs, use your shell or file manager after running this skill
