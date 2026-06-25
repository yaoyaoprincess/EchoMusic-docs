---
title: Windows & System
outline: [2, 4]
---

# 🪟 Windows & System

This document covers how plugins control EchoMusic's various windows and access system-level APIs.

---

## Floating Windows

Floating windows declared in `contributes.windows` can be programmatically controlled via `ctx.window`.

### API

| API | Description |
|-----|------|
| `ctx.window.show(pluginId, windowId, options?)` | Show a floating window |
| `ctx.window.hide(pluginId, windowId)` | Hide a floating window |
| `ctx.window.getContext()` | Get current floating window context (only available inside the floating window) |

```js
// Show floating window
ctx.window.show("my-plugin", "my-float", {
  width: 400,
  height: 300,
});

// Hide floating window
ctx.window.hide("my-plugin", "my-float");
```

| Parameter | Type | Description |
|------|------|------|
| `pluginId` | `string` | Plugin ID (`ctx.manifest.id`) |
| `windowId` | `string` | Window `id` declared in manifest |
| `options` | `object` | Optional, overrides default dimensions in manifest |

---

## Desktop Lyric

`ctx.desktopLyric` provides full control over the desktop lyric floating window.

### State Query & Control

| API | Returns | Description |
|-----|------|------|
| `getSnapshot()` | `Promise<DesktopLyricSnapshot>` | Get current lyric state snapshot |
| `show()` | `Promise<DesktopLyricSnapshot>` | Show desktop lyric |
| `hide()` | `Promise<DesktopLyricSnapshot>` | Hide desktop lyric |
| `toggleLock()` | `Promise<DesktopLyricSnapshot>` | Toggle lock state |
| `updateSettings(settings)` | `Promise<DesktopLyricSnapshot>` | Update lyric settings |
| `command(cmd)` | `void` | Send command (e.g., adjust font size) |
| `setIgnoreMouseEvents(ignore)` | `void` | Mouse passthrough toggle (`true` = clicks pass through) |

### Subscribing to Lyric State

```js
ctx.desktopLyric.onSnapshot((snapshot) => {
  console.log("Lyric state:", snapshot);
  // { visible, locked, lines, currentLine, ... }
});
```

Returns a cancellation function, auto-cancelled on plugin disable.

### Syncing State

```js
ctx.desktopLyric.syncSnapshot({
  locked: true,
  // ... other fields to sync
});
```

---

## Mini Player

`ctx.miniPlayer` controls the mini player window.

### State Query & Control

| API | Returns | Description |
|-----|------|------|
| `getSnapshot()` | `Promise<MiniPlayerSnapshot>` | Get current state |
| `show()` / `hide()` / `toggle()` | `Promise<MiniPlayerSnapshot>` | Show/hide/toggle |
| `setExpanded(bool)` | `Promise<MiniPlayerSnapshot>` | Expand/collapse |
| `setAlwaysOnTop(bool)` | `Promise<MiniPlayerSnapshot>` | Always on top toggle |
| `getBounds()` | `Promise<{x,y,width,height}>` | Get window position and size |
| `move(x, y)` | `void` | Move window to coordinates |
| `applyExpandBounds()` | `Promise<MiniPlayerSnapshot>` | Apply expanded dimensions |
| `command(cmd)` | `void` | Send command |
| `notifyLyricVisibility(bool)` | `void` | Notify lyric visibility |

### Subscriptions

```js
// State changes
ctx.miniPlayer.onSnapshot((snapshot) => {
  console.log("Mini player state:", snapshot);
});

// Command listener
ctx.miniPlayer.onCommand((cmd) => {
  console.log("Received command:", cmd);
});

// Lyric visibility changes
ctx.miniPlayer.onLyricVisibility((visible) => {
  console.log("Lyric visible:", visible);
});
```

---

## Now Playing

`ctx.nowPlaying` operates the now-playing info floating window.

| API | Description |
|-----|------|
| `getSnapshot()` | Get current state snapshot |
| `syncSnapshot(patch)` | Sync state |
| `command(cmd)` | Send command |
| `onSnapshot(fn)` | Subscribe to state changes |
| `onCommand(fn)` | Subscribe to commands |

```js
// Listen for lyric display state
ctx.nowPlaying.onSnapshot((snapshot) => {
  console.log("Now Playing:", snapshot.title, snapshot.artist);
});

// Send command
ctx.nowPlaying.command("toggleLyrics");
```

---

## Shortcuts

`ctx.shortcuts` allows plugins to register and manage global keyboard shortcuts.

| API | Description |
|-----|------|
| `register({ enabled, shortcutMap })` | Register shortcut mappings |
| `refresh()` | Refresh shortcut registrations (for re-binding after updates) |
| `onTrigger(fn)` | Listen for shortcut triggers, callback receives command name |

```js
// Register shortcuts
ctx.shortcuts.register({
  enabled: true,
  shortcutMap: {
    "toggle-visualizer": "Ctrl+Shift+V",
    "next-theme": "Ctrl+Shift+T",
  },
});

// Listen for triggers
ctx.shortcuts.onTrigger((command) => {
  switch (command) {
    case "toggle-visualizer":
      toggleVisualizer();
      break;
    case "next-theme":
      cycleTheme();
      break;
  }
});
```

| Field | Type | Description |
|------|------|------|
| `enabled` | `boolean` | Whether shortcuts are enabled |
| `shortcutMap` | `Record<string, string>` | Command name → key combination |

Key combination format: `Ctrl+Shift+Key`, `Alt+Key`, `CommandOrControl+Key`, etc., compatible with Electron accelerator syntax.

---

## Window Control

`ctx.windowControl` operates on the current window.

```js
ctx.windowControl("minimize");   // Minimize
ctx.windowControl("maximize");   // Maximize
ctx.windowControl("close");      // Close
ctx.windowControl("fullscreen"); // Fullscreen
```

> Only available in the main window and Mini player, not in floating windows.

---

## System Tray

`ctx.tray` interacts with the system tray.

```js
// Sync playback state to tray icon
ctx.tray.syncPlayback({
  isPlaying: true,
  playMode: "loop",
  volume: 80,
});

// Listen for tray play mode changes
ctx.tray.onSetPlayMode((playMode) => {
  console.log("Play mode changed to:", playMode);
});
```

---

## Power Events

`ctx.power` responds to system suspend/resume.

| API | Description |
|-----|------|
| `onSuspend(fn)` | Callback when system is about to suspend, returns cancellation function |
| `onResume(fn)` | Callback when system resumes from suspend, returns cancellation function |

```js
ctx.power.onSuspend(() => {
  console.log("System suspending, saving state...");
  ctx.storage.kvSet("lastState", getCurrentState());
});

ctx.power.onResume(() => {
  console.log("System resumed");
  // Restore UI
});
```

---

## Process Management

> Requires capability: `process: true`

`ctx.process` allows plugins to launch and terminate native executables.

| API | Description |
|-----|------|
| `launch(options)` | Launch an executable within the plugin directory |
| `terminate()` | Terminate the launched process |

```js
// Launch executable
const result = await ctx.process.launch({
  command: "tools/my-helper.exe",
  args: ["--port", "12345"],
  env: { CUSTOM_VAR: "value" },
  cwd: "tools/",
});

// Terminate later
ctx.process.terminate();
```

| Parameter | Type | Required | Description |
|------|------|:--:|------|
| `command` | `string` | ✅ | Executable path (relative to plugin directory) |
| `args` | `string[]` | ❌ | Command-line arguments |
| `env` | `Record<string, string>` | ❌ | Additional environment variables |
| `cwd` | `string` | ❌ | Working directory (relative path) |

> ⚠️ The executable path must be **relative to the plugin directory** — arbitrary system paths are not allowed.

---

## App Icons

`ctx.icons` manages application window and taskbar icons.

| API | Description |
|-----|------|
| `refresh()` | Refresh all icon caches (re-read icon files) |
| `setRuntimeWindowIcon(iconPath)` | Set runtime window icon (plugin directory path) |
| `restoreDefaultWindowIcon()` | Restore EchoMusic default window icon |
| `restoreDefaultDesktopIcon()` | Restore default desktop icon |
| `restoreDefaultTaskbarIcon()` | Restore default taskbar icon |

```js
// Switch to custom window icon
ctx.icons.setRuntimeWindowIcon("icons/alt-icon.png");

// Restore default
ctx.icons.restoreDefaultWindowIcon();
```

---

## App Info

`ctx.appInfo` retrieves EchoMusic application information.

| API | Description |
|-----|------|
| `get()` | Get version, platform, etc. |
| `getChangelog()` | Get changelog text |

```js
const info = await ctx.appInfo.get();
// { version: "2.2.7", platform: "win32", arch: "x64", ... }

const changelog = await ctx.appInfo.getChangelog();
```

---

## Updater

`ctx.updater` controls EchoMusic's auto-update flow.

| API | Description |
|-----|------|
| `download()` | Download latest update |
| `install(silent?)` | Install downloaded update (`silent=true` suppresses dialog) |
| `onDownloadStatus(fn)` | Download progress listener, returns cancellation function |

```js
ctx.updater.onDownloadStatus((status) => {
  console.log(`Download progress: ${status.percent}%`);
  if (status.complete) {
    ctx.toast.info("Update downloaded, restart to apply");
  }
});

// Manually trigger download
ctx.updater.download();
```

---

## API Server

`ctx.apiServer` controls EchoMusic's built-in local API service.

| API | Description |
|-----|------|
| `start()` | Start local HTTP API service |
| `status()` | Get service running status |

```js
const { running, port } = await ctx.apiServer.status();
if (!running) {
  await ctx.apiServer.start();
}
```

---

## Fonts

`ctx.fonts` retrieves available system fonts.

```js
const fonts = await ctx.fonts.getAll();
// ["Microsoft YaHei", "SimSun", "Arial", ...]
```

---

## Audio Effects Management

`ctx.audioEffects` manages impulse response (IR) audio effect files.

| API | Description |
|-----|------|
| `importImpulseResponse()` | Open file picker to import IR audio file |
| `deleteImpulseResponse(filePath)` | Delete an imported IR file |
| `reconcileImpulseResponses(files)` | Sync IR file list |

---

## Logging

`ctx.logging` and `ctx.logger` provide logging capabilities.

```js
// Structured logging (auto-prefixed with plugin ID)
ctx.logger.info("User performed an action");
ctx.logger.error("Processing failed", { details: "..." });
ctx.logger.warn("API about to be deprecated");

// Log settings
const settings = await ctx.logging.get();
await ctx.logging.update({ level: "debug" });
```

---

## Cross-Window Communication (BroadcastChannel)

EchoMusic provides `BroadcastChannel` for cross-window communication (main window ↔ Mini player ↔ desktop lyric).

```js
// Plugin in main window
const channel = new BroadcastChannel("my-plugin-channel");
channel.postMessage({ type: "sync", data: {...} });

// Same plugin in Mini player (if runtime.miniPlayer: true)
const channel = new BroadcastChannel("my-plugin-channel");
channel.onmessage = (event) => {
  console.log("Received sync message:", event.data);
};
```

> Channel name should be prefixed with the plugin ID to avoid conflicts with other plugins.

---

## Next Steps

| Document | Content |
|------|------|
| [Player & Audio Engine →](./player-audio) | Playback controls, EQ, spatial audio, IR convolution |
| [Audio Spectrum →](./audio-spectrum) | Real-time spectrum data subscription and visualization |
| [Filesystem & Storage →](./filesystem-storage) | FS, KV storage, playback queue |
| [API Reference →](./context-api) | Complete ctx API listing |
