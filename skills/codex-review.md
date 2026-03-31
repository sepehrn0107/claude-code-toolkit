---
name: codex-review
description: Delegate a review or testing task to Codex using its /codex:review skill. Passes context as file paths (not content) so Codex reads them directly. Falls back to Claude review with an explicit user notification when Codex is unavailable. Invoke whenever something needs review — Phase 4 Verify, standards-check, and ad-hoc review requests.
---

# /codex-review

Delegate a review or testing task to Codex. Context is passed as file paths so Codex reads them at runtime — never paste file contents into the prompt.

---

## When to use

- Phase 4 (Verify) in `/implement` — confirm implementation before PR
- `/standards-check` — code review pass
- Any time the user says "review", "check this", or "test this"
- After a Codex implementation (`codex-delegate`) to review its own output

---

## Protocol

### Step 0 — Availability check

Read the `CODEX_AVAILABLE` session flag set at startup.

- `true` → proceed to Step 1
- `false` → skip directly to **Fallback**

Do not re-invoke `codex:setup`. The flag is set once per session.

---

### Step 1 — Identify review scope

Determine what needs to be reviewed. Collect the following as **paths only**:

#### 1a. Changed files
Run:
```bash
cd <project-dir> && git diff --name-only main
```
If no base branch exists or context is outside `/implement`, use the file list from the task description.

#### 1b. Ticket state files (when called from `/implement`)
```
.claude/tickets/<ticket-id>/context.md
.claude/tickets/<ticket-id>/plan.md
.claude/tickets/<ticket-id>/implementation.md
```

#### 1c. Applicable standards paths
Derive from the active stack. Pass paths, not summaries:

| Stack             | Standards paths                                                                                                 |
| ----------------- | --------------------------------------------------------------------------------------------------------------- |
| typescript-react  | `{{TOOLBOX_PATH}}/standards/universal/testing.md`, `{{TOOLBOX_PATH}}/standards/stacks/typescript-react/`       |
| typescript-nextjs | same as above + `{{TOOLBOX_PATH}}/standards/stacks/typescript-nextjs/`                                          |
| go                | `{{TOOLBOX_PATH}}/standards/universal/testing.md`, `{{TOOLBOX_PATH}}/standards/stacks/go/`                     |
| python-fastapi    | `{{TOOLBOX_PATH}}/standards/universal/testing.md`, `{{TOOLBOX_PATH}}/standards/stacks/python-fastapi/`         |
| (any stack)       | always include `{{TOOLBOX_PATH}}/standards/universal/error-handling.md`                                         |

---

### Step 2 — Build the Codex review prompt

Construct a prompt that gives Codex file paths to read — not content. Keep under ~600 tokens.

```
Task: Review the following implementation for correctness, test coverage, and standards compliance.

Project directory: <project-dir>

Files to review (read each before commenting):
- <changed-file-path-1>
- <changed-file-path-2>
- ...

Ticket context (read these for intent and plan):
- .claude/tickets/<ticket-id>/context.md
- .claude/tickets/<ticket-id>/plan.md
- .claude/tickets/<ticket-id>/implementation.md

Standards to check against (read these):
- <standards-path-1>
- <standards-path-2>
- ...

Review criteria:
- Do all tests pass and cover the stated behavior?
- Are edge cases from the plan covered?
- Are error paths handled per error-handling standards?
- Are there regressions or missing tests?
- Does implementation match the plan?

Output:
- A checklist: [ ] / [x] for each criterion above
- List of issues found: file:line — description (or "none")
- Verdict: PASS or NEEDS_FIX
- If NEEDS_FIX: list specific files and changes required

<if called from /implement>
When done: write the review verdict to:
  .claude/tickets/<ticket-id>/verification.md

  Format:
  # Verification Report
  ## Checklist
  - [ ] All tests pass
  - [ ] Edge cases covered
  - [ ] Error paths handled
  - [ ] No regressions
  ## Issues found
  <file:line — description; "none" if none>
  ## Verdict
  PASS or NEEDS_FIX
</if>
```

---

### Step 3 — Invoke Codex via the plugin

Launch a `codex:codex-rescue` subagent:

```
Agent(
  subagent_type: "codex:codex-rescue",
  prompt: "<project-dir> + review prompt from Step 2>"
)
```

Pass the project directory explicitly. Do not add `--full-auto` or raw bash flags.

**If the subagent exits with an error:**
- Auth error → remind user to run `codex login` or set `OPENAI_API_KEY`, then fall back
- Any other error → report the error; fall back to Claude review

---

### Step 4 — Parse and present results

Invoke `codex:codex-result-handling` to interpret the subagent output:

```
Skill("codex:codex-result-handling")
```

Present the result as:
- Checklist of criteria with pass/fail
- Issues list (file:line)
- Final verdict: **PASS** or **NEEDS_FIX**

If called from `/implement`: confirm `verification.md` was written and return control to the orchestrator.

---

## Fallback — Claude review

**When to use this path:**
- `CODEX_AVAILABLE` is false
- Codex subagent exits non-zero after one retry
- Auth error and user cannot resolve it

**Notify the user first:**
> Codex is not available. Continuing review with Claude.

Then perform the review directly as Claude:

1. Read the changed files and ticket state files listed in Step 1
2. Read the applicable standards files
3. Check each criterion from Step 2 (tests, edge cases, error paths, regressions, plan alignment)
4. If called from `/implement`: write `verification.md` using the same format
5. Present the same checklist output and verdict

The review quality and output format must be identical to the Codex path — only the reviewer differs.

---

## Failure handling

| Situation                          | Action                                                                                      |
| ---------------------------------- | ------------------------------------------------------------------------------------------- |
| `CODEX_AVAILABLE` is false         | Notify user; fall back to Claude review immediately                                         |
| Auth error from plugin             | Remind user to run `codex login` or set `OPENAI_API_KEY`; fall back for this task          |
| Subagent exits non-zero (other)    | Report error; fall back to Claude review                                                    |
| `verification.md` not written      | Warn user; write it manually from Codex output or Claude review results                     |
| Verdict is NEEDS_FIX               | Return issues list to orchestrator — do not re-run review; let the caller decide next steps |
