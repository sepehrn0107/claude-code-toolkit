# Testing Standards — Hono

## Stack

- **Runner**: Vitest
- **HTTP test client**: `@hono/testing` (provides `testClient` for type-safe fetch)
- **No real server** is started in unit/integration tests — use the in-process test client

## Test Scope

| Layer | What to test |
|-------|-------------|
| Handler (route) | HTTP behavior — status codes, response shape, auth enforcement |
| Service | Business logic — pure functions, no HTTP |
| Middleware | Isolation tests for each middleware |
| Schema | Zod schema parse/refine edge cases |

## Testing Handlers with `testClient`

```ts
// users.route.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { testClient } from 'hono/testing'
import { userRoute } from './users.route'
import * as usersService from '../services/users.service'

vi.mock('../services/users.service')

describe('GET /users', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('returns 200 with a list of users', async () => {
    const mockUsers = [{ id: '1', name: 'Alice' }]
    vi.mocked(usersService.listUsers).mockResolvedValue(mockUsers)

    const client = testClient(userRoute)
    const res = await client.index.$get()

    expect(res.status).toBe(200)
    const body = await res.json()
    expect(body).toEqual(mockUsers)
  })

  it('returns 401 when auth header is missing', async () => {
    const client = testClient(userRoute)
    const res = await client.index.$post({})

    expect(res.status).toBe(401)
  })
})
```

## Testing Services

Services are plain functions — test them without any HTTP setup:

```ts
// users.service.test.ts
import { describe, it, expect, vi } from 'vitest'
import { createUser } from './users.service'
import * as db from '../lib/db'

vi.mock('../lib/db')

describe('createUser', () => {
  it('inserts a user and returns it', async () => {
    const input = { name: 'Bob', email: 'bob@example.com' }
    vi.mocked(db.query).mockResolvedValue({ rows: [{ id: '2', ...input }] })

    const result = await createUser(input)

    expect(result).toMatchObject(input)
  })

  it('throws AppError with code USER_EXISTS when email is taken', async () => {
    vi.mocked(db.query).mockRejectedValue({ code: '23505' }) // Postgres unique violation

    await expect(createUser({ name: 'Bob', email: 'bob@example.com' }))
      .rejects.toMatchObject({ code: 'USER_EXISTS' })
  })
})
```

## Testing Middleware

Test middleware as a standalone Hono app:

```ts
// auth.middleware.test.ts
import { Hono } from 'hono'
import { describe, it, expect, vi } from 'vitest'
import { requireAuth } from './auth.middleware'
import * as tokenLib from '../lib/token'

vi.mock('../lib/token')

function makeApp() {
  const app = new Hono<AppEnv>()
  app.use('*', requireAuth)
  app.get('/protected', (c) => c.json({ ok: true }))
  return app
}

describe('requireAuth middleware', () => {
  it('passes when token is valid', async () => {
    vi.mocked(tokenLib.verifyToken).mockResolvedValue({ id: '1', role: 'user' })

    const res = await makeApp().request('/protected', {
      headers: { Authorization: 'Bearer valid-token' },
    })

    expect(res.status).toBe(200)
  })

  it('returns 401 when Authorization header is absent', async () => {
    const res = await makeApp().request('/protected')
    expect(res.status).toBe(401)
  })
})
```

## Testing Zod Schemas

```ts
// user.schema.test.ts
import { describe, it, expect } from 'vitest'
import { userCreateSchema } from './user.schema'

describe('userCreateSchema', () => {
  it('accepts valid input', () => {
    const result = userCreateSchema.safeParse({ name: 'Alice', email: 'alice@example.com' })
    expect(result.success).toBe(true)
  })

  it('rejects an invalid email', () => {
    const result = userCreateSchema.safeParse({ name: 'Alice', email: 'not-an-email' })
    expect(result.success).toBe(false)
  })
})
```

## Structure

- One test file per source file: `users.route.test.ts` alongside `users.route.ts`
- Test file naming: `<source-file>.test.ts`
- Group with `describe` matching the function or route name
- Test names describe the behavior: `'returns 404 when user is not found'`
- Arrange → Act → Assert pattern in each test

## Anti-Patterns

- Do not test that a Zod schema is called in a handler — test the HTTP behavior instead
- Do not start a real HTTP server in tests — use `testClient` or `app.request()`
- Do not share state between tests — use `beforeEach` to reset mocks
- Do not write handler tests that depend on a real database — mock the service layer
