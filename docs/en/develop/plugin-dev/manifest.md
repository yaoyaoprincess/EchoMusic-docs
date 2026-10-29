---
title: Manifest Reference
outline: [2, 4]
---

# 📋 Manifest Reference

`manifest.json` is the heart of your plugin — it defines the plugin's identity, capabilities, runtime environment, and version requirements. This document explains every configuration field in detail.

## Complete Example

```json
{
  "id": "my-awesome-plugin",
  "name": "My Awesome Plugin",
  "version": "1.0.0",
  "description": "A powerful EchoMusic plugin",
  "author": "EchoMusic User",
  "icon": "icon.svg",
  "main": "index.js",
  "style": "style.css",
  "tags": ["tool"],
  "runtime": {
    "miniPlayer": false,
    "desktopLyric": true
  },
  "capabilities": {
    "audioSpectrum": true,
    "lyrics": true,
    "localFiles": true
  },
  "requires": {
    "echoMusicVersion": ">=2.3.2 <3"
  },
  "contributes": {
    "windows": [
      {
        "id": "my-float",
        "title": "My Floating Window",
        "main": "float.js",
        "defaultWidth": 360,
        "defaultHeight": 200
      }
    ]
  }
}
```

---

## Basic Fields

### id

| Property | Value |
|----------|-------|
| Type | `string` |
| Required | ✅ |
| Format | kebab-case (recommended) |

Unique plugin identifier. This ID must be unique across all of EchoMusic.

```json
"id": "my-awesome-plugin"
```

- Use `kebab-case` format: lowercase letters + hyphens
- Avoid generic names that could conflict with other plugins
- On uninstall, EchoMusic uses this ID to locate the plugin directory and KV data

---

### name

| Property | Value |
|----------|-------|
| Type | `string` |
| Required | ✅ |

**Human-readable** name displayed in the plugin manager.

```json
"name": "My Awesome Plugin"
```

- Supports any characters including Chinese and Emoji
- Keep it under 30 characters recommended
- Can duplicate other plugins' names (but `id` must be unique)

---

### version

| Property | Value |
|----------|-------|
| Type | `string` |
| Required | ✅ |
| Format | [Semantic Versioning](https://semver.org/) |

```json
"version": "1.2.3"
```

- Follow MAJOR.MINOR.PATCH format
- The online plugin registry checks this to determine if an update is available
- Version upgrade conventions:
  - PATCH (1.0.0 → 1.0.1): Bug fixes, backward compatible
  - MINOR (1.0.0 → 1.1.0): New features, backward compatible
  - MAJOR (1.0.0 → 2.0.0): Breaking changes

---

### description

| Property | Value |
|----------|-------|
| Type | `string` |
| Required | ❌ |

Short description of your plugin, displayed in the plugin manager.

```json
"description": "A powerful EchoMusic plugin"
```

- Keep it under 100 characters recommended
- Concisely describe the plugin's core functionality

---

### author

| Property | Value |
|----------|-------|
| Type | `string` |
| Required | ❌ |

Plugin author name, displayed in the plugin manager.

```json
"author": "EchoMusic User"
```

---

### tags

| Property | Value |
|----------|-------|
| Type | `string[]` |
| Required | ❌ |

Plugin tags array, usable for categorization or filtering (the `tags` field in `echo-plugins.json` is used for registry catalog organization).

```json
"tags": ["lyrics", "tool"]
```

---

### downloadUrl

| Property | Value |
|----------|-------|
| Type | `string` |
| Required | ❌ |

Direct download URL of the plugin package (optional). When omitted, online registries download from the plugin source repository path.

```json
"downloadUrl": "https://example.com/releases/my-plugin-1.2.3.zip"
```

---

### icon

| Property | Value |
|----------|-------|
| Type | `string` |
| Required | ❌ |

Plugin icon. Supports three forms:

```json
// 1. Relative path (within plugin directory)
"icon": "icon.svg"

// 2. HTTPS URL
"icon": "https://example.com/icon.png"

// 3. data: URI (inline Base64)
"icon": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0..."
```

- **SVG** recommended (vector, small size)
- PNG also supported, 128×128 or larger recommended
- If not provided, EchoMusic shows a default icon

---

### main

| Property | Value |
|----------|-------|
| Type | `string` |
| Required | ❌ |
| Default | `"index.js"` |

Plugin entry JavaScript file. Path is relative to the plugin directory.

```json
"main": "index.js"
```

- Supports `.js` and `.mjs` extensions
- The entry file runs in a browser ESM environment; **cannot use** `require()` or Node.js built-in modules

---

### style

| Property | Value |
|----------|-------|
| Type | `string` |
| Required | ❌ |

Plugin stylesheet. Path is relative to the plugin directory, only `.css` is supported.

```json
"style": "style.css"
```

- This CSS file is injected into **all windows where the plugin is loaded**
- If `runtime.miniPlayer: true`, CSS is also injected into the Mini Player window

---

## runtime

Controls which windows the plugin loads in.

```json
"runtime": {
  "miniPlayer": false,
  "desktopLyric": true
}
```

| Field | Type | Default | Description |
|-------|------|:---:|------|
| `miniPlayer` | `boolean` | `false` | Whether to load in the Mini Player window |
| `desktopLyric` | `boolean` | `false` | Whether to load in the Desktop Lyric window. When changing desktop lyric layout, effects, or size, also use `ctx.lyricEffects.register({ scope: "desktop" })` and `ctx.desktopLyric`. |

### Use Cases

| Scenario | miniPlayer | desktopLyric |
|----------|:--:|:--:|
| Add main window settings panel | ❌ | ❌ |
| Show custom UI in Mini Player | ✅ | ❌ |
| Overlay effects on desktop lyrics | ❌ | ✅ |
| Cross-window communication (advanced) | ✅ | ✅ |

> ⚠️ The main window, Mini Player, and Desktop Lyric are **three independent renderer processes**. JS memory is not shared. If your plugin needs to appear in the Mini Player, you must enable `miniPlayer`.

---

## capabilities

Plugin access to sensitive APIs uses **explicit declaration**. Only declare the capabilities your plugin actually needs.

```json
"capabilities": {
  "audioSource": false,
  "audioSpectrum": true,
  "backups": false,
  "downloads": false,
  "kugouApi": false,
  "kugouVerification": false,
  "localFiles": true,
  "lyricEffects": false,
  "lyrics": true,
  "lyricsPage": false,
  "process": false,
  "serverIntercept": false,
  "sqlite": false,
  "tcp": false,
  "theme": false,
  "unrestrictedNetwork": false,
  "webServer": false
}
```

### Capability Details

#### audioSource

| Property | Value |
|----------|-------|
| Grants | `ctx.player.audioSource.register()` |

Take over audio source resolution for specific platforms or songs. Enable this when developing custom audio source plugins (e.g. integrating third-party music platform APIs).

```js
// Requires audioSource capability
ctx.player.audioSource.register({
  id: "my-platform-resolver",
  position: "after-catalog", // fallback level; legacy plugins default to before-catalog
  async resolve({ track, quality }) {
    const response = await fetch(`https://api.example.com/song/${track.id}`);
    const data = await response.json();
    return data.streamUrl; // return a URL string, or a Partial<ResolvedAudioSource> object
  },
});
```

#### audioSpectrum

| Property | Value |
|----------|-------|
| Grants | `ctx.audio.spectrum` |

Read or subscribe to **real-time audio spectrum data**. Useful for visualizer plugins, equalizers, VU meters, etc.

```js
// Requires audioSpectrum capability
ctx.audio.spectrum.subscribe({ fps: 30, binCount: 48 }, (frame) => {
  // frame.bins holds the spectrum data array; frame.waveform is optional waveform data
  drawVisualizer(frame.bins);
});
```

#### kugouApi

| Property | Value |
|----------|-------|
| Grants | `ctx.kugou` |

Call the **Kugou Music API** for searching, fetching song details, retrieving playback URLs, etc.

#### kugouVerification

| Property | Value |
|----------|-------|
| Grants | `ctx.kugouVerification.request(challenge)` |

Handle **Kugou security verification challenges** (slider, captcha, etc.). Returns `{ ok: true, eventId }` on success or `{ ok: false, error, canceled? }` on failure.

#### localFiles

| Property | Value |
|----------|-------|
| Grants | `ctx.fs` |

Scan and read audio files from the filesystem, or write data within the plugin directory.

#### lyricEffects

| Property | Value |
|----------|-------|
| Grants | `ctx.lyricEffects.register()` |

Register **lyric visual effects** (page lyrics and desktop lyrics) via CSS injection or overlay decoration layer. For desktop lyrics, use `scope: "desktop"`. See [Player & Audio →](./player-audio#lyrics-visual-effects).

#### lyrics

| Property | Value |
|----------|-------|
| Grants | `ctx.lyrics.registerResolver()` |

Provide a **custom lyrics resolver** for songs. Useful for integrating third-party lyrics sources.

#### process

| Property | Value |
|----------|-------|
| Grants | `ctx.process.launch()` |

Launch **native programs from within the plugin directory**. Useful for calling external tools.

> ⚠️ This capability allows executing arbitrary local programs. Only enable for trusted plugins.

#### webServer

| Property | Value |
|----------|-------|
| Grants | `ctx.webServer` |

Create a **local HTTP server** accessible by other software on the same machine (Wallpaper Engine, OBS, local scripts, etc.) to read EchoMusic state, lyrics pages, or visualizer pages. Listens on `127.0.0.1` by default. The port is automatically released on plugin disable, uninstall, or app exit.

```js
// Requires webServer capability
ctx.webServer.listen(async (req) => {
  return { status: 200, body: JSON.stringify({ playing: ctx.player.currentTrack }) }
}).then(port => console.log('Server on port', port));
```

#### sqlite

| Property | Value |
|----------|-------|
| Grants | `ctx.sqlite` |

Use a **plugin-private SQLite database**, created by the host in EchoMusic's user data directory and isolated by plugin ID. Default database name is `main`. Supports table creation, CRUD, transactions, and BLOBs. See [Filesystem & Storage →](./filesystem-storage#sqlite-database).

```js
// Requires sqlite capability
const db = await ctx.sqlite.open({ name: "library" });
await db.run("CREATE TABLE IF NOT EXISTS songs (id TEXT PRIMARY KEY, title TEXT)");
await db.run("INSERT OR REPLACE INTO songs (id, title) VALUES (?, ?)", ["1", "My Song"]);
const row = await db.get("SELECT * FROM songs WHERE id = ?", ["1"]);
```

#### backups

| Property | Value |
|----------|-------|
| Grants | `ctx.backups` |

Create and restore **app backups**, or register your plugin's storage backend as a backup provider. See [Backups →](./backups).

#### downloads

| Property | Value |
|----------|-------|
| Grants | `ctx.net.download` / `ctx.net.downloads` |

Use the host **download engine** for resumable downloads (progress subscription, pause/resume, sha256 verification). See [Network & Downloads →](./network).

#### lyricsPage

| Property | Value |
|----------|-------|
| Grants | `ctx.ui.lyricsPage` |

Register **custom lyrics pages and skins** (`register/usePage/useSkin/openSkins`). See [Lyrics Page Skin →](./lyrics-page).

#### theme

| Property | Value |
|----------|-------|
| Grants | `ctx.theme.register` |

Register a **full app theme** (light/dark variants, color tokens, background and decorations). See [the theme section](./filesystem-storage#themes).

#### tcp

| Property | Value |
|----------|-------|
| Grants | `ctx.net.tcp.connect` |

Open **raw TCP connections** (read/write, timeout and keep-alive options, connection limit of 16). See [Network & Downloads →](./network#tcp-client).

#### unrestrictedNetwork

| Property | Value |
|----------|-------|
| Grants | `ctx.net.request` |

Perform **main-process network requests** (bypasses renderer CORS, supports custom TLS/timeout/redirect policies). See [Network & Downloads →](./network).

#### serverIntercept

| Property | Value |
|----------|-------|
| Grants | `ctx.server.intercept` |

**Intercept requests the app sends to its API server** (read, modify, mock, or forward). See [Server Intercept →](./server-intercept).

---

## requires

```json
"requires": {
  "echoMusicVersion": ">=2.2.6-beta.9 <3"
}
```

| Field | Type | Description |
|-------|------|------|
| `echoMusicVersion` | `string` | Semver range describing compatible EchoMusic versions |

### Version Range Syntax

| Syntax | Meaning |
|--------|--------|
| `>=2.2.6` | 2.2.6 and above |
| `>=2.2.6 <3` | 2.2.6 up to (but not including) 3.0.0 |
| `>=2.2.6-beta.9` | 2.2.6-beta.9 and above (including beta versions) |
| `2.2.6` | Equivalent to `>=2.2.6` |
| `^2.2.0` | Compatible with 2.x.x (2.2.0 before 3.0.0) |

### Version Validation Behavior

| Scenario | Result |
|----------|--------|
| Version range syntax error | Manifest marked **invalid**, plugin won't appear in the list |
| Range valid but not satisfied | Plugin appears in list, shows **"Version Incompatible"**, activation blocked |
| Range satisfied | Normal operation |

---

## contributes

Declares static resources the plugin contributes to the host application. Currently supports floating windows.

### contributes.windows

```json
"contributes": {
  "windows": [
    {
      "id": "my-float",
      "title": "My Floating Window",
      "main": "float.js",
      "style": "float.css",
      "defaultWidth": 360,
      "defaultHeight": 200,
      "minWidth": 240,
      "minHeight": 120,
      "position": "top-center",
      "transparent": true,
      "alwaysOnTop": true,
      "skipTaskbar": true,
      "resizable": false,
      "movable": true,
      "rememberBounds": true,
      "allowOutsideWorkArea": false,
      "acceptFirstMouse": false
    }
  ]
}
```

| Parameter | Type | Default | Description |
|-----------|------|:---:|------|
| `id` | `string` | — | Unique window identifier (required, unique within the plugin) |
| `title` | `string` | `"{plugin name} - {window id}"` | Window title |
| `main` | `string` | — | **Floating window entry JS file** (required, relative to the plugin directory). Floating windows have no separate HTML — the entry script runs in the floating window environment provided by the host |
| `style` | `string` | — | Floating window stylesheet (relative to the plugin directory, `.css` only) |
| `type` | `string` | `"floating"` | Window type; currently only `"floating"` |
| `defaultWidth` | `number` | `420` | Default width (px) |
| `defaultHeight` | `number` | `72` | Default height (px), commonly used by taskbar-lyric-style horizontal strips |
| `minWidth` / `minHeight` | `number` | derived | Minimum size |
| `maxWidth` / `maxHeight` | `number` | derived | Maximum size |
| `position` | `string` | `"top-center"` | Initial position: `"top-center"` or `"center"` |
| `transparent` | `boolean` | `true` | Enable transparent background |
| `alwaysOnTop` | `boolean` | `true` | Keep window on top |
| `skipTaskbar` | `boolean` | `true` | Don't show in taskbar |
| `resizable` | `boolean` | `false` | Allow drag-resizing |
| `movable` | `boolean` | `true` | Allow drag-moving |
| `rememberBounds` | `boolean` | `true` | Remember window position and size |
| `allowOutsideWorkArea` | `boolean` | `false` | Allow positioning outside the monitor work area |
| `acceptFirstMouse` | `boolean` | `false` | Pass the first click through on window activation |

> ⚠️ The floating window entry is a **JS file** (`main`), not HTML — the `url`, `label`, `width`, and `height` fields from older docs are obsolete. Floating windows run in a **dedicated plugin window context** with a different API surface than the main window. See [Windows & System →](./windows-system#floating-window-context) and the [EchoMusicPlugins Floating Window Docs](https://github.com/hoowhoami/EchoMusicPlugins/blob/main/docs/floating-windows.md).

---

## Manifest Validation Rules

EchoMusic validates the manifest when loading a plugin:

1. ✅ **JSON format** — Must be valid JSON
2. ✅ **Required fields** — `id`, `name`, `version` must exist and be non-empty
3. ✅ **Version format** — `version` must conform to semver
4. ✅ **requires.echoMusicVersion** — Must use valid semver range syntax
5. ✅ **capabilities** — Declaring a non-existent capability won't error, but won't take effect either

Validation failure → manifest invalid → plugin doesn't appear in the manager list.

---

## Next Steps

- [Context API Reference →](./context-api) — Explore all available `ctx` APIs
- [UI Extension Guide →](./ui-extension) — Learn how to add UI elements
- [Getting Started →](./getting-started) — Create your first plugin from scratch
