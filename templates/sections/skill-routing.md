## Automatic Skill Routing

Detect user intent from the first message and route automatically — do not wait to be asked:

| User says…                                                              | Auto-trigger                          |
|-------------------------------------------------------------------------|---------------------------------------|
| "add [X]", "implement [X]", "build [X]", "create [feature]", "work on [ticket]", "ticket [X]" | Read and follow `/implement` skill  |
| "brainstorm [X]", "plan mode", "let's plan", "think through [X]", "help me plan", "/brainstorm" | Invoke `superpowers:brainstorming` skill |
| "fix [X]", "debug [X]", "something is broken", "not working"            | Invoke `superpowers:systematic-debugging` |
| "check this", "review [X]", "ready to merge", "before PR"              | Read and follow `/standards-check`    |
| "new project", "starting fresh", "scaffold this"                        | Read and follow `/new-project`        |
| "switch project", "change project", "work on [repo]"                    | Read and follow `/project` skill      |
| Message references a known project name (from the `Projects:` list in hook output) in a contextual way — "in `<name>`", "for `<name>`", "the `<name>` repo", a path containing `workspace/<name>/`, or an explicit "switch to `<name>`" / "work on `<name>` now" — AND that project is not the currently active one AND `WORKSPACE_MODE:` is present in context (not a sub-agent) | Read and follow `/auto-switch` skill |
| "create skill", "make a skill", "new skill", "improve skill", "edit skill", "optimize skill", "skill for [X]" | Invoke `skill-creator:skill-creator` system skill |
| "push to git", "push this", "commit and push", "push my changes", "send to github", "open a PR", "create a PR", "push these changes", "ship this", "just push it", "lets push" | Read and follow `/git-push` skill |
| "upgrade toolbox", "update toolbox", "run upgrade", "/upgrade"               | Read and follow `/upgrade` skill      |
| "upgrade-dev", "/upgrade-dev", "apply template", "sync live install", "render template" | Read and follow `/upgrade-dev` skill |
| Claude is about to use `WebFetch` or follow a URL to read page content  | **BLOCKING REQUIREMENT**: Read and follow `/web-fetch` skill BEFORE calling `WebFetch`. Never call the `WebFetch` tool directly — always route through `/web-fetch` first. |
| Claude is about to run multiple git commands (status, log, diff, branch) | Read and follow `/git-ctx` skill     |
| Claude is about to read `git diff` to understand what changed or draft a commit/PR | Read and follow `/diff-summary` skill |
| Claude needs to read one function, class, or section from a file >100 lines | Read and follow `/read-section` skill |
| Claude needs package version, types, license, or popularity for an npm/PyPI package | Read and follow `/pkg-info` skill  |
| Claude needs runtime versions, running ports, Docker state, or .env presence | Read and follow `/env-check` skill  |
| Claude is about to search code with Grep or search tools               | Read and follow `/grep` skill         |
| Claude is about to write or append to any memory file                  | Read and follow `/memory-sync` skill  |
| "delegate to codex", "let codex handle", "use codex for", "hand off to codex" | Read and follow `/codex-delegate` skill |
| "review with codex", "codex review", "let codex review", "delegate review" | Read and follow `/codex-review` skill |
| "set vault", "change vault path", "update vault path", "/set-vault" | Read and follow `/set-vault` skill |
| Any code edit request (none of the above matched)                       | Run `/load-standards` then proceed    |

Read the skill file from `{{TOOLBOX_PATH}}/skills/<skill>.md` before following it. Do not ask the user to run the skill — just do it.

<!-- superpowers skill reference (installed at ~/.claude/plugins/cache/claude-plugins-official/superpowers/)
     Known skills: superpowers:brainstorming, superpowers:systematic-debugging,
     superpowers:subagent-driven-development, superpowers:executing-plans,
     superpowers:requesting-code-review, superpowers:receiving-code-review,
     superpowers:finishing-a-development-branch, superpowers:dispatching-parallel-agents
     Note: /brainstorm command is deprecated — use superpowers:brainstorming skill instead -->
