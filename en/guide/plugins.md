---
title: Plugin System
---

# 🧩 Plugin System

EchoMusic supports a full plugin system starting from v2.2.6-beta.11. Plugins can extend the interface, add functionality, and customize the appearance — letting you build your own music experience.

## What Are Plugins

Plugins are small code packages written by the community or yourself. They can:

- 📌 Register custom pages or sidebar entries
- 🎨 Inject custom CSS styles
- 🎵 Monitor player state and control playback
- 🖼️ Create desktop floating windows (e.g., Dynamic Island lyrics)
- 📝 Provide custom lyrics or lyric effects
- 🔍 Intercept audio source resolution for specific songs
- ⚙️ Add settings panels
- 📋 Add custom menu items to track context menus

The plugin model is similar to VS Code / Obsidian's high-freedom local extensions: EchoMusic provides the host API, and plugins run freely.

## Installing Plugins

### Online Plugin Source (Recommended)

EchoMusic includes a built-in online plugin source for browsing and installing:

1. Open EchoMusic and go to "**Plugin Manager**"
2. Click the "**Online Plugins**" tab
3. Browse the available plugin list
4. Click "**Install**" — the plugin will download and install automatically

### Adding Third-Party Plugin Sources

You can add other GitHub repositories as plugin sources:

1. In Plugin Manager → Online Plugins, click "**Add Source**"
2. Enter the plugin source URL, for example:
   ```
   https://github.com/hoowhoami/EchoMusicPlugins
   ```
3. After refreshing, plugins from that source will appear

### Manual Installation

1. In Plugin Manager, click "**Open Directory**"
2. Copy the downloaded plugin folder (containing `manifest.json`) into it
3. Return to EchoMusic — the plugin will appear automatically in the list

```
<EchoMusic plugin directory>/
  hello-echo/
    manifest.json
    index.js
    style.css
```

## Managing Plugins

| Action | Description |
|--------|-------------|
| **Enable/Disable** | Toggle the switch on the plugin card. Disabling calls `deactivate` to clean up registered resources |
| **Uninstall** | Click the delete button — removes the plugin folder, data, and fault records |
| **Settings** | Some plugins offer settings panels — click the gear icon to configure |
| **Update** | For online-installed plugins, the manager checks for updates automatically |

## Safe Mode

EchoMusic provides a global "**Plugin Safe Mode**". When enabled, no plugins are loaded, but each plugin's enabled state is preserved.

### When to Use Safe Mode

- A plugin causes the UI to freeze or crash
- The window is unresponsive after launch
- Debugging plugin compatibility issues

### Entering Safe Mode

**Method 1: Plugin Manager**

Toggle "Plugin Safe Mode" in the Plugin Manager, then restart the app.

**Method 2: Command Line**

```bash
EchoMusic --safe-mode
```

In development:

```bash
pnpm exec electron . --safe-mode
```

### Auto-Trigger

EchoMusic tracks plugin startup and runtime state. If a plugin causes a renderer process crash, the main process will automatically attempt to switch to safe mode and reload the window.

## Troubleshooting

If you encounter plugin issues:

1. **Enable Safe Mode**: Confirm the problem is plugin-related
2. **Isolate**: Disable safe mode and enable plugins one by one to find the culprit
3. **Check Fault Records**: Plugin cards show ⚠️ warnings for faulty plugins — click to view error source, time, message, and stack trace
4. **Clear Records**: Once resolved, you can clear the fault records

::: warning Note
Plugins run in the renderer process with elevated privileges. Only install plugins from trusted sources. If you're unsure about a plugin, review its code before installing.
:::

## Command Line Arguments

| Argument | Description |
|----------|-------------|
| `--safe-mode` | Start in safe mode without loading any plugins |

---

- [Plugin Development Guide →](/develop/plugin-dev/)
- [EchoMusic Plugin Repository →](https://github.com/hoowhoami/EchoMusicPlugins)
