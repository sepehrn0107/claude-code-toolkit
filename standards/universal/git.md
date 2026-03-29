# Git Standards

## Commit Conventions

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <summary>

[optional body]

[optional footer]
```

**Types:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `ci`

- Summary: imperative mood, present tense, no period, ≤72 chars
- Body: explain *why*, not *what* (the diff shows what)
- Footer: reference issues (`Closes #123`), note breaking changes

## Branching Strategy
- `main`/`master`: always deployable, protected — never commit directly
- `feat/<slug>`: new features
- `fix/<slug>`: bug fixes
- `chore/<slug>`: non-functional changes (deps, config, tooling)
- `retro/<slug>-YYYY-MM-DD`: toolbox improvement branches from /retrospective

## Workflow
1. Branch from `main`
2. Keep branches short-lived (days, not weeks)
3. Open a pull request for all changes to `main`
4. Squash or merge — be consistent within a project

## Rules
- **Never push directly to `main`/`master`** — not even "just this once"
- **Always branch from `main`/`master`** before starting any work
- **Always open a pull request** — no direct merges, no force-pushes to main
- Never commit secrets, credentials, or large binaries
- Every commit message must be meaningful — "fix stuff" is not acceptable
- Keep commits atomic: one logical change per commit

## Claude Enforcement
When assisting with git tasks, Claude must:
1. Refuse to run `git push origin main` or `git push origin master` — always create a branch first
2. After committing, always offer/create a branch and PR instead of pushing to main
3. If asked to push to main directly, explain the rule and push to a feature branch + open a PR instead
