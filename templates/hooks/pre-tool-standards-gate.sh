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

# Check whether standards were loaded this session
SESSION_KEY="${CLAUDE_SESSION_ID:-$(pwd | md5sum | cut -c1-8)}"
FLAG="/tmp/toolbox-standards-loaded-${SESSION_KEY}"

if [ ! -f "$FLAG" ]; then
  echo "Standards not yet loaded for this session."
  echo "Run /load-standards first (reads universal + stack standards), then retry this edit."
  exit 2
fi

exit 0
