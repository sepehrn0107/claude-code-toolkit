---
name: auto-switch
description: Mid-session project context switcher. Detects when the user's message implies a shift to a different project and loads that project's memory — without requiring an explicit "switch project" command. For contextual signals (project name mentioned in passing), updates only the session-local state file. For explicit signals ("switch to X", "work on X now"), updates both the session file and the global active-project.md.
---

# /auto-switch

Automatically detects and loads a different project context based on signals in the user's message.

> **Sub-agent guard:** If `WORKSPACE_MODE:` does not appear anywhere in your context, you are
> running as a sub-agent — skip this skill entirely and proceed with your task.

---

## Step 1: Identify the target project

Get the known projects list from the `Projects:` field in the session-start hook output already
in context (e.g. `Projects: gymbro,medianasiri,vault`). Do not scan the workspace directory.

Extract the project name being referenced in the user's message. If the name is not in the known
projects list, do not switch — proceed normally.

---

## Step 2: Classify the signal

Examine the user's message and classify it as one of three types. Stop at the first match.

**Explicit switch** — user intends to change their working project:
- "switch to `<name>`", "work on `<name>` now", "change to `<name>`", "let's work on `<name>`"
- Action: update session file AND global `active-project.md`

**Contextual switch** — user is asking about or referencing another project mid-task:
- "`<name>` repo", "in `<name>`", "for `<name>`", "on `<name>`", "the `<name>` project"
- A file path containing `workspace/<name>/` or `/<name>/.claude/`
- Project name is the subject of a sentence about specific code or behavior
- Action: update session file only (do not touch global file)

**Incidental mention** — project name appears but no context shift is implied:
- Comparisons: "gymbro uses X but medianasiri uses Y"
- Historical or abstract discussion: "when we built gymbro we learned..."
- Project name as an example, not a directive
- Action: no switch — proceed normally

When ambiguous, default to **contextual switch**.

---

## Step 3: Check if already active

Read the current session file:
```bash
SESSION_KEY="${CLAUDE_SESSION_ID:-}"
[ -n "$SESSION_KEY" ] && cat "/tmp/toolbox-session-${SESSION_KEY}.md" 2>/dev/null
```

If the `active:` field matches the target project, skip steps 4–6 silently and answer the user.

---

## Step 4: Load memory

Load the target project's memory files in parallel (skip any that are missing):
- `{{VAULT_PATH}}/02-projects/<target>/memory/project_context.md`
- `{{VAULT_PATH}}/02-projects/<target>/memory/stack.md`
- `{{VAULT_PATH}}/02-projects/<target>/memory/architecture.md`
- `{{VAULT_PATH}}/02-projects/<target>/memory/progress.md`
- `{{VAULT_PATH}}/02-projects/<target>/memory/lessons.md`

---

## Step 5: Write state

Always write the session file:
```bash
SESSION_KEY="${CLAUDE_SESSION_ID:-}"
TODAY=$(date +%Y-%m-%d)
[ -n "$SESSION_KEY" ] && printf "active: <target>\nupdated: %s\n" "$TODAY" > "/tmp/toolbox-session-${SESSION_KEY}.md"
```

For **explicit switches only**, also write the global file:
```
active: <target>
updated: <YYYY-MM-DD>
```
to `{{VAULT_PATH}}/05-areas/claude-memory/active-project.md`

Do NOT write the global file for contextual switches.

---

## Step 6: Output a single notice line

Emit one line before answering the user's message:

- Contextual: `Switching context to <target>.`
- Explicit: `Switched to <target>. Future sessions will open this project.`

Do not ask for confirmation. Do not explain the detection logic.
