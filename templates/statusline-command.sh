#!/usr/bin/env bash
# Claude Code status line — writes stats to terminal and to the VS Code status bar cache.
# Installed to ~/.claude/statusline-command.sh by the toolbox setup/upgrade skill.
# Configured in ~/.claude/settings.json as: "statusLine": {"type": "command", "command": "bash ~/.claude/statusline-command.sh"}

input=$(cat)

# Use Python to parse JSON and output tab-separated fields
parsed=$(echo "$input" | python3 -c "
import sys, json

try:
    data = json.load(sys.stdin)
except Exception:
    data = {}

cwd       = (data.get('workspace') or {}).get('current_dir') or data.get('cwd') or '?'
model     = (data.get('model') or {}).get('display_name') or '?'
used_pct  = (data.get('context_window') or {}).get('used_percentage')
five_hour = ((data.get('rate_limits') or {}).get('five_hour') or {}).get('used_percentage')
vim_mode  = (data.get('vim') or {}).get('mode') or ''

print('\t'.join([
    cwd,
    model,
    str(used_pct) if used_pct is not None else '',
    str(five_hour) if five_hour is not None else '',
    vim_mode,
]))
" 2>/dev/null)

cwd=$(echo "$parsed"       | cut -f1)
model=$(echo "$parsed"     | cut -f2)
used_pct=$(echo "$parsed"  | cut -f3)
five_hour=$(echo "$parsed" | cut -f4)
vim_mode=$(echo "$parsed"  | cut -f5)

# Directory: last two path components (handles both / and \)
short_dir=$(echo "$cwd" | sed 's|\\|/|g' | awk -F'/' '{if(NF>=2) print $(NF-1)"/"$NF; else print $NF}')

# ANSI helpers
cyan='\033[0;36m'
yellow='\033[0;33m'
green='\033[0;32m'
red='\033[0;31m'
magenta='\033[0;35m'
reset='\033[0m'

parts="${cyan}${short_dir}${reset}"
parts="${parts}  ${yellow}${model}${reset}"

if [ -n "$used_pct" ]; then
  used_int=$(printf '%.0f' "$used_pct" 2>/dev/null || echo 0)
  if [ "$used_int" -ge 80 ]; then ctx_color="$red"
  elif [ "$used_int" -ge 50 ]; then ctx_color="$yellow"
  else ctx_color="$green"
  fi
  parts="${parts}  ${ctx_color}ctx:${used_int}%${reset}"
fi

if [ -n "$five_hour" ]; then
  five_int=$(printf '%.0f' "$five_hour" 2>/dev/null || echo 0)
  parts="${parts}  ${magenta}5h:${five_int}%${reset}"
fi

if [ -n "$vim_mode" ]; then
  parts="${parts}  ${green}[${vim_mode}]${reset}"
fi

printf "%b\n" "$parts"

# Write a plain-text (ANSI-stripped) copy for the VS Code status bar extension
plain=$(printf "%b" "$parts" | sed 's/\x1b\[[0-9;]*m//g')
echo "$plain" > ~/.claude/statusline-cache.txt