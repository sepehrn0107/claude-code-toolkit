# /skill-search

Search OpenSpace for pre-evolved skill patterns before attempting a complex or repeated task. Avoids reinventing solutions that have already been refined across executions.

## When to Use

Run this before starting any task that:
- Has been done before in a different project (repeated pattern)
- Involves external tools or APIs (skills evolve as APIs change)
- Is complex enough that a refined execution plan would save significant effort
- The user explicitly asks: "has anyone done X", "find a skill for X", "search for skill"

## Steps

### 1. Formulate a search query

Distil the task into 1–2 sentences describing:
- What needs to be accomplished (outcome)
- Key tools or technologies involved

Example: `"Set up a GitHub Actions CI pipeline for a Python project with pytest and coverage reporting"`

### 2. Search local skills first

Check `~/.openspace/skills/` for any skill whose name or description closely matches:
```bash
ls ~/.openspace/skills/
```
If a strong local match exists, present it immediately (skip cloud search unless the user wants more options).

### 3. Search OpenSpace (local + cloud)

Call OpenSpace MCP tool `search_skills` with the query string.

This searches:
- Local `~/.openspace/skills/` workspace
- OpenSpace cloud community registry (if `OPENSPACE_API_KEY` is set)

### 4. Evaluate results

For each result returned:
- Show: skill name, description, origin (CAPTURED/DERIVED/IMPORTED), version, quality score if available
- Highlight any skills marked as DERIVED (these have been optimized across multiple executions)

### 5. Decide with the user

Present the top match (if any) and ask:

> "Found: **<skill-name>** — <description>. Use this as the starting pattern, or proceed fresh?"

- **Use skill**: load the SKILL.md, follow its instructions as the execution plan for this task
- **Proceed fresh**: continue with the standard toolbox skill, then run `/self-evolve capture` after completion to add the new pattern

### 6. If no match found

Inform the user:
> "No existing skill found for this task. Proceed, then run `/self-evolve capture` afterward to save the pattern for future use."

Continue with the appropriate toolbox skill (`/add-feature`, `/new-project`, etc.).
