# Workspace Structure — pnpm + Turborepo

## Root Layout

```
.
├── apps/
│   ├── dashboard/          # Next.js or Vite React app
│   │   ├── src/
│   │   ├── package.json
│   │   └── tsconfig.json
│   └── api/                # Hono backend
│       ├── src/
│       ├── package.json
│       └── tsconfig.json
├── packages/
│   ├── contract/           # Single source of truth — Zod schemas + inferred types
│   │   ├── src/
│   │   │   ├── schemas/
│   │   │   └── index.ts
│   │   └── package.json
│   ├── ui/                 # Shared React components
│   ├── utils/              # Shared TypeScript utilities (no framework deps)
│   └── eslint-config/      # Shared ESLint config
├── services/
│   └── email-worker/       # BullMQ worker process
│       ├── src/
│       └── package.json
├── turbo.json
├── pnpm-workspace.yaml
├── package.json            # Root — no dependencies, only devDependencies for tooling
└── tsconfig.base.json      # Shared TypeScript base config
```

## pnpm Workspace Declaration

```yaml
# pnpm-workspace.yaml
packages:
  - 'apps/*'
  - 'packages/*'
  - 'services/*'
```

## Root `package.json`

The root is a tooling host only — it does not export code.

```json
{
  "private": true,
  "scripts": {
    "build": "turbo run build",
    "test": "turbo run test",
    "lint": "turbo run lint",
    "type-check": "turbo run type-check",
    "dev": "turbo run dev --parallel"
  },
  "devDependencies": {
    "turbo": "^2.0.0",
    "typescript": "^5.0.0"
  }
}
```

## TypeScript Configuration

Use a shared `tsconfig.base.json` at the root. Each package extends it:

```json
// tsconfig.base.json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "moduleResolution": "bundler",
    "module": "ESNext",
    "target": "ES2022",
    "skipLibCheck": true
  }
}
```

```json
// packages/utils/tsconfig.json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "outDir": "dist",
    "rootDir": "src"
  },
  "include": ["src"]
}
```

## Shared ESLint Config

Create `packages/eslint-config/` as a package that exports a shared config:

```ts
// packages/eslint-config/src/index.ts
export default {
  extends: ['eslint:recommended', 'plugin:@typescript-eslint/strict'],
  // ...
}
```

Each workspace package references it:
```json
// apps/dashboard/.eslintrc.json
{ "extends": ["@autocarline/eslint-config"] }
```

## Dependency Rules

- Internal packages: `workspace:*` only — never pin to a version number
- No circular dependencies between packages — enforced by Turbo's `dependsOn` graph
- `packages/contract` must not import from `apps/` or `services/` — it is a leaf package
- `packages/utils` must not import from `packages/ui` — utilities have no UI dependency

## The Contract Package

`packages/contract` is the only permitted location for types that describe API shapes or data contracts.

```ts
// packages/contract/src/schemas/user.schema.ts
import { z } from 'zod'

export const userSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1),
  email: z.string().email(),
  createdAt: z.string().datetime(),
})

export type User = z.infer<typeof userSchema>
```

```ts
// packages/contract/src/index.ts — re-export everything
export * from './schemas/user.schema'
export * from './schemas/booking.schema'
```

Both the API (`apps/api`) and the dashboard (`apps/dashboard`) import from `@autocarline/contract`. No type is copied — ever.

## Adding a New Package

1. Create `packages/<name>/` with `src/index.ts` and `package.json`
2. Set `"name": "@autocarline/<name>"` and add the standard scripts
3. Add `"@autocarline/<name>": "workspace:*"` to any consumer's `package.json`
4. Run `pnpm install` to link it
5. Add a `dependsOn` entry in `turbo.json` if the new package's build must precede a consumer's build
