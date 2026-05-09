## Standards

Before writing or editing any code, standards must be loaded. Three modes:

- **Orchestrating via `/implement`**: read only `{{TOOLBOX_PATH}}/standards/universal/DIGEST.md`
  (the compact 1-page reference). Full standards are loaded by sub-agents per phase.
  Do not read all 9 standards files into the main session.
- **Direct one-off edits**: invoke `{{TOOLBOX_PATH}}/skills/load-standards.md` — it will
  auto-detect the task category and load only the relevant subset of standards.
- **Pre-PR / standards-check**: loads all 9 standards (full mode).
