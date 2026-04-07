## Automatic Skill Routing

Detect user intent and route automatically — do not wait to be asked.

### User Intent Routes

| User says… | Auto-trigger |
|------------|-------------|
| "add/implement/build/create [X]", "work on [ticket]" | `/implement` |
| "brainstorm [X]", "plan mode", "let's plan" | `superpowers:brainstorming` |
| "fix/debug [X]", "not working" | `superpowers:systematic-debugging` |
| "check this", "review [X]", "ready to merge", "before PR" | `/standards-check` |
| "new project", "starting fresh", "scaffold this" | `/new-project` |
| "switch/change project", "work on [repo]" | `/project` |
| References a known project name AND that project is not currently active AND `WORKSPACE_MODE:` is present | `/auto-switch` |
| "create/make/improve/edit/optimize skill" | `skill-creator:skill-creator` |
| "push/commit and push/open a PR/create a PR/ship this" | `/git-push` |
| "upgrade/update toolbox", "/upgrade" | `/upgrade` |
| "upgrade-dev", "/upgrade-dev", "apply template" | `/upgrade-dev` |
| "delegate to codex", "use codex for" | `/codex-delegate` |
| "review with codex", "codex review" | `/codex-review` |
| "set vault", "change vault path" | `/set-vault` |
| "update docs", "docs are stale" | `/update-docs` |
| "`/skills`", "install/list/add/disable/enable/update skill" | `/skills` |
| Any code edit request (no match above) | `/load-standards` then proceed |

### Internal Auto-Routes

These trigger automatically when Claude is about to perform the listed action:

| Before… | Route through |
|---------|---------------|
| `WebFetch` or following a URL | **BLOCKING**: `/web-fetch` first — never call `WebFetch` directly |
| Multiple git commands | `/git-ctx` |
| Reading `git diff` for commit/PR | `/diff-summary` |
| Reading a section from a file >100 lines | `/read-section` |
| Checking package version/types/license | `/pkg-info` |
| Checking runtime versions/ports/Docker/.env | `/env-check` |
| Searching code with Grep | `/grep` |
| Writing to any memory file | `/memory-sync` |

Read the skill file from `{{TOOLBOX_PATH}}/skills/<skill>.md` before following it. Do not ask the user to run the skill — just do it.

<!-- superpowers skill reference (installed at ~/.claude/plugins/cache/claude-plugins-official/superpowers/)
     Known skills: superpowers:brainstorming, superpowers:systematic-debugging,
     superpowers:subagent-driven-development, superpowers:executing-plans,
     superpowers:requesting-code-review, superpowers:receiving-code-review,
     superpowers:finishing-a-development-branch, superpowers:dispatching-parallel-agents
     Note: /brainstorm command is deprecated — use superpowers:brainstorming skill instead -->
