---
title: System Features Integration
outline: [2, 4]
---

# ⚙️ System Features Integration

Shortcuts, power management, network settings, app updates, logging & diagnostics, effect resource management, window composition, the download engine, local music scanning, and other main-process capabilities.

---

## Shortcuts (electron.shortcuts)

| API | Description |
|-----|-------------|
| `register({ enabled, shortcutMap })` | Register in-app shortcut mapping (`ShortcutRegistrationResult`) |
| `refresh()` | Re-apply the current registration |
| `setLocalEditableActive(active)` | Notify the main process of editable-input state (in-app shortcuts yield while editing text) |
| `registerPluginGlobal(payload)` | Register a **plugin global** shortcut (system-wide, works while the app is in the background) |
| `unregisterPluginGlobal({ pluginId, registrationId })` | Unregister a plugin global shortcut |
| `onTrigger(fn)` | In-app shortcut triggered (callback receives the command name) |
| `onPluginGlobalTrigger(fn)` | Plugin global shortcut triggered (callback includes `pluginId` / `registrationId`) |

```js
electron.shortcuts.register({
  enabled: true,
  shortcutMap: { "toggle-visualizer": "Ctrl+Shift+V" },
});
electron.shortcuts.onTrigger((command) => { /* ... */ });
```

Key combinations follow Electron accelerator syntax (`Ctrl+Shift+Key`, `CommandOrControl+Key`, etc.). Plugin global shortcuts are exposed to plugins via `ctx.shortcuts` — see [Plugin Shortcuts](/en/develop/plugin-dev/context-api).

---

## Power management (electron.power)

| API | Description |
|-----|-------------|
| `onResume(fn)` | System resumed from sleep, returns an unsubscribe function |
| `executeSleepTimerAction(action)` | Execute a sleep timer action (any of `"pause" \| "quit" \| "shutdown"` except `"pause"`), returns `{ ok } \| { ok: false, error }` |

> ⚠️ `onSuspend` from older revisions **does not exist**: the renderer only receives the `power:resume` broadcast. Pre-suspend handling lives entirely in the main process.

Main-process `src/main/powerMonitor.ts` responsibilities:

- **suspend**: pause playback if playing (so the audio output idles cleanly) and release the power-save-blocker;
- **resume**: restore network sessions (re-apply proxy), rebuild the audio output device, resume playback when appropriate, and broadcast `power:resume` so the renderer re-enumerates devices;
- On Windows, `unlock-screen` is only a fallback for a "suspend confirmed but resume lost" case; a normal lock-screen unlock never interrupts playback.

The sleep timer (main process `sleepTimer`) lands its `pause` / `quit` / `shutdown` actions via `executeSleepTimerAction` when it fires.

---

## Scheduled shutdown (systemShutdown.ts)

Main-process module; `requestSystemShutdown()` invokes a fixed per-platform command (no shell, no sudo, no force-closing applications):

| Platform | Command |
|----------|---------|
| macOS | `/usr/bin/osascript -e 'tell application "System Events" to shut down'` |
| Windows | `shutdown.exe /s /t 0` |
| Linux | `/usr/bin/systemctl poweroff` |

---

## Network settings (electron.network)

| API | Description |
|-----|-------------|
| `get()` | `Promise<NetworkSettingsState>` current network settings |
| `update(request)` | Update settings (including sensitive fields such as the password, `NetworkSettingsUpdateRequest`) |

Five proxy modes (`NetworkProxyMode` in `src/shared/network.ts`): `'system'` (follow the system), `'direct'`, `'auto_detect'`, `'pac_script'`, and `'fixed_servers'` (fixed proxy rules with bypass list and authentication).

Main-process `src/main/networkSettings.ts` + `src/main/networkPolicy.ts` apply the proxy **uniformly across**: KuGou API requests, cover/image fetches, direct audio links, app updates (electron-updater), and plugin network requests. Sessions are partitioned by purpose (`echo-app-network` / `echo-kugou-api` / `echo-community-audio` / `persist:desktop-lyric` / `electron-updater`), each with the proxy and credentials applied; the engine-level streaming proxy is additionally pushed to `echo-audio-player` via `set_http_proxy(s)` (see [Audio Engine](audio-engine)). Post-wake network recovery also happens at this layer (see Power management).

---

## Updater (electron.updater)

| API | Description |
|-----|-------------|
| `download()` | Start downloading the latest update |
| `cancelDownload()` | Cancel the download |
| `install(silent?)` | Install the update (`silent=true` skips prompts) |
| `getState()` | `Promise<UpdateState>` current update state |
| `onDownloadStatus(fn)` | Download progress listener, returns an unsubscribe function |

---

## App info (electron.appInfo)

| API | Description |
|-----|-------------|
| `get()` | Version, platform, architecture, etc. `{ version, platform, arch, ... }` |
| `getChangelog()` | Changelog text |
| `relaunch()` | Relaunch the app (returns whether it was accepted) |
| `onOpenSettings(fn)` | Main process requests opening the settings page (optionally with a section), returns an unsubscribe function |

---

## Logging & diagnostics (electron.log / electron.logging / electron.diagnostics)

```js
// Structured logging (electron-log renderer wrapper)
electron.log.info("Operation succeeded");
electron.log.error("Processing failed", { details: "..." });
```

| API | Description |
|-----|-------------|
| `logging.get()` / `logging.update(settings)` | Log settings (level etc., `LogSettings`) |
| `diagnostics.getMemory(label?)` | Memory diagnostic snapshot: renderer memory (working set/private/heap), `performance.memory`, `webFrame` resource usage, all app process metrics |

Main-process counterparts: `src/main/eventLoopMonitor.ts` (event-loop blocking detection) and `src/main/diagnostics/` (`memory.ts` process memory sampling). Native logs are bridged into the unified log stream via echo-native-log (see [Native Addons](/en/develop/native-addons)).

---

## Audio effects management (electron.audioEffects)

Manages IRS / VPF effect resource files (activation goes through `player.setAudioEffect`, see [Audio Engine](audio-engine)):

| API | Description |
|-----|-------------|
| `importImpulseResponse()` | Open a file picker to import an effect file (`ImportImpulseResponseResult`) |
| `downloadCommunityAudioEffect(payload)` | Download a community effect (`DownloadCommunityAudioEffectRequest/Result`) |
| `deleteAudioEffect(filePath)` | Delete an effect file |
| `reconcileAudioEffects(files)` | Reconcile effect files against the renderer-side list (clean orphans, return survivors) |

> ⚠️ `deleteImpulseResponse` / `reconcileImpulseResponses` from older revisions **do not exist**; the actual names are `deleteAudioEffect` / `reconcileAudioEffects`.

---

## Window composition & backgrounds (main process)

Cross-platform window background/composition strategy; no direct preload API, triggered indirectly from the settings page via IPC:

| Module | Platform | Description |
|--------|----------|-------------|
| `src/main/window/windowsComposition.ts` | Windows | DWM transparent / Accent acrylic composition (coordinated with `echo-platform-adaptor`, covering Win11 22H2+ `setBackgroundMaterial` and Win10 Accent modes) |
| `src/main/window/backgroundMaterial.ts` | Windows | Electron `setBackgroundMaterial` wrapper |
| `src/main/window/hyprlandBackground.ts` (+ `hyprlandBlurQueue.ts`) | Linux | Hyprland compositor window blur (layer-shell protocol, queue-based to avoid flicker) |
| `src/main/window/macComposition.ts` | macOS | macOS vibrancy/transparent background |
| `src/main/windowDrag.ts` / `windowSizing.ts` | All | Custom titlebar dragging and window size constraints |
| `src/main/windowBoundsPersistence.ts` | All | Window bounds persistence |
| `src/main/windowBackgroundThrottling.ts` | All | Background window throttling control |

Failed transparency falls back to a solid background; diagnostics can be copied in one click from the Windows appearance settings (Accent/DWM backdrop/layered-style readback).

---

## Other main-process capabilities

| Module | Description |
|--------|-------------|
| `src/main/macBackgroundMode.ts` | macOS background running: hide the Dock (`app.dock.hide()`) and menu bar per close preferences, tray visibility coordination, restore on quit |
| `src/main/downloads/engine.ts` (+ `files.ts`) | Download engine: song/file download tasks, progress and disk writes |
| `src/main/localMusic.ts` + `src/main/media/fileScanner.ts` + `src/main/media/audioMetadata.ts` | Local music: directory scanning, deduplication, embedded metadata (tags/cover) parsing |
| `src/main/avatarUpload.ts` | Avatar upload (file reading and size validation) |
| `src/main/plugins/index.ts` etc. | Plugin runtime and **safe mode**: `plugins.setSafeMode(enabled)`; the app can start with `--safe-mode` to disable all plugins (failure recovery) — see [Plugin System](/en/develop/plugin-dev/getting-started) |
| `src/main/share.ts` / `src/main/ipc/cloud.ts` | Clipboard/screenshot sharing, cloud-drive file picking and reading (`electron.share` / `electron.cloud`) |
| `src/main/opencc/` + `src/main/ipc/opencc.ts` | Chinese script conversion for lyrics (`electron.opencc.convertBatch`, powered by echo-opencc) |
| `src/main/audioCapture.ts` + `src/main/ipc/recognize.ts` | Song recognition capture (`electron.recognize.*`, powered by echo-audio-capture) |
| `src/main/audioSpectrum.ts` | Audio spectrum subscription dispatch (`electron.audioSpectrum.*`, engine spectrum) |
| `src/main/external/index.ts` | External playlist/link resolution (`electron.external.resolvePlaylist`, KuGou/NetEase/QQ/Qishui/Spotify/Apple providers) |

---

## 📂 Related Documents

- [Internal API Overview](/en/develop/internal-api/) — module map
- [Audio Engine](/en/develop/internal-api/audio-engine) — effect activation path and engine networking
- [Playback State & Persistence](/en/develop/internal-api/playback-state) — settings backup and API server
- [Window & Interaction Management](/en/develop/internal-api/window-management) — taskbar integration and window control
- [Native Addons](/en/develop/native-addons) — echo-platform-adaptor platform integration
