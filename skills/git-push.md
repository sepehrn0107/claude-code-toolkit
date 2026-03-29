---
name: git-push
description: Full git push workflow — branch, group files into logical commits, write conventional commit messages, push to remote, and open a PR with a meaningful title and body. Use this skill whenever the user says "push to git", "push this", "commit and push", "push my changes", "send to github", "open a PR", "create a PR", "push these changes", "ship this", or anything that implies staging, committing, and publishing code. Always enforce: never push to main/master, always branch + PR. Trigger even when the user says it casually (e.g. "just push it" or "lets push").
---

# /git-push

Full workflow: inspect changes → branch → group into logical commits → push → open PR.

Read `{{TOOLBOX_PATH}}/standards/universal/git.md` before proceeding.

---

## Step 1 — Inspect current state

Run these in parallel:

```bash
git status --short
git diff --stat
git log --oneline -5
git branch --show-current
```

Hold:
- `CURRENT_BRANCH`: current branch name
- `CHANGED_FILES`: full list from `git status --short`
- `DEFAULT_BRANCH`: detect via `git remote show origin | grep 'HEAD branch'` or assume `main`

---

## Step 2 — Branch guard

If `CURRENT_BRANCH` is `main` or `master`:
1. Ask the user: "You're on `main`. What should the branch be named?" (suggest one based on the changes if obvious)
2. Run: `git checkout -b <branch-name>`
3. Update `CURRENT_BRANCH`

If already on a feature branch, continue. Never push to `main`/`master` directly — not even if the user explicitly asks. Explain the rule and redirect.

---

## Step 3 — Group files into logical commits

Look at `CHANGED_FILES` and group them by **what they accomplish together**, not by directory or file type. The goal is that each commit, when read in isolation, tells a complete, meaningful story.

Grouping heuristics:
- Files that implement the same feature or fix the same bug → one commit
- Test files go with the code they test (same commit)
- Config/env/dependency changes that enable a feature → same commit as the feature
- Pure refactors with no behavior change → separate commit
- Docs/changelog updates → separate commit if unrelated to a code change
- Unrelated changes across different features → separate commits

For each group, decide:
- **Type**: `feat`, `fix`, `refactor`, `test`, `chore`, `docs`, `perf`, `ci`
- **Scope** (optional): the module, page, or domain affected (e.g. `auth`, `dashboard`, `api`)
- **Summary**: imperative mood, present tense, ≤72 chars, no period

Present the grouping plan to the user before committing:

```
Proposed commits:
  1. feat(auth): add JWT refresh token rotation   [src/auth/refresh.ts, src/auth/tokens.ts, tests/auth/refresh.test.ts]
  2. chore(deps): upgrade drizzle-orm to 0.30      [package.json, pnpm-lock.yaml]

Proceed? (or tell me how to adjust)
```

Wait for confirmation if the split is non-obvious. For a single logical change, skip the check and just do it.

---

## Step 4 — Commit each group

For each group in order:

```bash
git add <files-in-group>
git commit -m "<type>(<scope>): <summary>"
```

If a commit needs a body (breaking change, or the summary alone doesn't explain the why):

```bash
git commit -m "<type>(<scope>): <summary>

<body explaining why, not what>

<footer: Closes #123 or BREAKING CHANGE: ...>"
```

Never use `git add .` or `git add -A` — always add specific files to avoid accidentally staging secrets or unintended files.

---

## Step 5 — Push

```bash
git push -u origin <CURRENT_BRANCH>
```

If the push fails due to upstream divergence, do NOT force-push. Investigate the cause and surface it to the user.

---

## Step 6 — Open PR

Use `gh pr create` with a meaningful title and body. The PR body should answer: what changed, why, and what to watch out for when reviewing.

```bash
gh pr create \
  --base <DEFAULT_BRANCH> \
  --title "<concise title — same style as a commit summary>" \
  --body "$(cat <<'EOF'
## What
<1-3 bullets summarizing what changed>

## Why
<1-2 sentences on the motivation — what problem does this solve or what feature does it add>

## How
<key decisions or non-obvious implementation choices, if any>

## Test plan
<how to verify this works — manual steps or test names>
EOF
)"
```

**PR title rules:**
- Mirror the most significant commit's message, or write a higher-level summary if multiple unrelated things landed
- No "WIP", no "misc", no "stuff"
- ≤70 chars

After the PR is created, output the URL.

---

## Rules (non-negotiable)

- Never push directly to `main` or `master`
- Never use `git add .` or `git add -A`
- Every commit message must follow Conventional Commits
- One logical change per commit — don't mix unrelated things
- If `gh` is not installed or not authenticated, tell the user and stop before pushing
