# Changelog

All notable changes to the toolbox are recorded here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

---

## [1.1.0] — 2026-03-31

### Added
- `templates/claude-sessions/statusline-command.js` — Claude Code `statusLine` command that shows session stats (directory, model, context %, 5h rate limit) in the Claude Code UI and writes per-session snapshots for the Claude Sessions extension
- `skills/upgrade.md` — `/upgrade` skill: applies pending toolbox migrations to an existing installation
- `VERSION` — tracks the canonical toolbox version; written to `~/.claude/toolbox-version.txt` on install/upgrade

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
