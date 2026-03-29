# Testing Standards (Next.js)

Extends `typescript-react/testing.md`. All React testing rules apply. This file adds the E2E layer.

## Test Runner Split

| Layer | Tool | Location | What it covers |
|---|---|---|---|
| Unit / service | Vitest | `src/**/*.test.ts` | Pure functions, services, API route handlers |
| Component | Vitest + RTL | `src/**/*.test.tsx` | UI behavior, conditional rendering |
| E2E / integration | Playwright | `e2e/**/*.spec.ts` | Full flows through the browser |

**Never put E2E specs inside `src/`** — Vitest will pick them up and fail (Playwright imports are not available in Vitest context).

## E2E Setup

Use `/add-e2e-playwright` skill for initial setup. Key outputs:
- `@playwright/cli` — global install, enables AI agent navigation
- `@playwright/test` — dev dependency, runs specs
- `playwright.config.ts` — in project root
- `e2e/` — top-level directory for all specs

## `playwright.config.ts` Pattern

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
  // Only start the server in CI — dev workflow assumes server is already running
  webServer: process.env.CI
    ? {
        command: 'npm run start',
        url: 'http://localhost:3000',
        reuseExistingServer: false,
      }
    : undefined,
});
```

## What to E2E Test

Write E2E specs for flows that span multiple layers (auth → API → DB → UI):
- Auth redirect (unauthenticated → login page)
- Full happy paths (login → create resource → see result)
- Navigation flows (bottom nav, back buttons)

Do **not** duplicate unit-level assertions in E2E — test that the page renders a heading, not every field's validation message.

## Scripts

```json
"test:e2e": "playwright test",
"test:e2e:ui": "playwright test --ui",
"test:e2e:debug": "playwright test --debug"
```

Run E2E locally with the dev server already running (`npm run dev` in another terminal).

## AI Navigation

With `@playwright/cli` installed and skills active, you can ask Claude to navigate the running app directly:

```
Use playwright-cli to test the login flow on localhost:3000
playwright-cli open http://localhost:3000 --headed
playwright-cli show   # visual dashboard of all sessions
```
