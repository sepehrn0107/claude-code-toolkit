# Agent Definition Standards

## Model

- Default: `claude-sonnet-4-6`
- Override per-agent only when justified — add a comment explaining why above the model line

## Tool Definitions

Always define tools with Zod schemas — never raw JSON schema:

```typescript
import { z } from 'zod';

const tools = {
  searchDocs: {
    description: 'Search the documentation for a given query',
    parameters: z.object({
      query: z.string().describe('The search query'),
      limit: z.number().optional().default(5),
    }),
    execute: async ({ query, limit }) => {
      // implementation
    },
  },
};
```

## System Prompt

- Keep the system prompt in `agents/<name>/index.ts`, not in the frontend or request body
- Use SDK skill blocks for on-demand context injection (documentation, policies, domain knowledge) instead of stuffing the system prompt

## Spend Limits

- Always set `maxBudgetUsd` in production agents — never leave it unlimited
- Typical range: `0.10`–`2.00` USD per turn depending on task complexity
- Review per-turn costs in the 21st dashboard before adjusting the limit

## Turn Limits

- Always set `maxTurns` explicitly — the default is unbounded
- Typical range: 3–10 for interactive agents; 20–50 for autonomous tasks

## Disallowed Tools

Enumerate tools the agent must never call:

```typescript
import { createAgent } from '@21st-sdk/agent';

const agent = createAgent({
  model: 'claude-sonnet-4-6',
  systemPrompt: `You are a helpful assistant.`,
  tools,
  maxBudgetUsd: 0.50,
  maxTurns: 10,
  disallowedTools: ['bash', 'file_write'],
});

export default agent;
```

## Agent File Location

Agent entry point always lives at `agents/<agent-name>/index.ts`. One agent per directory.
