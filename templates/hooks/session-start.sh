#!/usr/bin/env bash
# Toolbox SessionStart hook
# Outputs a project brief when opening a toolbox-enabled project.
# Installed to ~/.claude/hooks/session-start.sh by the toolbox setup skill.

# Dependency check — warn early if required tools are missing
MISSING_DEPS=""
for dep in jq bash python3; do
  command -v "$dep" >/dev/null 2>&1 || MISSING_DEPS="${MISSING_DEPS} ${dep}"
done
if [ -n "$MISSING_DEPS" ]; then
  echo "---"
  echo "Toolbox WARNING: missing dependencies:${MISSING_DEPS}"
  echo "Some toolbox features may not work. Install the missing tools and restart."
  echo "---"
fi

# Workspace mode: detect if we're in the workspace root (has memory/ but no .claude/memory/)
if [ -f "memory/MEMORY.md" ] && [ ! -f ".claude/memory/MEMORY.md" ]; then
  # Detect the toolbox directory to exclude it from project listings.
  # Priority: TOOLBOX_DIR env var > .toolbox-marker file > legacy "toolbox" name
  _TOOLBOX_NAME=""
  if [ -n "${TOOLBOX_DIR:-}" ]; then
    _TOOLBOX_NAME="$TOOLBOX_DIR"
  else
    for d in */; do
      if [ -f "${d}.toolbox-marker" ]; then
        _TOOLBOX_NAME="${d%/}"
        break
      fi
    done
  fi
  # Legacy fallback: if no marker found, exclude "toolbox" by name
  [ -z "$_TOOLBOX_NAME" ] && _TOOLBOX_NAME="toolbox"

  # Scan for user-facing git repos (exclude toolbox — it's infrastructure)
  PROJECTS=$(for d in */; do
    [ -d "${d}.git" ] && [ "${d%/}" != "$_TOOLBOX_NAME" ] && printf "%s," "${d%/}"
  done | sed 's/,$//')

  ACTIVE=$(grep -m1 "^active:" memory/active-project.md 2>/dev/null \
           | awk '{print $2}' | grep -v "^(none)$" || echo "")

  # Write or read session-scoped active project file (isolates parallel sessions)
  SESSION_KEY="${CLAUDE_SESSION_ID:-}"
  if [ -n "$SESSION_KEY" ]; then
    _TMPDIR="${TMPDIR:-/tmp}"
    SESSION_FILE="${_TMPDIR}/toolbox-session-${SESSION_KEY}.md"
    if [ ! -f "$SESSION_FILE" ]; then
      # Seed session file from global (only on first hook run for this session)
      [ -n "$ACTIVE" ] && printf "active: %s\nupdated: %s\n" "$ACTIVE" "$(date +%Y-%m-%d)" > "$SESSION_FILE"
    else
      # Session file already exists — a mid-session switch may have updated it; use it
      ACTIVE=$(grep -m1 "^active:" "$SESSION_FILE" 2>/dev/null | awk '{print $2}' || echo "$ACTIVE")
    fi
  fi

  echo "---"
  if [ -n "$ACTIVE" ]; then
    # Machine-readable tag + human hint on one line; SESSION_ID lets Claude construct the session file path
    echo "WORKSPACE_MODE:ACTIVE=${ACTIVE} | Projects: ${PROJECTS} | SESSION_ID=${CLAUDE_SESSION_ID}"
    echo "Active project: ${ACTIVE} — reply 'switch project' to change."
  else
    # Machine-readable tag first, then a human-readable selection list
    echo "WORKSPACE_MODE:CHOOSE | Projects: ${PROJECTS} | SESSION_ID=${CLAUDE_SESSION_ID}"
    echo ""
    echo "Which project are you working on? Reply with the name to load its context:"
    N=1
    IFS=',' read -ra PROJ_ARRAY <<< "$PROJECTS"
    for p in "${PROJ_ARRAY[@]}"; do
      echo "  ${N}. ${p}"
      N=$((N+1))
    done
  fi
  echo "Toolbox: active | Skills: ready | Standards: auto-load on first edit"
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
  INDEX_MTIME=$(stat -c "%Y" .claude/index/manifest.json 2>/dev/null \
    || stat -f "%m" .claude/index/manifest.json 2>/dev/null \
    || python3 -c "import os,sys; print(int(os.path.getmtime(sys.argv[1])))" .claude/index/manifest.json 2>/dev/null \
    || echo "0")
  if [ "$LAST_COMMIT_TIME" -gt "$INDEX_MTIME" ]; then
    INDEX_NOTE=" | Index stale — run /index-repo to refresh"
  else
    INDEX_NOTE=" | Index available"
  fi
else
  INDEX_NOTE=" | No index — run /index-repo to build"
fi

# Vault path validation — warn if configured path does not exist on disk
VAULT_PATH_LINE=$(grep -m1 '^\- `\$VAULT`' ~/.claude/toolbox-sections/vault-paths.md 2>/dev/null \
  | sed "s/.*\`\([^\`]*\)\`.*/\1/")
if [ -n "$VAULT_PATH_LINE" ] && [ ! -d "$VAULT_PATH_LINE" ]; then
  echo "Toolbox WARNING: vault path does not exist: ${VAULT_PATH_LINE}"
  echo "Memory reads will fail. Run /set-vault to update the path."
fi

echo "---"
echo "Project context loaded | Stack: ${STACK:-unknown} | Phase: ${PHASE} | Next: ${NEXT}${INDEX_NOTE}"
echo "Memory files are ready. Standards not yet loaded — will auto-load before first code edit."
echo "---"
