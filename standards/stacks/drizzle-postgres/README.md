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

## Dev Hot-Reload Guard (Next.js)

Next.js fast-refresh re-evaluates modules on every save but preserves the `globalThis` object. Without a guard, each save opens a new connection pool and exhausts the database limit within minutes.

```ts
// db/index.ts
import { drizzle } from 'drizzle-orm/node-postgres'
import { Pool } from 'pg'
import * as schema from './schema'

const globalForDb = globalThis as unknown as { pool?: Pool }

const pool = globalForDb.pool ?? new Pool({ connectionString: process.env.DATABASE_URL! })
if (process.env.NODE_ENV !== 'production') globalForDb.pool = pool

export const db = drizzle(pool, { schema })
```

> **Rule:** In Next.js projects, always use a `globalThis` guard for the DB client. Production is unaffected — the guard only assigns in dev mode.

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

## Circular Foreign Keys

Drizzle cannot represent a circular FK (Table A references Table B, Table B references Table A) using `.references()` on both sides simultaneously — it causes a runtime error during schema introspection.

**Pattern:** Declare the primary FK with `.references()`. Declare the back-reference as a plain `uuid` column (no `.references()`). Add the constraint as raw SQL in the migration file after both tables exist.

```ts
// schema/content.ts — galleries.coverPhotoId references photos, photos.galleryId references galleries
export const galleries = pgTable('galleries', {
  id:           uuid('id').primaryKey().defaultRandom(),
  coverPhotoId: uuid('cover_photo_id'),             // ← no .references() here
  // ... other columns
})

export const photos = pgTable('photos', {
  id:        uuid('id').primaryKey().defaultRandom(),
  galleryId: uuid('gallery_id').references(() => galleries.id), // ← FK declared here
  // ... other columns
})
```

In the generated migration, manually add:
```sql
ALTER TABLE photos ADD CONSTRAINT photos_gallery_id_fk
  FOREIGN KEY (gallery_id) REFERENCES galleries(id);

ALTER TABLE galleries ADD CONSTRAINT galleries_cover_photo_id_fk
  FOREIGN KEY (cover_photo_id) REFERENCES photos(id)
  DEFERRABLE INITIALLY DEFERRED;   -- deferred so inserts don't fail before cover is set
```

> **Rule:** Document every hand-edited migration in a comment at the top of the SQL file. Never silently edit generated files — note `-- MANUAL: circular FK constraint` on the added lines.

## Rules
- All DB access goes through the service layer — never query directly in route handlers
- Use `db.query.*` (relational API) for reads with relations; use core API for writes
- Never use raw SQL strings unless the query is impossible with the ORM
- `DATABASE_URL` must be in env — never hardcode connection strings
- Run `drizzle-kit generate` after any schema change, before starting the dev server
