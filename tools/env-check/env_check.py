#!/usr/bin/env python3
"""
Dev environment snapshot for Claude Code Toolbox.

Returns a compact summary of the local dev environment in a single call:
  - Language runtime versions (Python, Node, Go, git)
  - Running Docker containers (name + port mappings)
  - Listening on common dev ports
  - .env file presence in cwd (not contents — never reads secrets)

Always exits 0 — best-effort, never fails.

Usage:
  python env_check.py
"""

import os
import re
import socket
import subprocess
import sys
from pathlib import Path


def run(cmd, timeout=5):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip() if r.returncode == 0 else None
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


def version(cmd, pattern=r"(\d+\.\d+[\.\d]*)"):
    out = run(cmd)
    if not out:
        return None
    m = re.search(pattern, out)
    return m.group(1) if m else out.split("\n")[0][:30]


def port_open(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.4):
            return True
    except OSError:
        return False


COMMON_PORTS = {
    3000: "Next.js/React",
    3001: "dev-alt",
    4000: "dev",
    4200: "Angular",
    5000: "Flask/dev",
    5173: "Vite",
    5432: "PostgreSQL",
    6379: "Redis",
    8000: "Django/FastAPI",
    8080: "dev-proxy",
    8888: "Jupyter",
    9000: "dev",
    11235: "Crawl4AI",
    27017: "MongoDB",
}

ENV_FILES = [
    ".env",
    ".env.local",
    ".env.development",
    ".env.production",
    ".env.test",
    ".env.example",
]


def main():
    lines = []

    # ── Runtimes ─────────────────────────────────────────────────────────────
    runtimes = []
    for cmd, label in [
        (["python", "--version"], "python"),
        (["python3", "--version"], "python"),
        (["node", "--version"], "node"),
        (["go", "version"], "go"),
        (["git", "--version"], "git"),
    ]:
        v = version(cmd)
        if v and label not in [r.split()[0] for r in runtimes]:
            runtimes.append(f"{label} {v}")

    if runtimes:
        lines.append("runtimes: " + ", ".join(runtimes))

    # ── Docker ───────────────────────────────────────────────────────────────
    docker_out = run(["docker", "ps", "--format", "{{.Names}} ({{.Ports}})"])
    if docker_out:
        containers = [l.strip() for l in docker_out.splitlines() if l.strip()]
        lines.append(f"docker: {len(containers)} container{'s' if len(containers) != 1 else ''} running")
        for c in containers[:6]:
            lines.append(f"  {c}")
        if len(containers) > 6:
            lines.append(f"  ... and {len(containers) - 6} more")
    else:
        lines.append("docker: not running or not installed")

    # ── Listening ports ───────────────────────────────────────────────────────
    open_ports = [
        f"{port} ({label})"
        for port, label in COMMON_PORTS.items()
        if port_open(port)
    ]
    lines.append("ports: " + (", ".join(open_ports) if open_ports else "none detected"))

    # ── .env files ────────────────────────────────────────────────────────────
    cwd = Path.cwd()
    found = [f for f in ENV_FILES if (cwd / f).exists()]
    if found:
        lines.append(f"env files: {', '.join(found)}")
    else:
        lines.append("env files: none found in cwd")

    print("\n".join(lines))
    sys.exit(0)


if __name__ == "__main__":
    main()
