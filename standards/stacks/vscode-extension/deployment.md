# VS Code Extension — Deployment Standards

## VSIX vs Extension Development Host

VS Code extensions run in one of two modes:

- **Extension Development Host** (`F5`): loads source directly from the workspace. Source changes take effect after reloading the host window. No packaging required.
- **Installed VSIX**: the extension is installed from a `.vsix` package into `~/.vscode/extensions/`. Source changes have **no effect** until the VSIX is rebuilt and reinstalled.

### Detecting which mode is active

Check `~/.vscode/extensions/` for a directory named `<publisher>.<extension-name>-<version>`. If it exists, the user is running the installed VSIX — not the dev source.

---

## Package and Install Workflow

Whenever an implementation plan includes a smoke test or manual verification step, add the following before "launch Extension Development Host":

```bash
# 1. Repackage
cd <project-root>
npx vsce package --no-dependencies

# 2. Reinstall
"/path/to/bin/code" --install-extension <name>-<version>.vsix
```

**Windows note:** `code --install-extension` only works via `bin/code`, not `Code.exe`. Full path:
```
C:\Users\<user>\AppData\Local\Programs\Microsoft VS Code\bin\code
```

Include this step explicitly in implementation plans — users will not see view or contribution point changes (new panels, commands, config settings) until the VSIX is reinstalled and the window is reloaded.

---

## Implementation Plan Checklist

Every VS Code extension plan should include a final task with these steps:

- [ ] `npx vsce package --no-dependencies`
- [ ] Install via `bin/code --install-extension <file>.vsix`
- [ ] Reload VS Code window (`Developer: Reload Window`)
- [ ] Verify contribution points (views, commands, settings) appear as expected

---

## Parallelism in Extension Plans

When declaring tasks as parallelizable, verify TypeScript import dependencies first:

- If Task B imports a type or class created by Task A, they are **sequential**, not parallel — the TypeScript compiler will fail if Task A's file doesn't exist when Task B compiles.
- Only tasks that touch completely independent files with no cross-imports can run in parallel.
