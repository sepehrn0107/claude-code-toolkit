---
title: "Your First Session"
section: getting-started
skills-affected: [new-project, project, memory-sync]
last-updated: 2026-04-03
---

# Your First Session

## What Claude says when you open a project

If the project has memory files loaded, the session starts with:

```
Project context loaded | Stack: Next.js + TypeScript | Phase: In progress | Next: dashboard route
Memory files are ready. Standards not yet loaded — will auto-load before first code edit.
```

If this is the workspace root (no specific project open), Claude shows a project
chooser instead:

```
Which project are you working on?
  1. my-app
  2. api-service
```

Reply with the number or name to load that project's context.

## Starting a new project

Say:

```
new project
```

Claude runs `/new-project`: asks you a few questions about the stack and purpose,
creates memory files in your vault, sets up git, and writes the initial context.

## Loading an existing project

Open the project folder in Claude Code. If the project has memory files (set up with
`/new-project` previously), they load automatically at session start.

To switch projects without reopening Claude Code: say `"switch project"`.

## The status line

The Claude Code status bar shows live session stats when the toolkit is installed:
directory, model, context usage %, and the 5-hour rate limit counter. This comes from
`~/.claude/statusline-command.js`.

## What happens on the first code edit

Before writing any code, Claude auto-loads the standards for your stack. You'll see:

```
Standards loaded: universal (9 files) + typescript-nextjs (8 files)
```

This happens once per session. After that, all edits proceed without prompting.
