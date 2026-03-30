# Next.js Project Scaffold Standards

## create-next-app in a Non-Empty Directory

`create-next-app` fails when the target directory is not empty (common when `.claude/`, `README.md`,
or other files already exist). Do **not** delete or move these files.

**Workaround:** Create all scaffold files manually. The scaffold produces a predictable set of files —
create them directly instead of relying on the interactive CLI.

### Minimum scaffold files
```
package.json          — dependencies, scripts
tsconfig.json         — strict: true, noUncheckedIndexedAccess: true, paths: { "@/*": ["./src/*"] }
next.config.ts        — typedRoutes, remotePatterns with runtime env guard
.gitignore            — node_modules, .next/, .env*.local, coverage/, playwright-report/
.prettierrc           — printWidth: 100, singleQuote: true, trailingComma: "all", semi: true
eslint.config.mjs     — next/core-web-vitals + @typescript-eslint/recommended + import/no-cycle
src/app/layout.tsx    — root layout, metadata, font imports, globals.css import
src/app/page.tsx      — minimal placeholder
src/styles/globals.css — placeholder (design system agent fills this)
```

### Key tsconfig settings
```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "paths": { "@/*": ["./src/*"] }
  }
}
```

### next.config.ts pattern — runtime env guard
```ts
// Gate remotePatterns on runtime value — never assert at module level
// so `npm run build` succeeds without credentials in CI.
const nextConfig: import('next').NextConfig = {
  experimental: { typedRoutes: true },
  images: {
    remotePatterns: process.env.R2_PUBLIC_HOSTNAME
      ? [{ hostname: process.env.R2_PUBLIC_HOSTNAME }]
      : [],
  },
}
export default nextConfig
```

### ESLint flat config (eslint.config.mjs)
```js
import { dirname } from 'path'
import { fileURLToPath } from 'url'
import { FlatCompat } from '@eslint/eslintrc'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)
const compat = new FlatCompat({ baseDirectory: __dirname })

export default [
  ...compat.extends('next/core-web-vitals', 'next/typescript'),
  {
    rules: {
      'import/no-cycle': 'error',   // enforces Clean Architecture (no circular deps)
    },
  },
]
```

## npm audit on Fresh Installs

`npm install` on a new Next.js 15 project typically reports vulnerabilities in transitive
dependencies. Do **not** block progress on these. Recommended approach:

1. Run `npm audit --audit-level=critical` — address critical issues only at scaffold time.
2. Schedule a dedicated `npm audit fix` pass before the first production deploy.
3. Document known unfixed CVEs in `README.md` if they cannot be resolved without a major version bump.

## Rules
- Always pin exact versions in `package.json` (no `^` or `~`) for production apps — prevents silent breaking changes from transitive updates.
- Never commit `.env.local` — only `.env.local.example` with all vars documented and no real values.
- `typedRoutes: true` provides compile-time safety for all `<Link href>` calls — always enable for App Router projects.
