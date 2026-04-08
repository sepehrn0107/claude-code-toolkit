---
name: web-fetch
description: Use this skill whenever Claude needs to read any external URL — checking documentation, reading a web page, fetching a spec, or any outbound fetch where full page content is needed. Auto-triggers instead of WebFetch when reading a page for its content. Runs fetch.py via Bash, reads stdout as the page markdown. Falls back to WebFetch if Crawl4AI is not running.
---

# /web-fetch

Use this skill to fetch any external URL. Routes through Crawl4AI for clean
markdown output and caches results in the vault under `07-web-cache/`.

## When This Skill Triggers

Auto-trigger whenever Claude is about to:
- Use the `WebFetch` tool to read a page's full content
- Follow a URL from search results to read it
- Fetch external documentation, specs, changelogs, or READMEs

Do NOT trigger for searches where only the title/snippet matters — only when
the full page body is needed.

---

## How to Fetch

Run via Bash:

```bash
python {{TOOLBOX_PATH}}/tools/crawl4ai/fetch.py --url "<URL>"
```

Optional flags:
- `--force` — bypass cache, always re-fetch
- `--max-age-hours <N>` — override default cache TTL (default: 24h from config)

### Reading the output

| Stream | Meaning |
|--------|---------|
| **stdout** | Page content as clean markdown — this is what you read and reason over |
| **stderr** | Status messages (`cache hit`, `fetching`, `cached to`, errors) — informational only |
| **exit 0** | Success |
| **exit 1** | Error — see stderr |

### Cache behaviour

If the URL was fetched within the last 24 hours, the cached version is returned
instantly (stderr: `cache hit`). Cache lives at:

```
{{VAULT_PATH}}/07-web-cache/<domain>/<path>.md
```

Each cache file uses vault frontmatter format:
```
---
url: <original url>
fetched_at: <ISO timestamp>
last_updated: <ISO timestamp>
source: crawl4ai
---
<markdown content>
```

---

## Fallback Protocol

If exit code is 1 and stderr contains `"not reachable"`:

1. Log: `[web-fetch] Crawl4AI unavailable — falling back to WebFetch`
2. Use the built-in `WebFetch` tool for the same URL
3. Do not retry `fetch.py` again in this session
4. Remind the user:
   ```
   Crawl4AI is not running. Start it with:
   docker run -d -p 11235:11235 --name crawl4ai --shm-size=1g unclecode/crawl4ai:latest
   ```

For any other exit 1 (HTTP error, config error, parse error): report the stderr
message to the user and stop — do not silently fall back.

---

## Examples

```bash
# Standard fetch (uses cache if fresh)
python {{TOOLBOX_PATH}}/tools/crawl4ai/fetch.py --url "https://docs.python.org/3/library/pathlib.html"

# Force re-fetch (ignore cache)
python {{TOOLBOX_PATH}}/tools/crawl4ai/fetch.py --url "https://example.com/changelog" --force

# Longer cache TTL for stable reference docs
python {{TOOLBOX_PATH}}/tools/crawl4ai/fetch.py --url "https://docs.python.org/3/reference/expressions.html" --max-age-hours 168
```
