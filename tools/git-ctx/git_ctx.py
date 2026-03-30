#!/usr/bin/env python3
"""
Compact git context CLI for Claude Code Toolbox.

Returns a structured summary of the current git state in ~15 lines:
  - branch + tracking info (ahead/behind)
  - staged / unstaged / untracked counts
  - recent N commits (one-liner each)
  - working tree diff stat

Replaces running git status + git log + git diff separately.

Exit codes:
  0  Success — stdout contains the summary
  1  Not a git repo or git not available
"""

import argparse
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def run_git(args, cwd=None):
    try:
        r = subprocess.run(
            ["git"] + args,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            cwd=cwd,
        )
        stdout = r.stdout.strip() if r.stdout else None
        stderr = r.stderr.strip() if r.stderr else None
        return (stdout, None) if r.returncode == 0 else (None, stderr)
    except FileNotFoundError:
        return None, "git not found in PATH"


def main():
    parser = argparse.ArgumentParser(description="Compact git context summary")
    parser.add_argument("--repo", default=".", help="Path to git repo (default: .)")
    parser.add_argument("--log", type=int, default=5, help="Recent commits to show (default: 5)")
    args = parser.parse_args()

    repo = args.repo

    _, err = run_git(["rev-parse", "--git-dir"], cwd=repo)
    if err:
        print(f"[git-ctx] ERROR: {err}", file=sys.stderr)
        sys.exit(1)

    lines = []

    # ── Branch + tracking ────────────────────────────────────────────────────
    branch, _ = run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=repo)
    branch = branch or "(detached HEAD)"

    tracking, _ = run_git(
        ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], cwd=repo
    )
    if tracking:
        ahead_raw, _ = run_git(["rev-list", "--count", f"{tracking}..HEAD"], cwd=repo)
        behind_raw, _ = run_git(["rev-list", "--count", f"HEAD..{tracking}"], cwd=repo)
        ahead = int(ahead_raw or 0)
        behind = int(behind_raw or 0)
        track_info = f" ({ahead} ahead, {behind} behind {tracking})"
    else:
        track_info = " (no upstream)"

    lines.append(f"branch: {branch}{track_info}")

    # ── Status counts ────────────────────────────────────────────────────────
    status_out, _ = run_git(["status", "--porcelain"], cwd=repo)
    staged = unstaged = untracked = 0
    if status_out:
        for line in status_out.splitlines():
            if len(line) < 2:
                continue
            x, y = line[0], line[1]
            if x not in (" ", "?"):
                staged += 1
            if y in ("M", "D"):
                unstaged += 1
            if x == "?" and y == "?":
                untracked += 1

    lines.append(f"status: {staged} staged, {unstaged} unstaged, {untracked} untracked")

    # ── Recent commits ───────────────────────────────────────────────────────
    log_out, _ = run_git(
        ["log", "--format=%h %s (%cr)", f"-{args.log}"], cwd=repo
    )
    if log_out:
        lines.append(f"recent commits (last {args.log}):")
        for commit_line in log_out.splitlines():
            lines.append(f"  {commit_line}")
    else:
        lines.append("recent commits: (none)")

    # ── Diff stat ────────────────────────────────────────────────────────────
    diff_stat, _ = run_git(["diff", "--stat", "HEAD"], cwd=repo)
    if diff_stat:
        summary = diff_stat.splitlines()[-1].strip()
        lines.append(f"working tree: {summary}")

    print("\n".join(lines))
    sys.exit(0)


if __name__ == "__main__":
    main()
