---
name: codex-delegate
description: Hand off a coding task to OpenAI Codex via the codex-plugin-cc with accurate context, availability check, and fallback to direct Claude implementation
---

# /codex-delegate

Delegate a focused coding task to Codex via the `codex-plugin-cc` plugin. Codex runs autonomously in the target directory and edits files directly. Claude provides accurate context, verifies the result, and falls back to direct implementation if Codex is unavailable.

---

## When to use

- Task is well-scoped (fix X, refactor Y, implement Z in specific files)
- You have a clear target directory and know which files are involved
- You want Codex to handle the mechanical implementation while Claude handles planning and verification
- Called automatically from `/implement` Phase 3 when Codex is available

---

## Protocol

### Step 0 — Availability check

Read the `CODEX_AVAILABLE` session flag set during Session Start (from `codex:setup`).

- If `CODEX_AVAILABLE` is true → proceed to Step 1
- If `CODEX_AVAILABLE` is false → skip to **Fallback** immediately

Do not re-invoke `codex:setup` here. The check runs once per session at startup.

---

### Step 1 — Identify the target directory

- Use the active project path from memory (`project_context.md`) or the current working directory
- Confirm the directory is a git repo:
  ```bash
  cd <project-dir> && git rev-parse --is-inside-work-tree 2>/dev/null || echo NOT_GIT
  ```
- If not a git repo: warn the user (diff verification won't work), but proceed if they confirm

---

### Step 2 — Build the context package

Collect all of the following before writing the Codex prompt. Do NOT pass full file contents — pass paths, summaries, and constraints.

#### 2a. Touched files

- If called from `/implement`: read the `## Files` section of `.claude/tickets/<ticket-id>/plan.md`
- Otherwise: identify files from the task description and a quick Glob/Grep

#### 2b. Applicable standards

Derive from the stack in `context.md` or `stack.md`:

| Stack             | Standards paths to summarize                                                                                  |
| ----------------- | ------------------------------------------------------------------------------------------------------------- |
| typescript-react  | `standards/universal/architecture.md`, `standards/universal/testing.md`, `standards/stacks/typescript-react/` |
| typescript-nextjs | same as above + `standards/stacks/typescript-nextjs/`                                                         |
| go                | `standards/universal/architecture.md`, `standards/universal/testing.md`, `standards/stacks/go/`               |
| python-fastapi    | `standards/universal/architecture.md`, `standards/universal/testing.md`, `standards/stacks/python-fastapi/`   |
| drizzle-postgres  | `standards/stacks/drizzle-postgres/`                                                                          |
| (any stack)       | always include `standards/universal/error-handling.md`                                                        |

Do not dump full standard files into the prompt. Extract the key rules as a short bullet list (≤20 bullets).

#### 2c. Implement phase context (when called from `/implement`)

Include these constraints from Phase 3:

- Component name being implemented
- TDD requirement: write failing tests first, follow red-green-refactor
- Do not change public APIs or function signatures unless the plan explicitly says so
- Append an IMPLEMENTATION SUMMARY to `.claude/tickets/<ticket-id>/implementation.md` when done

---

### Step 3 — Build the Codex prompt

Before writing the final prompt, invoke `codex:gpt-5-4-prompting` to get guidance on structuring the task, constraint ordering, and output instructions for the Codex runtime. Apply that guidance when composing the prompt below.

Template:

```
Task: <one clear sentence>

Files to create or modify:
- <path>: <what to do>
- <path>: <what to do>

Standards to follow:
- <bullet from 2b>
- <bullet from 2b>

TDD: Write failing tests first. Follow red-green-refactor for all business logic.

Do not:
- Change public API signatures unless listed above
- Add new dependencies without approval
- Modify files not listed above

<if called from /implement>
When done: append an IMPLEMENTATION SUMMARY block to .claude/tickets/<ticket-id>/implementation.md
Format:
# Implementation Summary — <component>
## Files created or modified
<list>
## Tests written
<list>
## Deviations from plan
<list or "none">
## New risks discovered
<list or "none">
</if>
```

Keep the full prompt under ~800 tokens. If the task is too large to express concisely, break it into two sequential codex-delegate calls.

---

### Step 4 — Invoke Codex via the plugin

Launch a `codex:rescue` subagent using the Agent tool:

```
Agent(
  subagent_type: "codex:codex-rescue",
  prompt: "<full context package: project dir + task prompt from Step 3>"
)
```

Pass the project directory explicitly in the prompt so the subagent knows where to operate. The plugin runtime manages sandboxing, approval mode, and file access — do not add `--full-auto` or bash flags.

**If the subagent exits with an error:**

- Auth error → remind the user to run `codex login` or set `OPENAI_API_KEY`, then fall back
- Any other error → report the error, fall back to direct Claude implementation

---

### Step 5 — Parse results

Invoke `codex:codex-result-handling` to interpret the subagent's output consistently:

```
Skill("codex:codex-result-handling")
```

This ensures file change summaries, warnings, and implementation notes are presented in a standard format regardless of how Codex returns its output.

---

### Step 6 — Verify changes

```bash
cd <project-dir> && git diff
```

Check:

- Changes match the task and listed files
- No unintended files modified
- No new dependencies added without approval
- Tests exist for new business logic (if TDD was required)

If anything looks wrong: flag it to the user before continuing. Do not commit.

---

### Step 7 — Report

Summarize what Codex changed: file name + one-line description per file. If called from `/implement`, confirm the implementation.md summary was appended and return control to the implement orchestrator.

---

## Fallback — direct Claude implementation

Use this when:

- `codex:setup` reports CLI not installed, not in PATH, or not authenticated
- Codex subagent exits with an auth error
- Codex subagent exits non-zero after one retry
- User explicitly says to skip Codex

**Action:** implement the task directly using Claude, following the same context package (touched files, standards, TDD requirement) built in Step 2. If called from `/implement` Phase 3, follow the Phase 3c sub-agent prompt exactly as written in `implement.md`.

Do not tell the user "Codex failed" unless the task itself fails — just proceed with direct implementation silently.

---

## Failure handling

| Situation                         | Action                                                                                           |
| --------------------------------- | ------------------------------------------------------------------------------------------------ |
| `codex:setup` reports unavailable | Fall back immediately; do not mention Codex to user                                              |
| Auth error from plugin            | Remind user to run `codex login` or set `OPENAI_API_KEY`; fall back for this task               |
| Subagent exits non-zero (other)   | Report error; fall back                                                                          |
| `git diff` shows no changes       | Warn user — Codex may have misunderstood; retry once with a more specific prompt, then fall back |
| Changes in unexpected files       | Flag to user; do not commit                                                                      |

---

## First-time setup

1. Install the plugin: follow the instructions at https://github.com/openai/codex-plugin-cc
2. Run `codex` in a terminal — it will open a browser for OpenAI OAuth (one-time)
3. Alternative: set `OPENAI_API_KEY` as an environment variable for API key auth
4. Verify readiness: invoke `codex:setup` — it will confirm the CLI is ready and auth is valid

---

## Notes

- The plugin provides a runtime bridge between Claude Code and the Codex CLI — always use the plugin skills rather than invoking the CLI directly via bash.
- Codex works best on focused, well-specified tasks. For large multi-file refactors, break into smaller sequential delegate calls.
- Always verify with `git diff` before committing — Codex may make stylistic changes beyond the stated task.
- The availability check (`codex:setup`) runs every time — there is no persistent "Codex is available" state carried across calls.
