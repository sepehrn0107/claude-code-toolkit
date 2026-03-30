---
name: grep
description: Smart search guidelines — how to use Grep efficiently to minimise token waste, redundant calls, and large noisy result sets.
---

# /grep

Search guidelines to get precise results with fewer calls and less context noise.

---

## When This Skill Applies

Apply these guidelines whenever Claude is about to search the codebase for a symbol, pattern, or file.

---

## The Two-Phase Pattern

### Phase 1 — locate files (cheap)

Start with `files_with_matches` to identify *which* files are relevant:

```
Grep: pattern="<term>", output_mode="files_with_matches"
```

This returns only paths — no content, minimal tokens. Read the file list, then decide which ones to dig into.

### Phase 2 — read content in specific files (targeted)

Once you know the right file(s), search within them:

```
Grep: pattern="<term>", path="<specific_file>", output_mode="content", head_limit=50
```

Never run a broad content search across the whole repo on the first attempt.

---

## Narrowing patterns

| Goal | Pattern |
|---|---|
| Function definition only | `def <name>\|function <name>\|func <name>` |
| Class definition only | `class <name>\|interface <name>\|struct <name>` |
| Import/require of a module | `from <module> import\|require.*<module>` |
| Specific file types | Add `glob="*.ts"` or `type="py"` |
| Case-insensitive | Add `-i: true` |

---

## Always set head_limit

Default ripgrep output can be thousands of lines. Always cap it:

```
Grep: ..., output_mode="content", head_limit=50
```

Increase only if you've confirmed the first batch is insufficient.

---

## Anti-patterns

| Anti-pattern | Fix |
|---|---|
| Content search across whole repo immediately | `files_with_matches` first |
| Running the same search twice | Check results before retrying |
| Reading every matching file in full after grep | Use `read-section` for the specific block |
| One wide search for both definitions and usages | Two narrow searches |
| No `head_limit` on content searches | Always set it |

---

## When grep isn't finding it

After 3 attempts without a match:
1. The name may differ — check for aliases, re-exports, or snake_case vs camelCase variants
2. Use `read-section --after` to scan a file's headings/structure
3. If `.claude/index/` exists — query it via `query-index.md` instead of grepping

---

## prefer Grep over Bash grep/rg

Always use the `Grep` tool, not `Bash grep` or `Bash rg`. The tool has correct permissions, better output formatting, and is reviewable by the user.
