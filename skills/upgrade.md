# /upgrade — Toolbox Upgrade

Applies pending toolbox updates to an existing installation.

## When to run

Triggered automatically when user says: "upgrade toolbox", "update toolbox", "run upgrade", or "/upgrade"

Always `git pull` the toolbox repo before running this skill.

---

## Steps

### 1. Determine versions

Read the `"version"` field from `{{TOOLBOX_PATH}}/package.json` → `TARGET_VERSION`

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

#### v1.1.0 — Status Line Command

Installs the Claude Code status line command that shows session stats (directory, model, context %, 5h rate limit) in the Claude Code UI.

**Steps:**

1. Copy `{{TOOLBOX_PATH}}/templates/claude-sessions/statusline-command.js`
   → `~/.claude/statusline-command.js`

2. Add `statusLine` to `~/.claude/settings.json`:
   - Read `~/.claude/settings.json` (or start from `{}` if absent)
   - Set `settings["statusLine"] = {"type": "command", "command": "node ~/.claude/statusline-command.js"}`
   - Write back (use Python for JSON operations)

3. Output:
   > Status line command installed.

---

#### v1.2.0 — Claude Sessions Extension

Installs a VS Code extension that lets you browse your local Claude Code session history from the Activity Bar.

**Steps:**

1. Create `~/.vscode/extensions/sepehrn.claude-sessions-0.1.0/` if it does not exist.

2. Copy all files from `{{TOOLBOX_PATH}}/templates/claude-sessions/`
   → `~/.vscode/extensions/sepehrn.claude-sessions-0.1.0/`
   (copy `package.json`, `media/`, and `out/` recursively)

3. Register the extension in `~/.vscode/extensions/extensions.json`:
   - Read the file (or start from `[]` if absent)
   - Skip if an entry with `"relativeLocation": "sepehrn.claude-sessions-0.1.0"` already exists
   - Otherwise append this entry (replace `<HOME_POSIX>` with the user's home in POSIX format):
     ```json
     {
       "identifier": {"id": "sepehrn.claude-sessions"},
       "version": "0.1.0",
       "location": {
         "$mid": 1,
         "path": "<HOME_POSIX>/.vscode/extensions/sepehrn.claude-sessions-0.1.0",
         "scheme": "file"
       },
       "relativeLocation": "sepehrn.claude-sessions-0.1.0",
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
   - Use the same Python path-construction pattern from v1.1.0 for `<HOME_POSIX>`.

4. Output:
   > Claude Sessions extension installed. Restart VS Code to activate — look for the chat icon in the Activity Bar.

---

#### v1.3.0 — Stop Hook (Retrospective Nudge)

Installs the stop hook that prompts the user to run `/retrospective` when `lessons.md` was updated during a session.

**Steps:**

1. Copy `{{TOOLBOX_PATH}}/templates/hooks/stop-hook.sh`
   → `~/.claude/stop-hook-git-check.sh`
   Then run: `chmod +x ~/.claude/stop-hook-git-check.sh`

2. Add the `Stop` hook to `~/.claude/settings.json`:
   - Read `~/.claude/settings.json` (or start from `{}` if absent)
   - If `settings["hooks"]["Stop"]` does not already contain an entry with command `~/.claude/stop-hook-git-check.sh`, append:
     ```json
     {
       "hooks": [
         {
           "type": "command",
           "command": "~/.claude/stop-hook-git-check.sh"
         }
       ]
     }
     ```
   - Write back using Python for JSON safety.

3. Output:
   > Stop hook installed. You'll be nudged to run /retrospective when lessons.md is updated during a session.

---

#### v1.4.0 — Enforce web-fetch skill as blocking requirement

Patches `~/.claude/CLAUDE.md` to replace the soft web-fetch routing rule with an explicit blocking requirement that prevents direct `WebFetch` tool calls.

**Steps:**

1. Read `~/.claude/CLAUDE.md` into memory.

2. Replace the old routing row (if present):
   ```
   | Claude is about to use `WebFetch` or follow a URL to read page content  | Read and follow `/web-fetch` skill    |
   ```
   with:
   ```
   | Claude is about to use `WebFetch` or follow a URL to read page content  | **BLOCKING REQUIREMENT**: Read and follow `/web-fetch` skill BEFORE calling `WebFetch`. Never call the `WebFetch` tool directly — always route through `/web-fetch` first. |
   ```
   Use Python string replacement — match the exact old string, write the file back only if a replacement was made.

3. If no match was found (user has a newer install or already patched), skip silently.

4. Output:
   > web-fetch skill enforced as blocking requirement in ~/.claude/CLAUDE.md.

---

### 3. Write updated version

Write `TARGET_VERSION` (plain text, one line) to `~/.claude/toolbox-version.txt`

Output:
> Toolbox upgraded to v`TARGET_VERSION`. ✓

---

## Adding a new version (for toolbox maintainers)

When releasing a new version, bump the `"version"` field in `package.json` (the single source of truth).
Then add a new `#### vX.Y.Z — <Title>` migration block above the "Write updated version" step.