# Testing Standards — BullMQ

## Stack

- **Runner**: Vitest
- **Unit tests**: `ioredis-mock` (no real Redis needed)
- **Integration tests**: real Redis instance in CI (Docker service)

## What to Test

| Layer | What to test |
|-------|-------------|
| Job helper | Correct `queue.add()` call — name, data, options (jobId, attempts, backoff) |
| Worker processor | Delegates to the service; passes job data correctly |
| Service | Business logic — independent of BullMQ entirely |
| Backoff config | `attempts`, `backoff.type`, `backoff.delay` set as expected |
| Idempotency | Same `jobId` is not enqueued twice |

Do not test BullMQ internals (Redis storage, retry scheduling) — that is the library's responsibility.

## Unit Tests with `ioredis-mock`

Use `ioredis-mock` to avoid a real Redis dependency in unit tests.

```ts
// src/test/setup.ts
import { vi } from 'vitest'
import IORedisMock from 'ioredis-mock'

vi.mock('../lib/redis', () => ({
  redisConnection: new IORedisMock(),
}))
```

### Testing Job Enqueue Helpers

```ts
// src/jobs/send-welcome-email.job.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { enqueueSendWelcomeEmail } from './send-welcome-email.job'
import { emailDeliveryQueue } from '../queues/email-delivery.queue'

vi.mock('../queues/email-delivery.queue', () => ({
  emailDeliveryQueue: { add: vi.fn() },
}))

describe('enqueueSendWelcomeEmail', () => {
  beforeEach(() => vi.clearAllMocks())

  it('adds the job with the correct name and data', async () => {
    const data = { userId: 'u1', email: 'a@example.com', name: 'Alice' }
    await enqueueSendWelcomeEmail(data, 'event-123')

    expect(emailDeliveryQueue.add).toHaveBeenCalledWith(
      'send-welcome-email',
      data,
      expect.objectContaining({ jobId: 'event-123', attempts: 5 })
    )
  })

  it('uses the eventId as the jobId for idempotency', async () => {
    const data = { userId: 'u2', email: 'b@example.com', name: 'Bob' }
    await enqueueSendWelcomeEmail(data, 'event-456')

    const call = vi.mocked(emailDeliveryQueue.add).mock.calls[0]
    expect(call[2]).toMatchObject({ jobId: 'event-456' })
  })
})
```

### Testing Worker Processor Delegation

```ts
// src/workers/email-delivery.worker.test.ts
import { describe, it, expect, vi } from 'vitest'
import * as emailService from '../services/email.service'
import type { Job } from 'bullmq'

// Import the processor function directly — not the worker instance
import { processEmailDeliveryJob } from './email-delivery.worker'

vi.mock('../services/email.service')

describe('processEmailDeliveryJob', () => {
  it('calls sendWelcomeEmail with job data', async () => {
    const mockJob = {
      data: { userId: 'u1', email: 'a@example.com', name: 'Alice' },
    } as Job

    vi.mocked(emailService.sendWelcomeEmail).mockResolvedValue({ messageId: 'msg-1', sentAt: '2024-01-01' })

    const result = await processEmailDeliveryJob(mockJob)

    expect(emailService.sendWelcomeEmail).toHaveBeenCalledWith(mockJob.data)
    expect(result).toMatchObject({ messageId: 'msg-1' })
  })
})
```

Export the processor function separately from the worker instance to make it independently testable:

```ts
// src/workers/email-delivery.worker.ts
export async function processEmailDeliveryJob(
  job: Job<SendWelcomeEmailJobData>
): Promise<SendWelcomeEmailJobResult> {
  return sendWelcomeEmail(job.data)
}

export const emailDeliveryWorker = new Worker(
  QUEUE_NAMES.EMAIL_DELIVERY,
  processEmailDeliveryJob,
  { connection: redisConnection, /* ... */ }
)
```

## Integration Tests (Real Redis in CI)

Use a real Redis instance for end-to-end job lifecycle tests. Run Redis as a Docker service in CI.

```yaml
# .github/workflows/test.yml
services:
  redis:
    image: redis:7-alpine
    ports: ['6379:6379']
```

```ts
// src/workers/email-delivery.integration.test.ts
import { describe, it, expect, afterAll } from 'vitest'
import { Queue, Worker } from 'bullmq'
import { redisConnection } from '../lib/redis'

describe('email delivery end-to-end', () => {
  const queue = new Queue('test-email-delivery', { connection: redisConnection })
  let worker: Worker

  afterAll(async () => {
    await worker?.close()
    await queue.close()
    await queue.obliterate()
  })

  it('processes a job and marks it complete', async () => {
    let jobDone = false
    worker = new Worker('test-email-delivery', async () => { jobDone = true }, {
      connection: redisConnection,
    })

    await queue.add('test-job', { userId: 'u1' })

    await new Promise<void>((resolve) => {
      worker.on('completed', () => resolve())
    })

    expect(jobDone).toBe(true)
  })
})
```

## Structure

- Unit tests: `<source-file>.test.ts` alongside source
- Integration tests: `<source-file>.integration.test.ts` or a separate `tests/integration/` folder
- Mark integration tests with a `@integration` tag or separate Vitest config so they can be skipped locally

## Anti-Patterns

- Do not test that Redis stored the job correctly — test your code's behavior
- Do not import the Worker constructor in unit tests — mock the queue's `add()` method instead
- Do not use `setTimeout` to wait for job processing — use `QueueEvents` or `worker.on('completed')`
- Do not run integration tests without cleaning up test queues — `queue.obliterate()` in `afterAll`
