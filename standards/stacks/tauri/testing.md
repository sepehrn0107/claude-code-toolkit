# Testing Standards — Tauri

## Two Test Surfaces

| Surface | Runner | What it covers |
|---------|--------|----------------|
| React frontend | Vitest + React Testing Library | Components, hooks, stores, command wrappers |
| Rust commands | `cargo test` | Command logic, service functions, state |

## Frontend Testing (Vitest)

All typescript-react testing standards apply. Tauri-specific additions:

### Mocking Tauri APIs

`@tauri-apps/api` calls must be mocked in every test — no real Tauri runtime is available in Vitest.

Set up a global mock in `src/test/setup.ts`:

```ts
// src/test/setup.ts
import { vi } from 'vitest'

vi.mock('@tauri-apps/api/core', () => ({
  invoke: vi.fn(),
}))

vi.mock('@tauri-apps/api/event', () => ({
  listen: vi.fn().mockResolvedValue(() => {}),
  emit: vi.fn(),
}))
```

Register in `vite.config.ts`:
```ts
test: {
  setupFiles: ['./src/test/setup.ts'],
  environment: 'jsdom',
}
```

### Testing Command Wrappers

```ts
// src/lib/commands/settings.test.ts
import { describe, it, expect, vi } from 'vitest'
import { invoke } from '@tauri-apps/api/core'
import { getSettings, saveSettings } from './settings'

vi.mock('@tauri-apps/api/core')

describe('getSettings', () => {
  it('calls invoke with the correct command name', async () => {
    vi.mocked(invoke).mockResolvedValue({ theme: 'dark', language: 'en' })

    const result = await getSettings()

    expect(invoke).toHaveBeenCalledWith('get_settings')
    expect(result.theme).toBe('dark')
  })
})
```

### Testing Zustand Stores

Reset store state between tests:

```ts
// src/stores/settings.store.test.ts
import { beforeEach, describe, it, expect } from 'vitest'
import { useSettingsStore } from './settings.store'
import { act, renderHook } from '@testing-library/react'

beforeEach(() => {
  useSettingsStore.setState({ theme: 'light', language: 'en' })
})

describe('useSettingsStore', () => {
  it('updates theme', () => {
    const { result } = renderHook(() => useSettingsStore())
    act(() => result.current.setTheme('dark'))
    expect(result.current.theme).toBe('dark')
  })
})
```

## Rust Testing (cargo test)

Test the business logic of commands, not the Tauri infrastructure. Keep command handlers thin so there is little to test in them directly — test the service functions they call.

```rust
// src-tauri/src/commands/settings.rs
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_settings_default_theme_is_light() {
        let settings = Settings::default();
        assert_eq!(settings.theme, "light");
    }
}
```

For async tests (tokio required):
```rust
#[tokio::test]
async fn test_save_settings_persists_theme() {
    let service = SettingsService::in_memory();
    let settings = Settings { theme: "dark".into(), language: "en".into() };
    service.save(settings.clone()).await.unwrap();
    let loaded = service.get().await.unwrap();
    assert_eq!(loaded.theme, settings.theme);
}
```

Rules:
- Test service functions, not Tauri plumbing
- Do not test that `tauri::State` works — that is Tauri's responsibility
- Use `#[cfg(test)]` modules or a `tests/` folder; both are fine
- Run `cargo test` in CI alongside frontend tests

## CI Integration

```yaml
# Example GitHub Actions step
- name: Run frontend tests
  run: pnpm test --run

- name: Run Rust tests
  working-directory: src-tauri
  run: cargo test
```

## Anti-Patterns

- Do not test that `invoke()` was called with specific arguments in component tests — test component behavior instead
- Do not import real Tauri API modules in tests without mocking them — they will throw
- Do not skip Rust tests because "it's just glue" — the command layer is a trust boundary and must be tested
