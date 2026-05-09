# Worker Patterns — BullMQ

## One Worker Class Per Job Type

Each queue gets one Worker. The processor function inside the Worker calls a service — it does not contain business logic itself.

```ts
// src/workers/email-delivery.worker.ts
import { Worker, type Job } from 'bullmq'
import { redisConnection } from '../lib/redis'
import { QUEUE_NAMES } from '../queues/names'
import { sendWelcomeEmail } from '../services/email.service'
import type { SendWelcomeEmailJobData, SendWelcomeEmailJobResult } from '../types/jobs'

export const emailDeliveryWorker = new Worker<SendWelcomeEmailJobData, SendWelcomeEmailJobResult>(
  QUEUE_NAMES.EMAIL_DELIVERY,
  async (job: Job<SendWelcomeEmailJobData>) => {
    // Worker only dispatches to the service layer
    return sendWelcomeEmail(job.data)
  },
  {
    connection: redisConnection,
    concurrency: 5,
    removeOnComplete: { count: 1000, age: 24 * 3600 },  // keep 1000 or 24h, whichever is less
    removeOnFail: { age: 14 * 24 * 3600 },              // keep failures for 14 days (DLQ retention)
  }
)
```

Rules:
- Never put business logic inside the processor function — call a service
- Always set `removeOnComplete` and `removeOnFail` — without these, completed jobs accumulate in Redis indefinitely
- `concurrency` must be tuned per job type; default to `5` and adjust based on load testing

## Job Enqueue Helpers

Wrap queue `.add()` calls in typed helper functions — never call `.add()` directly from application code.

```ts
// src/jobs/send-welcome-email.job.ts
import { emailDeliveryQueue } from '../queues/email-delivery.queue'
import type { SendWelcomeEmailJobData } from '../types/jobs'

export async function enqueueSendWelcomeEmail(
  data: SendWelcomeEmailJobData,
  eventId: string,           // used as jobId for idempotency
): Promise<void> {
  await emailDeliveryQueue.add('send-welcome-email', data, {
    jobId: eventId,          // idempotent deduplication key
    attempts: 5,
    backoff: {
      type: 'exponential',
      delay: 1000,           // 1s → 2s → 4s → 8s → 16s
    },
  })
}
```

## Idempotency

Set `jobId` to a stable, event-derived ID (e.g., the originating event's UUID or `${type}:${entityId}`). BullMQ will silently skip duplicate additions with the same `jobId` in the same queue.

```ts
// Good — idempotent by event ID
await enqueueSendWelcomeEmail(data, `user-created:${user.id}`)

// Bad — no jobId; duplicate events create duplicate jobs
await emailDeliveryQueue.add('send-welcome-email', data)
```

## Exponential Backoff with Jitter

Default retry configuration for all workers:

```ts
{
  attempts: 5,
  backoff: {
    type: 'exponential',
    delay: 1000,   // Base: 1 second. Delays: 1s, 2s, 4s, 8s, 16s
  },
}
```

Add jitter at the service level for external API calls to avoid thundering-herd retries:

```ts
const jitter = Math.random() * 500
await delay(jitter)
```

## Dead Letter Queue (DLQ)

Jobs that exhaust all retries are moved to the "failed" set by BullMQ. Set `removeOnFail: { age: 14 * 24 * 3600 }` to keep them for 14 days for manual inspection.

Add a `QueueEvents` listener to log and alert on final failures:

```ts
// src/workers/email-delivery.worker.ts
import { QueueEvents } from 'bullmq'
import { QUEUE_NAMES } from '../queues/names'

const queueEvents = new QueueEvents(QUEUE_NAMES.EMAIL_DELIVERY, {
  connection: redisConnection,
})

queueEvents.on('failed', ({ jobId, failedReason }) => {
  console.error(`[DLQ] Job ${jobId} exhausted retries: ${failedReason}`)
  // Alert via your observability stack (e.g., Sentry, PagerDuty)
})
```

## Session-Scoped Ordering with `groupId`

When jobs belonging to the same logical session must run in order, use BullMQ Pro's `group` feature or serialize per-session enqueues explicitly:

```ts
await queue.add('process-event', data, {
  group: { id: sessionId },   // BullMQ Pro
})
```

Without BullMQ Pro, use a per-session queue keyed by `sessionId`, or enforce ordering in the service layer.

## Stalled Job Watchdog

Enable stall detection to catch workers that crash without marking a job as complete or failed:

```ts
new Worker(QUEUE_NAMES.EMAIL_DELIVERY, processor, {
  connection: redisConnection,
  stalledInterval: 30_000,   // Check every 30s
  maxStalledCount: 2,        // Max stall events before marking failed
})
```

## BullMQ Board (Admin UI)

Expose BullMQ Board behind admin authentication:

```ts
// Hono example
import { createBullBoard } from '@bull-board/api'
import { BullMQAdapter } from '@bull-board/api/bullMQAdapter'
import { HonoAdapter } from '@bull-board/hono'

const serverAdapter = new HonoAdapter(serveStatic)
createBullBoard({
  queues: [new BullMQAdapter(emailDeliveryQueue)],
  serverAdapter,
})

app.route('/admin/queues', requireAdminAuth, serverAdapter.registerPlugin())
```

Never expose the queue board publicly.

## Anti-Patterns

- Do not put business logic inside the Worker processor — call a service instead
- Do not omit `removeOnComplete` / `removeOnFail` — Redis will fill up
- Do not use wall-clock delays as a substitute for proper backoff
- Do not create a single "catch-all" worker for all job types — one worker per job type
- Do not enqueue jobs without a `jobId` when idempotency matters
- Do not call external APIs directly in the Worker processor — call a service that handles rate limiting, circuit breaking, and error mapping
