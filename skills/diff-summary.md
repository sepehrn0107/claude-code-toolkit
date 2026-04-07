---
name: diff-summary
description: Compact per-file diff summary — file list with +/- counts and changed symbol names. Use before commits or PRs instead of reading full `git diff` output.
---

# /diff-summary

Shape of the change at a glance — avoids loading hundreds of diff lines into context.

> `{{TOOLBOX_PATH}}` — resolved at install time from `~/.claude/toolbox-sections/vault-paths.md`

---

## When This Skill Triggers

Auto-trigger when Claude is about to:
- Read full `git diff` output to understand what changed
- Draft a commit message or PR description
- Summarise changes since branching from main

Do NOT trigger when you need to read the actual code changes — use `--full` for that, or `Read` the specific file.

---

## How to Run

```bash
python {{TOOLBOX_PATH}}/tools/diff-summary/diff_summary.py
```

Options:
- `--base <ref>` — compare against this ref (default: auto-detect `main`/`master`/`develop`)
- `--staged` — diff staged changes only (use before `git commit`)
- `--full` — append full diff after the summary

### Output format (stdout)

```
diff: main...HEAD (3 files, +142 -37)
  src/auth/handler.ts                     +89 -12  [handleRefresh, validateToken]
  src/api/routes.ts                       +32 -18  [router]
  tests/auth.test.ts                      +21 -7
```

| Stream | Meaning |
|--------|---------|
| **stdout** | Compact summary |
| **stderr** | Status / error messages |
| **exit 0** | Success |
| **exit 1** | Not a git repo or no changes detected |

---

## Examples

```bash
# Since main (default)
python {{TOOLBOX_PATH}}/tools/diff-summary/diff_summary.py

# Staged changes before commit
python {{TOOLBOX_PATH}}/tools/diff-summary/diff_summary.py --staged

# Compare against specific base
python {{TOOLBOX_PATH}}/tools/diff-summary/diff_summary.py --base develop

# Summary header + full diff body
python {{TOOLBOX_PATH}}/tools/diff-summary/diff_summary.py --full
```
