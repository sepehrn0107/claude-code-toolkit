# Naming Conventions — BullMQ

## Queue Names

- `kebab-case` string constants — `'email-delivery'`, `'report-generation'`, `'webhook-dispatch'`
- Prefix with a domain when multiple services share Redis — `'autocarline:email-delivery'`
- Define all queue names as exported constants in `src/queues/names.ts` — never use inline strings

```ts
// src/queues/names.ts
export const QUEUE_NAMES = {
  EMAIL_DELIVERY: 'email-delivery',
  REPORT_GENERATION: 'report-generation',
  WEBHOOK_DISPATCH: 'webhook-dispatch',
} as const

export type QueueName = typeof QUEUE_NAMES[keyof typeof QUEUE_NAMES]
```

## Job Types

- Job name (BullMQ `name` field): `kebab-case` — `'send-welcome-email'`, `'generate-monthly-report'`
- Job data interface: `<JobName>JobData` in PascalCase — `SendWelcomeEmailJobData`, `GenerateMonthlyReportJobData`
- Job result type: `<JobName>JobResult` — `SendWelcomeEmailJobResult`

```ts
export interface SendWelcomeEmailJobData {
  userId: string
  email: string
  name: string
}

export interface SendWelcomeEmailJobResult {
  messageId: string
  sentAt: string
}
```

## Files and Folders

```
src/
  queues/
    names.ts                  # All queue name constants
    email-delivery.queue.ts   # Queue instances — one file per queue
    report-generation.queue.ts
  workers/
    email-delivery.worker.ts  # Worker — one file per queue
    report-generation.worker.ts
  jobs/
    send-welcome-email.job.ts # Job enqueue helper — one file per job type
    generate-report.job.ts
  services/                   # Business logic called by workers
    email.service.ts
    report.service.ts
  types/
    jobs.ts                   # Job data/result interfaces
```

## Worker Class Names

Worker class: `<Domain>Worker` — `EmailDeliveryWorker`, `ReportGenerationWorker`

## Queue Instance Names

Queue variable: `<domain>Queue` — `emailDeliveryQueue`, `reportGenerationQueue`

## Connection

Export a single shared Redis connection (or connection options object) from `src/lib/redis.ts`:

```ts
// src/lib/redis.ts
import IORedis from 'ioredis'
export const redisConnection = new IORedis(process.env.REDIS_URL!, {
  maxRetriesPerRequest: null,  // Required by BullMQ
})
```
