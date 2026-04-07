---
name: skills
description: Skill manager for the Claude Code toolbox. Lists, installs, enables, disables, and updates skills (local and marketplace). Triggered by /skills, "install skill", "list skills", "add skill", "disable skill", "enable skill", "update skill".
---

# /skills — Skill Manager

Manages skills in the toolbox: list installed skills, install new ones from GitHub or marketplace, enable/disable, and update.

## When to Use

Triggered automatically when user says: `/skills`, "install skill", "list skills", "add skill", "disable skill", "enable skill", "update skill".

## Commands

### `/skills list`
List all skills registered in `skills.json`, grouped by source.

### `/skills install <source>`
Install a skill from GitHub (`github:<owner>/<repo>`).
1. Download `skills/<name>.md` from raw GitHub URL
2. Write to `{{TOOLBOX_PATH}}/skills/<name>.md`
3. Append entry to `skills.json` and `skills.lock.json`
4. If download fails, output error and do NOT update skills.json

### `/skills disable <name>` / `/skills enable <name>`
Toggle skill activation via `~/.claude/skills-user.json` disabled array.

### `/skills update [<name>]`
Re-download one or all github-sourced skills and update `skills.lock.json`.

## Data Files

| File | Purpose |
|---|---|
| `{{TOOLBOX_PATH}}/skills.json` | Canonical list of installed skills with source and version |
| `{{TOOLBOX_PATH}}/skills.lock.json` | Locked versions and commit SHAs |
| `~/.claude/skills-user.json` | User overrides: disabled list |
