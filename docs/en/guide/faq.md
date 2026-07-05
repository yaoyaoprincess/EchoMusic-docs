---
title: FAQ
---

# ❓ FAQ

## Installation & Startup

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

## Playback Issues

### Can't Play Songs

1. Check your network connection
2. Verify you're logged in correctly
3. Try switching audio quality (some qualities may require VIP)
4. Restart the app

### Playback Failed: "Temporarily Unable to Get Available Audio Source"

1. Check if you have a VIP membership
2. If not, you can manually sign in on the **Kugou Concept Edition** mobile app to claim VIP
3. Alternatively, search GitHub for automated sign-in tools

### Creating/Favoriting Playlists Fails After Login

Please check whether your account is a **Kugou Concept Edition account**. If not, register a Kugou Concept Edition account and log in again.

### Stuttering or Intermittent Playback

1. Lower the audio quality (Settings → Quality → Standard)
2. Check network stability and speed
3. Close other apps using network bandwidth

### Can't Switch Audio Quality

Some songs may only offer specific quality tiers:

- Hi-Res and SQ require a VIP account
- Older songs may only have standard quality

### Lyrics Out of Sync

1. Try switching the lyrics source (if multiple versions are available)
2. Adjust the lyrics delay in lyrics settings
3. Some songs may not have precise word-level lyrics and fall back to LRC

## Feature Issues

### Music Recognition Not Working

- **Microphone mode**: Ensure microphone permission is granted and the environment isn't too noisy
- **System audio mode**: Ensure audio is actually playing on your system

### Personal FM Recommendations Inaccurate

FM recommendations are based on your listening history and feedback:

1. Use the "Like" and "Dislike" buttons more often
2. It takes some listening accumulation for recommendations to become accurate
3. Listen to diverse music to enrich recommendation dimensions

### Favorited Songs Disappeared

1. Confirm you're logged into the correct account
2. Favorites data is stored locally — switching devices won't sync
3. If you cleared app data, favorites are lost

### Can I Download Music?

**No.** EchoMusic does not provide music file download functionality, nor does it cache audio files locally.

### The Old Version Had Auto VIP Claim, Why Is It Gone?

This feature was removed to avoid risks. You can manually sign in on the Kugou Concept Edition mobile app to claim VIP, or search GitHub for automated sign-in tools.

## Account Issues

### Is It Free?

**Yes.** EchoMusic is completely free and open source. If you obtained it through a paid channel, you've been scammed.

### Account Security

- EchoMusic connects directly to Kugou's official servers
- Account data never passes through third parties
- We recommend using a strong password to protect your Kugou account

### How to Log Out / Switch Accounts

Go to **Settings → Account** and select log out, then log in with another account.

## Updates & Network

### Slow Download Speed / Can't Get Latest Version / Plugin System Won't Load Latest Plugins

Configure a GitHub acceleration proxy in **Settings → Experimental Features → GitHub Acceleration Settings** (see group announcement for details).

## Updates & Feedback

### How to Check for Updates

EchoMusic automatically checks for updates on launch. You can also check manually: **Settings → About → Check for Updates**.

### How to Report Issues

- [GitHub Issues](https://github.com/hoowhoami/EchoMusic/issues) — Report bugs or suggest features
- QQ Group: 1036693403
- Telegram: [@EchoMusicGroup](https://t.me/+H9vpkAJrDlViZjU1)

### How to Contribute

Please read the [Contributing Guide](/en/develop/contributing). Pull Requests are welcome!

## Platform Limitations

### Mobile Support?

No. EchoMusic is designed exclusively for desktop and will not support Android/iOS or other mobile platforms.

### Will There Be Mobile/Car/TV Clients?

EchoMusic is designed exclusively for desktop. There are no plans to support other platforms.

### Windows: Only Uninstaller Present After Installation, No Main Program

You installed an architecture-mismatched package. If you don't know your PC's architecture, use the **x64 installer** (available in the group files).