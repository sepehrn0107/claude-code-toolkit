# 21st Agents SDK Standards

Standards for projects using the [21st Agents SDK](https://21st.dev/agents).

## When to Use

Use this stack when shipping a Claude-backed agent with built-in chat UI, sandboxed execution, spend controls, and observability — without building the infrastructure yourself.

## Packages

### Core (all Next.js templates)

```bash
pnpm add @21st-sdk/agent @21st-sdk/nextjs @21st-sdk/react @21st-sdk/node @ai-sdk/react ai zod
```

### CLI

```bash
pnpm add -D @21st-sdk/cli
```

## Base Stack

- **Next.js projects**: inherit `typescript-nextjs` standards + all files in this directory
- **Python projects**: inherit `python-fastapi` standards + `agent.md` and `observability.md` only
- **Go projects**: inherit `go` standards + `agent.md` and `observability.md` only

`deployment.md` and `frontend.md` are Next.js-specific — skip them for Python/Go projects.

## Files in This Directory

| File | Covers |
|------|--------|
| `agent.md` | Agent definition: model, tools, system prompt, spend limits, turn limits |
| `deployment.md` | Token route, env vars, sandboxes, thread management, CLI deploy |
| `frontend.md` | `AgentChat` wiring, streaming, runtime options, theming, file attachments |
| `observability.md` | Traces, cost tracking, log retention, debugging checklist |

## Links

- [Quickstart](https://21st.dev/agents/docs/get-started/quickstart)
- [API Reference](https://21st.dev/agents/docs/api-reference)
- [Dashboard](https://21st.dev/agents/app)
