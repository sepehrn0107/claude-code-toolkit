---
name: new-project
description: Full scaffolding skill for starting any new project, repo, service, or tool from scratch. Use this when the user says "new project", "starting fresh", "scaffold this", or begins work in a directory with no existing project context. Handles stack detection, brainstorming, planning, memory scaffold creation, and git init. Always trigger this before /implement on a brand-new codebase — if there's no project memory in the vault yet, this should run first.
---

# /new-project

Entry point for starting any project from scratch.

## When to Use
Run this when starting a new project, repo, service, or tool with no existing context.

## Steps

### 0. Prerequisites Check

Run:
```bash
docker ps --filter name=crawl4ai --format "{{.Names}}"
```

- **Empty output** (container not running) → print setup instructions below, then continue — do not block the session:
  ```
  [crawl4ai] Container not running. To start it:
    docker pull unclecode/crawl4ai:latest
    docker run -d -p 11235:11235 --name crawl4ai --shm-size=1g unclecode/crawl4ai:latest
  Verify: curl http://localhost:11235/health
  ```
- **`crawl4ai` in output** → skip silently, proceed to Step 1.

This check is informational only — the session continues regardless of outcome.

### 1. Load Global Context and Detect Stack (parallel)

Run both of these at the same time — they have no dependency on each other:

- Read `{{VAULT_PATH}}/05-areas/claude-memory/MEMORY.md` — global preferences and learnings
- Read `{{TOOLBOX_PATH}}/standards/universal/` — all 5 universal standard files
- Check working directory for stack signals: `package.json`, `go.mod`, `requirements.txt`, `Cargo.toml`, `pyproject.toml`, etc.

### 2. Collect the Idea
Ask the user for input in the most natural way:
- **Freeform**: "Tell me about the project — what is it, what does it do, who uses it?"
- **Structured prompts**: Ask about goal, users, key constraints, success criteria
- **Existing spec**: If the user has a doc, read it first instead of asking

### 3. Confirm Stack

1. If signals found in Step 1 → propose the detected stack and ask to confirm
2. If no signals → ask: "What stack are you using?"
3. If stack directory exists at `{{TOOLBOX_PATH}}/standards/stacks/<stack>/` → load it
4. If stack is new → research current best practices, draft a new standards file, get user approval, save to `{{TOOLBOX_PATH}}/standards/stacks/<new-stack>/`

#### 21st-agents-sdk Detection

If `@21st-sdk/agent` is found in `package.json` → auto-propose `21st-agents-sdk` stack and skip the stack selection prompt.

#### Agent Project Selection

If the user picks "agent" as the project type → ask which template:

**Starters (minimal):**
- `nextjs` — Next.js chat UI with AgentChat component
- `python` — Terminal chat client
- `go` — Terminal chat client

**Use-cases (opinionated):**
- `docs-assistant` — Q&A agent over a docs URL via llms.txt
- `support-agent` — Docs-powered support + email escalation (Resend)
- `lead-research` — Email lookup + Slack alerts (Exa.ai)
- `note-taker` — Persistent notes with real-time sync (Convex)
- `browser-scraper` — Structured data extraction (Browser Use Cloud)

#### Scaffold by Template Type

**Next.js templates** (`nextjs`, `docs-assistant`, `support-agent`, `lead-research`, `note-taker`, `browser-scraper`):

Before scaffolding files:
```bash
pnpm add @21st-sdk/agent @21st-sdk/nextjs @21st-sdk/react @21st-sdk/node @ai-sdk/react ai zod
pnpm add -D @21st-sdk/cli
```

Then create:

`agents/my-agent/index.ts`:
```typescript
import { createAgent } from '@21st-sdk/agent';

const agent = createAgent({
  model: 'claude-sonnet-4-6',
  systemPrompt: `You are a helpful assistant.`,
  tools: {},
  maxBudgetUsd: 0.50,
  maxTurns: 10,
  disallowedTools: [],
});

export default agent;
```

`app/api/agent-token/route.ts`:
```typescript
import { createTokenHandler } from '@21st-sdk/nextjs';

export const POST = createTokenHandler({
  apiKey: process.env.API_KEY_21ST!,
});
```

`app/page.tsx`:
```typescript
import { AgentChat } from '@21st-sdk/nextjs';

export default function Page() {
  return <AgentChat agentId="my-agent" />;
}
```

Copy `{{TOOLBOX_PATH}}/templates/21st-agent-CLAUDE.md.template` → project `CLAUDE.md` and fill in the agent name.

---

**Python template** (`python`):

```bash
pip install 21st-sdk   # verify published package name at scaffold time
```

Create `main.py` from the 21st Python starter pattern (verify current pattern at https://21st.dev/agents/docs/get-started/quickstart).

Stack standard: inherit `python-fastapi` + `21st-agents-sdk` (`agent.md` and `observability.md` only — skip `deployment.md` and `frontend.md`).

---

**Go template** (`go`):

```bash
go get github.com/21st-dev/sdk-go   # verify module path at scaffold time
```

Create `main.go` from the 21st Go starter pattern (verify current pattern at https://21st.dev/agents/docs/get-started/quickstart).

Stack standard: inherit `go` + `21st-agents-sdk` (`agent.md` and `observability.md` only — skip `deployment.md` and `frontend.md`).

### 4. Brainstorm + Plan

Invoke `{{TOOLBOX_PATH}}/skills/select-model.md` with task: "Brainstorm and plan a new project."
Use the returned model for both agent calls below.

Invoke `superpowers:brainstorming` using the chosen model to scope and design the project.

If the project has a UI — any frontend, mobile app, dashboard, landing page, or user-facing screens — invoke the `ui-ux-pro-max` skill now to establish the design system (style, color palette, typography) before writing the plan.

Invoke `superpowers:writing-plans` using the chosen model to produce the implementation plan.

### 5. Scaffold the Project
Create the following structure:

**In the project root:**
```
<project>/
└── CLAUDE.md    # Filled from {{TOOLBOX_PATH}}/templates/CLAUDE.md.template
```

**In vault:**
```
{{VAULT_PATH}}/02-projects/<name>/
├── memory/
│   ├── MEMORY.md              # From {{TOOLBOX_PATH}}/templates/memory/project/MEMORY.md
│   ├── project_context.md     # Filled with collected project info
│   ├── stack.md               # Chosen stack and why
│   ├── architecture.md        # High-level structure from brainstorm
│   ├── progress.md            # Phase = "planning", Next = first task
│   ├── lessons.md             # Empty to start
│   └── decisions/             # Empty — ADRs added as decisions are made
├── plans/                     # Implementation plans written here
└── specs/                     # Design specs written here
```

Replace all `{{PLACEHOLDER}}` values in CLAUDE.md with actual project details.
Replace `{{TOOLBOX_PATH}}` with the actual toolbox path from `~/.claude/CLAUDE.md`.
Do NOT replace `$VAULT` — it is a portable variable defined in the user's global CLAUDE.md and must stay as-is.

### 6. Initialize Git
If no git repo exists:
```bash
git init
git add .
git commit -m "chore: initial scaffold"
```
If git already exists, skip this step.

### 7. Hand Off
Announce: "Project scaffolded. Run /implement to start building."
