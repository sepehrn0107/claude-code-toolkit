#!/usr/bin/env python3
"""
Crawl4AI web fetch CLI for Claude Code Toolbox.

Fetches a URL via the Crawl4AI REST API, caches the result as a vault markdown
file, and prints the raw markdown to stdout. Uses urllib.request (stdlib only)
— no pip dependencies required.

Exit codes:
  0  Success — stdout contains the raw markdown content
  1  Crawl4AI unreachable, fetch failed, or config error

Usage:
  python fetch.py --url https://example.com/page
  python fetch.py --url https://example.com/page --force
  python fetch.py --url https://example.com/page --max-age-hours 48
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


# ─────────────────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────────────────

def load_config(config_path: str) -> dict:
    if not os.path.exists(config_path):
        print(f"[crawl4ai] ERROR: config not found at {config_path}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(config_path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[crawl4ai] ERROR: invalid JSON in config: {e}", file=sys.stderr)
        sys.exit(1)


# ─────────────────────────────────────────────────────────────────────────────
# URL → filesystem cache path
# ─────────────────────────────────────────────────────────────────────────────

def url_to_cache_path(url: str, cache_dir: str) -> str:
    """Convert a URL to a filesystem path under cache_dir.

    Strategy:
      - Strip scheme (https://, http://)
      - Split host from rest of URL
      - Separate query/fragment from path; append sanitized to slug
      - Replace unsafe filesystem chars with '-'; collapse repeated dashes
      - Strip .html/.htm extension; append .md

    Examples:
      https://docs.python.org/3/library/os.html
        → <cache_dir>/docs.python.org/3/library/os.md
      https://example.com/
        → <cache_dir>/example.com/index.md
      https://example.com/page?foo=bar
        → <cache_dir>/example.com/page-foo-bar.md
    """
    stripped = re.sub(r'^https?://', '', url)

    if '/' in stripped:
        host, rest = stripped.split('/', 1)
    else:
        host = stripped
        rest = ''

    path_part = rest
    suffix = ''
    for sep in ('?', '#'):
        if sep in path_part:
            idx = path_part.index(sep)
            suffix += '-' + path_part[idx + 1:]
            path_part = path_part[:idx]

    path_part = path_part.rstrip('/')
    if not path_part:
        path_part = 'index'

    segments = [s for s in path_part.split('/') if s]

    def sanitize(s: str) -> str:
        s = re.sub(r'[^\w\-.]', '-', s)
        s = re.sub(r'-{2,}', '-', s)
        return s.strip('-')

    sanitized = [sanitize(s) for s in segments]
    slug = sanitized[-1] if sanitized else 'index'
    dir_parts = sanitized[:-1]

    if suffix:
        suffix = re.sub(r'[^\w\-]', '-', suffix)
        suffix = re.sub(r'-{2,}', '-', suffix).strip('-')
        slug = slug + '-' + suffix

    slug = re.sub(r'\.(html?|htm)$', '', slug, flags=re.IGNORECASE)
    filename = slug + '.md'

    return os.path.join(cache_dir, host, *dir_parts, filename)


# ─────────────────────────────────────────────────────────────────────────────
# Cache: read / write / freshness
# ─────────────────────────────────────────────────────────────────────────────

def _parse_fetched_at(cache_file: str) -> Optional[datetime]:
    """Extract fetched_at timestamp from YAML frontmatter."""
    try:
        with open(cache_file, encoding='utf-8') as f:
            lines = f.readlines()
    except OSError:
        return None

    if not lines or lines[0].strip() != '---':
        return None

    for line in lines[1:]:
        stripped = line.strip()
        if stripped == '---':
            break
        if stripped.startswith('fetched_at:'):
            value = stripped[len('fetched_at:'):].strip()
            try:
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                return None
    return None


def cache_is_fresh(cache_file: str, max_age_hours: float) -> bool:
    if not os.path.exists(cache_file):
        return False
    fetched_at = _parse_fetched_at(cache_file)
    if fetched_at is None:
        return False
    return datetime.now(timezone.utc) - fetched_at < timedelta(hours=max_age_hours)


def read_cache_content(cache_file: str) -> str:
    """Return body of cache file (everything after the closing ---)."""
    with open(cache_file, encoding='utf-8') as f:
        content = f.read()
    if content.startswith('---'):
        end = content.find('\n---', 3)
        if end != -1:
            return content[end + 4:].lstrip('\n')
    return content


def write_cache(cache_file: str, url: str, markdown: str) -> None:
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    frontmatter = (
        f"---\n"
        f"url: {url}\n"
        f"fetched_at: {now}\n"
        f"last_updated: {now}\n"
        f"source: crawl4ai\n"
        f"---\n\n"
    )
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    with open(cache_file, 'w', encoding='utf-8') as f:
        f.write(frontmatter + markdown)


# ─────────────────────────────────────────────────────────────────────────────
# Crawl4AI API
# ─────────────────────────────────────────────────────────────────────────────

def _http_get(url: str, timeout: int) -> dict:
    req = urllib.request.Request(url, method='GET')
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode('utf-8'))


def _poll_task(task_id: str, base_url: str, timeout: int) -> dict:
    """Poll /task/{task_id} until status == 'completed' or timeout."""
    endpoint = base_url.rstrip('/') + f'/task/{task_id}'
    deadline = time.monotonic() + timeout
    poll_interval = 2

    while time.monotonic() < deadline:
        try:
            data = _http_get(endpoint, timeout=min(10, int(deadline - time.monotonic()) + 1))
        except (urllib.error.URLError, OSError):
            time.sleep(poll_interval)
            continue

        status = data.get('status', '')
        if status == 'completed':
            return data
        if status == 'failed':
            print(
                f"[crawl4ai] ERROR: task {task_id} failed: {data.get('error', 'unknown')}",
                file=sys.stderr,
            )
            sys.exit(1)

        time.sleep(poll_interval)

    print(
        f"[crawl4ai] ERROR: task {task_id} timed out after {timeout}s",
        file=sys.stderr,
    )
    sys.exit(1)


def _extract_markdown(data: dict) -> Optional[str]:
    """Try multiple known response shapes to extract raw markdown text."""
    # Shape 1 (sync): { "result": { "markdown": { "raw_markdown": "..." } } }
    result = data.get('result')
    if isinstance(result, dict):
        md = result.get('markdown')
        if isinstance(md, dict):
            raw = md.get('raw_markdown')
            if isinstance(raw, str):
                return raw
        if isinstance(md, str):
            return md

    # Shape 2 (list): { "results": [{ "markdown": {...} }] }
    results = data.get('results')
    if isinstance(results, list) and results:
        first = results[0]
        if isinstance(first, dict):
            md = first.get('markdown')
            if isinstance(md, dict):
                return md.get('raw_markdown')
            if isinstance(md, str):
                return md

    # Shape 3 (top-level): { "markdown": { "raw_markdown": "..." } }
    md = data.get('markdown')
    if isinstance(md, dict):
        return md.get('raw_markdown')
    if isinstance(md, str):
        return md

    return None


def fetch_via_crawl4ai(url: str, base_url: str, priority: int, timeout: int) -> str:
    endpoint = base_url.rstrip('/') + '/crawl'
    payload = json.dumps({"urls": [url], "priority": priority}).encode('utf-8')
    req = urllib.request.Request(
        endpoint,
        data=payload,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        print(f"[crawl4ai] ERROR: HTTP {e.code} from Crawl4AI\n{body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(
            f"[crawl4ai] ERROR: Crawl4AI not reachable at {base_url}\n"
            f"  Reason: {e.reason}\n"
            f"  Is the container running? Try:\n"
            f"    docker ps --filter name=crawl4ai\n"
            f"    docker run -d -p 11235:11235 --name crawl4ai --shm-size=1g unclecode/crawl4ai:latest",
            file=sys.stderr,
        )
        sys.exit(1)
    except OSError as e:
        print(f"[crawl4ai] ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(body)
    except json.JSONDecodeError as e:
        print(f"[crawl4ai] ERROR: non-JSON response: {e}", file=sys.stderr)
        sys.exit(1)

    # Handle async task response
    task_id = data.get('task_id')
    if task_id:
        print(f"[crawl4ai] async task {task_id}, polling...", file=sys.stderr)
        data = _poll_task(task_id, base_url, timeout)

    markdown = _extract_markdown(data)
    if markdown is None:
        print(
            f"[crawl4ai] ERROR: could not find markdown in response.\n"
            f"  Response keys: {list(data.keys())}",
            file=sys.stderr,
        )
        sys.exit(1)

    return markdown


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description='Fetch a URL via Crawl4AI, cache to vault, print markdown to stdout.'
    )
    parser.add_argument('--url', required=True, help='URL to fetch')
    parser.add_argument('--force', action='store_true', help='Bypass cache, always re-fetch')
    parser.add_argument('--max-age-hours', type=float, default=None,
                        help='Max cache age in hours (default: from config)')
    parser.add_argument('--config', default=os.path.join(SCRIPT_DIR, 'config.json'),
                        help='Path to config.json')
    args = parser.parse_args()

    cfg = load_config(args.config)
    base_url  = cfg.get('base_url', 'http://localhost:11235')
    timeout   = int(cfg.get('timeout_seconds', 30))
    priority  = int(cfg.get('priority', 10))
    cache_dir = cfg.get('vault_cache_dir', '')
    max_age   = args.max_age_hours if args.max_age_hours is not None else cfg.get('max_age_hours', 24)

    if not cache_dir:
        print('[crawl4ai] ERROR: vault_cache_dir not set in config.json', file=sys.stderr)
        sys.exit(1)

    url = args.url
    cache_file = url_to_cache_path(url, cache_dir)

    if not args.force and cache_is_fresh(cache_file, max_age):
        print(f'[crawl4ai] cache hit: {cache_file}', file=sys.stderr)
        print(read_cache_content(cache_file))
        sys.exit(0)

    if os.path.exists(cache_file):
        print(f'[crawl4ai] stale cache, re-fetching: {url}', file=sys.stderr)
    else:
        print(f'[crawl4ai] fetching: {url}', file=sys.stderr)

    markdown = fetch_via_crawl4ai(url, base_url, priority, timeout)
    write_cache(cache_file, url, markdown)
    print(f'[crawl4ai] cached to: {cache_file}', file=sys.stderr)
    print(markdown)
    sys.exit(0)


if __name__ == '__main__':
    main()
