# Middleware Standards — Hono

## Middleware Chains

Hono executes middleware in registration order. Global middleware (logger, CORS, request ID) runs before route-level middleware (auth, validation).

```
Request → logger → cors → requestId → [route match] → requireAuth → zValidator → handler
```

Register global middleware in `app.ts` before mounting routes:

```ts
app.use('*', logger())
app.use('*', cors({ origin: env.ALLOWED_ORIGINS }))
app.use('*', requestId())
```

## `c.var` for Request Context

Use `c.var` to pass data between middleware and handlers. Always declare the variable shape in the `Variables` type so TypeScript enforces it.

```ts
// types/app.ts
export type Variables = {
  currentUser: User
  requestId: string
}
```

```ts
// middleware/auth.middleware.ts
export const requireAuth: MiddlewareHandler<AppEnv> = async (c, next) => {
  const token = c.req.header('Authorization')?.replace('Bearer ', '')
  if (!token) return c.json({ error: 'Unauthorized' }, 401)

  const user = await verifyToken(token)
  if (!user) return c.json({ error: 'Unauthorized' }, 401)

  c.set('currentUser', user)   // typed — must match Variables.currentUser
  await next()
}
```

```ts
// In the handler — type is inferred from Variables
const user = c.get('currentUser')  // type: User
```

## Writing Custom Middleware

A middleware is a function `(c: Context, next: Next) => Promise<void | Response>`.

- Call `await next()` to continue the chain — omitting it short-circuits all downstream handlers
- To modify the response, `await next()` first and then mutate `c.res`
- Return a `Response` (e.g., `return c.json(...)`) to short-circuit — do this for auth failures, rate-limiting, etc.

```ts
// Timing middleware example
export const timing: MiddlewareHandler = async (c, next) => {
  const start = Date.now()
  await next()
  c.res.headers.set('X-Response-Time', `${Date.now() - start}ms`)
}
```

## Auth Middleware Pattern

- `requireAuth` — verifies token, attaches `currentUser` to `c.var`, returns 401 on failure
- `requireRole(role)` — factory that returns middleware checking `currentUser.role`

```ts
export const requireRole = (role: Role): MiddlewareHandler<AppEnv> =>
  async (c, next) => {
    const user = c.get('currentUser')
    if (!user || user.role !== role) return c.json({ error: 'Forbidden' }, 403)
    await next()
  }
```

## Built-in Middleware

Prefer Hono's built-in middleware over custom implementations:

| Need | Built-in |
|------|----------|
| CORS | `hono/cors` |
| Request logging | `hono/logger` |
| Request ID | `hono/request-id` |
| Compression | `hono/compress` |
| Secure headers | `hono/secure-headers` |
| Rate limiting | `hono/rate-limiter` (or third-party) |

## Anti-Patterns

- Do not read the request body in middleware unless the middleware owns validation — `c.req.json()` consumes the body stream
- Do not store mutable shared state in module scope as a substitute for `c.var` — it is not request-scoped
- Do not write auth logic inline in handlers — always extract to `requireAuth` middleware
- Do not apply auth middleware globally and then skip it for public routes — explicitly list public routes and apply auth only to protected groups
