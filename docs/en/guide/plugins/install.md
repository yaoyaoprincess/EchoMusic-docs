---
title: Installing Plugins
---

# 📥 Installing Plugins

## Online Plugin Source (Recommended)

EchoMusic includes a built-in online plugin source for browsing and installing:

1. Open EchoMusic and go to "**Plugin Manager**"
2. Click the "**Online Plugins**" tab
3. Browse the available plugin list
4. Click "**Install**" — the plugin will download and install automatically

## One-Click Updates

v2.2.7 introduced a **one-click plugin update** feature. When an installed plugin has a new version available, the Plugin Manager will show an update prompt — click to upgrade to the latest version.

## Adding Third-Party Plugin Sources

You can add other GitHub repositories as plugin sources:

1. In Plugin Manager → Online Plugins, click "**Add Source**"
2. Enter the plugin source URL, for example:
   ```
   https://github.com/username/echo-plugins-source
   ```
3. After refreshing, plugins from that source will appear

## Manual Installation

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

## 💡 Where Is the Plugin Directory

- **Windows**: `%APPDATA%/echomusic/plugins/`
- **macOS**: `~/Library/Application Support/echomusic/plugins/`
- **Linux**: `~/.config/echomusic/plugins/`

You can also open it via Plugin Manager → "Open Directory".

---

- [← Plugin System Overview](./)
- [📋 Plugin List →](./list)
