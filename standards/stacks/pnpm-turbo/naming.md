# Naming Conventions — pnpm + Turborepo

## Package Names

- Namespace: `@autocarline/<name>` — all internal packages share this scope
- Package name segment: `kebab-case` — `@autocarline/contract`, `@autocarline/ui`, `@autocarline/utils`
- Keep names short and intent-revealing — `@autocarline/ui` not `@autocarline/shared-ui-components`

## Workspace Folders

```
apps/          # Deployable applications (Next.js apps, Hono APIs)
packages/      # Shared libraries consumed by apps and services
services/      # Backend processes (BullMQ workers, cron services)
```

- Folder name inside each category: `kebab-case` — `apps/dashboard`, `packages/contract`, `services/email-worker`
- Each workspace folder contains one package with its own `package.json`

## Package Directory Structure

Each package in `packages/` or `services/` follows this layout:

```
packages/<name>/
  src/
    index.ts     # Public API — everything exported from here
  package.json
  tsconfig.json
  vitest.config.ts
```

## Exports

Every shared package must declare a `main` export in `package.json` pointing to `src/index.ts` (dev mode, no compilation):

```json
{
  "name": "@autocarline/utils",
  "exports": {
    ".": "./src/index.ts"
  }
}
```

Only export from `src/index.ts` — never import deep paths from another package:

```ts
// Good
import { formatDate } from '@autocarline/utils'

// Bad — breaks encapsulation
import { formatDate } from '@autocarline/utils/src/date/formatDate'
```

## Turbo Task Names

- Task names (in `turbo.json`): `camelCase` matches the `package.json` script name
- Standard scripts every package must have: `build`, `test`, `lint`, `type-check`

```json
// Each package's package.json
{
  "scripts": {
    "build": "tsc",
    "test": "vitest run",
    "lint": "eslint src",
    "type-check": "tsc --noEmit"
  }
}
```

## Version Pinning for Internal Packages

Internal package references use `workspace:*` — never a pinned version:

```json
{
  "dependencies": {
    "@autocarline/contract": "workspace:*",
    "@autocarline/utils": "workspace:*"
  }
}
```

## Contract Package (Single Source of Truth)

`packages/contract` is the canonical location for all Zod schemas and generated TypeScript types shared between frontend and backend. No type definitions that describe the API shape live anywhere else.

- Schema file per domain: `src/schemas/<domain>.schema.ts`
- Generated type: exported alongside the schema — `export type User = z.infer<typeof userSchema>`
