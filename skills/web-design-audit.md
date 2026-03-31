---
name: web-design-audit
description: Performs a structured web design audit covering spacing systems, typography, color contrast (WCAG), universal/accessible design, page flow, visual hierarchy, responsive layout, and component consistency. Use this skill whenever the user asks to review, audit, or improve a web project's design, UI quality, visual consistency, accessibility, or spacing. Trigger when the user says "audit the design", "check the UI", "review the spacing", "check accessibility", "design review", "how does the page flow look", "is the typography consistent", or any variation of wanting to evaluate the look, feel, or accessibility of a web project. Also trigger proactively when starting a new feature that touches layout or design tokens.
---

# /web-design-audit

A systematic design audit for web projects. Produces a prioritized report covering token adherence, typography, spacing, accessibility, and page flow — with specific file references and actionable fixes.

## When to Run

- User asks to audit/review/improve design quality, UI, or accessibility
- Before a PR that touches CSS, components, or tokens
- When adding a new page or section — audit the surrounding context

---

## How to Run the Audit

Work through each section below. For each finding, note:
- **Severity**: `critical` (breaks usability/WCAG) | `warning` (inconsistency or missed standard) | `suggestion` (polish)
- **Location**: file path + line number or selector
- **Fix**: concrete one-liner describing the change

### Step 1 — Read Design Foundation

Read in parallel:
- All token files (e.g. `tokens.css`, `marketing-tokens.css`, `theme.ts`, `tailwind.config.*`)
- Global CSS (e.g. `globals.css`, `reset.css`)
- Root layout file (e.g. `app/layout.tsx`)
- Font loading configuration

Note: what tokens are defined (colors, spacing, typography, radius, shadows, z-index), and which are missing or incomplete.

### Step 2 — Audit Design Tokens

Check:
- **Completeness**: Are all semantic roles covered? (background, foreground, primary, accent, muted, border, destructive, surface tiers)
- **Z-index gaps**: Are all stacking contexts covered (nav, sticky, overlay, modal, tooltip)? Cross-check every CSS file that uses `z-index` against what is tokenized.
- **Hardcoded values leaking into components**: Search CSS files for hardcoded hex colors, px/rem sizes, and weights that should reference a token. Flag any that bypass the system.
- **Spacing token usage**: Are large spacing values (section padding, gaps) using tokens, or are they inline rem values? The latter creates drift.
- **Token naming consistency**: Are tokens named semantically (what they mean) rather than literally (what they look like)? E.g. `--color-primary` not `--color-gold`.

### Step 3 — Typography Audit

Check:
- **Type scale**: Is there a clear scale? Are sizes defined as tokens and used from them? Flag hardcoded px/rem font sizes that fall outside the defined scale — especially values below the smallest token (e.g. 0.6875rem when `--font-size-xs` is 0.75rem).
- **Hierarchy**: Does each page have a single H1? Do heading levels descend logically (H1 → H2 → H3)? Scan page files for heading usage.
- **Line height**: Is body copy at 1.5–1.75 for readability? Are display/headline elements using tighter line heights (1.05–1.25)?
- **Letter spacing**: Is letter-spacing applied consistently? Excessive `letter-spacing` on body text (> 0.05em) hurts readability. Track down any deviations.
- **Responsive type**: Are display headings using `clamp()` or fluid scaling? Are body sizes fixed — and if so, is the smallest breakpoint still readable (≥ 15px)?
- **Font loading**: Is `font-display: swap` or `optional` used? Are subsets specified to reduce payload?

### Step 4 — Spacing & Rhythm Audit

Check:
- **Vertical rhythm**: Do sections have consistent top/bottom padding? Is section gap (space between sections) harmonious?
- **Token adherence**: Are padding/margin/gap values using spacing tokens (e.g. `var(--space-6)`) or arbitrary rem values? Flag the latter.
- **Scale jumps**: Are there dramatic jumps in the spacing scale that create visual imbalance? (e.g. --space-4: 16px next to a hardcoded 8.5rem hero padding)
- **Component internal spacing**: Are component-level gaps (padding inside cards, gap between label and input) consistent across similar components?
- **Max-width containers**: Is there a consistent max-width for content columns? Are different sections using different max-widths without good reason?

### Step 5 — Color & Contrast Audit

Check WCAG 2.1 contrast ratios:
- **AA (normal text)**: ≥ 4.5:1 for text ≤ 18px
- **AA (large text)**: ≥ 3:1 for text > 18px or bold > 14px
- **AA (UI components)**: ≥ 3:1 for interactive elements and focus indicators

Specifically audit:
- Body text on its background
- Muted/secondary text on its background
- Placeholder text on input background (common failure — placeholders are often too light)
- CTA button text on button background
- Link colors in context (both default and hover states)
- Focus ring visibility — does it meet 3:1 against both the element and its surroundings?
- Any text layered over images or gradients (needs overlay analysis)

Flag hardcoded color values that bypass the token system — these are contrast risks.

### Step 6 — Accessibility Audit

Check:
- **Focus states**: Do all interactive elements (links, buttons, inputs, selects) have visible `:focus-visible` styles? Look for `outline: none` with no replacement focus indicator — this is a critical WCAG 2.4.7 failure.
- **Skip link**: Is there a "skip to main content" link as the first focusable element? This is a WCAG 2.4.1 requirement.
- **Reduced motion**: Do animations respect `@media (prefers-reduced-motion: reduce)`? Scan for `@keyframes`, `transition`, `animation` properties that lack this media query override.
- **Semantic HTML**: Are headings, landmarks (`<header>`, `<main>`, `<footer>`, `<nav>`, `<section>`), and lists used correctly? Are sections labeled with `aria-label` or `aria-labelledby`?
- **ARIA usage**: Are ARIA attributes used correctly and only where native HTML is insufficient? Check for `aria-hidden` on decorative elements, `aria-label` on icon-only buttons.
- **Form accessibility**: Do all form inputs have associated `<label>` elements (or `aria-label`)? Are error states communicated accessibly (not just by color)?
- **Image alt text**: Are all `<img>` tags (or `next/image`) given meaningful alt text? Are decorative images marked `alt=""`?
- **Color-only information**: Is color used as the *only* means of conveying information (e.g., a red border with no text for errors)?
- **Touch targets**: Are interactive elements at least 44×44px on mobile?

### Step 7 — Responsive Layout Audit

Check:
- **Breakpoint strategy**: Are breakpoints consistent across components, or does each file define its own? Identify the breakpoint set in use and flag outliers.
- **Mobile-first vs desktop-first**: Is the codebase consistent in its approach? Mixing `max-width` and `min-width` queries without a clear pattern creates maintenance issues.
- **Content reflow**: Does the layout reflow gracefully at each breakpoint? Identify grid/flex patterns that may overflow or collapse unexpectedly.
- **Text overflow**: Scan for long strings (nav items, headings) that could overflow without `overflow-wrap: break-word` or `text-overflow: ellipsis`.
- **Touch-only behavior**: Are hover-only features (e.g., `background-attachment: fixed`) disabled for touch devices? Check `@media (hover: none)` overrides.
- **Viewport units**: Are `vh` units used? Note that `100vh` breaks on mobile browsers with dynamic toolbars — flag and recommend `100svh` or `dvh`.

### Step 8 — Page Flow Audit

For each marketing page, read the page file and assess:
- **Above-the-fold value proposition**: Is the hero section immediately communicating what the site offers?
- **CTA placement**: Is a primary CTA visible within the first viewport? Is the CTA repeated at logical decision points (after services, after portfolio)?
- **Section sequencing**: Does the page flow logically? Common effective order for portfolios: Hero → Proof (portfolio/work) → Services → Trust (about/testimonials) → CTA.
- **Content-to-CTA ratio**: Is there enough context before each CTA for the user to feel informed?
- **Navigation clarity**: Is the nav structure intuitive? Are active states shown? Is the mobile menu accessible?
- **Dead ends**: Are there pages that end without a next step for the user?

### Step 9 — Component Consistency Audit

Check:
- **Button variants**: Are buttons styled consistently? Do all "primary CTA" buttons share the same visual language regardless of where they appear?
- **Section headers**: Do section heading patterns (eyebrow label + heading + optional subhead) look identical across pages?
- **Card patterns**: Are card components reusing the same base component or is each section rolling its own?
- **Link styling**: Are text links styled consistently? Are hover underline animations uniform?
- **Interaction patterns**: Are transitions consistent in duration and easing (e.g., all hover transitions `0.2s ease`)?

---

## Output Format

After completing all steps, produce a structured report:

```
# Web Design Audit — [Project Name]
_Audited: [date] · Scope: [what was reviewed]_

## Summary
[2–3 sentences on overall quality and top concerns]

## Critical Issues
[Issues that break WCAG or severely impact usability — fix before shipping]

| # | Area | Issue | Location | Fix |
|---|------|-------|----------|-----|
| 1 | Accessibility | No focus-visible style on nav links | Header.module.css:47 | Add :focus-visible with 2px outline offset |

## Warnings
[Inconsistencies, token drift, design system leaks — fix soon]

| # | Area | Issue | Location | Fix |
|---|------|-------|----------|-----|

## Suggestions
[Polish items — nice to have, not blocking]

| # | Area | Issue | Location | Fix |
|---|------|-------|----------|-----|

## What's Working Well
[Explicit call-out of good patterns the team should keep — don't skip this]

## Prioritized Fix Order
1. [Most impactful fix first]
2. ...
```

Be specific — always include file paths and CSS selectors. Vague findings like "improve contrast" are useless; "`.muted` text (#c6c7c2) on `#131313` bg is 5.2:1 — passes AA but `.placeholder` (#353534) on `#131313` is ~1.3:1 — fails" is actionable.

Estimate contrast ratios using the formula: relative luminance from sRGB. When in doubt, flag it as needing verification rather than guessing.
