---
title: Preferences
---

# ⚙️ Preferences

EchoMusic offers a wide range of personalization options to make the player look and feel just the way you like it.

## Appearance

EchoMusic supports multiple appearance modes for different usage scenarios:

| Theme | Description |
|------|------|
| 🌞 Light Mode | Bright and clean, ideal for daytime use |
| 🌙 Dark Mode | Eye-friendly and comfortable, ideal for nighttime or low-light environments |
| 🔄 Auto Switch | Follows system settings to switch between light and dark modes |

Switch themes in **Settings → Appearance**.

### Global Theme Color

EchoMusic supports three theme color modes:

| Mode | Description |
|------|------|
| Follow Cover | Automatically extracts the dominant color from the current song's cover for a visually consistent color experience |
| Preset Themes | Choose from built-in color schemes |
| Custom Color | Manually pick your preferred color |

Switch modes in **Settings → Appearance → Theme Color**.

### Font Settings

Customize the application font:

- Select installed system fonts in **Settings → Appearance → Font**
- Adjust font size
- Preview takes effect in real time

### Theme Center & Layout Editing

v2.3.2 adds a unified Theme Center and a brand-new sidebar layout; both the sidebar and the player bar support layout editing, so you can adjust the interface structure to your liking.

### Transparent Background & Frosted Glass

v2.3.1 adds a transparent app background and frosted glass effects, with adjustable opacity and base color; the transparent window edges get a fine stroke adapted to light/dark themes.

## Shortcuts

### Global Shortcuts

Global shortcuts work even when the app is in the background:

| Action | Default Shortcut |
|------|-----------|
| Play / Pause | Media key ▶⏸ |
| Previous | Media key ⏮ |
| Next | Media key ⏭ |
| Volume + | Media key 🔊 |
| Volume - | Media key 🔉 |

### In-App Shortcuts

| Action | Default Shortcut |
|------|-----------|
| Open Search | `Ctrl + F` / `Cmd + F` |
| Play / Pause | `Space` |
| Close Dialog | `Esc` |

Customize shortcuts in **Settings → Shortcuts**; press `Esc` while configuring to clear a shortcut instead of recording it.

Added in v2.3.1: a toggle to disable default browser key behaviors, turning off browser defaults such as Space, arrow keys and page-up/down scrolling and activation.

## System Tray

EchoMusic supports minimizing to the system tray for background playback:

- When you close the window, EchoMusic minimizes to the tray instead of exiting
- Right-click the tray icon for a quick menu:

| Action | Description |
|------|------|
| Play / Pause | Quick playback control |
| Previous / Next | Quick track switching |
| Show Main Window | Open the app interface |
| Quit | Fully exit the app |

- Supports **Mini Mode**: shrink the player to a compact mini window via title bar button
- On macOS (added in v2.3.2), separate toggles can hide the Dock and menu bar icons while the app runs in the background

Adjust tray behavior in **Settings → System**.

## Startup & Updates

| Setting | Description |
|------|------|
| Launch at startup | Auto-run EchoMusic when the system starts |
| Start minimized | Minimize to tray on launch |
| Auto update | Automatically check and download new versions in the background |
| Silent update | Auto-install on next launch after download |

## Network Settings

v2.3.1 adds standalone network settings with several proxy configuration modes:

| Mode | Description |
|------|------|
| Follow system | Use the system proxy settings |
| Forced direct connection | Bypass proxies and connect directly |
| WPAD auto-detection | Detect the proxy via the Web Proxy Auto-Discovery protocol |
| PAC script | Configure the proxy with a PAC script |
| Manual proxy | Enter the proxy server and credentials manually |

The global proxy uniformly covers the Kugou API, covers, audio direct links, updates, plugins and other app network requests.

## Data Management

### Local Storage

EchoMusic uses a local SQLite database to store:

- Playback history
- Favorites (songs, playlists)
- Play queue state
- Personal preferences

::: info
All personal data is stored locally only — nothing is uploaded to the cloud. Your privacy is protected.
:::

### Data Clearing

Clear data in **Settings → Data**:

- Playback history
- Search history
- Cache data

### Backup & Restore

v2.3.1 adds backup and restore for app settings, plugins and plugin data, letting you quickly restore your configuration after switching devices or reinstalling.

## Playback Settings

| Setting | Description |
|------|------|
| Crossfade duration | Transition effect duration when switching tracks (0-5 seconds) |
| Default volume | Volume level on startup |
| Auto-resume playback | Continue playing from where you left off on startup |
| MV audio fallback | Falls back to audio playback when the MV video source is unavailable (added in v2.3.2, disabled by default) |

## Account Management

- v2.3.2 adds multi-account switching management, supporting multiple accounts with quick switching
- The profile center supports viewing and editing your profile and avatar (added in v2.3.1)
- v2.3.1 adds login device management in the profile center: view the current account's logged-in devices and remove non-local devices

## About

View in **Settings → About**:

- App version number
- Open source license information
- Open source dependency acknowledgements
- Check for updates