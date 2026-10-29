---
title: Development Guide
---

# 🛠️ Development Guide

Welcome to the EchoMusic development documentation. This section is for developers who want to contribute to the project or understand its internal implementation.

## Tech Stack

| Category | Technology |
|------|------|
| Desktop Framework | Electron 43.7 |
| Frontend Framework | Vue 3.5 + Composition API |
| Type System | TypeScript 5.9 |
| Build Tool | Vite 8 |
| State Management | Pinia 4 + custom SQLite persistence plugin (`sqlitePersist`) |
| UI Component Library | Reka UI |
| CSS Framework | Tailwind CSS v4.3 (integrated via the `@tailwindcss/vite` plugin) |
| Routing | Vue Router |
| Package Manager | pnpm 9+ (workspace includes the `server` submodule) |
| Backend Service | Node.js (KuGouMusicApi loaded in-process as a git submodule, accessed over IPC) |
| Audio Engine | echo-audio-player (vendored FFmpeg decoding + SoundTouch, embedded in-process via Rust NAPI) |
| Native Extensions | napi-rs (Rust → Node.js native modules) |
| Local Storage | SQLite (via echo-sqlite-store addon) |
| License | GPL-3.0-only |

## Core Architecture

EchoMusic uses Electron's dual-process architecture with Rust NAPI native extensions for high-performance audio playback. The renderer communicates with the main process directly over IPC, and the Kugou API service is loaded in-process as a submodule without any standalone HTTP port:

```
┌──────────────────────────────────────────────────┐
│                  Electron Shell                   │
│  ┌────────────────┐    ┌───────────────────────┐ │
│  │  Main Process  │IPC │   Renderer Process    │ │
│  │  (Node.js)     │◄──►│     (Vue 3 + Vite)    │ │
│  │                │    │                       │ │
│  │  ┌──────────┐  │    │  ┌─────────────────┐  │ │
│  │  │ KuGou API│  │    │  │      Pinia      │  │ │
│  │  │(submodule│  │    │  │  25+ Stores +   │  │ │
│  │  │in-process│  │    │  │ sqlitePersist   │  │ │
│  │  │   load)  │  │    │  └─────────────────┘  │ │
│  │  └──────────┘  │    │  ┌─────────────────┐  │ │
│  │  ┌──────────┐  │    │  │   Tailwind v4   │  │ │
│  │  │  Native  │  │    │  └─────────────────┘  │ │
│  │  │  Addons  │  │    │                       │ │
│  │  │  (Rust)  │  │    │                       │ │
│  │  └──────────┘  │    │                       │ │
│  └────────────────┘    └───────────────────────┘ │
└──────────────────────────────────────────────────┘
```

### Native Modules Overview

EchoMusic ships 9 Rust native modules: 8 are distributed with the installers, and 1 is an internal dependency only:

| Module | Function | Distributed On |
|------|------|----------|
| `echo-audio-player` | Playback, decoding, and audio effect processing (FFmpeg + SoundTouch) | macOS / Windows / Linux |
| `echo-audio-capture` | System audio and microphone capture (song recognition) | macOS / Windows / Linux |
| `echo-media-controls` | System media controls (SMTC / MPRIS / MPNowPlayingInfoCenter) | macOS / Windows / Linux |
| `echo-sqlite-store` | SQLite persistence | macOS / Windows / Linux |
| `echo-opencc` | Lyric Simplified/Traditional Chinese conversion | macOS / Windows / Linux |
| `echo-upnp` | DLNA / UPnP device control | macOS / Windows / Linux |
| `echo-airplay` | AirPlay device discovery and audio streaming | macOS / Windows / Linux |
| `echo-platform-adaptor` | Platform adaptation (system windows, taskbar, etc.) | macOS / Windows (not needed on Linux) |
| `echo-native-log` (internal) | Native logging, depended on by other crates, not distributed with installers | — |

See [Local Dev Setup](/en/develop/local-dev) for how to build the modules, and [Native Addons](/en/develop/native-addons) for module APIs and implementation details.

## Technical Highlights

| Feature | Description |
|------|------|
| Audio Engine | Vendored FFmpeg + SoundTouch, embedded in-process via Rust NAPI with zero-latency direct function calls; no system FFmpeg required |
| Audio Quality | Hi-Res, SQ(flac), HQ(320kbps), Standard(128kbps) |
| Audio Effects | Built-in cross-platform effects engine: 10-band EQ (with full-range pre-compensation), LUFS loudness normalization, WAV/IRS spatial audio, plus compatible DSP Provider and community effect imports |
| Playback Formats | Standard audio + LRC/YRC word-by-word lyrics parsing |
| Network Casting | DLNA / UPnP and AirPlay device discovery and casting, preserving the local playback queue |
| Plugin System | Online plugin marketplace browsing/installing and local plugin loading; plugin floating windows run in a separate window process |
| Platform Output | macOS (dmg/zip), Windows (nsis, x64/arm64), Linux (AppImage/deb/pacman/rpm/tar.gz) |

## Document Index

- [Architecture](/en/develop/architecture) — In-depth architecture design
- [Project Structure](/en/develop/project-structure) — Complete directory structure
- [Local Dev Setup](/en/develop/local-dev) — Set up your local development environment
- [Native Addons](/en/develop/native-addons) — Rust NAPI native extension development
- [Build & Package](/en/develop/build) — Multi-platform build packaging
- [Contributing](/en/develop/contributing) — How to contribute
- [Kugou API Reference](/en/develop/kugou-api) — Kugou Music public API documentation
- [Internal API Reference](/en/develop/internal-api/) — Main app internal APIs (FFmpeg engine, desktop lyrics, etc.)
