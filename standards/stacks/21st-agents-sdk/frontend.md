# Frontend Standards

## Chat Component

Use `AgentChat` from `@21st-sdk/nextjs` — do not hand-roll a chat UI:

```typescript
// app/page.tsx
import { AgentChat } from '@21st-sdk/nextjs';

interface Props {
  threadId: string;
  sandboxId: string;
}

export default function Page({ threadId, sandboxId }: Props) {
  return (
    <AgentChat
      agentId="my-agent"
      threadId={threadId}
      sandboxId={sandboxId}
    />
  );
}
```

## Streaming

Wire streaming via `useChat` from `@ai-sdk/react`:

```typescript
import { useChat } from '@ai-sdk/react';

const { messages, input, handleInputChange, handleSubmit } = useChat({
  api: '/api/agent-token',
});
```

## Runtime Options

Pass per-message runtime options in the request body `options` field — never rebuild the agent for runtime variation:

```typescript
await fetch('/api/agent-token', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    messages,
    options: {
      systemPrompt: 'Custom prompt for this session',
      maxTurns: 5,
      maxBudgetUsd: 0.25,
      disallowedTools: ['bash'],
    },
  }),
});
```

## Theming

Use SDK theme variables — do not override with hardcoded color values:

```css
/* Correct */
color: var(--21st-primary);
background: var(--21st-surface);

/* Wrong — breaks theme switching */
color: #6366f1;
background: #ffffff;
```

## File Attachments

Configure accepted MIME types explicitly — do not accept all types by default:

```typescript
<AgentChat
  agentId="my-agent"
  threadId={threadId}
  sandboxId={sandboxId}
  acceptedFileTypes={['image/png', 'image/jpeg', 'application/pdf']}
/>
```
