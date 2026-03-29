# REST API Standards (Next.js Route Handlers)

## URL Conventions
- Plural nouns for resources: `/api/workouts`, `/api/exercises`
- Kebab-case for multi-word segments: `/api/muscle-groups`
- Nested for ownership: `/api/workouts/[workoutId]/sets`
- No verbs in URLs — use HTTP methods instead
- No version prefix unless breaking changes are expected; add `/v1/` only then

## HTTP Methods
| Method | Semantics |
|--------|-----------|
| GET | Read — safe, idempotent, no body |
| POST | Create — returns 201 with created resource |
| PUT | Full replace — idempotent |
| PATCH | Partial update |
| DELETE | Remove — returns 204 no body |

## Response Shape
All responses use a consistent envelope:

```ts
// Success
{ "data": <payload> }

// Error
{ "error": { "message": string, "code"?: string } }
```

Never mix fields across success and error shapes.

## Status Codes
| Code | When |
|------|------|
| 200 | Successful GET / PATCH / PUT |
| 201 | Successful POST (resource created) |
| 204 | Successful DELETE (no body) |
| 400 | Validation error (bad input) |
| 401 | Unauthenticated |
| 403 | Authenticated but unauthorized |
| 404 | Resource not found |
| 409 | Conflict (e.g. duplicate) |
| 500 | Unexpected server error |

## Typed Error Hierarchy

Define domain errors in `lib/errors.ts` that carry their own HTTP status codes. Services throw domain errors; handlers catch once at the boundary.

```ts
// lib/errors.ts
export class AppError extends Error {
  constructor(
    message: string,
    public readonly statusCode: number,
    public readonly code?: string,
  ) {
    super(message)
    this.name = this.constructor.name
  }
}

export class NotFoundError extends AppError {
  constructor(message = 'Not found') { super(message, 404, 'NOT_FOUND') }
}
export class UnauthorizedError extends AppError {
  constructor(message = 'Unauthorized') { super(message, 401, 'UNAUTHORIZED') }
}
export class ForbiddenError extends AppError {
  constructor(message = 'Forbidden') { super(message, 403, 'FORBIDDEN') }
}
export class ConflictError extends AppError {
  constructor(message: string) { super(message, 409, 'CONFLICT') }
}
export class ValidationError extends AppError {
  constructor(message: string) { super(message, 400, 'VALIDATION_ERROR') }
}
```

Route handler catch block (pair with `ok()` / `err()` helpers):
```ts
} catch (e) {
  if (e instanceof AppError) return err(e.message, e.statusCode, e.code)
  console.error(e)
  return err('Internal server error', 500)
}
```

No HTTP status codes anywhere except `errors.ts` — services throw, handlers catch once.

## Route Handler Structure

```ts
// app/api/workouts/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'
import { workoutService } from '@/services/workout'
import { getSession } from '@/lib/auth'

const CreateWorkoutSchema = z.object({
  name: z.string().min(1),
  date: z.string().datetime(),
})

export async function POST(req: NextRequest) {
  const session = await getSession(req)
  if (!session) return NextResponse.json({ error: { message: 'Unauthorized' } }, { status: 401 })

  const body = await req.json()
  const parsed = CreateWorkoutSchema.safeParse(body)
  if (!parsed.success) {
    return NextResponse.json({ error: { message: parsed.error.message } }, { status: 400 })
  }

  const workout = await workoutService.create(session.userId, parsed.data)
  return NextResponse.json({ data: workout }, { status: 201 })
}
```

## Response Helpers

Extract `ok()` / `err()` into `lib/api-response.ts` to enforce the envelope shape in one place and keep handlers thin:

```ts
// lib/api-response.ts
import { NextResponse } from 'next/server'

export const ok = <T>(data: T, status = 200) =>
  NextResponse.json({ data }, { status })

export const err = (message: string, status = 500, code?: string) =>
  NextResponse.json({ error: { message, ...(code && { code }) } }, { status })
```

Usage:
```ts
// app/api/exercises/route.ts
export async function GET() {
  const session = await requireSession()
  if (!session) return err('Unauthorized', 401)
  const exercises = await exerciseService.list(session.userId)
  return ok(exercises)
}
```

## Rules
- No business logic in route handlers — delegate to service functions
- Always validate input with Zod at the boundary
- Always check auth before any data access
- Never leak internal error messages to clients — map to safe messages at boundary
- Keep route handler files thin: auth check → validate → call service → return response
- Use `ok()` / `err()` helpers — never inline `NextResponse.json` with envelope shapes directly
