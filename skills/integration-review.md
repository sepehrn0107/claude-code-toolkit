---
name: integration-review
description: Cross-cutting review to run after all plans in a multi-plan project are individually approved, before tagging or shipping. Traces shared-state contracts across plan boundaries and verifies infrastructure artifacts.
---

# /integration-review

Run this **after** all plans in a multi-plan project have passed their individual spec + code quality reviews, but **before** the final tag or `v1.0.0` commit.

Individual plan reviews catch issues within a plan. This skill catches issues *between* plans — specifically: shared-state contracts, infrastructure artifacts, and cross-plan wiring assumptions.

## When to Use

- Any project split into multiple independent implementation plans (e.g., via `subagent-driven-development`)
- Before the final integration plan (e.g., Plan F) is dispatched
- Before tagging a milestone release

## Steps

### 1. Trace shared-state contracts

Identify every key written to a shared-state bus (e.g., `ctx.scratch`, Redux store, event bus, async context) by *any* plan, and verify there is a matching reader in the plan that consumes it.

For Python pipeline projects using `ctx.scratch`:
```bash
grep -r 'ctx\.scratch\[' pipeline/ tests/ --include="*.py" | sort
```

For each key written: confirm the consumer reads from the same key name. Missing readers = silent no-op. Missing writers = `KeyError` or wrong default.

### 2. Verify infrastructure artifacts are non-empty

Check that generated infrastructure files have real content — not stubs or empty bodies.

**Alembic migrations:**
```bash
# Fail if any migration's upgrade() is empty
python -c "
import re, pathlib, sys
for f in pathlib.Path('migrations/versions').glob('*.py'):
    src = f.read_text()
    if re.search(r'def upgrade.*?:\s*(pass\s*)?$', src, re.MULTILINE | re.DOTALL):
        print(f'WARNING: {f.name} may have empty upgrade()')
        sys.exit(1)
"
```

Also run `alembic check` if a live DB is available — it compares the ORM models against the current migration head and fails if they diverge.

**OpenAPI spec:** If a spec was generated, verify it has at least one path:
```bash
python -c "import yaml,sys; d=yaml.safe_load(open('openapi.yaml')); sys.exit(0 if d.get('paths') else 1)"
```

### 3. Check for duplicated shared utilities

Grep for identical function definitions that appear in more than one module — a common sign that a shared utility was copy-pasted instead of extracted:

```bash
grep -rn "^def make_storage\|^def get_db\|^def build_client" --include="*.py" .
```

If the same function body appears in multiple plan-owned files, extract it to a shared module before final integration.

### 4. Run a final cross-cutting security pass

- **Cross-tenant access**: verify every endpoint that takes a `tenant_id` path parameter also calls a `require_tenant` (or equivalent) guard that checks the JWT's tenant claim matches the path param.
- **Path traversal**: any endpoint or function that constructs file paths from user input must normalize the input (`posixpath.normpath` / `Path.resolve()`) before any access check.
- **Deprecated datetime**: `datetime.utcnow()` → `datetime.now(timezone.utc)` — search and replace before tagging.

```bash
grep -rn "datetime.utcnow\|\.utcnow()" --include="*.py" .
```

### 5. Run the full test suite one final time

```bash
uv run pytest -v --tb=short
```

All tests must pass. 0 failures, 0 errors. Warnings are acceptable.

### 6. Output

Summarize findings. If any cross-plan contract gap, empty artifact, or security issue is found, dispatch a fix sub-agent before tagging. If clean, confirm ready to tag.

---

## Common Cross-Plan Bugs Caught by This Skill

| Bug | Symptom | Root cause |
|-----|---------|------------|
| `ctx.scratch` key written by Plan A, never set by Plan F's runner | Stage silently no-ops (e.g., EXIF stripping skipped) | Plan A's stage docs assumed the runner would set the key; Plan F's runner was written from scratch |
| Empty Alembic `upgrade()` | Fresh Postgres deployment creates no tables | Agent ran `alembic revision` without `--autogenerate`, or autogenerate found no changes due to missing model imports in `env.py` |
| Duplicate `_make_storage()` | Config change applied in one place, silently missing in another | Two plan-owned files independently defined the same factory rather than importing a shared one |
| Cross-tenant path traversal | `startswith("tenants/t1/")` check passes for `tenants/t1/../t2/file` | Key not normalized before prefix check |
