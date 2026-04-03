---
name: update-docs
description: Updates /docs files after any skill, standard, or tool change. Invoked automatically at the end of /implement Phase 5 before the PR is opened. Can also be run manually to fix stale docs. Reads plan.md from the ticket state to find changed items, maps them to docs via skills-affected frontmatter, makes surgical edits, and writes a docs.md artifact to the ticket state.
---

# /update-docs

Keeps `/docs` in sync with skills, standards, and tools after every change.

## When This Runs

- **Automatic:** called by `/implement` Phase 5 (Step 5a) before the PR is opened
- **Manual:** run anytime to repair stale docs (`run /update-docs`)

---

## Steps

### 1. Identify changed items

**If called from `/implement` Phase 5 (ticket ID available):**

Read `.claude/tickets/<ticket-id>/plan.md` — extract the "Files" section:
- Any file under `skills/` that appears in "New" or "Modified" → extract the base name (e.g. `implement`)
- Any file under `standards/` → extract the base name (e.g. `architecture`)
- Any file under `tools/` → extract the tool folder name (e.g. `read-section`)

Hold as `CHANGED_ITEMS`: a list of base names.

**If called manually (no ticket ID):**

Run:
```bash
git diff --name-only main | grep -E "^toolbox/(skills|standards|tools)/"
```

Extract base names from the output. Hold as `CHANGED_ITEMS`.

---

### 2. Find affected doc files

For each item in `CHANGED_ITEMS`:

Run:
```bash
grep -rl "<item-name>" toolbox/docs/ --include="*.md"
```

Collect all files where `skills-affected` in the frontmatter contains the item name.
Hold as `AFFECTED_DOCS`: a list of doc file paths.

---

### 3. Update each affected doc

For each file in `AFFECTED_DOCS`:

1. Read the file
2. Identify what changed in the skill/standard/tool (from the ticket plan or git diff)
3. Make the minimum surgical edit — update only the paragraphs or steps that describe the changed behavior; do not rewrite unaffected sections
4. Update the `last-updated` field in the frontmatter to today's date (YYYY-MM-DD)

---

### 4. Handle new items with no doc

For each item in `CHANGED_ITEMS` that produced **no matches** in Step 2
(no existing doc covers it):

Create a stub doc at the correct path:

| Item type | Doc path |
|---|---|
| New skill | `toolbox/docs/skills/<group>.md` (add a new section to the most relevant group file) |
| New universal standard | `toolbox/docs/standards/universal.md` (add a new section) |
| New stack standard | `toolbox/docs/standards/stacks.md` (add a new section) |
| New tool | `toolbox/docs/tools/README.md` (add a new section) |

Add a `needs-content: true` flag to the frontmatter of any stub:

```yaml
---
title: "..."
section: ...
skills-affected: [new-item-name]
last-updated: YYYY-MM-DD
needs-content: true
---

<!-- TODO: fill this section before merging -->
```

---

### 5. Write the `docs.md` artifact

**If called from `/implement` (ticket ID available):**

Write `.claude/tickets/<ticket-id>/docs.md`:

```markdown
## Docs Updated

- docs/path/to/file.md — <one sentence describing what changed>

## Docs Created (stub — needs content)

- docs/path/to/stub.md
```

If no docs were updated or created, write:
```markdown
## Docs

No doc changes required for this ticket.
```

**If called manually:** skip this step.

---

### 6. Output result

Print a summary line:

```
[update-docs] Updated: <n> files | Created stubs: <n> | No-op: <n items with no matching docs>
```

If any stubs were created with `needs-content: true`, print:

```
⚠ Stub docs need content before merging:
  - docs/path/to/stub.md
```
