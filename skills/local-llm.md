---
name: local-llm
description: Invoke the local LLM (LM Studio) via call.py for self-contained,
  mechanical tasks. Called automatically by select-model.md when routing to Tier 0,
  and by implement.md for simple Phase 3 components. Never use for tasks requiring
  codebase search, multi-file coordination, or standards compliance at write time.
---

# /local-llm

Invoke the local LLM for self-contained, low-risk tasks that don't require Claude's reasoning.

> `{{TOOLBOX_PATH}}` is resolved to the actual toolbox path from `~/.claude/CLAUDE.md`.

---

## When This Skill Is Used

This skill executes when `select-model.md` returns `tier: local`. That happens for:

| Task type | Notes |
|---|---|
| Single-function code generation (signature given) | Fits in one prompt |
| Unit test scaffolding for a given function | Formulaic output |
| Code summarization (< 200 lines) | No standards required |
| Docstrings / inline documentation | Mechanical |
| Simple single-file refactoring (rename, extract, lint) | Deterministic |
| Boilerplate / CRUD skeleton generation | Template-driven |

**Do NOT use local LLM for:**
- Tasks requiring reading multiple files
- Any task where output must comply with project standards at write time
- Feature ideation, architecture, or security decisions
- Anything involving session context, memory, or tickets (those need Claude)

---

## Invocation Pattern

Call via Bash tool — **always use the full absolute path**:

```bash
python3 {{TOOLBOX_PATH}}/tools/local-llm/call.py \
  --task-type <TASK_TYPE> \
  --prompt "<PROMPT>"
```

Available `--task-type` values: `coding`, `tests`, `summarize`, `docs`, `refactor`, `generic`

Optional flags:
- `--model-slot quality` — use the quality model slot from config.models (for harder tasks)
- `--no-cache` — skip cache when the input code has changed since the last call
- `--max-tokens N` — override the default max_tokens for longer outputs

### Exit Codes

| Exit code | Meaning | Action |
|---|---|---|
| 0 | Success | Use stdout as the LLM's completion |
| 1 | Server unreachable or disabled | Fall back to haiku sub-agent for the same task |
| 2 | Config error | Alert user: check `{{TOOLBOX_PATH}}/tools/local-llm/config.json` |

---

## Prompt Construction Guidelines

Keep prompts **focused and short** (target < 500 tokens for code tasks):

1. **Include only what the model needs**: function signature, a brief description, constraints
2. **Do not paste full files**: extract the relevant function or class only
3. **Be explicit about output format**: "Output only the function, no explanation, no markdown fences"
4. **For test tasks**: paste the function body + explicitly name the test framework (pytest)
5. **For refactor tasks**: describe the specific change, not a general improvement request

### Example — coding task

```bash
python3 {{TOOLBOX_PATH}}/tools/local-llm/call.py \
  --task-type coding \
  --prompt "Write a Python function \`validate_email(email: str) -> bool\` that returns True if the email has a valid format (contains @ and a dot after @). No external libraries. Output only the function."
```

### Example — test task

```bash
python3 {{TOOLBOX_PATH}}/tools/local-llm/call.py \
  --task-type tests \
  --prompt "Write pytest unit tests for this function:\n\ndef celsius_to_fahrenheit(c: float) -> float:\n    return c * 9/5 + 32\n\nCover: freezing point, boiling point, body temperature, negative value."
```

### Example — summarize task

```bash
python3 {{TOOLBOX_PATH}}/tools/local-llm/call.py \
  --task-type summarize \
  --no-cache \
  --prompt "Summarize what this function does in 3-5 sentences:\n\n<paste function here>"
```

---

## Fallback Protocol

When exit code is non-zero (local LLM unavailable):

1. Log: `[local-llm unavailable — routing to haiku]`
2. Launch a haiku sub-agent with the identical task and prompt
3. Do not retry the local call in the same session
4. Note the fallback in the ticket's implementation.md if inside `/implement`

---

## Caching Behavior

Identical prompts within the cache TTL (default: 24h) return in < 10ms. Use `--no-cache` when:
- The code being summarized or refactored has changed since the last call
- You are running benchmarks (`bench.py` always passes `--no-cache`)
- The task is non-deterministic by nature (ideation)

Cache lives at `{{TOOLBOX_PATH}}/tools/local-llm/cache/` — gitignored.

---

## Switching Models

To use a different model:
1. Load it in LM Studio
2. Update `{{TOOLBOX_PATH}}/tools/local-llm/config.json` → `model` field
3. Or update `models.fast` / `models.quality` for named slots
4. Run `python3 {{TOOLBOX_PATH}}/tools/local-llm/bench.py --categories smoke` to verify

To compare two models:
```bash
python3 {{TOOLBOX_PATH}}/tools/local-llm/bench.py --compare <other-model-name>
```

---

## Health Check

Verify LM Studio is reachable:
```bash
python3 {{TOOLBOX_PATH}}/tools/local-llm/call.py --health
```

Outputs: `[local-llm] status=ok model=... latency=X.Xs`
Exit 0 on success, exit 1 if unreachable.
