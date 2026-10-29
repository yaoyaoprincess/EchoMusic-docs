---
title: Window & Interaction Management
outline: [2, 4]
---

# 🖥️ Window & Interaction Management

Taskbar lyrics/progress/preview, network casting (DLNA / AirPlay), desktop lyrics, Mini Player, main window control, and system tray sync.

---

## The four Windows taskbar modules

Four main-process modules form the Windows taskbar integration, with native capabilities from `echo-platform-adaptor` (DWM thumbnails, `Shell_TrayWnd` child windows, UIA layout):

| Module | Function |
|--------|----------|
| `src/main/taskbarMediaBar.ts` | **Taskbar lyrics**: embeds a lyric window as a child of the primary taskbar, rendering scrolling lyrics and cover art in the taskbar's free space |
| `src/main/taskbarProgress.ts` | **Taskbar progress**: playback progress overlay on the taskbar icon (`TaskbarList` progress state) |
| `src/main/taskbarThumbnail.ts` | **DWM cover preview**: cover thumbnail and Aero Peek on taskbar hover (bitmap decoded in main, capped at 512px, delivered as premultiplied BGRA) |
| `src/main/thumbar.ts` | **Thumbnail toolbar buttons**: previous/play-pause/next buttons on the taskbar preview |

### Taskbar lyrics API (electron.taskbarLyric)

| API | Description |
|-----|-------------|
| `getState()` | `Promise<TaskbarLyricState>` current state |
| `setEnabled(enabled)` | Toggle taskbar lyrics |
| `setSettings(settings)` | Update settings (`position: 'auto'\|'left'\|'right'`, `maxWidth`, `fontSize`, `showCover`, `showTranslation`, `wordByWord`) |
| `setContentWidth(width)` | Report content width (drives native layout) |
| `showMain()` | Request showing the main window |
| `onStateChange(fn)` | State push subscription |

Implementation notes (see upstream `docs/taskbar-child-window-pitfalls.md` and `docs/taskbar-explorer-investigation.md`):

- The window is reparented into the primary taskbar `Shell_TrayWnd` after first paint, keeping the Electron window type and adding layered/tool-window/no-activate styles (`WS_EX_LAYERED` must be applied **after** `SetParent`, otherwise the renderer receives no mouse events at all);
- Win11 locates free taskbar intervals via UIA structure notifications + WinEvent; Win10 reserves and restores space in the native task list. Unknown, vertical, crowded and full-screen layouts hide the lyric child window;
- **Explorer restart recovery**: `WM_TASKBARCREATED` (`TaskbarCreated`) is observed to drop the old shell binding and re-embed; when Explorer restarts, the lyric HWND may receive `WM_NCDESTROY` without `WM_DESTROY` — the native layer's `window_lifecycle.rs` reinstates the missing destruction phase via a subclass, preventing Chromium's destructor CHECK crash; the main process rebuilds the window and session after `closed`;
- UIA suppression: `WM_GETOBJECT` from explorer returns 0, avoiding a cross-process UIA traversal hang of explorer.

---

## Network casting (electron.output)

Cast current playback to DLNA (UPnP) or AirPlay receiver devices.

| API | Description |
|-----|-------------|
| `listTargets()` | List discovered casting targets |
| `refresh()` | Rescan |
| `connect(targetId, pin?)` | Connect to a target (AirPlay supports a pairing PIN) |
| `disconnect()` | Disconnect the current session |
| `setEnabled(enabled)` | Toggle the casting feature (device discovery) |
| `setBrowsing(open)` | Open/close browsing (continuous discovery) |
| `setTrackMeta(meta)` | Sync track metadata `{ title?, artist?, album?, artwork?, durationMs?, mime?, headers? }` (artwork served by the media server) |
| `getSession()` | Current session state |
| `clearRecords()` | Clear connection records |
| `onEvent(fn)` | Session event subscription `{ type, payload? }` |

Architecture: `src/main/mediaTransport/` (`discovery.ts` device discovery, `dlnaAdapter.ts` DLNA adapter, `raopAdapter.ts` AirPlay/RAOP adapter, `mediaServer.ts` audio HTTP server, `genaReceiver.ts` UPnP event subscription, `didlLite.ts` DIDL-Lite metadata, `delivery.ts` delivery flow, `upnpClient.ts` echo-upnp wrapper) + `src/main/outputs/` (`outputHost.ts` ~75KB, the output session host; `sessionManager.ts`, `commandGate.ts`, `airplayBonjourDiagnostics.ts`, etc.). The native layer is `echo-upnp` (rupnp) and `echo-airplay` (ALAC 44.1kHz 16-bit from post-DSP i16 PCM) — see [Native Addons](/en/develop/native-addons).

---

## Now-playing snapshot (electron.nowPlaying)

The unified channel for the main window to broadcast playback state to desktop lyrics, mini player and other auxiliary windows:

| API | Description |
|-----|-------------|
| `getSnapshot()` | Read the current full snapshot |
| `syncSnapshot(payload)` | Main window pushes an incremental patch (`NowPlayingSnapshotPatch`) |
| `onSnapshot(fn)` | Auxiliary windows subscribe to full snapshots |
| `command(cmd)` / `invokeCommand(cmd)` | Send a playback command (async/sync variants) |
| `onCommand(fn)` | Auxiliary windows receive commands |

The snapshot is nested: `snapshot.playback` (`trackId`, `title`, `artist`, `album?`, `coverUrl?`, `duration`, `currentTime`, `isPlaying`, `isFavorite`, `isPersonalFM`, `playbackRate`, `clock?` etc.), `snapshot.lyric` (line-by-line lyrics, translation/romanization modes, offset), `snapshot.appearance` (dark mode, accent color, font family).

The command set is a superset of shortcut commands (`togglePlayback` / `nextTrack` / `toggleTranslation` / `lyricOffsetForward` ...), plus object commands `{ type: 'seek' | 'setVolume', value }` and `{ type: 'adjustVolume', delta }`.

---

## Desktop lyrics (electron.desktopLyric)

Controls the desktop lyrics floating window (a separate transparent window, main process `src/main/desktopLyric/`).

| API | Returns | Description |
|-----|---------|-------------|
| `getSnapshot()` / `getSessionNonce()` / `getWindow()` / `getHover()` | — | Read state, session nonce, window bounds, hover state |
| `show()` / `hide()` / `toggleLock()` | `Promise<Snapshot>` | Show / hide / toggle lock |
| `updateSettings(payload)` | `Promise<Snapshot>` | Update lyric settings |
| `updateWindow(bounds)` | — | Update window bounds |
| `startDrag(sessionId)` → `move(sessionId, x, y)` → `endDrag(sessionId)` | — | Drag session (idempotent token prevents cross-talk) |
| `startResize(sessionId)` → `resize(sessionId, bounds)` → `endResize(sessionId)` | — | Resize session |
| `cancelDrag(sessionId)` / `cancelResize(sessionId)` | — | Cancel drag/resize (returns rollback bounds) |
| `onCancelDrag(fn)` / `onCancelResize(fn)` | Unsubscribe | Notified when the main process force-cancels |
| `syncSnapshot(patch)` | `void` | Main window pushes lyric content patches |
| `onSnapshot(fn)` | Unsubscribe | Subscribe to snapshots |
| `setIgnoreMouseEvents(bool)` | `void` | Mouse click-through toggle |
| `setUnlockButtonBounds(rect \| null)` | `void` | Hit-test area of the unlock button in locked mode |
| `command(cmd)` | `void` | Send a command |

---

## Mini Player (electron.miniPlayer)

Controls the Mini Player window (the plugin-side wrapper `ctx.miniPlayer` is documented in [Plugin Windows & System Integration](/en/develop/plugin-dev/windows-system); this is a quick reference):

| API | Returns | Description |
|-----|---------|-------------|
| `getSnapshot()` / `show()` / `hide()` / `toggle()` | `Promise<Snapshot>` | Read state, show/hide/toggle |
| `setExpanded(bool)` / `setAlwaysOnTop(bool)` | `Promise<Snapshot>` | Expand / keep on top |
| `getBounds()` / `applyExpandBounds()` | — | Bounds / apply expanded bounds |
| `startDrag(sessionId)` → `move(x, y)` → `endDrag(sessionId)` / `cancelDrag(sessionId)` | — | Drag session |
| `syncSnapshot(patch)` / `onSnapshot(fn)` | — | Snapshot sync |
| `command(cmd)` / `onCommand(fn)` | — | Command channel |
| `notifyLyricVisibility(bool)` / `onLyricVisibility(fn)` | — | Lyric visibility coordination |

---

## Window control (electron.windowControl)

Controls the current window's state.

```js
electron.windowControl("minimize");   // Minimize
electron.windowControl("maximize");   // Maximize
electron.windowControl("close");      // Close
electron.windowControl("fullscreen"); // Fullscreen
```

> Only available in the main window and Mini Player.

---

## System tray (electron.tray)

| API | Description |
|-----|-------------|
| `syncPlayback(state)` | Sync playback state to the tray menu (`{ isPlaying?, playMode?, volume?, trackTitle?, trackArtist? }`) |
| `onSetPlayMode(fn)` | Listen for tray play-mode changes |

---

## 📂 Related Documents

- [Internal API Overview](/en/develop/internal-api/) — module map
- [Audio Engine](/en/develop/internal-api/audio-engine) — engine events and control
- [Playback State & Persistence](/en/develop/internal-api/playback-state) — queue persistence and API server
- [System Features](/en/develop/internal-api/system-features) — window composition and background materials
