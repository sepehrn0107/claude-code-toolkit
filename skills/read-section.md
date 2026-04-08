---
name: read-section
description: Extract a specific function, class, markdown section, or line range from a file instead of reading the whole thing. Use on files >100 lines when only a specific part is needed.
---

# /read-section

Read only the part of a file you actually need.

## When This Skill Triggers

Use instead of the `Read` tool when:
- The file is >100 lines and you only need one function, class, or section
- You already know what symbol or heading you're looking for
- Claude has already read this file in the session and needs to re-visit one part

Do NOT trigger for:
- Small files (<100 lines) — just `Read` the whole thing
- When you need the full file for context before editing

---

## How to Run

```bash
# By function name
python {{TOOLBOX_PATH}}/tools/read-section/read_section.py \
  --file <path> --fn <name>

# By class / interface / struct name
python {{TOOLBOX_PATH}}/tools/read-section/read_section.py \
  --file <path> --class <name>

# By markdown heading (exact text, any level)
python {{TOOLBOX_PATH}}/tools/read-section/read_section.py \
  --file <path> --after "<heading text>"

# By line range
python {{TOOLBOX_PATH}}/tools/read-section/read_section.py \
  --file <path> --lines 100-150
```

### Output

| Stream | Meaning |
|--------|---------|
| **stdout** | The section content, exactly as in the file |
| **stderr** | `fn "name" at lines X-Y of path — Z lines shown of N total` |
| **exit 0** | Found |
| **exit 1** | File not found, section not found, or bad arguments |

### Language support

| Language | Block detection |
|---|---|
| Python (`.py`, `.pyi`) | Indentation-based |
| JS / TS / Go / Java / C# / Rust | Brace counting |
| Markdown | Heading hierarchy |
| Others | Brace → indent fallback |

---

## Examples

```bash
TOOL={{TOOLBOX_PATH}}/tools/read-section/read_section.py

# Function
python $TOOL --file src/auth/handler.ts --fn handleRefresh

# Class
python $TOOL --file src/models/user.ts --class UserRepository

# Markdown section
python $TOOL --file README.md --after "API Routes"

# Lines
python $TOOL --file src/config.py --lines 50-100
```

---

## Fallback

If exit code 1 and the error is "not found":
1. Try a broader name (e.g. partial match or camelCase vs snake_case variant)
2. Fall back to `Read` the full file — the function may be dynamically defined
3. Try `Grep` to locate the exact definition line first, then use `--lines`
