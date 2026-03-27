# Naming Conventions

## Files
- Components: `PascalCase.tsx` (e.g., `UserCard.tsx`)
- Hooks: `useCamelCase.ts` (e.g., `useCurrentUser.ts`)
- Utilities/helpers: `camelCase.ts` (e.g., `formatDate.ts`)
- Flat constants: `SCREAMING_SNAKE_CASE.ts` (e.g., `API_ROUTES.ts`)
- Config/object constants: `camelCase.ts` (e.g., `apiConfig.ts`)
- Types-only files: `camelCase.types.ts` (e.g., `user.types.ts`)

## Folders
- Feature folders: `kebab-case` (e.g., `user-profile/`)
- Component-colocated folders: `PascalCase` matching the component (e.g., `UserCard/`)

## Components
- `PascalCase`
- Name describes what it renders, not where it is used — `UserCard` not `HomePageCard`

## Props
- Props interface named `<ComponentName>Props`, colocated with the component
- Boolean props prefixed with `is`, `has`, or `can` — `isLoading`, `hasError`, `canEdit`

## Hooks
- Always `use` prefix
- Named after what they return, not how they work — `useCurrentUser` not `useFetchAndCacheUser`

## Event Handlers
- `handle<Event>` in the definition: `handleSubmit`, `handleClick`
- `on<Event>` in props: `onSubmit`, `onClick`

## Variables
- `camelCase` throughout
- No abbreviations except industry-standard: `id`, `url`, `api`, `ref`, `ctx`

## Types and Interfaces
- `PascalCase`
- No `I` prefix — `UserProfile` not `IUserProfile`
- Prefer `type` for unions and computed types; `interface` for object shapes that may be extended

## Constants
- Module-level constants: `SCREAMING_SNAKE_CASE`
- Object/config constants: `camelCase`

## Redux
- Slice name: camelCase feature name (e.g., `userSlice`)
- Actions: `feature/verbNoun` format (e.g., `users/fetchById`, `cart/addItem`)
