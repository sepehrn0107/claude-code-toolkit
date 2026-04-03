---
title: "Optional Setup"
section: user-guide
skills-affected: [web-fetch, codex-delegate]
last-updated: 2026-04-03
---

# Optional Setup

These features are not required for the toolkit to work. Each adds a specific capability.

## Codex CLI — automatic Phase 3 delegation

When Codex CLI is installed, `/implement` Phase 3 (implementation) delegates to Codex
automatically. Claude falls back silently if Codex is unavailable.

```bash
npm install -g @openai/codex
codex   # authenticate once via browser
```

After installing, say `/upgrade` so the toolkit registers it.

## Crawl4AI — clean web fetching

Routes all `WebFetch` calls through a local Crawl4AI container. Outputs clean Markdown,
caches pages for 24 hours — the same URL is never fetched twice in a day. Requires Docker.

```bash
docker run -d -p 11235:11235 --name crawl4ai --shm-size=1g unclecode/crawl4ai:latest
```

Without this, the toolkit falls back to Claude's built-in `WebFetch`.

## Local LLM — zero API cost for mechanical tasks

Routes mechanical tasks (boilerplate, docstrings, simple refactors, unit test scaffolding)
to a local model via LM Studio. Results are cached for 24 hours.

1. Install [LM Studio](https://lmstudio.ai) and download a model
2. Start the local server in LM Studio (default port: 1234)
3. Edit `toolbox/tools/local-llm/config.json` to point at your model

Claude checks LM Studio availability at session start. If unreachable, it falls back to
a Haiku sub-agent silently.
