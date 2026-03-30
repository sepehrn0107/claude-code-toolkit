# Auth.js / NextAuth Standards (Next.js)

> **Version warning:** This file documents Auth.js **v5 (beta)**. If your project uses
> `next-auth@^4` (stable), the APIs are incompatible — `auth()`, `handlers`, and
> `DrizzleAdapter` do not exist in v4. Always check your project's ADR before applying
> these patterns.
>
> **next-auth v4 quick reference** (JWT strategy, no adapter tables):
> ```ts
> // auth.ts
> import type { NextAuthOptions } from 'next-auth'
> import CredentialsProvider from 'next-auth/providers/credentials'
> export const authOptions: NextAuthOptions = {
>   session: { strategy: 'jwt' },
>   providers: [CredentialsProvider({ ... })],
>   callbacks: {
>     async jwt({ token, user }) {
>       if (user) { token.id = user.id; token.role = user.role; }
>       return token;
>     },
>     async session({ session, token }) {
>       session.user.id = token.id as string;
>       session.user.role = token.role as 'customer' | 'admin';
>       return session;
>     },
>   },
> }
>
> // app/api/auth/[...nextauth]/route.ts
> import NextAuth from 'next-auth'
> import { authOptions } from '@/lib/auth/config'
> const handler = NextAuth(authOptions)
> export { handler as GET, handler as POST }
>
> // middleware.ts
> import { withAuth } from 'next-auth/middleware'
> export default withAuth(fn, { callbacks: { authorized: ({ token }) => !!token } })
>
> // Server helpers
> import { getServerSession } from 'next-auth/next'
> const session = await getServerSession(authOptions)  // NOT auth()
> ```
>
> v4 advantages: stable release, no sessions/accounts/verificationTokens tables (JWT is
> stateless), edge middleware reads JWT without DB hit. Tradeoff: no server-side session
> revocation without a token blocklist.

## Auth.js v5 (NextAuth beta)

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

## OTP Email Verification (Credentials provider)

When using the Credentials provider, gate sign-in on email verification via a 6-digit OTP sent on registration.

**Schema:**
```ts
// db/schema/otp-tokens.ts
export const otpTokens = pgTable('otp_tokens', {
  id:        uuid('id').primaryKey().defaultRandom(),
  userId:    uuid('user_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  code:      varchar('code', { length: 6 }).notNull(),
  expiresAt: timestamp('expires_at').notNull(),
  usedAt:    timestamp('used_at'),
})
```

**Service:**
```ts
// services/otp.service.ts
export async function generateOtp(userId: string) {
  const code = Math.floor(100000 + Math.random() * 900000).toString()
  const expiresAt = new Date(Date.now() + 10 * 60 * 1000) // 10 min TTL
  await db.insert(otpTokens).values({ userId, code, expiresAt })
  return code
}

export async function verifyOtp(userId: string, code: string) {
  const token = await db.query.otpTokens.findFirst({
    where: and(
      eq(otpTokens.userId, userId),
      eq(otpTokens.code, code),
      isNull(otpTokens.usedAt),
      gt(otpTokens.expiresAt, new Date()),
    ),
  })
  if (!token) throw new UnauthorizedError('Invalid or expired code')
  await db.update(otpTokens).set({ usedAt: new Date() }).where(eq(otpTokens.id, token.id))
}
```

**Registration flow:** create user (unverified) → generate OTP → send email → redirect to `/verify-email` → call `verifyOtp()` → set `emailVerified = new Date()` → redirect to sign-in.

**`authorize()` guard:**
```ts
async authorize(credentials) {
  const user = await userService.verifyCredentials(parsed.data)
  if (!user.emailVerified) throw new Error('EMAIL_NOT_VERIFIED')
  return user
}
```

## Rules
- Never store plain-text passwords — always bcrypt hash with cost ≥12
- Use `session: { strategy: 'database' }` (not JWT) for server-side session revocation
- All API route handlers must call `auth()` and check for a valid session before touching data
- Wrap `authorize()` in Credentials provider with Zod validation — never trust raw input
- OAuth users have no password; Credentials users have no OAuth account — handle both gracefully
- OTP tokens: store in a dedicated table (not `users`), mark `usedAt` on consumption (don't delete), enforce expiry in the DB query
