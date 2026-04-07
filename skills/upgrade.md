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

#### v1.5.0 — Multi-Session Isolation and Auto-Switch

Installs session-scoped project state (so parallel Claude Code windows don't conflict) and
mid-session project auto-detection (so Claude switches context when you reference another repo).

**Steps:**

1. Copy `{{TOOLBOX_PATH}}/templates/hooks/session-start.sh`
   → `~/.claude/hooks/session-start.sh`
   Then run: `chmod +x ~/.claude/hooks/session-start.sh`

2. Resolve tokens and write `{{TOOLBOX_PATH}}/templates/CLAUDE.global.md` → `~/.claude/CLAUDE.md`:
   - Replace `{{TOOLBOX_PATH}}` with the resolved toolbox path
   - Replace `{{WORKSPACE_PATH}}` with the resolved workspace path
   - (Use the same Python token-substitution logic as the original setup flow)

3. Output:
   > Session isolation and auto-switch installed. Each terminal window now maintains its own
   > active project. Mid-session context switches are detected automatically.

---

#### v1.6.0 — Modular CLAUDE sections

Splits the monolithic `~/.claude/CLAUDE.md` into modular section files, making `~/.claude/CLAUDE.md` user-owned (one @import line) so upgrades never overwrite custom content.

**Steps:**

1. Resolve `TOOLBOX_PATH`, `WORKSPACE_PATH`, and `CLAUDE_PATH` (= `~/.claude` absolute path).

2. Create `<CLAUDE_PATH>/toolbox-sections/` if it does not exist.

3. For each of the 9 section templates in `<TOOLBOX_PATH>/templates/sections/`:
   - Read the template, replace `{{TOOLBOX_PATH}}`, `{{WORKSPACE_PATH}}`, `{{CLAUDE_PATH}}`
   - Write rendered file to `<CLAUDE_PATH>/toolbox-sections/<filename>.md`

4. Read `<TOOLBOX_PATH>/templates/CLAUDE.global.md`, replace all 3 tokens, write to `<CLAUDE_PATH>/CLAUDE.global.md`.

5. Migrate `<CLAUDE_PATH>/CLAUDE.md`:
   - If it contains `## Session Start (automatic)` (old monolithic format): replace the entire file content with the single @import line: `@<CLAUDE_PATH>/CLAUDE.global.md`
     (Any content after a `# User` heading or `<!-- user content -->` comment is preserved after the @import line)
   - If the @import line is already present: do nothing
   - If neither: prepend `@<CLAUDE_PATH>/CLAUDE.global.md` followed by a blank line

6. Output:
   > Modular CLAUDE sections installed. ~/.claude/CLAUDE.md now contains a single @import line.
   > Your custom content (if any) is preserved. Section files are in ~/.claude/toolbox-sections/.

---

#### v1.8.0 — Path Variables in Global Config

Adds `$WORKSPACE` and `$VAULT` variable definitions to `~/.claude/toolbox-sections/vault-paths.md` so per-project `CLAUDE.md` files can use portable variable names instead of hardcoded absolute paths.

**Steps:**

1. Read `~/.claude/toolbox-sections/vault-paths.md`.

2. If the file already contains the text `$WORKSPACE` → output:
   > Path variables already present — skipping.
   ...and skip to the next migration.

3. Otherwise, extract the vault path from the existing rendered content using Python:

   ```python
   import re, pathlib

   f = pathlib.Path.home() / ".claude/toolbox-sections/vault-paths.md"
   content = f.read_text()

   m = re.search(r'`([^`\n]+)/02-projects/', content)
   vault_path = m.group(1)
   workspace_path = str(pathlib.Path(vault_path).parent)

   prefix = (
       "## Path Variables\n\n"
       "These variables can be used in any per-project `CLAUDE.md` — Claude resolves them using these definitions:\n\n"
       f"- `$WORKSPACE` = `{workspace_path}`\n"
       f"- `$VAULT` = `{vault_path}`\n\n"
   )
   f.write_text(prefix + content)
   print("done")
   ```

4. Output:
   > Path variables added to vault-paths.md. Per-project CLAUDE.md files can now use `$VAULT` instead of hardcoded paths.

---

#### v1.9.0 — Add /update-docs skill routing

```python
import pathlib

routing_path = pathlib.Path.home() / ".claude" / "toolbox-sections" / "skill-routing.md"

lifecycle_path = pathlib.Path.home() / ".claude" / "toolbox-sections" / "lifecycle-skills.md"

routing_content = routing_path.read_text(encoding="utf-8")
if "update-docs" not in routing_content:
    routing_content = routing_content.replace(
        "| Any code edit request",
        '| "update docs", "docs are stale", "fix stale docs", "/update-docs" | Read and follow `/update-docs` skill |\n| Any code edit request'
    )
    routing_path.write_text(routing_content, encoding="utf-8")
    print("Applied: add /update-docs routing row")
else:
    print("Skipped: /update-docs routing already present")

lifecycle_content = lifecycle_path.read_text(encoding="utf-8")
if "update-docs" not in lifecycle_content:
    lifecycle_content = lifecycle_content.rstrip() + "\n- /update-docs      → {{TOOLBOX_PATH}}/skills/update-docs.md\n"
    lifecycle_path.write_text(lifecycle_content, encoding="utf-8")
    print("Applied: add /update-docs lifecycle entry")
else:
    print("Skipped: /update-docs lifecycle already present")
```

---

#### v2.0.0 — Skill Manager Bootstrap

Installs the skill manager into the toolbox: downloads `skills/skills.md`, generates the initial `skills.json` and `skills.lock.json` from the current installed state, creates `~/.claude/skills-user.json`, and registers `/skills` in the routing table.

**Steps:**

1. Download `skills/skills.md` from the skill-manager repo and write to `{{TOOLBOX_PATH}}/skills/skills.md`:

```python
import urllib.request, pathlib

toolbox_path = pathlib.Path("{{TOOLBOX_PATH}}")
url = "https://raw.githubusercontent.com/sepehrn0107/skill-manager/main/skills/skills.md"
with urllib.request.urlopen(url, timeout=15) as r:
    content = r.read().decode()
dest = toolbox_path / "skills" / "skills.md"
dest.write_text(content, encoding="utf-8")
print(f"Downloaded skills.md → {dest}")
```

2. Generate `{{TOOLBOX_PATH}}/skills.json` from current installed plugins + local skills:

```python
import json, pathlib

home = pathlib.Path.home()
toolbox_path = pathlib.Path("{{TOOLBOX_PATH}}")
installed_plugins_path = home / ".claude" / "plugins" / "installed_plugins.json"

installed = json.loads(installed_plugins_path.read_text())
skills = []

# skill-manager itself
skills.append({
    "name": "skill-manager",
    "source": "github:sepehrn0107/skill-manager",
    "version": "1.0.0"
})

# Installed marketplace/github plugins
for plugin_key, plugin_list in installed["plugins"].items():
    entry = plugin_list[0]
    name = plugin_key.split("@")[0]
    marketplace = plugin_key.split("@")[1] if "@" in plugin_key else "unknown"
    version = entry.get("version", "unknown")
    skills.append({
        "name": name,
        "source": f"marketplace:{marketplace}/{name}",
        "version": version
    })

# Local skills (toolbox/skills/*.md)
skills_dir = toolbox_path / "skills"
reserved = {"skills"}
for skill_file in sorted(skills_dir.glob("*.md")):
    if skill_file.stem not in reserved:
        skills.append({
            "name": skill_file.stem,
            "source": f"local:skills/{skill_file.name}"
        })

manifest = {"version": "1", "skills": skills}
out = toolbox_path / "skills.json"
out.write_text(json.dumps(manifest, indent=2))
print(f"Written {out} with {len(skills)} skills")
```

3. Generate `{{TOOLBOX_PATH}}/skills.lock.json` from current installed plugins:

```python
import json, pathlib
from datetime import datetime, timezone

home = pathlib.Path.home()
toolbox_path = pathlib.Path("{{TOOLBOX_PATH}}")
installed_plugins_path = home / ".claude" / "plugins" / "installed_plugins.json"

installed = json.loads(installed_plugins_path.read_text())
locked = {}

for plugin_key, plugin_list in installed["plugins"].items():
    entry = plugin_list[0]
    name = plugin_key.split("@")[0]
    locked[name] = {
        "resolvedVersion": entry.get("version", "unknown"),
        "gitCommitSha": entry.get("gitCommitSha", ""),
        "lockedAt": entry.get("lastUpdated", datetime.now(timezone.utc).isoformat())
    }

locked["skill-manager"] = {
    "resolvedVersion": "1.0.0",
    "gitCommitSha": "",
    "lockedAt": datetime.now(timezone.utc).isoformat()
}

lock = {"version": "1", "locked": locked}
out = toolbox_path / "skills.lock.json"
out.write_text(json.dumps(lock, indent=2))
print(f"Written {out}")
```

4. Create `~/.claude/skills-user.json` if it does not exist:

```python
import json, pathlib
p = pathlib.Path.home() / ".claude" / "skills-user.json"
if not p.exists():
    p.write_text(json.dumps({"disabled": []}, indent=2))
    print("Created ~/.claude/skills-user.json")
else:
    print("~/.claude/skills-user.json already exists — skipping")
```

5. Register `/skills` in `~/.claude/toolbox-sections/skill-routing.md`:

```python
import pathlib

routing_path = pathlib.Path.home() / ".claude" / "toolbox-sections" / "skill-routing.md"

content = routing_path.read_text(encoding="utf-8")
if "skills" not in content:
    content = content.replace(
        "| Any code edit request",
        '| "`/skills`", "install skills", "list skills", "add skill", "disable skill", "enable skill", "update skill" | Read and follow `/skills` skill |\n| Any code edit request'
    )
    routing_path.write_text(content, encoding="utf-8")
    print("Added /skills routing entry")
else:
    print("Skipped: /skills routing already present")
```

6. Register `/skills` in `~/.claude/toolbox-sections/lifecycle-skills.md`:

```python
import pathlib

lifecycle_path = pathlib.Path.home() / ".claude" / "toolbox-sections" / "lifecycle-skills.md"
content = lifecycle_path.read_text(encoding="utf-8")
if "/skills" not in content:
    content = content.rstrip() + "\n- /skills             → {{TOOLBOX_PATH}}/skills/skills.md\n"
    lifecycle_path.write_text(content, encoding="utf-8")
    print("Added /skills lifecycle entry")
else:
    print("Skipped: /skills lifecycle already present")
```

7. Output:
   > Skill manager bootstrapped. Run `/skills list` to see your installed skills.

---

#### v2.1.0 — Compact Skill Routing Table

Compacts the skill routing table by ~40%, separating user-facing routes from internal auto-routes and removing verbose trigger descriptions.

**Steps:**

1. Read `{{TOOLBOX_PATH}}/templates/sections/skill-routing.md`, replace all tokens (`{{TOOLBOX_PATH}}`, `{{WORKSPACE_PATH}}`, `{{CLAUDE_PATH}}`), write to `<CLAUDE_PATH>/toolbox-sections/skill-routing.md`.

2. Output:
   > Skill routing table compacted. Token savings: ~200 tokens per session.

---

### 3. Write updated version

Write `TARGET_VERSION` (plain text, one line) to `~/.claude/toolbox-version.txt`

Output:
> Toolbox upgraded to v`TARGET_VERSION`. ✓

---

## Adding a new version (for toolbox maintainers)

When releasing a new version, bump the `"version"` field in `package.json` (the single source of truth).
Then add a new `#### vX.Y.Z — <Title>` migration block above the "Write updated version" step.