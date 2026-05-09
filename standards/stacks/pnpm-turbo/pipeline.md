# Turbo Pipeline — pnpm + Turborepo

## `turbo.json` Structure

Define every task the monorepo supports. Turbo uses this to determine execution order, caching, and parallelism.

```json
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**", "!.next/cache/**"]
    },
    "test": {
      "dependsOn": ["^build"],
      "outputs": ["coverage/**"],
      "cache": true
    },
    "lint": {
      "dependsOn": [],
      "outputs": [],
      "cache": true
    },
    "type-check": {
      "dependsOn": ["^build"],
      "outputs": [],
      "cache": false
    },
    "dev": {
      "cache": false,
      "persistent": true
    }
  }
}
```

## `dependsOn` Rules

- `"^build"` — run this task only after all **upstream workspace dependencies** have built. Use this for `build`, `test`, and `type-check`.
- `"build"` (no `^`) — run this package's own `build` task first. Use when a task depends on local build output.
- `[]` (empty array) — no dependencies; the task can run immediately. Use for `lint`.
- Never declare circular `dependsOn` — Turbo will error on this.

```
packages/contract (build) → apps/api (build) → apps/dashboard (build)
                         ↘ services/email-worker (build)
```

## Caching

Cache is keyed on input files, task configuration, and environment variables. Turbo caches `outputs` declared in `turbo.json`.

- Always declare `outputs` for `build` tasks — without this Turbo cannot restore cache artifacts
- `cache: false` for `dev` (never cache the dev server) and `type-check` (types change with deps, hard to hash correctly)
- Inputs default to all files tracked by git in the package. Add `inputs` to narrow the cache key if needed:

```json
"test": {
  "inputs": ["src/**", "vitest.config.ts", "tsconfig.json"],
  "outputs": ["coverage/**"],
  "cache": true
}
```

## Targeted Builds with `--filter`

Use `--filter` to run tasks for a subset of the graph. This is critical for CI to avoid building unrelated packages.

```bash
# Build only the api app and its dependencies
pnpm turbo build --filter=@autocarline/api

# Test only packages changed since the last commit
pnpm turbo test --filter='[HEAD^1]'

# Test a specific package and everything that depends on it
pnpm turbo test --filter=...@autocarline/contract
```

## CI Pipeline

```yaml
# .github/workflows/ci.yml
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 2 }     # Required for --filter=[HEAD^1] to work

      - uses: pnpm/action-setup@v4
        with: { version: 9 }

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: pnpm

      - run: pnpm install --frozen-lockfile

      - name: Build
        run: pnpm turbo build

      - name: Test
        run: pnpm turbo test

      - name: Lint
        run: pnpm turbo lint
```

Run `pnpm install --frozen-lockfile` (not `pnpm install`) in CI — fails loudly if `pnpm-lock.yaml` is out of sync.

## Dev Mode

Run all packages in parallel with `--parallel`:

```bash
pnpm turbo dev --parallel
```

For a subset (e.g., only the API and its contract dep):
```bash
pnpm turbo dev --filter=@autocarline/api...
```

## Environment Variables in Pipelines

Turbo hashes environment variables that affect builds. Declare them in the task's `env` array so cache misses happen when they change:

```json
"build": {
  "dependsOn": ["^build"],
  "env": ["NODE_ENV", "NEXT_PUBLIC_API_URL"],
  "outputs": [".next/**"]
}
```

Do not include secrets in `env` — they will appear in cache keys and potentially logs. Secrets should not influence build output; use runtime env injection instead.

## Anti-Patterns

- Do not run `pnpm install` without `--frozen-lockfile` in CI — version drift is silent and dangerous
- Do not add a package to `apps/` if it is consumed as a library by other packages — it belongs in `packages/`
- Do not create circular dependencies — `packages/contract` must not depend on `apps/*`
- Do not forget to declare `outputs` for build tasks — Turbo cannot cache what it cannot find
- Do not use `--force` to bypass cache in CI unless debugging — cache correctness is critical for speed
