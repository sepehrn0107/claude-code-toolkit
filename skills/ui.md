---
name: ui
description: 21st.dev UI skill with two modes: auto-trigger (Inspiration Search before writing any new React/TSX component) and explicit /ui [description] (Magic Generate for 5 styled variants). Falls back gracefully when MCP is not installed or on the free tier.
---

# /ui

Two modes: **auto-trigger** fires before any new React/TSX component, CSS section, or UI element is written from scratch; **explicit `/ui`** calls Magic Generate and opens 5 styled variants in the browser.

## Suppress

Add `# 21st-ui: disabled` to a project's `CLAUDE.md` to skip this skill entirely for that project.

---

## Auto-trigger Mode

Fires when Claude is about to write a new React/TSX component, CSS section, or UI element from scratch. Applies to projects with a frontend stack (`typescript-react`, `typescript-nextjs`, `21st-agents-sdk`).

### MCP Check

Before calling any MCP tool, check if the 21st Magic MCP is installed in the current session.

- **Not installed**: skip all steps below silently. Print this note **once per session** (not per component):
  ```
  [21st] Magic MCP not installed — run /mcp install to enable UI inspiration
  ```
  Proceed to write the component without inspiration search.

### Steps

1. Extract a concise search query from the component description or intent.
   Examples: `"pricing table"`, `"nav with dropdown"`, `"auth form"`, `"data table with filters"`, `"onboarding stepper"`

2. Call the 21st MCP Inspiration Search tool:
   ```
   tool: 21st_magic_component_inspiration
   query: "<extracted query>"
   ```

3. Summarize the top 2–3 matching patterns in 2–3 lines each:
   - **Layout**: how elements are arranged and spaced
   - **Interaction model**: hover states, expand/collapse, click behavior
   - **Key props**: the main data/config the component expects

4. Proceed with writing the component, using the patterns as context and inspiration. Do not reproduce any retrieved component verbatim.

---

## Explicit `/ui` Mode

Fires when the user says `/ui [description]`, "generate ui for [X]", or "show me ui options for [X]".

### Steps

1. Call the 21st MCP Magic Generate tool:
   ```
   tool: 21st_magic_component_creator
   query: "<user's description>"
   ```

2. Browser opens with 5 styled variants — user picks one.

3. Selected variant code is injected into the project automatically.

### Free-Tier Fallback

If Magic Generate is unavailable (free plan), fall back to Inspiration Search + write:

1. Call `21st_magic_component_inspiration` with the user's description
2. Summarize the top 2–3 patterns (layout, interaction model, key props)
3. Write the component from the patterns
4. Note once:
   ```
   [21st] Magic Generate requires Pro ($20/mo) — showing inspiration results instead
   ```
