# Rendering Standards (Next.js)

## Default: Server Components
- Every component is a Server Component by default — do not add `"use client"` unless required
- Server Components can: fetch data, access backend resources, keep secrets out of the bundle
- Server Components cannot: use hooks, add event listeners, use browser APIs

## When to Add `"use client"`
Add `"use client"` only when the component needs:
- Event handlers (`onClick`, `onChange`, `onSubmit`)
- React hooks (`useState`, `useEffect`, `useContext`, etc.)
- Browser-only APIs (`window`, `localStorage`, `navigator`)
- Third-party libraries that depend on client state

## Push `"use client"` Down the Tree
Keep Client Components as leaf nodes. Do not mark a parent `"use client"` just because one child needs it — extract that child instead.

```tsx
// correct: extract the interactive leaf
export default function ProductPage() {          // Server Component
  return <div><ProductInfo /><AddToCartButton /></div>
}

'use client'
// AddToCartButton.tsx — "use client" scoped to only what needs it
export function AddToCartButton() { ... }
```

## Rendering Strategies
| Strategy | When to Use |
|----------|-------------|
| Static (SSG) | Content does not change per request (marketing pages, docs) |
| Dynamic (SSR) | Content is personalized or must be fresh on every request |
| ISR (`revalidate`) | Content can be stale for a time window (product listings, blog posts) |

Configure via `export const revalidate = N` in the segment, or `{ next: { revalidate: N } }` in `fetch`.

## Data Fetching
- Fetch data in Server Components — avoid fetching in Client Components when possible
- Use `fetch` with Next.js cache options; do not wrap in `useEffect` for initial data
- Next.js 15+: `fetch` is uncached by default (`no-store`) — opt in explicitly with `{ cache: 'force-cache' }` or `export const revalidate`. Next.js 14: `fetch` is cached by default — opt out with `{ cache: 'no-store' }`
- For client-side dynamic data (search, filters), use SWR or React Query
