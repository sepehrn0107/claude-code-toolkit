---
title: "Universal Standards"
section: standards
skills-affected: [load-standards, standards-check]
last-updated: 2026-04-03
---

# Universal Standards

These nine standards apply to every project regardless of stack. They are loaded
by `/load-standards` at the start of every session.

## Architecture (`standards/universal/architecture.md`)

Clean layer boundaries: domain logic must not know about infrastructure, HTTP, or UI.
One responsibility per module. Depend on abstractions. Avoid premature abstraction —
wait for 3+ instances before extracting.

## Security (`standards/universal/security.md`)

Validate all input at system boundaries. Never hardcode secrets — use environment
variables or a secrets manager. Use established auth libraries. Hash passwords with
bcrypt or argon2. Enforce authorization at the service layer, not the handler.

## Git (`standards/universal/git.md`)

Conventional commits: `type(scope): imperative summary ≤72 chars`. Never push to
`main`/`master` directly — always branch + PR. One logical change per commit.

## Testing (`standards/universal/testing.md`)

Test pyramid: unit tests for logic, integration tests for boundaries, E2E for critical
flows. Test behavior, not implementation. Every bug fix gets a regression test.

## Documentation (`standards/universal/documentation.md`)

Document why, not what. README covers: what this is, setup, run, test, key decisions.
ADRs for significant architectural choices. For `/docs` files: frontmatter with
`skills-affected` and `last-updated` (see [Contributing / Documentation](../contributing/documentation.md)).

## Error Handling (`standards/universal/error-handling.md`)

Fail fast and explicitly. Include context in error messages (what was being done, what
failed, what to do). Validate at system boundaries — trust internal code.
Retry only on transient failures; don't retry on invalid input.

## Debugging (`standards/universal/debugging.md`)

Scientific method: hypothesize, test one thing at a time. Binary search for the bug
location. Read the error message fully before doing anything else. Check the obvious
things first (typos, missing imports, wrong env). When stuck, step back and re-read
the original requirements.

## Observability (`standards/universal/observability.md`)

Log structured output (JSON in production). Include request IDs for tracing. Health
check endpoints for services. Alert on symptoms, not causes. Never log secrets or PII.

## Code Review (`standards/universal/code-review.md`)

PR authors: describe what, why, and how to test. Keep PRs small and focused.
Reviewers: check correctness, security, tests, and standards compliance — not personal
style. Approve when it's good enough, not perfect.
