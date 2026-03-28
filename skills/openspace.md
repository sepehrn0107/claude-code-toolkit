# /openspace

Run a self-organized, collaborative Open Space Technology (OST) session around a theme or problem.

## What This Is

Open Space Technology is a facilitation format where participants set the agenda themselves.
It works best for complex problems with no single right answer, cross-cutting concerns,
or situations where diverse perspectives matter.

Key principles:
- **Whoever shows up** (as context, ideas, or constraints) **are the right inputs**
- **Whatever emerges** is the only thing that could have emerged
- **When it starts, it starts** — no waiting for perfect conditions
- **When it's over, it's over** — output matters more than process
- **Law of Two Feet**: if a topic isn't generating value, move to one that is

## When to Use

Run this when you need to:
- Explore a large or fuzzy problem across multiple angles simultaneously
- Run a team retrospective in open, self-organized format
- Generate and vet ideas before committing to an approach
- Surface hidden constraints, risks, or opportunities in a domain
- Facilitate a knowledge-sharing session across projects or stacks

Do NOT use this as a substitute for `/add-feature` (implementation) or `/retrospective` (solo close-out).

## Steps

### 1. Define the Theme

Ask the user:
> "What is the central question or challenge this session is exploring?"

The theme should be:
- Open-ended (not yes/no)
- Genuinely uncertain (not already decided)
- Worth 30–120 minutes of exploration

Record the theme. It anchors the whole session.

### 2. Open the Marketplace

Ask the user to generate topics — questions, problems, or ideas they want to explore
within the theme. Each topic becomes a "session" to investigate.

If the user provides fewer than 3 topics, generate additional ones by:
- Reading `.claude/memory/` to surface known pain points or open questions
- Reading `{{TOOLBOX_PATH}}/memory/MEMORY.md` for recurring cross-project themes
- Asking: "What questions are you afraid to ask? What assumptions haven't been tested?"

Display the marketplace board:

```
MARKETPLACE — [Theme]
─────────────────────
[A] [Topic title]
[B] [Topic title]
[C] [Topic title]
...
```

Ask the user to add, remove, or rename any topics before proceeding.

### 3. Select Model

Invoke `{{TOOLBOX_PATH}}/skills/select-model.md` with task:
"Run a multi-topic open space exploration session with synthesis."

Use the returned model for all sub-agent work in Step 4.

### 4. Explore Topics (Parallel)

For each topic, launch a **sub-agent** using the chosen model. Each sub-agent:

1. Reads the topic title and the session theme
2. If `.claude/index/README.md` exists, reads `{{TOOLBOX_PATH}}/skills/query-index.md`
   and uses it to answer: "Which parts of the codebase are relevant to [topic]?"
3. Explores the topic freely — asks clarifying questions internally, surfaces tradeoffs,
   identifies risks, proposes directions
4. Returns a structured summary:
   ```
   Topic: [title]
   Key insights: (3–5 bullets)
   Open questions: (what remains uncertain)
   Proposed actions: (concrete next steps, if any)
   Toolbox impact: (anything worth adding to standards or memory)
   ```

Run all topic sub-agents in parallel. Do not wait for one to finish before starting others.

### 5. Synthesize the Session

After all sub-agents return, synthesize across topics:

- What patterns appeared in multiple discussions?
- What tensions or contradictions emerged?
- What is the most important insight from the session?
- What decisions, if any, can be made now?

Present the synthesis clearly before moving to outputs.

### 6. Capture Outputs

#### 6a. Actions
For any concrete actions surfaced, ask the user to confirm them and add to
`.claude/memory/progress.md` under "Next".

#### 6b. Decisions
If an architectural or design decision was made, write an ADR:
`.claude/memory/decisions/YYYY-MM-DD-<slug>.md`
Use `{{TOOLBOX_PATH}}/templates/ADR.md`.

#### 6c. Toolbox Improvements
For anything marked "Toolbox impact" in any topic summary:
- Propose the specific change (new standard, updated skill, memory entry)
- Ask for approval before writing
- If approved, follow the same PR process as `/retrospective` Step 4

### 7. Update Memory

Write a session summary to `{{TOOLBOX_PATH}}/memory/openspace_lessons.md`:

```markdown
## [YYYY-MM-DD] — [Theme]

**Topics explored:** [comma-separated list]
**Key synthesis:** [2–3 sentences]
**Actions taken:** [list]
**Toolbox changes proposed:** [list or "none"]
```

Then update `{{TOOLBOX_PATH}}/memory/MEMORY.md` to point at `openspace_lessons.md`
if not already linked.

### 8. Close

Announce:
> "Open space session complete. [N] topics explored. [N] actions captured."

Prompt:
> "Want to run `/retrospective` to capture any deeper learnings before closing?"
