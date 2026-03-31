## Codex Integration (automatic)

When in `/implement` Phase 3 (or any direct code-edit task), always attempt Codex first:

1. Check the `CODEX_AVAILABLE` flag set at session start — do not re-invoke `codex:setup`
2. If `CODEX_AVAILABLE` is true: read and follow `/codex-delegate` — pass the full context package (touched files from plan.md, applicable standards, TDD requirement, implement phase context)
3. If false or Codex exits non-zero: fall back to direct Claude implementation silently — do not announce the failure unless the task itself fails
4. After Codex completes: verify with `git diff` and continue the implement lifecycle as normal

This applies to every Phase 3 component invocation in `/implement`. The fallback must be transparent to the user.

When in `/implement` Phase 4 (or any review/verify task), always use `/codex-review`:

1. Check the `CODEX_AVAILABLE` flag
2. If true: read and follow `/codex-review` — pass file paths (not content), ticket state paths, and stack-appropriate standards paths
3. If false: `/codex-review` notifies the user ("Codex is not available. Continuing review with Claude.") and performs the review directly
4. The fallback is explicit — the user is always notified when Codex is skipped for review tasks
