# Naming Conventions — Tauri

All typescript-react naming conventions apply. The additions below cover Tauri-specific concepts.

## Tauri Commands (Rust)

- Command functions: `snake_case` (Rust convention) — `get_user_profile`, `save_settings`
- Command file: `commands/` folder under `src-tauri/src/`, one file per domain — `commands/settings.rs`, `commands/files.rs`
- State types: `PascalCase` Rust structs — `AppState`, `DatabaseState`

```rust
// src-tauri/src/commands/settings.rs
#[tauri::command]
pub async fn get_settings(state: tauri::State<'_, AppState>) -> Result<Settings, String> {
    // ...
}
```

## Frontend Invoke Wrappers

On the TypeScript side, wrap every `invoke()` call in a typed function in a `src/lib/commands/` file. Never call `invoke()` directly from a component.

- Wrapper file: `src/lib/commands/<domain>.ts` — `src/lib/commands/settings.ts`
- Wrapper function: `camelCase` matching the Rust command — `getSettings`, `saveSettings`
- Return type: explicit TypeScript type, not inferred from `invoke<any>()`

```ts
// src/lib/commands/settings.ts
import { invoke } from '@tauri-apps/api/core'
import type { Settings } from '../types/settings'

export async function getSettings(): Promise<Settings> {
  return invoke<Settings>('get_settings')
}

export async function saveSettings(settings: Settings): Promise<void> {
  return invoke<void>('save_settings', { settings })
}
```

## Tauri Events

- Event names: `kebab-case` string literals, namespaced by domain — `'app:update-available'`, `'download:progress'`
- Event payload types: `PascalCase` interface — `UpdateAvailablePayload`, `DownloadProgressPayload`
- Event listener hooks: `use<EventName>` — `useUpdateAvailable`, `useDownloadProgress`

## Zustand Stores

- Store file: `src/stores/<domain>.store.ts` — `src/stores/settings.store.ts`
- Store hook: `use<Domain>Store` — `useSettingsStore`
- State interface: `<Domain>State` — `SettingsState`

```ts
// src/stores/settings.store.ts
interface SettingsState {
  theme: 'light' | 'dark'
  language: string
  setTheme: (theme: 'light' | 'dark') => void
}
```

## Files and Folders

```
src/                     # React/TypeScript frontend
  components/
  features/
  hooks/
  lib/
    commands/            # Typed invoke() wrappers — one file per Rust module
    events/              # Tauri event listener setup
  stores/                # Zustand stores
  types/                 # Shared TypeScript types (no Rust-generated code here)

src-tauri/
  src/
    commands/            # Rust command handlers — one file per domain
    state/               # Rust state types and initialization
    lib.rs               # App setup, plugin registration
    main.rs              # Entry point
  Cargo.toml
  tauri.conf.json
```

## Window and Menu Identifiers

- Window labels: `kebab-case` string — `'main'`, `'settings'`, `'splash'`
- Menu item IDs: `kebab-case` — `'file-open'`, `'edit-copy'`
