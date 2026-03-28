#!/usr/bin/env python3
"""
Semantic enrichment — Layer 2: TF-IDF or Ollama embeddings.

Reads .claude/index/config.json to determine mode.
Updates vectors.json incrementally — only re-embeds files whose content has changed.

Usage:
    python3 semantic.py --index .claude/index

Modes (set in config.json):
    tfidf   — algorithmic cosine similarity, requires scikit-learn
    ollama  — local LLM via Ollama HTTP API, no pip dependencies
"""

import argparse
import hashlib
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def load_json(path: str, default=None):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default if default is not None else {}


def save_json(path: str, data) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def doc_for_file(record: dict) -> str:
    """Build the text used for embedding. Stable: same input → same embedding."""
    parts = [record.get("path", "")]
    parts.extend(record.get("exports", []))
    parts.extend(record.get("tags", []))
    summary = record.get("summary", "")
    if summary:
        parts.append(summary)
    return " ".join(p for p in parts if p)


def semantic_hash(doc: str) -> str:
    """Short hash of the embedding document — used to detect staleness."""
    return "sem:" + hashlib.sha256(doc.encode()).hexdigest()[:12]


# ─────────────────────────────────────────────────────────────────────────────
# TF-IDF mode
# ─────────────────────────────────────────────────────────────────────────────

def run_tfidf(index_dir: str, config: dict) -> None:
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
    except ImportError:
        print("ERROR: scikit-learn is required for TF-IDF mode.")
        print("Install with: pip install scikit-learn")
        sys.exit(1)

    files = load_json(os.path.join(index_dir, "files.json"), [])
    if not files:
        print("No files in index. Run indexer.py first.")
        return

    top_n: int = config.get("top_n", 5)
    paths: list[str] = []
    documents: list[str] = []

    for record in files:
        paths.append(record["path"])
        documents.append(doc_for_file(record))

    vectorizer = TfidfVectorizer(
        analyzer="word",
        token_pattern=r"[a-zA-Z_][a-zA-Z0-9_]+",
        min_df=1,
        max_features=5000,
        sublinear_tf=True,
    )
    matrix = vectorizer.fit_transform(documents)
    sim_matrix = cosine_similarity(matrix)

    entries: dict[str, dict] = {}
    for i, path in enumerate(paths):
        doc = documents[i]
        scores = sim_matrix[i]
        ranked = scores.argsort()[::-1]

        similar: list[dict] = []
        for j in ranked:
            if j == i:
                continue
            score = float(scores[j])
            if score < 0.05:
                break
            similar.append({"path": paths[j], "score": round(score, 3)})
            if len(similar) >= top_n:
                break

        entries[path] = {
            "semantic_hash": semantic_hash(doc),
            "similar": similar,
            "vector": None,
        }

    save_json(os.path.join(index_dir, "vectors.json"), {
        "mode": "tfidf",
        "model": None,
        "updated_at": _now(),
        "entries": entries,
    })
    print(f"TF-IDF complete. {len(entries)} files indexed.")


# ─────────────────────────────────────────────────────────────────────────────
# Ollama mode
# ─────────────────────────────────────────────────────────────────────────────

def run_ollama(index_dir: str, config: dict) -> None:
    base_url = config.get("ollama_url", "http://localhost:11434").rstrip("/")
    model = config.get("ollama_model", "nomic-embed-text")
    embed_url = f"{base_url}/api/embeddings"

    # Verify Ollama is reachable
    try:
        with urllib.request.urlopen(f"{base_url}/api/tags", timeout=5) as resp:
            pass
    except urllib.error.URLError as e:
        print(f"ERROR: Cannot reach Ollama at {base_url}: {e}")
        print("Make sure Ollama is running: ollama serve")
        sys.exit(1)

    files = load_json(os.path.join(index_dir, "files.json"), [])
    existing_vectors = load_json(os.path.join(index_dir, "vectors.json"), {})
    existing_entries: dict[str, dict] = existing_vectors.get("entries", {})

    entries = dict(existing_entries)
    updated = 0
    skipped = 0
    errors = 0

    for record in files:
        path = record["path"]
        doc = doc_for_file(record)
        shash = semantic_hash(doc)

        # Skip if embedding is still valid
        if path in entries and entries[path].get("semantic_hash") == shash:
            skipped += 1
            continue

        # Request embedding from Ollama
        payload = json.dumps({"model": model, "prompt": doc}).encode()
        req = urllib.request.Request(
            embed_url,
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.load(resp)
            vector = result.get("embedding", [])
            entries[path] = {
                "semantic_hash": shash,
                "similar": [],  # computed lazily at query time
                "vector": vector,
            }
            updated += 1
        except urllib.error.URLError as e:
            print(f"  WARNING: Embedding failed for {path}: {e}")
            errors += 1

    save_json(os.path.join(index_dir, "vectors.json"), {
        "mode": "ollama",
        "model": model,
        "updated_at": _now(),
        "entries": entries,
    })
    print(
        f"Ollama complete. "
        f"{updated} updated, {skipped} skipped (unchanged)"
        + (f", {errors} errors" if errors else "")
        + f". Total: {len(entries)} files."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Semantic enrichment layer — Layer 2")
    parser.add_argument("--index", required=True, help="Path to .claude/index/ directory")
    args = parser.parse_args()

    index_dir = args.index
    config = load_json(os.path.join(index_dir, "config.json"), {})
    mode = config.get("semantic", "none")

    if mode == "none":
        print("Semantic mode is 'none'. Nothing to do.")
        return
    elif mode == "tfidf":
        print("Running TF-IDF semantic enrichment...")
        run_tfidf(index_dir, config)
    elif mode == "ollama":
        print(f"Running Ollama semantic enrichment (model: {config.get('ollama_model', 'nomic-embed-text')})...")
        run_ollama(index_dir, config)
    else:
        print(f"ERROR: Unknown semantic mode '{mode}'. Expected: tfidf, ollama, none")
        sys.exit(1)


if __name__ == "__main__":
    main()
