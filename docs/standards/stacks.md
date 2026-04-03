---
title: "Stack Standards"
section: standards
skills-affected: [load-standards, add-stack-standards]
last-updated: 2026-04-03
---

# Stack Standards

## Available stacks

| Stack | Directory | Inherits |
|---|---|---|
| `typescript-react` | `standards/stacks/typescript-react/` | — |
| `typescript-nextjs` | `standards/stacks/typescript-nextjs/` | `typescript-react` |
| `go` | `standards/stacks/go/` | — |
| `python-fastapi` | `standards/stacks/python-fastapi/` | — |
| `drizzle-postgres` | `standards/stacks/drizzle-postgres/` | — |

## Stack details

### `typescript-react`

Covers: component patterns (functional only, no class components), naming conventions
(PascalCase components, camelCase props), styling (CSS Modules or Tailwind — no inline
styles for layout), state management, testing with Vitest + Testing Library, TypeScript
strictness rules.

### `typescript-nextjs`

Inherits all `typescript-react` rules. Adds: routing (App Router conventions), rendering
strategy selection (SSR vs SSG vs ISR — when to use each), API route patterns, auth
integration (Auth.js), Drizzle ORM usage, and deployment configuration.

Inheritance is declared in `_base.md`:
```
base: typescript-react
```

### `go`

Covers: package design (one purpose per package), error handling (wrap with context,
never ignore), testing (table-driven tests, `testify` assertions), toolchain (go vet,
staticcheck, golangci-lint), naming conventions (unexported by default).

### `python-fastapi`

Covers: route structure (routers per domain), dependency injection patterns, Pydantic
validation at boundaries, async vs sync decisions, testing with pytest + httpx,
environment config via `pydantic-settings`.

### `drizzle-postgres`

Covers: schema design (one file per domain), migration discipline (never edit old
migration files), query patterns (typed queries, avoid raw SQL), type safety
(infer types from schema, never duplicate).

## Adding a new stack

Say: `"add standards for [stack name]"` — runs `/add-stack-standards`.

Alternatively, create the directory manually:

1. Create `toolbox/standards/stacks/<name>/README.md` with an overview
2. Add topic files (naming, testing, patterns, etc.) as needed
3. If this stack inherits another, add `_base.md` with `base: <parent-stack>`
4. Update `toolbox/skills/load-standards.md` to detect and load the new stack
5. Run `/upgrade-dev` to sync the live install

## File format

Stack standard files are plain Markdown. No frontmatter needed. Write in imperative
statements that Claude follows as rules:

```markdown
## Routing

- Put each domain's routes in a separate file: `routes/<domain>.py`
- Never put business logic in route handlers — delegate to a service function
- Use `APIRouter` with a prefix, not global `app.include_router` in the route file
```

Keep each file under 150 lines. One concern per file.
