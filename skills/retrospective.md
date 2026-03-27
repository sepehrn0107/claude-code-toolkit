# /retrospective

Capture learnings from a completed feature or project and propose toolbox improvements.

## When to Use
Run this: at project completion, after a significant milestone, or when prompted after a feature.

## Steps

### 1. Load Project Memory
Read all of Layer 3:
- `.claude/memory/project_context.md`
- `.claude/memory/stack.md`
- `.claude/memory/architecture.md`
- `.claude/memory/progress.md`
- `.claude/memory/lessons.md`
- `.claude/memory/decisions/*.md`

### 2. Extract Learnings
Identify from the session or project:
- What worked well (patterns worth repeating)
- What didn't work (patterns to avoid or improve)
- New reusable patterns discovered
- Stack-specific learnings not yet in toolbox standards
- Universal patterns worth promoting to `standards/universal/`

### 3. Propose Toolbox Updates
For each learning, propose one of:
- **Update an existing standard** in `{{TOOLBOX_PATH}}/standards/`
- **Add a new stack standard** in `{{TOOLBOX_PATH}}/standards/stacks/<stack>/`
- **Promote to universal** in `{{TOOLBOX_PATH}}/standards/universal/`
- **Write a new skill** in `{{TOOLBOX_PATH}}/skills/`

Present each proposed change to the user one at a time. Do not make any changes without explicit approval.

### 4. Implement Approved Changes via PR
For each approved change:

1. Create a branch in the local toolbox clone:
   ```bash
   cd {{TOOLBOX_PATH}}
   git checkout -b retro/<slug>-YYYY-MM-DD
   ```
2. Write the content to the appropriate file
3. Commit with a descriptive message:
   ```bash
   git commit -m "docs(<area>): <what changed and why>"
   ```
4. Open a PR to `https://github.com/sepehrn0107/toolbox`:
   - Title: what changed
   - Body: what was learned, from which project, why it's being proposed

### 5. Update Global Memory
Write a summary of the session's key learnings to `{{TOOLBOX_PATH}}/memory/MEMORY.md`.
This is personal memory — it does NOT require a PR.

Format each entry as a new memory file in `{{TOOLBOX_PATH}}/memory/` and add a pointer to `MEMORY.md`.

### 6. Mark Progress
Update `.claude/memory/progress.md`:
- Note retrospective was run
- Note what was proposed or merged to toolbox
