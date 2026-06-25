---
title: Audio Settings
---

# 🎚️ Audio Settings

EchoMusic provides professional-grade audio adjustments, including a 10-band EQ equalizer, multiple sound effect modes, and audio quality options.

## Audio Quality

EchoMusic supports multiple quality tiers, selectable on the playback page:

| Quality | Format | Description |
|------|------|------|
| **Hi-Res** | Lossless | Highest quality, ideal for high-end audio equipment |
| **DSD** | Premium | DSD high-resolution audio, limited song availability |
| **SQ** | FLAC | Lossless quality, CD-level |
| **HQ** | 320kbps | High-quality compression, balanced quality and bandwidth |
| **Standard** | 128kbps | Standard quality, for limited network conditions |

::: tip
Higher quality requires faster network speeds and more data. We recommend HQ or SQ quality when connected to Wi-Fi.
:::

## EQ Equalizer

EchoMusic features a built-in 10-band graphic equalizer for precise frequency control.

### Band Reference

| Band | Frequency | Sound Character |
|------|----------|----------|
| Band 1 | 31Hz | Sub-bass — depth and impact of low frequencies |
| Band 2 | 62Hz | Bass extension |
| Band 3 | 125Hz | Bass punch |
| Band 4 | 250Hz | Low-mid — warmth and fullness |
| Band 5 | 500Hz | Mid — body of vocals |
| Band 6 | 1kHz | Mid — vocal clarity |
| Band 7 | 2kHz | Upper-mid — brightness |
| Band 8 | 4kHz | High — sibilance and detail |
| Band 9 | 8kHz | High extension — airiness |
| Band 10 | 16kHz | Ultra-high — harmonics and spaciousness |

### Usage

1. Go to **Settings → Audio → EQ**
2. Drag each band's slider to adjust
3. Listen to the effect in real time

::: tip EQ Tips
- Boost bass (31Hz-125Hz): Great for electronic and hip-hop
- Boost mids (500Hz-1kHz): Emphasizes vocals
- Boost highs (4kHz-16kHz): Adds detail and air
- We recommend small adjustments (within ±3dB) to avoid distortion
:::

## Sound Effects

EchoMusic includes 9 built-in sound effect modes for different listening experiences:

| Effect | Best For |
|------|----------|
| **Vocal** | Plays only vocals, suppresses accompaniment |
| **Instrumental** | Plays only accompaniment, suppresses vocals |
| **Piano** | Highlights piano tones, great for instrumental music |
| **Vocal Accompaniment** | Reduces vocals, highlights backing instruments |
| **Bone Flute** | Enhances treble, ideal for traditional folk music |
| **Ukulele** | Bright and lively tone |
| **Suona** | Enhanced penetration and presence |
| **DJ** | Boosts bass, ideal for electronic dance music |
| **Viper Master** | Mastering-grade audio processing |
| **Viper Surround** | Spatial surround sound effect |
| **Viper Ultra Clear** | High-definition audio restoration |

### Spatial Audio

EchoMusic supports spatial audio rendering via IR (impulse response) audio files:

1. Import IR audio files in **Settings → Effects → Spatial Audio**
2. Rename and remove imported IR files as needed
3. Quickly switch between spatial audio presets from the effects popup on the playback page

Use cases:
- Simulate different acoustic environments (concert hall, studio, etc.)
- Virtual surround sound experience
- Enhanced spatial audio for headphones

::: tip
You can search for or record your own IR files online. EchoMusic renders them into the playback audio in real time.
:::

Click the sound effect button on the playback page to switch.

## Volume Normalization

Based on LUFS (Loudness Units relative to Full Scale) loudness normalization:

- Automatically adjusts different songs to similar loudness levels
- Prevents sudden volume jumps when switching tracks
- Enable in **Settings → Audio**

## Audio Devices

Manage audio output devices:

1. Click the audio device icon on the player bar
2. Select the output device to use (speakers, headphones, etc.)
3. Supports **Exclusive Mode**: Bypasses system mixing and outputs directly to the device, reducing latency

::: warning Note
In exclusive mode, other applications cannot play audio simultaneously. If you need to use multiple audio apps at once, disable exclusive mode.
:::