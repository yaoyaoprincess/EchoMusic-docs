---
title: Features
---

# Features

EchoMusic is a third-party Kugou Concept Music client built for desktop, combining aesthetic design, powerful features, and an exceptional experience.

<div class="feature-cards">

<div class="feature-card">

### 🎨 Stunning Design

Carefully crafted desktop layout with light and dark modes, balancing information density with an immersive experience. Every detail has been polished to make music playback a visual delight.

</div>

<div class="feature-card">

### 🔒 Data Security

Direct connection to official servers — all data bypasses third-party servers. Your login info, listening history, and favorites are fully under your control.

</div>

<div class="feature-card">

### 🎵 Advanced Playback

Play queue management, list loop / single loop / shuffle modes, volume control, progress scrubbing, speed control (0.5x - 2.0x), crossfade transitions — a professional-grade playback experience.

[Learn more →](/en/guide/playback)

</div>

<div class="feature-card">

### 🔍 Multi-Dimensional Discovery

Comprehensive search across songs, artists, albums, and playlists. Home recommendations, charts, new releases, trending artists — make music discovery a pleasure.

[Learn more →](/en/guide/music-discovery)

</div>

<div class="feature-card">

### 📝 Lyrics System

Supports LRC/YRC word-level lyrics parsing with precise scroll sync. Full-screen lyrics mode and desktop lyrics floating window immerse you in every melody.

[Learn more →](/en/guide/lyrics)

</div>

<div class="feature-card">

### 🎚️ Audio Enhancement

10-band EQ equalizer with free adjustment, LUFS-based volume normalization, Viper Master/Surround/Ultra Clear and other sound effect modes. Hi-Res / SQ(flac) / HQ(320) / Standard(128) quality tiers.

[Learn more →](/en/guide/audio)

</div>

<div class="feature-card">

### 🎧 Personal FM

Smart personalized radio recommendations that continuously optimize based on your listening preferences, helping you discover more great music.

[Learn more →](/en/guide/personal-fm)

</div>

<div class="feature-card">

### 🎤 Music Recognition

Supports microphone and system audio capture to quickly identify songs playing around you. Never miss a good song again.

[Learn more →](/en/guide/music-recognition)

</div>

<div class="feature-card">

### 💬 Song Details & Comments

View complete song archives and playback details, browse insightful comments, support comment thread jumping — add more story to your listening experience.

[Learn more →](/en/guide/song-detail)

</div>

<div class="feature-card">

### 🖥️ Cross-Platform

Full support for macOS, Windows, and Linux desktop operating systems. Whatever computer you use, EchoMusic runs perfectly.

</div>

<div class="feature-card">

### ⚙️ Deep System Integration

macOS MPNowPlayingInfoCenter / Windows SMTC / Linux MPRIS native system media controls. System tray quick actions, global shortcuts, audio device switching — EchoMusic truly becomes part of your desktop.

[Learn more →](/en/guide/settings)

</div>

<div class="feature-card">

### 🔄 Auto Updates

Built-in update detection and download with silent updates. Automatically checks for new versions every launch — never miss a new feature.

</div>

<div class="feature-card">

### 🪟 Mini Mode

Shrinks the player into a compact mini window showing only cover art and basic controls. Always on top, perfect for work or multitasking.

[Learn more →](/en/guide/playback#mini-mode)

</div>

<div class="feature-card">

### 🌐 Spatial Audio

Import IR (impulse response) audio files for real-time spatial audio rendering. Simulate different acoustic environments or create personalized virtual surround sound.

[Learn more →](/en/guide/audio#spatial-audio)

</div>

<div class="feature-card">

### 🎤 Vocal / Instrumental Split

One-click switch between vocals-only and accompaniment-only playback. Extracted track data is cached for instant switching on the same song.

[Learn more →](/en/guide/audio#sound-effects)

</div>

<div class="feature-card">

### 🌈 Global Theme Color

Auto-extract from cover art, preset themes, or custom color — three modes. The entire app's color scheme changes with your preference.

[Learn more →](/en/guide/settings#global-theme-color)

</div>

<div class="feature-card">

### 📥 External Playlist Import

Import playlists from multiple music platforms. One-click migration of your collections — break free from platform barriers.

</div>

<div class="feature-card">

### 🚀 Launch at Startup

Auto-start on boot and minimize to tray. Music starts with your computer — no need to manually launch the app.

[Learn more →](/en/guide/settings#startup-updates)

</div>

<div class="feature-card">

### 🧩 Plugin System

VS Code-style high-freedom plugin extension. Browse and install from online plugin sources, register custom pages, inject styles, create desktop floating windows, intercept audio resolution — infinitely extend EchoMusic.

[Learn more →](/en/guide/plugins/)

</div>

</div>

## Technical Highlights

| Feature | Details |
|------|------|
| Audio Engine | libmpv, embedded in-process via Rust NAPI — zero-latency direct function calls |
| Audio Quality | Hi-Res, SQ(flac), HQ(320kbps), Standard(128kbps) |
| Sound Effects | Piano, Vocal, Instrumental, Bone Flute, Ukulele, Suona, DJ, Viper Master, Viper Surround, Viper Ultra Clear, Spatial Audio (IR) |
| Playback Formats | Standard audio + LRC/YRC word-level lyrics parsing |
| Platform Output | macOS (dmg/zip), Windows (exe/portable), Linux (deb/rpm/AppImage/tar.gz) |

<style>
.feature-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  margin-top: 24px;
}
.feature-card {
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  padding: 20px;
  transition: border-color 0.25s, box-shadow 0.25s;
}
.feature-card:hover {
  border-color: var(--vp-c-brand);
  box-shadow: 0 2px 12px var(--vp-c-brand-soft);
}
.feature-card h3 {
  margin-top: 0;
  font-size: 1.1em;
}
.feature-card a {
  font-size: 0.9em;
}
</style>