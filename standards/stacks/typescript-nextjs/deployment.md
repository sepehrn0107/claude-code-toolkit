# Deployment Standards (Cloud-Agnostic, Next.js)

## Principles
- All configuration via environment variables — no hardcoded hosts, ports, or credentials
- The app must run identically locally and in any cloud (Vercel, Railway, Render, Fly.io, AWS, GCP)
- Docker is the portability layer — if it runs in Docker, it runs anywhere

## Environment Variables
Required variables documented in `.env.example` (committed, no values):

```env
# App
NODE_ENV=
NEXT_PUBLIC_APP_URL=

# Database
DATABASE_URL=

# Auth0
AUTH0_SECRET=
AUTH0_BASE_URL=
AUTH0_ISSUER_BASE_URL=
AUTH0_CLIENT_ID=
AUTH0_CLIENT_SECRET=
```

Rules:
- `.env.local` for local dev (gitignored)
- `.env.example` committed with placeholder values
- Never commit `.env`, `.env.local`, or any file with real secrets

## Dockerfile
```dockerfile
FROM node:20-alpine AS base

FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup --system --gid 1001 nodejs && adduser --system --uid 1001 nextjs
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
USER nextjs
EXPOSE 3000
ENV PORT=3000
CMD ["node", "server.js"]
```

Requires `output: 'standalone'` in `next.config.ts`.

## Docker Compose (Local Dev)
```yaml
# docker-compose.yml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: app
      POSTGRES_DB: gymtracker
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

Run the Next.js app with `npm run dev` locally against the Dockerized Postgres.

## Health Check
Expose `GET /api/health` returning `{ status: 'ok' }` with 200. Used by load balancers and container orchestrators.

## Rules
- `next.config.ts` must set `output: 'standalone'` for Docker builds
- No platform-specific build steps in `package.json` scripts
- DB migrations run as a separate step before app start — never auto-migrate on boot in production
- Log to stdout only — never write log files inside the container
