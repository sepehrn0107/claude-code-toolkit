# Routing Standards — Hono

## Typed Route Factories

Always type the Hono app with `AppEnv` so that `c.var` is typed across the request lifecycle.

```ts
// types/app.ts
export type Variables = {
  currentUser: User
  requestId: string
}
export type AppEnv = { Variables: Variables }
```

```ts
// Every route file creates a typed sub-app
const userRoute = new Hono<AppEnv>()
```

## Route Organization

Group routes by resource, one file per resource. Mount all resource routers in `app.ts`.

```ts
// Prefer method chaining — it keeps the route table visible at a glance
export const userRoute = new Hono<AppEnv>()
  .get('/', listUsersHandler)
  .post('/', requireAuth, createUserHandler)
  .get('/:id', getUserHandler)
  .put('/:id', requireAuth, updateUserHandler)
  .delete('/:id', requireAuth, deleteUserHandler)
```

Do not mix unrelated resources in the same route file. If two resources are closely related (e.g., `posts` and `posts/comments`), nest them:

```ts
app.route('/api/posts', postRoute)
app.route('/api/posts/:postId/comments', commentRoute)
```

## Handler Type

Use Hono's `Handler` type for standalone handler functions to get full type inference:

```ts
import type { Handler } from 'hono'

export const getUserHandler: Handler<AppEnv> = async (c) => {
  const { id } = c.req.param()
  const user = await getUser(id)
  if (!user) return c.notFound()
  return c.json(user)
}
```

## Input Validation with Zod

Always validate inputs through the Zod validator middleware — never call `c.req.json()` raw in a handler if the input needs validation.

```ts
import { zValidator } from '@hono/zod-validator'
import { userCreateSchema } from '../schemas/user.schema'

userRoute.post(
  '/',
  requireAuth,
  zValidator('json', userCreateSchema),   // validated; type inferred
  async (c) => {
    const body = c.req.valid('json')       // type: UserCreateInput
    const user = await createUser(body)
    return c.json(user, 201)
  }
)
```

## Error Handling

Register a global error handler in `app.ts`. Do not use try/catch in individual handlers for domain errors — throw them and let the global handler normalize them.

```ts
app.onError((err, c) => {
  if (err instanceof AppError) {
    return c.json({ error: err.message, code: err.code }, err.statusCode)
  }
  console.error(err)
  return c.json({ error: 'Internal server error' }, 500)
})

app.notFound((c) => c.json({ error: 'Not found' }, 404))
```

Define a project-level `AppError` class in `types/errors.ts`:

```ts
export class AppError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode: number = 400,
  ) {
    super(message)
    this.name = 'AppError'
  }
}
```

## HTTP Status Codes

- `200` — successful GET, PUT/PATCH that returns the updated resource
- `201` — successful POST that creates a resource
- `204` — successful DELETE (no body)
- `400` — malformed request / business rule violation
- `401` — unauthenticated
- `403` — authenticated but not authorized
- `404` — resource not found
- `422` — validation error (Zod parse failure)
- `500` — unhandled server error

## Anti-Patterns

- Do not put business logic inside handlers — call a service function instead
- Do not catch and swallow errors in handlers — let them propagate to the global error handler
- Do not return different shapes for success vs error — use consistent `{ data }` / `{ error }` envelopes
- Do not use `c.req.json()` without validation when the body is user-controlled
