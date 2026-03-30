#!/usr/bin/env python3
"""
Package info fetcher for Claude Code Toolbox.

Fetches package metadata from npm or PyPI JSON APIs and returns a compact
one-screen summary. Results are cached for 24 h to avoid repeat network calls.
Uses urllib.request (stdlib only) — no pip dependencies required.

Usage:
  python pkg_info.py --name <package>
  python pkg_info.py --name <package> --registry npm|pypi
  python pkg_info.py --name <package> --force
  python pkg_info.py --name <package> --max-age-hours 72

Exit codes:
  0  Success — stdout contains the summary
  1  Package not found, registry unreachable, or config error
"""

import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path


CACHE_DIR = Path.home() / ".claude" / "cache" / "pkg-info"
DEFAULT_TTL = 24


# ─────────────────────────────────────────────────────────────────────────────
# Cache helpers
# ─────────────────────────────────────────────────────────────────────────────

def _cache_path(name: str, registry: str) -> Path:
    safe = name.replace("/", "__").replace("@", "at-")
    return CACHE_DIR / f"{registry}-{safe}.json"


def _read_cache(path: Path, max_age_hours: float):
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        cached_at = datetime.fromisoformat(data.get("_cached_at", "2000-01-01T00:00:00+00:00"))
        if cached_at.tzinfo is None:
            cached_at = cached_at.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) - cached_at < timedelta(hours=max_age_hours):
            return data
    except (json.JSONDecodeError, ValueError, KeyError):
        pass
    return None


def _write_cache(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data["_cached_at"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(data))


# ─────────────────────────────────────────────────────────────────────────────
# HTTP
# ─────────────────────────────────────────────────────────────────────────────

def _http_get(url: str, timeout: int = 10):
    req = urllib.request.Request(url, headers={"User-Agent": "claude-toolbox/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        print(f"[pkg-info] HTTP {e.code}: {url}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"[pkg-info] ERROR: registry unreachable — {e.reason}", file=sys.stderr)
        sys.exit(1)


# ─────────────────────────────────────────────────────────────────────────────
# Registry fetchers
# ─────────────────────────────────────────────────────────────────────────────

def _fmt_downloads(n) -> str:
    if not isinstance(n, int):
        return str(n)
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.0f}K"
    return str(n)


def fetch_npm(name: str) -> dict | None:
    data = _http_get(f"https://registry.npmjs.org/{name}")
    if not data:
        return None

    latest = data.get("dist-tags", {}).get("latest", "")
    vdata = data.get("versions", {}).get(latest, {})

    # TypeScript types
    bundled = bool(vdata.get("types") or vdata.get("typings"))
    if bundled:
        types_str = "bundled"
    else:
        bare = name.lstrip("@").split("/")[0]
        types_str = f"@types/{bare} (check separately)"

    # Weekly downloads
    dl = _http_get(f"https://api.npmjs.org/downloads/point/last-week/{name}") or {}
    downloads = _fmt_downloads(dl.get("downloads", "n/a"))

    published = data.get("time", {}).get(latest, "")[:10]

    return {
        "name": name,
        "registry": "npm",
        "version": latest,
        "description": data.get("description", ""),
        "types": types_str,
        "homepage": data.get("homepage") or vdata.get("homepage", ""),
        "license": vdata.get("license") or data.get("license", ""),
        "published": published,
        "weekly_downloads": downloads,
    }


def fetch_pypi(name: str) -> dict | None:
    data = _http_get(f"https://pypi.org/pypi/{name}/json")
    if not data:
        return None

    info = data.get("info", {})
    urls = data.get("urls", [])
    published = ""
    if urls:
        published = (urls[0].get("upload_time") or "")[:10]

    return {
        "name": name,
        "registry": "pypi",
        "version": info.get("version", ""),
        "description": info.get("summary", ""),
        "types": "see py.typed / stubs",
        "homepage": info.get("home_page") or info.get("project_url", ""),
        "license": info.get("license", ""),
        "published": published,
        "weekly_downloads": "n/a",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Formatting
# ─────────────────────────────────────────────────────────────────────────────

def format_info(info: dict) -> str:
    rows = [
        f'package: {info["name"]} ({info["registry"]})',
        f'version: {info["version"]}',
    ]
    if info.get("description"):
        rows.append(f'description: {info["description"]}')
    if info.get("types"):
        rows.append(f'types: {info["types"]}')
    if info.get("homepage"):
        rows.append(f'homepage: {info["homepage"]}')
    if info.get("license"):
        rows.append(f'license: {info["license"]}')
    if info.get("published"):
        rows.append(f'published: {info["published"]}')
    if info.get("weekly_downloads") and info["weekly_downloads"] != "n/a":
        rows.append(f'weekly downloads: {info["weekly_downloads"]}')
    return "\n".join(rows)


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Fetch package metadata from npm or PyPI")
    parser.add_argument("--name", required=True, help="Package name")
    parser.add_argument(
        "--registry",
        choices=["npm", "pypi", "auto"],
        default="auto",
        help="Registry to query (default: auto — npm for @scoped or default, pypi if not found)",
    )
    parser.add_argument("--force", action="store_true", help="Bypass cache, always re-fetch")
    parser.add_argument(
        "--max-age-hours", type=float, default=DEFAULT_TTL,
        help=f"Cache TTL in hours (default: {DEFAULT_TTL})",
    )
    args = parser.parse_args()

    registry = (
        args.registry
        if args.registry != "auto"
        else ("npm" if args.name.startswith("@") else "npm")
    )

    cp = _cache_path(args.name, registry)

    if not args.force:
        cached = _read_cache(cp, args.max_age_hours)
        if cached:
            print(f"[pkg-info] cache hit: {cp}", file=sys.stderr)
            print(format_info(cached))
            sys.exit(0)

    print(f"[pkg-info] fetching {args.name} from {registry}...", file=sys.stderr)

    if registry == "npm":
        info = fetch_npm(args.name)
        if not info and args.registry == "auto":
            # Fallback: try PyPI
            print("[pkg-info] not found on npm, trying pypi...", file=sys.stderr)
            registry = "pypi"
            cp = _cache_path(args.name, registry)
            info = fetch_pypi(args.name)
    else:
        info = fetch_pypi(args.name)

    if not info:
        print(
            f'[pkg-info] ERROR: package "{args.name}" not found on {registry}',
            file=sys.stderr,
        )
        sys.exit(1)

    _write_cache(cp, info)
    print(f"[pkg-info] cached to: {cp}", file=sys.stderr)
    print(format_info(info))
    sys.exit(0)


if __name__ == "__main__":
    main()
