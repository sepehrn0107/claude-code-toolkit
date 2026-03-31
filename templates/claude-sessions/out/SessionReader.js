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
exports.listProjects = listProjects;
exports.slugToPath = slugToPath;
exports.listSessions = listSessions;
exports.readSession = readSession;
const fs = __importStar(require("fs"));
const os = __importStar(require("os"));
const path = __importStar(require("path"));
const CLAUDE_DIR = path.join(os.homedir(), ".claude", "projects");
function listProjects() {
    if (!fs.existsSync(CLAUDE_DIR))
        return [];
    return fs
        .readdirSync(CLAUDE_DIR, { withFileTypes: true })
        .filter((d) => d.isDirectory())
        .map((d) => d.name);
}
function slugToPath(slug) {
    return slug.replace(/^[a-z]--/, (m) => m[0].toUpperCase() + ":\\").replace(/--/g, "\\");
}
function listSessions(projectSlug) {
    const dir = path.join(CLAUDE_DIR, projectSlug);
    if (!fs.existsSync(dir))
        return [];
    const files = fs
        .readdirSync(dir)
        .filter((f) => f.endsWith(".jsonl") && !f.startsWith("."));
    const sessions = [];
    for (const file of files) {
        const filePath = path.join(dir, file);
        const id = file.replace(".jsonl", "");
        const lines = readLines(filePath, 20);
        let startedAt = "";
        let firstUserMessage = "(empty)";
        for (const line of lines) {
            try {
                const obj = JSON.parse(line);
                if (!startedAt && obj.timestamp) {
                    startedAt = obj.timestamp;
                }
                if (obj.type === "user" &&
                    obj.message?.content?.[0]?.text &&
                    firstUserMessage === "(empty)") {
                    firstUserMessage = obj.message.content[0].text.slice(0, 80).trim();
                }
            }
            catch {
                // skip malformed lines
            }
        }
        sessions.push({
            id,
            projectSlug,
            projectPath: slugToPath(projectSlug),
            filePath,
            startedAt,
            firstUserMessage,
        });
    }
    return sessions.sort((a, b) => b.startedAt.localeCompare(a.startedAt));
}
function readSession(filePath) {
    const messages = [];
    const content = fs.readFileSync(filePath, "utf8");
    for (const line of content.split("\n")) {
        if (!line.trim())
            continue;
        try {
            const obj = JSON.parse(line);
            if (obj.type === "user" && obj.message?.content) {
                const text = extractText(obj.message.content);
                if (text) {
                    messages.push({ role: "user", text, timestamp: obj.timestamp ?? "" });
                }
            }
            else if (obj.type === "assistant" && obj.message?.content) {
                const text = extractText(obj.message.content);
                if (text) {
                    messages.push({
                        role: "assistant",
                        text,
                        timestamp: obj.timestamp ?? "",
                    });
                }
            }
        }
        catch {
            // skip malformed lines
        }
    }
    return messages;
}
function readLines(filePath, maxLines) {
    const content = fs.readFileSync(filePath, "utf8");
    return content.split("\n").slice(0, maxLines);
}
function extractText(content) {
    if (typeof content === "string")
        return content;
    if (Array.isArray(content)) {
        return content
            .filter((c) => c?.type === "text")
            .map((c) => c.text)
            .join("\n");
    }
    return "";
}
//# sourceMappingURL=SessionReader.js.map