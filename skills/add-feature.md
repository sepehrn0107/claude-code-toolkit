# /add-feature

Entry point for adding anything to an existing project.

> **Prefer `/work-ticket` for complex features** — it delegates all phases to sub-agents and keeps
> the main session context lean. Use `/add-feature` for simple, focused edits that don't warrant
> a full ideate → plan → implement → test → PR workflow.

## When to Use
Run this when adding a new feature, endpoint, component, or capability to an existing project.

## Steps

### 1. Load Standards, Project Context, and Index (parallel)

Run all at the same time — no dependencies between them:

- Invoke `{{TOOLBOX_PATH}}/skills/load-standards.md` and wait for the confirmation line
- Project memory is already loaded from session start. If this is a fresh session
  without a session-start hook, read `.claude/memory/MEMORY.md` and the files it
  indexes (`stack.md`, `architecture.md`, `progress.md`, `decisions/*.md`).
  Otherwise skip — do not re-read files already in context.
- If `.claude/index/README.md` exists, launch a **sub-agent** (haiku model):
  - Task: read `{{TOOLBOX_PATH}}/skills/query-index.md` and follow it
  - Question: "Give me the high-level map: entry points, clusters, and which areas are most active"
  - Return the answer to the parent session — do not read the index files yourself

Do not write or edit any code until `/load-standards` has confirmed.

### 2. Select Model

Invoke `{{TOOLBOX_PATH}}/skills/select-model.md` with task: "Implement a feature: scoping, TDD, and verification."
Use the returned model for all agent calls in Steps 3–5.

### 3. Scope the Feature

Invoke `superpowers:brainstorming` using the chosen model to clarify:
- What exactly is being added?
- Where does it fit in the existing architecture?
- What edge cases or constraints apply?
- Does this decision warrant an ADR?

If the index is available (`.claude/index/` exists), use it during scoping by launching
targeted **sub-agents** (haiku model) via `{{TOOLBOX_PATH}}/skills/query-index.md`:
- "Which cluster(s) does [feature area] belong to?"
- "What files import [affected file]?" — to understand blast radius
- "What calls [key function]?" — to understand call chain impact
Launch each query as a separate sub-agent and use the returned answers to inform scoping.
Do not read index files directly in the main session.

If the feature involves UI work — screens, components, color palette, typography, layout, design system, or any visual styling — invoke the `ui-ux-pro-max` skill before moving to implementation.

### 4. Implement with TDD

Invoke `superpowers:test-driven-development` using the chosen model.
Follow red-green-refactor for all business logic.

### 5. Verify Before Declaring Done

Invoke `superpowers:verification-before-completion` using the chosen model.
Do not claim the feature is complete until this passes.

### 6. Write ADR (if applicable)

If an architectural decision was made during implementation, write an ADR to:
`.claude/memory/decisions/YYYY-MM-DD-<slug>.md`

Use the template at `{{TOOLBOX_PATH}}/templates/ADR.md`.

### 7. Update Progress
Update `.claude/memory/progress.md`:
- Move completed feature to "Done"
- Update "Next" to the next planned task

### 8. Prompt for Retrospective
After completing, prompt:
> "Feature complete. Want to run `/retrospective` to capture any learnings before closing out?"
