# Component Standards

## Structure
- Functional components only — no class components
- One component per file; filename matches component name (PascalCase)
- Colocate component, its types, its styles, and its tests in the same folder

## Composition
- Composition over prop-drilling — extract sub-components before passing 3+ props down
- Extract repeated JSX into a component, not a helper that returns JSX
- Keep component files focused: if a file exceeds ~150 lines, it is doing too much

## Hooks
- Custom hooks extract reusable stateful logic — name starts with `use`
- Colocate hooks with the component they serve, or place in `hooks/` if shared
- Do not call hooks conditionally or inside loops

## Responsibilities
- Components handle presentation and wiring only — no business logic
- Data fetching lives in hooks or server layer, not directly in component bodies
- Side effects belong in `useEffect` or event handlers, not in render
