# Toolbox Public Release — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite the README, add a logo, create a social preview image, and prepare GitHub repo settings so the toolbox is discoverable and compelling when made public.

**Architecture:** Content-only overhaul — no code changes to skills, standards, or templates. Four files change: `README.md` (full rewrite), `logo.svg` (added to repo root), `og-image.png` (new social preview), `.gitignore` (whitelist two new files).

**Tech Stack:** Markdown, SVG, HTML (for og-image generation), GitHub repo settings UI

---

## File Map

| File | Action | Purpose |
|---|---|---|
| `logo.svg` | Create (copy) | Repo logo for README hero and social sharing |
| `og-image.png` | Create | 1280×640 social preview shown when link is shared |
| `og-image.html` | Create (temp) | Source HTML to screenshot for og-image.png |
| `README.md` | Full rewrite | The entire public-facing documentation |
| `.gitignore` | Modify | Whitelist `logo.svg` and `og-image.png` |

---

## Task 1: Add logo and update .gitignore

**Files:**
- Create: `logo.svg` (repo root)
- Modify: `.gitignore`

The `.gitignore` uses a whitelist pattern (`*` at the top ignores everything; `!file` lines re-allow specific files). The two new files must be explicitly whitelisted or git will ignore them.

- [ ] **Step 1: Copy the logo SVG to the repo root**

```bash
cp "C:/Users/sepeh/.vscode/extensions/sepehrn.claude-sessions-0.1.0/media/icon.svg" \
   "C:/Users/sepeh/Documents/workspace/toolbox/logo.svg"
```

- [ ] **Step 2: Verify the copy succeeded**

```bash
ls -lh C:/Users/sepeh/Documents/workspace/toolbox/logo.svg
```

Expected: file exists, size ~90KB

- [ ] **Step 3: Add logo.svg and og-image.png to the .gitignore whitelist**

Open `.gitignore`. After the `!.claude/settings.json` line at the bottom, add:

```gitignore
!logo.svg
!og-image.png
```

The file should end with:
```gitignore
!.claude/
!.claude/settings.json
!logo.svg
!og-image.png
```

- [ ] **Step 4: Verify git sees the logo**

```bash
cd C:/Users/sepeh/Documents/workspace/toolbox && git status
```

Expected output includes `logo.svg` as an untracked file. If it does not appear, the whitelist entry was not saved correctly — recheck `.gitignore`.

- [ ] **Step 5: Commit**

```bash
cd C:/Users/sepeh/Documents/workspace/toolbox
git add logo.svg .gitignore
git commit -m "feat: add repo logo and whitelist in .gitignore"
```

---

## Task 2: Create the social preview image

**Files:**
- Create: `og-image.html` (repo root, temporary — not committed)
- Create: `og-image.png` (repo root, committed)

GitHub shows this 1280×640 image whenever someone shares the repo link. It must be a PNG.

- [ ] **Step 1: Create og-image.html**

Create `C:/Users/sepeh/Documents/workspace/toolbox/og-image.html` with this exact content:

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    width: 1280px;
    height: 640px;
    background: #0d1117;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    overflow: hidden;
  }
  img {
    width: 100px;
    height: 100px;
    object-fit: contain;
    filter: brightness(0) invert(1);
    margin-bottom: 28px;
  }
  h1 {
    font-size: 52px;
    font-weight: 700;
    color: #e6edf3;
    margin-bottom: 20px;
    letter-spacing: -1px;
  }
  p {
    font-size: 24px;
    color: #8b949e;
    text-align: center;
    max-width: 900px;
    line-height: 1.5;
  }
  .badges {
    display: flex;
    gap: 12px;
    margin-top: 32px;
  }
  .badge {
    padding: 6px 18px;
    border-radius: 20px;
    font-size: 16px;
    font-weight: 500;
  }
  .b1 { background: #238636; color: #fff; }
  .b2 { background: #1f6feb; color: #fff; }
  .b3 { background: #6e40c9; color: #fff; }
</style>
</head>
<body>
  <img src="logo.svg" alt="logo" />
  <h1>claude-code-toolkit</h1>
  <p>Give Claude Code a permanent memory, consistent rules, and a structured way to work — across every project, every session.</p>
  <div class="badges">
    <span class="badge b1">MIT License</span>
    <span class="badge b2">Claude Code</span>
    <span class="badge b3">v1.7.0</span>
  </div>
</body>
</html>
```

- [ ] **Step 2: Open the file in a browser and screenshot it**

Open `og-image.html` in Chrome or Edge. The page renders at exactly 1280×640 (the body dimensions are set).

Take a screenshot using one of these methods:
- **Chrome DevTools:** Open DevTools → Cmd/Ctrl+Shift+P → "Capture screenshot" (captures the full page at the correct dimensions)
- **Windows Snipping Tool:** Set browser window to 1280×640, snip exactly the body area
- **macOS:** `Cmd+Shift+4`, drag to select exactly the rendered area

Save the screenshot as `og-image.png` in the repo root: `C:/Users/sepeh/Documents/workspace/toolbox/og-image.png`

- [ ] **Step 3: Verify dimensions**

```bash
python3 -c "
from PIL import Image
img = Image.open('C:/Users/sepeh/Documents/workspace/toolbox/og-image.png')
print(f'Size: {img.size}')
assert img.size == (1280, 640), f'Expected (1280, 640), got {img.size}'
print('OK')
"
```

If PIL is not available, skip this step and verify visually. The image should show the logo, title, tagline, and three badges on a dark background.

- [ ] **Step 4: Commit**

```bash
cd C:/Users/sepeh/Documents/workspace/toolbox
git add og-image.png
git commit -m "feat: add social preview image for GitHub"
```

Note: do not commit `og-image.html` — it's a temporary generation tool.

---

## Task 3: Rewrite README.md

**Files:**
- Modify: `README.md`

This replaces the entire current README. The content below is the complete final file — do not preserve any of the current content.

- [ ] **Step 1: Replace README.md with the new content**

Write the following as the complete content of `C:/Users/sepeh/Documents/workspace/toolbox/README.md`:

````markdown
<div align="center">
  <img src="logo.svg" width="80" alt="claude-code-toolkit" />

  # claude-code-toolkit

  Give Claude Code a permanent memory, consistent rules, and a structured way to work —<br>across every project, every session.

  ![License](https://img.shields.io/badge/license-MIT-green)
  ![Version](https://img.shields.io/badge/version-1.7.0-purple)
  ![Claude Code](https://img.shields.io/badge/Claude%20Code-compatible-blue)
</div>

---

## The problem

Every Claude Code session starts cold.

It doesn't know your project, your tech stack, your past decisions, or how you like to work. You re-explain everything. Every time. And the moment you close the window, it's gone.

---

## The fix

This toolkit installs once and runs silently in the background every time you open Claude Code.

It gives Claude:
- **A persistent memory** — reads your project context, stack, and past decisions at the start of every session automatically
- **Rules it always follows** — coding standards, security practices, git hygiene — loaded per project, never forgotten
- **A built-in workflow** — the right process for every task, triggered by plain English

You open a project. Claude already knows what it is, what stack it uses, and what you were working on. No setup. No re-explaining.

---

## Who is this for?

| | |
|---|---|
| **🙋 I don't write code** | You use Claude to help you write, research, plan, or build things — and you're tired of explaining your project from scratch every session. This toolkit makes Claude remember. Setup takes 5 minutes and you never touch it again. |
| **👩‍💻 I'm a developer** | You use Claude Code daily but work without structured workflows — no consistent standards, no memory between sessions, no automatic routing to the right process. This toolkit fixes all three. One install, every project. |

---

## See it in action

> **Session without the toolkit:**
> You: *"I'm working on a Next.js app with Drizzle ORM, here's what we built last time..."*
> *(re-explains the whole project, every single session)*

> **Session with the toolkit:**
> Claude: *"Active project: my-app | Stack: Next.js + Drizzle + TypeScript | Last session: implemented auth middleware, next up: dashboard route. Ready to continue."*
> You: *"add the dashboard route"*
> Claude: *(reads plan, loads Next.js standards, runs TDD implementation, opens PR — no prompting)*

---

## Install

**Requirements:** [Claude Code](https://claude.ai/code), Git, Python 3

```bash
# 1. Create a workspace folder and clone
mkdir -p ~/Documents/workspace
git clone https://github.com/sepehrn0107/claude-code-toolkit ~/Documents/workspace/toolbox

# 2. Open the toolbox folder in Claude Code, then say:
Set up the toolbox
```

That's it. Claude handles the rest — it writes the config files, installs the hooks, and sets up your memory system.

> **Already have a workspace?** Clone the toolkit as a subfolder named `toolbox` inside your existing workspace folder, then say `Set up the toolbox`.

---

## What it does

### Claude remembers your project

At the start of every session, the toolkit reads your project's memory files — what the project is, what stack you're using, what decisions you've made, and what you were working on last time. You never re-explain.

**Example:**
> You open Claude Code in your project
> Claude: *"Loaded: my-app | Stack: Python + FastAPI | Last session: finished user auth, next: build the API endpoints for profiles"*

---

### Say what you want — it knows what to do

You don't need to know slash commands or workflows. The toolkit detects your intent and routes to the right process automatically.

| You say | What happens |
|---|---|
| `"add [feature]"` | Full implementation workflow: brainstorm → plan → TDD → PR |
| `"fix [bug]"` | Systematic debugging process |
| `"push this"` | Groups commits logically, writes conventional commit messages, opens PR |
| `"new project"` | Full scaffold: memory files, stack detection, design system, git init |
| `"review this"` | Standards check across architecture, security, testing, git hygiene |
| `"switch project"` | Loads a different repo from your workspace |

---

### Coding standards, automatically

The toolkit ships with standards for common stacks. When you work on a project, the right standards load automatically — your code is reviewed against them before every commit.

**Available stacks:** TypeScript + React, Next.js, Go, Python + FastAPI, Drizzle + PostgreSQL

**What standards cover:** architecture patterns, naming conventions, security rules, testing expectations, git hygiene

> No more *"Claude, please follow our naming conventions"* — it just does.

Add standards for a new stack anytime: say `"add standards for [stack]"`.

---

### Full feature implementation, start to finish

Say `"add [feature]"` and the toolkit runs a 5-phase workflow end to end:

| Phase | What happens |
|---|---|
| **1. Understand** | Reads your memory and standards, writes a context doc |
| **2. Plan** | Brainstorms scope, risks, edge cases; produces a file-level plan |
| **3. Build** | TDD implementation, red-green-refactor, follows your stack standards |
| **4. Verify** | Checks tests pass, edge cases covered, error paths handled |
| **5. Ship** | Standards check, conventional commit, opens PR via GitHub CLI |

All state saves to `.claude/tickets/` — if interrupted, it resumes from where it left off.

---

### Code index for large projects

Run `/index-repo` once and the toolkit builds a structural map of your codebase — every file, its symbols, imports, and call relationships. Claude uses this map automatically instead of grepping, keeping searches fast and context usage low.

---

### Web design audit

Before any PR that touches UI, the toolkit automatically audits your design for 9 areas: design tokens, typography, spacing, color contrast, accessibility (WCAG 2.1 AA), responsive layout, page flow, component consistency, and token adherence. Outputs a prioritized fix list with exact file references.

---

### Fetch any URL cleanly

Routes web fetches through a local [Crawl4AI](https://github.com/unclecode/crawl4ai) container — clean markdown output, 24-hour cache. Never fetches the same page twice in a day. Requires Docker.

---

### Delegate to Codex (optional)

When [Codex CLI](https://github.com/openai/codex-plugin-cc) is installed, implementation tasks in Phase 3 are automatically delegated to it. Falls back to direct Claude silently if unavailable.

---

## Memory

The toolkit remembers things in two places:

**Per-project memory** (`.claude/memory/` in each project):

| File | What's stored |
|---|---|
| `project_context.md` | What the project is and who it's for |
| `stack.md` | Tech stack and why it was chosen |
| `architecture.md` | High-level structure, key modules |
| `progress.md` | What's done, what's next |
| `lessons.md` | Patterns and anti-patterns discovered |

**Global memory** (`<workspace>/memory/`): cross-project learnings, model preferences, active project pointer.

Memory is read at the start of every session. It's written at the end. It grows as you work.

---

## How it works (for developers)

Four layers load in order:

```
~/.claude/CLAUDE.md              ← your global config (a single @import — never overwritten by upgrades)
~/.claude/CLAUDE.global.md       ← toolbox routing, skills, session rules
<workspace>/toolbox/standards/   ← universal + stack-specific coding standards
<project>/.claude/memory/        ← project context, loaded each session
```

Two shell hooks run automatically:
- **`session-start.sh`** — detects the active project, prints status, loads context
- **`pre-tool-standards-gate.sh`** — blocks file edits until standards are loaded for the session

Sub-agents spawned during `/implement`, code reviews, etc. inherit all rules automatically via the global `CLAUDE.md` — no explicit context injection needed.

### Stack standards included

| Stack | What's covered |
|---|---|
| `typescript-react` | Components, naming, styling, testing, TypeScript conventions |
| `typescript-nextjs` | Routing, rendering (SSR/SSG/ISR), API routes — inherits React standards |
| `go` | Package design, error handling, testing, toolchain |
| `python-fastapi` | Route structure, dependency injection, validation, testing |
| `drizzle-postgres` | Schema design, migrations, query patterns, type safety |

---

## Optional setup

### Codex delegation

```bash
npm install -g @openai/codex
codex   # authenticate once via browser
```

Implementation tasks in `/implement` Phase 3 are then delegated to Codex automatically. Falls back to direct Claude if Codex is unavailable.

### Web fetching via Crawl4AI

```bash
docker run -d -p 11235:11235 --name crawl4ai --shm-size=1g unclecode/crawl4ai:latest
```

### Local LLM (Tier 0 — zero API cost)

Routes mechanical tasks (boilerplate, docstrings, simple refactors) to a local LLM via LM Studio. See [`skills/local-llm.md`](skills/local-llm.md).

---

## Contributing

All changes go through PRs. The `/retrospective` skill handles this automatically — it creates a branch, commits the proposed change, and opens a PR from within Claude Code.

To contribute manually:

```bash
git checkout -b feat/your-feature
git commit -m "feat: description"
gh pr create
```

---

## License

MIT
````

- [ ] **Step 2: Verify the file was written**

```bash
wc -l C:/Users/sepeh/Documents/workspace/toolbox/README.md
```

Expected: roughly 200–230 lines. If it's under 100, the write failed — try again.

- [ ] **Step 3: Preview the README locally**

Open `README.md` in VS Code. Install the "Markdown Preview Enhanced" extension if not already present, or use VS Code's built-in `Ctrl+Shift+V`. Check:
- Logo `<img>` tag appears at the top (won't render locally without the file, but the tag should be there)
- All tables render correctly — each `|---|---|` row has matching columns
- All code blocks are closed (no unclosed triple backticks)
- The "See it in action" blockquotes render as indented quote blocks
- Badge `![...]` images appear (they fetch from shields.io — requires internet)

- [ ] **Step 4: Commit**

```bash
cd C:/Users/sepeh/Documents/workspace/toolbox
git add README.md
git commit -m "docs: rewrite README for public release — problem-first, audience-split, full feature showcase"
```

---

## Task 4: GitHub repo settings (manual checklist)

**No files.** These are changes made on github.com after the repo is made public.

- [ ] **Step 1: Make the repo public**

Go to `https://github.com/sepehrn0107/claude-code-toolkit` → Settings → Danger Zone → "Change repository visibility" → Public.

- [ ] **Step 2: Set the repo description**

In the repo's main page, click the gear icon next to "About" (top right of the file list). Set:

**Description:**
```
Give Claude Code a permanent memory and consistent rules. Loads automatically. Works across every project.
```

**Website:** leave blank

- [ ] **Step 3: Add all topics**

In the same "About" edit dialog, add these topics one by one (GitHub autocompletes them):

```
claude-code
claude
anthropic
ai-tools
llm
developer-tools
productivity
coding-standards
agentic-ai
memory
claude-code-toolkit
ai-workflow
```

- [ ] **Step 4: Set the social preview image**

Settings → General → Social preview → Upload image → select `og-image.png` from the repo root.

After uploading, paste the repo URL into [opengraph.xyz](https://www.opengraph.xyz/) to verify the preview renders correctly.

- [ ] **Step 5: Pin the repo to your profile**

Go to your GitHub profile (`github.com/sepehrn0107`) → "Customize your profile" → pin `claude-code-toolkit`.

---

## Task 5: Launch (community posts)

**No files.** Execute after the repo is public and settings are confirmed.

- [ ] **Step 1: Post to Claude Code GitHub Discussions**

Navigate to `https://github.com/anthropics/claude-code/discussions`. Find a "Show and tell" or "General" category. Post:

**Title:** I built a toolkit that gives Claude Code persistent memory and auto-loads coding standards

**Body:**
```
Every Claude Code session starts cold — no memory of your project, stack, or past decisions.

I built a toolkit that fixes this: https://github.com/sepehrn0107/claude-code-toolkit

What it does:
- Reads your project context at the start of every session (never re-explain)
- Loads the right coding standards per project automatically
- Routes "add [feature]" / "fix [bug]" / "push this" to the right workflow without prompting
- Runs a 5-phase implementation loop (brainstorm → plan → TDD → verify → PR)

Works across all projects. One install. MIT licensed.

Happy to answer questions.
```

- [ ] **Step 2: Post to Reddit r/ClaudeAI**

Title: `I built a toolkit that gives Claude Code persistent memory across sessions`

Body: same as above, plus add the before/after example from the README's "See it in action" section.

- [ ] **Step 3: Post to Reddit r/ChatGPTCoding**

Same post, slightly reworded: replace "Claude Code" with "Claude" in the opening line since this audience is broader.

- [ ] **Step 4: Hacker News Show HN**

Title: `Show HN: claude-code-toolkit – persistent memory and structured workflows for Claude Code`

Body: paste the problem/fix section from the README, link to the repo. Keep it under 200 words.

- [ ] **Step 5: Respond to all comments within 24 hours**

This is the highest-leverage action for early traction. Every response keeps the post active in ranking algorithms.

---

## Verification Checklist

Run this after all tasks are complete:

- [ ] `logo.svg` exists in repo root and appears in the README hero on GitHub
- [ ] `og-image.png` exists and is set as the GitHub social preview
- [ ] README renders correctly on GitHub (dark/light mode — check both)
- [ ] Logo renders white on dark mode, dark on light mode (it uses `currentColor`, this is automatic)
- [ ] All 12 topics appear on the repo
- [ ] Repo description matches the spec exactly
- [ ] Repo is public and visible without login
- [ ] At least one community post is live
