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
exports.SessionsProvider = exports.SessionNode = exports.ProjectNode = void 0;
const vscode = __importStar(require("vscode"));
const SessionReader_1 = require("./SessionReader");
class ProjectNode extends vscode.TreeItem {
    slug;
    constructor(slug) {
        const label = (0, SessionReader_1.slugToPath)(slug);
        super(label, vscode.TreeItemCollapsibleState.Collapsed);
        this.slug = slug;
        this.contextValue = "project";
        this.iconPath = new vscode.ThemeIcon("folder");
        this.tooltip = label;
    }
}
exports.ProjectNode = ProjectNode;
class SessionNode extends vscode.TreeItem {
    session;
    constructor(session) {
        const date = session.startedAt
            ? new Date(session.startedAt).toLocaleString()
            : "Unknown date";
        super(session.firstUserMessage || date, vscode.TreeItemCollapsibleState.None);
        this.session = session;
        this.description = date;
        this.contextValue = "session";
        this.iconPath = new vscode.ThemeIcon("comment-discussion");
        this.tooltip = `${date}\n${session.id}`;
        this.command = {
            command: "claudeSessions.openSession",
            title: "Open Session",
            arguments: [session],
        };
    }
}
exports.SessionNode = SessionNode;
class SessionsProvider {
    _onDidChangeTreeData = new vscode.EventEmitter();
    onDidChangeTreeData = this._onDidChangeTreeData.event;
    refresh() {
        this._onDidChangeTreeData.fire(undefined);
    }
    getTreeItem(element) {
        return element;
    }
    getChildren(element) {
        if (!element) {
            return (0, SessionReader_1.listProjects)().map((slug) => new ProjectNode(slug));
        }
        if (element instanceof ProjectNode) {
            return (0, SessionReader_1.listSessions)(element.slug).map((s) => new SessionNode(s));
        }
        return [];
    }
}
exports.SessionsProvider = SessionsProvider;
//# sourceMappingURL=SessionsProvider.js.map