---
title: Getting Started
---

# 🚀 Getting Started

This guide will help you download, install, and launch EchoMusic.

## Download

Visit the [GitHub Releases](https://github.com/hoowhoami/EchoMusic/releases) page and download the package for your platform:

| Platform | Package Format |
|------|-----------|
| **macOS** | `.dmg` (recommended), `.zip` |
| **Windows** | `.exe` installer (recommended), `portable` |
| **Linux** | `.deb`, `.rpm`, `.AppImage` (recommended), `.tar.gz` |

Not sure which format to download? Click the button below!

::: info Recommendation
Pre-release versions are recommended — they update more frequently with new features and faster bug fixes.
:::

<DownloadButton version="both" type="card" :show-version="true" />

### macOS Installation

1. Download the `.dmg` file
2. Double-click to open, drag `EchoMusic.app` into the `Applications` folder
3. On first launch, if you see "Cannot verify developer", run:
   ```bash
   xattr -cr /Applications/EchoMusic.app
   ```
   Or go to **System Settings → Privacy & Security → Open Anyway**

### Windows Installation

1. Download the `.exe` installer
2. Double-click and follow the setup wizard
3. After installation, shortcuts will be created on your desktop and Start Menu

> For the portable version, simply extract and run `EchoMusic.exe` — no installation required.

### Linux Installation

**AppImage (recommended)**:

```bash
chmod +x EchoMusic-*.AppImage
./EchoMusic-*.AppImage
```

**deb package**:

```bash
sudo dpkg -i EchoMusic-*.deb
```

**rpm package**:

```bash
sudo rpm -i EchoMusic-*.rpm
```

## First Launch

1. Launch EchoMusic
2. On first launch, you'll see the login page — log in with your Kugou account
3. Once logged in, start exploring the world of music

::: tip
EchoMusic connects directly to Kugou's official servers. Your data never passes through any third party. Your account information is secure.
:::

## System Requirements

| Component | Minimum |
|------|----------|
| OS | macOS 11+ / Windows 10+ / Linux (mainstream distros) |
| RAM | 4GB |
| Storage | 200MB free space |
| Network | Internet connection required (online streaming) |

## Next Steps

- [Playback](/en/guide/playback) — Learn basic playback controls
- [Music Discovery](/en/guide/music-discovery) — Explore recommendations & charts
- [FAQ](/en/guide/faq) — Find answers to common questions