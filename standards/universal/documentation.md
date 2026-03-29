# Documentation Standards

## What to Document

### Always Document
- **Why**, not just what — the code shows what; comments explain why
- Non-obvious decisions and their rationale
- Public APIs and interfaces
- Setup, run, and test instructions in README

### Never Over-Document
- Don't explain what the code obviously does
- Don't write comments that will go stale (prefer self-documenting names instead)
- Don't document private internals unless the logic is genuinely complex

## README

Every project needs a README with:
1. What this is (one paragraph)
2. How to set it up
3. How to run it
4. How to run tests
5. Key architectural decisions or important caveats

## ADRs (Architectural Decision Records)

Write an ADR whenever you make a significant architectural choice:
- Stored in `.claude/memory/decisions/YYYY-MM-DD-<slug>.md`
- Format: context → decision → consequences → alternatives considered

See `/implement` skill for the full ADR template.

## Code Comments
- Explain the *why* of complex or non-obvious logic
- Mark intentional workarounds: `// TODO: <reason>` or `// HACK: <reason>`
- Keep comments up to date — stale comments are actively harmful
