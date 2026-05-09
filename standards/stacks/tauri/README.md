# Tauri Standards

Standards for desktop applications using Tauri 2 with a React/TypeScript frontend and Rust backend. Windows-first.

## Stack Profile

- **Framework**: [Tauri 2](https://v2.tauri.app/) — Rust backend + Vite/React frontend
- **Frontend**: TypeScript + React (extends typescript-react standards)
- **State**: Zustand (React UI state) + Rust state via Tauri commands/events
- **Styling**: Tailwind CSS
- **Build**: Vite + Cargo, bundled by Tauri CLI
- **Testing**: Vitest (frontend), `cargo test` (Rust commands)

## Base Stack

This stack extends `typescript-react`. All typescript-react standards apply unless overridden here.
See `_base.md`.

## Files in This Directory

| File | Topic |
|------|-------|
| `README.md` | This file — stack overview and file index |
| `_base.md` | Base stack declaration |
| `naming.md` | Naming conventions for commands, events, stores, files |
| `structure.md` | Project layout — React src, Rust src-tauri separation |
| `commands.md` | Tauri command patterns, IPC contracts, security rules |
| `testing.md` | Frontend Vitest patterns + Rust cargo test patterns |

## Non-Goals

These standards do not cover:
- Mobile targets (Tauri Mobile is out of scope for this stack)
- Custom Tauri plugins authored from scratch
- Rust non-command code (complex Rust modules; follow Rust idioms)
