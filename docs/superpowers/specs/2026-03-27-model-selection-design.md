# Model Selection Design Spec
**Date:** 2026-03-27
**Status:** Approved

---

## Overview

When the toolbox launches sub-agents, it automatically selects the most cost-effective model for the task. A memory-first policy means zero friction once configured — Claude reads a saved preference and launches silently. When no config exists, Claude reasons about the task and presents 2 options; the user types `1` or `2` and may optionally say "save this config" to persist the choice.

Sub-agents launched by the toolbox have access to superpowers skills via the `Skill` tool and are instructed to use them when relevant.

---

## Architecture

### Flow

```
Before launching any sub-agent:
  1. Read memory/model-config.md
  2. If config exists → use saved model silently, launch agent
  3. If no config → reason about task complexity, present 2 options
  4. User types 1 or 2 (optionally adds "save this config")
  5. If "save this config" → write choice to memory/model-config.md
  6. Launch agent with chosen model + superpowers instruction
```

### `memory/model-config.md` schema

```markdown
---
default_model: haiku
saved_by_user: true
---

Use haiku for routine/search/lookup tasks.
Use sonnet for complex reasoning, multi-step implementation, or architecture decisions.
Use opus for highly novel, open-ended, or high-stakes tasks.
```

This file is written by `skills/select-model.md` when the user says "save this config". It lives in the global toolbox memory so the preference applies across all projects.

---

## `skills/select-model.md`

A new skill invoked by any toolbox skill before spawning an agent. Responsibilities:

1. **Read config** — check `memory/model-config.md`. If present, return the saved model immediately (no prompt).
2. **Reason about task** — if no config, evaluate the task description against complexity heuristics (see below).
3. **Present 2 options** — recommended model as option 1, more capable as option 2, each with a one-line justification.
4. **Accept input** — user types `1` or `2`. If response includes "save this config", write to `memory/model-config.md`.
5. **Return model** — the calling skill uses this model in the `Agent` tool call.
6. **Inject superpowers** — every agent prompt includes: *"You have access to superpowers skills via the Skill tool — use them when relevant."*

### Complexity heuristics

| Task type | Recommended model |
|---|---|
| File search, pattern matching, simple lookups | haiku |
| Code reading, summarization, straightforward edits | haiku |
| Multi-step implementation, TDD, code generation | sonnet |
| Architecture decisions, brainstorming, planning | sonnet |
| Novel problem-solving, highly ambiguous tasks | opus |
| Security review, high-stakes analysis | opus |

When uncertain, recommend sonnet as the safe middle ground.

---

## Sub-agent Superpowers

**Finding:** Superpowers is enabled as a plugin in `.claude/settings.json`. Sub-agents launched in the project inherit the plugin, so the `Skill` tool is available to them. The `using-superpowers` orchestration skill contains a `<SUBAGENT-STOP>` directive — this is intentional and correct. Sub-agents skip the brainstorming/planning workflow but can and should invoke individual skills (e.g., `superpowers:code-reviewer`, `superpowers:systematic-debugging`).

**Implementation:** The `select-model.md` skill appends the following to every agent prompt it generates:

> You have access to superpowers skills via the Skill tool. Use them when relevant — for example, use `superpowers:systematic-debugging` if you encounter a bug, or `superpowers:code-reviewer` when reviewing code.

No changes to the superpowers plugin itself are needed.

---

## Skills Updated

The following skills launch sub-agents and must be updated to invoke `select-model.md` before each `Agent` call:

- `skills/add-feature.md` — invokes brainstorming, TDD, verification agents
- `skills/new-project.md` — invokes brainstorming and writing-plans agents
- `skills/standards-check.md` — invokes code-reviewer and code-simplifier agents
- `skills/retrospective.md` — invokes analysis agents

---

## README

A root `README.md` is added covering:

1. What this is
2. Getting started (clone, setup, first use)
3. How it works (4-layer system, lifecycle skills)
4. Model selection (memory-first policy, 2-option prompt, "save this config")
5. Sub-agents and superpowers
6. Contributing (PRs only, never direct to master)

---

## Files Added / Modified

| File | Action |
|---|---|
| `skills/select-model.md` | New — model selection skill |
| `memory/model-config.md` | New — written on first "save this config" |
| `skills/add-feature.md` | Updated — invoke select-model before agent launches |
| `skills/new-project.md` | Updated — invoke select-model before agent launches |
| `skills/standards-check.md` | Updated — invoke select-model before agent launches |
| `skills/retrospective.md` | Updated — invoke select-model before agent launches |
| `README.md` | New — getting started + model selection docs |
