#!/usr/bin/env python3
"""
Compact git diff summary for Claude Code Toolbox.

Returns a per-file change summary with +/- counts and changed symbol names.
Replaces reading full `git diff` output before commits or PRs.

Usage:
  python diff_summary.py
  python diff_summary.py --base main
  python diff_summary.py --staged
  python diff_summary.py --full

Exit codes:
  0  Success — stdout contains the summary
  1  Not a git repo, no changes, or git unavailable
"""

import argparse
import re
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


# ─────────────────────────────────────────────────────────────────────────────
# Stat parsing
# ─────────────────────────────────────────────────────────────────────────────

def parse_numstat(numstat_output):
    """Parse `git diff --numstat` into per-file dicts."""
    files = []
    for line in numstat_output.splitlines():
        parts = line.split("\t", 2)
        if len(parts) == 3:
            add_s, del_s, path = parts
            try:
                files.append({
                    "path": path.strip(),
                    "add": int(add_s) if add_s != "-" else 0,
                    "del": int(del_s) if del_s != "-" else 0,
                })
            except ValueError:
                continue
    return files


# ─────────────────────────────────────────────────────────────────────────────
# Symbol extraction from diff hunks
# ─────────────────────────────────────────────────────────────────────────────

def extract_symbols_for_file(diff_output, filepath):
    """Extract function/class names from @@ hunk headers for a given file path."""
    symbols = []
    in_file = False

    for line in diff_output.splitlines():
        if line.startswith("diff --git"):
            in_file = False
        elif line.startswith("+++ b/"):
            current = line[6:]
            in_file = current == filepath or current.endswith("/" + filepath)
        elif in_file and line.startswith("@@"):
            # @@ -10,7 +10,9 @@ function foo() {
            m = re.search(r"@@[^@]*@@\s*(.*)", line)
            if m:
                ctx = m.group(1).strip()
                sym = re.search(
                    r"(?:function|def|async\s+def|func|class|interface|struct|fn)\s+(\w+)",
                    ctx,
                )
                if sym and sym.group(1) not in symbols:
                    symbols.append(sym.group(1))

    return symbols


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Compact git diff summary")
    parser.add_argument(
        "--base",
        default=None,
        help="Base ref to compare against (default: auto-detect main/master/develop)",
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Summarise staged changes only (index vs HEAD)",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Append the full diff after the summary",
    )
    args = parser.parse_args()

    # Verify git repo
    _, err = run_git(["rev-parse", "--git-dir"])
    if err:
        print(f"[diff-summary] ERROR: {err}", file=sys.stderr)
        sys.exit(1)

    # Build diff args
    if args.staged:
        numstat_args = ["diff", "--numstat", "--staged"]
        full_args = ["diff", "--staged"]
        label = "staged changes"
    elif args.base:
        numstat_args = ["diff", "--numstat", f"{args.base}...HEAD"]
        full_args = ["diff", f"{args.base}...HEAD"]
        label = f"{args.base}...HEAD"
    else:
        base = None
        for candidate in ("main", "master", "develop"):
            out, _ = run_git(["rev-parse", "--verify", candidate])
            if out:
                base = candidate
                break
        if base:
            numstat_args = ["diff", "--numstat", f"{base}...HEAD"]
            full_args = ["diff", f"{base}...HEAD"]
            label = f"{base}...HEAD"
        else:
            numstat_args = ["diff", "--numstat", "HEAD"]
            full_args = ["diff", "HEAD"]
            label = "working tree vs HEAD"

    numstat_out, err = run_git(numstat_args)
    if err or not numstat_out:
        print("[diff-summary] no changes detected", file=sys.stderr)
        sys.exit(1)

    file_stats = parse_numstat(numstat_out)
    if not file_stats:
        print("[diff-summary] no changes detected", file=sys.stderr)
        sys.exit(1)

    full_diff, _ = run_git(full_args)

    total_add = sum(f["add"] for f in file_stats)
    total_del = sum(f["del"] for f in file_stats)
    n = len(file_stats)

    out_lines = [
        f'diff: {label} ({n} file{"s" if n != 1 else ""}, +{total_add} -{total_del})'
    ]

    for f in file_stats:
        symbols = extract_symbols_for_file(full_diff or "", f["path"]) if full_diff else []
        sym_note = f'  [{", ".join(symbols)}]' if symbols else ""
        path_col = f'  {f["path"]}'
        stat_col = f'+{f["add"]} -{f["del"]}'
        out_lines.append(f"{path_col:<52}{stat_col}{sym_note}")

    if args.full and full_diff:
        out_lines.append("")
        out_lines.append("--- full diff ---")
        out_lines.append(full_diff)

    print("\n".join(out_lines))
    sys.exit(0)


if __name__ == "__main__":
    main()
