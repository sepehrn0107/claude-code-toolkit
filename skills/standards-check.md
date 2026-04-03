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

### 2.5 Docs Check

For each file changed in this PR that lives under `skills/`, `standards/`, or `tools/`:

1. Run:
   ```bash
   grep -rl "skills-affected:.*\b<base-name>\b" {{TOOLBOX_PATH}}/docs/ --include="*.md"
   ```
   to find which doc files cover it (via `skills-affected` frontmatter).

2. For each found doc file, read its `last-updated` field and compare it to the file's
   last git commit date:
   ```bash
   git log -1 --format="%as" -- toolbox/skills/<name>.md
   ```

3. If `last-updated` is **older** than the file's last commit date, the doc is stale.

4. If any stale docs are found, **block the PR**:
   ```
   [ ] Docs — stale: docs/skills/lifecycle.md covers 'implement' (last-updated: 2026-01-01,
       skill last changed: 2026-03-15). Run `/update-docs` or update manually before merging.
   ```

5. If no stale docs are found (or no docs cover the changed files), mark as pass:
   ```
   [x] Docs — pass
   ```

Add the docs result to the output checklist in Step 5.

### 3. Code Review

Read and follow `{{TOOLBOX_PATH}}/skills/codex-review.md`.

Pass the following context to the skill:
- Project directory: current working directory
- Review scope: the changed files identified in Step 1 (plus their direct importers if index is available)
- Stack: from `.claude/memory/stack.md` or inferred
- No ticket ID (standalone review — skip writing `verification.md`)

The skill delegates to Codex (passing file paths, not content), notifies the user if Codex is unavailable, and falls back to Claude review. Use its verdict and issues list as input for Step 5.

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
[x] Docs              — pass
```

Address all failures before merging.
