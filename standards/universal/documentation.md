# Documentation Standards

## What to Document

### Always Document
- **Why**, not just what — the code shows what; comments explain why
- Non-obvious decisions and their rationale
- Public APIs and interfaces
- Setup, run, and test instructions in README

### Never Over-Document
- Don't explain what the code obviously does
- Don't write comments that will go stale (prefer self-documenting names instead)
- Don't document private internals unless the logic is genuinely complex

## README

Every project needs a README with:
1. What this is (one paragraph)
2. How to set it up
3. How to run it
4. How to run tests
5. Key architectural decisions or important caveats

## ADRs (Architectural Decision Records)

Write an ADR whenever you make a significant architectural choice:
- Stored in `.claude/memory/decisions/YYYY-MM-DD-<slug>.md`
- Format: context → decision → consequences → alternatives considered

See `/implement` skill for the full ADR template.

## Code Comments
- Explain the *why* of complex or non-obvious logic
- Mark intentional workarounds: `// TODO: <reason>` or `// HACK: <reason>`
- Keep comments up to date — stale comments are actively harmful

## /docs File Standard

All files under `docs/` must follow this standard. The `/standards-check` skill
enforces these rules automatically before any PR.

### Frontmatter Schema

Every `docs/` file must open with this frontmatter block:

```yaml
---
title: "Human-readable title"
section: getting-started | user-guide | skills | standards | tools | contributing
skills-affected: [skill-name-1, skill-name-2]
last-updated: YYYY-MM-DD
---
```

`skills-affected` lists the skill file names (without `.md`), tool names, or standard names
that this doc covers. The `/update-docs` skill uses this field to find which docs need
updating when a skill or standard changes.

### Writing Rules

- **Second person, imperative voice** — "Run this command", not "The user should run"
- **One concrete example per concept** — no concept introduced without a demonstration
- **No placeholder content** — `TBD`, `TODO`, or empty sections are failures caught by `/standards-check`
- **Max one list nesting level** — no sub-sub-bullets
- **Code blocks** for all commands, file paths, config snippets, and output examples
- **Skill names in backtick code** — write `` `/skill-name` `` not plain text
- **Scope discipline** — each file covers exactly what its `skills-affected` declares; do not add content about unrelated skills

### Freshness Rule

A doc is **stale** when any item in `skills-affected` has been modified (in git) after the
doc's `last-updated` date. Stale docs block PR merge via `/standards-check`.

The `/update-docs` skill updates `last-updated` automatically when it edits a doc.
For manual edits, update `last-updated` by hand before committing.
