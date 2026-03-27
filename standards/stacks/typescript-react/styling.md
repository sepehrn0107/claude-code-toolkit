# Styling Standards

## Pick One Per Project
Use either Tailwind CSS or CSS Modules — do not mix within a project. Document the choice in `.claude/memory/stack.md`.

## Tailwind CSS
- Utility classes in JSX — no inline `style` props
- Do not use `@apply` to extract utilities — extract to a component instead
- Design tokens (colors, spacing) live in `tailwind.config.ts`, not hardcoded in classes
- For conditional classes use `clsx` or a `cn` wrapper (a local utility combining `clsx` + `tailwind-merge`) — not string concatenation

```tsx
// correct
<div className={cn('rounded p-4', isActive && 'bg-blue-500')} />

// incorrect
<div className={`rounded p-4 ${isActive ? 'bg-blue-500' : ''}`} />
```

## CSS Modules
- One `.module.css` file per component, colocated
- Class names in BEM-style within the module: `.card`, `.card__title`, `.card--active`
- No global class names except in `globals.css` (resets, CSS custom properties)
- Import as `styles` consistently: `import styles from './UserCard.module.css'`

```tsx
// UserCard.module.css
// .card { padding: 1rem; }
// .card--active { background: var(--color-primary); }

import styles from './UserCard.module.css'

export function UserCard({ isActive }: { isActive: boolean }) {
  return (
    <div className={`${styles.card} ${isActive ? styles['card--active'] : ''}`}>
      ...
    </div>
  )
}
```

## Global Styles
- Only resets and CSS custom properties (design tokens) in global stylesheets
- No component styles in global files
