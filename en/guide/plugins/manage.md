---
title: Management & Safety
---

# ⚙️ Management & Safety

## Managing Plugins

| Action | Description |
|--------|-------------|
| **Enable/Disable** | Toggle the switch on the plugin card. Disabling calls the plugin's `deactivate` to clean up registered resources |
| **Uninstall** | Click the delete button — removes the plugin directory, data, and fault records |
| **Settings** | Some plugins offer settings panels — click the gear icon to configure |
| **Update** | For online-installed plugins, update to the latest version with one click in Plugin Manager |

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

EchoMusic tracks plugin startup and runtime state. If a plugin causes a renderer process crash, the main process will automatically attempt to switch to safe mode and reload the window. If the app is force-closed or the renderer becomes unresponsive, safe mode is also automatically activated on the next launch.

The Plugin Manager marks affected plugin cards with ⚠️ warning indicators for startup failures, runtime errors, or recent suspected faults. Click to view the error source, timestamp, message, and stack trace — you can also clear a plugin's error records.

## Troubleshooting

If you encounter plugin issues:

1. **Enable Safe Mode**: First enter safe mode to confirm the problem is plugin-related
2. **Isolate**: Disable safe mode and enable plugins one by one to find the culprit
3. **Check Fault Records**: The Plugin Manager marks faulty plugins with ⚠️ — click to view error source, time, message, and stack trace
4. **Clear Records**: Once resolved, you can clear the fault records

::: warning Note
Plugins run in the renderer process with elevated privileges. Only install plugins from trusted sources. If you're unsure about a plugin, review its code before installing.
:::

## Command Line Arguments

| Argument | Description |
|----------|-------------|
| `--safe-mode` | Start in safe mode without loading any plugins |

---

- [← Plugin List](./list)
- [Plugin System Overview →](./)
- [🔌 Plugin Development Guide →](/en/develop/plugin-dev/)
