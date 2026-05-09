# Testing Standards — pnpm + Turborepo

## Principle: Each Package Owns Its Tests

Tests are not centralized. Every package runs its own test script with its own test runner and configuration. Turbo orchestrates running them all (or a subset) with caching.

```bash
# Run all tests across the monorepo (with caching)
pnpm turbo test

# Run tests for a single package
pnpm turbo test --filter=@autocarline/contract

# Run tests for a package and all packages that depend on it
pnpm turbo test --filter=...@autocarline/contract
```

## Per-Package Test Configuration

Each package that has tests must have:
- A `test` script in its `package.json`
- A `vitest.config.ts` (or framework-specific test config)
- Its own test dependencies declared in its `package.json`

```json
// packages/utils/package.json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest"
  },
  "devDependencies": {
    "vitest": "^2.0.0"
  }
}
```

```ts
// packages/utils/vitest.config.ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    include: ['src/**/*.test.ts'],
    coverage: {
      reporter: ['text', 'lcov'],
      reportsDirectory: 'coverage',
    },
  },
})
```

## Testing the Contract Package

The `packages/contract` package contains only Zod schemas and types. Tests verify schema correctness:

```ts
// packages/contract/src/schemas/user.schema.test.ts
import { describe, it, expect } from 'vitest'
import { userSchema } from './user.schema'

describe('userSchema', () => {
  it('accepts a valid user', () => {
    const result = userSchema.safeParse({
      id: '550e8400-e29b-41d4-a716-446655440000',
      name: 'Alice',
      email: 'alice@example.com',
      createdAt: '2024-01-01T00:00:00.000Z',
    })
    expect(result.success).toBe(true)
  })

  it('rejects an invalid email', () => {
    const result = userSchema.safeParse({ id: 'x', name: 'A', email: 'not-email', createdAt: '2024' })
    expect(result.success).toBe(false)
  })
})
```

## Turbo Task Configuration for Tests

Declare `test` in `turbo.json` with `dependsOn: ["^build"]` so upstream packages are built before tests run.

```json
"test": {
  "dependsOn": ["^build"],
  "inputs": ["src/**", "vitest.config.ts", "tsconfig.json"],
  "outputs": ["coverage/**"],
  "cache": true
}
```

With `cache: true`, Turbo skips re-running tests if the inputs haven't changed. This makes CI dramatically faster for large repos.

## Cross-Package Type Testing

If `packages/contract` exports types consumed by `apps/api`, type-check the consumer to catch contract breaks:

```bash
pnpm turbo type-check --filter=@autocarline/api
```

Always run `type-check` in CI after `build` — it catches import/type errors that tests may not surface.

## Test Isolation

- Each package's tests run in isolation — no shared test state across packages
- Do not import test utilities from another package's `src/` — create a `packages/test-utils/` package if shared setup is needed
- `packages/test-utils` is a devDependency; never a production dependency

## CI Matrix (Optional)

For large monorepos, split the CI `test` step by affected packages:

```yaml
- name: Test affected packages
  run: pnpm turbo test --filter='[HEAD^1]'
```

This runs tests only for packages whose files changed since the previous commit, plus packages that depend on them.

## Anti-Patterns

- Do not run tests from the root with a glob (e.g., `vitest run packages/*/src`) — each package must own its own test run
- Do not share a single `vitest.config.ts` at the root — test configs belong per-package
- Do not skip declaring `outputs: ["coverage/**"]` — Turbo cannot cache test results without it
- Do not import from `../../packages/utils/src/index.ts` using relative paths — use the package name `@autocarline/utils`
