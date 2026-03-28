# Error Handling Standards

Universal rules for handling errors across all stacks and project types.

---

## Core Principles

### Fail Fast, Fail Loudly
Detect and surface errors as early as possible. An error that crashes immediately
with a clear message is far better than one that silently corrupts state and fails
mysteriously later.

- Validate inputs at system boundaries (API endpoints, CLI args, file reads)
- Assert preconditions at the start of functions that have them
- Never swallow exceptions with empty catch blocks

### Don't Use Exceptions for Flow Control
Exceptions are for exceptional, unexpected situations — not for branching logic.
Using try/catch as an if/else replacement makes code harder to read and reason about.

```
# Wrong — using exceptions for expected control flow
try:
    user = get_user(id)
except NotFoundError:
    return create_user(id)

# Right — check explicitly
if not user_exists(id):
    return create_user(id)
return get_user(id)
```

### Errors Must Carry Context
A bare "something went wrong" is useless. Every error should answer:
- **What** failed (the operation)
- **Why** it failed (the cause)
- **Where** it failed (enough context to find it)

Wrap low-level errors with context as they propagate up the call stack.

---

## Where to Catch vs. Where to Propagate

| Layer | Rule |
|-------|------|
| Infrastructure (DB, HTTP client, file I/O) | Catch, wrap with context, re-raise as domain error |
| Domain / business logic | Let domain errors propagate; don't catch what you can't handle |
| Application / use case | Catch domain errors, map to user-facing responses |
| Entry point (HTTP handler, CLI, worker) | Final catch-all — log, return safe response, never crash the process |

Never catch an error just to log it and re-throw — you'll produce duplicate log entries.

---

## User-Facing vs. Internal Errors

**Never leak internal details to users.** Stack traces, SQL queries, file paths, and
internal identifiers are security risks and useless to end users.

- Map internal errors to user-safe messages at the boundary
- Use error codes (e.g. `USER_NOT_FOUND`, `PAYMENT_DECLINED`) so clients can handle them programmatically
- Log the full internal error (with stack trace) server-side
- Return a correlation/request ID in the response so support can trace the log

```
# User sees:
{ "error": "USER_NOT_FOUND", "message": "No account found with that email.", "request_id": "abc-123" }

# Logs contain:
[ERROR] request_id=abc-123 op=login email=foo@bar.com db_error="pq: no rows in result set" stack=...
```

---

## Validation Errors

Treat validation as a first-class concern, not an afterthought.

- Validate at the entry point — never let invalid data reach business logic
- Collect **all** validation errors before returning, not just the first one
- Return structured validation errors (field + message), not a single string
- Never throw a generic "invalid input" — be specific about what's wrong and why

---

## Retry Logic

Not all errors warrant a retry. Retrying the wrong errors wastes time and amplifies load.

| Error type | Retry? |
|------------|--------|
| Network timeout / transient failure | Yes — with exponential backoff + jitter |
| Rate limit (429) | Yes — after the `Retry-After` delay |
| Server error (500/503) | Sometimes — if idempotent |
| Client error (400/401/404) | No — retrying won't fix a bad request |
| Validation error | No |

Always set a maximum retry count and a total deadline. Log each retry attempt.

---

## Logging Errors

- Log at `ERROR` level when something unexpected happened and action is needed
- Log at `WARN` level for expected-but-notable situations (retrying, degraded mode)
- Always include: timestamp, severity, operation name, relevant IDs (user, request, entity), and the error message + stack trace
- Never log sensitive data: passwords, tokens, PII, card numbers

---

## Anti-Patterns to Avoid

- **Silent swallow**: `catch (e) {}` — hides bugs entirely
- **Catch-log-rethrow**: `catch (e) { log(e); throw e; }` — double-logs the same error
- **Generic messages**: "An error occurred" — gives no actionable information
- **Catch-all at every layer**: Catching everything everywhere prevents errors from being handled at the right level
- **Boolean returns for errors**: `return false` instead of throwing/returning an error type — callers ignore booleans
- **Error in error handler**: Ensure your error handling code itself cannot throw
