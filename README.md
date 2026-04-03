<div align="center">
  <img src="logo.svg" width="80" alt="claude-code-toolkit" />

  # claude-code-toolkit

  Give Claude Code a permanent memory, consistent rules, and a structured way to work —<br>across every project, every session.

  ![License](https://img.shields.io/badge/license-MIT-green)
  ![Version](https://img.shields.io/badge/version-1.7.0-purple)
  ![Claude Code](https://img.shields.io/badge/Claude%20Code-compatible-blue)
  [![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://sepehrn0107.github.io/claude-code-toolkit/)
</div>

---

## The problem

Every Claude Code session starts cold. No project context, no past decisions, no rules — you re-explain everything, every time.

---

## The fix

Install once. Claude reads your project context, stack, and history at the start of every session automatically.

- **Persistent memory** — project context, stack decisions, progress, and learnings survive across sessions
- **Automatic standards** — coding rules load per project and are enforced before every code edit
- **Intent routing** — say `"add [feature]"` or `"fix [bug]"` and the right workflow runs
- **Full implementation workflow** — brainstorm → plan → TDD → verify → PR, end to end

---

## Install

**Requirements:** [Claude Code](https://claude.ai/code), Git, Python 3

```bash
mkdir -p ~/Documents/workspace
git clone https://github.com/sepehrn0107/claude-code-toolkit ~/Documents/workspace/toolbox
```

Open the toolbox folder in Claude Code, then say: `Set up the toolbox`

Then run `/upgrade-dev` once to configure your vault path.

---

## Documentation

Full docs at **[sepehrn0107.github.io/claude-code-toolkit](https://sepehrn0107.github.io/claude-code-toolkit/)**.

| | |
|---|---|
| [Getting Started](https://sepehrn0107.github.io/claude-code-toolkit/getting-started/install/) | Install, vault setup, first session |
| [User Guide](https://sepehrn0107.github.io/claude-code-toolkit/user-guide/memory/) | Memory, routing, standards, multi-project |
| [Skills Reference](https://sepehrn0107.github.io/claude-code-toolkit/skills/) | All skills with trigger phrases and purpose |
| [Standards Reference](https://sepehrn0107.github.io/claude-code-toolkit/standards/) | Universal and stack-specific standards |
| [Tools Reference](https://sepehrn0107.github.io/claude-code-toolkit/tools/) | Python tools: purpose and invocation |
| [Contributing](https://sepehrn0107.github.io/claude-code-toolkit/contributing/overview/) | Adding skills, standards, upgrade migrations |

---

## License

MIT
