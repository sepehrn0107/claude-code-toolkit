# /query-index

Answer a structural question about the codebase using the repo index.

This skill is designed to run **as a sub-agent**. It reads only the index files
relevant to the specific question, synthesizes a precise answer, and returns it
— without flooding the main context window with large JSON files.

## When to Use

Always prefer this over Grep or Glob when the question is structural:
- "What files are in the payments area?"
- "What imports `src/api/processor.ts`?"
- "What calls `processPayment`?"
- "What are the entry points of this app?"
- "Which files are related to authentication?"
- "What does `src/payments/processor.ts` export?"
- "Show me the call chain from `handleRequest` down"
- "What external services does this codebase integrate with?"

Fall back to Grep only if the index doesn't exist, or the question is about
specific string content within a file (not about structure or relations).

## How to Invoke from Another Skill

Read this skill file, then launch a sub-agent:

```
Launch a sub-agent (haiku model — index reads are simple):
- Task: read {{TOOLBOX_PATH}}/skills/query-index.md and follow it
- Question: <specific structural question>
- Index: .claude/index/
```

The sub-agent returns a structured answer. Use that answer in the parent task
without needing to read any index files yourself.

## Steps

### 1. Check Index Exists

Check whether `.claude/index/README.md` exists.
If it does not, return immediately:
```
No index found. Run /index-repo first, then retry.
```

### 2. Read the Index Map

Always read `.claude/index/README.md` first — it is small and gives orientation:
clusters, entry points, last indexed date, and semantic mode.

### 3. Read Only the Relevant Index Files

Select files based on the question type. Never read all index files — only what you need:

| Question type | File(s) to read |
|---|---|
| Clusters / areas ("what's in X?", "what areas exist?") | `graph-clusters.json` |
| Import deps ("what imports X?", "what does X depend on?") | `graph-imports.json` |
| Call chains ("what calls X?", "what does X call?") | `graph-calls.json` |
| Symbol details ("what does function X do?", "signature of X?") | `symbols.json` — filter to matching entries only |
| File details ("what does file X export?", "what language?") | `files.json` — filter to matching path |
| Similarity ("files related to X") | `vectors.json` (only if semantic mode is enabled, check README) |
| External services ("what external APIs?") | `files.json` — filter imports where `external: true` |
| Entry points / overview | Already in `README.md` — no additional file needed |

For `files.json` and `symbols.json` (which can be large): do not read the entire
file if the question is about a specific path or name. Read the file and filter
mentally — return only the matching entries.

### 4. Return a Structured Answer

Format your response exactly as:

```
Query: <the question>

Answer: <direct answer in 1–3 sentences>

Files:
- path/to/file.ts — why it's relevant
- path/to/other.ts — why it's relevant

Symbols (if applicable):
- functionName (path/to/file.ts:42) — one-line description

Next (if the answer is incomplete):
- Read X to find Y
```

Do not paste raw JSON. Synthesize only the relevant parts.
Keep the answer concise — the parent agent will act on it directly.
