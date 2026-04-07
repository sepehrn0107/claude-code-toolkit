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


### 0. Dependency pre-check

Verify required tools are present before attempting any path resolution or rendering:

```bash
MISSING_DEPS=""
for dep in jq bash python3; do
  command -v "$dep" >/dev/null 2>&1 || MISSING_DEPS="${MISSING_DEPS} ${dep}"
done
if [ -n "$MISSING_DEPS" ]; then
  echo "[upgrade-dev] ERROR: missing dependencies:${MISSING_DEPS}"
  echo "Install the missing tools (e.g. 'brew install jq', 'apt install jq', 'choco install jq') then re-run /upgrade-dev."
  exit 1
fi
```

If any dependency is missing: stop and print the install hint. Do not proceed.

### 1. Resolve paths

`TOOLBOX_PATH` = the absolute path to the toolbox repo root (the directory containing this skill file's parent `skills/` folder).

Derive `WORKSPACE_PATH` = the parent directory of `TOOLBOX_PATH`.

`CLAUDE_PATH` = the user's `~/.claude` directory (e.g. `C:/Users/<name>/.claude` on Windows, `/home/<name>/.claude` on Linux/Mac). Derive from `HOME` env var or equivalent.

If any paths are already known from the current session context (e.g. from `CLAUDE.md`), use those directly.

`VAULT_PATH` = the user's vault directory. Derive as follows:
- If `VAULT_PATH` is already known from the current session context (e.g. from a rendered `vault-paths.md` section in CLAUDE.md), use that value directly.
- Otherwise, prompt the user: "Enter your vault path (absolute path, forward slashes):"
- Wait for their input before proceeding.

### 2. Render section files

For each of the 10 section templates in `<TOOLBOX_PATH>/templates/sections/`:

- `session-start.md`
- `skill-routing.md`
- `standards.md`
- `before-pr.md`
- `lifecycle-skills.md`
- `memory.md`
- `code-navigation.md`
- `codex-integration.md`
- `always-apply.md`
- `vault-paths.md`

Do for each:
1. Read the template file
2. Replace every occurrence of `{{TOOLBOX_PATH}}`, `{{WORKSPACE_PATH}}`, `{{CLAUDE_PATH}}`, and `{{VAULT_PATH}}` with their resolved values
3. **Before writing any file**, ensure the directory exists:
   ```bash
   mkdir -p <CLAUDE_PATH>/toolbox-sections
   ```
   This is required on first run — the directory does not exist by default.
4. Write the rendered content to `<CLAUDE_PATH>/toolbox-sections/<filename>.md`

### 2b. Validate rendered section files — no unresolved tokens

After writing all section files, scan each rendered file for any remaining `{{` tokens.
These indicate a substitution was skipped (e.g. vault path was empty or a new token was added
to the template but not wired up in the render step):

```python
import pathlib, re, sys

sections_dir = pathlib.Path.home() / ".claude" / "toolbox-sections"
broken = []

for md_file in sorted(sections_dir.glob("*.md")):
    content = md_file.read_text(encoding="utf-8")
    if "{{" in content:
        tokens = list(set(re.findall(r"\{\{[^}]+\}\}", content)))
        broken.append((md_file.name, tokens))

if broken:
    print("[upgrade-dev] ERROR: Unresolved template tokens in rendered section files:")
    for filename, tokens in broken:
        print(f"  {filename}: {', '.join(tokens)}")
    print("Re-run /upgrade-dev and supply all required path values.")
    sys.exit(1)
else:
    print("[upgrade-dev] Token validation passed — all placeholders resolved.")
```

If validation fails (exit 1): stop and report the affected files. Do not proceed to Step 3.

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

### 4b. Validate rendered skill paths

After writing all section files, parse the rendered `lifecycle-skills.md` and verify every
referenced skill path exists on disk:

```python
import pathlib, re, sys

claude_path = pathlib.Path.home() / ".claude"
lifecycle_file = claude_path / "toolbox-sections" / "lifecycle-skills.md"
content = lifecycle_file.read_text(encoding="utf-8")
pattern = re.compile(r"→\s+(.+\.md)")
missing = []

for line in content.splitlines():
    m = pattern.search(line)
    if m:
        skill_path = pathlib.Path(m.group(1).strip())
        if not skill_path.exists():
            missing.append(str(skill_path))

if missing:
    print("[upgrade-dev] WARNING: Ghost skill paths in lifecycle-skills.md:")
    for p in missing:
        print(f"  MISSING: {p}")
    sys.exit(1)
else:
    print("[upgrade-dev] All skill paths validated — no ghost entries found.")
```

If validation fails (exit 1): stop and report. Do not leave a broken `lifecycle-skills.md` installed.

### 5. Scaffold vault structure (first-time only)

If `<VAULT_PATH>/05-areas/claude-memory/` does not exist:
```bash
mkdir -p "<VAULT_PATH>/05-areas/claude-memory"
```
Copy starter files from `<TOOLBOX_PATH>/templates/memory/global/` into `<VAULT_PATH>/05-areas/claude-memory/`:
- `MEMORY.md`
- `active-project.md`

If the files already exist, skip silently — do not overwrite.

If `<WORKSPACE_PATH>/memory/` exists and contains `.md` files (migration case), print:
```
[upgrade-dev] Found existing global memory at <WORKSPACE_PATH>/memory/.
To migrate to vault, run:
  cp <WORKSPACE_PATH>/memory/*.md <VAULT_PATH>/05-areas/claude-memory/
Then verify the vault files look correct before deleting the originals.
```
Do NOT automatically delete or overwrite the old `workspace/memory/` — the user migrates manually.

### 6. Output

> Live install updated. Section files written to `~/.claude/toolbox-sections/`.
> Vault path set to: `<VAULT_PATH>`
> To ship this change to other users: add a migration in `skills/upgrade.md` and bump `"version"` in `package.json`.

---

## Notes

- `~/.claude/CLAUDE.md` is **user-owned** — only the @import line is managed by the toolbox. Never overwrite content beyond prepending the @import.
- `~/.claude/CLAUDE.global.md` and `~/.claude/toolbox-sections/` are **toolbox-managed** — always safe to overwrite.
- The templates in `templates/sections/` are the single source of truth. Never edit rendered files directly.
