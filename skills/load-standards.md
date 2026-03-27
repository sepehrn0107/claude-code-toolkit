# /load-standards

Mandatory gate before writing any code. Reads and activates all applicable standards for this project.

## When to Use

Invoke this before writing, editing, or reviewing any code. It is a blocking requirement — do not
proceed to implementation until this skill completes.

## Steps

### 1. Identify the Stack

Read `.claude/memory/stack.md` if it exists.
- Extract the stack name (e.g. `go`, `typescript-react`, `python-fastapi`)
- If the file does not exist, infer from project signals: `go.mod`, `package.json`, `pyproject.toml`, `requirements.txt`, `Cargo.toml`
- If the stack cannot be determined, ask the user before continuing

### 2. Read Universal Standards

Read all five files — do not skip any:

- `{{TOOLBOX_PATH}}/standards/universal/architecture.md`
- `{{TOOLBOX_PATH}}/standards/universal/security.md`
- `{{TOOLBOX_PATH}}/standards/universal/git.md`
- `{{TOOLBOX_PATH}}/standards/universal/testing.md`
- `{{TOOLBOX_PATH}}/standards/universal/documentation.md`

### 3. Read Stack Standards

If a stack was identified in step 1:
- Check whether `{{TOOLBOX_PATH}}/standards/stacks/<stack>/` contains standard files beyond README.md
- If it does, read each one
- If the directory only has a README placeholder, note that no stack-specific rules are active yet

### 4. Confirm Active Standards

Output a one-line acknowledgment listing what was loaded. Example:

```
Standards loaded: universal (architecture, security, git, testing, documentation) + go stack
```

If stack standards were empty:
```
Standards loaded: universal (architecture, security, git, testing, documentation) — no go-specific rules yet
```

This output is required before any code is written. Do not skip it.
