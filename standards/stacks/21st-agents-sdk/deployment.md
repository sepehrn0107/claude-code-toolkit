# Deployment Standards

## Login

Login once per machine — not per project:

```bash
npx @21st-sdk/cli login
```

The API key is in the [21st dashboard](https://21st.dev/agents/app) under Settings → API Keys.

## Deploy

From the project root:

```bash
npx @21st-sdk/cli deploy
```

If deploy fails, surface `stderr` to the user — do not retry silently.

## Token Route

Always use `createTokenHandler` server-side — never expose the API key to the browser:

```typescript
// app/api/agent-token/route.ts
import { createTokenHandler } from '@21st-sdk/nextjs';

export const POST = createTokenHandler({
  apiKey: process.env.API_KEY_21ST!,
});
```

If `API_KEY_21ST` is missing at runtime, the token route returns HTTP 500 with a generic error message. Never include the env var name or API key value in the client-visible response body.

## Environment Variables

| Variable | Scope | Notes |
|----------|-------|-------|
| `API_KEY_21ST` | Server only | Store in `.env.local`, never `.env` (which may be committed) |

Never reference `API_KEY_21ST` in client-side code or `next.config.js` `env` exports.

## Sandboxes

Create sandboxes server-side; pass `sandboxId` to the client component:

```typescript
// Server action or API route
import { AgentClient } from '@21st-sdk/node';

const sandbox = await AgentClient.sandboxes.create({ agent: 'my-agent' });
// Pass sandbox.id to the client via props or API response
return { sandboxId: sandbox.id };
```

## Thread Management

Create threads server-side; pass `threadId` to `AgentChat` for conversation continuity across page loads:

```typescript
// Server action or API route
const thread = await AgentClient.threads.create();
return { threadId: thread.id };
```

Pass `threadId` as a prop to `AgentChat` — do not create threads client-side.
