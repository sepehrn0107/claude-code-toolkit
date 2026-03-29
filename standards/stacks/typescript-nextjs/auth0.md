# Auth0 Standards (Next.js)

## Package
Use `@auth0/nextjs-auth0` (v3+, App Router compatible).

## Required Environment Variables
```env
AUTH0_SECRET=                  # 32+ random bytes (openssl rand -hex 32)
AUTH0_BASE_URL=                # e.g. http://localhost:3000
AUTH0_ISSUER_BASE_URL=         # e.g. https://your-tenant.auth0.com
AUTH0_CLIENT_ID=
AUTH0_CLIENT_SECRET=
```
Never commit these. Use `.env.local` for local dev, platform secrets for production.

## Route Setup
Create the Auth0 catch-all handler:

```ts
// app/api/auth/[auth0]/route.ts
import { handleAuth } from '@auth0/nextjs-auth0'
export const GET = handleAuth()
```

This exposes: `/api/auth/login`, `/api/auth/logout`, `/api/auth/callback`, `/api/auth/me`.

## Protecting Routes (Middleware)
```ts
// middleware.ts
import { withMiddlewareAuthRequired } from '@auth0/nextjs-auth0/edge'

export default withMiddlewareAuthRequired()

export const config = {
  matcher: ['/dashboard/:path*', '/api/workouts/:path*'],
}
```

## Getting the Session
**Server Component / Route Handler:**
```ts
import { getSession } from '@auth0/nextjs-auth0'

const session = await getSession()
// session.user.sub = Auth0 user ID
// session.user.email, session.user.name
```

**Client Component:**
```tsx
'use client'
import { useUser } from '@auth0/nextjs-auth0/client'

const { user, isLoading } = useUser()
```

## User Identity in the DB
- Store the Auth0 `sub` (subject) as `external_id` in your `users` table
- On first login, upsert the user record (create if not exists, update profile fields)
- Never store Auth0 tokens in your DB — Auth0 manages sessions

```ts
// lib/auth.ts — helper to get or create local user
import { getSession } from '@auth0/nextjs-auth0'
import { db } from '@/db'
import { users } from '@/db/schema'
import { eq } from 'drizzle-orm'

export async function getOrCreateUser() {
  const session = await getSession()
  if (!session) return null

  const { sub, email, name } = session.user
  const existing = await db.query.users.findFirst({ where: eq(users.externalId, sub) })
  if (existing) return existing

  const [created] = await db.insert(users).values({ externalId: sub, email, name }).returning()
  return created
}
```

## Rules
- All API routes that touch user data must verify the session
- Use `getOrCreateUser()` (or equivalent) at the start of any authenticated handler
- Never expose `sub` or internal IDs in client-facing error messages
- Wrap Auth0 config in a single `lib/auth.ts` — do not scatter SDK calls across handlers
