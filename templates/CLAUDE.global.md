# Toolbox

Standards, memory, and lifecycle skills for all projects.
Source: https://github.com/sepehrn0107/claude-code-toolkit (local clone: {{TOOLBOX_PATH}})

> `{{WORKSPACE_PATH}}` = the directory that contains the toolbox clone (i.e. the parent of `{{TOOLBOX_PATH}}`).
> Example: if `{{TOOLBOX_PATH}}` = `C:/Users/sepeh/Documents/workspace/toolbox`, then `{{WORKSPACE_PATH}}` = `C:/Users/sepeh/Documents/workspace`.

## Session Start (automatic)

> **Sub-agent check:** If `WORKSPACE_MODE:` does not appear anywhere in your context, you are
> running as a sub-agent — skip this entire block. Sub-agents do not receive session-start hook
> output; project context is injected via the project-level `CLAUDE.md` or the orchestrator prompt.
> Proceed directly to your task.

At the start of every session, before responding to the first message, do all of this silently:

1. Check if `.claude/memory/MEMORY.md` exists in the current project
2. If yes: read all memory files in parallel — `project_context.md`, `stack.md`, `architecture.md`, `progress.md`, `lessons.md`
3. Also read `{{WORKSPACE_PATH}}/memory/MEMORY.md` to load global cross-project learnings
4. Note whether `.claude/index/README.md` exists — if it does, it is available for code navigation
5. Invoke `codex:setup` — store the result as session flag `CODEX_AVAILABLE` (true/false). Do not re-check during the session; use this flag everywhere.
6. Do not announce any of this — just have the context ready before responding
7. If the session-start hook output includes `WORKSPACE_MODE`:
   - If the line starts with `WORKSPACE_MODE:ACTIVE=<name>`: silently load
     `{{WORKSPACE_PATH}}/<name>/.claude/memory/` files in parallel
     (project_context.md, stack.md, architecture.md, progress.md, lessons.md — skip missing).
     Do not output anything — the hook already printed the "Active project" line.
   - If the line starts with `WORKSPACE_MODE:CHOOSE`: the hook has already shown a numbered list.
     Treat the user's FIRST message as their project choice (name or number).
     Resolve number → name using the `Projects:` list in the hook line.
     Then: write the choice to `{{WORKSPACE_PATH}}/memory/active-project.md`
     as `active: <choice>` / `updated: <YYYY-MM-DD>`, load that project's memory files, and
     output: `Active project: <choice>. Context loaded.`
     If the user's first message is not a valid project name/number, re-show the list and wait.

## Automatic Skill Routing

Detect user intent from the first message and route automatically — do not wait to be asked:

| User says…                                                              | Auto-trigger                          |
|-------------------------------------------------------------------------|---------------------------------------|
| "add [X]", "implement [X]", "build [X]", "create [feature]", "work on [ticket]", "ticket [X]" | Read and follow `/implement` skill  |
| "fix [X]", "debug [X]", "something is broken", "not working"            | Invoke `superpowers:systematic-debugging` |
| "check this", "review [X]", "ready to merge", "before PR"              | Read and follow `/standards-check`    |
| "new project", "starting fresh", "scaffold this"                        | Read and follow `/new-project`        |
| "switch project", "change project", "work on [repo]"                    | Read and follow `/project` skill      |
| "create skill", "make a skill", "new skill", "improve skill", "edit skill", "optimize skill", "skill for [X]" | Invoke `skill-creator:skill-creator` system skill |
| "push to git", "push this", "commit and push", "push my changes", "send to github", "open a PR", "create a PR", "push these changes", "ship this", "just push it", "lets push" | Read and follow `/git-push` skill |
| "upgrade toolbox", "update toolbox", "run upgrade", "/upgrade"               | Read and follow `/upgrade` skill      |
| "delegate to codex", "let codex handle", "use codex for", "hand off to codex" | Read and follow `/codex-delegate` skill |
| "review with codex", "codex review", "let codex review", "delegate review" | Read and follow `/codex-review` skill |
| Claude is about to use `WebFetch` or follow a URL to read page content  | Read and follow `/web-fetch` skill    |
| Claude is about to run multiple git commands (status, log, diff, branch) | Read and follow `/git-ctx` skill     |
| Claude is about to read `git diff` to understand what changed or draft a commit/PR | Read and follow `/diff-summary` skill |
| Claude needs to read one function, class, or section from a file >100 lines | Read and follow `/read-section` skill |
| Claude needs package version, types, license, or popularity for an npm/PyPI package | Read and follow `/pkg-info` skill  |
| Claude needs runtime versions, running ports, Docker state, or .env presence | Read and follow `/env-check` skill  |
| Claude is about to search code with Grep or search tools               | Read and follow `/grep` skill         |
| Claude is about to write or append to any memory file                  | Read and follow `/memory-sync` skill  |
| Any code edit request (none of the above matched)                       | Run `/load-standards` then proceed    |

Read the skill file from `{{TOOLBOX_PATH}}/skills/<skill>.md` before following it. Do not ask the user to run the skill — just do it.

## Standards

Before writing or editing any code, standards must be loaded. Two modes:

- **Orchestrating via `/implement`**: read only `{{TOOLBOX_PATH}}/standards/universal/DIGEST.md`
  (the compact 1-page reference). Full standards are loaded by sub-agents per phase.
  Do not read all 9 standards files into the main session.
- **Direct one-off edits**: invoke `{{TOOLBOX_PATH}}/skills/load-standards.md` and wait for
  the confirmation line. This is a blocking requirement — do not proceed without it.

## Before Any PR (automatic)

When preparing to push code or open a PR — even if the user does not ask — automatically run `/standards-check` first. Do not skip this.

## Lifecycle Skills

Skills are loaded from the local toolbox clone. Read the skill file before following it.

- /new-project      → {{TOOLBOX_PATH}}/skills/new-project.md
- /implement        → {{TOOLBOX_PATH}}/skills/implement.md
- /standards-check  → {{TOOLBOX_PATH}}/skills/standards-check.md
- /retrospective    → {{TOOLBOX_PATH}}/skills/retrospective.md
- /add-stack-standards → {{TOOLBOX_PATH}}/skills/add-stack-standards.md
- /index-repo       → {{TOOLBOX_PATH}}/skills/index-repo.md
- /project          → {{TOOLBOX_PATH}}/skills/project.md
- /git-push         → {{TOOLBOX_PATH}}/skills/git-push.md
- /web-fetch        → {{TOOLBOX_PATH}}/skills/web-fetch.md
- /git-ctx          → {{TOOLBOX_PATH}}/skills/git-ctx.md
- /diff-summary     → {{TOOLBOX_PATH}}/skills/diff-summary.md
- /read-section     → {{TOOLBOX_PATH}}/skills/read-section.md
- /pkg-info         → {{TOOLBOX_PATH}}/skills/pkg-info.md
- /grep             → {{TOOLBOX_PATH}}/skills/grep.md
- /env-check        → {{TOOLBOX_PATH}}/skills/env-check.md
- /memory-sync      → {{TOOLBOX_PATH}}/skills/memory-sync.md
- /codex-delegate   → {{TOOLBOX_PATH}}/skills/codex-delegate.md
- /codex-review     → {{TOOLBOX_PATH}}/skills/codex-review.md
- /upgrade          → {{TOOLBOX_PATH}}/skills/upgrade.md

## Codex Integration (automatic)

When in `/implement` Phase 3 (or any direct code-edit task), always attempt Codex first:

1. Check the `CODEX_AVAILABLE` flag set at session start — do not re-invoke `codex:setup`
2. If `CODEX_AVAILABLE` is true: read and follow `/codex-delegate` — pass the full context package (touched files from plan.md, applicable standards, TDD requirement, implement phase context)
3. If false or Codex exits non-zero: fall back to direct Claude implementation silently — do not announce the failure unless the task itself fails
4. After Codex completes: verify with `git diff` and continue the implement lifecycle as normal

This applies to every Phase 3 component invocation in `/implement`. The fallback must be transparent to the user.

When in `/implement` Phase 4 (or any review/verify task), always use `/codex-review`:

1. Check the `CODEX_AVAILABLE` flag
2. If true: read and follow `/codex-review` — pass file paths (not content), ticket state paths, and stack-appropriate standards paths
3. If false: `/codex-review` notifies the user ("Codex is not available. Continuing review with Claude.") and performs the review directly
4. The fallback is explicit — the user is always notified when Codex is skipped for review tasks

## Memory
- Global memory: {{WORKSPACE_PATH}}/memory/MEMORY.md
- Project memory: .claude/memory/MEMORY.md (when present)

## Code Navigation

When you need to find files, understand code structure, or answer questions about the codebase:

1. If `.claude/index/` exists in the current project, **use it before Grep or Glob**:
   - Read `{{TOOLBOX_PATH}}/skills/query-index.md`, then launch a **sub-agent** with the specific question
   - The sub-agent reads only the relevant index files and returns precise, synthesized results
   - This is faster than grep and keeps the main context clean
2. Fall back to Grep/Glob only if:
   - `.claude/index/` does not exist — remind the user they can run `/index-repo` to build it
   - The question is about specific string content within a file (not structure or relations)
3. Never re-read files that the index already summarizes — use the index answer and read source only when editing

## Always Apply
- Read project memory before starting any task
- Follow active stack standards
- Write session summary to progress.md when stopping work
- When starting a new project with no context, run /new-project
- When two or more steps have no data dependency between them, run them in parallel using multiple tool calls in a single message
- When using /implement: act as orchestrator only — hold file paths and one-line summaries, not content. All reasoning, file reading, and code writing happens inside sub-agents.
