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
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const fs = __importStar(require("fs"));
const os = __importStar(require("os"));
const path = __importStar(require("path"));
const SessionsProvider_1 = require("./SessionsProvider");
const SessionPanel_1 = require("./SessionPanel");
function activate(context) {
    const provider = new SessionsProvider_1.SessionsProvider();
    context.subscriptions.push(vscode.window.registerTreeDataProvider("claudeSessionsTree", provider));
    context.subscriptions.push(vscode.commands.registerCommand("claudeSessions.refresh", () => {
        provider.refresh();
    }));
    context.subscriptions.push(vscode.commands.registerCommand("claudeSessions.openSession", (session) => {
        SessionPanel_1.SessionPanel.open(session, context.extensionUri);
    }));
    // watch ~/.claude/projects for new sessions
    const watchDir = path.join(os.homedir(), ".claude", "projects");
    if (fs.existsSync(watchDir)) {
        const watcher = fs.watch(watchDir, { recursive: true }, () => {
            provider.refresh();
        });
        context.subscriptions.push({ dispose: () => watcher.close() });
    }
}
function deactivate() { }
//# sourceMappingURL=extension.js.map