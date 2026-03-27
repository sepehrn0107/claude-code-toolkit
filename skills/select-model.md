# /select-model

Invoked before every `Agent` tool call. Determines the right model for the task and injects the superpowers instruction into the agent prompt.

## When to Use

Call this skill immediately before using the `Agent` tool. Pass the task description as context.

> `{{TOOLBOX_PATH}}` is resolved to the actual toolbox path from `~/.claude/CLAUDE.md` — never pass the literal placeholder string to any tool.

## Steps

### 1. Check for Saved Config

Read `{{TOOLBOX_PATH}}/memory/model-config.md`.

- If the file exists → extract `default_model` from the frontmatter, skip to Step 4. If `default_model` is missing or not one of `haiku / sonnet / opus`, treat the file as absent and continue to Step 2.
- If the file does not exist → continue to Step 2.

### 2. Reason About Task Complexity

Evaluate the task description against this table:

| Task type | Model |
|---|---|
| File search, pattern matching, simple lookups | haiku |
| Code reading, summarization, straightforward edits | haiku |
| Multi-step implementation, TDD, code generation | sonnet |
| Architecture decisions, brainstorming, planning | sonnet |
| Novel problem-solving, highly ambiguous tasks | opus |
| Security review, high-stakes analysis | opus |

When uncertain, default to **sonnet**.

### 3. Present 2 Options

Show the user this prompt (filling in the actual task and models):

```
About to launch an agent for: [one-line task description]

1. [recommended model] — [one-line justification] (recommended)
2. [next tier up] — [one-line justification]

Type 1 or 2. Add "save this config" to persist your choice.
```

If `opus` is the recommended model, present `opus` as option 1 and `sonnet` as option 2 (labeled as lighter/cheaper alternative), reversing the usual order.

Wait for the user to respond. Accept:
- `1` or `2` — use that model
- Any response containing "save this config" — use the chosen model AND write `memory/model-config.md`

If the user responds with neither `1` nor `2` (e.g. they type a model name or free text), use the recommended model from Step 2 as the default.

**Step 3a — Writing saved config (only when user says "save this config"):**

Write `{{TOOLBOX_PATH}}/memory/model-config.md` with:

```markdown
---
default_model: [chosen model]
saved_by_user: true
---

Use haiku for routine/search/lookup tasks.
Use sonnet for complex reasoning, multi-step implementation, or architecture decisions.
Use opus for highly novel, open-ended, or high-stakes tasks.
```

### 4. Inject Superpowers and Launch

The chosen model is: the value of `default_model` from Step 1 (saved config path), or the model the user selected in Step 3 (no config path).

Append the following line to the `prompt` parameter string you are about to pass to the `Agent` tool call:

> You have access to superpowers skills via the Skill tool. Use them when relevant — for example, use `superpowers:systematic-debugging` if you encounter a bug, or `superpowers:requesting-code-review` when reviewing code.

Pass `model: [chosen model]` to the `Agent` tool call.
