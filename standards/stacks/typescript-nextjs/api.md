# API and Data Standards (Next.js)

## Server Actions
Use Server Actions for mutations triggered from the UI (form submissions, button clicks).

```tsx
// app/actions/user.ts
'use server'

import { z } from 'zod'

const UpdateProfileSchema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
})

export async function updateProfile(formData: FormData) {
  const parsed = UpdateProfileSchema.safeParse({
    name: formData.get('name'),
    email: formData.get('email'),
  })
  if (!parsed.success) throw new Error('Invalid input')
  // delegate to service layer
  await userService.update(parsed.data)
}
```

## Route Handlers
Use Route Handlers (`app/.../route.ts`) for API endpoints consumed by external clients or third-party webhooks.

```ts
// app/api/users/[id]/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function GET(req: NextRequest, { params }: { params: { id: string } }) {
  const user = await userService.findById(params.id)
  if (!user) return NextResponse.json({ error: 'Not found' }, { status: 404 })
  return NextResponse.json(user)
}
```

## Rules
- No business logic in Server Actions or Route Handlers — delegate to service/domain functions
- Validate all inputs at the boundary with Zod — never trust client-provided data
- Return consistent error shapes from Route Handlers: `{ error: string }`
- Server Actions throw errors; Route Handlers return `NextResponse` with status codes

## What Not to Do
- Do not create a Route Handler for mutations that are only called from your own UI — use Server Actions
- Do not fetch from your own Route Handlers inside Server Components — call the service function directly
