# Routing Standards (Next.js App Router)

## Use App Router
- Always use App Router (`app/` directory) — Pages Router only for legacy projects being migrated
- Document the router choice in `.claude/memory/stack.md`

## File Conventions
| File | Role |
|------|------|
| `page.tsx` | The unique UI for a route — makes it publicly accessible |
| `layout.tsx` | Shared shell wrapping a segment and its children |
| `loading.tsx` | Automatic Suspense fallback for the segment |
| `error.tsx` | Error boundary for the segment — must be a Client Component |
| `not-found.tsx` | UI for `notFound()` calls within the segment |
| `template.tsx` | Like a layout but creates a new instance on each navigation — use for animations or per-page state reset |
| `default.tsx` | Fallback UI for a parallel route slot when no match exists |
| `route.ts` | API Route Handler — no UI |

## Route Organization
- Route groups `(groupName)/` organize routes without affecting the URL
- Use route groups to share layouts between routes that don't share a URL prefix
- Dynamic segments: `[slug]`, catch-all: `[...slug]`, optional catch-all: `[[...slug]]`
- Parallel routes `@slot/` for simultaneously rendered route segments (dashboards, modals)

## Naming
- Route segment folders: `kebab-case`
- Dynamic segment folders: `[camelCase]` (e.g., `[userId]`)
