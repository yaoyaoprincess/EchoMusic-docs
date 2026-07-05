---
title: Internal API Reference
outline: [2, 4]
---

# 🔧 Internal API Reference

> ⚠️ **This documentation is for core development reference only.** The following APIs are EchoMusic main/renderer process internal interfaces, **not exposed to plugins**. For plugin development, please refer to [Plugin API Overview →](../plugin-dev/context-api).

EchoMusic's internal APIs cover core modules including the audio engine, window management, system integration, and playback state persistence. They are organized into four categories:

| Module | Description | Entry |
|------|------|:--:|
| 🎵 Audio Engine | mpv engine: EQ, spatial audio, IR convolution, device control, event listening | [→](audio-engine) |
| 📡 Playback State & Persistence | Playback events, queue persistence, local API server, HTTP request proxy | [→](playback-state) |
| 🖥️ Window & Interaction Management | Desktop lyrics, Mini Player, window control, system tray | [→](window-management) |
| ⚙️ System Features Integration | Shortcuts, power management, app updates, logging, audio effects management | [→](system-features) |

---

## Module Overview

### 🎵 Audio Engine (`ctx.audio`)

The complete operational surface for the underlying libmpv engine. 18-band parametric equalizer, spatial audio presets, IR impulse response convolution, audio device switching, volume fade, loudness normalization, MKV track selection, engine lifecycle management, and more.

### 📡 Playback State & Persistence (`ctx.events` / `ctx.storage` / `ctx.apiServer` / `ctx.api`)

Playback lifecycle events (track change / play-pause / volume change), persistent storage of the playback queue (restore on restart), local HTTP API server start/stop, main-process proxied HTTP client.

### 🖥️ Window & Interaction Management (`ctx.desktopLyric` / `ctx.miniPlayer` / `ctx.windowControl` / `ctx.tray`)

Show/hide/lock/click-through of the desktop lyrics overlay, expand/always-on-top/position control of the Mini Player window, minimize/maximize/fullscreen for the current window, system tray icon status synchronization.

### ⚙️ System Features Integration (`ctx.shortcuts` / `ctx.power` / `ctx.updater` / `ctx.appInfo` / `ctx.logger` / `ctx.audioEffects`)

Global shortcut registration and listening, system suspend/resume response, automatic app update download and install, version/platform info query, structured logging, IR impulse response file management.

---

## 📂 Related Documents

- [Plugin API Overview →](../plugin-dev/context-api) — Official APIs available to plugins
- [Project Architecture →](../architecture) — EchoMusic overall architecture
- [Project Structure →](../project-structure) — Complete directory structure
- [KuGou API Reference →](../api) — KuGou Music public API
