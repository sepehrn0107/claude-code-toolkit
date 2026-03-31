# /upgrade — Toolbox Upgrade

Applies pending toolbox updates to an existing installation.

## When to run

Triggered automatically when user says: "upgrade toolbox", "update toolbox", "run upgrade", or "/upgrade"

Always `git pull` the toolbox repo before running this skill.

---

## Steps

### 1. Determine versions

Read `{{TOOLBOX_PATH}}/VERSION` → `TARGET_VERSION`

Read `~/.claude/toolbox-version.txt` → `INSTALLED_VERSION`
- If the file does not exist, treat `INSTALLED_VERSION` as `0.0.0` (pre-versioning install)

Compare: if `INSTALLED_VERSION == TARGET_VERSION`, output:
> Already at v`TARGET_VERSION` — nothing to do.

...and stop.

Otherwise output:
> Upgrading toolbox: v`INSTALLED_VERSION` → v`TARGET_VERSION`

---

### 2. Apply migrations in order

Run each migration block whose version is **greater than** `INSTALLED_VERSION`.

---

#### v1.0.0 — Baseline

No migration steps. This is the retroactive baseline for all installs before versioning was introduced.

---

#### v1.1.0 — VS Code Status Bar

Installs a VS Code extension that shows Claude Code session stats (directory, model, context %, 5h rate limit) in the VS Code status bar, polled every 2 seconds from a cache file written by Claude Code's status line command.

**Steps:**

1. Create `~/.vscode/extensions/claude-statusbar-0.0.1/` if it does not exist.

2. Copy `{{TOOLBOX_PATH}}/templates/vscode-statusbar/extension.js`
   → `~/.vscode/extensions/claude-statusbar-0.0.1/extension.js`

3. Copy `{{TOOLBOX_PATH}}/templates/vscode-statusbar/package.json`
   → `~/.vscode/extensions/claude-statusbar-0.0.1/package.json`

4. Copy `{{TOOLBOX_PATH}}/templates/statusline-command.sh`
   → `~/.claude/statusline-command.sh`
   Then run: `chmod +x ~/.claude/statusline-command.sh`

5. Add `statusLine` to `~/.claude/settings.json`:
   - Read `~/.claude/settings.json` (or start from `{}` if absent)
   - Set `settings["statusLine"] = {"type": "command", "command": "bash ~/.claude/statusline-command.sh"}`
   - Write back (use Python for JSON operations)

6. Register the extension in `~/.vscode/extensions/extensions.json`:
   - Read the file (or start from `[]` if absent)
   - Skip if an entry with `"relativeLocation": "claude-statusbar-0.0.1"` already exists
   - Otherwise append this entry (replace `<HOME_POSIX>` with the user's home in POSIX format, e.g. `/c:/Users/alice` on Windows, `/home/alice` on Linux/Mac):
     ```json
     {
       "identifier": {"id": "local.claude-statusbar"},
       "version": "0.0.1",
       "location": {
         "$mid": 1,
         "path": "<HOME_POSIX>/.vscode/extensions/claude-statusbar-0.0.1",
         "scheme": "file"
       },
       "relativeLocation": "claude-statusbar-0.0.1",
       "metadata": {
         "isApplicationScoped": false,
         "isMachineScoped": false,
         "isBuiltin": false,
         "installedTimestamp": <current_unix_ms>,
         "pinned": false,
         "source": "gallery"
       }
     }
     ```
   - Use Python to detect home, construct the POSIX path, and write back the JSON.
   - Sample Python snippet for path construction:
     ```python
     import pathlib
     home = pathlib.Path.home()
     # On Windows: home = WindowsPath('C:/Users/alice')
     # POSIX form for VS Code: /c:/Users/alice
     parts = home.as_posix()  # gives 'C:/Users/alice' on Windows
     if len(parts) >= 2 and parts[1] == ':':
         posix_path = '/' + parts[0].lower() + parts[2:]  # -> /c:/Users/alice
     else:
         posix_path = parts  # already POSIX on Linux/Mac
     ext_path = posix_path + '/.vscode/extensions/claude-statusbar-0.0.1'
     ```

7. Output:
   > VS Code status bar installed. Restart VS Code to activate.

---

### 3. Write updated version

Write `TARGET_VERSION` (plain text, one line) to `~/.claude/toolbox-version.txt`

Output:
> Toolbox upgraded to v`TARGET_VERSION`. ✓