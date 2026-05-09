# Project Structure — Tauri

## Directory Layout

```
.
├── src/                        # React/TypeScript frontend (Vite root)
│   ├── App.tsx
│   ├── main.tsx
│   ├── components/             # Shared UI components
│   ├── features/               # Feature folders (see typescript-react/components.md)
│   │   └── settings/
│   │       ├── components/
│   │       ├── hooks/
│   │       └── index.ts
│   ├── hooks/                  # Shared hooks
│   ├── lib/
│   │   ├── commands/           # Typed invoke() wrappers — one file per Rust module
│   │   │   ├── settings.ts
│   │   │   └── files.ts
│   │   └── events/             # Tauri event listeners
│   │       └── updates.ts
│   ├── stores/                 # Zustand stores
│   │   └── settings.store.ts
│   └── types/                  # Shared TypeScript interfaces
│       └── settings.ts
├── src-tauri/
│   ├── src/
│   │   ├── commands/           # Tauri command handlers
│   │   │   ├── mod.rs
│   │   │   ├── settings.rs
│   │   │   └── files.rs
│   │   ├── state/              # AppState and initializers
│   │   │   └── mod.rs
│   │   ├── lib.rs              # tauri::Builder setup
│   │   └── main.rs
│   ├── Cargo.toml
│   ├── tauri.conf.json
│   └── capabilities/           # Tauri 2 permission declarations
│       └── default.json
├── vite.config.ts
├── package.json
└── tsconfig.json
```

## Frontend Architecture

Follow all `typescript-react` structural rules. Additional Tauri-specific rules:

- `src/lib/commands/` is the only place that imports `@tauri-apps/api` — never import Tauri APIs directly in components or hooks
- Feature folders may have a `hooks/use<Feature>Commands.ts` that composes multiple command wrappers into a single hook
- Stores hold UI-driven state only (e.g., current theme selection in the UI). Persisted preferences are written via a Tauri command to secure storage — not to `localStorage`

## Rust Module Layout

Organize Rust code by domain, registering all commands in `lib.rs`:

```rust
// src-tauri/src/lib.rs
mod commands;
mod state;

pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_store::Builder::default().build())
        .manage(state::AppState::new())
        .invoke_handler(tauri::generate_handler![
            commands::settings::get_settings,
            commands::settings::save_settings,
            commands::files::open_file,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application")
}
```

Register commands in `generate_handler![]` — this is the single source of truth for which Rust functions are exposed to the frontend.

## State Pattern

Use `tauri::State` for shared Rust state. Initialize state in `lib.rs` via `.manage()`.

```rust
// src-tauri/src/state/mod.rs
use std::sync::Mutex;

pub struct AppState {
    pub db: Mutex<Option<DatabaseConnection>>,
}

impl AppState {
    pub fn new() -> Self {
        AppState { db: Mutex::new(None) }
    }
}
```

## Build Artifacts

- Development: `pnpm tauri dev` — hot-reloads Vite + recompiles Rust on change
- Production: `pnpm tauri build` — bundles Vite output into Tauri, produces NSIS/MSI on Windows
- Never commit `target/` or `dist/` — add both to `.gitignore`
