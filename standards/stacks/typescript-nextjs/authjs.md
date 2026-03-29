# Auth.js v5 (NextAuth) Standards (Next.js)

## Package
Use `next-auth@beta` (v5, App Router compatible) + `@auth-kit/drizzle-adapter` or the built-in Drizzle adapter.

```bash
npm install next-auth@beta
```

## Required Environment Variables
```env
AUTH_SECRET=              # 32+ random bytes: openssl rand -hex 32
AUTH_URL=                 # e.g. http://localhost:3000 (optional in prod if AUTH_SECRET set)

# OAuth providers (add as needed)
AUTH_GOOGLE_ID=
AUTH_GOOGLE_SECRET=

AUTH_GITHUB_ID=
AUTH_GITHUB_SECRET=
```

Never commit these. Use `.env.local` for local dev.

## Config File
```ts
// auth.ts (project root)
import NextAuth from 'next-auth'
import { DrizzleAdapter } from '@auth/drizzle-adapter'
import Google from 'next-auth/providers/google'
import Credentials from 'next-auth/providers/credentials'
import { db } from '@/db'
import { z } from 'zod'
import { userService } from '@/services/user'

export const { handlers, signIn, signOut, auth } = NextAuth({
  adapter: DrizzleAdapter(db),
  providers: [
    Google,
    Credentials({
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        const parsed = z.object({
          email: z.string().email(),
          password: z.string().min(8),
        }).safeParse(credentials)
        if (!parsed.success) return null
        return userService.verifyCredentials(parsed.data)
      },
    }),
  ],
  session: { strategy: 'database' },
  pages: {
    signIn: '/login',
    error: '/login',
  },
})
```

## Route Handler
```ts
// app/api/auth/[...nextauth]/route.ts
import { handlers } from '@/auth'
export const { GET, POST } = handlers
```

## Protecting Routes (Middleware)
```ts
// middleware.ts
import { auth } from '@/auth'
import { NextResponse } from 'next/server'

export default auth((req) => {
  if (!req.auth) {
    return NextResponse.redirect(new URL('/login', req.url))
  }
})

export const config = {
  matcher: ['/dashboard/:path*', '/api/workouts/:path*', '/api/exercises/:path*'],
}
```

## Getting the Session

**Server Component / Route Handler:**
```ts
import { auth } from '@/auth'

const session = await auth()
// session.user.id = DB user ID (via DrizzleAdapter)
// session.user.email, session.user.name
```

**Client Component:**
```tsx
'use client'
import { useSession } from 'next-auth/react'

const { data: session, status } = useSession()
```

Wrap the root layout with `<SessionProvider>` for client-side session access:
```tsx
// app/layout.tsx
import { SessionProvider } from 'next-auth/react'
import { auth } from '@/auth'

export default async function RootLayout({ children }) {
  const session = await auth()
  return (
    <html>
      <body>
        <SessionProvider session={session}>{children}</SessionProvider>
      </body>
    </html>
  )
}
```

## DB Schema (Drizzle — required by DrizzleAdapter)
Auth.js requires these tables. Generate via the adapter's schema helper or add manually:
- `users` — id, name, email, emailVerified, image
- `accounts` — OAuth account links
- `sessions` — active sessions
- `verificationTokens` — email verification

Extend `users` with your app fields (e.g. `unitPreference`, `displayName`) in the same table.

## Password Hashing (for Credentials provider)
```ts
// lib/password.ts
import bcrypt from 'bcryptjs'

export const hashPassword = (plain: string) => bcrypt.hash(plain, 12)
export const verifyPassword = (plain: string, hash: string) => bcrypt.compare(plain, hash)
```

Store the hash in a `password` column on `users` (nullable — null for OAuth users).

## Rules
- Never store plain-text passwords — always bcrypt hash with cost ≥12
- Use `session: { strategy: 'database' }` (not JWT) for server-side session revocation
- All API route handlers must call `auth()` and check for a valid session before touching data
- Wrap `authorize()` in Credentials provider with Zod validation — never trust raw input
- OAuth users have no password; Credentials users have no OAuth account — handle both gracefully
