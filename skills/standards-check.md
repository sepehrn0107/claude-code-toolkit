---
name: standards-check
description: Verifies the codebase meets all toolbox standards (architecture, security, git, testing, documentation) before merging. Run this before opening any PR, after a major implementation, or when the user says "check this", "review", "ready to merge", or "before PR". This is automatically required before any push or PR — never skip it. Also invokes code-simplifier for a quality pass on recently changed code.
---

# /standards-check

Run at any point to verify the codebase meets toolbox standards.

## When to Use
Run this: before opening a PR, after a major implementation, or on demand.

## Steps

### 1. Load Active Standards and Index (parallel)

Run both at the same time:

- Invoke `{{TOOLBOX_PATH}}/skills/load-standards.md` and wait for the confirmation line
- If `.claude/index/README.md` exists:
  - Run `git diff --name-only main` to get the list of changed files
  - Launch a **sub-agent** (haiku model) via `{{TOOLBOX_PATH}}/skills/query-index.md` with question:
    "What are the direct importers (imported_by) of these files: [paste the changed file list]?
     Also note which cluster(s) they belong to."
  - The sub-agent reads `graph-imports.json` and `graph-clusters.json` and returns the blast radius
  - Use the returned file list as the review scope — changed files plus their direct importers

### 2. Check Code Against Standards
Review relevant code against each standard area:

- **Architecture**: separation of concerns, clean layer boundaries, no god objects, no business logic in handlers/controllers
- **Security**: input validation at boundaries, no hardcoded secrets, no obvious OWASP violations
- **Git**: commit messages follow conventions, no secrets or binaries committed
- **Testing**: business logic covered, tests test behavior not implementation, regression test for recent bugs
- **Documentation**: README present and current, ADRs written for key decisions, non-obvious code commented

### 3. Code Review
Invoke `{{TOOLBOX_PATH}}/skills/select-model.md` with task: "Review code against standards and best practices."
Use the returned model for Steps 3 and 4.

Invoke `superpowers:requesting-code-review` using the chosen model.

### 4. Simplify
Invoke `code-simplifier` using the chosen model for a quality and clarity pass on recently changed code.

### 5. Output Results
Produce a checklist with pass/fail for each area, with file references for failures:

```
Standards Check Results
=======================
[x] Architecture      — pass
[ ] Security          — hardcoded API key at src/config.ts:12
[x] Git               — pass
[ ] Testing           — no tests for UserService.createUser
[x] Documentation     — pass
```

Address all failures before merging.
