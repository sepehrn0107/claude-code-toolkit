# /self-evolve

Enable agent self-evolution using OpenSpace — capture successful task patterns, optimize them over time, auto-repair broken skills, and share to the community.

## Prerequisites (first-time setup)

Before using this skill, ensure OpenSpace is installed and configured:

```bash
# Install OpenSpace
pip install openspace

# Create workspace
mkdir -p ~/.openspace/skills

# Add to shell profile (~/.bashrc or ~/.zshrc):
export OPENSPACE_HOST_SKILL_DIRS=~/.openspace/skills
export OPENSPACE_WORKSPACE=~/.openspace
export OPENSPACE_API_KEY=your_key_here   # optional — enables cloud features
```

The OpenSpace MCP server must be registered in `{{TOOLBOX_PATH}}/.claude/settings.json` under `mcpServers.openspace`. If not yet installed, run "Set up the toolbox" to apply the configuration.

---

## Sub-Commands

---

### `/self-evolve capture`

Run this after completing a successful task to extract the execution pattern as a reusable SKILL.md.

**Steps:**

1. Identify the task that just completed:
   - Type of task (e.g., "debug React component", "set up CI pipeline")
   - Tools used and key decision points
   - Derive a slug: lowercase, hyphen-separated (e.g., `debug-react-component`)

2. Check whether a SKILL.md already exists:
   ```
   ~/.openspace/skills/<slug>/SKILL.md
   ```

3. If **no existing skill**: call OpenSpace MCP tool `execute_task` in **CAPTURED** mode:
   - Pass the task description, tools used, and execution trace
   - This distills the pattern into a new SKILL.md

4. If **existing skill**: call `execute_task` in **DERIVED** mode:
   - Pass the existing skill path and current execution trace
   - This refines the pattern and reduces token overhead for future runs

5. Confirm: `Skill captured: <slug> (v<N>, mode: CAPTURED|DERIVED)`

6. Update `{{TOOLBOX_PATH}}/memory/MEMORY.md` with a pointer to the new/updated skill.

---

### `/self-evolve fix <skill-slug>`

Auto-repair a broken SKILL.md when a skill fails due to changed APIs, tool renames, or degraded behaviour.

**Steps:**

1. Load the broken skill:
   ```
   ~/.openspace/skills/<skill-slug>/SKILL.md
   ```

2. Collect error context:
   - The error message or failure trace from the most recent execution
   - Which tool call or step failed
   - Any relevant environment changes (new API version, changed CLI flag)

3. Call OpenSpace MCP tool `fix_skill`:
   - Pass the skill path and error context
   - OpenSpace analyzes root cause and generates a repair patch

4. Review the proposed patch with the user — do not apply without approval.

5. Once approved, the patched SKILL.md is written back to disk by OpenSpace.

6. Verify the fix by re-running the task's key failing step (dry-run if possible).

7. Confirm: `Skill repaired: <slug> (FIX v<N>)`

---

### `/self-evolve upload <skill-slug>`

Share an evolved skill to the OpenSpace cloud community.

**Requires:** `OPENSPACE_API_KEY` set in environment.

**Steps:**

1. Validate `OPENSPACE_API_KEY` is present:
   ```bash
   echo $OPENSPACE_API_KEY
   ```
   If absent, inform the user and stop.

2. Load `~/.openspace/skills/<skill-slug>/SKILL.md` and display a summary to the user.

3. Ask the user for visibility:
   - `public` — anyone can discover and import
   - `group` — shared within a team
   - `private` — personal cloud backup only

4. Call OpenSpace MCP tool `upload_skill` with the skill path and visibility choice.

5. Confirm: `Uploaded: <slug> → https://open-space.cloud/skills/<id>`

---

### `/self-evolve status`

Audit all evolved skills in the local workspace.

**Steps:**

1. List all SKILL.md files under `~/.openspace/skills/`:
   ```bash
   find ~/.openspace/skills -name "SKILL.md"
   ```

2. For each skill, read the YAML frontmatter and `.skill_id` sidecar to extract:
   - Name, version, origin (CAPTURED / DERIVED / FIXED / IMPORTED)
   - Last evolved date

3. Present as a table:
   ```
   Slug                    | Version | Origin    | Last Evolved
   ----------------------- | ------- | --------- | ------------
   debug-react-component   | v3      | DERIVED   | 2026-03-20
   setup-ci-pipeline       | v1      | CAPTURED  | 2026-03-28
   ```

4. Flag any skills with error history or that have not been used in > 60 days.

---

## When to Use Each Sub-Command

| Situation | Command |
|---|---|
| Just finished a task successfully | `/self-evolve capture` |
| A skill fails with a tool/API error | `/self-evolve fix <slug>` |
| Running `/retrospective` and want to share a pattern | `/self-evolve upload <slug>` |
| Want an overview of evolved skills | `/self-evolve status` |
| Starting a complex task (search first) | `/skill-search` |
