#!/usr/bin/env python3
"""
Repo indexer — Layer 1: static analysis.

Crawls a git repo, extracts file and symbol metadata, builds import/call/inheritance
graphs and domain clusters, and writes JSON files to .claude/index/.

No third-party dependencies — Python stdlib only.

Usage:
    python3 indexer.py --root . --output .claude/index
    python3 indexer.py --root . --output .claude/index --incremental
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# File classification
# ─────────────────────────────────────────────────────────────────────────────

SOURCE_EXTS = {
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
    ".py", ".go", ".rs", ".java", ".kt", ".rb", ".cs", ".cpp", ".c", ".h",
}
TEST_PATTERN = re.compile(
    r"(\.test\.|\.spec\.|_test\.|__tests__|/tests?/|/specs?/)", re.I
)
CONFIG_EXTS = {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf"}
CONFIG_NAMES = {"Dockerfile", "Makefile", "makefile", ".env.example",
                ".eslintrc", ".prettierrc", ".babelrc"}
STYLE_EXTS = {".css", ".scss", ".sass", ".less", ".styl"}
DOC_EXTS = {".md", ".mdx", ".txt", ".rst", ".adoc"}

EXCLUDE_DIRS = {
    ".git", "node_modules", "vendor", ".venv", "venv", "__pycache__",
    "dist", "build", ".next", ".nuxt", "coverage", ".nyc_output",
    "__snapshots__", "testdata", "fixtures", ".pytest_cache", ".mypy_cache",
    "target", "out", ".gradle", ".idea", ".vscode",
}
EXCLUDE_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".pdf", ".zip", ".tar", ".gz", ".bz2", ".xz",
    ".exe", ".dll", ".so", ".dylib", ".a",
    ".map",
}
EXCLUDE_NAMES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "go.sum", "poetry.lock", "Pipfile.lock", "Cargo.lock",
}


def classify_file(path: str) -> str | None:
    p = Path(path)
    name = p.name
    ext = p.suffix.lower()

    if name in EXCLUDE_NAMES:
        return None
    if ext in EXCLUDE_EXTS:
        return None
    for part in p.parts:
        if part in EXCLUDE_DIRS:
            return None

    if ext in SOURCE_EXTS:
        return "test" if TEST_PATTERN.search(path) else "source"
    if ext in STYLE_EXTS:
        return "style"
    if ext in DOC_EXTS:
        return "docs"
    if ext in CONFIG_EXTS or name in CONFIG_NAMES:
        return "config"
    return None


def detect_language(path: str) -> str:
    return {
        ".ts": "typescript", ".tsx": "typescript",
        ".js": "javascript", ".jsx": "javascript",
        ".mjs": "javascript", ".cjs": "javascript",
        ".py": "python",
        ".go": "go",
        ".rs": "rust",
        ".java": "java",
        ".kt": "kotlin",
        ".rb": "ruby",
        ".cs": "csharp",
        ".cpp": "cpp", ".c": "c", ".h": "c",
    }.get(Path(path).suffix.lower(), "unknown")


# ─────────────────────────────────────────────────────────────────────────────
# Body and call helpers
# ─────────────────────────────────────────────────────────────────────────────

_CALL_SKIP = {
    "if", "for", "while", "switch", "catch", "function", "return",
    "class", "new", "typeof", "instanceof", "import", "export",
    "print", "len", "range", "str", "int", "float", "list", "dict",
    "tuple", "set", "super", "self", "this", "console", "Math",
    "Object", "Array", "Promise", "Error", "require",
}


def _extract_body(lines: list[str], start: int, max_lines: int = 60) -> str:
    return "\n".join(lines[start : start + max_lines])


def _extract_python_body(lines: list[str], start: int) -> str:
    if start + 1 >= len(lines):
        return ""
    base_indent = len(lines[start]) - len(lines[start].lstrip())
    body = []
    for line in lines[start + 1 : start + 80]:
        stripped = line.lstrip()
        if not stripped:
            body.append(line)
            continue
        if len(line) - len(stripped) <= base_indent and stripped:
            break
        body.append(line)
    return "\n".join(body)


def _extract_calls(body: str) -> list[str]:
    seen: set[str] = set()
    calls: list[str] = []
    for m in re.finditer(r"\b([a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*)\s*\(", body):
        name = m.group(1)
        if name.lower() in _CALL_SKIP or name in seen:
            continue
        seen.add(name)
        calls.append(name)
        if len(calls) >= 20:
            break
    return calls


# ─────────────────────────────────────────────────────────────────────────────
# Language-specific extraction
# ─────────────────────────────────────────────────────────────────────────────

def _is_external(from_path: str) -> bool:
    return not (
        from_path.startswith("./")
        or from_path.startswith("../")
        or from_path.startswith("@/")
        or from_path.startswith("~/")
    )


def extract_ts_js(content: str, path: str):
    exports, imports, symbols = [], [], []
    lines = content.split("\n")

    # Named exports
    for m in re.finditer(
        r"^export\s+(?:default\s+)?(?:async\s+)?"
        r"(?:function\s+(\w+)|class\s+(\w+)|(?:const|let|var)\s+(\w+)"
        r"|type\s+(\w+)|interface\s+(\w+)|enum\s+(\w+))",
        content, re.M,
    ):
        name = next(g for g in m.groups() if g)
        if name not in exports:
            exports.append(name)

    # module.exports = { ... }
    for m in re.finditer(r"^module\.exports\s*=\s*\{([^}]+)\}", content, re.M):
        for name in re.findall(r"\b([A-Za-z_]\w*)\b", m.group(1)):
            if name not in exports:
                exports.append(name)

    # Imports
    for m in re.finditer(
        r"^import\s+(?:\*\s+as\s+(\w+)|\{([^}]+)\}|(\w+))?\s*"
        r"(?:,\s*\{([^}]+)\})?\s*from\s+['\"]([^'\"]+)['\"]",
        content, re.M,
    ):
        from_path = m.group(5)
        syms: list[str] = []
        if m.group(1):
            syms = [m.group(1)]
        if m.group(2):
            syms += [s.strip().split(" as ")[0].strip()
                     for s in m.group(2).split(",") if s.strip()]
        if m.group(3):
            syms.append(m.group(3))
        if m.group(4):
            syms += [s.strip().split(" as ")[0].strip()
                     for s in m.group(4).split(",") if s.strip()]
        imports.append({"from": from_path, "symbols": syms, "external": _is_external(from_path)})

    # Side-effect imports
    for m in re.finditer(r"^import\s+['\"]([^'\"]+)['\"]", content, re.M):
        from_path = m.group(1)
        if not any(i["from"] == from_path for i in imports):
            imports.append({"from": from_path, "symbols": [], "external": _is_external(from_path)})

    # require()
    for m in re.finditer(r"require\s*\(['\"]([^'\"]+)['\"]\)", content):
        from_path = m.group(1)
        if not any(i["from"] == from_path for i in imports):
            imports.append({"from": from_path, "symbols": [], "external": _is_external(from_path)})

    # Symbols
    for i, line in enumerate(lines, 1):
        # function declaration
        m = re.match(r"^(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)", line)
        if m:
            name, params = m.group(1), m.group(2)
            sig = line.strip().rstrip("{").strip()
            body = _extract_body(lines, i - 1)
            symbols.append({
                "name": name, "kind": "function", "signature": sig,
                "line": i, "calls": _extract_calls(body), "called_by": [],
            })
            continue

        # class declaration
        m = re.match(r"^(?:export\s+)?(?:abstract\s+)?class\s+(\w+)", line)
        if m:
            symbols.append({
                "name": m.group(1), "kind": "class",
                "signature": line.strip().rstrip("{").strip(),
                "line": i, "calls": [], "called_by": [],
            })
            continue

        # exported arrow function / const component
        m = re.match(r"^(?:export\s+)?(?:const|let)\s+(\w+)\s*(?::[^=]+)?=\s*(?:async\s+)?\(", line)
        if m:
            name = m.group(1)
            if name[0].isupper() or name in exports:
                body = _extract_body(lines, i - 1)
                symbols.append({
                    "name": name, "kind": "function",
                    "signature": line.strip(),
                    "line": i, "calls": _extract_calls(body), "called_by": [],
                })

    return exports, imports, symbols


def extract_python(content: str, path: str):
    exports, imports, symbols = [], [], []
    lines = content.split("\n")

    # __all__ takes precedence for exports
    m = re.search(r"^__all__\s*=\s*\[([^\]]+)\]", content, re.M)
    forced_exports = (
        [s.strip().strip("'\"") for s in m.group(1).split(",") if s.strip()]
        if m else []
    )

    # from X import Y
    for m in re.finditer(r"^from\s+(\S+)\s+import\s+(.+)$", content, re.M):
        from_path = m.group(1)
        external = not from_path.startswith(".")
        syms = [
            s.strip().split(" as ")[0].strip()
            for s in m.group(2).split(",")
            if s.strip() and s.strip() != "*"
        ]
        imports.append({"from": from_path, "symbols": syms, "external": external})

    # import X
    for m in re.finditer(r"^import\s+(\S+)", content, re.M):
        from_path = m.group(1).rstrip(";")
        if not any(i["from"] == from_path for i in imports):
            imports.append({"from": from_path, "symbols": [], "external": True})

    # Top-level functions and classes
    for i, line in enumerate(lines, 1):
        m = re.match(r"^(def|async def|class)\s+(\w+)", line)
        if not m:
            continue
        raw_kind = m.group(1)
        name = m.group(2)
        kind = "class" if raw_kind == "class" else "function"

        if not name.startswith("_"):
            if not forced_exports:
                exports.append(name)
            sig = line.strip().rstrip(":")
            body = _extract_python_body(lines, i - 1)
            symbols.append({
                "name": name, "kind": kind, "signature": sig,
                "line": i,
                "calls": _extract_calls(body) if kind == "function" else [],
                "called_by": [],
            })

    if forced_exports:
        exports = forced_exports
    if not exports:
        exports = [s["name"] for s in symbols]

    return exports, imports, symbols


def extract_go(content: str, path: str):
    exports, imports, symbols = [], [], []
    lines = content.split("\n")

    # Single import
    for m in re.finditer(r'^import\s+"([^"]+)"', content, re.M):
        from_path = m.group(1)
        external = "." not in from_path.split("/")[0]
        imports.append({"from": from_path, "symbols": [from_path.split("/")[-1]], "external": external})

    # Import block
    in_import = False
    for line in lines:
        if re.match(r"^import\s*\(", line):
            in_import = True
            continue
        if in_import:
            if line.strip() == ")":
                in_import = False
                continue
            m = re.search(r'"([^"]+)"', line)
            if m:
                from_path = m.group(1)
                if not any(i["from"] == from_path for i in imports):
                    external = "." not in from_path.split("/")[0]
                    imports.append({
                        "from": from_path,
                        "symbols": [from_path.split("/")[-1]],
                        "external": external,
                    })

    # Exported functions and types
    for i, line in enumerate(lines, 1):
        m = re.match(r"^func\s+([A-Z]\w*)\s*\(", line)
        if m:
            name = m.group(1)
            exports.append(name)
            body = _extract_body(lines, i - 1)
            symbols.append({
                "name": name, "kind": "function",
                "signature": line.strip().rstrip("{").strip(),
                "line": i, "calls": _extract_calls(body), "called_by": [],
            })
            continue

        # Method on exported receiver
        m = re.match(r"^func\s+\(\w+\s+\*?([A-Z]\w*)\)\s+([A-Z]\w*)\s*\(", line)
        if m:
            name = f"{m.group(1)}.{m.group(2)}"
            exports.append(name)
            body = _extract_body(lines, i - 1)
            symbols.append({
                "name": name, "kind": "method",
                "signature": line.strip().rstrip("{").strip(),
                "line": i, "calls": _extract_calls(body), "called_by": [],
            })
            continue

        # Exported type
        m = re.match(r"^type\s+([A-Z]\w*)\s+(struct|interface)", line)
        if m:
            name = m.group(1)
            kind = "class" if m.group(2) == "struct" else "interface"
            exports.append(name)
            symbols.append({
                "name": name, "kind": kind,
                "signature": line.strip(),
                "line": i, "calls": [], "called_by": [],
            })

    return exports, imports, symbols


def extract_rust(content: str, path: str):
    exports, imports, symbols = [], [], []
    lines = content.split("\n")

    for m in re.finditer(r"^use\s+([\w:]+(?:::\{[^}]+\})?);", content, re.M):
        use_path = m.group(1)
        external = not (
            use_path.startswith("crate::")
            or use_path.startswith("super::")
            or use_path.startswith("self::")
        )
        imports.append({"from": use_path, "symbols": [], "external": external})

    for i, line in enumerate(lines, 1):
        m = re.match(r"^pub\s+(?:async\s+)?fn\s+(\w+)\s*[<(]", line)
        if m:
            name = m.group(1)
            exports.append(name)
            body = _extract_body(lines, i - 1)
            symbols.append({
                "name": name, "kind": "function",
                "signature": line.strip().rstrip("{").strip(),
                "line": i, "calls": _extract_calls(body), "called_by": [],
            })
            continue

        m = re.match(r"^pub\s+(struct|enum|trait)\s+(\w+)", line)
        if m:
            kind_map = {"struct": "class", "enum": "enum", "trait": "interface"}
            name = m.group(2)
            exports.append(name)
            symbols.append({
                "name": name, "kind": kind_map[m.group(1)],
                "signature": line.strip(),
                "line": i, "calls": [], "called_by": [],
            })

    return exports, imports, symbols


EXTRACTORS = {
    "typescript": extract_ts_js,
    "javascript": extract_ts_js,
    "python": extract_python,
    "go": extract_go,
    "rust": extract_rust,
}


# ─────────────────────────────────────────────────────────────────────────────
# Tagging
# ─────────────────────────────────────────────────────────────────────────────

_DOMAIN_KWS = [
    "auth", "user", "payment", "order", "product", "cart", "checkout",
    "api", "db", "database", "cache", "queue", "job", "worker", "email",
    "notification", "config", "util", "helper", "service", "controller",
    "model", "schema", "router", "middleware", "handler", "client", "server",
    "test", "mock", "store", "hook", "component", "page", "layout",
    "theme", "type", "index", "main", "app",
]

_SKIP_SEGMENTS = {"src", "lib", "app", "pkg", ".", "..", "index", "main", "__init__"}


def extract_tags(path: str, exports: list[str]) -> list[str]:
    parts = list(Path(path).parts)
    text = " ".join(parts + exports).lower()
    tags: list[str] = []
    for kw in _DOMAIN_KWS:
        if kw in text:
            tags.append(kw)
    for part in parts[:-1]:  # skip filename
        slug = part.lower()
        if slug and slug not in _SKIP_SEGMENTS and slug not in tags:
            tags.append(slug)
    return tags[:6]


# ─────────────────────────────────────────────────────────────────────────────
# Hashing
# ─────────────────────────────────────────────────────────────────────────────

def file_hash(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return "sha256:" + h.hexdigest()[:16]


# ─────────────────────────────────────────────────────────────────────────────
# File listing
# ─────────────────────────────────────────────────────────────────────────────

def git_tracked_files(root: str) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"], cwd=root, capture_output=True, text=True
    )
    if result.returncode == 0:
        return [f.strip() for f in result.stdout.splitlines() if f.strip()]

    # Fallback: walk directory
    files: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d for d in dirnames
            if d not in EXCLUDE_DIRS and not d.startswith(".")
        ]
        for name in filenames:
            rel = os.path.relpath(os.path.join(dirpath, name), root)
            files.append(rel)
    return files


# ─────────────────────────────────────────────────────────────────────────────
# Graph construction
# ─────────────────────────────────────────────────────────────────────────────

def _resolve_import(from_path: str, current_file: str, known: set[str]) -> str | None:
    if not (from_path.startswith("./") or from_path.startswith("../")):
        return None
    base = os.path.normpath(str(Path(current_file).parent / from_path))
    for ext in ("", ".ts", ".tsx", ".js", ".jsx", ".py", "/index.ts", "/index.js", "/index.tsx"):
        candidate = base + ext
        if candidate in known:
            return candidate
    return None


def build_import_graph(file_records: list[dict]) -> dict:
    known = {r["path"] for r in file_records}
    graph = {r["path"]: {"imports": [], "imported_by": []} for r in file_records}

    for record in file_records:
        path = record["path"]
        for imp in record.get("imports", []):
            if imp.get("external"):
                continue
            resolved = _resolve_import(imp["from"], path, known)
            if resolved and resolved in graph:
                if resolved not in graph[path]["imports"]:
                    graph[path]["imports"].append(resolved)
                if path not in graph[resolved]["imported_by"]:
                    graph[resolved]["imported_by"].append(path)

    return graph


def build_call_graph(symbol_records: list[dict]) -> dict:
    # Map symbol name → file (first occurrence wins)
    sym_file: dict[str, str] = {}
    for sym in symbol_records:
        if sym["name"] not in sym_file:
            sym_file[sym["name"]] = sym["file"]

    graph: dict[str, dict] = {}
    for sym in symbol_records:
        graph[sym["name"]] = {
            "defined_in": sym["file"],
            "calls": sym.get("calls", []),
            "called_by": [],
        }

    # Invert: populate called_by
    for sym in symbol_records:
        caller_ref = f"{sym['file']}:{sym['name']}"
        for callee in sym.get("calls", []):
            if callee in graph:
                if caller_ref not in graph[callee]["called_by"]:
                    graph[callee]["called_by"].append(caller_ref)

    return graph


def build_inheritance_graph(all_content: dict[str, str]) -> dict:
    graph: dict[str, dict] = {}

    for path, content in all_content.items():
        lang = detect_language(path)
        if lang in ("typescript", "javascript"):
            for m in re.finditer(
                r"class\s+(\w+)\s+extends\s+(\w+)(?:\s+implements\s+([^{]+))?",
                content,
            ):
                name, base = m.group(1), m.group(2)
                impls = [i.strip() for i in m.group(3).split(",")] if m.group(3) else []
                graph[name] = {"defined_in": path, "extends": base, "implements": impls}

        elif lang == "python":
            for m in re.finditer(r"^class\s+(\w+)\s*\(([^)]+)\)", content, re.M):
                name = m.group(1)
                bases = [
                    b.strip() for b in m.group(2).split(",")
                    if b.strip() and b.strip() != "object"
                ]
                if bases:
                    graph[name] = {
                        "defined_in": path,
                        "extends": bases[0],
                        "implements": bases[1:],
                    }

    return graph


def build_clusters(file_records: list[dict]) -> dict:
    clusters: dict[str, dict] = {}

    for record in file_records:
        path = record["path"]
        parts = Path(path).parts

        cluster_name: str | None = None
        for part in parts[:-1]:
            slug = part.lower()
            if slug not in _SKIP_SEGMENTS:
                cluster_name = slug
                break

        if not cluster_name:
            tags = record.get("tags", [])
            cluster_name = tags[0] if tags else "misc"

        if cluster_name not in clusters:
            clusters[cluster_name] = {"files": [], "description": ""}
        clusters[cluster_name]["files"].append(path)

    for name, cluster in clusters.items():
        count = len(cluster["files"])
        cluster["description"] = f"{name} — {count} file{'s' if count != 1 else ''}"

    return clusters


# ─────────────────────────────────────────────────────────────────────────────
# I/O helpers
# ─────────────────────────────────────────────────────────────────────────────

def load_json(path: str, default=None):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default if default is not None else {}


def save_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# ─────────────────────────────────────────────────────────────────────────────
# Main indexing logic
# ─────────────────────────────────────────────────────────────────────────────

def run_index(root: str, index_dir: str, incremental: bool) -> dict:
    os.makedirs(index_dir, exist_ok=True)

    manifest = load_json(os.path.join(index_dir, "manifest.json"))
    existing_files = manifest.get("files", {})

    all_git_files = git_tracked_files(root)

    # Classify
    classified: dict[str, str] = {}
    for f in all_git_files:
        cls = classify_file(f)
        if cls:
            classified[f] = cls

    # Determine scope
    is_incremental = incremental and bool(existing_files)
    if is_incremental:
        deleted = [f for f in existing_files if f not in classified]
        files_to_process = []
        for f, cls in classified.items():
            full = os.path.join(root, f)
            if not os.path.exists(full):
                continue
            h = file_hash(full)
            if f not in existing_files or existing_files[f].get("hash") != h:
                files_to_process.append(f)
    else:
        deleted = []
        files_to_process = list(classified.keys())

    print(f"Mode:             {'incremental' if is_incremental else 'full'}")
    print(f"Files to process: {len(files_to_process)}"
          + (f" | Deleted: {len(deleted)}" if deleted else ""))

    # Load existing records
    file_records_map: dict[str, dict] = {
        r["path"]: r
        for r in load_json(os.path.join(index_dir, "files.json"), [])
    }
    sym_records_by_file: dict[str, list] = {}
    for sym in load_json(os.path.join(index_dir, "symbols.json"), []):
        sym_records_by_file.setdefault(sym["file"], []).append(sym)

    # Remove deleted
    for d in deleted:
        file_records_map.pop(d, None)
        sym_records_by_file.pop(d, None)

    # Process files
    all_content: dict[str, str] = {}
    new_manifest_files = dict(existing_files)

    for rel_path in files_to_process:
        full_path = os.path.join(root, rel_path)
        if not os.path.exists(full_path):
            continue

        cls = classified[rel_path]
        lang = detect_language(rel_path)

        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except OSError:
            continue

        exports, imports_list, symbols = [], [], []
        if cls in ("source", "test") and lang in EXTRACTORS:
            all_content[rel_path] = content
            exports, imports_list, symbols = EXTRACTORS[lang](content, rel_path)

        tags = extract_tags(rel_path, exports)
        h = file_hash(full_path)

        file_records_map[rel_path] = {
            "path": rel_path,
            "classification": cls,
            "language": lang,
            "size_lines": content.count("\n") + 1,
            "exports": exports,
            "imports": imports_list,
            "summary": "",
            "tags": tags,
            "clusters": [],
        }
        sym_records_by_file[rel_path] = [
            {**s, "file": rel_path} for s in symbols
        ]
        new_manifest_files[rel_path] = {"hash": h, "indexed": True, "classification": cls}

    # For full run, read unchanged source files for inheritance graph
    if not is_incremental:
        for rel_path, cls in classified.items():
            if rel_path not in all_content and cls in ("source", "test"):
                full_path = os.path.join(root, rel_path)
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        all_content[rel_path] = f.read()
                except OSError:
                    pass

    # Flatten
    all_file_records = list(file_records_map.values())
    all_symbol_records = [s for syms in sym_records_by_file.values() for s in syms]

    # Build graphs
    import_graph = build_import_graph(all_file_records)
    call_graph = build_call_graph(all_symbol_records)
    inheritance_graph = build_inheritance_graph(all_content)
    clusters = build_clusters(all_file_records)

    # Attach clusters to file records
    for cluster_name, cluster_data in clusters.items():
        for path in cluster_data["files"]:
            if path in file_records_map:
                rec = file_records_map[path]
                if cluster_name not in rec["clusters"]:
                    rec["clusters"].append(cluster_name)

    # Stats
    stats = {
        "total_files": len(all_file_records),
        "source_files": sum(1 for r in all_file_records if r["classification"] == "source"),
        "test_files": sum(1 for r in all_file_records if r["classification"] == "test"),
        "config_files": sum(1 for r in all_file_records if r["classification"] == "config"),
        "docs_files": sum(1 for r in all_file_records if r["classification"] == "docs"),
        "symbols": len(all_symbol_records),
        "clusters": len(clusters),
    }

    # Write all outputs
    now = datetime.now(timezone.utc).isoformat()
    save_json(os.path.join(index_dir, "manifest.json"), {
        "version": "1",
        "indexed_at": now,
        "toolbox_skill": "index-repo",
        "stats": stats,
        "files": new_manifest_files,
    })
    save_json(os.path.join(index_dir, "files.json"), all_file_records)
    save_json(os.path.join(index_dir, "symbols.json"), all_symbol_records)
    save_json(os.path.join(index_dir, "graph-imports.json"), import_graph)
    save_json(os.path.join(index_dir, "graph-calls.json"), call_graph)
    if inheritance_graph:
        save_json(os.path.join(index_dir, "graph-inheritance.json"), inheritance_graph)
    save_json(os.path.join(index_dir, "graph-clusters.json"), clusters)

    return stats


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Static repo indexer — Layer 1")
    parser.add_argument("--root", default=".", help="Project root directory")
    parser.add_argument(
        "--output", default=".claude/index",
        help="Output directory for index files (relative to root or absolute)",
    )
    parser.add_argument(
        "--incremental", action="store_true",
        help="Re-index only files that have changed since last run",
    )
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    index_dir = (
        args.output if os.path.isabs(args.output)
        else os.path.join(root, args.output)
    )

    print(f"Indexing: {root}")
    print(f"Output:   {index_dir}")
    print()

    stats = run_index(root, index_dir, args.incremental)

    print()
    print("Index complete.")
    print(f"  Files:   {stats['total_files']}"
          f" ({stats['source_files']} source,"
          f" {stats['test_files']} test,"
          f" {stats['config_files']} config,"
          f" {stats['docs_files']} docs)")
    print(f"  Symbols: {stats['symbols']}")
    print(f"  Clusters:{stats['clusters']}")
    print(f"  Output:  {index_dir}")


if __name__ == "__main__":
    main()
