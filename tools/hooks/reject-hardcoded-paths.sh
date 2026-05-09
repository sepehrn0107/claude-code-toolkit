#!/usr/bin/env bash
# Pre-commit hook: reject user-specific absolute paths in tracked skill/template files.

set -euo pipefail

PATTERN='(C:/Users/[^{[:space:]]+/|/home/[^{[:space:]]+/toolbox|/Users/[^{[:space:]]+/toolbox)'
TRACKED=$(git diff --cached --name-only --diff-filter=ACM | grep -E '^(skills|templates|standards|tools/hooks)/' || true)

if [ -z "$TRACKED" ]; then exit 0; fi

FOUND=0
while IFS= read -r file; do
  if git show ":$file" 2>/dev/null | grep -qE "$PATTERN"; then
    echo "[reject-hardcoded-paths] User-specific absolute path found in: $file"
    echo "  Replace with {{TOOLBOX_PATH}}, {{VAULT_PATH}}, or another placeholder."
    FOUND=1
  fi
done <<< "$TRACKED"

if [ "$FOUND" -eq 1 ]; then
  echo ""
  echo "Commit rejected. Fix the paths above before committing."
  exit 1
fi

exit 0
