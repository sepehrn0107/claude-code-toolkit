# Changelog

All notable changes to the toolbox are recorded here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

---

## [1.1.0] — 2026-03-31

### Added
- `templates/vscode-statusbar/` — VS Code extension that shows Claude Code session stats (directory, model, context %, 5h rate limit) in the status bar, polled every 2 seconds
- `templates/statusline-command.sh` — Claude Code `statusLine` command that writes terminal output and a plain-text cache file for the VS Code extension
- `skills/upgrade.md` — `/upgrade` skill: applies pending toolbox migrations to an existing installation
- `VERSION` — tracks the canonical toolbox version; written to `~/.claude/toolbox-version.txt` on install/upgrade
- Setup skill (CLAUDE.md steps 14–18) now installs the VS Code extension, registers it in `extensions.json`, and writes the installed version

### How to upgrade existing installs
1. `git pull` in the toolbox repo
2. Say `/upgrade` in any Claude Code session

---

## [1.0.0] — 2026-03-31

Retroactive baseline — all features that existed before versioning was introduced.

### Added
- `standards/universal/error-handling.md` — Principles for failing fast, error context, validation, retry logic, and anti-patterns
- `standards/universal/debugging.md` — Systematic debugging process (scientific method, binary search, layer-specific tools, when to ask for help)
- `standards/universal/code-review.md` — Standards for PR authors and reviewers: what to look for, how to give and receive feedback
- `standards/universal/observability.md` — Logging, metrics, health checks, distributed tracing, and alerting standards
- Updated `skills/load-standards.md` to load the four new universal standards
- Full set of lifecycle skills, universal standards, stack standards, and tooling (see README)
