---
title: Plugin System
---

# 🧩 Plugin System Overview

EchoMusic supports a full plugin system starting from v2.2.6-beta.11. Plugins can extend the interface, add functionality, and customize the appearance — letting you build your own music experience.

## Plugin System Design

EchoMusic features a fully custom, deeply integrated plugin runtime built from scratch. Its design philosophy differs fundamentally from Chromium-based browser extensions — it is not compatible with Chrome extension specifications, sandbox isolation models, or permission manifest mechanisms.

### Maximum Extensibility

The plugin runtime is natively integrated with the main application without layered security sandbox isolation. The host fully exposes low-level interfaces including the audio kernel, local file system, database, window management, networking, and peripherals to plugins. Developers can leverage complete application capabilities to implement deep customizations such as audio source integration, UI redesign, real-time audio processing, system integration, and batch local media management — with no hard limits imposed by the framework.

### Security — User-Controlled

EchoMusic does not proactively restrict plugin operation permissions. Installation, enabling, disabling, uninstalling, and trust decisions are entirely at the user's discretion. Risks from third-party plugins are acknowledged and assumed by the user. The project does not enforce mandatory plugin review, fully delegating usage choices to the user.

### Built-in Safe Mode

To address issues like plugin crashes, malicious code, or logic errors that could freeze, crash, or corrupt the main application in a sandbox-free environment, the system includes Safe Mode (see [Management & Safety →](./manage#safe-mode) for details).

## What Are Plugins

Plugins are small code packages written by the community or yourself. They can:

- 📌 Register custom pages or sidebar entries
- 🎨 Inject custom CSS styles and modify the UI
- 🎵 Monitor player state and control playback
- 🖼️ Create desktop floating windows (e.g., taskbar lyrics, Dynamic Island)
- 📝 Provide custom lyrics content or lyric effects
- 🔍 Intercept audio source resolution for specific songs (e.g., WebDAV cloud music)
- ⚙️ Add settings panels
- 📋 Add options to track context menus
- 📊 Read audio spectrum data for visualizations

The plugin model is similar to VS Code / Obsidian's high-freedom local extensions: EchoMusic provides the host API, and plugins run freely.

## Quick Navigation

- [📥 Installing Plugins →](./install)
- [📋 Plugin List →](./list)
- [⚙️ Management & Safety →](./manage)
- [🔌 Plugin Development Guide →](/en/develop/plugin-dev/)
- [🐙 EchoMusic Plugin Repository →](https://github.com/hoowhoami/EchoMusicPlugins)
