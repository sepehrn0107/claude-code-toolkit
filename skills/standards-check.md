# /standards-check

Run at any point to verify the codebase meets toolbox standards.

## When to Use
Run this: before opening a PR, after a major implementation, or on demand.

## Steps

### 1. Load Active Standards
Read:
- `{{TOOLBOX_PATH}}/standards/universal/` — all 5 universal standard files
- `{{TOOLBOX_PATH}}/standards/stacks/<stack>/` — if stack is set in `.claude/memory/stack.md`

### 2. Check Code Against Standards
Review relevant code against each standard area:

- **Architecture**: separation of concerns, clean layer boundaries, no god objects, no business logic in handlers/controllers
- **Security**: input validation at boundaries, no hardcoded secrets, no obvious OWASP violations
- **Git**: commit messages follow conventions, no secrets or binaries committed
- **Testing**: business logic covered, tests test behavior not implementation, regression test for recent bugs
- **Documentation**: README present and current, ADRs written for key decisions, non-obvious code commented

### 3. Code Review
Invoke `superpowers:requesting-code-review`.

### 4. Simplify
Invoke `code-simplifier` for a quality and clarity pass on recently changed code.

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
