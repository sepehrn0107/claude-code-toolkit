---
title: "Writing Documentation"
section: contributing
skills-affected: [update-docs, standards-check]
last-updated: 2026-04-03
---

# Writing Documentation

All files under `docs/` follow the standard defined in
`standards/universal/documentation.md`. This page explains how to apply it.

## Frontmatter

Every doc file must open with this block:

```yaml
---
title: "Human-readable title"
section: skills
skills-affected: [skill-name-1, skill-name-2]
last-updated: YYYY-MM-DD
---
```

`section` must be exactly one of: `getting-started`, `user-guide`, `skills`, `standards`, `tools`, `contributing`.

`skills-affected` is the key that keeps docs in sync with code. List every skill file
name (without `.md`), tool name, or standard name that the doc covers. When any of those
files changes, `/update-docs` will find and update this doc automatically.

## Writing Rules

- Write in second person, imperative voice: "Run this command", not "The user should run"
- Include one concrete example per concept — never introduce a concept without showing it
- No placeholders: `TBD` or empty sections cause `/standards-check` to block the PR
- One level of list nesting maximum
- Use code blocks for all commands, file paths, config snippets, and output
- Write skill names in backtick code: `` `/implement` `` not "the implement skill"
- Stay within scope: cover only what `skills-affected` declares

## Freshness

A doc becomes stale when any file in `skills-affected` is modified after `last-updated`.
Stale docs block PRs.

- **Automatic:** `/update-docs` runs at the end of every `/implement` ticket and updates
  `last-updated` for any docs it touches.
- **Manual:** if you edit a skill or standard directly (outside `/implement`), update
  `last-updated` in the corresponding doc before committing.

## Adding a New Doc

When a new skill, standard, or tool is created:

1. Create the doc file at the correct path under `docs/`
2. Add complete frontmatter including `skills-affected` pointing at the new item
3. Write content following the rules above
4. Add a link to `docs/README.md` under the correct section

If you use `/implement` to add the skill, the `/update-docs` step will create a stub doc
automatically — you only need to fill in the content and remove the `needs-content: true`
flag before merging.

## Where Docs Live

| Content | Path |
|---|---|
| Install, first session, concepts | `docs/getting-started/` |
| Memory, routing, standards, multi-project, optional setup | `docs/user-guide/` |
| All skills grouped by category | `docs/skills/` |
| Universal and stack-specific standards | `docs/standards/` |
| Python tools | `docs/tools/README.md` |
| Contributing guides | `docs/contributing/` |
