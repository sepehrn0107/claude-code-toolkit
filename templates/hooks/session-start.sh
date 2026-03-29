#!/usr/bin/env bash
# Toolbox SessionStart hook
# Outputs a project brief when opening a toolbox-enabled project.
# Installed to ~/.claude/hooks/session-start.sh by the toolbox setup skill.

# Workspace mode: detect if we're in the workspace root (has memory/ but no .claude/memory/)
if [ -f "memory/MEMORY.md" ] && [ ! -f ".claude/memory/MEMORY.md" ]; then
  # Scan for user-facing git repos (exclude toolbox — it's infrastructure)
  PROJECTS=$(for d in */; do
    [ -d "${d}.git" ] && [ "${d%/}" != "toolbox" ] && printf "%s," "${d%/}"
  done | sed 's/,$//')

  ACTIVE=$(grep -m1 "^active:" memory/active-project.md 2>/dev/null \
           | awk '{print $2}' | grep -v "^(none)$" || echo "")

  echo "---"
  if [ -n "$ACTIVE" ]; then
    # Machine-readable tag + human hint on one line
    echo "WORKSPACE_MODE:ACTIVE=${ACTIVE} | Projects: ${PROJECTS}"
    echo "Active project: ${ACTIVE} — reply 'switch project' to change."
  else
    # Machine-readable tag first, then a human-readable selection list
    echo "WORKSPACE_MODE:CHOOSE | Projects: ${PROJECTS}"
    echo ""
    echo "Which project are you working on? Reply with the name to load its context:"
    N=1
    IFS=',' read -ra PROJ_ARRAY <<< "$PROJECTS"
    for p in "${PROJ_ARRAY[@]}"; do
      echo "  ${N}. ${p}"
      N=$((N+1))
    done
  fi
  echo "---"
  exit 0
fi

# Only activate if this is a toolbox-enabled project
if [ ! -f ".claude/memory/MEMORY.md" ]; then
  exit 0
fi

# Skip the toolbox repo itself
if [ -f "CLAUDE.md" ] && grep -q "set up the toolbox" CLAUDE.md 2>/dev/null; then
  exit 0
fi

# Read stack and current phase from memory files
STACK=$(grep -m1 "^primary:" .claude/memory/stack.md 2>/dev/null | sed 's/primary:[[:space:]]*//' || echo "")
if [ -z "$STACK" ]; then
  STACK=$(grep -m1 "primary" .claude/memory/stack.md 2>/dev/null | awk '{print $NF}' || echo "unknown")
fi

PHASE=$(grep -m1 "^## Current Phase" .claude/memory/progress.md 2>/dev/null | sed 's/## Current Phase:[[:space:]]*//' || echo "")
if [ -z "$PHASE" ]; then
  PHASE=$(grep -A1 "Current Phase" .claude/memory/progress.md 2>/dev/null | tail -1 | sed 's/^[[:space:]]*//' || echo "see progress.md")
fi

NEXT=$(grep -A2 "^## Next" .claude/memory/progress.md 2>/dev/null | grep -v "^##" | grep -v "^$" | head -1 | sed 's/^[-*[:space:]]*//' || echo "see progress.md")

# Check if the code index exists and whether it may be stale
INDEX_NOTE=""
if [ -d ".claude/index" ] && [ -f ".claude/index/manifest.json" ]; then
  LAST_COMMIT_TIME=$(git log -1 --format="%ct" 2>/dev/null || echo "0")
  INDEX_MTIME=$(stat -c "%Y" .claude/index/manifest.json 2>/dev/null || echo "0")
  if [ "$LAST_COMMIT_TIME" -gt "$INDEX_MTIME" ]; then
    INDEX_NOTE=" | Index stale — run /index-repo to refresh"
  else
    INDEX_NOTE=" | Index available"
  fi
else
  INDEX_NOTE=" | No index — run /index-repo to build"
fi

echo "---"
echo "Project context loaded | Stack: ${STACK:-unknown} | Phase: ${PHASE} | Next: ${NEXT}${INDEX_NOTE}"
echo "Memory files are ready. Standards not yet loaded — will auto-load before first code edit."
echo "---"
