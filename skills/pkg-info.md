---
name: pkg-info
description: Fetch package metadata from npm or PyPI JSON APIs — version, types, homepage, license. Cached 24h. Use instead of WebFetch when you just need package facts, not full docs.
---

# /pkg-info

Compact package info without crawling the full docs page.

> `{{TOOLBOX_PATH}}` = `C:/Users/sepeh/Documents/workspace/toolbox`

---

## When This Skill Triggers

Use instead of `/web-fetch` when Claude needs to know:
- Current published version of an npm or PyPI package
- Whether a package ships TypeScript types (or needs `@types/*`)
- License, homepage, publish date
- Rough popularity (npm weekly downloads)

Do NOT trigger when you need:
- Full API documentation or changelog → use `/web-fetch`
- Package source code → use `Read` or `Grep` on the installed files

---

## How to Run

```bash
python C:/Users/sepeh/Documents/workspace/toolbox/tools/pkg-info/pkg_info.py --name <package>
```

Options:
- `--name <pkg>` — package name (`express`, `@types/node`, `fastapi`)
- `--registry npm|pypi|auto` — registry to query (default: `auto` — npm first, falls back to pypi)
- `--force` — bypass cache, always re-fetch
- `--max-age-hours <N>` — cache TTL override (default: `24`)

### Output format (stdout)

```
package: express (npm)
version: 4.18.2
description: Fast, unopinionated, minimalist web framework
types: @types/express (check separately)
homepage: https://expressjs.com
license: MIT
published: 2023-08-03
weekly downloads: 32.1M
```

| Stream | Meaning |
|--------|---------|
| **stdout** | Compact info |
| **stderr** | `cache hit` / `fetching...` / errors |
| **exit 0** | Success |
| **exit 1** | Package not found or registry unreachable |

### Cache location

```
~/.claude/cache/pkg-info/<registry>-<name>.json
```

---

## Examples

```bash
TOOL=C:/Users/sepeh/Documents/workspace/toolbox/tools/pkg-info/pkg_info.py

# Auto-detect registry (npm default)
python $TOOL --name express

# Scoped npm package
python $TOOL --name @types/node

# PyPI package
python $TOOL --name fastapi --registry pypi

# Force refresh
python $TOOL --name react --force
```

---

## Fallback

If exit code 1 with "not found":
- Try the other registry explicitly (`--registry pypi` or `--registry npm`)
- Some packages exist on both (e.g. `pydantic` is PyPI only)

If exit code 1 with "registry unreachable":
- Fall back to `/web-fetch` for the package's npmjs.com or pypi.org page
