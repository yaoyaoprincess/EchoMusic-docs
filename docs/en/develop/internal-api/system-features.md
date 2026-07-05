---
title: System Features Integration
outline: [2, 4]
---

# ⚙️ System Features Integration

Global shortcuts, power management, app updates, version info, logging system, audio effects resource management.

---

## Shortcuts (ctx.shortcuts)

| API | Description |
|-----|------|
| `register({ enabled, shortcutMap })` | Register shortcut mappings |
| `refresh()` | Refresh shortcut registrations |
| `onTrigger(fn)` | Listen for shortcut triggers, callback parameter is the command name |

```js
ctx.shortcuts.register({
  enabled: true,
  shortcutMap: {
    "toggle-visualizer": "Ctrl+Shift+V",
    "next-theme": "Ctrl+Shift+T",
  },
});
ctx.shortcuts.onTrigger((command) => {
  switch (command) {
    case "toggle-visualizer": /* ... */ break;
    case "next-theme": /* ... */ break;
  }
});
```

Key combinations are compatible with Electron accelerator syntax (`Ctrl+Shift+Key`, `CommandOrControl+Key`, etc.).

---

## Power Management (ctx.power)

| API | Description |
|-----|------|
| `onSuspend(fn)` | System is about to suspend, returns a cancel function |
| `onResume(fn)` | System woke from suspend, returns a cancel function |

```js
ctx.power.onSuspend(() => {
  // Save current state
});
ctx.power.onResume(() => {
  // Restore state
});
```

---

## Updater (ctx.updater)

Controls EchoMusic's automatic update flow.

| API | Description |
|-----|------|
| `download()` | Download the latest update |
| `install(silent?)` | Install the update (`silent=true` suppresses dialogs) |
| `onDownloadStatus(fn)` | Download progress listener, returns a cancel function |

```js
ctx.updater.onDownloadStatus((status) => {
  console.log(`Progress: ${status.percent}%`);
});
ctx.updater.download();
```

---

## App Info (ctx.appInfo)

| API | Description |
|-----|------|
| `get()` | Get version, platform, etc. `{ version, platform, arch, ... }` |
| `getChangelog()` | Get the changelog text |

---

## Logging System (ctx.logger / ctx.logging)

```js
// Structured logging (auto-prefixed with source)
ctx.logger.info("Operation succeeded");
ctx.logger.error("Processing failed", { details: "..." });
ctx.logger.warn("Deprecated API");
ctx.logger.debug("Debug info");
```

```js
// Log level settings
const settings = await ctx.logging.get();
await ctx.logging.update({ level: "debug" });  // debug | info | warn | error
```

---

## Audio Effects Management (ctx.audioEffects)

Manage IR impulse response audio effect files.

| API | Description |
|-----|------|
| `importImpulseResponse()` | Open file picker to import IR file |
| `deleteImpulseResponse(path)` | Delete an imported IR file |
| `reconcileImpulseResponses(files)` | Sync the IR file list |

---

## UI Component Injection (ctx.ui.addPlayerButton)

Add a custom button to the main player control bar.

```js
ctx.ui.addPlayerButton({
  id: "my-button",
  icon: "tabler:heart",
  label: "Favorite",
  onClick() { /* ... */ },
  order: 50,
});
```

> This API is an internal interface. Plugins use `ctx.ui.mount()` to mount into the player area for similar effects.

---

## 📂 Related Documents

- [Internal API Overview →](./) — Quick overview of the four modules
- [Audio Engine →](audio-engine) — Full mpv engine control
- [Playback State & Persistence →](playback-state) — Playback events & queue persistence
- [Window & Interaction Management →](window-management) — Window component management
