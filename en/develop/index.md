---
title: Development Guide
---

# 🛠️ Development Guide

Welcome to the EchoMusic development documentation. This section is for developers who want to contribute to the project or understand its internal implementation.

## Tech Stack

| Category | Technology |
|------|------|
| Desktop Framework | Electron 42 |
| Frontend Framework | Vue 3 + Composition API |
| Type System | TypeScript 5.7 |
| Build Tool | Vite |
| State Management | Pinia + pinia-plugin-persistedstate |
| UI Component Library | Reka UI |
| CSS Framework | Tailwind CSS v4 |
| Routing | Vue Router |
| Package Manager | pnpm 9+ |
| Backend Service | Node.js (built-in local server, in-process invocation) |
| Audio Engine | libmpv (embedded via Rust NAPI addon in-process) |
| Native Extensions | napi-rs (Rust → Node.js native modules) |
| Local Storage | SQLite (via echo-storage addon) |
| License | MIT |

## Core Architecture

EchoMusic uses Electron's classic dual-process architecture with Rust NAPI native extensions for high-performance audio playback:

```
┌─────────────────────────────────────────┐
│              Electron Shell              │
│  ┌──────────────┐  ┌─────────────────┐  │
│  │  Main Process │  │ Renderer Process │  │
│  │  (Node.js)    │  │   (Vue 3 + Vite)│  │
│  │               │  │                  │  │
│  │  ┌─────────┐  │  │  ┌────────────┐  │  │
│  │  │ Server  │  │  │  │   Pinia    │  │  │
│  │  │ (API)   │◄─┼──┼─►│  (Store)   │  │  │
│  │  └─────────┘  │  │  └────────────┘  │  │
│  │  ┌─────────┐  │  │  ┌────────────┐  │  │
│  │  │ Native  │  │  │  │  Tailwind  │  │  │
│  │  │ Addons  │  │  │  │  CSS v4    │  │  │
│  │  │ (Rust)  │  │  │  └────────────┘  │  │
│  │  └─────────┘  │  │                  │  │
│  └──────────────┘  └─────────────────┘  │
└─────────────────────────────────────────┘
```

### Three Native Modules

| Module | Function | Technology |
|------|------|------|
| `echo-mpv-player` | libmpv playback engine wrapper | Rust + libmpv |
| `echo-media-controls` | System media control integration | Rust + OS API |
| `echo-storage` | SQLite local persistence | Rust + rusqlite |

## Document Index

- [Architecture](/en/develop/architecture) — In-depth architecture design
- [Project Structure](/en/develop/project-structure) — Complete directory structure
- [Local Dev Setup](/en/develop/local-dev) — Set up your local development environment
- [Native Addons](/en/develop/native-addons) — Rust NAPI native extension development
- [Build & Package](/en/develop/build) — Multi-platform build packaging
- [Contributing](/en/develop/contributing) — How to contribute
- [Kugou API Reference](/en/develop/api) — Kugou Music public API documentation