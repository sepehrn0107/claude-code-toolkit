---
title: "Adding Standards"
section: contributing
skills-affected: [load-standards, add-stack-standards, upgrade-dev]
last-updated: 2026-04-03
---

# Adding Standards

## Adding a universal rule

Edit the appropriate file in `toolbox/standards/universal/`:

| File | When to edit |
|---|---|
| `architecture.md` | Module boundaries, dependencies, layering |
| `security.md` | Input validation, secrets, auth patterns |
| `git.md` | Commit conventions, branching, PR rules |
| `testing.md` | Test pyramid, coverage, test design |
| `documentation.md` | Doc format, freshness rules, ADR guidance |
| `error-handling.md` | Error types, retry logic, validation |
| `debugging.md` | Debugging process, tooling |
| `observability.md` | Logging, metrics, health checks |
| `code-review.md` | PR author/reviewer expectations |

After editing a universal standard, **also update `standards/universal/DIGEST.md`**
with the changed rule (max 3 bullets per standard in the digest).

## Adding a stack

### Quick path

Say: `"add standards for [stack name]"` — runs `/add-stack-standards`.

### Manual path

1. Create `toolbox/standards/stacks/<name>/README.md`:

```markdown
# <Stack Name> Standards

Brief overview of what this covers and why these rules matter.
```

2. Create topic files as needed (e.g., `naming.md`, `testing.md`, `patterns.md`).
   Keep each file under 150 lines. One concern per file.

3. If this stack inherits from another, create `_base.md`:

```markdown
base: typescript-react
```

4. Update `toolbox/skills/load-standards.md` — add a detection block for the new stack.

5. Run `/upgrade-dev`.

## File format

Stack standards files are plain Markdown. No frontmatter needed. Write in imperative
statements that Claude follows as rules:

```markdown
## Routing

- Put each domain's routes in a separate file: `routes/<domain>.py`
- Never put business logic in route handlers — delegate to a service function
- Use `APIRouter` with a prefix, not global `app.include_router` in the route file
```

## After adding any standard

Run `/standards-check` to verify the new rule doesn't conflict with existing ones.
If the change affects installed behavior, add a migration and bump the version.
