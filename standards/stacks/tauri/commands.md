# Tauri Commands & IPC Standards

## The Core Rule

All system-level work (filesystem, OS APIs, native dialogs, secure storage, network) goes in Rust commands. The React frontend only calls `invoke()` via typed wrappers. Never access the OS directly from JavaScript.

```
React component
  → lib/commands/<domain>.ts (TypeScript invoke wrapper)
    → Rust command (tauri::command)
      → OS / filesystem / DB
```

## Writing Rust Commands

Annotate with `#[tauri::command]` and return `Result<T, String>`. Keep commands thin — they call service functions, they do not contain business logic.

```rust
// src-tauri/src/commands/settings.rs
use crate::state::AppState;
use serde::{Deserialize, Serialize};
use tauri::State;

#[derive(Serialize, Deserialize)]
pub struct Settings {
    pub theme: String,
    pub language: String,
}

#[tauri::command]
pub async fn get_settings(state: State<'_, AppState>) -> Result<Settings, String> {
    state.settings_service.get()
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn save_settings(
    settings: Settings,
    state: State<'_, AppState>,
) -> Result<(), String> {
    state.settings_service.save(settings)
        .map_err(|e| e.to_string())
}
```

Rules:
- Return `Result<T, String>` — the `String` becomes the rejection reason on the frontend
- Use `serde::Serialize` + `serde::Deserialize` on all types that cross the IPC boundary
- Do not `panic!` inside commands — map errors to `String` with `.map_err(|e| e.to_string())`
- State is accessed via `tauri::State<'_, T>` — never use global statics

## Writing TypeScript Wrappers

Every Rust command gets exactly one TypeScript wrapper in `src/lib/commands/<domain>.ts`.

```ts
// src/lib/commands/settings.ts
import { invoke } from '@tauri-apps/api/core'

export interface Settings {
  theme: 'light' | 'dark'
  language: string
}

export async function getSettings(): Promise<Settings> {
  return invoke<Settings>('get_settings')
}

export async function saveSettings(settings: Settings): Promise<void> {
  return invoke<void>('save_settings', { settings })
}
```

Rules:
- Parameter names in `invoke()` must exactly match Rust function parameter names (Tauri serializes by name)
- Always provide the generic type parameter to `invoke<T>()` — never `invoke<any>()`
- Never call `invoke()` from React components or hooks directly — always go through `lib/commands/`
- Export types alongside wrappers so consumers get the full contract in one import

## Tauri Events

Use Tauri events for Rust → React push notifications (progress updates, background task completion, system events).

```rust
// Rust: emit from a command or background task
app_handle.emit("download:progress", ProgressPayload { percent: 50, bytes_done: 1024 }).ok();
```

```ts
// src/lib/events/download.ts
import { listen } from '@tauri-apps/api/event'

export interface ProgressPayload {
  percent: number
  bytesDone: number
}

export function onDownloadProgress(handler: (payload: ProgressPayload) => void) {
  return listen<ProgressPayload>('download:progress', (event) => handler(event.payload))
}
```

```ts
// React hook
export function useDownloadProgress(onProgress: (p: ProgressPayload) => void) {
  useEffect(() => {
    const unlisten = onDownloadProgress(onProgress)
    return () => { unlisten.then(fn => fn()) }
  }, [onProgress])
}
```

## Permissions (Tauri 2 Capabilities)

Declare only the permissions your app needs. Tauri 2 uses a capability-based permission model — default deny, explicit allow.

```json
// src-tauri/capabilities/default.json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "default",
  "description": "Default app capabilities",
  "windows": ["main"],
  "permissions": [
    "core:default",
    "dialog:allow-open",
    "fs:allow-read-text-file",
    "store:allow-get",
    "store:allow-set"
  ]
}
```

Rules:
- Never grant `fs:allow-read-dir` or broader filesystem permissions unless strictly necessary
- Never expose raw filesystem paths to the frontend — use Tauri path APIs (`appDataDir`, `documentsDir`) in Rust
- Do not use `shell:allow-execute` unless there is no Tauri plugin alternative

## Secure Storage

Use `tauri-plugin-store` for persisted user preferences. Use the OS keychain (via `tauri-plugin-stronghold` or OS credential APIs) for secrets (tokens, passwords).

```ts
// Preferences (non-secret) via plugin-store
import { load } from '@tauri-apps/plugin-store'

const store = await load('settings.json', { autoSave: false })
await store.set('theme', 'dark')
await store.save()
```

Never store secrets in `localStorage`, `sessionStorage`, or plain files.

## Security Rules

- Never pass unsanitized user input directly to a Rust command that runs shell commands or constructs file paths
- Never pass a filesystem path from the frontend to a command — compute the path in Rust using Tauri path APIs
- Keep the CSP restrictive: `"dangerousDisableAssetCspModification": false` in `tauri.conf.json`
- Signed releases via GitHub Actions — do not distribute unsigned binaries

## Anti-Patterns

- Do not put business logic inside Tauri command handlers — call a service/module function
- Do not use `window.__TAURI__` directly — use `@tauri-apps/api` imports
- Do not call `invoke()` in component render functions synchronously — all invoke calls are async and belong in event handlers or `useEffect`
- Do not `unwrap()` or `expect()` in release Rust code — map errors explicitly
