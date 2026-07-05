---
title: Installation & Startup
---

# 🚀 Installation & Startup

### macOS: "Cannot Verify Developer"

This is macOS's security mechanism and doesn't affect normal usage. Solutions:

```bash
# Method 1: Run in Terminal
xattr -cr /Applications/EchoMusic.app

# Method 2: System Settings
# System Settings → Privacy & Security → Click "Open Anyway"
```

### Windows: "Windows Protected Your PC"

Click "More info" → "Run anyway".

### Windows: Only Uninstaller Present After Installation, No Main Program

You installed an architecture-mismatched package. If you don't know your PC's architecture, use the **x64 installer** (available in the group files).

### Linux: AppImage Won't Run

Ensure it has executable permissions:

```bash
chmod +x EchoMusic-*.AppImage
./EchoMusic-*.AppImage
```

### App Crashes on Launch

1. Check if your system meets the minimum requirements
2. Try running with administrator/root privileges
3. Check if security software is blocking it

### "Playback Engine Initialization Failed"

Please update to the latest version. If you're already on the latest version, contact the developer.

### "Device Registration Failed"

1. Check your network environment
2. Disable any proxy/accelerator and retry
3. If it still doesn't work, try switching to a different network (e.g., mobile hotspot)

### App Won't Start or Fails to Launch

Run the following command in the program's root directory, then take a screenshot of the terminal output and share it in the community group:

```bash
.\EchoMusic.exe --console
```
