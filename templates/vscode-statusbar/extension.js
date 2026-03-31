const vscode = require('vscode');
const fs = require('fs');
const path = require('path');
const os = require('os');

const CACHE_FILE = path.join(os.homedir(), '.claude', 'statusline-cache.txt');
const POLL_MS = 2000;

function activate(context) {
  const bar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
  bar.tooltip = 'Claude Code session status';
  bar.show();

  function update() {
    try {
      const stat = fs.statSync(CACHE_FILE);
      const ageMs = Date.now() - stat.mtimeMs;
      const text = fs.readFileSync(CACHE_FILE, 'utf8').trim();

      if (!text) {
        bar.text = '$(robot) Claude: idle';
      } else if (ageMs > 60_000) {
        // Cache is stale (no active session for >1 min)
        bar.text = `$(robot) ${text} (idle)`;
      } else {
        bar.text = `$(robot) ${text}`;
      }
    } catch {
      bar.text = '$(robot) Claude';
    }
  }

  update();
  const timer = setInterval(update, POLL_MS);

  context.subscriptions.push(bar);
  context.subscriptions.push({ dispose: () => clearInterval(timer) });
}

function deactivate() {}

module.exports = { activate, deactivate };