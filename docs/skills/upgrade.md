---
title: "Upgrade Skills"
section: skills
skills-affected: [upgrade, upgrade-dev, add-stack-standards]
last-updated: 2026-04-03
---

# Upgrade Skills

## `/upgrade` — apply pending migrations

**Trigger:** `"upgrade toolbox"`, `"update toolbox"`, `"/upgrade"`

Applies all pending migration steps to an existing installation.

```bash
cd ~/Documents/workspace/toolbox
git pull
```

Then say `/upgrade` in any Claude Code session. Claude compares the installed version
(from `~/.claude/toolbox-version.txt`) to the target version (from `package.json`) and
runs each migration block whose version is greater than the installed one.

Migration steps are idempotent — they skip silently if the target pattern is already
present. Safe to run multiple times.

---

## `/upgrade-dev` — sync live install from template

**Trigger:** `"/upgrade-dev"`, `"apply template"`, `"sync live install"`

For toolbox developers. Renders `templates/CLAUDE.global.md` with resolved path tokens
and writes the result directly to `~/.claude/CLAUDE.md`. Also syncs section files and
settings.

Run this after any change to `templates/sections/` to see the effect immediately
without cutting a new release.

---

## `/add-stack-standards` — add a new tech stack

**Trigger:** `"add standards for [stack]"`

Guides Claude through creating a new stack standards directory:

1. Ask about the stack's key conventions (naming, testing, architecture patterns)
2. Create `toolbox/standards/stacks/<stack-name>/` with appropriate files
3. Add a `README.md` summarizing what the stack covers
4. Wire the new stack into `/load-standards`
5. Update `CLAUDE.global.md` template so sessions can detect and load the new stack

After adding, run `/upgrade-dev` so the live install picks up the new stack.
