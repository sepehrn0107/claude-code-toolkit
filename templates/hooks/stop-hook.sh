#!/usr/bin/env bash
# Toolbox Stop hook — retrospective nudge
# If lessons.md was updated this session, remind the user to run /retrospective.
# Never blocks — always exits 0 to allow the session to end.
# Installed to ~/.claude/stop-hook-git-check.sh by the toolbox upgrade skill.

# Read hook input (contains session_id, transcript_path, etc.)
HOOK_INPUT=$(cat)

# Only activate for toolbox-enabled projects
if [ ! -f ".claude/memory/MEMORY.md" ]; then
  exit 0
fi

# Skip the toolbox repo itself
if [ -f "CLAUDE.md" ] && grep -q "set up the toolbox" CLAUDE.md 2>/dev/null; then
  exit 0
fi

LESSONS=".claude/memory/lessons.md"

if [ ! -f "$LESSONS" ]; then
  exit 0
fi

# Check if lessons.md was modified within the last 8 hours (session window)
MTIME=$(stat -c "%Y" "$LESSONS" 2>/dev/null || echo "0")
NOW=$(date +%s)
AGE=$(( NOW - MTIME ))
EIGHT_HOURS=28800

if [ "$AGE" -lt "$EIGHT_HOURS" ]; then
  echo "lessons.md was updated this session. Run /retrospective to capture learnings before closing out, or save it for project completion."
fi

exit 0
