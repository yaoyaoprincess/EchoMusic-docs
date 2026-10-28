---
title: User Guide
---

# 📖 User Guide

Welcome to EchoMusic! This guide will help you get started and master all of EchoMusic's features.

## ✨ Feature Overview

<div class="feature-cards">

<div class="feature-card">

### 🎵 Advanced Playback

Queue management, list/single/shuffle modes, volume control, progress scrubbing, variable speed (0.5x–2.0x), crossfade.

[Learn more →](/en/guide/playback)

</div>

<div class="feature-card">

### 📝 Lyrics System

LRC/YRC word-by-word lyrics, precise scrolling sync, full-screen & desktop lyrics overlay.

[Learn more →](/en/guide/lyrics)

</div>

<div class="feature-card">

### 🎚️ Audio Enhancement

10-band EQ, LUFS loudness normalization, Viper Master/Surround/Ultra effects, Hi-Res/SQ/HQ/Standard quality tiers.

[Learn more →](/en/guide/audio)

</div>

<div class="feature-card">

### 🎧 Personal FM

Smart personalized radio that continuously optimizes recommendations based on your taste.

[Learn more →](/en/guide/personal-fm)

</div>

<div class="feature-card">

### 🎤 Music Recognition

Microphone and system-audio capture to quickly identify songs playing around you.

[Learn more →](/en/guide/music-recognition)

</div>

<div class="feature-card">

### 🔍 Multi-Dimensional Search

Search across songs, artists, albums, and playlists to quickly locate content.

[Learn more →](/en/guide/search)

</div>

<div class="feature-card">

### 💬 Song Details & Comments

View song info and playback details, browse reviews, jump to comment floors.

[Learn more →](/en/guide/song-detail)

</div>

<div class="feature-card">

### 🧩 Plugin System

VS Code-like high-freedom extensions, 46 community plugins covering themes/lyrics/audio/efficiency.

[Learn more →](/en/guide/plugins/)

</div>

<div class="feature-card">

### 🌐 Spatial Audio

Import IR impulse response files to render spatial audio and simulate acoustic environments.

[Learn more →](/en/guide/audio#spatial-audio)

</div>

<div class="feature-card">

### 🖥️ Cross-Platform & Integration

Full support for macOS/Windows/Linux, with tray, global shortcuts, and system media controls.

[Learn more →](/en/guide/settings)

</div>

</div>

<style>
.feature-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
  margin: 16px 0 24px;
}
.feature-card {
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  padding: 16px 20px;
  transition: border-color 0.25s, box-shadow 0.25s;
}
.feature-card:hover {
  border-color: var(--vp-c-brand);
  box-shadow: 0 2px 12px var(--vp-c-brand-soft);
}
.feature-card h3 {
  margin-top: 0;
  font-size: 1.05em;
}
.feature-card a {
  font-size: 0.9em;
}
</style>

## 🚀 Quick Navigation

### For Beginners

If you're new to EchoMusic, we recommend reading in this order:

- [Getting Started](/en/guide/getting-started) — Download, install & log in
- [Playback](/en/guide/playback) — Master basic playback controls
- [Music Discovery](/en/guide/music-discovery) — Browse recommendations & charts
- [Search](/en/guide/search) — Find the music you want

### Advanced Features

Once you're comfortable with the basics, explore these advanced features:

- [Lyrics](/en/guide/lyrics) — LRC/YRC lyrics, full-screen & desktop lyrics
- [Audio Settings](/en/guide/audio) — EQ equalizer, sound effects, audio quality
- [Personal FM](/en/guide/personal-fm) — Personalized radio recommendations
- [Music Recognition](/en/guide/music-recognition) — Identify songs playing around you
- [Song Details & Comments](/en/guide/song-detail) — View song info & reviews
- [Play History](/en/guide/settings#data-management) — View and manage listening history
- [Plugin System](/en/guide/plugins/) — Extend functionality, install & manage plugins

### Personalization

- [Preferences](/en/guide/settings) — Themes, shortcuts, system tray

### Need Help?

- [FAQ](/en/faq/) — Frequently asked questions

## Document Structure

```:no-line-numbers
en/guide/
├── getting-started.md        ← Download, install, first launch
├── playback.md                ← Playback controls & queue management
├── music-discovery.md         ← Music discovery, charts, recommendations
├── search.md                  ← Search songs/artists/albums/playlists
├── lyrics.md                  ← Lyrics display & settings
├── audio.md                   ← EQ, sound effects, audio quality
├── personal-fm.md             ← Personal FM radio
├── music-recognition.md       ← Music recognition
├── song-detail.md             ← Song details & comments
├── settings.md                ← Personalization settings
├── plugins/                   ← Plugin system (4 subpages)
└── faq.md                     ← Frequently asked questions
```