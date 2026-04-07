#!/usr/bin/env bash
# Toolbox PreToolUse standards gate
# Blocks Edit/Write/MultiEdit/NotebookEdit until /load-standards has been run this session.
# Installed to ~/.claude/hooks/pre-tool-standards-gate.sh by the toolbox setup skill.
#
# Claude Code passes the tool call as JSON via stdin.
# Exit code 2 = block the tool call and show stdout as the error message.

# Read the tool name from stdin JSON
TOOL_NAME=$(cat | jq -r '.tool_name // empty' 2>/dev/null)

# Only gate code-editing tools
case "$TOOL_NAME" in
  Edit|Write|MultiEdit|NotebookEdit) ;;
  *) exit 0 ;;
esac

# Only activate if this is a toolbox-enabled project
if [ ! -f ".claude/memory/MEMORY.md" ]; then
  exit 0
fi

# Skip the toolbox repo itself
if [ -f "CLAUDE.md" ] && grep -q "set up the toolbox" CLAUDE.md 2>/dev/null; then
  exit 0
fi

# Portable md5: GNU md5sum (Linux/Windows-Git-Bash) → macOS md5 → python3 fallback
_md5() {
  if command -v md5sum >/dev/null 2>&1; then
    md5sum | cut -c1-8
  elif command -v md5 >/dev/null 2>&1; then
    md5 -q | cut -c1-8
  else
    python3 -c "import sys,hashlib; print(hashlib.md5(sys.stdin.buffer.read()).hexdigest()[:8])"
  fi
}

# Check whether standards were loaded this session
SESSION_KEY="${CLAUDE_SESSION_ID:-$(pwd | _md5)}"
_TMPDIR="${TMPDIR:-/tmp}"
FLAG="${_TMPDIR}/toolbox-standards-loaded-${SESSION_KEY}"

if [ ! -f "$FLAG" ]; then
  echo "Standards not yet loaded for this session."
  echo "Run /load-standards first (reads universal + stack standards), then retry this edit."
  exit 2
fi

exit 0
