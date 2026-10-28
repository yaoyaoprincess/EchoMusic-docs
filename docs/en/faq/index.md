---
title: FAQ
---

# ❓ FAQ

Having trouble? Browse the categories below — each question links to a dedicated page with detailed solutions.

## Installation & Startup

| Question | Quick answer |
|----------|--------------|
| [How do I download EchoMusic?](/en/faq/install#download) | From GitHub Releases or the QQ group files; pick the package matching your system. |
| [Windows says "Windows protected your PC"](/en/faq/install#windows-smartscreen) | SmartScreen warning — click **More info**, then **Run anyway**. |
| [No main program after installing on Windows, only an uninstaller](/en/faq/install#wrong-arch) | Wrong-architecture installer. Re-download the correct one; x64 works if unsure. |
| [macOS says the developer cannot be verified](/en/faq/install#macos-gatekeeper) | Gatekeeper blocks unverified apps. Run `xattr -cr` or click **Open Anyway**. |
| [Linux AppImage won't run](/en/faq/install#appimage) | Add executable permission with `chmod +x`, then run it from the terminal. |
| [The app crashes right after launch](/en/faq/install#crash-on-start) | Check system requirements, try admin/root privileges, and check security software. |
| [Engine initialization / device registration fails on startup](/en/faq/install#engine-init-fail) | Disable proxies, whitelist the app, switch networks, update, then export logs. |
| [How do I start via command line to capture logs?](/en/faq/install#console-log) | Run `.\EchoMusic.exe --console` from the installation directory. |

## Playback & Quality

| Question | Quick answer |
|----------|--------------|
| [Playback fails with "no available audio source"](/en/faq/playback#no-audio-source) | Check VIP, enable Smart Compatibility Mode, bypass proxies, update, then export logs. |
| [Songs won't play](/en/faq/playback#cannot-play) | Check network and login in order, try another quality, then restart the app. |
| [How do I listen to Viper Mastering / Viper Ultra / Viper Spatial audio?](/en/faq/playback#viper-audio) | Requires Kugou SVIP; then enable Viper quality in Settings → Playback. |
| [A song skips to the next one before it finishes](/en/faq/playback#auto-skip) | Adjust Song Transition in Settings → Playback; see the Playback guide. |
| [I can't switch the audio quality](/en/faq/playback#quality-switch) | Hi-Res/SQ need VIP; older songs may only offer standard quality. |
| [Playback stutters or buffers](/en/faq/playback#stutter) | Lower the quality, check your network, and close bandwidth-heavy programs. |
| [Lyrics are out of sync](/en/faq/playback#lyrics-sync) | Switch the lyrics source, adjust the delay, or rely on the LRC fallback. |

## Account & Membership

| Question | Quick answer |
|----------|--------------|
| [Do I need to pay?](/en/faq/account#free) | Completely free and open source; anyone charging you is scamming you. |
| [How do I claim Kugou Concept Edition VIP?](/en/faq/account#get-vip) | Sign in daily in the Concept Edition app; unofficial auto check-in tools carry risks. |
| [Can I listen without a VIP?](/en/faq/account#listen-without-vip) | Yes — free SD previews plus the Try MV audio fallback; higher quality needs VIP. |
| [VIP claim fails or VIP songs won't play](/en/faq/account#vip-verify) | Re-login on mobile, then log out, clear data and re-verify on desktop. |
| [Creating playlists or saving favorites fails](/en/faq/account#playlist-fail) | Re-scan the QR code with the Concept Edition app; Kugou and Concept accounts are separate. |
| [How do I log out or switch accounts?](/en/faq/account#switch-account) | Go to Settings → Account and log out, then sign in with another account. |
| [Is my account safe?](/en/faq/account#account-safety) | Direct connection to Kugou's servers, no third parties; use a strong password. |

## Features

| Question | Quick answer |
|----------|--------------|
| [Can I download music?](/en/faq/features#download-music) | No — the project explicitly will never support downloads. Find other channels yourself. |
| [How do I add local music?](/en/faq/features#local-music) | Install the Echo Local Simple or Local Music plugin from Online Plugins. |
| [How do I listen to songs not in the Kugou library?](/en/faq/features#cloud-drive) | Music cloud drive with Cloud Priority, embedded metadata, or the local music plugin. |
| [Music recognition doesn't work](/en/faq/features#music-recognition) | Grant microphone permission, and make sure system audio is actually playing. |
| [Personal FM recommendations are off](/en/faq/features#personal-fm) | Use Like/Dislike feedback often; accuracy improves with listening accumulation. |
| [My favorited songs are gone](/en/faq/features#favorites-lost) | Favorites are local — wrong account, device switching or cleared data loses them. |

## Updates & Feedback

| Question | Quick answer |
|----------|--------------|
| [How do I check for updates?](/en/faq/updates#check-update) | Automatic on launch, or manually via Settings → About → Check for updates. |
| [Auto-update fails or downloads slowly](/en/faq/updates#update-slow) | The old Experimental path is deprecated; set a GitHub acceleration address in Settings → Network. |
| [I see net::ERR_CONNECTION XXX](/en/faq/updates#err-connection) | Fill in a GitHub acceleration address, or choose Direct connection in Settings → Network. |
| [How do I report a problem?](/en/faq/updates#feedback) | GitHub Issues, QQ Group 1036693403, or Telegram. |
| [How do I contribute code?](/en/faq/updates#contributing) | Read the Contributing Guide and open a pull request. |

## Platform Limitations

| Question | Quick answer |
|----------|--------------|
| [Is there a mobile version?](/en/faq/platform#mobile) | No Android/iOS support; use the official Kugou Concept Edition app on mobile. |
| [Will there be mobile / car / TV versions?](/en/faq/platform#other-platforms) | Desktop-only by design; no mobile, car or TV plans. |

## Still can't find an answer?

- [GitHub Issues](https://github.com/hoowhoami/EchoMusic/issues) — report bugs or suggest features
- QQ Group: **1036693403**
- Telegram: [@EchoMusicGroup](https://t.me/+H9vpkAJrDlViZjU1)
