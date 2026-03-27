# /add-stack-standards

Automates the full workflow for adding standards for a new technology stack to the toolbox.
Run this whenever you need to add or populate standards for a stack that doesn't have them yet.

## When to Use

Invoke when the user says any of:
- "add standards for [stack]"
- "add documentation for my stack"
- "document the [stack] stack"
- `/add-stack-standards`

## Steps

### 1. Identify the Stack

- If the user named a stack explicitly, use that name
- Otherwise, infer from project signals in the current working directory:
  - `package.json` with `next` dependency → `typescript-nextjs`
  - `package.json` with `react` but no `next` → `typescript-react`
  - `go.mod` → `go`
  - `pyproject.toml` or `requirements.txt` with `fastapi` → `python-fastapi`
  - `pyproject.toml` or `requirements.txt` → `python`
- If inference is ambiguous, ask: "What stack should I add standards for?"
- Normalize the name to `kebab-case`

### 2. Check for Existing Standards

- Check whether `{{TOOLBOX_PATH}}/standards/stacks/<stack>/` already has files beyond `README.md`
- If yes: confirm with the user whether to extend or replace existing standards before continuing

### 3. Determine Base Stack

Ask: "Does this stack extend another? For example, Next.js extends React. If so, what's the base stack name? (Leave blank if standalone)"

If a base stack is given:
- Verify `{{TOOLBOX_PATH}}/standards/stacks/<base-stack>/` exists
- Note it — you will create `_base.md` in Step 6

### 4. Ask Clarifying Questions

Ask these one at a time. Skip any that don't apply to the stack.

1. **State management** — what approach does this stack use? (e.g., Redux, Zustand, Context, Vuex, none)
2. **Testing** — what framework and libraries? (e.g., Vitest+RTL, Jest, pytest, Go testing)
3. **Styling** — how is UI styled? (e.g., Tailwind, CSS Modules, SCSS, not applicable)
4. **Build tooling** — what builds this? (e.g., Vite, Next.js, esbuild, Go toolchain)
5. **Any strong conventions** — naming, file layout, patterns the team has settled on?

### 5. Generate Standards Files

Based on the answers, create files under `{{TOOLBOX_PATH}}/standards/stacks/<stack>/`. Use the existing `typescript-react` standards as a reference for depth and format.

Always create at minimum:
- `components.md` (or equivalent: `modules.md`, `packages.md`) — structural patterns
- `naming.md` — naming conventions for files, variables, types, functions
- `testing.md` — testing approach and conventions

Add additional files for topics with meaningful conventions (state, styling, tooling, api, etc.).

Each file should:
- Use `#` heading matching the file's topic
- Use `##` sections for sub-topics
- Include concrete examples (code blocks) wherever conventions are non-obvious
- Be direct — state the rule, then explain or example it

### 6. Create _base.md (if applicable)

If a base stack was identified in Step 3:

Create `{{TOOLBOX_PATH}}/standards/stacks/<stack>/_base.md`:
```
# Base stack declaration — read by load-standards to load base stack first
base: <base-stack-name>
```

### 7. Check load-standards for Inheritance Support

Open `{{TOOLBOX_PATH}}/skills/load-standards.md` and verify Step 2 ("Check for Base Stack") is present.
- If present: nothing to do
- If missing: add Step 2 as described in the load-standards skill file

### 8. Register the Stack in CLAUDE.md and Template

Open `{{TOOLBOX_PATH}}/CLAUDE.md`. If a "Stacks" or similar section exists, add the new stack name.
Open `{{TOOLBOX_PATH}}/templates/CLAUDE.global.md`. Apply the same addition.

### 9. Commit and Open PR

```bash
git checkout -b feat/add-<stack>-standards
git add standards/stacks/<stack>/
git commit -m "feat: add <stack> standards"
gh pr create --title "feat: add <stack> standards" --body "Adds substantive standards for the <stack> stack via /add-stack-standards."
```

### 10. Confirm

Tell the user:
- Which files were created
- What the stack name is (for use in `.claude/memory/stack.md` in projects)
- PR link
