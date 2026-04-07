---
name: env-check
description: One-call dev environment snapshot — runtime versions, running Docker containers, listening ports, and .env file presence. Replaces 5+ separate shell commands.
---

# /env-check

Compact environment snapshot before running dev commands or at session start.

> `{{TOOLBOX_PATH}}` — resolved at install time from `~/.claude/toolbox-sections/vault-paths.md`

---

## When This Skill Triggers

Use when Claude needs to check any combination of:
- Installed language runtime versions (Python, Node, Go, git)
- Running Docker containers and their port mappings
- Which common dev ports are currently active
- Whether `.env` files exist in the current project directory

---

## How to Run

```bash
python {{TOOLBOX_PATH}}/tools/env-check/env_check.py
```

No options required. Always exits 0 — best-effort, never fails.

### Output format (stdout)

```
runtimes: python 3.11.5, node 20.10.0, git 2.42.0
docker: 3 containers running
  postgres (0.0.0.0:5432->5432/tcp)
  redis (0.0.0.0:6379->6379/tcp)
  crawl4ai (0.0.0.0:11235->11235/tcp)
ports: 3000 (Next.js/React), 5432 (PostgreSQL), 6379 (Redis), 11235 (Crawl4AI)
env files: .env, .env.local
```

| Stream | Meaning |
|--------|---------|
| **stdout** | Environment summary |
| **stderr** | Nothing — script never prints to stderr |
| **exit 0** | Always (best-effort) |

### Checked ports

`3000` Next.js/React · `3001` dev-alt · `4000/4200` dev/Angular · `5000` Flask · `5173` Vite · `5432` PostgreSQL · `6379` Redis · `8000` Django/FastAPI · `8080` proxy · `8888` Jupyter · `11235` Crawl4AI · `27017` MongoDB

---

## Replace These Patterns

Instead of:
```bash
python --version && node --version && git --version
docker ps
netstat -an | findstr LISTEN
ls .env*
```

Run the single script once.

---

## Example

```bash
python {{TOOLBOX_PATH}}/tools/env-check/env_check.py
```
