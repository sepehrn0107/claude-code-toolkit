# /index-repo

Build a structural index of the current repo. Writes JSON files to `.claude/index/` describing
every file and symbol, their import/call/inheritance relations, and domain clusters.
An optional semantic layer adds TF-IDF or Ollama embeddings for similarity queries.

Supports incremental re-runs — only changed files are re-processed.

## When to Use

Run this:
- After `/new-project` once initial code exists
- After a major refactor or architectural change
- When Claude is struggling to navigate a large codebase
- On demand: `/index-repo`

## Steps

### 1. Pre-flight Check (parallel)

Run both at the same time — no dependencies between them:

- Read `.claude/memory/stack.md` to confirm the project language(s)
- Check whether `.claude/index/manifest.json` exists:
  - If yes → **incremental run** (pass `--incremental` in Step 2)
  - If no  → **full run**

Also confirm Python 3 is available:
```bash
python3 --version
```
If Python 3 is not available, stop and tell the user: "Python 3 is required to run the indexer."

### 2. Run Layer 1 — Static Analysis

Run the indexer script:

```bash
python3 {{TOOLBOX_PATH}}/tools/indexer/indexer.py \
  --root . \
  --output .claude/index
```

For incremental runs, add `--incremental`:
```bash
python3 {{TOOLBOX_PATH}}/tools/indexer/indexer.py \
  --root . \
  --output .claude/index \
  --incremental
```

Wait for the script to finish and confirm it printed "Index complete." before proceeding.

### 3. Run Layer 2 — Semantic Enrichment

Read `.claude/index/config.json`.

**If `config.json` does not exist** (first run), ask the user:

> Enable semantic layer for similarity queries?
> 1. none — skip (structural index only)
> 2. tfidf — algorithmic similarity, no external service (requires scikit-learn)
> 3. ollama — local LLM embeddings via Ollama (no pip required, needs Ollama running)

Write their choice to `.claude/index/config.json`:

For `none`:
```json
{ "semantic": "none" }
```

For `tfidf`:
```json
{ "semantic": "tfidf", "top_n": 5 }
```

For `ollama`, also ask for model (default: `nomic-embed-text`) and URL (default: `http://localhost:11434`):
```json
{ "semantic": "ollama", "ollama_model": "nomic-embed-text", "ollama_url": "http://localhost:11434" }
```

**If `config.json` already exists**, use the stored mode without prompting.

**Run the semantic script** (unless mode is `none`):

For `tfidf` — install scikit-learn if needed, then run:
```bash
pip install scikit-learn -q
python3 {{TOOLBOX_PATH}}/tools/indexer/semantic.py --index .claude/index
```

For `ollama`:
```bash
python3 {{TOOLBOX_PATH}}/tools/indexer/semantic.py --index .claude/index
```

### 4. Write Index README

Read these files:
- `.claude/index/files.json`
- `.claude/index/graph-clusters.json`
- `.claude/index/manifest.json`

Write `.claude/index/README.md` with this structure:

```markdown
# Repo Index

Last indexed: YYYY-MM-DD
Files: N total (N source, N test, N config, N docs)
Clusters: cluster1, cluster2, ...
Semantic: none | tfidf | ollama (model-name)

## Entry Points
(List files that are imported by many others but import few themselves, or named index/main/app)

## Clusters
For each cluster, write one sentence describing what it contains based on the file paths and tags.

## How to Query This Index
- "What calls X?" → read graph-calls.json
- "What imports Y?" → read graph-imports.json
- "Files related to Z" → read graph-clusters.json, then filter files.json
- "Similar files to W" → read vectors.json (if semantic layer enabled)
- Re-index after major changes: /index-repo
```

### 5. Update Architecture Memory

Read `.claude/memory/architecture.md`.

Find or create a `## Code Index` section and replace it with:

```markdown
## Code Index

Last indexed: YYYY-MM-DD
Index location: `.claude/index/`
Key clusters: (comma-separated cluster names)
Entry points: (list main entry files)
Semantic layer: none | tfidf | ollama

Run `/index-repo` to refresh after major changes.
```

### 6. Confirm

Output a summary:

```
Index complete.
  Mode:          full | incremental (N files updated, M deleted)
  Files indexed: N (N source, N test, N config, N docs)
  Symbols:       N
  Clusters:      name1, name2, ...
  Semantic:      none | tfidf | ollama (model-name)

Written to: .claude/index/
Memory updated: .claude/memory/architecture.md
```
