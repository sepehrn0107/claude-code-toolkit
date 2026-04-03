---
title: "Memory Skills"
section: skills
skills-affected: [memory-sync, project, auto-switch, set-vault]
last-updated: 2026-04-03
---

# Memory Skills

## `/memory-sync` — write only the delta

**Auto-triggered:** before any write to a memory file.

Before writing anything to memory, reads the existing file and classifies each
intended entry:

| Classification | Action |
|---|---|
| Already captured | Skip — do not duplicate |
| Update to existing entry | Edit in place |
| Correction of stale content | Replace old entry |
| Genuinely new | Append only the new entry |

This keeps memory files lean — updates are targeted edits, not rewrites.

**Example:** marking Phase 2 as done becomes two line edits — moving the item from
"In progress" to "Done" — not a rewrite of the whole `progress.md` file.

---

## `/project` — switch active project

**Trigger:** `"switch project"`, `"change project"`, `"work on [repo]"`

Shows the list of projects in the workspace, loads memory files for the chosen one,
and updates `vault/05-areas/claude-memory/active-project.md`.

---

## `/auto-switch` — switch without being asked

**Auto-triggered:** when a message references a known project name that isn't currently
active (e.g., "in `my-app`", "for the `api-service` repo").

Runs `/project` automatically so the right context is loaded before Claude responds.

---

## `/set-vault` — change the vault path

**Trigger:** `"set vault"`, `"change vault path"`, `"/set-vault"`

Prompts for the new vault path, updates all config references in the rendered
`~/.claude/CLAUDE.md`, and re-renders `templates/CLAUDE.global.md`. Existing vault
files stay in place.
