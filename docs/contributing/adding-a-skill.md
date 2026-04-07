---
title: "Adding a Skill"
section: contributing
skills-affected: [upgrade-dev, upgrade]
last-updated: 2026-04-03
---

# Adding a Skill

## Step 1 — Write the skill file

Create `toolbox/skills/<name>.md`:

```markdown
---
name: skill-name
description: One sentence: when this triggers and what it does. This is matched by the router.
---

# /skill-name

## When to Use
<trigger conditions>

## Steps

### 1. <First step>
<instructions>

### 2. <Second step>
<instructions>
```

Rules for the skill body:
- Use `{{TOOLBOX_PATH}}` as a placeholder for the toolbox install path
- Write structured output to ticket state files (`.claude/tickets/<id>/`)
- Follow the memory-sync protocol for any memory writes
- Return a one-line status string at the end (e.g., `"Skill complete."`)

## Step 2 — Add a routing row

In `toolbox/templates/sections/skill-routing.md`, find `## Automatic Skill Routing` and add:

```markdown
| "trigger phrase [X]" | Read and follow `/skill-name` skill |
```

If the skill is a named lifecycle skill (user-invocable), also add it under
`## Lifecycle Skills` in `toolbox/templates/sections/lifecycle-skills.md`:

```markdown
- /skill-name      → {{TOOLBOX_PATH}}/skills/skill-name.md
```

## Step 3 — Sync the live install

Run `/upgrade-dev` to re-render the templates into `~/.claude/`.

Verify the routing row appears in the live install:

```bash
grep "skill-name" ~/.claude/toolbox-sections/skill-routing.md
```

## Step 4 — Add a migration (for releases)

In `toolbox/skills/upgrade.md`, add a new migration block above the
`### 3. Write updated version` line:

```markdown
#### vX.Y.Z — Add skill-name skill

```python
import re, pathlib

path = pathlib.Path.home() / ".claude" / "toolbox-sections" / "skill-routing.md"
content = path.read_text()

if "skill-name" not in content:
    content = content.replace(
        "| Any code edit request",
        '| "trigger phrase [X]" | Read and follow `/skill-name` skill |\n| Any code edit request'
    )
    path.write_text(content)
```
```

Then bump `"version"` in `package.json` to match.

## Step 5 — Write the doc

Add a section to the appropriate doc file under `docs/skills/`:
- Lifecycle skills → `docs/skills/lifecycle.md`
- Memory skills → `docs/skills/memory-skills.md`
- Code tool skills → `docs/skills/code-tools.md`
- Upgrade skills → `docs/skills/upgrade.md`

Update that doc's `last-updated` frontmatter field.
Also add a row to the quick-reference table in `docs/skills/README.md`.

## Step 6 — PR

```bash
git add toolbox/skills/skill-name.md toolbox/templates/sections/ toolbox/skills/upgrade.md package.json toolbox/docs/
git commit -m "feat(skills): add /skill-name skill"
gh pr create
```
