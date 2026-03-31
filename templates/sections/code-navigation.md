## Code Navigation

When you need to find files, understand code structure, or answer questions about the codebase:

1. If `.claude/index/` exists in the current project, **use it before Grep or Glob**:
   - Read `{{TOOLBOX_PATH}}/skills/query-index.md`, then launch a **sub-agent** with the specific question
   - The sub-agent reads only the relevant index files and returns precise, synthesized results
   - This is faster than grep and keeps the main context clean
2. Fall back to Grep/Glob only if:
   - `.claude/index/` does not exist — remind the user they can run `/index-repo` to build it
   - The question is about specific string content within a file (not structure or relations)
3. Never re-read files that the index already summarizes — use the index answer and read source only when editing
