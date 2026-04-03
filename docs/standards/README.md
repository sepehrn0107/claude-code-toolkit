---
title: "Standards Reference"
section: standards
skills-affected: [load-standards, standards-check, add-stack-standards]
last-updated: 2026-04-03
---

# Standards Reference

## What standards are

Standards are Markdown files under `toolbox/standards/` that define rules Claude follows
when writing and reviewing code. They are not style guides — they are loaded into Claude's
context and followed as instructions.

## How the standards gate works

A shell hook (`pre-tool-standards-gate.sh`) checks for a session flag before allowing
any file edit. The flag (`/tmp/toolbox-standards-loaded-<session-id>`) is created by
`/load-standards` after it confirms all applicable standards are loaded.

The gate is active in any project that has `.claude/memory/MEMORY.md` (created by
`/new-project`). Projects without that file bypass the gate silently.

## Standard file structure

Every standards file is plain Markdown. No special format required. Standards under
`standards/universal/` apply to every project. Standards under `standards/stacks/<name>/`
apply only when that stack is active.

The `standards/universal/DIGEST.md` file is a one-page summary of all 9 universal
standards. The main session loads only the digest; sub-agents receive paths to the
specific full files they need.

## Adding standards

- **New universal rule** → edit the appropriate file in `standards/universal/`
- **New stack** → say `"add standards for [stack]"` (runs `/add-stack-standards`)
- **Rule from project work** → run `/retrospective` after a project milestone

See [Standards / Stacks](stacks.md) for the inheritance model and file format.
