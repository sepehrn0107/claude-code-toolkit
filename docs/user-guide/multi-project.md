---
title: "Working Across Projects"
section: user-guide
skills-affected: [project, auto-switch, set-vault]
last-updated: 2026-04-03
---

# Working Across Projects

## Workspace layout

The toolkit expects a workspace folder with `toolbox/` as one subfolder and each of
your project repos as siblings:

```
~/Documents/workspace/
├── toolbox/           ← the toolkit itself
├── my-app/            ← project A
├── api-service/       ← project B
└── ...
```

When you open Claude Code at the workspace root (not inside a project), the session
hook detects this layout and shows a project chooser.

## Switching projects

To load a different project's context in the same session, say:

```
switch project
```

Claude runs `/project` — shows the list of repos in the workspace and loads the
memory files for whichever you choose. The active project pointer in
`vault/05-areas/claude-memory/active-project.md` updates automatically.

## Auto-switching

When you mention a project name from the workspace in a message — "in `my-app`",
"for the `api-service` repo" — and it's not the currently active project, Claude
detects this and runs `/auto-switch` automatically before responding.

## The vault

The vault is where all persistent output lives — global memory, plans, specs, ADRs,
and web cache. It's separate from your project repos so it survives re-clones.

Set the vault path once with `/upgrade-dev`, or change it anytime by saying:

```
set vault
```

Claude runs `/set-vault` — prompts for the new path, updates all config references,
and re-renders the templates. Any existing vault files stay in place.
