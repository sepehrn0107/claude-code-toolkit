# pnpm + Turborepo Standards

Standards for TypeScript monorepos using pnpm workspaces and Turborepo.

## Stack Profile

- **Package manager**: [pnpm](https://pnpm.io/) workspaces
- **Build orchestration**: [Turborepo](https://turborepo.dev/)
- **Language**: TypeScript throughout
- **Package namespace**: `@autocarline/<name>`
- **Testing**: each package owns its test script; Turbo caches results

## Files in This Directory

| File | Topic |
|------|-------|
| `README.md` | This file — stack overview and file index |
| `naming.md` | Naming conventions for packages, workspaces, exports |
| `structure.md` | Workspace layout — apps/, packages/, services/ |
| `pipeline.md` | Turbo pipeline config, caching, CI filter patterns |
| `testing.md` | Per-package testing conventions and Turbo test caching |

## Non-Goals

These standards do not cover:
- Per-app framework standards (see typescript-react, typescript-hono, etc.)
- Remote caching setup (infrastructure concern — document per project)
- Changesets / release management (document separately if adopted)
