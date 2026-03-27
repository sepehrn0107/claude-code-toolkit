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
- Never commit directly to `main`/`master`
- Never commit secrets, credentials, or large binaries
- Every commit message must be meaningful — "fix stuff" is not acceptable
- Keep commits atomic: one logical change per commit
