# TypeScript + Hono Standards

Standards for projects using Hono as the API backend with TypeScript — REST + OpenAPI, deployed on Fly.io.

## Stack Profile

- **Framework**: [Hono](https://hono.dev/) — ultrafast Web Standards-based framework
- **Validation**: Zod via `@hono/zod-openapi`
- **Runtime**: Node.js or Bun; deployed on Fly.io
- **Build**: esbuild or tsc
- **Testing**: Vitest + `@hono/testing`

## Files in This Directory

| File | Topic |
|------|-------|
| `README.md` | This file — stack overview and file index |
| `naming.md` | Naming conventions for files, routes, variables, types |
| `structure.md` | Project layout and module organization |
| `routing.md` | Route factories, typed handlers, OpenAPI registration |
| `middleware.md` | Middleware chains and `c.var` context patterns |
| `testing.md` | Testing approach with Vitest + `@hono/testing` |

## Non-Goals

These standards do not cover:
- Frontend rendering (Hono JSX is not used in this stack)
- WebSocket or SSE patterns (document separately per project)
- Database access patterns (see drizzle-postgres standards if applicable)
