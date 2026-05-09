# Naming Conventions — Hono

## Files

- Route files: `kebab-case.route.ts` (e.g., `users.route.ts`, `auth.route.ts`)
- Handler files (if separated): `kebab-case.handler.ts`
- Service files: `kebab-case.service.ts`
- Middleware files: `kebab-case.middleware.ts`
- Schema/validation files: `kebab-case.schema.ts`
- Types-only files: `kebab-case.types.ts`
- App entry point: `index.ts` or `app.ts`

## Folders

```
src/
  routes/         # Hono router instances, one file per resource
  services/       # Business logic (no Hono imports)
  middleware/     # Custom middleware
  schemas/        # Zod schemas for request/response
  types/          # Shared TypeScript types
  lib/            # Third-party wrappers (db client, mailer, etc.)
```

## Routes

- Path segments: `kebab-case` (`/user-profiles/:id`, not `/userProfiles/:id`)
- Route group (Hono app): named as `<resource>Route` — `userRoute`, `authRoute`
- Route factory return value: `Hono` instance, typed with `AppEnv`

```ts
// users.route.ts
export const userRoute = new Hono<AppEnv>()
  .get('/', listUsersHandler)
  .post('/', createUserHandler)
  .get('/:id', getUserHandler)
```

## Variables and Functions

- Handler functions: `<verb><Resource>Handler` — `listUsersHandler`, `createUserHandler`
- Service functions: `<verb><Resource>` — `listUsers`, `createUser`, `deleteUser`
- Middleware functions: descriptive verb — `requireAuth`, `attachCurrentUser`, `logRequest`
- Context variable keys: `camelCase` string literals registered via `c.var` — `'currentUser'`, `'requestId'`

## Types

- `PascalCase` throughout
- Hono environment type: `AppEnv` (single shared type in `types/app.ts`)
- Request body types: `<Resource>CreateInput`, `<Resource>UpdateInput`
- Response types: `<Resource>Response`, `<Resource>ListResponse`
- No `I` prefix — `UserResponse` not `IUserResponse`

## Zod Schemas

- Schema variable: `<resource><Operation>Schema` — `userCreateSchema`, `userParamsSchema`
- Colocate in `schemas/` or alongside the route if the schema is route-specific only

```ts
// schemas/user.schema.ts
export const userCreateSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
})
export type UserCreateInput = z.infer<typeof userCreateSchema>
```

## Environment Variables

- Access via a typed `env` object initialized at startup — never call `process.env` directly in handlers
- Variable names: `SCREAMING_SNAKE_CASE` in the environment; camelCase property names in the typed wrapper

```ts
// lib/env.ts
import { z } from 'zod'
const envSchema = z.object({
  DATABASE_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
  PORT: z.coerce.number().default(3000),
})
export const env = envSchema.parse(process.env)
```
