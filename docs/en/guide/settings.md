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

Customize shortcuts in **Settings → Shortcuts**.

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

Adjust tray behavior in **Settings → System**.

## Startup & Updates

| Setting | Description |
|------|------|
| Launch at startup | Auto-run EchoMusic when the system starts |
| Start minimized | Minimize to tray on launch |
| Auto update | Automatically check and download new versions in the background |
| Silent update | Auto-install on next launch after download |

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

## Playback Settings

| Setting | Description |
|------|------|
| Crossfade duration | Transition effect duration when switching tracks (0-5 seconds) |
| Default volume | Volume level on startup |
| Auto-resume playback | Continue playing from where you left off on startup |

## About

View in **Settings → About**:

- App version number
- Open source license information
- Open source dependency acknowledgements
- Check for updates