# Observability Standards

## Built-in Traces

Session replay and full tool call traces are built into the 21st dashboard — no additional instrumentation is needed.

- Link the dashboard in the project's `CLAUDE.md`:
  ```
  Dashboard: https://21st.dev/agents/app
  ```
- Always check traces before debugging a misbehaving agent — traces show the complete tool call history, inputs, outputs, and token usage per turn

## Cost Tracking

- Review per-turn token costs in the dashboard before increasing `maxBudgetUsd`
- Unexpected cost spikes usually indicate runaway tool loops — inspect the trace for the offending turn before modifying the agent

## Log Retention

- Set up a log retention policy at project start
- Default is 30 days
- Adjust in dashboard Settings → Project → Retention

## Debugging Checklist

Before adding debug logging or changing the agent definition:

1. Open the 21st dashboard traces for the failing session
2. Find the turn where behavior diverged from expectations
3. Inspect the tool calls in that turn — inputs and outputs are both logged
4. Only after confirming the root cause in traces: modify the agent definition, tools, or system prompt
