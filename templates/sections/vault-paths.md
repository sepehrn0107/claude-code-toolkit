## Spec & Plan Output Paths

When writing specs (brainstorming output) or implementation plans (writing-plans output), always use the vault paths below — these override the default `docs/superpowers/` paths specified in the superpowers plugin.

- **Specs** → `{{VAULT_PATH}}/02-projects/<active-project>/specs/YYYY-MM-DD-<topic>-design.md`
- **Plans** → `{{VAULT_PATH}}/02-projects/<active-project>/plans/YYYY-MM-DD-<topic>.md`

If no project is active, use `{{VAULT_PATH}}/02-projects/toolbox/` as the fallback location.

These paths are rendered at install time. Do not read a config file — use the literal paths above.
