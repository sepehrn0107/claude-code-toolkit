---
title: "Standards"
section: user-guide
skills-affected: [load-standards, standards-check, add-stack-standards]
last-updated: 2026-04-03
---

# Standards

## What standards are

Standards are Markdown files under `toolbox/standards/` that define rules Claude follows
when writing code. They cover architecture, naming, security, testing, git hygiene, and
more. Claude reads the applicable standards before writing any code — this is enforced by
a shell hook that blocks file edits until standards are loaded in projects that use the
toolkit (those set up with `/new-project`).

## How they load

**Per session, once.** When Claude is about to write code for the first time in a
session, it runs `/load-standards`:

1. Reads `standards/universal/DIGEST.md` (a one-page summary of all 9 universal standards)
2. Detects the project stack from `.claude/memory/stack.md`
3. Reads the applicable stack standards
4. Sets a session flag — the pre-tool hook allows edits from this point forward

Standards are never re-read during the same session.

## Available stacks

| Stack | What's covered |
|---|---|
| `typescript-react` | Components, naming, styling, testing, TypeScript conventions |
| `typescript-nextjs` | Routing, rendering (SSR/SSG/ISR), API routes — inherits React standards |
| `go` | Package design, error handling, testing, toolchain |
| `python-fastapi` | Route structure, dependency injection, validation, testing |
| `drizzle-postgres` | Schema design, migrations, query patterns, type safety |

## Adding standards for a new stack

Say:

```
add standards for [stack name]
```

Claude runs `/add-stack-standards` — it asks about the stack's conventions, then writes
a new directory under `toolbox/standards/stacks/<stack-name>/` and wires it into the
load-standards skill.

See [Standards Reference / Stacks](../standards/stacks.md) for detail on stack
inheritance and file format.
