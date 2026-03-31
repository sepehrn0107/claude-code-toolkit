# Toolbox Public Release — Design Spec
**Date:** 2026-03-31  
**Status:** Awaiting user approval  
**Goal:** Make the repo public on GitHub with maximum discoverability (GitHub search + Google) and the best possible first impression for two audiences: non-coders and developers new to agentic AI workflows.

---

## 1. Overview

This is a content and presentation overhaul, not a feature build. The toolbox already works. The job is to make it findable, understandable, and compelling to people who have never heard of it.

**Structure chosen:** Problem-First (A) + Audience-Split sections (C)  
**Logo:** SVG from `sepehrn.claude-sessions` VS Code extension (`media/icon.svg`), 80px, uses `currentColor` so it adapts to GitHub light/dark themes automatically  
**Audiences:** Non-coders who use Claude and want it to remember context; developers who use Claude Code but work without structured workflows

---

## 2. GitHub Repository Settings

These are changed on github.com, not in the codebase. Do them the moment the repo goes public.

### Description (≤160 characters — shown in search results)
```
Give Claude Code a permanent memory and consistent rules. Loads automatically. Works across every project.
```

### Topics (add all of these — they are GitHub's SEO tags)
```
claude-code  claude  anthropic  ai-tools  llm  developer-tools  productivity
coding-standards  agentic-ai  memory  claude-code-toolkit  ai-workflow
```

### Social Preview Image
- Create a 1280×640px image using the logo SVG on a dark background (#0d1117) with the tagline in white
- This is the thumbnail shown when someone shares the repo link on Twitter/LinkedIn/Discord
- Tool: Figma, Canva, or a simple HTML→screenshot approach
- File goes in repo root as `og-image.png`

### Website field
Leave blank for now (no GitHub Pages site). Add later if traffic justifies it.

---

## 3. README — Full Content Spec

The README is the single landing page. Every section serves a purpose. Nothing is filler.

### 3.1 Hero Section

```markdown
<div align="center">
  <img src="logo.svg" width="80" alt="claude-code-toolkit" />
  <h1>claude-code-toolkit</h1>
  <p>Give Claude Code a permanent memory, consistent rules, and a structured way to work —<br>across every project, every session.</p>

  <!-- badges -->
  ![License](https://img.shields.io/badge/license-MIT-green)
  ![Version](https://img.shields.io/badge/version-1.7.0-purple)
  ![Claude Code](https://img.shields.io/badge/Claude%20Code-compatible-blue)
</div>
```

**Notes:**
- The logo SVG must be committed to the repo root so GitHub can render it
- Badges show legitimacy instantly to developers; non-coders read the tagline and move on
- No table of contents here — keep the opening clean

---

### 3.2 The Problem

```markdown
## The problem

Every Claude Code session starts cold.

It doesn't know your project, your tech stack, your past decisions, or how you like to work.
You re-explain everything. Every time. And the moment you close the window, it's gone.
```

**Why this section exists:** This is pure SEO. Google indexes the words in H2s and the first paragraph. People search for "Claude Code forgets context", "Claude Code memory", "Claude Code keeps forgetting". This section catches all of them. Non-coders feel it immediately. Developers recognize it.

---

### 3.3 The Fix

```markdown
## The fix

This toolkit installs once and runs silently in the background every time you open Claude Code.

It gives Claude:
- **A persistent memory** — it reads your project context, stack, and past decisions automatically at the start of every session
- **Rules it always follows** — coding standards, security practices, git hygiene — loaded per project, never forgotten
- **A built-in workflow** — the right process for every task (building a feature, fixing a bug, reviewing code, opening a PR) triggered by plain English

You open a project. Claude already knows what it is, what stack it uses, and what you were working on. No setup. No re-explaining.
```

---

### 3.4 Who Is This For?

```markdown
## Who is this for?

| | |
|---|---|
| **🙋 I don't write code** | You use Claude to help you write, research, plan, or build things — and you're tired of explaining your project from scratch every session. This toolkit makes Claude remember. Setup takes 5 minutes and you never touch it again. |
| **👩‍💻 I'm a developer** | You use Claude Code daily but work without structured workflows — no consistent standards, no memory between sessions, no automatic routing to the right process. This toolkit fixes all three. One install, every project. |
```

---

### 3.5 Demo / Screenshots

```markdown
## See it in action

> **Session without the toolkit:**  
> You: *"I'm working on a Next.js app with Drizzle ORM..."*  
> *(re-explains project every single session)*

> **Session with the toolkit:**  
> Claude: *"Active project: medianasiri | Stack: Next.js + Drizzle + TypeScript | Last session: implemented auth middleware, next up: dashboard route. Ready to continue."*  
> You: *"add the dashboard route"*  
> Claude: *(reads plan, loads Next.js standards, runs TDD implementation, opens PR — no prompting)*
```

**Implementation note:** Add a real terminal recording GIF here before going public. Recommended tool: [Terminalizer](https://github.com/faressoft/terminalizer) or [Asciinema](https://asciinema.org/). The GIF should show:
1. Opening Claude Code in a project
2. Claude printing the status line with project context already loaded
3. Saying "add X" and watching it route to `/implement` automatically

Even a single 10-second GIF will dramatically increase time-on-page and shares.

---

### 3.6 Quick Install

```markdown
## Install

**Requirements:** Claude Code, Git, Python 3

```bash
# 1. Create a workspace folder and clone
mkdir -p ~/Documents/workspace
git clone https://github.com/sepehrn0107/claude-code-toolkit ~/Documents/workspace/toolbox

# 2. Open the toolbox folder in Claude Code, then say:
Set up the toolbox
```

That's it. Claude handles the rest — it writes the config files, installs the hooks, and sets up your memory system. Takes about 2 minutes.

> **Already have a workspace?** If you just want to add the toolkit to an existing folder, clone it as a subfolder named `toolbox` and say `Set up the toolbox`.
```

**Why this is different from the current README:** The current install section has 6 steps, Windows PATH instructions, and Codex setup before the user has any reason to care. This version does 2 steps first, defers everything optional (Codex, Docker) to a later section.

---

### 3.7 What It Does — Feature Showcase

This is the longest section. Each feature follows the same format:
1. Plain-language title (what it does, not what it's called)
2. One-sentence description
3. **"You say / Claude does"** example box
4. Technical detail (collapsed or below, for developers)

```markdown
## What it does

### Claude remembers your project

At the start of every session, the toolkit reads your project's memory files — what the project is, what stack you're using, what decisions you've made, and what you were doing last time. You never re-explain.

**Example:**
> You open Claude Code in your project  
> Claude: *"Loaded: my-app | Stack: Python + FastAPI | Last session: finished user auth, next: build the API endpoints for profiles"*

---

### Say what you want — it knows what to do

You don't need to know slash commands or workflows. The toolkit detects your intent and routes to the right process automatically.

| You say | What happens |
|---|---|
| "add [feature]" | Full implementation workflow: brainstorm → plan → TDD → PR |
| "fix [bug]" | Systematic debugging process |
| "push this" | Groups commits logically, writes conventional commit messages, opens PR |
| "new project" | Full scaffold: memory files, stack detection, design system, git init |
| "review this" | Standards check across architecture, security, testing, git hygiene |

---

### Coding standards, automatically

The toolkit ships with standards for common stacks. When you work on a project, the right standards load automatically — your code is reviewed against them before every commit.

**Available stacks:** TypeScript + React, Next.js, Go, Python + FastAPI, Drizzle + PostgreSQL

**What standards cover:** architecture patterns, naming conventions, security rules, testing expectations, git hygiene

> No more "Claude, please follow our naming conventions" — it just does.

---

### Full feature implementation, start to finish

Say "add [feature]" and the toolkit runs a 5-phase workflow end to end:

1. **Understand** — reads your memory and standards, writes a context doc
2. **Plan** — brainstorms scope, risks, edge cases; produces a file-level plan
3. **Build** — TDD implementation, red-green-refactor, follows your stack standards
4. **Verify** — checks tests pass, edge cases are covered, error paths handled
5. **Ship** — standards check, conventional commit, opens PR via GitHub CLI

All state is saved to `.claude/tickets/` — if interrupted, it resumes from where it left off.

---

### Code index for large projects

Run `/index-repo` once and the toolkit builds a structural map of your codebase — every file, its symbols, imports, and how it relates to others. Claude uses this map instead of grep, keeping searches fast and context usage low.

---

### Web design audit

Before any PR that touches UI, the toolkit automatically audits your design for 9 areas: design tokens, typography, spacing, color contrast, accessibility (WCAG 2.1 AA), responsive layout, page flow, component consistency, and token adherence.

---

### Fetch any URL cleanly

Routes web fetches through a local [Crawl4AI](https://github.com/unclecode/crawl4ai) container — clean markdown output, 24-hour cache. Never fetches the same page twice in a day.

---

### Delegate to Codex (optional)

When [Codex CLI](https://github.com/openai/codex-plugin-cc) is installed, implementation tasks in Phase 3 are automatically delegated to it. Falls back to direct Claude silently if unavailable.
```

---

### 3.8 Memory System (plain-language explanation)

```markdown
## Memory

The toolkit remembers things in two places:

**Per-project memory** (`.claude/memory/` in each project):
- What the project is and who it's for
- What tech stack it uses and why
- The high-level architecture
- What's been done and what's next
- Patterns and lessons learned

**Global memory** (`<workspace>/memory/`):
- Cross-project learnings
- Your model preferences
- Which project is currently active

Memory is read at the start of every session. It's written at the end. It grows as you work.
```

---

### 3.9 How It's Structured (for developers)

```markdown
## How it works

Four layers load in order:

```
~/.claude/CLAUDE.md              ← your global config (a single @import line — never overwritten)
~/.claude/CLAUDE.global.md       ← toolbox routing, skills, session rules
<workspace>/toolbox/standards/   ← universal + stack-specific coding standards
<project>/.claude/memory/        ← project context, loaded each session
```

Skills live in `toolbox/skills/`. Standards live in `toolbox/standards/`. Templates in `toolbox/templates/`. Nothing is hardcoded — paths are inferred from where you cloned the repo.

Two shell hooks run automatically:
- **`session-start.sh`** — detects the active project, prints status, loads context
- **`pre-tool-standards-gate.sh`** — blocks file edits until standards are loaded for the session

Sub-agents (spawned during `/implement`, code reviews, etc.) inherit all rules automatically via the global `CLAUDE.md` — no explicit context injection needed.
```

---

### 3.10 Optional Setup

```markdown
## Optional setup

### Codex delegation
Install the [Codex CLI](https://github.com/openai/codex-plugin-cc) to have Phase 3 of `/implement` delegate to Codex automatically. Falls back to Claude if unavailable.

```bash
npm install -g @openai/codex
codex   # authenticate once
```

### Web fetching via Crawl4AI
For clean URL fetching with caching:
```bash
docker run -d -p 11235:11235 --name crawl4ai --shm-size=1g unclecode/crawl4ai:latest
```

### Local LLM (Tier 0)
For mechanical tasks (boilerplate, docstrings, simple refactors), the toolkit can route to a local LLM via LM Studio — zero API cost. See `skills/local-llm.md`.
```

---

### 3.11 Contributing

```markdown
## Contributing

All changes go through PRs. The `/retrospective` skill handles this automatically — it creates a branch, commits the proposed change, and opens a PR from within Claude Code.

To contribute manually:
```bash
git checkout -b feat/your-feature
git commit -m "feat: description"
gh pr create
```
```

---

## 4. GitHub Discoverability Strategy

### 4.1 GitHub SEO

GitHub search ranks repos by: stars, forks, topic match, description match, README content match.

**Immediate actions (day of going public):**
1. Set description to the 160-char version in §2
2. Add all 12 topics listed in §2
3. Add the social preview image
4. Pin the repo to your profile

**README keyword density (already baked in above):**
The README naturally contains: `Claude Code`, `memory`, `coding standards`, `persistent memory`, `workflow`, `TDD`, `Claude Code toolkit`, `agentic AI`, `sessions`, `standards`. These are the terms people search.

### 4.2 Google SEO

GitHub READMEs are indexed by Google. The signals Google weights:
- **H1/H2 keywords** — "The problem", "Claude Code", "memory", "coding standards" all appear in headings
- **First 160 characters** — the tagline hits the key terms
- **Backlinks** — every place you share the repo adds a backlink

**Target search queries this README will rank for:**
- "claude code memory persistent"
- "claude code coding standards automatically"
- "claude code workflow toolkit"
- "claude code forgets project"
- "claude code best practices"
- "claude code session memory"

### 4.3 Community Launch Strategy

These are the highest-leverage places to share, in order:

1. **Claude Code GitHub Discussions** — post in the "Show and tell" or similar category. This is the highest-intent audience. Link: `github.com/anthropics/claude-code/discussions`
2. **Reddit r/ClaudeAI** — post as "I built a toolkit that gives Claude Code persistent memory and structured workflows" with a before/after example
3. **Reddit r/ChatGPTCoding** — same post, slightly reworded for the audience
4. **Hacker News "Show HN"** — "Show HN: A toolkit that gives Claude Code persistent memory and auto-loads coding standards" — lead with the problem statement
5. **Twitter/X** — short thread: problem → solution → GIF → link. Tag `@AnthropicAI`
6. **Discord servers** — Claude API Discord, AI Engineer Discord, any developer communities you're in

**What makes a post get traction:**
- Lead with the pain, not the feature list
- Show a before/after (the example in §3.5 is perfect for this)
- Have the GIF ready — posts with visuals get 3-5x more engagement
- Respond to every comment in the first 24 hours

### 4.4 README Badges to Add Later

Once the repo has activity, add:
```markdown
![GitHub stars](https://img.shields.io/github/stars/sepehrn0107/claude-code-toolkit)
![GitHub forks](https://img.shields.io/github/forks/sepehrn0107/claude-code-toolkit)
```
Don't add these on day one — a "0 stars" badge hurts more than it helps.

---

## 5. Logo Usage

**Source:** `C:/Users/sepeh/.vscode/extensions/sepehrn.claude-sessions-0.1.0/media/icon.svg`  
**Action:** Copy to `logo.svg` in the toolbox repo root  
**Size in README:** 80px  
**Color behavior:** Uses `currentColor` — renders white on GitHub dark theme, dark on light theme automatically  
**No modification needed** — it works on both themes as-is

---

## 6. Files To Create / Modify

| File | Action | Notes |
|---|---|---|
| `README.md` | Full rewrite | Replace current content with spec above |
| `logo.svg` | Add to repo root | Copy from claude-sessions extension |
| `og-image.png` | Create and add | 1280×640, dark background, logo + tagline |
| `.gitignore` | Add `.superpowers/` | Keep brainstorm files out of the repo |
| GitHub repo settings | Update | Description, topics, social preview |

**Not changing:**
- Any skill files
- Any standards files
- Any template files
- CHANGELOG.md
- package.json

---

## 7. What This Does Not Include

- A GitHub Pages website (deferred — build if the repo gains traction)
- A "lite" non-coder edition (the plain-language README is sufficient; a separate edition adds maintenance overhead)
- Video tutorials or a YouTube channel (good idea for later, not now)
- Localization (English only for now)
