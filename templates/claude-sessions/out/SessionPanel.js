"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.SessionPanel = void 0;
const vscode = __importStar(require("vscode"));
const SessionReader_1 = require("./SessionReader");
class SessionPanel {
    static open(session, extensionUri) {
        const panel = vscode.window.createWebviewPanel("claudeSession", session.firstUserMessage.slice(0, 40) || "Session", vscode.ViewColumn.One, { enableScripts: false });
        let messages = [];
        try {
            messages = (0, SessionReader_1.readSession)(session.filePath);
        }
        catch (e) {
            vscode.window.showErrorMessage(`Failed to read session: ${e}`);
        }
        panel.webview.html = buildHtml(session, messages);
    }
}
exports.SessionPanel = SessionPanel;
function buildHtml(session, messages) {
    const date = session.startedAt
        ? new Date(session.startedAt).toLocaleString()
        : "Unknown";
    const messagesHtml = messages
        .map((m) => {
        const role = m.role === "user" ? "You" : "Claude";
        const cls = m.role === "user" ? "user" : "assistant";
        const time = m.timestamp ? new Date(m.timestamp).toLocaleTimeString() : "";
        const text = escapeHtml(m.text);
        return `
      <div class="message ${cls}">
        <div class="meta"><span class="role">${role}</span><span class="time">${time}</span></div>
        <div class="body">${text}</div>
      </div>`;
    })
        .join("\n");
    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Claude Session</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: var(--vscode-font-family);
      font-size: var(--vscode-font-size);
      color: var(--vscode-foreground);
      background: var(--vscode-editor-background);
      padding: 16px;
    }
    .header {
      border-bottom: 1px solid var(--vscode-panel-border);
      padding-bottom: 12px;
      margin-bottom: 20px;
    }
    .header h2 {
      font-size: 1.1em;
      font-weight: 600;
      margin-bottom: 4px;
      color: var(--vscode-foreground);
    }
    .header .meta {
      font-size: 0.82em;
      color: var(--vscode-descriptionForeground);
    }
    .message {
      margin-bottom: 20px;
      max-width: 860px;
    }
    .message .meta {
      display: flex;
      gap: 12px;
      align-items: baseline;
      margin-bottom: 4px;
    }
    .message .role {
      font-weight: 600;
      font-size: 0.85em;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    .message.user .role { color: var(--vscode-charts-blue); }
    .message.assistant .role { color: var(--vscode-charts-green); }
    .message .time {
      font-size: 0.78em;
      color: var(--vscode-descriptionForeground);
    }
    .message .body {
      line-height: 1.6;
      white-space: pre-wrap;
      word-break: break-word;
      padding: 10px 14px;
      border-radius: 6px;
      background: var(--vscode-editor-inactiveSelectionBackground);
    }
    .message.user .body {
      background: var(--vscode-inputOption-activeBackground);
    }
    .empty {
      color: var(--vscode-descriptionForeground);
      font-style: italic;
      margin-top: 40px;
      text-align: center;
    }
  </style>
</head>
<body>
  <div class="header">
    <h2>${escapeHtml(session.firstUserMessage || session.id)}</h2>
    <div class="meta">${escapeHtml(date)} &nbsp;·&nbsp; ${escapeHtml(session.projectPath)} &nbsp;·&nbsp; ${messages.length} messages</div>
  </div>
  ${messagesHtml || '<div class="empty">No messages found in this session.</div>'}
</body>
</html>`;
}
function escapeHtml(str) {
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}
//# sourceMappingURL=SessionPanel.js.map