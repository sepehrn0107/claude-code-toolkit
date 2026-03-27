# /select-model

Invoked before every `Agent` tool call. Determines the right model for the task and injects the superpowers instruction into the agent prompt.

## When to Use

Call this skill immediately before using the `Agent` tool. Pass the task description as context.

## Steps

### 1. Check for Saved Config

Read `{{TOOLBOX_PATH}}/memory/model-config.md`.

- If the file exists → extract `default_model` from the frontmatter, skip to Step 4.
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

Wait for the user to respond. Accept:
- `1` or `2` — use that model
- Any response containing "save this config" — use the chosen model AND write `memory/model-config.md` (see Step 3a)

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

Append the following line to the agent prompt before launching:

> You have access to superpowers skills via the Skill tool. Use them when relevant — for example, use `superpowers:systematic-debugging` if you encounter a bug, or `superpowers:code-reviewer` when reviewing code.

Pass `model: [chosen model]` to the `Agent` tool call.
