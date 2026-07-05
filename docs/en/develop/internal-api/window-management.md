---
title: Window & Interaction Management
outline: [2, 4]
---

# 🖥️ Window & Interaction Management

Desktop lyrics overlay, Mini Player, main window control, system tray status synchronization.

---

## Desktop Lyrics (ctx.desktopLyric)

Control the desktop lyrics overlay window.

| API | Returns | Description |
|-----|------|------|
| `getSnapshot()` | `Promise<Snapshot>` | Get current lyrics state |
| `show()` / `hide()` | `Promise<Snapshot>` | Show / hide |
| `toggleLock()` | `Promise<Snapshot>` | Toggle lock state |
| `updateSettings(s)` | `Promise<Snapshot>` | Update lyrics settings |
| `onSnapshot(fn)` | Cancel function | Subscribe to state changes |
| `command(cmd)` | `void` | Send a command |
| `setIgnoreMouseEvents(bool)` | `void` | Toggle click-through |

```js
ctx.desktopLyric.show();
ctx.desktopLyric.onSnapshot((snap) => {
  console.log("Lyrics visible:", snap.visible, "Locked:", snap.locked);
});
```

---

## Mini Player (ctx.miniPlayer)

Control the Mini Player window.

| API | Returns | Description |
|-----|------|------|
| `getSnapshot()` | `Promise<Snapshot>` | Get current state |
| `show()` / `hide()` / `toggle()` | `Promise<Snapshot>` | Show / hide / toggle |
| `setExpanded(bool)` | `Promise<Snapshot>` | Expand / collapse |
| `setAlwaysOnTop(bool)` | `Promise<Snapshot>` | Toggle always-on-top |
| `getBounds()` | `Promise<{x,y,w,h}>` | Window position and size |
| `move(x, y)` | `void` | Move the window |
| `applyExpandBounds()` | `Promise<Snapshot>` | Apply expanded bounds |
| `onSnapshot(fn)` | Cancel function | Subscribe to state |
| `onCommand(fn)` | Cancel function | Listen for commands |
| `notifyLyricVisibility(bool)` | `void` | Notify lyric visibility |
| `onLyricVisibility(fn)` | Cancel function | Lyric visibility change |
| `command(cmd)` | `void` | Send a command |

```js
ctx.miniPlayer.show();
ctx.miniPlayer.setAlwaysOnTop(true);
ctx.miniPlayer.setExpanded(true);
```

---

## Window Control (ctx.windowControl)

Manipulate the window state of the current window.

```js
ctx.windowControl("minimize");   // Minimize
ctx.windowControl("maximize");   // Maximize
ctx.windowControl("close");      // Close
ctx.windowControl("fullscreen"); // Fullscreen
```

> Only available in the main window and Mini Player.

---

## System Tray (ctx.tray)

| API | Description |
|-----|------|
| `syncPlayback(state)` | Sync playback state to the tray (`{ isPlaying, playMode, volume }`) |
| `onSetPlayMode(fn)` | Listen for tray play mode switch |

---

## 📂 Related Documents

- [Internal API Overview →](./) — Quick overview of the four modules
- [Audio Engine →](audio-engine) — Full mpv engine control
- [Playback State & Persistence →](playback-state) — Playback events & queue persistence
- [System Features Integration →](system-features) — Shortcuts, updates, logging, etc.
