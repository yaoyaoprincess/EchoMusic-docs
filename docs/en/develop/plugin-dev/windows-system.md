---
title: Windows & System
outline: [2, 4]
---

# 🪟 Windows & System

This document covers how plugins control EchoMusic's various windows and access system-level APIs.

> ℹ️ Tray, power, updater, logging, and similar APIs are internal and out of scope for plugins. The mini player and desktop lyric are open to plugins — see [Mini Player](#mini-player) and [Desktop Lyric](#desktop-lyric) below.

---

## Floating Window Management

Floating windows declared in `contributes.windows` can be controlled programmatically via `ctx.windows`. **Every method takes the floating window's `windowId` as its first argument** (the `contributes.windows[].id` from the manifest) — a plugin may declare multiple windows and control any of its own windows this way (never another plugin's windows).

| API | Description |
|-----|------|
| `ctx.windows.show(windowId, options?)` | Show the window (created on first use); returns `{ ok, window, bounds }` |
| `ctx.windows.hide(windowId)` | Hide the window |
| `ctx.windows.close(windowId)` | Close the window |
| `ctx.windows.move(windowId, bounds)` | Move/resize, `bounds` is `{ x?, y?, width?, height? }` |
| `ctx.windows.getBounds(windowId)` | Get position and size `{ x, y, width, height }` |
| `ctx.windows.setIgnoreMouseEvents(windowId, ignore)` | Toggle click-through |
| `ctx.windows.showOnTop(windowId, options?)` | Raise the window to the front once (does not change always-on-top) |

```js
// Show the floating window (optionally overriding manifest defaults)
await ctx.windows.show("island", {
  width: 420,
  height: 72,
  x: 100,
  y: 0,
  alwaysOnTop: true,
  allowOutsideWorkArea: true,
});

// Hide / close
await ctx.windows.hide("island");
await ctx.windows.close("island");

// Move and resize
await ctx.windows.move("island", { x: 100, y: 200, width: 360, height: 64 });

// Read position and size
const result = await ctx.windows.getBounds("island");
if (result.ok) console.log(result.bounds);

// Click-through (a locked lyric strip)
await ctx.windows.setIgnoreMouseEvents("island", true);
```

`show()` options:

| Option | Type | Description |
|------|------|------|
| `width` / `height` | `number` | Override the display size (still clamped by manifest `min*/max*` and the display bounds) |
| `x` / `y` | `number` | Override the position |
| `alwaysOnTop` | `boolean` | Toggle always-on-top at runtime (on macOS the host rebuilds the window when the window type must change) |
| `allowOutsideWorkArea` | `boolean` | Allow the full display bounds (can sit over the taskbar area) |

Manifest fields for floating windows (`type`, `transparent`, `rememberBounds`, `position`, etc.) are covered in the [Manifest Reference](./manifest#contributeswindows).

### Drag & Resize (windows.drag / windows.resize)

In the main plugin entry, binding a floating window's drag/resize session to a DOM element **inside the main window** is uncommon; these APIs mostly serve low-level integrations. The usual approach is `ctx.window.drag.bind(element)` inside the floating window entry (see "Floating window context" below).

```js
// Low-level session APIs (windowId is explicit)
await ctx.windows.drag.start("island", sessionId);
ctx.windows.drag.move("island", sessionId, screenX, screenY);
await ctx.windows.drag.end("island", sessionId);
await ctx.windows.drag.cancel("island", sessionId);

// You can also bind main-window elements as drag/resize handles
const stopDrag = ctx.windows.drag.bind("island", titlebarElement);
const stopResize = ctx.windows.resize.bind("panel", handleElement, {
  direction: "se",           // n / ne / e / se / s / sw / w / nw
  minWidth: 240,
  minHeight: 120,
});
```

`bind()` returns a dispose function; when the manifest sets `resizable: false`, the host rejects resize sessions.

### Raising to the front (showOnTop)

```js
await ctx.windows.showOnTop("island");                  // take focus and activate
await ctx.windows.showOnTop("island", { focus: false }); // raise without stealing focus
```

`showOnTop()` raises the window to the front once but **does not change its always-on-top state**: a hidden window is shown first, a minimized one restored, then the level is raised. Use it for one-shot "summon/focus" actions.

---

## Floating Window Context

The floating window entry (the script pointed to by `contributes.windows[].main`) runs in a separate Electron window. Export `activateWindow(ctx)` / `activate(ctx)` or a default function and the host calls it. **It is not a reuse of the main plugin context**: there is no `ctx.ui`, `ctx.player`, `ctx.playlist`, etc. — only the subset needed to render the window.

```js
// island.js — floating window entry
export function activateWindow(ctx) {
  const { h, createApp, ref, onMounted } = ctx.vue;

  const App = {
    setup() {
      const text = ref("EchoMusic");
      const update = (snapshot) => {
        text.value = snapshot?.lyric?.lines[snapshot?.lyric?.currentIndex ?? -1]?.text
          || snapshot?.playback?.title
          || "EchoMusic";
      };
      onMounted(async () => {
        update(await ctx.nowPlaying.getSnapshot());
        ctx.nowPlaying.onSnapshot(update);
      });
      return () => h("div", { class: "island" }, text.value);
    },
  };

  createApp(App).mount(ctx.container);
}
```

### Context members

| Member | Description |
|------|------|
| `id` / `pluginId` / `windowId` | Plugin and window identifiers |
| `manifest` / `descriptor` / `windowDescriptor` | Plugin and window descriptors |
| `vue` / `icons` / `container` | Vue namespace, Iconify icon set, mount container |
| `nowPlaying` | Now-playing snapshot API (same as main entry) |
| `fonts` / `cover` | System fonts, themed icon covers |
| `audio.spectrum` | Spectrum subset (`getStatus` / `getSnapshot` / `subscribe(options, handler)`; requires the `audioSpectrum` capability) |
| `storage` | `get` / `set` / `delete`, sharing the plugin's data with the main entry |
| `backups` | Backups API (consume only; cannot register backup providers) |
| `fs` | File API subset (`listFiles` / `listImageFiles` / `getFileUrl` / `readTextFile` / `readFileBytes` / `readAudioMetadata`) |
| `process` | `launch` / `terminate` (requires the `process` capability) |
| `net` / `webServer` / `sqlite` | Native network requests, local web server, SQLite (same capability requirements as the main entry) |
| `css` | `inject(cssText, { id? })`; styles are removed automatically when the window is destroyed |
| `electron` | Full preload bridge (advanced use) |
| `dispose(fn)` | Register a cleanup function, invoked when the window is destroyed |

### Controlling the current window (ctx.window)

Inside the floating window context, `ctx.window` **only controls the current floating window**, so no `windowId` parameter is needed:

| API | Description |
|-----|------|
| `getBounds()` | Get the current window position and size |
| `move(bounds)` | Move/resize the current window |
| `drag.bind(element)` | Bind an element as the drag region (recommended; handles pointer capture, cancellation, focus loss, and multi-monitor DPI automatically) |
| `drag.start/move/end/cancel(sessionId)` | Low-level drag session |
| `resize.bind(element, options?)` | Bind an element as a resize handle; `options` accepts `direction` / `minWidth` / `minHeight` / `maxWidth` / `maxHeight` |
| `resize.start/resize/end/cancel(sessionId, ...)` | Low-level resize session |
| `onCancelInteraction(listener)` | Subscribe to the host cancelling the current drag/resize session (e.g. the window is being closed); the callback receives the rolled-back bounds |
| `hide()` / `close()` | Hide / close the current window |
| `setIgnoreMouseEvents(ignore)` | Toggle click-through |
| `setAlwaysOnTop(alwaysOnTop)` | Toggle always-on-top (persist the state in your own storage before calling) |
| `showOnTop(options?)` | Raise to the front once; `options.focus` defaults to `true` |

```js
// Typical self-dragging titlebar inside a floating window
export function activateWindow(ctx) {
  const titlebar = ctx.container.querySelector(".titlebar");
  const disposeDrag = ctx.window.drag.bind(titlebar);
  ctx.dispose(disposeDrag);

  ctx.window.onCancelInteraction((bounds) => {
    // The host has already rolled the native window back; only clear renderer state here
  });
}
```

### Raising host windows (ctx.host)

Both the main entry and the floating window entry provide `ctx.host.showOnTop(target?, options?)` to raise a **host window** to the front (without changing always-on-top):

```js
await ctx.host.showOnTop();                     // same as 'main', brings up the main window
await ctx.host.showOnTop("mini-player");        // bring up the mini player (returns ok: false when not open)
await ctx.host.showOnTop("main", { focus: false });
```

`target` is `'main' | 'mini-player'`, default `'main'`; `options.focus` defaults to `true`.

---

## Now Playing Snapshot

`ctx.nowPlaying` reads and subscribes to the "now playing" playback, lyric, and appearance state. Available in both the main plugin entry and the floating window entry.

| API | Description |
|-----|------|
| `getSnapshot()` | Get the current snapshot `{ playback, lyric, appearance, updatedAt }` |
| `onSnapshot(fn)` | Subscribe to snapshot changes; returns a dispose function |
| `command(cmd)` | Send a playback/lyric command (fire-and-forget) |
| `invokeCommand(cmd)` | Same as `command`, but resolves after the main process confirms delivery |

```js
// Subscribe to playback and lyric state
ctx.nowPlaying.onSnapshot((snapshot) => {
  console.log("Now Playing:", snapshot.playback?.title, snapshot.appearance?.accentColor);
});

// Commands: string commands + object commands
ctx.nowPlaying.command("togglePlayback");
ctx.nowPlaying.command("toggleTranslation");
ctx.nowPlaying.command({ type: "seek", value: 42 });        // seek to a position in seconds
ctx.nowPlaying.command({ type: "setVolume", value: 35 });   // absolute volume 0-100
ctx.nowPlaying.command({ type: "adjustVolume", delta: -10 }); // relative volume
```

`playback.currentTime` is the playback engine's most recently pushed discrete position; time-sensitive scenarios such as lyric scrolling should interpolate progress locally using `playback.updatedAt` and `playback.playbackRate`. See the official floating-window documentation for full snapshot types.

---

## Mini Player

`ctx.miniPlayer` controls EchoMusic's mini player window.

> Only plugins that declare `runtime.miniPlayer: true` run an entry script inside the mini player; controlling the mini player window itself only needs the API below.

| API | Description |
|-----|------|
| `getSnapshot()` | Get the snapshot `{ playback, appearance?, window?, queue?, lyric? }` |
| `show()` / `hide()` / `toggle()` | Show / hide / toggle the mini player |
| `setExpanded(expanded)` | Expand or collapse (expanded shows the play queue) |
| `setAlwaysOnTop(alwaysOnTop)` | Toggle always-on-top |
| `getBounds()` | Get the window position and size |
| `seek(value)` | Seek to a playback position (seconds) |
| `setVolume(value, requestId?)` | Set volume 0–100; `requestId` can correlate slider requests to avoid UI jitter |
| `adjustVolume(delta)` | Adjust volume relatively (clamped to 0–100) |
| `onSnapshot(fn)` | Subscribe to snapshot changes; returns a dispose function |
| `command(cmd)` | Send a mini player command |

```js
await ctx.miniPlayer.show();
await ctx.miniPlayer.setExpanded(true);
ctx.miniPlayer.onSnapshot((snapshot) => {
  console.log("Mini playing:", snapshot.playback?.title, "volume:", snapshot.playback?.volume);
});
```

`playback` carries track info, progress, volume, and favorite state; `appearance` carries dark mode, accent color, and mini lyric styling; `window` carries always-on-top and expand direction; `queue` / `lyric` provide queue and lyric data. `command` supports `togglePlayback` / `previousTrack` / `nextTrack` / `toggleFavorite` / `toggleMute` / `toggleDesktopLyric` / `showMainWindow` / `closeMiniPlayer`, plus object commands `{ type: 'seek' | 'setVolume' | 'adjustVolume' | 'playQueueTrack', ... }`.

---

## Desktop Lyric

`ctx.desktopLyric` controls EchoMusic's desktop lyric window.

| API | Description |
|-----|------|
| `getSnapshot()` | Get the full snapshot |
| `getWindow()` | Get the desktop lyric window bounds |
| `show()` / `hide()` | Show / hide |
| `toggleLock()` | Toggle lock (locked windows are click-through; unlock via the host UI) |
| `updateSettings(payload)` | Update settings (a `Partial<DesktopLyricSettings>`: font, colors, alignment, layout, etc.) |
| `updateWindow(bounds)` | Adjust the window bounds `{ x?, y?, width?, height? }` |
| `onSnapshot(fn)` | Subscribe to snapshot changes (full or incremental patches); returns a dispose function |
| `command(cmd)` | Send a desktop lyric command |

```js
const snapshot = await ctx.desktopLyric.getSnapshot();
console.log("enabled:", snapshot.settings.enabled, "locked:", snapshot.settings.locked);

// Show it and tweak the appearance
await ctx.desktopLyric.show();
await ctx.desktopLyric.updateSettings({ opacity: 0.8, activeFontSize: 44 });

ctx.desktopLyric.onSnapshot((message) => {
  // message is a full snapshot or an incremental patch
});
```

The snapshot carries three sections:

- **Playback**: `playback` (current track, cover, progress, playing state, rate)
- **Lyrics**: `lyrics` / `currentIndex` / `lyricTimeOffset` / `lyricsTrackId` / `lockPhase` / `lyricSyncWarning`
- **Appearance**: `settings` (fonts, sizes, colors, stroke, shadow, layout, translation/romanization toggles, etc.)

Full type definitions live in the host sources at `src/shared/desktopLyric.ts`. `command` supports `togglePlayback` / `previousTrack` / `nextTrack` / `toggleLyricsMode` / `cycleLyricsMode` / `openLyricSource` / `toggleTranslation` / `toggleRomanization` / `lyricOffsetBackward` / `lyricOffsetForward` / `lyricOffsetReset` / `openSettings`.

---

## Process Management

> Requires capability: `process: true`

`ctx.process` lets plugins launch and terminate executables **inside the plugin directory**.

| API | Description |
|-----|------|
| `launch(options)` | Launch a program from the plugin directory |
| `terminate(pid)` | Terminate a launched process (`pid` is required, from the `launch` result) |

```js
// Launch a program
const result = await ctx.process.launch({
  executable: "tools/my-helper.exe",  // relative to the plugin directory
  args: ["--port", "12345"],
  env: { CUSTOM_VAR: "value" },
  cwd: "tools/",                      // working directory relative to the plugin directory
});

if (result.ok) {
  const pid = result.pid;
  // Terminate later
  await ctx.process.terminate(pid);
}
```

| Option | Type | Required | Description |
|------|------|:--:|------|
| `executable` | `string` | ✅ | Executable path (relative to the plugin directory; never arbitrary system paths) |
| `args` | `string[]` | ❌ | Command-line arguments |
| `env` | `Record<string, string>` | ❌ | Extra environment variables (count and length limited) |
| `cwd` | `string` | ❌ | Working directory (relative and inside the plugin directory) |

### Consent flow

To prevent plugins from silently executing local programs, the host requires consent for every `launch`:

1. **First launch**: the host shows a system dialog "Allow this plugin to launch a local program?" listing the plugin name, plugin id, and program path. The program only starts after the user chooses "Allow and remember"
2. **Hash binding**: the consent record is bound to the executable's **SHA-256 hash** (`executableHash`); plugin updates, version changes, or any change to the file trigger a new consent prompt
3. **Windows restriction**: on Windows only `.exe` / `.com` executables are allowed; other platforms require the execute permission bit
4. `launch` fails immediately in safe mode, when the plugin is disabled, or when the version is incompatible

`ECHOMUSIC_PLUGIN_ID` and `ECHOMUSIC_PLUGIN_DIR` are injected into the environment automatically; some sensitive environment variables (e.g. proxy credentials) are filtered out. Child processes launched by a plugin are reaped when the plugin is disabled/uninstalled or the app exits (SIGTERM first, SIGKILL after a timeout).

---

## App Icons

`ctx.appIcons` manages the app window and taskbar icons. Configure icon paths via `ctx.storage`, then call `refresh()` to apply.

| API | Description |
|-----|------|
| `refresh()` | Refresh all icon caches (re-reads the configured icon files) |
| `setRuntimeWindowIcon(iconPath)` | Set the runtime window icon (path inside the plugin directory) |
| `restoreDefaultWindowIcon()` | Restore the default EchoMusic window icon |
| `restoreDefaultDesktopIcon()` | Restore the default desktop icon |
| `restoreDefaultTaskbarIcon()` | Restore the default taskbar icon |

```js
// Configure custom icons
await ctx.storage.set("appIcons", {
  trayIconPath: "generated/tray.png",
  taskbarIconPath: "generated/taskbar.ico",
  desktopIconPath: "generated/desktop.ico",
});
const result = await ctx.appIcons.refresh();
if (!result.desktopApplied && result.desktopError) {
  ctx.toast.warning(result.desktopError);
}
```

Per-platform configuration is supported:

```js
await ctx.storage.set("appIcons", {
  win32: { trayIconPath: "icons/tray.ico", taskbarIconPath: "icons/taskbar.ico" },
  linux: { trayIconPath: "icons/tray.png", taskbarIconPath: "icons/taskbar.png" },
  darwin: { trayIconPath: "icons/trayTemplate.png", taskbarIconPath: "icons/dock.icns" },
});
await ctx.appIcons.refresh();
```

### Icon library (ctx.icons)

`ctx.icons` provides Iconify icon objects that can be passed straight to the `Icon` component:

```js
const Icon = ctx.vue.resolveComponent("Icon");
h(Icon, { icon: ctx.icons.iconPictureInPicture, width: 16, height: 16 });
```

---

## Cross-window Communication (BroadcastChannel)

EchoMusic gives plugins `BroadcastChannel` for cross-window communication (main window ↔ mini player ↔ plugin floating windows).

```js
// Plugin in the main window
const channel = new BroadcastChannel("my-plugin-channel");
channel.postMessage({ type: "sync", data: {...} });

// Same plugin inside the mini player (if runtime.miniPlayer: true)
const channel = new BroadcastChannel("my-plugin-channel");
channel.onmessage = (event) => {
  console.log("Received:", event.data);
};
```

> Prefix the channel name with your plugin id to avoid conflicts with other plugins.

---

## Next Steps

| Document | Content |
|------|------|
| [Player & Audio Engine →](./player-audio) | Playback control, play queue, spectrum, lyrics system |
| [Audio Spectrum →](./audio-spectrum) | Real-time spectrum subscription and visualization |
| [Filesystem & Storage →](./filesystem-storage) | Filesystem, KV storage, appearance subscription |
| [API Overview →](./context-api) | Full plugin ctx API list |
