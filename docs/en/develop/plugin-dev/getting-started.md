---
title: Getting Started
outline: [2, 4]
---

# 🚀 Getting Started

This guide walks you through creating your first EchoMusic plugin in just 5 minutes.

## Prerequisites

- **EchoMusic ≥ 2.2.6-beta.9** installed
- A text editor (VS Code recommended)
- Basic JavaScript knowledge

## Step 1: Create the Plugin Directory

Open EchoMusic's plugin directory in your file manager and create a new folder:

```
EchoMusic/
  plugins/              ← Plugin root directory
    hello-echo/         ← Your plugin directory
```

> 💡 In EchoMusic, go to Settings → Plugins → click "Open Plugin Directory" to quickly navigate there.

## Step 2: Write manifest.json

Create `manifest.json` inside `hello-echo/`:

```json
{
  "id": "hello-echo",
  "name": "Hello Echo",
  "version": "1.0.0",
  "description": "My first EchoMusic plugin",
  "author": "Your Name",
  "main": "index.js",
  "requires": {
    "echoMusicVersion": ">=2.2.6-beta.9"
  }
}
```

### Minimum manifest.json Fields

| Field | Description |
|-------|-------------|
| `id` | Unique plugin identifier, use `kebab-case`, e.g. `hello-echo` |
| `name` | Plugin name displayed in the plugin manager |
| `version` | [Semantic version](https://semver.org/), e.g. `1.0.0` |
| `main` | Entry file, usually `index.js` |

These three fields are required. Other fields (`description`, `author`, `icon`, etc.) are optional but recommended.

## Step 3: Write the Entry File

Create `index.js` inside `hello-echo/`:

```js
// hello-echo/index.js

/**
 * Called when the plugin is enabled
 * @param {object} ctx — Plugin context, gateway to all APIs
 */
export function activate(ctx) {
  // Display a welcome toast
  ctx.toast.success(`🎉 ${ctx.manifest.name} enabled!`);

  // Log plugin info to console
  console.log(`[${ctx.manifest.id}] Plugin activated, version ${ctx.manifest.version}`);

  // Listen for track changes
  ctx.events.onTrackChange((track) => {
    console.log(`[${ctx.manifest.id}] Now playing: ${track.title}`);
  });
}

/**
 * Called when the plugin is disabled or before uninstall
 * Clean up resources (timers, DOM modifications, etc.)
 */
export function deactivate(ctx) {
  console.log(`[${ctx.manifest.id}] Plugin deactivated`);

  // Most registered resources (event listeners, pages, settings, menus, etc.)
  // are automatically cleaned up by EchoMusic — no manual removal needed
}
```

### Entry File Rules

| Rule | Description |
|------|-------------|
| **ESM format** | Entry files are loaded as browser ESM, use `export` |
| **Two export functions** | `activate(ctx)` and `deactivate(ctx)`, both async-safe |
| **No bare imports** | Don't write `import { ref } from 'vue'`, use `ctx.vue.ref` instead |
| **File name** | Specified by the `main` field in manifest, supports `.js` and `.mjs` |

## Step 4: Test the Plugin

1. **Restart EchoMusic** (or open the plugin manager — EchoMusic auto-scans for new plugins)
2. Go to **Settings → Plugin Manager**
3. Find "Hello Echo" and click **Enable**
4. You should see "🎉 Hello Echo enabled!" pop up in the bottom-right corner

### Quick Reload

When making frequent code changes during development:

- **Disable and re-enable** the plugin from the plugin manager
- Changes to `manifest.json` require a restart to take effect
- Changes to `index.js` take effect after re-enabling

## Step 5: Add More Features

Now that you have a working plugin, you can gradually add functionality:

```js
export function activate(ctx) {
  // 1. Add a right-click context menu item
  ctx.ui.addSongContextMenuItem({
    id: "copy-song-info",
    label: "Copy Song Info",
    async onSelect(song) {
      const info = `${song.title} - ${song.artist}`;
      await navigator.clipboard.writeText(info);
      ctx.toast.success("Song info copied");
    },
  });

  // 2. Register a plugin settings panel
  const SettingsPanel = {
    setup() {
      return () =>
        ctx.vue.h("div", { style: "padding: 12px;" }, [
          ctx.vue.h("p", "My first plugin 🎉"),
        ]);
    },
  };

  ctx.ui.settings.define({
    title: "Hello Echo Settings",
    component: SettingsPanel,
  });

  // 3. Register a page
  ctx.ui.addPage({
    id: "hello-page",
    title: "Hello Echo",
    icon: "🎵",
    component: {
      setup() {
        return () =>
          ctx.vue.h("div", { class: "page-container" }, [
            ctx.vue.h("h1", "Hello Echo"),
            ctx.vue.h("p", `Current time: ${new Date().toLocaleString()}`),
          ]);
      },
    },
  });
}
```

## Complete Directory Structure

After completing the steps above, your plugin directory should look like this:

```
hello-echo/
  manifest.json      ← Plugin description, version, permissions
  index.js           ← Plugin entry (ESM)
```

Optional extensions:

```
hello-echo/
  manifest.json
  index.js
  style.css          ← Optional: styles injected into the page
  icon.svg           ← Optional: plugin icon (SVG/PNG)
  float.html         ← Optional: floating window page (requires contributes.windows in manifest)
```

## Debugging Tips

### Using Developer Tools

1. Press `F12` or `Ctrl+Shift+I` in EchoMusic to open DevTools
2. Switch to the **Console** tab to see `console.log` output
3. Errors appear in red — click to jump to the source location

### Common Error Troubleshooting

| Symptom | Possible Cause | Solution |
|---------|---------------|----------|
| Plugin not appearing in list | malformed `manifest.json` | Check JSON syntax, ensure field names use double quotes |
| "Version incompatible" | `echoMusicVersion` range doesn't match | Update EchoMusic or relax the version requirement |
| No response after enabling | Syntax error in `index.js` | Open DevTools Console to check errors |
| Plugin name shown as id | Missing `name` field | Add `name` in manifest |
| `ctx.xxx` is undefined | Missing capability declaration | Add the corresponding capability in manifest |

## Next Steps

- [Manifest Reference →](./manifest) — Learn all manifest fields
- [Context API Reference →](./context-api) — Browse the complete `ctx` API
- [UI Extension Guide →](./ui-extension) — Learn how to customize the interface
- [Player & Audio →](./player-audio) — Playback control and audio processing
