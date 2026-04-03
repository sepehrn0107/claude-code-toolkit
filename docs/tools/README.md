---
title: "Tools Reference"
section: tools
skills-affected: [read-section, grep, env-check, pkg-info, diff-summary, git-ctx, index-repo, web-fetch]
last-updated: 2026-04-03
---

# Tools Reference

Python tools that skills invoke via Bash. Claude calls these automatically — you
don't run them directly unless troubleshooting.

## `tools/read-section/read_section.py`

Extracts one function, class, or section from a source file without loading the rest.

```bash
python tools/read-section/read_section.py --file src/auth.ts --fn validateToken
python tools/read-section/read_section.py --file docs/guide.md --after "## Install"
python tools/read-section/read_section.py --file handler.go --lines 50-80
```

Language detection is automatic. Supports: Python (indent-based), JS/TS/Go/Java/C#/Rust
(brace-counting), Markdown (heading hierarchy), others (brace → indent fallback).

Exit code 0 = found; exit code 1 = not found or unreadable.

---

## `tools/env-check/env_check.py`

Checks runtime environment: language versions, open ports, Docker container status,
`.env` file presence and git-ignore status.

```bash
python tools/env-check/env_check.py
```

Output is structured JSON. The `/env-check` skill parses it and returns a summary.

---

## `tools/pkg-info/pkg_info.py`

Queries npm or PyPI for package metadata.

```bash
python tools/pkg-info/pkg_info.py --pkg drizzle-orm --registry npm
python tools/pkg-info/pkg_info.py --pkg fastapi --registry pypi
```

Returns: latest version, TypeScript types, license, weekly downloads, homepage.

---

## `tools/diff-summary/diff_summary.py`

Produces a structured summary of `git diff` output — file-by-file with a one-line
description per change.

```bash
python tools/diff-summary/diff_summary.py
```

Reads from `git diff` on stdin or runs `git diff HEAD` automatically.

---

## `tools/git-ctx/git_ctx.py`

Batches multiple git queries into one structured output: branch, status, recent log,
and diff stat.

```bash
python tools/git-ctx/git_ctx.py
```

---

## `tools/indexer/indexer.py`

Builds the structural code index for the project. Run once via `/index-repo`.

```bash
python tools/indexer/indexer.py --project-dir /path/to/project --output .claude/index/
```

Produces: `files.json`, `symbols.json`, `graph-imports.json`, `graph-calls.json`,
`graph-clusters.json`, `manifest.json`. Supports incremental re-runs via the manifest.

---

## `tools/crawl4ai/fetch.py`

Fetches a URL through the local Crawl4AI container and returns clean Markdown.

```bash
python tools/crawl4ai/fetch.py --url "https://example.com/docs"
```

Caches output at `vault/07-web-cache/` for 24 hours. Falls back to printing
`"not reachable"` on stderr if Crawl4AI is down (callers fall back to built-in WebFetch).
