---
title: Context API Reference
outline: [2, 4]
---

# 🔧 Context API Reference

The `ctx` object is the core entry point for plugins. This document is a quick reference for every API available to plugins, with links to the detailed docs.

> ℹ️ This document is verified item-by-item against the main-program source (`src/renderer/plugins/runtime/context.ts`, the `EchoPluginContext` interface). The plugin marketplace stats subsystem is documented separately — see [Heat & Stats →](./marketplace-stats).

---

## 🏗️ Host Runtime

| API | Type | Description |
|-----|------|------|
| `ctx.vue` | Vue 3 runtime | `defineComponent` / `h` / `ref` / `computed` / `watch` / `onMounted` / `onUnmounted` / `defineAsyncComponent` / `reactive` / `resolveComponent` |
| `ctx.app` | App instance | The main application's Vue app instance |
| `ctx.router` | Router instance | Vue Router instance |
| `ctx.pinia` | Pinia instance | Pinia state management instance |

> ⚠️ Do **not** write `import { ref } from 'vue'`. Always access Vue through `ctx.vue.ref()`.

---

## 📦 Stores

| API | Description | Details |
|-----|------|:--:|
| `ctx.stores.player` | Playback state: current track, progress, volume, play mode | [Player](./player-audio) |
| `ctx.stores.playlist` | Playback queue state | [Player](./player-audio) |
| `ctx.stores.lyric` | Lyric state: current line, translation, offset | [Player](./player-audio#lyrics) |
| `ctx.stores.settings` | User settings | — |
| `ctx.stores.theme` | Theme colors, dark mode | [Filesystem](./filesystem-storage#appearance-subscription) |

---

## 🎨 UI Extension

| API | Description | Details |
|-----|------|:--:|
| `ctx.ui.addPage({id, title, icon?, component, sidebar?})` | Register a standalone page (sidebar accepts a config object) | [UI Extension](./ui-extension#registering-pages) |
| `ctx.ui.sidebar.addItem({id, title, icon?, pageId, ...})` | Add a sidebar item for a registered page | [UI Extension](./ui-extension#sidebar-items) |
| `ctx.ui.sidebar.shortcuts.register({id, title, pageId?, onClick?})` | Register a sidebar shortcut card | [UI Extension](./ui-extension#sidebar-shortcut-cards) |
| `ctx.ui.titlebar.register({id, title, icon?, defaultPlacement?, onClick})` | Register a title-bar button | [UI Extension](./ui-extension#titlebar-buttons) |
| `ctx.ui.playerbar.register({id, title, icon?, badge?, trigger?, ...})` | Register a player-bar button | [UI Extension](./ui-extension#player-bar-buttons) |
| `ctx.ui.lyricsPage.register({id, component, ...})` | Register a custom lyrics page / skin (requires `lyricsPage`) | [Lyrics Page Skin](./lyrics-page) |
| `ctx.ui.settings.define({title, component})` | Register a plugin settings panel | [UI Extension](./ui-extension#settings-panel) |
| `ctx.ui.addSongContextMenuItem({id, label, onSelect})` | Song context-menu item | [UI Extension](./ui-extension#song-context-menu) |
| `ctx.ui.cover.setFallback({id, resolveUrl})` | Fallback image when covers fail to load | [UI Extension](./ui-extension#cover-fallback) |
| `ctx.ui.mount(target, component, opts?)` | Mount a Vue component to the DOM | [UI Extension](./ui-extension#component-mounting) |
| `ctx.ui.teleport(component, opts?)` | Teleport a component to `document.body` | [UI Extension](./ui-extension#component-teleport) |
| `ctx.ui.components.*` | Host-provided components (auto-exposes everything under `ui/`, `music/`, `player/`) | [UI Extension](./ui-extension#preset-components) |
| `ctx.css.inject(css, {id?})` | Inject CSS dynamically; returns a dispose function (re-invoking with the same `id` replaces the old one) | [UI Extension](./ui-extension#css-injection) |
| `ctx.dom.observe(selector, callback, opts?)` | Watch for DOM nodes appearing (`opts`: `{root?, once?}`; the callback may return a cleanup function) | [UI Extension](./ui-extension#dom-watchers) |
| `ctx.dom.query(selector)` / `queryAll(selector)` | Query elements within the plugin scope | [UI Extension](./ui-extension#dom-watchers) |
| `ctx.commands.register(id, handler, {title?})` / `execute(id, ...args)` | Register / execute plugin commands | — |

---

## 🎵 Playback & Audio

### Playback Controls

| API | Description | Details |
|-----|------|:--:|
| `ctx.player.play(trackId?, options?)` | Play a specific track or resume playback | [Player](./player-audio#playback-controls) |
| `ctx.player.pause()` | Pause | [Player](./player-audio#playback-controls) |
| `ctx.player.toggle()` | Toggle play/pause | [Player](./player-audio#playback-controls) |
| `ctx.player.next()` / `prev()` | Next / previous track within the queue | [Player](./player-audio#playback-controls) |
| `ctx.player.stop()` | Stop | [Player](./player-audio#playback-controls) |
| `ctx.player.playTrack(trackId, options?)` | Play a track by ID | [Player](./player-audio#playback-controls) |
| `ctx.player.playSong(song, options?)` | Play a song object (enqueue and play) | [Player](./player-audio#playback-controls) |
| `ctx.player.playNext(song, options?)` / `playLast(song, options?)` | Insert a song after the current one / at the end | [Player](./player-audio#playback-controls) |
| `ctx.player.replaceQueueAndPlay(songs, options?)` | Replace the queue and play | [Player](./player-audio#playback-controls) |
| `ctx.player.seek(time)` | Seek (seconds) | [Player](./player-audio#playback-controls) |
| `ctx.player.setVolume(v)` | Set volume (0-100) | [Player](./player-audio#playback-controls) |
| `ctx.player.setPlaybackRate(r)` | Playback rate (0.5-3.0) | [Player](./player-audio#playback-controls) |
| `ctx.player.setPlayMode(m)` | Play mode | [Player](./player-audio#playback-controls) |
| `ctx.player.setAudioQuality(q)` | Audio quality | [Player](./player-audio#playback-controls) |
| `ctx.player.setAudioEffect(e)` | Set audio effect | [Player](./player-audio#playback-controls) |
| `ctx.player.dislikePersonalFm()` | Dislike in Personal FM | [Player](./player-audio#playback-controls) |
| `ctx.player.toggleLyricView(open?)` | Toggle the lyrics view | [Player](./player-audio#playback-controls) |

### Playback State (computed, read-only reactive)

| Property | Type | Description |
|------|:--:|------|
| `currentTrack` | `computed` | Current track object |
| `currentTrackId` | `computed` | Current track ID |
| `currentTime` / `duration` | `computed` | Progress / duration (seconds) |
| `isPlaying` / `isLoading` | `computed` | Playing / loading |
| `playbackState` | `computed` | Displayed playback state |
| `playbackRate` | `computed` | Playback rate |
| `volume` | `computed` | Volume (0-100) |
| `playMode` | `computed` | Play mode |
| `audioQuality` | `computed` | `{effective, resolved, override}` quality info |
| `audioEffect` | `computed` | `{current, resolved}` effect info |

### Playback Queue

> The queue supports a **multi-queue** model: `queues` lists all queues and `activeQueue` is the currently active one. Most operations accept an optional `queueId?`; they target the active queue by default.

| API | Description | Details |
|-----|------|:--:|
| `ctx.playlist.getActiveQueue()` | Get the active queue | [Player](./player-audio#queue-management) |
| `ctx.playlist.getQueue(queueId)` | Get a specific queue | [Player](./player-audio#queue-management) |
| `ctx.playlist.getQueueSongs(queueId?)` | Get the songs of a queue | [Player](./player-audio#queue-management) |
| `ctx.playlist.queues` / `activeQueue` | All queues / the active queue (computed) | [Player](./player-audio#queue-management) |
| `ctx.playlist.setActiveQueue(queueId)` | Switch the active queue | [Player](./player-audio#queue-management) |
| `ctx.playlist.replace(songs, options?)` | Replace queue contents | [Player](./player-audio#queue-management) |
| `ctx.playlist.replaceAndPlay(songs, options?)` | Replace the queue and play | [Player](./player-audio#queue-management) |
| `ctx.playlist.append(songs, options?)` | Append songs to the queue | [Player](./player-audio#queue-management) |
| `ctx.playlist.playNext(song, options?)` / `playLast(song, options?)` | Insert after the current track / at the end | [Player](./player-audio#queue-management) |
| `ctx.playlist.enqueuePlayNext(songId)` / `enqueuePlayNextSequential(songId)` | Enqueue by ID (overwriting / sequential) | [Player](./player-audio#queue-management) |
| `ctx.playlist.remove(songId, queueId?)` | Remove a song | [Player](./player-audio#queue-management) |
| `ctx.playlist.reorder(fromIndex, toIndex, queueId?)` | Reorder | [Player](./player-audio#queue-management) |
| `ctx.playlist.clear(queueId?)` | Clear a queue | [Player](./player-audio#queue-management) |

### Audio Spectrum

> Requires capability: `audioSpectrum: true`

| API | Description | Details |
|-----|------|:--:|
| `ctx.audio.spectrum.getStatus()` | Get capture status | [Spectrum](./audio-spectrum#getstatus) |
| `ctx.audio.spectrum.getSnapshot()` | Single-frame spectrum snapshot | [Spectrum](./audio-spectrum#getsnapshot) |
| `ctx.audio.spectrum.subscribe(opts, cb)` | Subscribe to the spectrum in real time | [Spectrum](./audio-spectrum#subscribe) |

### Custom Audio Sources & Lyrics

| API | Description | Details |
|-----|------|:--:|
| `ctx.player.audioSource.register(opts)` | Register an audio source resolver (requires `audioSource: true`) | [Player](./player-audio#custom-audio-sources) |
| `ctx.lyrics.registerResolver(opts)` | Register a lyrics resolver (requires `lyrics: true`) | [Player](./player-audio#registering-a-lyrics-resolver) |
| `ctx.lyrics.getSnapshot()` | Lyric state snapshot | [Player](./player-audio#lyric-snapshot) |
| `ctx.lyrics.onSnapshot(fn)` | Subscribe to lyric changes | [Player](./player-audio#lyric-snapshot) |
| `ctx.lyrics.command(cmd)` | Send a lyric command | [Player](./player-audio#lyric-snapshot) |
| `ctx.lyricEffects.register(opts)` | Register a lyric effect (requires `lyricEffects: true`) | [Player](./player-audio#lyric-visual-effects) |

---

## 🖥️ Desktop Lyrics & Mini Player

> The Desktop Lyric and Mini Player are separate windows that do not share JS memory with the main window. Declare the corresponding fields in manifest `runtime`.

| API | Description | Details |
|-----|------|:--:|
| `ctx.desktopLyric.*` | Full Desktop Lyric API (snapshot subscription, show/hide, lock, settings) | [Windows](./windows-system#desktop-lyrics) |
| `ctx.miniPlayer.*` | Full Mini Player API (snapshot, always-on-top, volume, seek) | [Windows](./windows-system#mini-player) |
| `ctx.lyricEffects.register({ scope: "desktop", ... })` | Register desktop lyric visual effects (requires `lyricEffects: true`) | [Player](./player-audio#lyric-visual-effects) |

---

## 💾 Data & Files

### KV Storage

`ctx.storage` provides plugin-isolated persistent KV storage.

| API | Description | Details |
|-----|------|:--:|
| `ctx.storage.get(key)` | Read a value | [Data](./filesystem-storage#kv-storage) |
| `ctx.storage.set(key, value)` | Write a value | [Data](./filesystem-storage#kv-storage) |
| `ctx.storage.delete(key)` | Delete a value | [Data](./filesystem-storage#kv-storage) |

> KV data is removed automatically on uninstall; it survives upgrades (overwrite installs).

### Filesystem

> Requires capability: `localFiles: true` (most operations)

| API | Description | Details |
|-----|------|:--:|
| `ctx.fs.listFiles(directory, opts?)` | Scan a directory | [Data](./filesystem-storage#filesystem) |
| `ctx.fs.listImageFiles(directory, opts?)` | Scan image files | [Data](./filesystem-storage#filesystem) |
| `ctx.fs.readTextFile(path, opts?)` | Read a text file | [Data](./filesystem-storage#filesystem) |
| `ctx.fs.readFileBytes(path, opts?)` | Read a binary file | [Data](./filesystem-storage#filesystem) |
| `ctx.fs.writeFile(path, data, opts?)` | Write a file (plugin directory only) | [Data](./filesystem-storage#filesystem) |
| `ctx.fs.deleteFile(path)` | Delete a file (plugin directory only) | [Data](./filesystem-storage#filesystem) |
| `ctx.fs.getFileUrl(path)` | Get a playable file URL | [Data](./filesystem-storage#filesystem) |
| `ctx.fs.requestDirectory(...)` / `requestFiles(...)` | Request user-granted file/directory access | [Data](./filesystem-storage#granted-files-directories) |
| `ctx.fs.openMedia(ref)` | Open a media lease for playback | [Data](./filesystem-storage#granted-files-directories) |
| `ctx.fs.readAudioMetadata(path)` | Parse local audio metadata | [Data](./filesystem-storage#granted-files-directories) |

### Appearance & Fonts

| API | Description | Details |
|-----|------|:--:|
| `ctx.appearance.getSnapshot()` | Appearance snapshot: `{isDark, accentColor, fontFamily?, colors?, floatingSurfaceFrosted?}` | [Data](./filesystem-storage#appearance-subscription) |
| `ctx.appearance.onSnapshot(fn)` | Subscribe to appearance changes | [Data](./filesystem-storage#appearance-subscription) |
| `ctx.fonts.getAll()` | List of system font names | — |
| `ctx.fonts.getOptions({includeSystem?, systemLabel?, followLabel?})` | Font options (usable in Select components) | — |
| `ctx.fonts.buildFamily(name)` | Build a CSS font-family string | — |

### SQLite Database

> Requires capability: `sqlite: true`

Plugin-private SQLite database, isolated by plugin ID and hosted by EchoMusic.

| API | Description | Details |
|-----|------|:--:|
| `ctx.sqlite.open({name?, readOnly?, busyTimeoutMs?, migrations?})` | Open/create a database, default name `main` | [Data](./filesystem-storage#sqlite-database) |
| `ctx.sqlite.listDatabases()` | List databases | [Data](./filesystem-storage#sqlite-database) |
| `ctx.sqlite.deleteDatabase(name?)` | Delete a database | [Data](./filesystem-storage#sqlite-database) |
| `db.exec(sql)` | Execute SQL | [Data](./filesystem-storage#sqlite-database) |
| `db.run(sql, params?)` | INSERT/UPDATE/DELETE | [Data](./filesystem-storage#sqlite-database) |
| `db.get(sql, params?)` | Query a single row | [Data](./filesystem-storage#sqlite-database) |
| `db.all(sql, params?)` | Query multiple rows | [Data](./filesystem-storage#sqlite-database) |
| `db.transaction(sqls)` | Run a transaction (an **array of SQL statements**) | [Data](./filesystem-storage#sqlite-database) |
| `db.close()` | Close the connection | [Data](./filesystem-storage#sqlite-database) |

> BLOB parameters are supported: write `{ type: "hex", data }` or `{ type: "base64", data }`; queries return hex strings.

---

## 🪟 Windows & System

### Window Control

> The `windowId` first parameter selects the target window (e.g. a floating window ID declared by the plugin).

| API | Description | Details |
|-----|------|:--:|
| `ctx.windows.show(windowId, options?)` | Show a window | [Windows](./windows-system#window-control) |
| `ctx.windows.hide(windowId)` | Hide a window | [Windows](./windows-system#window-control) |
| `ctx.windows.close(windowId)` | Close a window | [Windows](./windows-system#window-control) |
| `ctx.windows.move(windowId, bounds)` | Move a window | [Windows](./windows-system#window-control) |
| `ctx.windows.getBounds(windowId)` | Get window bounds | [Windows](./windows-system#window-control) |
| `ctx.windows.setIgnoreMouseEvents(windowId, ignore)` | Toggle click-through | [Windows](./windows-system#window-control) |

### Now Playing

| API | Description | Details |
|-----|------|:--:|
| `ctx.nowPlaying.getSnapshot()` | Current state snapshot (nested: `snapshot.playback.title/artist`, etc.) | [Windows](./windows-system#now-playing-window) |
| `ctx.nowPlaying.onSnapshot(fn)` | Subscribe to state changes | [Windows](./windows-system#now-playing-window) |
| `ctx.nowPlaying.onCommand(fn)` | Listen for commands | [Windows](./windows-system#now-playing-window) |
| `ctx.nowPlaying.syncSnapshot(payload)` | Sync a snapshot (playback/lyric info; replaces the obsolete syncPlayback/syncLyric) | [Windows](./windows-system#now-playing-window) |

### Process Management

> Requires capability: `process: true`

| API | Description | Details |
|-----|------|:--:|
| `ctx.process.launch(opts)` | Launch a program inside the plugin directory (`executable`; first run requires user consent) | [Windows](./windows-system#process-management) |
| `ctx.process.terminate(pid)` | Terminate a launched process (`pid` required) | [Windows](./windows-system#process-management) |

### App Icons

| API | Description | Details |
|-----|------|:--:|
| `ctx.appIcons.refresh()` | Refresh all icon caches | [Windows](./windows-system#app-icons) |
| `ctx.appIcons.setRuntimeWindowIcon(path)` | Set the runtime window icon | [Windows](./windows-system#app-icons) |
| `ctx.appIcons.restoreDefaultWindowIcon()` | Restore the default window icon | [Windows](./windows-system#app-icons) |
| `ctx.appIcons.restoreDefaultDesktopIcon()` | Restore the default desktop icon | [Windows](./windows-system#app-icons) |
| `ctx.appIcons.restoreDefaultTaskbarIcon()` | Restore the default taskbar icon | [Windows](./windows-system#app-icons) |

### Icon Library

| API | Description |
|-----|------|
| `ctx.icons` | Iconify icon object, e.g. `ctx.icons.iconPictureInPicture`, usable directly as an `Icon` component |

```js
const Icon = ctx.vue.resolveComponent("Icon");
h(Icon, { icon: ctx.icons.iconPictureInPicture, width: 16, height: 16 });
```

### System Dialogs

| API | Description |
|-----|------|
| `ctx.dialog.selectDirectory(opts?)` | Open a directory picker, returns `{canceled, paths}` |
| `ctx.dialog.selectFiles(opts?)` | Open a file picker, supports `multiple` and `filters` |

---

## 🎨 Theme & Styles

### Surface Styles

```js
ctx.theme.surface.set({
  enabled: true,
  mainOpacity: 82,         // 0-100
  sidebarOpacity: 82,
  cardOpacity: 86,
  playerOpacity: 92,
  backdropFilter: "blur(10px)",
  playerBackdropFilter: "blur(20px) saturate(180%)",
});
ctx.theme.surface.clear(); // restore defaults
```

### Page Transition

```js
ctx.theme.pageTransition.set({
  enabled: true,
  mode: "out-in",          // or "in-out"
  appear: true,
  durationMs: 450,
  enterOpacity: 0,
  leaveOpacity: 0,
  enterTranslateY: 6,
  enterTranslateX: 0,
  leaveTranslateX: 0,
  enterScale: 1,
  leaveScale: 1,
  enterFilter: "none",
  leaveFilter: "none",
  name: "my-transition",   // optional: custom transition class prefix
  css: "",                 // optional: extra CSS
});
ctx.theme.pageTransition.clear();
```

### Accent Gradient

```js
ctx.theme.accentGradient.set({
  color: "#ff5c8a",
  angle: 180,
  height: "46%",
  peakOpacity: 0.28,
  enabled: true,
  opacity: 1,
  midPosition: 0.5,
  midOpacity: 0.6,
  background: "",
  dark: {},                // optional: separate dark-mode config
});
ctx.theme.accentGradient.clear();
```

---

## 📜 Scroll Canvas

`ctx.scroll` provides advanced control over page scroll containers — great for scroll-enhancement plugins.

| API | Description |
|-----|------|
| `queryContainers({role?, visible?})` | Get scroll containers (filter by role/visibility) |
| `getCurrentContainer()` | Get the focused container |
| `getState(el?)` | Get scroll state |
| `scrollToTop(el?)` / `scrollToBottom(el?)` | Scroll to top / bottom |
| `scrollTo(el, target, options?)` | Scroll precisely to an element or position |
| `selector` | CSS selector of the host scroll containers |
| `observeContainers(handler(el, state))` | Watch for scroll container changes |

---

## 🌐 Kugou API

> Requires capability: `kugouApi: true`

`ctx.kugou` exposes EchoMusic's built-in Kugou Music APIs. APIs are lazy-loaded and called on demand.

| Namespace | Example |
|----------|------|
| `ctx.kugou.music` | `ctx.kugou.music.getSongUrl(hash)` |
| `ctx.kugou.user` | `ctx.kugou.user.getUserDetail()` |
| `ctx.kugou.playlist` | `ctx.kugou.playlist.getUserPlaylists()` |
| `ctx.kugou.video` | `ctx.kugou.video.getVideoDetail(id)` |
| `ctx.kugou.search` | `ctx.kugou.search.search(keyword)` |
| `ctx.kugou.artist` | `ctx.kugou.artist.getArtistDetail(id)` |
| `ctx.kugou.album` | `ctx.kugou.album.getAlbumDetail(id)` |
| `ctx.kugou.comment` | `ctx.kugou.comment.getMusicComments(mixSongId)` |
| `ctx.kugou.audioEffect` | Audio effect related APIs |
| `ctx.kugou.blacklist` | Song blacklist management |
| `ctx.kugou.channel` | Channel related APIs |
| `ctx.kugou.importPlaylist` | External playlist import |
| `ctx.kugou.listenTogether` | Listen Together |
| `ctx.kugou.listeningPreferences` | Listening preferences |
| `ctx.kugou.purchased` | Purchased music |
| `ctx.kugou.recognize` | Song recognition |

> ⚠️ Plugins only pass business parameters (`hash`, `id`, etc.) — never credentials (token, dfid, mid). The main process injects the current login state automatically.

## 🔐 Kugou Verification

> Requires capability: `kugouVerification: true`

| API | Description |
|-----|------|
| `ctx.kugouVerification.request(challenge)` | Handle a Kugou security verification challenge, returns `{ok: true, eventId}` or `{ok: false, error, canceled?}` |

---

## ⚡ Native API

### Electron Object

```js
ctx.electron.platform  // "win32" | "darwin" | "linux"
```

You can access host Electron APIs directly (e.g. `ctx.electron.miniPlayer?.show()`), but prefer the `ctx`-wrapped APIs in most cases.

> ⚠️ **Plugin management methods live on `ctx.electron.plugins`, not `ctx.plugins`** — `EchoPluginContext` has no top-level `plugins` member. This is the most common pitfall. See [Publishing →](./publishing#plugin-management-api).

---

## 🧩 Plugin Management

> These methods live on **`ctx.electron.plugins`** (management-plane API, not `ctx.plugins`).

| API | Description | Details |
|-----|------|:--:|
| `ctx.electron.plugins.list()` | List all plugins | [Publishing](./publishing#plugin-management-api) |
| `ctx.electron.plugins.installLocal(paths, opts?)` | Install from local paths | [Publishing](./publishing#local-installation) |
| `ctx.electron.plugins.uninstall(pluginId, {removeData?})` | Uninstall a plugin | [Publishing](./publishing#uninstallation) |
| `ctx.electron.plugins.setEnabled(id, enabled)` | Enable/disable | [Publishing](./publishing#safe-mode-failure-management) |
| `ctx.electron.plugins.setSafeMode(enabled)` | Global safe mode | [Publishing](./publishing#safe-mode-failure-management) |
| `ctx.electron.plugins.reportFailure(failure)` | Report a failure | [Publishing](./publishing#failure-reporting) |
| `ctx.electron.plugins.clearFailure(pluginId?)` | Clear failure records | [Publishing](./publishing#failure-reporting) |
| `ctx.electron.plugins.marketplace.listSources()` | List plugin sources | [Publishing](./publishing#source-management) |
| `ctx.electron.plugins.marketplace.addSource(input)` | Add a plugin source | [Publishing](./publishing#source-management) |
| `ctx.electron.plugins.marketplace.patchSource(id, patch)` | Update a source | [Publishing](./publishing#source-management) |
| `ctx.electron.plugins.marketplace.removeSource(id)` | Remove a source | [Publishing](./publishing#source-management) |
| `ctx.electron.plugins.marketplace.list(opts?)` | Browse online plugins | [Publishing](./publishing#browsing-installing) |
| `ctx.electron.plugins.marketplace.install(srcId, pId, opts?)` | Install online | [Publishing](./publishing#browsing-installing) |

---

## 🌐 Network & Downloads

> Requires capabilities: `unrestrictedNetwork` (request) / `tcp` (TCP) / `downloads` (downloads). See [Network & Downloads →](./network).

| API | Description |
|-----|------|
| `ctx.net.request(options)` | HTTP request via the main process (bypasses CORS, custom TLS/timeout/redirect) |
| `ctx.net.fetch(input, init?)` | Browser fetch semantics |
| `ctx.net.tcp.connect({host, port, ...})` | Open a TCP connection (read/write, keep-alive, limit of 16) |
| `ctx.net.download(options)` | Resumable download (progress subscription, pause/resume, sha256) |
| `ctx.net.downloads.{list,get,attach,remove}` | Download task management |

## 🖼️ Graphics

> Requires capability: `graphics`. See [Graphics →](./graphics).

| API | Description |
|-----|------|
| `ctx.graphics.getCapabilities({refresh?})` | Query WebGPU/HDR capabilities |
| `ctx.graphics.createCanvas({dynamicRange, ...})` | Create an HDR/SDR drawing canvas (automatic fallback) |
| `ctx.graphics.onCapabilitiesChanged(cb)` | Subscribe to capability changes |

## 🛰️ Server Intercept

> Requires capability: `serverIntercept`. See [Server Intercept →](./server-intercept).

| API | Description |
|-----|------|
| `ctx.server.intercept(interceptor, {priority?, match?, name?})` | Intercept requests the app sends to its API server (read, modify, mock, forward) |

## 📋 Tasks

| API | Description |
|-----|------|
| `ctx.tasks.register({id, name, status, ...})` | Register a session-scoped task (progress, cancel, actions); returns a handle `{update, finish, dismiss, ...}` |

## 💾 Backups

> Requires capability: `backups`. See [Backups →](./backups).

| API | Description |
|-----|------|
| `ctx.backups.create(scope?, settingsData?)` | Create an app backup |
| `ctx.backups.inspect(data)` | Validate a backup and obtain a restore token |
| `ctx.backups.restore(token, scope?)` | Restore from a backup (auto-restarts on success) |
| `ctx.backups.registerProvider({id, name, ...})` | Register a custom backup provider |

## 🧭 Misc

| API | Description |
|-----|------|
| `ctx.id` / `ctx.manifest` | Current plugin ID and manifest (read-only) |
| `ctx.descriptor` | Plugin descriptor: `installSource`, `directory`, `compatibility`, etc. |
| `ctx.dispose(fn)` | Register a cleanup function (called when the plugin is disabled) |
| `ctx.toast.info(msg)` / `success(msg)` / `warning(msg)` / `danger(msg)` / `show(opts)` | Toast messages |
| `ctx.events` | Playback events: `onTrackChange / onPlaybackChange / onPlaybackStateChange / onPlay({immediate?}) / onPause / onEnded / onSeek / onError / onTimeUpdate / on(event, ...)` |
| `ctx.shortcuts.register(accelerator, handler)` | In-app shortcut |
| `ctx.shortcuts.registerGlobal(accelerator, handler)` | System-global shortcut (throws on conflict) |
| `ctx.commands.register(id, handler, {title?})` / `execute(id, ...args)` | Register / execute plugin commands |
| `ctx.host.showOnTop(target?, {focus?})` | Bring the `'main'` or `'mini-player'` window to the front |

---

## Next Steps

| Document | Content |
|------|------|
| [UI Extension Guide →](./ui-extension) | UI customization in depth |
| [Player & Audio →](./player-audio) | Playback, queue, spectrum, lyrics |
| [Filesystem & Storage →](./filesystem-storage) | Filesystem, KV, granted files, appearance |
| [Audio Spectrum →](./audio-spectrum) | Real-time FFT spectrum data |
| [Windows & System →](./windows-system) | Floating windows, Now Playing, taskbar, process, icons |
| [Network & Downloads →](./network) | Main-process requests, TCP, download engine |
| [Graphics →](./graphics) | HDR/WebGPU drawing canvas |
| [Server Intercept →](./server-intercept) | Intercept API server requests |
| [Tasks →](./tasks) | Session-scoped tasks |
| [Backups →](./backups) | App backups and custom providers |
| [Lyrics Page Skin →](./lyrics-page) | Custom lyrics pages and skins |
| [Heat & Stats →](./marketplace-stats) | Plugin heat scoring and query API |
| [Publishing →](./publishing) | Sources, marketplace, failure management |
