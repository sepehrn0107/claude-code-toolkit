# Project Structure — Hono

## Directory Layout

```
src/
  app.ts              # Hono app factory — assembles routes and global middleware
  index.ts            # Entry point — binds app to port/runtime adapter
  routes/
    users.route.ts
    auth.route.ts
    health.route.ts
  services/
    users.service.ts  # Business logic — no Hono types imported here
    auth.service.ts
  middleware/
    auth.middleware.ts
    logger.middleware.ts
    cors.middleware.ts
  schemas/
    user.schema.ts    # Zod input/output schemas
    auth.schema.ts
  types/
    app.ts            # AppEnv, Variables, Bindings types
  lib/
    db.ts             # Database client singleton
    redis.ts          # Redis client if used
    env.ts            # Typed environment variables
```

## App Factory Pattern

Assemble routes and middleware in `app.ts`, not `index.ts`. This allows `app.ts` to be imported in tests without starting a server.

```ts
// app.ts
import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { logger } from 'hono/logger'
import { userRoute } from './routes/users.route'
import { authRoute } from './routes/auth.route'

export function createApp() {
  const app = new Hono<AppEnv>()

  // Global middleware — order matters
  app.use('*', logger())
  app.use('*', cors())

  // Routes
  app.route('/api/users', userRoute)
  app.route('/api/auth', authRoute)

  return app
}

// index.ts
import { serve } from '@hono/node-server'
import { createApp } from './app'
import { env } from './lib/env'

serve({ fetch: createApp().fetch, port: env.PORT })
```

## Layers and Responsibilities

| Layer | Imports | Does NOT import |
|-------|---------|-----------------|
| Route/Handler | Hono, services, schemas | Database, Redis directly |
| Service | Domain types, lib | Hono `Context`, `Request`, `Response` |
| Lib | Third-party clients | Services, routes |
| Schema | Zod | Everything else |

Business logic must never appear in route handlers. The handler's only job is:
1. Extract validated input from the context
2. Call a service function
3. Return the response

```ts
// users.route.ts — handler is thin
const createUserHandler: Handler<AppEnv> = async (c) => {
  const body = c.req.valid('json')          // already validated by Zod middleware
  const user = await createUser(body)       // service call
  return c.json(user, 201)
}
```

## OpenAPI Registration

Use `@hono/zod-openapi` to declare routes with input/output schemas and generate the OpenAPI spec automatically.

```ts
import { createRoute, z } from '@hono/zod-openapi'
import { OpenAPIHono } from '@hono/zod-openapi'

const route = createRoute({
  method: 'post',
  path: '/users',
  request: { body: { content: { 'application/json': { schema: userCreateSchema } } } },
  responses: {
    201: { content: { 'application/json': { schema: userResponseSchema } }, description: 'Created' },
    422: { description: 'Validation error' },
  },
})

export const userRoute = new OpenAPIHono<AppEnv>()
userRoute.openapi(route, createUserHandler)
```

Register the OpenAPI doc endpoint once in `app.ts`:

```ts
app.doc('/openapi.json', { openapi: '3.1.0', info: { title: 'API', version: '1.0.0' } })
```

## File Size Rule

Keep handler files under ~120 lines. If a route file grows beyond this, the handlers have too much logic — move it to a service.
