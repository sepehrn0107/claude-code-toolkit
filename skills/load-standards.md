---
name: load-standards
description: Mandatory pre-coding gate that loads all applicable standards (universal + stack-specific) before any code is written or edited. This skill must run before writing, editing, or reviewing any code — it sets the session flag that allows edits through the PreToolUse gate. Invoke it at the start of any direct coding task. If you're about to write code and haven't loaded standards yet, stop and run this first. Do not skip it even for small changes.
---

# /load-standards

Mandatory gate before writing any code. Reads and activates all applicable standards for this project.

> **Note for `/implement` sub-agents**: when this skill is invoked inside a Phase 3–5 sub-agent,
> load the full standards as normal — sub-agents always get the full load. Only the main session
> uses the compact `DIGEST.md` instead.

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

### 3. Read Relevant Universal Standards

Classify the current task into one of these categories, then load **only** the listed files:

| Category | Trigger | Standards to load |
|----------|---------|-------------------|
| **implementation** | Writing new code, adding features, building components | architecture, testing, error-handling |
| **bugfix** | Fixing bugs, debugging issues | debugging, error-handling, testing |
| **security** | Auth, input validation, secrets, OWASP concerns | security, architecture |
| **review** | Code review, PR preparation, standards check | code-review, security, architecture |
| **documentation** | Writing docs, README, ADRs | documentation, git |
| **observability** | Logging, metrics, alerting, health checks | observability, error-handling |
| **full** | `/standards-check`, pre-PR gate, or explicit "load all standards" | All 9 files (current behavior) |

If the category is unclear, default to **implementation** (the most common case).

Read only the files listed for the matched category from `{{TOOLBOX_PATH}}/standards/universal/`.

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
