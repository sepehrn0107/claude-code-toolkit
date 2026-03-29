# Toolbox

A cross-repo development assistant built on Claude Code. It brings coding standards, memory, and workflow skills to every project — automatically.

When you open any project in Claude Code, the toolbox is already there: it loads your standards, reads project memory so you never repeat context, and guides each phase of development with the right workflow. You run one command; it handles the rest.

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
- `/implement` — add a feature to an existing project (scope → TDD → verify)
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

**Skills** in `skills/` orchestrate the right workflow for each phase of development. They chain together superpowers skills — a suite of workflow skills built into Claude Code (brainstorming, TDD, code review, etc.) — so the right process is always followed.

**Memory** persists context across sessions — project goals, stack decisions, architectural choices, lessons learned. Nothing is re-explained from scratch.

---

## Model Selection

When the toolbox runs a complex workflow step, it dispatches a sub-agent — a focused Claude process with its own context — to handle that step. It automatically picks the most cost-effective model for the task.

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

Every sub-agent launched by the toolbox is instructed to use superpowers skills when relevant. Sub-agents have the `Skill` tool available and will invoke skills like `superpowers:systematic-debugging` or `superpowers:requesting-code-review` without you asking.

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
