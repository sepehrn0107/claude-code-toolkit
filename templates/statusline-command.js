#!/usr/bin/env node
// Claude Code status line — reads session JSON from stdin, writes terminal output
// and per-session snapshot files for the Claude Sessions extension.
//
// Configured in ~/.claude/settings.json as:
//   "statusLine": { "type": "command", "command": "node ~/.claude/statusline-command.js" }
//
// Replaces statusline-command.sh (no bash or Python required).
'use strict';

const fs   = require('fs');
const os   = require('os');
const path = require('path');

let raw = '';
process.stdin.on('data', d => raw += d);
process.stdin.on('end', () => {
  let data = {};
  try { data = JSON.parse(raw); } catch {}

  const cw  = data.context_window || {};
  const fh  = (data.rate_limits || {}).five_hour || {};
  const vim = data.vim || {};
  const ws  = data.workspace || {};

  const cwd         = ws.current_dir || data.cwd || '?';
  const model       = (data.model || {}).display_name || '?';
  const usedPct     = cw.used_percentage               ?? null;
  const usedTokens  = cw.used_tokens                   ?? null;
  const totalTokens = cw.total_tokens ?? cw.max_tokens ?? null;
  const fiveHour    = fh.used_percentage               ?? null;
  const vimMode     = vim.mode                         || '';

  // Short directory — last 2 path components (handles Windows backslashes)
  const normalized = cwd.replace(/\\/g, '/');
  const cwdParts   = normalized.split('/').filter(Boolean);
  const shortDir   = cwdParts.length >= 2
    ? cwdParts.slice(-2).join('/')
    : (cwdParts[0] || cwd);

  // ANSI color helpers
  const C = {
    cyan:    '\x1b[0;36m',
    yellow:  '\x1b[0;33m',
    green:   '\x1b[0;32m',
    red:     '\x1b[0;31m',
    magenta: '\x1b[0;35m',
    reset:   '\x1b[0m',
  };

  let out = `${C.cyan}${shortDir}${C.reset}  ${C.yellow}${model}${C.reset}`;

  if (usedPct !== null) {
    const pct   = Math.round(usedPct);
    const color = pct >= 80 ? C.red : pct >= 50 ? C.yellow : C.green;
    out += `  ${color}ctx:${pct}%${C.reset}`;
  }
  if (fiveHour !== null) {
    out += `  ${C.magenta}5h:${Math.round(fiveHour)}%${C.reset}`;
  }
  if (vimMode) {
    out += `  ${C.green}[${vimMode}]${C.reset}`;
  }

  // Terminal output (ANSI colored)
  process.stdout.write(out + '\n');

  // Per-session snapshot — used by the Claude Sessions extension to show all sessions.
  // process.ppid is the Claude Code process PID, matching ~/.claude/sessions/<pid>.json
  const ppid = process.ppid;
  if (ppid && ppid > 0) {
    const statusDir = path.join(os.homedir(), '.claude', 'sessions-status');
    try {
      fs.mkdirSync(statusDir, { recursive: true });

      const snapshot = {
        pid:       ppid,
        updatedAt: Date.now(),
        cwd,
        model,
      };
      if (usedPct     !== null) snapshot.contextUsedPct     = Math.round(usedPct);
      if (usedTokens  !== null) snapshot.contextUsedTokens  = Math.round(usedTokens);
      if (totalTokens !== null) snapshot.contextTotalTokens = Math.round(totalTokens);
      if (fiveHour    !== null) snapshot.fiveHourUsedPct    = Math.round(fiveHour);

      fs.writeFileSync(
        path.join(statusDir, `${ppid}.json`),
        JSON.stringify(snapshot)
      );
    } catch { /* ignore write failures */ }
  }
});
