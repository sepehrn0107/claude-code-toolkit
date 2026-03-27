# Model Selection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add automatic model selection to toolbox sub-agent launches, with a memory-first policy and a root README covering getting started and the feature.

**Architecture:** A new `skills/select-model.md` skill is invoked by any toolbox skill before launching an agent via the `Agent` tool. It reads saved config from `memory/model-config.md` and silently uses it if present; otherwise it reasons about the task and presents 2 options. Four existing skills are updated to call it. A root `README.md` documents everything for new users.

**Tech Stack:** Markdown skill files, Claude Code Agent tool (accepts `model: haiku | sonnet | opus`), toolbox memory system.

---

### Task 1: Create `skills/select-model.md`

**Files:**
- Create: `skills/select-model.md`

This skill is invoked by other skills immediately before any `Agent` tool call. It reads saved config, or reasons about the task and prompts the user.

- [ ] **Step 1: Create the skill file**

Write `skills/select-model.md` with the following exact content:

````markdown
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
````

- [ ] **Step 2: Verify the file reads correctly**

Read `skills/select-model.md` and confirm:
- Step 1 checks `memory/model-config.md` first
- Step 2 has the full complexity heuristics table
- Step 3 shows the exact prompt format
- Step 3a covers the "save this config" write path
- Step 4 appends the superpowers instruction and passes the model to `Agent`

- [ ] **Step 3: Commit**

```bash
git add skills/select-model.md
git commit -m "feat(skills): add select-model skill for automatic agent model selection"
```

---

### Task 2: Update `skills/add-feature.md`

**Files:**
- Modify: `skills/add-feature.md`

This skill invokes brainstorming (Step 3), TDD (Step 4), and verification (Step 5) via superpowers. These are the agent launch points that need model selection prepended.

- [ ] **Step 1: Read the current file**

Read `skills/add-feature.md` to confirm current content before editing.

- [ ] **Step 2: Add select-model invocation before each agent launch**

Replace the agent-launching steps (3, 4, 5) content so each is preceded by a select-model call. Edit `skills/add-feature.md`:

Change Step 3 from:
```
### 3. Scope the Feature
Invoke `superpowers:brainstorming` to clarify:
```

To:
```
### 3. Scope the Feature
Invoke `{{TOOLBOX_PATH}}/skills/select-model.md` with task: "Scope and design the feature via brainstorming."
Then invoke `superpowers:brainstorming` using the chosen model to clarify:
```

Change Step 4 from:
```
### 4. Implement with TDD
Invoke `superpowers:test-driven-development`.
```

To:
```
### 4. Implement with TDD
Invoke `{{TOOLBOX_PATH}}/skills/select-model.md` with task: "Implement the feature using test-driven development."
Then invoke `superpowers:test-driven-development` using the chosen model.
```

Change Step 5 from:
```
### 5. Verify Before Declaring Done
Invoke `superpowers:verification-before-completion`.
```

To:
```
### 5. Verify Before Declaring Done
Invoke `{{TOOLBOX_PATH}}/skills/select-model.md` with task: "Verify the feature is complete and correct."
Then invoke `superpowers:verification-before-completion` using the chosen model.
```

- [ ] **Step 3: Verify the edit**

Read `skills/add-feature.md` and confirm each of steps 3, 4, 5 now starts with a select-model invocation.

- [ ] **Step 4: Commit**

```bash
git add skills/add-feature.md
git commit -m "feat(skills): invoke select-model before agent launches in add-feature"
```

---

### Task 3: Update `skills/new-project.md`

**Files:**
- Modify: `skills/new-project.md`

Step 4 invokes brainstorming and writing-plans agents.

- [ ] **Step 1: Read the current file**

Read `skills/new-project.md` to confirm current content.

- [ ] **Step 2: Add select-model before Step 4 agent launches**

Change Step 4 from:
```
### 4. Brainstorm + Plan
Invoke `superpowers:brainstorming` to scope and design the project.
Then invoke `superpowers:writing-plans` to produce the implementation plan.
```

To:
```
### 4. Brainstorm + Plan
Invoke `{{TOOLBOX_PATH}}/skills/select-model.md` with task: "Brainstorm and scope a new project."
Then invoke `superpowers:brainstorming` using the chosen model to scope and design the project.

Invoke `{{TOOLBOX_PATH}}/skills/select-model.md` with task: "Write the implementation plan for the project."
Then invoke `superpowers:writing-plans` using the chosen model to produce the implementation plan.
```

- [ ] **Step 3: Verify the edit**

Read `skills/new-project.md` and confirm Step 4 now has two select-model invocations (one before brainstorming, one before writing-plans).

- [ ] **Step 4: Commit**

```bash
git add skills/new-project.md
git commit -m "feat(skills): invoke select-model before agent launches in new-project"
```

---

### Task 4: Update `skills/standards-check.md`

**Files:**
- Modify: `skills/standards-check.md`

Steps 3 and 4 invoke requesting-code-review and code-simplifier.

- [ ] **Step 1: Read the current file**

Read `skills/standards-check.md` to confirm current content.

- [ ] **Step 2: Add select-model before Steps 3 and 4**

Change Step 3 from:
```
### 3. Code Review
Invoke `superpowers:requesting-code-review`.
```

To:
```
### 3. Code Review
Invoke `{{TOOLBOX_PATH}}/skills/select-model.md` with task: "Review code against standards and best practices."
Then invoke `superpowers:requesting-code-review` using the chosen model.
```

Change Step 4 from:
```
### 4. Simplify
Invoke `code-simplifier` for a quality and clarity pass on recently changed code.
```

To:
```
### 4. Simplify
Invoke `{{TOOLBOX_PATH}}/skills/select-model.md` with task: "Simplify and clarify recently changed code."
Then invoke `code-simplifier` using the chosen model for a quality and clarity pass on recently changed code.
```

- [ ] **Step 3: Verify the edit**

Read `skills/standards-check.md` and confirm Steps 3 and 4 each start with a select-model invocation.

- [ ] **Step 4: Commit**

```bash
git add skills/standards-check.md
git commit -m "feat(skills): invoke select-model before agent launches in standards-check"
```

---

### Task 5: Update `skills/retrospective.md`

**Files:**
- Modify: `skills/retrospective.md`

Step 4 launches agents to implement approved changes.

- [ ] **Step 1: Read the current file**

Read `skills/retrospective.md` to confirm current content.

- [ ] **Step 2: Add select-model before the agent launch in Step 4**

In Step 4 ("Implement Approved Changes via PR"), add a select-model invocation at the top of the step, before the branch + commit instructions:

Change the Step 4 header block from:
```
### 4. Implement Approved Changes via PR
For each approved change:

1. Create a branch in the local toolbox clone:
```

To:
```
### 4. Implement Approved Changes via PR
For each approved change:

Invoke `{{TOOLBOX_PATH}}/skills/select-model.md` with task: "Implement an approved toolbox change and open a PR."
Use the chosen model for any agent work in this step.

1. Create a branch in the local toolbox clone:
```

- [ ] **Step 3: Verify the edit**

Read `skills/retrospective.md` and confirm Step 4 now starts with a select-model invocation before the branch creation steps.

- [ ] **Step 4: Commit**

```bash
git add skills/retrospective.md
git commit -m "feat(skills): invoke select-model before agent launches in retrospective"
```

---

### Task 6: Create root `README.md`

**Files:**
- Create: `README.md`

- [ ] **Step 1: Check no README exists**

Run:
```bash
ls README.md 2>/dev/null && echo "exists" || echo "not found"
```
Expected: `not found`. If it exists, read it first before proceeding.

- [ ] **Step 2: Write README.md**

Write `README.md` with the following content:

````markdown
# Toolbox

A cross-repo development assistant built on Claude Code. It brings coding standards, memory, and workflow skills to every project — automatically.

---

## Getting Started

**Requirements:** Claude Code installed, Git.

### 1. Clone the toolbox

```bash
git clone https://github.com/sepehrn0107/toolbox ~/Documents/toolbox
```

### 2. Run setup

Open the toolbox directory in Claude Code and say:

```
Set up the toolbox
```

Claude will write `~/.claude/CLAUDE.md` pointing to your local clone. That's the only manual step.

### 3. Start using it

In any project directory, open Claude Code and run:

- `/new-project` — start a new project from scratch (brainstorm → plan → scaffold)
- `/add-feature` — add a feature to an existing project (scope → TDD → verify)
- `/standards-check` — check code against toolbox standards before a PR
- `/retrospective` — capture learnings and propose toolbox improvements

---

## How It Works

The toolbox is organized as 4 layers:

```
Layer 1 — Global preferences     ~/.claude/CLAUDE.md + toolbox/memory/
Layer 2 — Stack standards        toolbox/standards/
Layer 3 — Project context        <project>/.claude/memory/
Layer 4 — Session context        progress.md (written each session)
```

**Standards** live in `standards/universal/` (applies everywhere) and `standards/stacks/<stack>/` (detected automatically per project).

**Skills** in `skills/` orchestrate the right workflow for each phase of development. They chain together superpowers skills (brainstorming, TDD, code review, etc.) so the right process is always followed.

**Memory** persists context across sessions — project goals, stack decisions, architectural choices, lessons learned. Nothing is re-explained from scratch.

---

## Model Selection

When the toolbox launches a sub-agent, it automatically picks the most cost-effective model for the task.

### Memory-first policy

If you have saved a model preference, it is used silently every time — no prompts.

To save a preference, respond to any model selection prompt with your choice and add **"save this config"**:

```
2 save this config
```

Your preference is stored in `memory/model-config.md` and applied to all future agent launches.

### First-time prompt

When no saved config exists, Claude reasons about the task and presents 2 options:

```
About to launch an agent for: implement the authentication feature

1. sonnet — multi-step implementation warrants stronger reasoning (recommended)
2. opus — maximum capability for complex or novel problems

Type 1 or 2. Add "save this config" to persist your choice.
```

Type `1` or `2`. That's all.

### How models are chosen

| Task type | Default model |
|---|---|
| File search, pattern matching, simple lookups | haiku |
| Code reading, summarization, straightforward edits | haiku |
| Multi-step implementation, TDD, code generation | sonnet |
| Architecture decisions, brainstorming, planning | sonnet |
| Novel problem-solving, highly ambiguous tasks | opus |
| Security review, high-stakes analysis | opus |

When uncertain, sonnet is the default.

### Resetting your saved config

Delete `memory/model-config.md` in the toolbox directory. The prompt will appear again on the next agent launch.

---

## Sub-agents and Superpowers

Every sub-agent launched by the toolbox is instructed to use superpowers skills when relevant. Sub-agents have the `Skill` tool available and will invoke skills like `superpowers:systematic-debugging` or `superpowers:code-reviewer` without you asking.

---

## Contributing

All changes go through GitHub PRs — nothing is committed to `master` directly.

The `/retrospective` skill handles this automatically: it creates a branch, commits the proposed change, and opens a PR for review.

To contribute manually:

```bash
git checkout -b feat/<your-feature>
# make changes
git commit -m "feat: description"
gh pr create
```
````

- [ ] **Step 3: Verify the file**

Read `README.md` and confirm all 6 sections are present: what this is, getting started, how it works, model selection, sub-agents, contributing.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: add root README with getting started guide and model selection docs"
```

---

## Self-Review

**Spec coverage check:**

| Spec requirement | Covered by |
|---|---|
| Memory-first policy (read config, use silently) | Task 1 Step 1 |
| Reason about task complexity | Task 1 Step 2 (heuristics table) |
| Present 2 options with justification | Task 1 Step 3 (exact prompt format) |
| User types 1 or 2 | Task 1 Step 3 |
| "save this config" writes memory/model-config.md | Task 1 Step 3a (exact file content) |
| Inject superpowers instruction into agent prompt | Task 1 Step 4 |
| Update add-feature.md | Task 2 |
| Update new-project.md | Task 3 |
| Update standards-check.md | Task 4 |
| Update retrospective.md | Task 5 |
| Root README with all 6 sections | Task 6 |

**Placeholder scan:** No TBDs, no "implement later", all code/content blocks are complete.

**Consistency check:** `{{TOOLBOX_PATH}}/skills/select-model.md` path used consistently across all skill updates. `memory/model-config.md` frontmatter format matches between Task 1 Step 3a and README model selection section.
