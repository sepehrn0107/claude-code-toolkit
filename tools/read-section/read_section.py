#!/usr/bin/env python3
"""
Read a specific section of a source file for Claude Code Toolbox.

Extracts only the relevant block rather than forcing Claude to read an entire
large file. Supports function, class/interface/struct, markdown heading, and
raw line range.

Usage:
  python read_section.py --file <path> --fn <name>
  python read_section.py --file <path> --class <name>
  python read_section.py --file <path> --after "<heading>"
  python read_section.py --file <path> --lines 100-150

Exit codes:
  0  Found — stdout contains the section content
  1  Not found, bad args, or file unreadable
"""

import argparse
import re
import sys

# Ensure UTF-8 output on Windows (default is cp1252)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


PYTHON_EXTS = {"py", "pyi"}


# ─────────────────────────────────────────────────────────────────────────────
# File I/O
# ─────────────────────────────────────────────────────────────────────────────

def read_lines(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.readlines()
    except OSError as e:
        print(f"[read-section] ERROR: {e}", file=sys.stderr)
        sys.exit(1)


def file_ext(path):
    if "." in path:
        return path.rsplit(".", 1)[-1].lower()
    return ""


# ─────────────────────────────────────────────────────────────────────────────
# Block extraction
# ─────────────────────────────────────────────────────────────────────────────

def extract_brace_block(lines, start_idx):
    """Extract a {}-delimited block starting at start_idx."""
    depth = 0
    found_open = False
    end_idx = start_idx

    for i in range(start_idx, len(lines)):
        for ch in lines[i]:
            if ch == "{":
                depth += 1
                found_open = True
            elif ch == "}":
                depth -= 1
        if found_open and depth == 0:
            end_idx = i
            break
    else:
        end_idx = len(lines) - 1

    return start_idx, end_idx, lines[start_idx : end_idx + 1]


def extract_indent_block(lines, start_idx):
    """Extract an indentation-delimited block (Python style)."""
    def indent_of(line):
        return len(line) - len(line.lstrip())

    base_indent = indent_of(lines[start_idx])
    end_idx = start_idx

    for i in range(start_idx + 1, len(lines)):
        line = lines[i]
        if not line.strip():
            continue
        if indent_of(line) <= base_indent:
            end_idx = i - 1
            break
        end_idx = i

    # Trim trailing blank lines
    while end_idx > start_idx and not lines[end_idx].strip():
        end_idx -= 1

    return start_idx, end_idx, lines[start_idx : end_idx + 1]


# ─────────────────────────────────────────────────────────────────────────────
# Definition finding
# ─────────────────────────────────────────────────────────────────────────────

def find_definition(lines, name, kind):
    """Return the line index (0-based) of the first definition matching name+kind."""
    escaped = re.escape(name)

    if kind == "fn":
        patterns = [
            # Python: def foo( / async def foo(
            rf"^\s*(?:async\s+)?def\s+{escaped}\s*[\(:]",
            # JS/TS: function foo( / async function foo(
            rf"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+{escaped}\s*[\(<]",
            # JS/TS arrow: const foo = ( / const foo = async (
            rf"^\s*(?:export\s+)?(?:const|let|var)\s+{escaped}\s*=\s*(?:async\s*)?\(",
            # Class method: foo( / async foo( with access modifier
            rf"^\s*(?:(?:public|private|protected|static|async|override)\s+)+{escaped}\s*\(",
            # Go: func foo( / func (recv) foo(
            rf"^\s*func\s+(?:\([^)]*\)\s*)?{escaped}\s*\(",
            # Rust: fn foo(
            rf"^\s*(?:pub\s+)?(?:async\s+)?fn\s+{escaped}\s*[\(<]",
        ]
    else:  # class
        patterns = [
            # class / interface / struct / enum / type (TS/JS/Java/C#/Go)
            rf"^\s*(?:export\s+)?(?:abstract\s+)?(?:class|interface|struct|enum|type)\s+{escaped}[\s{{<(]",
            rf"^\s*(?:public|private|internal)\s+(?:abstract\s+)?(?:class|interface|enum)\s+{escaped}[\s{{]",
            # Rust struct/enum/trait
            rf"^\s*(?:pub\s+)?(?:struct|enum|trait|impl)\s+{escaped}[\s{{<]",
        ]

    for i, line in enumerate(lines):
        for pattern in patterns:
            if re.search(pattern, line):
                return i

    return -1


# ─────────────────────────────────────────────────────────────────────────────
# Markdown section
# ─────────────────────────────────────────────────────────────────────────────

def find_md_section(lines, heading):
    """Find a markdown section by heading text. Returns (start_idx, end_idx)."""
    target = heading.strip().lstrip("#").strip().lower()

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue
        level = len(stripped) - len(stripped.lstrip("#"))
        text = stripped.lstrip("#").strip().lower()
        if text != target:
            continue
        # Found — scan for the next heading at same or higher level
        for j in range(i + 1, len(lines)):
            next_stripped = lines[j].strip()
            if next_stripped.startswith("#"):
                next_level = len(next_stripped) - len(next_stripped.lstrip("#"))
                if next_level <= level:
                    return i, j - 1
        return i, len(lines) - 1

    return -1, -1


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Extract a specific section from a source file"
    )
    parser.add_argument("--file", required=True, help="Path to the file")
    parser.add_argument("--fn", help="Function name to extract")
    parser.add_argument("--class", dest="cls", help="Class/interface/struct name to extract")
    parser.add_argument("--after", help="Markdown heading — extract the section below it")
    parser.add_argument("--lines", help="Line range, e.g. 100-150")
    args = parser.parse_args()

    lines = read_lines(args.file)
    total = len(lines)

    # ── Line range ───────────────────────────────────────────────────────────
    if args.lines:
        try:
            parts = args.lines.split("-")
            start = max(0, int(parts[0]) - 1)
            end = min(total - 1, int(parts[1]) - 1 if len(parts) > 1 else start)
            content = lines[start : end + 1]
            print(f"[read-section] lines {start+1}-{end+1} of {args.file}", file=sys.stderr)
            print(f"[read-section] {len(content)} lines shown of {total} total", file=sys.stderr)
            print("".join(content), end="")
            sys.exit(0)
        except (ValueError, IndexError) as e:
            print(f"[read-section] ERROR: invalid --lines format: {e}", file=sys.stderr)
            sys.exit(1)

    # ── Markdown section ─────────────────────────────────────────────────────
    if args.after:
        s, e = find_md_section(lines, args.after)
        if s == -1:
            print(f'[read-section] ERROR: heading "{args.after}" not found', file=sys.stderr)
            sys.exit(1)
        content = lines[s : e + 1]
        print(f'[read-section] section "{args.after}" at lines {s+1}-{e+1}', file=sys.stderr)
        print(f"[read-section] {len(content)} lines shown of {total} total", file=sys.stderr)
        print("".join(content), end="")
        sys.exit(0)

    # ── Function / class ─────────────────────────────────────────────────────
    kind = "fn" if args.fn else "class" if args.cls else None
    name = args.fn or args.cls

    if not kind:
        print(
            "[read-section] ERROR: specify one of --fn, --class, --after, --lines",
            file=sys.stderr,
        )
        sys.exit(1)

    idx = find_definition(lines, name, kind)
    if idx == -1:
        print(
            f'[read-section] ERROR: {kind} "{name}" not found in {args.file}',
            file=sys.stderr,
        )
        sys.exit(1)

    ext = file_ext(args.file)

    if ext in PYTHON_EXTS:
        s, e, content = extract_indent_block(lines, idx)
    else:
        # Use brace-based extraction if the surrounding context has braces
        context = "".join(lines[idx : min(idx + 6, total)])
        if "{" in context:
            s, e, content = extract_brace_block(lines, idx)
        else:
            s, e, content = extract_indent_block(lines, idx)

    print(f'[read-section] {kind} "{name}" at lines {s+1}-{e+1} of {args.file}', file=sys.stderr)
    print(f"[read-section] {len(content)} lines shown of {total} total", file=sys.stderr)
    print("".join(content), end="")
    sys.exit(0)


if __name__ == "__main__":
    main()
