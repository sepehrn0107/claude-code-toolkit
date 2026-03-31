---
name: implement
description: Full lifecycle skill for implementing any feature, endpoint, component, or capability in an existing project. Use this whenever the user says "add [X]", "implement [X]", "build [X]", "create a feature", "work on a ticket", or any similar intent to introduce new functionality. This orchestrates ideation → planning → TDD implementation → verification → PR via sub-agents. This is the primary entry point for all non-trivial development work — default to this over ad-hoc coding whenever the task has more than one moving part.
---

# /implement

Primary entry point for adding any feature, endpoint, component, or capability to an existing project.
Each phase runs as a sub-agent and writes its output to a ticket state file.
The main session is an orchestrator only — it holds file paths, not content.

## Ticket State Files

Each phase writes its output to `.claude/tickets/<ticket-id>/`:

```
.claude/tickets/<ticket-id>/
  context.md        ← Phase 0: intake summary
  ideation.md       ← Phase 1: IDEATION REPORT
  plan.md           ← Phase 2: PLAN
  implementation.md ← Phase 3: IMPLEMENTATION SUMMARY (appended per component)
  verification.md   ← Phase 4: VERIFICATION REPORT
  pr.md             ← Phase 5: PR_SUMMARY + URL
```

Ticket ID is derived from the feature name or request (e.g. `add-dark-mode`, `fix-auth-flow`).
If `.claude/tickets/<ticket-id>/` already contains state files, resume from the latest phase.

---

## Phase 0 — Intake (main session, no sub-agent)

1. Derive `TICKET_ID` from the feature name/request provided by the user.
   Create `.claude/tickets/<ticket-id>/` if it does not exist.

2. Read in parallel — do not load full standards files:
   - `{{TOOLBOX_PATH}}/standards/universal/DIGEST.md`
   - `.claude/memory/MEMORY.md` if present and not already loaded this session

3. Extract and hold only these values in working memory:
   - `TICKET`: one-paragraph description of the feature
   - `STACK`: active stack name (from `.claude/memory/stack.md` or inferred)
   - `INDEX_AVAILABLE`: true if `.claude/index/README.md` exists, otherwise false
   - `PROJECT_SUMMARY`: one line per memory file (project_context, stack, architecture, progress)
     — do NOT re-read full memory files if session start already loaded them

4. Write `context.md`:
   ```
   # Ticket Context

   ## Ticket
   <one-paragraph description>

   ## Stack
   <stack name>

   ## Index available
   <true/false>

   ## Project summary
   - project_context: <one line>
   - stack: <one line>
   - architecture: <one line>
   - progress: <one line>
   ```

5. Announce: "Feature understood. Starting Phase 1 — Ideate."

---

## Phase 1 — Ideate

Goal: understand the problem space, clarify scope, surface unknowns.

Invoke `{{TOOLBOX_PATH}}/skills/select-model.md` with task: "Brainstorm a feature: ideation and scoping."

Launch a sub-agent with this prompt:

```
ROLE: You are a senior engineer doing ideation for a feature.

INPUT — read this file first:
  .claude/tickets/<ticket-id>/context.md

FETCH RULE — if you need to read any external URL, do not call WebFetch directly. Run:
  python {{TOOLBOX_PATH}}/tools/crawl4ai/fetch.py --url "<URL>"
  Read stdout as page content. Fall back to WebFetch only if stderr says "not reachable".

If INDEX_AVAILABLE is true:
  - Read {{TOOLBOX_PATH}}/skills/query-index.md
  - Launch sub-agents (haiku model) for:
    - "Which cluster(s) does [feature area] belong to?"
    - "What files are relevant to [feature area]?"

YOUR TASK:
  Invoke superpowers:brainstorming to explore:
  - What exactly is being added or changed?
  - Where does it fit in the existing architecture?
  - What edge cases, constraints, or risks apply?
  - What is the minimal viable scope? What is explicitly out of scope?
  - Does this decision warrant an ADR?

OUTPUT — write a structured IDEATION REPORT to:
  .claude/tickets/<ticket-id>/ideation.md

  Format:
  # Ideation Report
  ## Summary
  <2-3 sentences>
  ## Key design questions answered
  <bullet list>
  ## Risks and edge cases
  <bullet list>
  ## Recommended scope
  - In scope: <list>
  - Out of scope: <list>
  ## Files/areas likely to be touched
  <list>
  ## ADR needed?
  <yes/no + one-line reason>

Write the file, then return only: "Phase 1 complete. Wrote ideation.md."
Do not return the full report content — the main session will read the file.
```

After the sub-agent completes, announce: "Phase 1 complete. Starting Phase 2 — Plan."

---

## Phase 2 — Plan

Goal: produce a concrete, file-level implementation plan.

Invoke `{{TOOLBOX_PATH}}/skills/select-model.md` with task: "Architecture planning and implementation design."

Launch a sub-agent with this prompt:

```
ROLE: You are a senior architect producing an implementation plan.

INPUT — read these files first:
  .claude/tickets/<ticket-id>/context.md
  .claude/tickets/<ticket-id>/ideation.md

FETCH RULE — if you need to read any external URL, do not call WebFetch directly. Run:
  python {{TOOLBOX_PATH}}/tools/crawl4ai/fetch.py --url "<URL>"
  Read stdout as page content. Fall back to WebFetch only if stderr says "not reachable".

STANDARDS — read these files in full before planning:
  {{TOOLBOX_PATH}}/standards/universal/architecture.md
  {{TOOLBOX_PATH}}/standards/universal/security.md
  {{TOOLBOX_PATH}}/standards/universal/documentation.md

If INDEX_AVAILABLE is true (check context.md):
  - Read {{TOOLBOX_PATH}}/skills/query-index.md
  - Launch sub-agents (haiku) for:
    - "What calls [key function from ideation]?"
    - "What are the direct importers of [affected files from ideation]?"

YOUR TASK:
  Invoke superpowers:writing-plans to produce a file-level implementation plan.

OUTPUT — write a structured PLAN to:
  .claude/tickets/<ticket-id>/plan.md

  Format:
  # Plan
  ## Implementation steps
  <numbered list — each step: file, change, why>
  ## Test strategy
  <what tests to write, in what order>
  ## Files
  - New: <list>
  - Modified: <list>
  ## Component breakdown
  <if 3+ distinct clusters or 8+ files: list components for parallel impl sub-agents>
  ## ADR draft
  <if ideation flagged one needed; otherwise omit>
  ## Risks and mitigations
  <bullet list>

Write the file, then return only: "Phase 2 complete. Wrote plan.md."
```

After the sub-agent completes, announce: "Phase 2 complete. Starting Phase 3 — Implement."

---

## Phase 3 — Implement

Goal: TDD implementation of the plan.

### 3a. Standards gate (main session)

Set the standards-loaded flag so the PreToolUse hook allows edits in this session:

```bash
touch "/tmp/toolbox-standards-loaded-${CLAUDE_SESSION_ID:-$(pwd | md5sum | cut -c1-8)}"
```

Run silently via the Bash tool.

### 3b. Classify and route components

Read `.claude/tickets/<ticket-id>/plan.md` (the "Component breakdown" section only).

For each component, classify it before deciding how to implement it:

- **simple**: single file, estimated ≤ ~100 LOC, no cross-file dependencies
- **complex**: multiple files, cross-cutting logic, or requires standards compliance at write time

**For simple components** — use the local LLM + haiku review hybrid:

1. Invoke `{{TOOLBOX_PATH}}/skills/select-model.md` → this will detect Tier 0 and call `local-llm.md` automatically
2. Build a focused prompt: function/class signature + description + constraints (< 500 tokens total — do not paste full files)
3. Run `python3 {{TOOLBOX_PATH}}/tools/local-llm/call.py --task-type coding --prompt "<prompt>"` via Bash tool
4. If exit code 0: take stdout as the draft code
5. If exit code 1: skip to the complex path (haiku sub-agent handles the full task)
6. Launch a haiku sub-agent to: apply standards compliance, write tests, and append the IMPLEMENTATION SUMMARY to `implementation.md`

**For complex components** — use the standard sub-agent (Step 3c below) unchanged.

If the plan has no component breakdown: treat the entire feature as a single component and apply the classification above.

### Write contention note
When multiple implementation sub-agents run in parallel, they may conflict if all try to append
to `implementation.md` simultaneously. If an agent reports being denied write access to
`implementation.md`, the orchestrator (main session) should append that agent's summary manually
after it completes — ask the agent to return the summary in its output, or read the agent's last
message and write the section directly.

### 3c. For each **complex** component, use this sub-agent prompt:

```
ROLE: You are a senior engineer implementing a component using TDD.

INPUT — read these files first:
  .claude/tickets/<ticket-id>/context.md
  .claude/tickets/<ticket-id>/plan.md

YOUR COMPONENT: <component name / file group from plan>

FETCH RULE — if you need to read any external URL, do not call WebFetch directly. Run:
  python {{TOOLBOX_PATH}}/tools/crawl4ai/fetch.py --url "<URL>"
  Read stdout as page content. Fall back to WebFetch only if stderr says "not reachable".

STANDARDS — read these files in full before writing any code:
  {{TOOLBOX_PATH}}/standards/universal/architecture.md
  {{TOOLBOX_PATH}}/standards/universal/testing.md
  {{TOOLBOX_PATH}}/standards/universal/error-handling.md
  {{TOOLBOX_PATH}}/standards/universal/observability.md
  <if stack standards exist: {{TOOLBOX_PATH}}/standards/stacks/<stack>/>

STEP 1: Invoke {{TOOLBOX_PATH}}/skills/load-standards.md — wait for the confirmation
line before writing any code.

STEP 2: Invoke superpowers:test-driven-development.
Follow red-green-refactor for all business logic. Write failing tests first.

OUTPUT — append a structured IMPLEMENTATION SUMMARY to:
  .claude/tickets/<ticket-id>/implementation.md

  Format:
  # Implementation Summary — <component name>
  ## Files created or modified
  <list with one-line description per file>
  ## Tests written
  <list of test names or descriptions>
  ## Deviations from plan
  <any changes from the plan and why; "none" if none>
  ## New risks discovered
  <bullet list; "none" if none>

Append to the file (do not overwrite), then return only:
"Phase 3 complete for <component>. Appended to implementation.md."
```

After all components complete, announce: "Phase 3 complete. Starting Phase 4 — Verify."

---

## Phase 4 — Verify

Goal: confirm the implementation is correct and complete before PR.

Invoke `{{TOOLBOX_PATH}}/skills/select-model.md` with task: "Verification and quality check of implementation."

Launch a sub-agent with this prompt:

```
ROLE: You are a QA engineer verifying an implementation before PR.

INPUT — read these files first:
  .claude/tickets/<ticket-id>/context.md
  .claude/tickets/<ticket-id>/plan.md
  .claude/tickets/<ticket-id>/implementation.md

FETCH RULE — if you need to read any external URL, do not call WebFetch directly. Run:
  python {{TOOLBOX_PATH}}/tools/crawl4ai/fetch.py --url "<URL>"
  Read stdout as page content. Fall back to WebFetch only if stderr says "not reachable".

STANDARDS — read these files before verifying:
  {{TOOLBOX_PATH}}/standards/universal/testing.md
  {{TOOLBOX_PATH}}/standards/universal/error-handling.md

YOUR TASK:
  Invoke superpowers:verification-before-completion. Check:
  - Do all tests pass?
  - Are edge cases from the ideation report covered?
  - Are error paths handled correctly per error-handling standards?
  - Are there any obvious regressions?

OUTPUT — write a structured VERIFICATION REPORT to:
  .claude/tickets/<ticket-id>/verification.md

  Format:
  # Verification Report
  ## Checklist
  - [ ] All tests pass
  - [ ] Edge cases covered
  - [ ] Error paths handled
  - [ ] No regressions
  ## Issues found
  <list with file + description; "none" if none>
  ## Verdict
  PASS or NEEDS_FIX

Write the file, then return only: "Phase 4 complete. Verdict: <PASS|NEEDS_FIX>."
```

- If `NEEDS_FIX`: re-enter Phase 3 targeting only the specific issues. Limit to 2 retry loops.
- If `PASS`: announce "Phase 4 complete. Starting Phase 5 — PR."

---

## Phase 5 — PR

Goal: full standards check, commit, and open PR.

Invoke `{{TOOLBOX_PATH}}/skills/select-model.md` with task: "Code review, standards check, and PR creation."

Launch a sub-agent with this prompt:

```
ROLE: You are a senior engineer preparing a PR for review.

INPUT — read these files first:
  .claude/tickets/<ticket-id>/context.md
  .claude/tickets/<ticket-id>/implementation.md
  .claude/tickets/<ticket-id>/verification.md

STANDARDS — read all of these in full:
  {{TOOLBOX_PATH}}/standards/universal/architecture.md
  {{TOOLBOX_PATH}}/standards/universal/security.md
  {{TOOLBOX_PATH}}/standards/universal/git.md
  {{TOOLBOX_PATH}}/standards/universal/testing.md
  {{TOOLBOX_PATH}}/standards/universal/documentation.md
  {{TOOLBOX_PATH}}/standards/universal/error-handling.md
  {{TOOLBOX_PATH}}/standards/universal/code-review.md
  {{TOOLBOX_PATH}}/standards/universal/observability.md
  <if stack standards exist: {{TOOLBOX_PATH}}/standards/stacks/<stack>/>

STEP 1: Run `git diff --name-only main` to get the list of changed files.
STEP 2: Review each changed file against the standards above.
STEP 3: Invoke superpowers:requesting-code-review.
STEP 4: Run /standards-check checklist: architecture, security, git, testing, docs.
STEP 5: If the plan included an ADR: write it to
  .claude/memory/decisions/YYYY-MM-DD-<slug>.md
  using the template at {{TOOLBOX_PATH}}/templates/ADR.md
STEP 6: Update .claude/memory/progress.md — move feature to Done, update Next.
STEP 7: Commit all changes following git standards (conventional commits).
STEP 8: Open PR with the GitHub MCP tools. Include in body:
  - What: summary of changes
  - Why: the feature description (from context.md)
  - How: key decisions from plan.md
  - Tests: what was tested

OUTPUT — write a structured PR_SUMMARY to:
  .claude/tickets/<ticket-id>/pr.md

  Format:
  # PR Summary
  ## PR URL
  <url>
  ## Standards check
  - architecture: pass/fail
  - security: pass/fail
  - git: pass/fail
  - testing: pass/fail
  - documentation: pass/fail
  ## Blocking issues
  <list; "none" if none>

Write the file, then return the PR URL and verdict.
```

- If blocking issues found: return to Phase 3 or 4 as appropriate.
- Otherwise: announce the PR URL and prompt:
  > "Feature complete. PR: [URL]. Want to run `/retrospective` to capture any learnings?"
