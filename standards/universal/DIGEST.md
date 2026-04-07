# Standards Digest

> Compact reference for main-session orchestration. Load this instead of the 9 full standards files.
> Sub-agents receive paths to the specific full files they need.
>
> MAINTAINERS: Update this file whenever any standard file changes. One entry per standard, max 3 bullets.

## architecture → {{TOOLBOX_PATH}}/standards/universal/architecture.md
- Depend on abstractions; domain layer must not know about infrastructure, HTTP, or UI
- One responsibility per module; business logic never lives in handlers, controllers, or routes
- Avoid premature abstraction — wait for 3+ instances before extracting

## security → {{TOOLBOX_PATH}}/standards/universal/security.md
- Validate all input at system boundaries; never trust user data in SQL, shell commands, or file paths
- Never hardcode secrets; use environment variables or a secrets manager; never commit `.env`
- Use established auth libraries; hash passwords with bcrypt/argon2; enforce authz at the service layer

## git → {{TOOLBOX_PATH}}/standards/universal/git.md
- Conventional commits: `type(scope): imperative summary ≤72 chars` (feat/fix/docs/refactor/test/chore)
- **Never push to main/master** — always branch from main, commit there, open a PR; no exceptions
- Never commit secrets, binaries, or generated files

## testing → {{TOOLBOX_PATH}}/standards/universal/testing.md
- Unit > integration > E2E pyramid; test behavior, not implementation details
- Every bug fix gets a regression test before the fix lands
- Coverage is a proxy metric — prioritize coverage of business logic paths

## documentation → {{TOOLBOX_PATH}}/standards/universal/documentation.md
- Document why, not what; code shows what — comments explain non-obvious intent
- README must cover: what it is, setup, run, test, key decisions/caveats; ADR for key decisions
- Every `docs/` file needs frontmatter with `skills-affected` and `last-updated`; stale docs block PRs

## error-handling → {{TOOLBOX_PATH}}/standards/universal/error-handling.md
- Fail fast, fail loudly; never swallow exceptions silently
- Errors must carry context: what failed, why, where — use structured error types
- Map internal errors to user-safe messages at the boundary; never leak stack traces to clients

## debugging → {{TOOLBOX_PATH}}/standards/universal/debugging.md
- Reproduce → isolate → hypothesize → test → fix → verify; never skip to the fix
- Write a failing test before touching code; fix the root cause, not the symptom
- If stuck for 30 min, form a minimal reproduction before escalating

## code-review → {{TOOLBOX_PATH}}/standards/universal/code-review.md
- Self-review the diff before opening a PR; keep PRs under 400 lines
- Review order: correctness → tests → security → design → readability → style
- Label every comment: `[blocking]` / `[suggestion]` / `[nit]`

## observability → {{TOOLBOX_PATH}}/standards/universal/observability.md
- Structured JSON logs with timestamp, level, and request_id on every entry; never log secrets
- Four golden signals: latency, traffic, errors, saturation
- Alert on symptoms (error rate, p99 latency) not causes (CPU%); every alert needs a runbook
