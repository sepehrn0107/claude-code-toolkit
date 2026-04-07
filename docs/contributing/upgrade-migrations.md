---
title: "Upgrade Migrations"
section: contributing
skills-affected: [upgrade, upgrade-dev]
last-updated: 2026-04-03
---

# Upgrade Migrations

## When a migration is required

Any change to installed behavior requires a migration:
- Routing table changes
- New or removed hook files
- Settings structure changes
- New skill added to lifecycle list
- Any change to `templates/sections/`

Changes that are purely additive to non-installed files (new skill files, standards
files, docs) do not require migrations.

## Migration pattern

In `toolbox/skills/upgrade.md`, add a new block above the
`### 3. Write updated version` line:

```markdown
#### vX.Y.Z — <Title>

```python
import pathlib

path = pathlib.Path.home() / ".claude" / "toolbox-sections" / "skill-routing.md"
content = path.read_text()

if "target-string" not in content:
    content = content.replace(
        "existing-anchor-string",
        "new-content\nexisting-anchor-string"
    )
    path.write_text(content)
    print("Applied: <description>")
else:
    print("Skipped: already applied")
```
```

## Rules

- **Idempotent:** always check if the target pattern already exists before writing.
  Use `if "target-string" not in content` to skip silently on already-patched installs.
- **String replacement only for `.md` patches** — no regex unless the match is unambiguous
- **JSON ops for settings patches** — load, mutate, dump; never string-replace JSON
- **One migration per version** — each `vX.Y.Z` block maps to exactly one `package.json`
  version bump

## Bumping the version

After adding a migration block, bump `"version"` in `package.json` to the matching version:

```json
{
  "version": "1.8.0"
}
```

The `/upgrade` skill compares this against `~/.claude/toolbox-version.txt` to decide
which migrations to run.

## Testing a migration

1. Back up `~/.claude/toolbox-sections/skill-routing.md`
2. Remove the target string manually to simulate a pre-migration state
3. Run `/upgrade`
4. Verify the target string is present in the file
5. Run `/upgrade` again — verify it skips silently (idempotency check)
