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
      ├── style.css      ← Optional
      └── icon.svg       ← Optional
```

> Downside: users can't receive automatic updates.

---

## Online Plugin Registry

An online registry lets users **browse, one-click install, and auto-update** plugins from within EchoMusic's plugin manager.

### How It Works

```
  ┌─────────────┐     fetch echo-plugins.json     ┌──────────────┐
  │  EchoMusic   │ ───────────────────────────────▶│  GitHub Repo  │
  │ Plugin Manager│                                  │  (Registry)   │
  │              │ ◀───────────────────────────────│              │
  │ Show plugin  │      Return plugin index data    └──────────────┘
  │ list         │
  └──────┬───────┘
         │ User clicks "Install"
         ▼
  ┌─────────────┐     clone / download              ┌──────────────┐
  │ Local plugin │ ◀─────────────────────────────────│  Plugin Repo  │
  │ directory    │                                    └──────────────┘
  └─────────────┘
```

### Step 1: Create a Registry Repository

Create a GitHub repository (e.g. `my-echo-plugins`) and add `echo-plugins.json` at the root:

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

### echo-plugins.json Fields

#### Root-Level Fields

| Field | Type | Required | Description |
|-------|------|:--:|------|
| `name` | `string` | ✅ | Registry name |
| `homepage` | `string` | ❌ | Registry homepage URL |
| `plugins` | `array` | ✅ | List of included plugins |

#### plugins[] Entry Fields

| Field | Type | Required | Description |
|-------|------|:--:|------|
| `id` | `string` | ✅ | Plugin ID, must match `id` in manifest.json |
| `path` | `string` | ✅ | Plugin directory path within the repo (empty string = repo root) |
| `repo` | `string` | ❌ | Plugin source repository URL; leave empty to use the registry repo |
| `homepage` | `string` | ❌ | Plugin detail page or documentation link |
| `tags` | `string[]` | ❌ | Category tags for filtering and searching in the online list |

> ⚠️ **Do not include `version`, `description`, or `author` in `echo-plugins.json`.** These belong to each plugin's `manifest.json`. EchoMusic reads them automatically from the plugin repository.

### Step 2: Place Plugins in the Repository

If the plugin lives in a separate repository (recommended):

```
your-name/lyric-enhancer/        ← Independent plugin repo
  ├── manifest.json
  ├── index.js
  ├── style.css
  └── icon.svg
```

Then reference it in the registry's `echo-plugins.json`:

```json
{
  "id": "lyric-enhancer",
  "path": "",                    ← Empty string because the repo root is the plugin
  "repo": "https://github.com/your-name/lyric-enhancer"
}
```

If multiple plugins are in the same repository:

```
your-name/my-echo-plugins/       ← Registry repository
  ├── echo-plugins.json
  ├── lyric-enhancer/            ← Plugin 1
  │   ├── manifest.json
  │   └── index.js
  └── mini-spectrum/             ← Plugin 2
      ├── manifest.json
      └── index.js
```

Corresponding `echo-plugins.json`:

```json
{
  "plugins": [
    {
      "id": "lyric-enhancer",
      "path": "lyric-enhancer",   ← Points to subdirectory
      "repo": ""                  ← Empty, uses this repo
    },
    {
      "id": "mini-spectrum",
      "path": "mini-spectrum",
      "repo": ""
    }
  ]
}
```

### Step 3: Users Add the Registry in EchoMusic

1. Open EchoMusic → Settings → Plugin Manager
2. Click "Add Plugin Registry"
3. Enter the registry repository URL: `https://github.com/your-name/my-echo-plugins`
4. EchoMusic automatically fetches `echo-plugins.json` and displays available plugins

---

## Version Management

### version in manifest.json

Plugin version is defined in `manifest.json` following [Semantic Versioning](https://semver.org/):

```json
{
  "version": "1.2.0"
}
```

### Update Detection

EchoMusic compares the locally installed plugin `version` with the online registry's `manifest.json` `version`:

| Scenario | EchoMusic Behavior |
|----------|-------------------|
| Online version > local version | Shows "Update available", prompts user to upgrade |
| Online version = local version | Shows "Up to date" |
| Local version not found in registry | No automatic update prompt |

### Version Upgrade Guidelines

```json
// Bug fix: bump PATCH
"version": "1.0.0" → "1.0.1"

// New feature (backward compatible): bump MINOR, reset PATCH
"version": "1.0.5" → "1.1.0"

// Breaking change: bump MAJOR, reset MINOR and PATCH
"version": "1.5.2" → "2.0.0"
```

---

## Using TypeScript / Vue SFC

Plugin entries run in a browser ESM environment. If you need TypeScript or `.vue` single-file components, you must first bundle them into plain JavaScript ESM.

### Recommended Toolchain

#### Option 1: Vite (Recommended)

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
      entry: 'src/index.ts',        // Entry point
      formats: ['es'],              // ESM format
      fileName: () => 'index.js',   // Output filename
    },
    rollupOptions: {
      external: [],                 // Don't exclude any deps (host provides none)
    },
    outDir: 'dist',
  },
});
```

After building, point `main` in `manifest.json` to `dist/index.js`:

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

## Floating Window Supplement

Regarding `contributes.windows` configuration (detailed in [Manifest Reference](./manifest#contributeswindows)), here are additional tips:

- Floating windows are created by the **Electron main process** and run in a different process from your plugin JS
- The floating window's HTML can use `<script>` tags, but cannot directly access `ctx`
- For communication between the floating window and main window, use `postMessage` or Electron IPC (via host-provided bridges)
- See the [EchoMusicPlugins Windows Docs](https://github.com/hoowhoami/EchoMusicPlugins/blob/main/docs/windows.md) for detailed documentation

---

## Release Checklist

Before publishing your plugin, verify each item:

- [ ] `manifest.json` is well-formed, valid JSON
- [ ] `id` is unique, no conflicts
- [ ] `version` follows semver
- [ ] `capabilities` follows the principle of least privilege
- [ ] Entry file has no bare imports (no `import from 'vue'`)
- [ ] `requires.echoMusicVersion` range is reasonable
- [ ] Tested successfully in EchoMusic
- [ ] `echo-plugins.json` does not include version/description/author (belongs to manifest.json)

---

## Next Steps

- [Plugin Development Overview →](./) — Back to overview
- [Context API Reference →](./context-api) — Complete ctx API reference
- [EchoMusicPlugins Repository →](https://github.com/hoowhoami/EchoMusicPlugins) — Official plugin examples
