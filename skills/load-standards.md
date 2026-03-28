# /load-standards

Mandatory gate before writing any code. Reads and activates all applicable standards for this project.

## When to Use

Invoke this before writing, editing, or reviewing any code. It is a blocking requirement — do not
proceed to implementation until this skill completes.

## Steps

### 1. Identify the Stack

Read `.claude/memory/stack.md` if it exists.
- Extract the stack name (e.g. `go`, `typescript-react`, `typescript-nextjs`, `python-fastapi`)
- If the file does not exist, infer from project signals: `go.mod`, `package.json`, `pyproject.toml`, `requirements.txt`, `Cargo.toml`
- If the stack cannot be determined, ask the user before continuing

### 2. Check for Base Stack

- Look for `{{TOOLBOX_PATH}}/standards/stacks/<stack>/_base.md`
- If found, read it and extract the value after `base:` — this is the base stack name
- Note it for Step 4 — the base stack's standards are loaded before the detected stack's standards
- If `_base.md` does not exist, there is no base stack — continue

### 3. Read Universal Standards

Read all files — do not skip any:

- `{{TOOLBOX_PATH}}/standards/universal/architecture.md`
- `{{TOOLBOX_PATH}}/standards/universal/security.md`
- `{{TOOLBOX_PATH}}/standards/universal/git.md`
- `{{TOOLBOX_PATH}}/standards/universal/testing.md`
- `{{TOOLBOX_PATH}}/standards/universal/documentation.md`
- `{{TOOLBOX_PATH}}/standards/universal/error-handling.md`
- `{{TOOLBOX_PATH}}/standards/universal/debugging.md`
- `{{TOOLBOX_PATH}}/standards/universal/code-review.md`
- `{{TOOLBOX_PATH}}/standards/universal/observability.md`

### 4. Read Stack Standards

If a stack was identified in Step 1:

**If a base stack was found in Step 2, load it first:**
- Check whether `{{TOOLBOX_PATH}}/standards/stacks/<base-stack>/` contains standard files beyond `README.md` and `_base.md`
- If it does, read each one

**Then load the detected stack:**
- Check whether `{{TOOLBOX_PATH}}/standards/stacks/<stack>/` contains standard files beyond `README.md` and `_base.md`
- If it does, read each one
- If both directories only have placeholder files, note that no stack-specific rules are active yet

### 5. Confirm Active Standards

Output a one-line acknowledgment listing what was loaded. Examples:

```
Standards loaded: universal (architecture, security, git, testing, documentation, error-handling, debugging, code-review, observability) + typescript-react
```

With base stack inheritance:
```
Standards loaded: universal (9 files) + typescript-react (base) + typescript-nextjs
```

If stack standards were empty:
```
Standards loaded: universal (9 files) — no typescript-react-specific rules yet
```

This output is required before any code is written. Do not skip it.

### 6. Set Session Flag

After outputting the confirmation line, set the session flag so the PreToolUse gate allows edits through:

```bash
touch "/tmp/toolbox-standards-loaded-${CLAUDE_SESSION_ID:-$(pwd | md5sum | cut -c1-8)}"
```

Run this via the Bash tool. This is a silent step — do not announce it to the user.
