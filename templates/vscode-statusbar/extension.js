'use strict';
const vscode = require('vscode');
const fs     = require('fs');
const path   = require('path');
const os     = require('os');

const CLAUDE_DIR         = path.join(os.homedir(), '.claude');
const CACHE_FILE         = path.join(CLAUDE_DIR, 'statusline-cache.txt');
const SESSIONS_DIR       = path.join(CLAUDE_DIR, 'sessions');
const SESSIONS_STATUS_DIR = path.join(CLAUDE_DIR, 'sessions-status');

const POLL_MS   = 2000;
const STALE_MS  = 10 * 60 * 1000; // 10 minutes without update = session considered gone
const CLEAN_MS  = 5  * 60 * 1000; // run cleanup every 5 minutes

// ── PID liveness ──────────────────────────────────────────────────────────────
function isPidAlive(pid) {
  try {
    process.kill(pid, 0);
    return true;
  } catch (e) {
    return e.code === 'EPERM'; // process exists but we lack permission to signal it
  }
}

// ── Read and merge all session data ──────────────────────────────────────────
function readAllSessions() {
  // Base metadata: pid → { sessionId, cwd, startedAt, kind, entrypoint }
  const meta = {};
  try {
    for (const f of fs.readdirSync(SESSIONS_DIR)) {
      if (!f.endsWith('.json')) continue;
      const pid = parseInt(f, 10);
      if (!isFinite(pid)) continue;
      try { meta[pid] = JSON.parse(fs.readFileSync(path.join(SESSIONS_DIR, f), 'utf8')); }
      catch { /* skip corrupt */ }
    }
  } catch { /* directory missing */ }

  // Live status snapshots
  const sessions = [];
  try {
    for (const f of fs.readdirSync(SESSIONS_STATUS_DIR)) {
      if (!f.endsWith('.json')) continue;
      const pid = parseInt(f, 10);
      if (!isFinite(pid)) continue;
      try {
        const s = JSON.parse(fs.readFileSync(path.join(SESSIONS_STATUS_DIR, f), 'utf8'));
        if (Date.now() - (s.updatedAt || 0) > STALE_MS) continue; // too old
        if (!isPidAlive(pid)) continue;                            // dead process
        const m = meta[pid] || {};
        sessions.push({
          pid,
          sessionId:          m.sessionId          || null,
          cwd:                s.cwd                || m.cwd || '?',
          startedAt:          m.startedAt          || null,
          model:              s.model              || '?',
          contextUsedPct:     s.contextUsedPct     ?? null,
          contextUsedTokens:  s.contextUsedTokens  ?? null,
          contextTotalTokens: s.contextTotalTokens ?? null,
          fiveHourUsedPct:    s.fiveHourUsedPct    ?? null,
          updatedAt:          s.updatedAt          || 0,
        });
      } catch { /* skip corrupt */ }
    }
  } catch { /* sessions-status dir missing */ }

  sessions.sort((a, b) => b.updatedAt - a.updatedAt);
  return sessions;
}

// ── Cleanup stale / dead session status files ─────────────────────────────────
function cleanStaleStatusFiles() {
  try {
    for (const f of fs.readdirSync(SESSIONS_STATUS_DIR)) {
      if (!f.endsWith('.json')) continue;
      const pid      = parseInt(f, 10);
      const filePath = path.join(SESSIONS_STATUS_DIR, f);
      try {
        const s     = JSON.parse(fs.readFileSync(filePath, 'utf8'));
        const stale = Date.now() - (s.updatedAt || 0) > STALE_MS;
        const dead  = !isPidAlive(pid);
        if (stale || dead) fs.unlinkSync(filePath);
      } catch {
        try { fs.unlinkSync(filePath); } catch {} // unreadable → delete
      }
    }
  } catch { /* directory missing, nothing to do */ }
}

// ── Dashboard HTML ────────────────────────────────────────────────────────────
function buildDashboardHtml(sessions) {
  function shortDir(cwd) {
    const p = cwd.replace(/\\/g, '/').split('/').filter(Boolean);
    return p.length >= 2 ? p.slice(-2).join('/') : (p[0] || cwd);
  }
  function barColor(pct) {
    if (pct === null) return '#4a4a4a';
    if (pct >= 80)    return '#e05252';
    if (pct >= 50)    return '#d4a017';
    return '#4caf50';
  }
  function fmtTokens(n) {
    if (n == null)    return '—';
    if (n >= 1e6)     return (n / 1e6).toFixed(1) + 'M';
    if (n >= 1e3)     return (n / 1e3).toFixed(1) + 'k';
    return String(n);
  }
  function timeAgo(ms) {
    if (!ms) return '';
    const s = Math.floor((Date.now() - ms) / 1000);
    if (s < 5)    return 'just now';
    if (s < 60)   return `${s}s ago`;
    if (s < 3600) return `${Math.floor(s / 60)}m ago`;
    return `${Math.floor(s / 3600)}h ago`;
  }

  const cards = sessions.length === 0
    ? '<div class="empty">No active Claude sessions detected.</div>'
    : sessions.map(s => {
        const pct      = s.contextUsedPct;
        const barW     = pct !== null ? Math.min(100, Math.max(0, pct)) : 0;
        const bColor   = barColor(pct);
        const pctLabel = pct !== null ? `${pct}%` : '—';
        const usedTok  = fmtTokens(s.contextUsedTokens);
        const totalTok = fmtTokens(s.contextTotalTokens);
        const tokStr   = (s.contextUsedTokens != null || s.contextTotalTokens != null)
          ? `${usedTok} / ${totalTok} tokens` : '';
        const fiveH    = s.fiveHourUsedPct !== null ? `${s.fiveHourUsedPct}%` : '—';

        return `
        <div class="card">
          <div class="card-header">
            <span class="dir" title="${s.cwd.replace(/"/g, '&quot;')}">${shortDir(s.cwd)}</span>
            <span class="pid">PID ${s.pid}</span>
          </div>
          <div class="model">${s.model}</div>
          <div class="ctx-row">
            <div class="ctx-label">
              <span>Context</span>
              <span class="ctx-pct" style="color:${bColor}">${pctLabel}</span>
            </div>
            <div class="ctx-bar-bg">
              <div class="ctx-bar-fill" style="width:${barW}%;background:${bColor}"></div>
            </div>
            ${tokStr ? `<div class="ctx-tokens">${tokStr}</div>` : ''}
          </div>
          <div class="meta-row">
            <span class="meta-item">5h rate: <b>${fiveH}</b></span>
            <span class="updated">${timeAgo(s.updatedAt)}</span>
          </div>
        </div>`;
      }).join('');

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Claude Sessions</title>
<style>
  :root {
    --bg:      #1e1e1e;
    --surface: #252526;
    --border:  #3c3c3c;
    --text:    #cccccc;
    --muted:   #858585;
    --accent:  #569cd6;
    --radius:  6px;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--bg); color: var(--text);
    font-family: -apple-system, 'Segoe UI', sans-serif;
    font-size: 13px; padding: 16px;
  }
  h1 {
    font-size: 14px; font-weight: 600; color: var(--accent);
    margin-bottom: 14px; display: flex; align-items: center; gap: 8px;
  }
  h1 .count {
    background: var(--border); border-radius: 10px;
    padding: 1px 7px; font-size: 11px; color: var(--muted);
  }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 12px;
  }
  .card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 12px 14px;
    display: flex; flex-direction: column; gap: 8px;
  }
  .card-header { display: flex; justify-content: space-between; align-items: baseline; gap: 8px; }
  .dir {
    font-weight: 600; color: #4ec9b0;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex: 1;
  }
  .pid { font-size: 10px; color: var(--muted); white-space: nowrap; }
  .model { font-size: 11px; color: var(--accent); }
  .ctx-row { display: flex; flex-direction: column; gap: 4px; }
  .ctx-label { display: flex; justify-content: space-between; font-size: 11px; color: var(--muted); }
  .ctx-pct { font-weight: 600; }
  .ctx-bar-bg { height: 4px; background: var(--border); border-radius: 2px; overflow: hidden; }
  .ctx-bar-fill { height: 100%; border-radius: 2px; transition: width 0.3s; }
  .ctx-tokens { font-size: 10px; color: var(--muted); text-align: right; }
  .meta-row { display: flex; align-items: center; justify-content: space-between; font-size: 11px; color: var(--muted); }
  .updated { color: var(--muted); }
  .empty { color: var(--muted); font-style: italic; padding: 32px 0; text-align: center; }
  .footer { margin-top: 14px; display: flex; align-items: center; gap: 10px; }
  button {
    background: var(--surface); border: 1px solid var(--border);
    color: var(--text); padding: 4px 10px;
    border-radius: var(--radius); cursor: pointer; font-size: 12px;
  }
  button:hover { border-color: var(--accent); color: var(--accent); }
  .hint { font-size: 11px; color: var(--muted); }
</style>
</head>
<body>
<h1>Claude Sessions <span class="count">${sessions.length}</span></h1>
<div class="grid">${cards}</div>
<div class="footer">
  <button onclick="refresh()">Refresh</button>
  <span class="hint">Auto-refreshes every 5s</span>
</div>
<script>
  const vscode = acquireVsCodeApi();
  function refresh() { vscode.postMessage({ command: 'refresh' }); }
  setInterval(refresh, 5000);
</script>
</body>
</html>`;
}

// ── Extension activate ────────────────────────────────────────────────────────
function activate(context) {
  let panel = null;

  // Status bar item — clicking opens the dashboard
  const bar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
  bar.tooltip = 'Claude Code sessions — click to open dashboard';
  bar.command  = 'claudeStatusbar.showDashboard';
  bar.show();

  // Update status bar text from cache file (unchanged logic from v0.0.1)
  function updateBar() {
    try {
      const stat  = fs.statSync(CACHE_FILE);
      const ageMs = Date.now() - stat.mtimeMs;
      const text  = fs.readFileSync(CACHE_FILE, 'utf8').trim();
      if (!text)          bar.text = '$(robot) Claude: idle';
      else if (ageMs > 60_000) bar.text = `$(robot) ${text} (idle)`;
      else                bar.text = `$(robot) ${text}`;
    } catch {
      bar.text = '$(robot) Claude';
    }
  }

  // Open or refresh the dashboard webview
  function openOrRefreshDashboard() {
    const sessions = readAllSessions();
    if (!panel) {
      panel = vscode.window.createWebviewPanel(
        'claudeDashboard',
        'Claude Sessions',
        { viewColumn: vscode.ViewColumn.Beside, preserveFocus: true },
        { enableScripts: true, retainContextWhenHidden: true }
      );
      panel.onDidDispose(() => { panel = null; }, null, context.subscriptions);
      panel.webview.onDidReceiveMessage(
        msg => { if (msg.command === 'refresh') openOrRefreshDashboard(); },
        null, context.subscriptions
      );
    }
    panel.webview.html = buildDashboardHtml(sessions);
  }

  // Command: open or refresh dashboard
  const cmd = vscode.commands.registerCommand(
    'claudeStatusbar.showDashboard',
    openOrRefreshDashboard
  );

  // Poll: update status bar and auto-refresh open panel
  updateBar();
  const pollTimer = setInterval(() => {
    updateBar();
    if (panel) openOrRefreshDashboard();
  }, POLL_MS);

  // Watch sessions-status directory for instant refresh
  let watcher = null;
  try {
    fs.mkdirSync(SESSIONS_STATUS_DIR, { recursive: true });
    watcher = fs.watch(SESSIONS_STATUS_DIR, () => {
      if (panel) openOrRefreshDashboard();
    });
  } catch { /* fall back to polling only */ }

  // Periodic cleanup of stale snapshot files
  const cleanTimer = setInterval(cleanStaleStatusFiles, CLEAN_MS);

  context.subscriptions.push(bar, cmd, {
    dispose() {
      clearInterval(pollTimer);
      clearInterval(cleanTimer);
      if (watcher) watcher.close();
    },
  });
}

function deactivate() {}
module.exports = { activate, deactivate };
