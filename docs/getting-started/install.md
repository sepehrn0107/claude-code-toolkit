---
title: "Install"
section: getting-started
skills-affected: [upgrade, upgrade-dev, set-vault]
last-updated: 2026-04-03
---

# Install

## Requirements

- [Claude Code](https://claude.ai/code) — CLI, desktop app, or VS Code extension
- Git
- Python 3

Optional (for specific features):
- Docker — required for `/web-fetch` (Crawl4AI) and `/local-llm`
- [Codex CLI](https://github.com/openai/codex-plugin-cc) — enables automatic Phase 3 delegation

## Step 1 — Clone

Create a workspace folder and clone the toolkit as `toolbox/` inside it:

```bash
mkdir -p ~/Documents/workspace
git clone https://github.com/sepehrn0107/claude-code-toolkit ~/Documents/workspace/toolbox
```

The workspace folder can be named anything and can be any location. The toolkit must
live as a subfolder named `toolbox/` inside it.

> Already have a workspace? Clone into it directly:
> `git clone ... ~/Documents/workspace/toolbox`

## Step 2 — Run setup

Open the `toolbox/` folder in Claude Code. Say:

```
Set up the toolbox
```

Claude detects the install path, writes `~/.claude/CLAUDE.md`, installs the session
hooks, and sets up the global memory directory. Setup takes about 30 seconds.

## Step 3 — Configure vault path

Run `/upgrade-dev` and follow the prompt. Claude asks for the folder where memory,
specs, and plans should be stored. This can be any directory — an Obsidian vault,
a plain folder, or a synced cloud directory.

Change the vault path anytime with `/set-vault`.

## Verify the install

Open any project folder in Claude Code. You should see this status line at the start
of the session:

```
Toolbox: active | Skills: ready | Standards: auto-load on first edit
```

If you don't see it, check that `~/.claude/CLAUDE.md` was written and that the session
hook at `~/.claude/hooks/session-start.sh` is executable:

```bash
ls -la ~/.claude/hooks/session-start.sh
```

## Upgrading

```bash
cd ~/Documents/workspace/toolbox
git pull
```

Then say `/upgrade` in any Claude Code session.
