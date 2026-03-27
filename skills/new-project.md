# /new-project

Entry point for starting any project from scratch.

## When to Use
Run this when starting a new project, repo, service, or tool with no existing context.

## Steps

### 1. Load Global Context and Detect Stack (parallel)

Run both of these at the same time — they have no dependency on each other:

- Read `{{TOOLBOX_PATH}}/memory/MEMORY.md` — global preferences and learnings
- Read `{{TOOLBOX_PATH}}/standards/universal/` — all 5 universal standard files
- Check working directory for stack signals: `package.json`, `go.mod`, `requirements.txt`, `Cargo.toml`, `pyproject.toml`, etc.

### 2. Collect the Idea
Ask the user for input in the most natural way:
- **Freeform**: "Tell me about the project — what is it, what does it do, who uses it?"
- **Structured prompts**: Ask about goal, users, key constraints, success criteria
- **Existing spec**: If the user has a doc, read it first instead of asking

### 3. Confirm Stack

1. If signals found in Step 1 → propose the detected stack and ask to confirm
2. If no signals → ask: "What stack are you using?"
3. If stack directory exists at `{{TOOLBOX_PATH}}/standards/stacks/<stack>/` → load it
4. If stack is new → research current best practices, draft a new standards file, get user approval, save to `{{TOOLBOX_PATH}}/standards/stacks/<new-stack>/`

### 4. Brainstorm + Plan

Invoke `{{TOOLBOX_PATH}}/skills/select-model.md` with task: "Brainstorm and plan a new project."
Use the returned model for both agent calls below.

Invoke `superpowers:brainstorming` using the chosen model to scope and design the project.

If the project has a UI — any frontend, mobile app, dashboard, landing page, or user-facing screens — invoke the `ui-ux-pro-max` skill now to establish the design system (style, color palette, typography) before writing the plan.

Invoke `superpowers:writing-plans` using the chosen model to produce the implementation plan.

### 5. Scaffold the Project
Create the following structure in the project root:

```
<project>/
├── CLAUDE.md                      # Filled from {{TOOLBOX_PATH}}/templates/CLAUDE.md.template
└── .claude/
    └── memory/
        ├── MEMORY.md              # From {{TOOLBOX_PATH}}/templates/memory/MEMORY.md
        ├── project_context.md     # Filled with collected project info
        ├── stack.md               # Chosen stack and why
        ├── architecture.md        # High-level structure from brainstorm
        ├── progress.md            # Phase = "planning", Next = first task
        ├── lessons.md             # Empty to start
        └── decisions/             # Empty — ADRs added as decisions are made
```

Replace all `{{PLACEHOLDER}}` values in CLAUDE.md with actual project details.
Replace `{{TOOLBOX_PATH}}` with the actual toolbox path from `~/.claude/CLAUDE.md`.

### 6. Initialize Git
If no git repo exists:
```bash
git init
git add .
git commit -m "chore: initial scaffold"
```
If git already exists, skip this step.

### 7. Hand Off
Announce: "Project scaffolded. Run /add-feature to start building."
