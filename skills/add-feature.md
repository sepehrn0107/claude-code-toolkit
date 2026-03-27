# /add-feature

Entry point for adding anything to an existing project.

## When to Use
Run this when adding a new feature, endpoint, component, or capability to an existing project.

## Steps

### 1. Load Standards (blocking)

Invoke `{{TOOLBOX_PATH}}/skills/load-standards.md` and wait for the confirmation line before continuing.
Do not write or edit any code until standards are loaded and acknowledged.

### 2. Load Project Context
Read Layer 3 — project memory:
- `.claude/memory/MEMORY.md` — index of all memory files
- `.claude/memory/stack.md` — active stack and which standards to apply
- `.claude/memory/architecture.md` — existing structure and key components
- `.claude/memory/progress.md` — current phase and what's been done
- `.claude/memory/decisions/*.md` — any relevant ADRs

### 3. Scope the Feature
Invoke `{{TOOLBOX_PATH}}/skills/select-model.md` with task: "Scope and design the feature via brainstorming."
Then invoke `superpowers:brainstorming` using the chosen model to clarify:
- What exactly is being added?
- Where does it fit in the existing architecture?
- What edge cases or constraints apply?
- Does this decision warrant an ADR?

### 4. Implement with TDD
Invoke `{{TOOLBOX_PATH}}/skills/select-model.md` with task: "Implement the feature using test-driven development."
Then invoke `superpowers:test-driven-development` using the chosen model.
Follow red-green-refactor for all business logic.

### 5. Verify Before Declaring Done
Invoke `{{TOOLBOX_PATH}}/skills/select-model.md` with task: "Verify the feature is complete and correct."
Then invoke `superpowers:verification-before-completion` using the chosen model.
Do not claim the feature is complete until this passes.

### 6. Write ADR (if applicable)
If an architectural decision was made during implementation, write an ADR:

**File:** `.claude/memory/decisions/YYYY-MM-DD-<slug>.md`

```markdown
# Decision: <title>
Date: YYYY-MM-DD

## Context
What situation prompted this decision?

## Decision
What was decided?

## Consequences
What are the trade-offs?

## Alternatives Considered
What else was considered and why rejected?
```

### 7. Update Progress
Update `.claude/memory/progress.md`:
- Move completed feature to "Done"
- Update "Next" to the next planned task

### 8. Prompt for Retrospective
After completing, prompt:
> "Feature complete. Want to run `/retrospective` to capture any learnings before closing out?"
