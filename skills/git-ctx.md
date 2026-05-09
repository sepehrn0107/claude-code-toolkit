---
name: git-ctx
description: Compact git context in one call — branch, tracking, staged/unstaged counts, and recent commits as a ~15-line summary. Auto-triggers when Claude is about to run multiple git info commands in sequence.
---

# /git-ctx

Returns compact git state in a single script call instead of chaining `git status` + `git log` + `git diff --stat`.

## When This Skill Triggers

Auto-trigger instead of running separate git commands when Claude needs to know any combination of:
- Current branch and upstream tracking (ahead/behind)
- Staged / unstaged / untracked file counts
- Recent commit history (one-liners)
- Working tree diff stat summary

Do NOT trigger when you need:
- The full diff content → use `/diff-summary` or `git diff`
- Actual file contents of changed files → use `Read`

---

## How to Run

```bash
python {{TOOLBOX_PATH}}/tools/git-ctx/git_ctx.py
```

Options:
- `--repo <path>` — git repo path (default: `.`)
- `--log <N>` — recent commits to show (default: `5`)

### Output format (stdout)

```
branch: feature/add-auth (3 ahead, 0 behind origin/main)
status: 2 staged, 1 unstaged, 0 untracked
recent commits (last 5):
  abc1234 feat(auth): add refresh token endpoint (2h ago)
  def5678 fix(api): handle null user (5h ago)
  ghi9012 chore: update deps (1d ago)
working tree: 3 files changed, 142 insertions(+), 37 deletions(-)
```

| Stream | Meaning |
|--------|---------|
| **stdout** | Compact summary — read and reason over this |
| **stderr** | Status / error messages |
| **exit 0** | Success |
| **exit 1** | Not a git repo or git unavailable |

---

## Examples

```bash
# Default (current dir, last 5 commits)
python {{TOOLBOX_PATH}}/tools/git-ctx/git_ctx.py

# Different repo, more commits
python {{TOOLBOX_PATH}}/tools/git-ctx/git_ctx.py --repo ../gymbro --log 10
```
