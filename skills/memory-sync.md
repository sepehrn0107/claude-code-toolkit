---
name: memory-sync
description: Before writing to any memory file, read the existing content and write only the delta — new or changed entries. Prevents duplicate memory bloat across sessions.
---

# /memory-sync

Write only what's actually new. Read before you write.

---

## When This Skill Applies

Apply before writing or appending to any memory file:
- `{{VAULT_PATH}}/02-projects/<project>/memory/progress.md`
- `{{VAULT_PATH}}/02-projects/<project>/memory/lessons.md`
- `{{VAULT_PATH}}/02-projects/<project>/memory/architecture.md`
- `{{VAULT_PATH}}/02-projects/<project>/memory/project_context.md`
- `{{VAULT_PATH}}/05-areas/claude-memory/*.md` (global memory)

---

## Protocol

### 1. Read the existing file first

Read the current content before writing anything.

### 2. Classify each intended entry

For every piece of content you plan to write, ask:

| Question | Action |
|---|---|
| Already captured (same fact, different words)? | Skip — do not duplicate |
| Update to an existing entry? | Edit that entry in place |
| Correction of stale content? | Replace the old entry |
| Genuinely new information? | Append only the new entry |

### 3. Write the minimum delta

- **Updating** → use `Edit` to change the specific line/section
- **Appending** → add only new entries, not the full file
- **Correcting** → replace the outdated entry; do not leave both versions

### 4. Confirm the write

After writing, output one line:
```
[memory-sync] Updated <filename>: <what changed in one sentence>
```

---

## What NOT to save to memory

Even if the user asks — explain why and save only the non-obvious part:

- Code patterns derivable from reading the codebase
- Git history (use `git log` instead)
- In-progress task state or current conversation context
- Anything already documented in `CLAUDE.md`
- Temporary decisions that will be superseded in the same session

---

## Example — progress.md

Existing file:
```markdown
## Done
- Phase 0: scaffold complete
- Phase 1: auth endpoints

## In progress
- Phase 2: dashboard UI
```

Intended write: "Phase 2 complete, Phase 3 starting"

Bad (rewrites whole file):
```markdown
## Done
- Phase 0: scaffold complete
- Phase 1: auth endpoints
- Phase 2: dashboard UI   ← NEW

## In progress
- Phase 3: notifications  ← NEW
```

Good (targeted edit):
- Move "Phase 2: dashboard UI" from In progress → Done
- Replace "Phase 2: dashboard UI" under In progress with "Phase 3: notifications"
