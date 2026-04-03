---
title: "Code Tool Skills"
section: skills
skills-affected: [read-section, grep, diff-summary, git-ctx, env-check, pkg-info, index-repo, web-fetch]
last-updated: 2026-04-03
---

# Code Tool Skills

These skills are triggered automatically by Claude's own internal actions — no user
prompt required. They enforce efficient, low-waste tool use.

## `/read-section` — extract one symbol from a large file

**Auto-triggered:** when Claude needs one function, class, or section from a file
over 100 lines.

Runs `tools/read-section/read_section.py` with language-aware extraction:

```bash
python tools/read-section/read_section.py --file src/auth.ts --fn validateToken
```

Returns only the requested block — not the full file. Prevents loading a 400-line
controller to read a 30-line function.

---

## `/grep` — two-phase code search

**Auto-triggered:** before any code search with Grep.

Enforces a two-phase pattern:
1. First pass: retrieve only matching file paths (no content)
2. Second pass: read content from the specific files identified

Broad content searches across the full repo on the first attempt are prohibited.
All searches cap output with `head_limit` to prevent unbounded result sets.

---

## `/diff-summary` — structured diff context

**Auto-triggered:** before reading `git diff` to draft a commit message or PR body.

Produces a structured summary of what changed and why — file-by-file, with a
one-line description per change. Used by `/git-push` and `/implement` Phase 5.

---

## `/git-ctx` — batch git state

**Auto-triggered:** when Claude needs to run multiple git commands (status, log,
diff, branch).

Batches all git state into a single parallel tool call instead of sequential commands.
Returns one structured context block covering branch, status, recent log, and diff stat.

---

## `/env-check` — runtime environment

**Auto-triggered:** when Claude needs runtime versions, running ports, Docker state,
or `.env` file presence.

Runs `tools/env-check/env_check.py` — checks Python/Node/Go versions, open ports,
Docker container status, and whether `.env` exists and is git-ignored.

---

## `/pkg-info` — package metadata

**Auto-triggered:** when Claude needs version, types, license, or popularity for
an npm or PyPI package.

Runs `tools/pkg-info/pkg_info.py` — queries the registry and returns the latest
version, TypeScript types availability, license, weekly downloads, and homepage.

---

## `/index-repo` — build structural code index

**Trigger:** `"/index-repo"` (run once per project, re-run after major changes)

Builds a structural map of the codebase — every file, its exported symbols, imports,
and call relationships. Stored in `.claude/index/` as JSON files.

After indexing, structural questions ("what calls X?", "what imports Y?") are answered
by a Haiku sub-agent that reads only the relevant index file — not the source. Keeps
searches fast and context usage low.

Supports incremental re-runs (only changed files re-processed).

---

## `/web-fetch` — cached clean web content

**Auto-triggered:** before any `WebFetch` call.

Routes fetches through the local Crawl4AI container (if running). Returns clean
Markdown output and caches pages for 24 hours — the same URL is never fetched twice
in a day. Falls back to Claude's built-in `WebFetch` if Crawl4AI is unreachable.
