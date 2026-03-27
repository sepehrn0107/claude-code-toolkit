# Testing Standards (React)

## Stack
- React Testing Library (RTL) for all component tests
- Runner is per-project: Vitest (preferred for Vite projects) or Jest
- Playwright or Cypress for E2E — document choice in `.claude/memory/stack.md`

## What to Test
- User-visible behavior — what the user sees and does, not implementation details
- All conditional rendering paths (loading, error, empty, populated)
- All user interactions that trigger state changes
- Every bug fix must include a regression test

## Query Priority (RTL)
Use queries in this order — the first that works is the right one:
1. `getByRole` (most semantic, preferred)
2. `getByLabelText`
3. `getByPlaceholderText`
4. `getByText`
5. `getByDisplayValue`
6. `getByAltText`
7. `getByTitle`
8. `getByTestId` (last resort — add `data-testid` only when no semantic query works)

Never query by class name, CSS selector, or component internals.

## Assertions
- Assert on what the user sees: text content, ARIA state, presence/absence of elements
- Do not assert on props, state, or internal methods

## Structure
- One `describe` block per component
- Test names describe behavior: `'shows error message when email is invalid'`
- Arrange → Act → Assert pattern in each test

## Anti-Patterns
- No snapshot tests for logic — snapshots only for design-system leaf components with stable output
- No `waitFor` polling loops — use `findBy*` queries for async elements
- Do not test implementation: no spying on `setState`, no reading component props

## User Interactions
- Use `userEvent` (from `@testing-library/user-event`) for all user interactions — not `fireEvent`
- `userEvent` simulates real browser behavior (focus, keyboard events, pointer events); `fireEvent` dispatches synthetic DOM events and misses many real-world scenarios
- Always call `userEvent.setup()` before each test:

```ts
const user = userEvent.setup()
await user.click(screen.getByRole('button', { name: /submit/i }))
await user.type(screen.getByLabelText('Email'), 'user@example.com')
```
