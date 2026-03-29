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

## Rules
- No business logic in route handlers — delegate to service functions
- Always validate input with Zod at the boundary
- Always check auth before any data access
- Never leak internal error messages to clients — map to safe messages at boundary
- Keep route handler files thin: auth check → validate → call service → return response
