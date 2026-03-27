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
import { userService } from '@/services/user' // import from your service layer

export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params
  const user = await userService.findById(id)
  if (!user) return NextResponse.json({ error: 'Not found' }, { status: 404 })
  return NextResponse.json(user)
}
```

## Rules
- No business logic in Server Actions or Route Handlers — delegate to service/domain functions
- Validate all inputs at the boundary with Zod — never trust client-provided data
- Return consistent error shapes from Route Handlers: `{ error: string }`
- Server Actions throw errors; Route Handlers return `NextResponse` with status codes

## Server Action Return Values
When used with `useActionState` (React 19 / Next.js 15), return a typed result instead of throwing — this enables field-level error display without an error boundary. Replace the throwing pattern above with this signature:

```ts
type ActionResult = { success: true } | { success: false; error: string }

export async function updateProfileAction(
  _prev: ActionResult,
  formData: FormData
): Promise<ActionResult> {
  const parsed = UpdateProfileSchema.safeParse({
    // extract fields from formData
  })
  if (!parsed.success) return { success: false, error: parsed.error.message }
  await userService.update(parsed.data)
  return { success: true }
}
```

## What Not to Do
- Do not create a Route Handler for mutations that are only called from your own UI — use Server Actions
- Do not fetch from your own Route Handlers inside Server Components — call the service function directly
