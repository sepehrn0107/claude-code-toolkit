# Drizzle ORM + PostgreSQL Standards

## Packages
```
drizzle-orm       # core ORM
drizzle-kit       # migrations CLI
postgres          # recommended driver (postgres.js — faster than pg)
```

## Connection
```ts
// db/index.ts
import { drizzle } from 'drizzle-orm/postgres-js'
import postgres from 'postgres'
import * as schema from './schema'

const client = postgres(process.env.DATABASE_URL!)
export const db = drizzle(client, { schema })
```

For serverless (Neon, Vercel Postgres): use `drizzle-orm/neon-http` + `@neondatabase/serverless` instead.

## Schema Definition
```ts
// db/schema/workouts.ts
import { pgTable, uuid, varchar, timestamp, integer } from 'drizzle-orm/pg-core'
import { users } from './users'

export const workouts = pgTable('workouts', {
  id:        uuid('id').primaryKey().defaultRandom(),
  userId:    uuid('user_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  name:      varchar('name', { length: 255 }).notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
})
```

- All tables in `db/schema/` — one file per domain entity
- Export all from `db/schema/index.ts`
- Use `uuid` primary keys (`.defaultRandom()`) — not auto-increment integers
- Always include `createdAt`; add `updatedAt` for mutable records
- Foreign keys declare `onDelete` behavior explicitly

## Migrations
```bash
# Generate migration from schema changes
npx drizzle-kit generate

# Apply to database
npx drizzle-kit migrate
```

- Never edit generated migration files
- Commit migration files to git
- Config lives in `drizzle.config.ts`

```ts
// drizzle.config.ts
import { defineConfig } from 'drizzle-kit'

export default defineConfig({
  schema: './db/schema/index.ts',
  out: './db/migrations',
  dialect: 'postgresql',
  dbCredentials: { url: process.env.DATABASE_URL! },
})
```

## Query Patterns
```ts
// Prefer relational queries for joins
const workout = await db.query.workouts.findFirst({
  where: eq(workouts.id, id),
  with: { sets: true },
})

// Use insert().returning() to get created record
const [created] = await db.insert(workouts).values(data).returning()

// Transactions for multi-step writes
await db.transaction(async (tx) => {
  const [workout] = await tx.insert(workouts).values(...).returning()
  await tx.insert(workoutSets).values({ workoutId: workout.id, ... })
})
```

## Rules
- All DB access goes through the service layer — never query directly in route handlers
- Use `db.query.*` (relational API) for reads with relations; use core API for writes
- Never use raw SQL strings unless the query is impossible with the ORM
- `DATABASE_URL` must be in env — never hardcode connection strings
- Run `drizzle-kit generate` after any schema change, before starting the dev server
