---
title: Internal API Reference
outline: [2, 4]
---

# 🔧 Internal API Reference

> ⚠️ **This documentation is for core development reference only.** The following APIs are EchoMusic main/renderer process internal interfaces, **not exposed to plugins** (plugins get a restricted subset). For plugin development, see the [Plugin API Overview](/en/develop/plugin-dev/context-api).

EchoMusic's internal APIs are exposed as `window.electron` by the single `contextBridge.exposeInMainWorld('electron', ...)` call in the preload script `src/preload/index.ts`, covering 25+ API groups across the audio engine, window management, system integration and persistence. They are organized into four categories:

| Module | Description | Entry |
|--------|-------------|:--:|
| 🎵 Audio Engine | Rust engine: loading/gapless source switching, track transitions, EQ, effects & DSP providers, audio graph, devices, events | [→](/en/develop/internal-api/audio-engine) |
| 📡 Playback State & Persistence | Multi-queue storage, history, key-value, settings backup, API server, HTTP request proxy | [→](/en/develop/internal-api/playback-state) |
| 🖥️ Window & Interaction Management | Taskbar quartet, network casting (DLNA/AirPlay), desktop lyrics, Mini Player, window control, tray | [→](/en/develop/internal-api/window-management) |
| ⚙️ System Features Integration | Shortcuts, power, network settings, updates, logging & diagnostics, effect files, window composition, etc. | [→](/en/develop/internal-api/system-features) |

---

## API group map

All API groups actually exposed on `window.electron` (plus top-level fields `platform`, `isWayland`, `notifyPageMounted()` and the launch-argument-injected `echoInitialDark` / `echoWindowBackground`):

### Groups with dedicated pages

| API group | One-line description | Docs |
|-----------|----------------------|:--:|
| `player` | Full audio engine control: loading/source switching, transitions, EQ, effects, devices, events | [Audio Engine](/en/develop/internal-api/audio-engine) |
| `storage` | Playback snapshot / multi-queue / history / key-value persistence | [Playback State & Persistence](/en/develop/internal-api/playback-state) |
| `apiServer` | In-process KuGou API host (`start` / `status` / `identity`) | [Playback State & Persistence](/en/develop/internal-api/playback-state) |
| `settingsBackup` | Settings & data backup export/inspect/import | [Playback State & Persistence](/en/develop/internal-api/playback-state) |
| `desktopLyric` | Desktop lyrics floating window (incl. drag/resize sessions) | [Window & Interaction Management](/en/develop/internal-api/window-management) |
| `nowPlaying` | Now-playing snapshot sync and command channel | [Window & Interaction Management](/en/develop/internal-api/window-management) |
| `taskbarLyric` | Windows taskbar lyrics (state/settings/width) | [Window & Interaction Management](/en/develop/internal-api/window-management) |
| `miniPlayer` | Mini Player floating window | [Window & Interaction Management](/en/develop/internal-api/window-management) |
| `windowControl` | Minimize/maximize/close/fullscreen for the current window | [Window & Interaction Management](/en/develop/internal-api/window-management) |
| `output` | Network casting (DLNA / AirPlay target discovery and sessions) | [Window & Interaction Management](/en/develop/internal-api/window-management) |
| `tray` | Tray playback state sync and play mode | [Window & Interaction Management](/en/develop/internal-api/window-management) |
| `shortcuts` | In-app and plugin global shortcuts | [System Features](/en/develop/internal-api/system-features) |
| `power` | Resume notification and sleep timer actions | [System Features](/en/develop/internal-api/system-features) |
| `network` | Proxy settings (5 modes) | [System Features](/en/develop/internal-api/system-features) |
| `updater` | App update download/cancel/install/state | [System Features](/en/develop/internal-api/system-features) |
| `appInfo` | Version info, changelog, relaunch, open settings | [System Features](/en/develop/internal-api/system-features) |
| `log` / `logging` | Structured logging and log settings | [System Features](/en/develop/internal-api/system-features) |
| `diagnostics` | Memory and process diagnostic snapshots | [System Features](/en/develop/internal-api/system-features) |
| `audioEffects` | Effect resource import/download/delete/reconcile | [System Features](/en/develop/internal-api/system-features) |

### Groups summarized on this page

| API group | One-line description |
|-----------|----------------------|
| `ipcRenderer` | Restricted `send` / `invoke` / `on` / `off` passthrough (payloads uniformly sanitized for serialization); generally not used directly |
| `api` | Main-process proxied HTTP client `api.request(config)`, supports binary body passthrough |
| `cloud` | Cloud-drive upload file picking and reading (`pickUploadFiles` / `readUploadFileData` / `clearUploadFiles`) |
| `share` | Text copy, clipboard read, region screenshot (`captureRectToClipboard`) and share-target open |
| `fonts` | System font enumeration (`getAll()`) |
| `opencc` | Batch Chinese script conversion for lyrics `convertBatch(texts, profile)` (5 profiles, powered by echo-opencc) |
| `recognize` | Song recognition capture (device enumeration/start/stop/cancel, powered by echo-audio-capture; PCM uploaded through the `api.request` binary channel) |
| `audioSpectrum` | Engine spectrum subscription (`getStatus` / `getSnapshot` / `subscribe(options, fn)`, returns a handle) |
| `external` | External playlist/link resolution `resolvePlaylist(req)` (KuGou/NetEase/QQ/Qishui/Spotify/Apple Music etc.) |
| `mediaControls` | System media control sync (metadata/state/timeline/skip intervals, powered by SMTC / MPRIS / MPNowPlayingInfoCenter) |
| `plugins` | Full plugin-system interface (install/marketplace/files/network/database/windows/backups) — **has its own docs**, see the [Plugin API Overview](/en/develop/plugin-dev/context-api) |

> The marketplace's anonymous statistics reporting (aggregate install counts etc.) is collected by the main process `src/main/plugins/marketplaceStats.ts`; see [Marketplace Stats Reporting](/en/develop/plugin-dev/marketplace-stats).

---

## 📂 Related Documents

- [Plugin API Overview](/en/develop/plugin-dev/context-api) — the official API available to plugins
- [Architecture](/en/develop/architecture) — overall EchoMusic architecture
- [Project Structure](/en/develop/project-structure) — full directory structure
- [Native Addons](/en/develop/native-addons) — Rust NAPI native extensions
- [Kugou API Reference](/en/develop/kugou-api) — Kugou Music public API
