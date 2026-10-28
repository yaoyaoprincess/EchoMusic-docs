---
title: Installation & Startup
---

# 🚀 Installation & Startup

### How do I download EchoMusic? {#download}

Download from [GitHub Releases](https://github.com/hoowhoami/EchoMusic/releases) or the QQ group files:

| System | Package |
|--------|---------|
| Windows | `Windows-Setup-x64` |
| macOS (Intel) | `mac-x64` |
| macOS (Apple Silicon) | `macOS-arm64` |

> The group files only host the Windows package. For macOS and Linux, download from GitHub Releases.

### Windows says "Windows protected your PC" {#windows-smartscreen}

This is SmartScreen blocking an app from an unverified publisher. Click **More info** → **Run anyway**.

### No main program after installing on Windows, only an uninstaller {#wrong-arch}

You installed the wrong-architecture installer. Check your system architecture and re-download the matching package; if you are unsure, use the **x64 installer**.

### macOS says the developer cannot be verified {#macos-gatekeeper}

This is Gatekeeper protecting you from apps by unidentified developers. Either fix it from the Terminal:

```bash
xattr -cr /Applications/EchoMusic.app
```

Or open **System Settings → Privacy & Security**, find the blocked EchoMusic prompt and click **Open Anyway**.

### Linux AppImage won't run {#appimage}

Grant it executable permission first:

```bash
chmod +x EchoMusic-*.AppImage
./EchoMusic-*.AppImage
```

### The app crashes right after launch {#crash-on-start}

1. Check that your system meets the minimum requirements
2. Try running with administrator (Windows) or root (Linux/macOS) privileges
3. Check whether security software is blocking the app

### "Playback engine initialization failed" or "Device registration failed" on startup {#engine-init-fail}

1. Disable your proxy — in **Settings → Network** choose **Direct connection** and apply
2. Whitelist EchoMusic in your security software (Windows Defender, App Control, etc.)
3. Switch to a different network (e.g. a mobile hotspot) and retry
4. If the engine fails to initialize, update to the latest version first
5. If none of this helps, click **Enter Anyway** on the dialog to get into the app, export the logs in settings and send them for feedback

### How do I start via command line to capture logs? {#console-log}

Run the following command in the app's installation directory:

```powershell
.\EchoMusic.exe --console
```

The terminal prints the runtime logs — take a screenshot and share it when reporting a problem.
