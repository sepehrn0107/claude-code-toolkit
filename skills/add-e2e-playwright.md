---
name: add-e2e-playwright
description: Adds @playwright/cli (AI navigation) and @playwright/test (E2E specs) to an existing project. Run when the user asks to add E2E testing, playwright, or AI browser navigation.
---

# /add-e2e-playwright

Adds Playwright to an existing project: CLI for AI navigation + test runner for writing specs.

## Background: CLI vs MCP

- **`@playwright/cli`** — global CLI optimised for coding agents. Token-efficient (no accessibility tree in context). Installs "skills" that Claude Code uses automatically.
- **`@playwright/test`** — dev dependency for writing and running E2E test specs.
- **Playwright MCP** — alternative for long-running agentic loops needing persistent browser state. Not needed for typical coding-agent + test workflows.

## Steps

### 1. Install `@playwright/cli` globally
```bash
npm install -g @playwright/cli@latest
```

### 2. Install skills in the project root
```bash
playwright-cli install --skills
```
This creates `.claude/skills/playwright-cli/` in the project. Skills are workspace-scoped — must be re-run for each project.

### 3. Install `@playwright/test`
```bash
npm install --save-dev @playwright/test
```

### 4. Install the browser
```bash
npx playwright install chromium
```
`@playwright/cli` auto-detects system Chrome; `@playwright/test` needs its own managed binary.

### 5. Create `playwright.config.ts` in the project root

For a Next.js project:
```ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: process.env.E2E_BASE_URL ?? 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
  webServer: process.env.CI
    ? {
        command: 'npm run start',
        url: 'http://localhost:3000',
        reuseExistingServer: false,
      }
    : undefined,
});
```

Key decisions:
- `testDir: './e2e'` — keeps E2E specs outside `src/` so vitest doesn't pick them up
- `webServer` only in CI — dev workflow assumes the dev server is already running
- `E2E_BASE_URL` env var allows overriding for staging/preview environments

### 6. Create `e2e/` with a starter auth spec

```ts
// e2e/auth.spec.ts
import { test, expect } from '@playwright/test';

test.describe('auth', () => {
  test('redirects unauthenticated user to login', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/login|\/signin/);
  });

  test('login page renders', async ({ page }) => {
    await page.goto('/login');
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
  });
});
```

### 7. Add scripts to `package.json`
```json
"test:e2e": "playwright test",
"test:e2e:ui": "playwright test --ui",
"test:e2e:debug": "playwright test --debug"
```

### 8. Check vitest config excludes `e2e/`

If the project uses vitest, confirm `vitest.config.ts` or `vite.config.ts` does not include `e2e/`. Vitest's default exclude covers `node_modules` but not a top-level `e2e/` directory if it contains `.spec.ts` files. Add explicitly if needed:
```ts
test: {
  exclude: ['node_modules', 'e2e/**'],
}
```

## Usage after setup

```bash
# Run all E2E tests (dev server must be running)
npm run test:e2e

# Interactive UI mode for debugging
npm run test:e2e:ui

# Ask Claude to navigate the app
# "Use playwright-cli to test the login flow on localhost:3000"
```

## Key distinctions to remember
- `@playwright/cli` is global — install once per machine, skills per project
- `@playwright/test` is a dev dep — install per project
- Never put E2E tests inside `src/` — vitest will pick them up
- In dev: start the server manually before running `npm run test:e2e`
- In CI: `webServer` in `playwright.config.ts` handles server startup
