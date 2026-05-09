# BullMQ Standards

Standards for projects using BullMQ as the async job queue with TypeScript and Redis.

## Stack Profile

- **Queue**: [BullMQ](https://docs.bullmq.io/) — Redis-backed job queue for Node.js
- **Language**: TypeScript (strict mode)
- **Testing**: Vitest with `ioredis-mock` or real Redis in CI
- **Build**: tsc

## Files in This Directory

| File | Topic |
|------|-------|
| `README.md` | This file — stack overview and file index |
| `naming.md` | Naming conventions for queues, workers, job types |
| `workers.md` | Worker class patterns, DLQ, backoff, idempotency |
| `testing.md` | Testing approach with mocked Redis and real-Redis CI |

## Non-Goals

These standards do not cover:
- Queue dashboard authentication (handled at infrastructure level)
- Redis cluster configuration (ops concern)
- Scheduler / cron job patterns beyond BullMQ's `repeat` option
