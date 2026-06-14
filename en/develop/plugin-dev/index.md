---
title: Plugin Development Overview
outline: [2, 4]
---

# 🔌 Plugin Development Overview

The EchoMusic plugin system provides a highly flexible local extension mechanism, similar in concept to the plugin architectures of VS Code or Obsidian. Plugins can customize the UI, extend functionality, process audio data, and deeply integrate with the player.

## Plugin System Architecture

### Overall Architecture

```
┌────────────────────────────────────────┐
│           EchoMusic Application         │
│  ┌──────────┐  ┌──────────┐            │
│  │Main Window│  │Mini Player│            │
│  │(Electron) │  │(Separate) │            │
│  ├──────────┤  ├──────────┤            │
│  │Plugin A   │  │Plugin A   │ ← if      │
│  │Plugin B   │  │           │  miniPlayer│
│  │Plugin C   │  │           │  enabled   │
│  └──────────┘  └──────────┘            │
│  ┌──────────┐                          │
│  │Desktop    │                         │
│  │Lyrics     │                          │
│  │(Separate) │                          │
│  ├──────────┤                          │
│  │Plugin A   │ ← if desktopLyric       │
│  │           │   enabled               │
│  └──────────┘                          │
│       ▲                                │
│       │ ctx injection                  │
│       │                                │
│  ┌────┴─────┐                          │
│  │Plugin     │ Load / Unload /         │
│  │Manager    │ Lifecycle               │
│  └──────────┘                          │
└────────────────────────────────────────┘
```

### Multi-Window Model

EchoMusic has three independent renderer windows, **each with separate JS memory**:

| Window | Description | Plugin Participation |
|--------|-------------|:--:|
| **Main Window** | Full player UI, settings, plugin management, etc. | All enabled plugins loaded by default |
| **Mini Player** | Compact mini player window | Requires `runtime.miniPlayer: true` in manifest |
| **Desktop Lyric** | Floating desktop lyrics window | Requires `runtime.desktopLyric: true` in manifest |

> If your plugin only operates on the main window (e.g., adding settings panels or registering pages), you don't need to enable miniPlayer or desktopLyric.

### Plugin Lifecycle

```
  [User Enables Plugin]
       │
       ▼
  ┌─────────────┐     ┌──────────────────┐
  │ Load manifest│ ──▶ │ Validate version / │
  │              │     │ capabilities      │
  └─────────────┘     └──────┬───────────┘
                             │
                    ┌────────▼──────────┐
                    │ Version mismatch?  │
                    │ → Show "Incompatible│
                    │   version"          │
                    │ Block activation    │
                    └────────┬──────────┘
                             │ Pass
                    ┌────────▼──────────┐
                    │ Load entry JS (ESM)│
                    │ Inject ctx object  │
                    └────────┬──────────┘
                             │
                    ┌────────▼──────────┐
                    │ activate(ctx)      │
                    │ Plugin registers   │
                    │ resources          │
                    └────────┬──────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
       Normal operation  Disable/Uninstall  Crash/Error
              │              │              │
              │       ┌──────▼──────┐       │
              │       │deactivate() │       │
              │       │Auto cleanup │       │
              │       │ctx.dispose()│       │
              │       └──────┴──────┘       │
              │                             │
              └──────────────┬──────────────┘
                             │
                    ┌────────▼──────────┐
                    │ Plugin stopped      │
                    │ Directory removed   │
                    │ on uninstall        │
                    │ KV data & error logs│
                    │ cleared             │
                    └───────────────────┘
```

## Security Model

### Trust Boundary

- Plugins are **user-enabled** local code running in the Electron renderer process
- EchoMusic does not sandbox plugins — they can access all renderer process APIs
- Therefore, **only enable plugins from trusted sources**

### Capabilities

Plugin access to sensitive APIs uses an **explicit declaration** mechanism. After declaring the required capability in the manifest, the corresponding `ctx` APIs become available:

| Capability | API Access Granted |
|------------|-------------------|
| `audioSource` | `ctx.player.audioSource.register()` — Take over audio source resolution |
| `audioSpectrum` | `ctx.audio.spectrum` — Read/subscribe to audio spectrum |
| `kugouApi` | `ctx.kugou` — Call Kugou Music API |
| `localFiles` | `ctx.fs` — Scan/read local files |
| `lyricEffects` | `ctx.lyricEffects.register()` — Register lyric visual effects |
| `lyrics` | `ctx.lyrics.registerResolver()` — Provide custom lyrics |
| `process` | `ctx.process.launch()` — Launch native programs |

> Follow the **principle of least privilege**: only declare capabilities your plugin actually needs.

## Development Environment Requirements

- **Node.js**: 18+ recommended
- **Runtime**: Browser ESM (Node.js built-in modules like `fs`, `path` are unavailable)
- **Vue dependency**: Use `ctx.vue`, **do not** use bare imports (e.g. `import { ref } from 'vue'`)
- **Build tools (optional)**: Use Vite / esbuild to bundle TypeScript or Vue SFC into a single ESM file

## Documentation Navigation

| Document | Audience | Content |
|----------|:--:|------|
| [Getting Started →](./getting-started) | Beginners | Build your first plugin from scratch |
| [Manifest Reference →](./manifest) | Everyone | Complete manifest.json field reference |
| [Context API Reference →](./context-api) | Everyone | Complete `ctx` API listing |
| [UI Extension Guide →](./ui-extension) | Frontend Devs | Pages, settings panels, context menus, component injection |
| [Player & Audio →](./player-audio) | Audio Devs | Playback control, audio spectrum, lyrics system |
| [File Storage & Events →](./filesystem-events) | Advanced Devs | Local files, KV storage, event listeners, appearance |
| [Publishing & Distribution →](./publishing) | Plugin Authors | Plugin registry, versioning, packaging & release |

---

- [EchoMusicPlugins Repository →](https://github.com/hoowhoami/EchoMusicPlugins)
- [User Guide: Plugin System →](/guide/plugins)
