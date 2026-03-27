# TypeScript Standards

## Configuration
- `strict: true` in `tsconfig.json` — always, no exceptions
- `noUncheckedIndexedAccess: true` — catches undefined array access at compile time
- `exactOptionalPropertyTypes: true` — distinguishes missing from undefined

## No `any`
- Never use `any` — use `unknown` with type narrowing instead
- If a third-party type is poorly typed, use a local type assertion at the boundary and document why
- `// @ts-ignore` is banned — use `// @ts-expect-error` with a comment if unavoidable

## Props
- Props interface named `<ComponentName>Props`, colocated with the component
- Export props type — consumers may need it

```tsx
// UserCard.tsx
export interface UserCardProps {
  userId: string
  isEditable?: boolean
}

export function UserCard({ userId, isEditable = false }: UserCardProps) { ... }
```

## Types vs Interfaces
- `type` for unions, intersections, and computed types
- `interface` for object shapes that may be extended or implemented

```ts
type Status = 'idle' | 'loading' | 'error' | 'success'  // union → type
interface User { id: string; name: string }              // object shape → interface
```

## Type Assertions
- Avoid `as` except at system boundaries (API responses, DOM events)
- Never use `as any` — it defeats the type system entirely
- Prefer type guards over assertions:

```ts
// prefer this
function isUser(value: unknown): value is User {
  return typeof value === 'object' && value !== null && 'id' in value
}

// over this
const user = response as User
```

## Generics
- Name type parameters descriptively for public APIs: `TItem`, `TResult`, not just `T`
- Single-letter `T` is acceptable in short, obvious utility types
```
