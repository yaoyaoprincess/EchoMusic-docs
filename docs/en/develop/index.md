---
title: Development Guide
---

# 🛠️ Development Guide

Welcome to the EchoMusic development documentation. This section is for developers who want to contribute to the project or understand its internal implementation.

## Tech Stack

| Category | Technology |
|------|------|
| Desktop Framework | Electron 42.3 |
| Frontend Framework | Vue 3.5 + Composition API |
| Type System | TypeScript 5.9 |
| Build Tool | Vite 8 |
| State Management | Pinia + pinia-plugin-persistedstate |
| UI Component Library | Reka UI |
| CSS Framework | Tailwind CSS v4.3 |
| Routing | Vue Router |
| Package Manager | pnpm 9+ |
| Backend Service | Node.js (built-in local server, in-process invocation) |
| Audio Engine | echo-ffmpeg-player (embedded FFmpeg decoding + SoundTouch via Rust NAPI in-process) |
| Native Extensions | napi-rs (Rust → Node.js native modules) |
| Local Storage | SQLite (via echo-sqlite-store addon) |
| License | GPL v3.0 |

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
| `echo-ffmpeg-player` | FFmpeg + SoundTouch playback engine wrapper with fade, EQ, loudness normalization, speed control, device switching, exclusive output, real-time spectrum | Rust + FFmpeg |
| `echo-media-controls` | System media control integration (macOS / Windows / Linux native APIs) | Rust + OS API |
| `echo-sqlite-store` | SQLite local persistence for settings, playback queue, and state snapshots | Rust + rusqlite |

## Document Index

- [Architecture](/en/develop/architecture) — In-depth architecture design
- [Project Structure](/en/develop/project-structure) — Complete directory structure
- [Local Dev Setup](/en/develop/local-dev) — Set up your local development environment
- [Native Addons](/en/develop/native-addons) — Rust NAPI native extension development
- [Build & Package](/en/develop/build) — Multi-platform build packaging
- [Contributing](/en/develop/contributing) — How to contribute
- [Kugou API Reference](/en/develop/api) — Kugou Music public API documentation