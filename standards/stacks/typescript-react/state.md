# State Management Standards

## Decision Rule
Choose the simplest state mechanism that works:
1. `useState` — single-component, simple values
2. `useReducer` — single-component, complex state transitions
3. Context API — low-frequency shared state (auth, theme, user preferences)
4. Redux Toolkit — complex global state shared across many distant components

Reach for global state only when state is genuinely cross-cutting. If only two components share state, lift it to their common ancestor first.

## Context API
- Use for: auth session, theme, locale, user preferences
- Do not use for: high-frequency updates (causes unnecessary re-renders)
- Keep context values stable — memoize with `useMemo` when the provider re-renders often
- One context per concern — do not create a single "app context" with everything

## Redux Toolkit
- Use when: state is shared across many distant components, needs DevTools/time-travel, or has complex update logic
- All state lives in slices — no hand-rolled reducers
- Use `createAsyncThunk` for async operations
- Derive data in selectors, not in components

## Typing
- No `any` in state types
- Derive types from Zod schemas at API boundaries
- Define state shape explicitly in slice — `initialState` must be fully typed

## Anti-Patterns
- Do not store derived data in state — compute it
- Do not duplicate server state in Redux — use React Query or SWR for server state
- Do not put UI state (modal open, tab active) in Redux — `useState` is correct for this
