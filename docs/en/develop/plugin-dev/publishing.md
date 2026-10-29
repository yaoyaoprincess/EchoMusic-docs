---
title: Publishing & Distribution
outline: [2, 4]
---

# 🚢 Publishing & Distribution

There are two ways to share your plugin with other EchoMusic users: direct directory sharing, or publishing to the online plugin registry.

## Direct Distribution

The simplest approach: zip the plugin folder and share it. Users unzip it into EchoMusic's plugin directory.

```
my-plugin.zip
  └── my-plugin/
      ├── manifest.json
      ├── index.js
      ├── style.css      ← optional
      └── icon.svg       ← optional
```

> Drawback: users cannot get updates automatically.

---

## Online Plugin Registry

An online registry lets users **browse, one-click install, and auto-update** plugins from EchoMusic's plugin management page.

> 📊 Install popularity statistics are collected by EchoMusic automatically — no integration needed. See [Popularity & Stats](./marketplace-stats).

### How it works

```
  ┌─────────────┐      fetch echo-plugins.json      ┌──────────────┐
  │  EchoMusic   │ ─────────────────────────────────▶ │  GitHub repo  │
  │  management  │                                     │  (registry)   │
  │    page      │ ◀───────────────────────────────── │              │
  │  shows list  │      returns the plugin index       └──────────────┘
  └──────┬───────┘
         │ user clicks "Install"
         ▼
  ┌─────────────┐      clone / download               ┌──────────────┐
  │ local plugin │ ◀────────────────────────────────── │  plugin repo  │
  │   directory  │                                     └──────────────┘
  └─────────────┘
```

### Step 1: create a registry repository

Create a GitHub repository (e.g. `my-echo-plugins`) and add an `echo-plugins.json` at the repository root:

```json
{
  "name": "My Plugin Registry",
  "homepage": "https://github.com/your-name/my-echo-plugins",
  "plugins": [
    {
      "id": "lyric-enhancer",
      "path": "lyric-enhancer",
      "repo": "https://github.com/your-name/lyric-enhancer",
      "homepage": "https://github.com/your-name/lyric-enhancer#readme",
      "tags": ["lyrics", "ui"]
    },
    {
      "id": "mini-spectrum",
      "path": "mini-spectrum",
      "repo": "https://github.com/your-name/mini-spectrum",
      "homepage": "https://github.com/your-name/mini-spectrum",
      "tags": ["visualizer", "audio"]
    }
  ]
}
```

### echo-plugins.json fields

#### Root fields

| Field | Type | Required | Description |
|------|------|:--:|------|
| `name` | `string` | ✅ | Registry name |
| `homepage` | `string` | ❌ | Registry home page URL |
| `plugins` | `array` | ✅ | Included plugin list |

#### plugins[] entries

| Field | Type | Required | Description |
|------|------|:--:|------|
| `id` | `string` | ✅ | Plugin id; must match the `id` in the plugin's manifest.json |
| `path` | `string` | ✅ | Directory path inside the repository (empty string means the repository root) |
| `repo` | `string` | ❌ | Plugin source repository; leave empty to use the registry repository |
| `homepage` | `string` | ❌ | Plugin details or documentation link |
| `tags` | `string[]` | ❌ | Category tags used for filtering and search in the online list |

> ⚠️ **Do not maintain `version`, `description`, `author`, etc. in `echo-plugins.json`.** Those belong to each plugin's `manifest.json`; EchoMusic reads them from the plugin repository automatically.

### Step 2: put the plugin into a repository

If the plugin lives in its own repository (recommended):

```
your-name/lyric-enhancer/        ← standalone plugin repository
  ├── manifest.json
  ├── index.js
  ├── style.css
  └── icon.svg
```

Then point to it from the registry's `echo-plugins.json`:

```json
{
  "id": "lyric-enhancer",
  "path": "",                    ← empty string: the repository root is the plugin
  "repo": "https://github.com/your-name/lyric-enhancer"
}
```

If multiple plugins share one repository:

```
your-name/my-echo-plugins/       ← registry repository
  ├── echo-plugins.json
  ├── lyric-enhancer/            ← plugin 1
  │   ├── manifest.json
  │   └── index.js
  └── mini-spectrum/             ← plugin 2
      ├── manifest.json
      └── index.js
```

The corresponding `echo-plugins.json`:

```json
{
  "plugins": [
    {
      "id": "lyric-enhancer",
      "path": "lyric-enhancer",   ← points to the subdirectory
      "repo": ""                  ← empty: use this repository
    },
    {
      "id": "mini-spectrum",
      "path": "mini-spectrum",
      "repo": ""
    }
  ]
}
```

---

## Programmatic Plugin Management API

Besides the UI's "Add registry" flow, plugins can manage registries and install/uninstall plugins programmatically via **`ctx.electron.plugins`**.

> ⚠️ These APIs live under `ctx.electron.plugins` (the host preload's `window.electron.plugins`), **not** `ctx.plugins` — the ctx top level has no `plugins` member. They are host management APIs: calling them directly changes the user's plugin list (install, uninstall, enable/disable). Use them only in clearly management-oriented plugins (e.g. a plugin manager) and make the actions explicit in your UI.

### Registry management (electron.plugins.marketplace)

| API | Description |
|-----|------|
| `ctx.electron.plugins.marketplace.listSources()` | List all added registries, returns `{ sources }` |
| `ctx.electron.plugins.marketplace.addSource(input, options?)` | Add a registry, `input` is `{ url, name?, enabled? }` |
| `ctx.electron.plugins.marketplace.patchSource(sourceId, patch)` | Update registry settings, `patch` is `{ name?, enabled? }` |
| `ctx.electron.plugins.marketplace.removeSource(sourceId)` | Remove a registry |
| `ctx.electron.plugins.marketplace.list(options?)` | Browse available plugins across registries, returns `{ ok, sources, plugins, fetchedAt }` |
| `ctx.electron.plugins.marketplace.install(sourceId, pluginId, options?)` | Install a plugin from a registry |

```js
// Add a registry (enabled: false adds it without enabling)
await ctx.electron.plugins.marketplace.addSource({
  url: "https://github.com/hoowhoami/EchoMusicPlugins",
  name: "EchoMusic Official Plugins",
  enabled: true,
});

// List current registries
const { sources } = await ctx.electron.plugins.marketplace.listSources();
console.log(sources);

// Rename a registry
await ctx.electron.plugins.marketplace.patchSource("source-id", {
  name: "Updated name",
});
```

### Browsing and installing

```js
// Get all available plugins
const result = await ctx.electron.plugins.marketplace.list();
// result.plugins is a PluginMarketplacePlugin list (sourceId, manifest, stats, compatibility, ...)

// Install a plugin online
const installResult = await ctx.electron.plugins.marketplace.install(
  "source-id",
  "my-plugin",
  {
    githubProxyUrl: "https://ghproxy.example/", // optional: GitHub acceleration proxy
    enableAfterInstall: true,                   // optional: enable right after install
  },
);
if (installResult.ok) {
  console.log("Installed:", installResult.plugin.name, "was update:", installResult.updated);
}
```

`install` options (`PluginMarketplaceInstallOptions`):

| Option | Type | Description |
|------|------|------|
| `githubProxyUrl` | `string` | GitHub acceleration proxy used for this install |
| `enableAfterInstall` | `boolean` | Whether to enable the plugin automatically after installation |

> There is no `force`-style override option: installing over an existing plugin goes through the host's update flow (version comparison + transactional replacement) and rolls back on failure.

---

## Local Install & Uninstall

### Local install

| API | Description |
|-----|------|
| `ctx.electron.plugins.installLocal(paths, options?)` | Install plugins from local paths (ZIP files/folders), `options` is `{ enableAfterInstall?, expectedPluginId? }` |
| `ctx.electron.plugins.getDroppedFilePaths(files)` | Convert a drop event's `File[]` into absolute local paths |

```js
// Install plugins dragged from the file manager
const paths = ctx.electron.plugins.getDroppedFilePaths(event.dataTransfer.files);
const result = await ctx.electron.plugins.installLocal(paths);
console.log(`Installed ${result.installed}, failed ${result.failed}`);
```

### Uninstall

| API | Description |
|-----|------|
| `ctx.electron.plugins.uninstall(pluginId, options?)` | Uninstall a plugin (the plugin directory, KV data, and SQLite are always removed); `options.removeData: true` additionally deletes files in the plugin's private data/cache directories |

```js
await ctx.electron.plugins.uninstall("my-plugin", { removeData: true });
```

---

## Enable/Disable & Safe Mode

| API | Description |
|-----|------|
| `ctx.electron.plugins.setEnabled(pluginId, enabled)` | Enable/disable a plugin |
| `ctx.electron.plugins.setSafeMode(enabled)` | Toggle global safe mode (true disables all plugins) |
| `ctx.electron.plugins.reloadRuntimes()` | Broadcast a plugin runtime reload to all windows |

### Failure reporting

Plugins can proactively report runtime failures so EchoMusic can decide whether to suggest disabling them.

| API | Description |
|-----|------|
| `reportFailure(failure)` | Report a failure record, `failure` is `{ pluginId?, pluginIds?, reason, message, createdAt? }` |
| `clearFailure(pluginId?)` | Clear failure records (omit the argument to clear all) |
| `markStartup(pluginIds)` | Mark plugins active during startup |
| `setActiveSession(pluginIds)` | Mark plugins active in the current session |
| `clearStartup()` | Clear startup markers |

`reason` is one of `"activation-error"` (activation failed), `"runtime-error"` (runtime error), `"render-process-gone"` (renderer crash), `"unresponsive"` (unresponsive).

```js
// Report a failure
ctx.electron.plugins.reportFailure({
  pluginId: ctx.manifest.id,
  reason: "runtime-error",
  message: "Network request failed during plugin initialization",
});

// Clear this plugin's failure history
ctx.electron.plugins.clearFailure(ctx.manifest.id);
```

> If an enabled plugin crashes repeatedly within one **startup session**, EchoMusic automatically suggests disabling it.

---

## Version Management

### version in manifest.json

The plugin version is defined in `manifest.json` and follows [Semantic Versioning](https://semver.org/):

```json
{
  "version": "1.2.0"
}
```

### Update detection

EchoMusic compares the installed plugin's `version` with the `manifest.json` `version` from the online registry:

| Situation | EchoMusic behavior |
|------|----------------|
| Online version > local version | Shows "update available" and prompts to upgrade |
| Online version = local version | Shows "up to date" |
| Local version missing from the registry | No update prompt |

### Version bump guidelines

```json
// Bug fix: bump PATCH
"version": "1.0.0" → "1.0.1"

// New feature (backward compatible): bump MINOR, reset PATCH
"version": "1.0.5" → "1.1.0"

// Breaking change: bump MAJOR, reset MINOR and PATCH
"version": "1.5.2" → "2.0.0"
```

---

## TypeScript / Vue SFC

The plugin entry runs in a browser ESM environment. To use TypeScript or `.vue` single-file components, bundle everything into a plain JavaScript ESM first.

### Recommended toolchains

#### Option 1: Vite (recommended)

```bash
# Initialize
npm init -y
npm install -D vite
```

```js
// vite.config.js
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  build: {
    lib: {
      entry: 'src/index.ts',        // entry
      formats: ['es'],              // ESM format
      fileName: () => 'index.js',   // output file name
    },
    rollupOptions: {
      external: [],                 // bundle everything (the host provides no dependencies)
    },
    outDir: 'dist',
  },
});
```

After building, point `manifest.json`'s `main` at `dist/index.js`:

```json
{
  "main": "dist/index.js"
}
```

#### Option 2: esbuild

```bash
npm install -D esbuild
```

```json
// package.json
{
  "scripts": {
    "build": "esbuild src/index.ts --bundle --format=esm --outfile=dist/index.js"
  }
}
```

---

## Floating window notes

For the `contributes.windows` configuration (detailed in the [Manifest Reference](./manifest#contributeswindows)), a few extra notes:

- Floating windows are created by the **Electron main process**, in a different process from the plugin JS
- The floating window entry script runs through the host's floating-window loader and receives a **dedicated floating window context** (`activateWindow(ctx)` / `activate(ctx)` / default function) with only the subset of APIs needed to render the window
- See [Windows & System →](./windows-system) and the [EchoMusicPlugins floating window guide](https://github.com/hoowhoami/EchoMusicPlugins/blob/main/docs/floating-windows.md) for details

---

## Publishing checklist

Before publishing, verify each item:

- [ ] `manifest.json` is valid JSON with the correct format
- [ ] `id` is unique and conflict-free
- [ ] `version` follows semver
- [ ] `capabilities` follows least privilege
- [ ] The entry file has no bare imports (no `import from 'vue'`)
- [ ] `requires.echoMusicVersion` has a sensible range
- [ ] Tested in EchoMusic
- [ ] `echo-plugins.json` contains no version/description/author (they belong in manifest.json)

---

## Next Steps

- [API Overview →](./context-api) — full ctx API reference
- [Windows & System →](./windows-system) — floating windows, desktop lyric, mini player
- [📊 Popularity & Stats →](./marketplace-stats) — popularity methodology and stat queries
- [Plugin Development Overview →](./) — back to the overview
- [EchoMusicPlugins repository →](https://github.com/hoowhoami/EchoMusicPlugins) — official plugin examples
