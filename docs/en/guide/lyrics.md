---
title: Lyrics
---

# 📝 Lyrics System

EchoMusic features a powerful lyrics display system, supporting multiple lyrics formats and display modes.

## Supported Formats

| Format | Description |
|------|------|
| **LRC** | Standard lyrics format, line-by-line timeline sync, most widely compatible |
| **YRC** | Word-level lyrics format, precise synchronization for each word |

> When a song has both LRC and YRC lyrics available, YRC (word-level) lyrics are used by default for a more accurate sing-along experience.

## Display Modes

EchoMusic offers multiple lyrics display modes for different scenarios.

### Player Bar Lyrics

Shows the current lyrics line in the bottom player bar — compact and concise. Ideal for daily use without taking extra screen space.

### Full-Screen Lyrics

Click the lyrics area on the player bar or the "Full-Screen Lyrics" button on the playback page:

- Immersive full-screen lyrics experience
- Lyrics centered, scrolling smoothly with playback progress
- Customizable background and font size
- Click blank area or press `Esc` to exit

### Desktop Lyrics

Float lyrics anywhere on your desktop without disrupting other tasks:

1. Enable "Desktop Lyrics" in Settings
2. The lyrics floating window stays always on top
3. Drag to reposition, with scaling and locking support
4. Adjustable font size and color, or let the lyrics color follow the album cover
5. Click the settings button on the floating window to open lyrics settings directly

::: tip
Desktop lyrics are perfect for when you're working or browsing the web — always visible.
:::

### Taskbar Lyrics

Added in v2.3.2 on Windows: lyrics are displayed directly on the taskbar, switching with a two-line upward scroll animation and paired with the taskbar cover preview — you can see the current lyrics at any time without a floating overlay.

## Lyrics Settings

Go to **Settings → Lyrics** to adjust:

| Setting | Description |
|------|------|
| Font size | Adjust lyrics display font size |
| Alignment | Left / Center alignment |
| Delay | Fine-tune lyrics-to-music sync timing |
| Global lyric time offset | Calibrate the time offset of the play page, desktop lyrics, Mini lyrics and taskbar lyrics together (added in v2.3.2) |
| Simplified/Traditional conversion | Convert lyrics between Original, Simplified, Traditional, Variant Traditional, Taiwan Standard and Hong Kong Traditional (added in v2.3.2) |
| Desktop lyrics color | Customize desktop lyrics text color |
| Desktop lyrics background | Toggle background box for desktop lyrics |
| Full-screen lyrics background | Choose background effect for full-screen lyrics |

::: tip
Since v2.3.2, lyrics settings consolidate the general, play page and desktop lyrics configurations, with general settings such as translation, transliteration, fine-tune step and lyrics filter managed in one place.
:::

## Lyrics Selection

When a song has multiple versions of lyrics available (different languages, translations, sources, etc.), EchoMusic supports manual selection:

1. Click the **Lyrics Selection** button on the lyrics page
2. Choose your preferred version from the available lyrics list
3. The display switches immediately after selection

Enhanced in v2.3.2:

- The dialog supports manual search — edit the song title and artist to look up lyrics
- The selected version is remembered for the current song

## Lyrics Filtering

Filter lyrics content using regular expressions:

1. Go to **Settings → Lyrics → Lyrics Filter**
2. Enter a regex rule (e.g., `/instrumental|backing/` to filter instrumental markers)
3. Matching content will be hidden from lyrics display

Use cases:
- Filter out ads or promotional text in lyrics
- Hide instrumental track markers
- Remove unwanted special symbols or annotations

## Translated Lyrics

Some songs support translated lyrics display:

- When a song has translated lyrics, they're shown below the original text
- Can be toggled on/off in lyrics settings
- Supports multilingual translations (when provided by the song)
- Added in v2.3.1: transliteration phonetic annotation display, with phonetic annotations for transliterated lyrics

## Lyrics Skins

Added in v2.3.2: skin switching for page lyrics, letting you change the style of the playback page lyrics. When a skin does not set its own colors, the unified play page lyrics color is used.

## Lyrics Danmaku

Added in v2.3.2-beta.4: danmaku (bullet comment) display and posting on the lyrics page and MVs — view and send danmaku while listening or watching MVs.

## Shortcuts

| Action | Shortcut |
|------|--------|
| Full-screen lyrics | Click the lyrics area on the player bar |
| Exit full-screen lyrics | `Esc` |
| Toggle desktop lyrics | Switch in Settings |