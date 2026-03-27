# /select-model

Invoked before every `Agent` tool call (or local LLM call). Determines the right
model tier for the task and routes execution accordingly.

## When to Use

Call this skill immediately before using the `Agent` tool. Pass the task description as context.

> `{{TOOLBOX_PATH}}` is resolved to the actual toolbox path from `~/.claude/CLAUDE.md` — never pass the literal placeholder string to any tool.

## Steps

### 1. Check for Saved Config

Read `{{TOOLBOX_PATH}}/memory/model-config.md`.

- If the file exists → extract `default_model` from the frontmatter, skip to Step 4.
  `default_model` must be one of `local / haiku / sonnet / opus`.
  If it is missing or not in that list, treat the file as absent and continue to Step 2.
- If the file does not exist → continue to Step 2.

### 2. Reason About Task Complexity

Evaluate the task description against this table:

| Task type | Model |
|---|---|
| Single-shot text generation with fully-specified input (commit msg from diff, classify a string, reformat text) | local |
| File search, pattern matching, simple lookups | haiku |
| Code reading, summarization, straightforward edits | haiku |
| Multi-step implementation, TDD, code generation | sonnet |
| Architecture decisions, brainstorming, planning | sonnet |
| Novel problem-solving, highly ambiguous tasks | opus |
| Security review, high-stakes analysis | opus |

When uncertain, default to **sonnet**.

**Use `local` only when ALL of these are true:**
- The full prompt can be passed as a single self-contained string (no file reads needed at runtime)
- The task requires no tool calls, no file writes, no multi-step reasoning
- The output is a single text blob (not a structured plan or action sequence)
- Correctness is not high-stakes

### 3. Present Options

**If `opus` is recommended:** show opus as option 1, sonnet as option 2.

**If `local` is recommended:** show all three lighter options:

```
About to call local LLM for: [one-line task description]

1. local ([auto-detected model or model from config]) — zero cost, no tool access (recommended)
2. haiku — fast cloud model, has tool access
3. sonnet — full reasoning, multi-step capable

Type 1, 2, or 3. Add "save this config" to persist your choice.
```

**Otherwise (haiku or sonnet recommended):** show the standard two options:

```
About to launch an agent for: [one-line task description]

1. [recommended model] — [one-line justification] (recommended)
2. [next tier up] — [one-line justification]

Type 1 or 2. Add "save this config" to persist your choice.
```

Wait for the user to respond. Accept:
- `1`, `2`, or `3` — use that model
- Any response containing "save this config" — use the chosen model AND write `memory/model-config.md`
- Anything else → use the recommended model from Step 2

**Step 3a — Writing saved config (only when user says "save this config"):**

Write `{{TOOLBOX_PATH}}/memory/model-config.md` with:

```markdown
---
default_model: [chosen model]
local_model: [auto-detected or blank if not applicable]
local_endpoint: http://localhost:11434
saved_by_user: true
---

Model tier guide:
- local: single-shot text tasks with fully-specified input, no tool access, zero cost
- haiku: routine tasks, file search, pattern matching, simple edits
- sonnet: complex reasoning, multi-step implementation, architecture decisions
- opus: highly novel, open-ended, or high-stakes tasks

Local model auto-detected from Ollama if local_model is absent.
Local endpoint defaults to http://localhost:11434 if local_endpoint is absent.
```

### 4. Execute

**If chosen model is `local`:**

Read `{{TOOLBOX_PATH}}/skills/local-llm.md` and follow it, passing the task prompt as PROMPT.
Do NOT invoke the Agent tool.

**If chosen model is `haiku`, `sonnet`, or `opus`:**

Append the following line to the `prompt` parameter string you are about to pass to the Agent tool:

> You have access to superpowers skills via the Skill tool. Use them when relevant — for example, use `superpowers:systematic-debugging` if you encounter a bug, or `superpowers:requesting-code-review` when reviewing code.

Pass `model: [chosen model]` to the `Agent` tool call.
