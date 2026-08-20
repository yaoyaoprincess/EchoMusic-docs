---
title: Native Addons (Rust NAPI)
---

# 🦀 Native Addons (Rust NAPI)

EchoMusic uses Rust to write native extensions, compiled into Node.js-callable native modules via the [napi-rs](https://napi.rs/) framework. Native modules run in the Electron main process, providing high-performance low-level capabilities.

## Why Rust?

| Advantage | Description |
|------|------|
| **Zero-latency calls** | Direct in-process function calls, no IPC overhead |
| **High performance** | Rust compiles to native machine code, performance near C/C++ |
| **Memory safety** | Rust's ownership system guarantees memory safety, no GC pauses |
| **Rich ecosystem** | FFI enables calling C libraries (e.g., FFmpeg) |

## Module Overview

### echo-ffmpeg-player — Playback Engine

Wraps the FFmpeg + SoundTouch native playback engine, providing complete audio playback capabilities.

**Core Features**:

| Feature | Description |
|------|------|
| Playback control | Play / Pause / Stop / Seek |
| Volume control | Volume adjustment, mute |
| Speed control | 0.5x - 2.0x playback speed |
| Crossfade | Smooth track transitions |
| EQ equalizer | 10-band parametric EQ (60Hz-16kHz) |
| Volume normalization | LUFS-based loudness normalization |
| Spatial audio | FFT-based convolution reverb (custom IR import supported) |
| Device management | Audio device switching, exclusive output |
| Spectrum analysis | Built-in real-time spectrum |
| Event callbacks | Playback progress, status change callbacks |

**Dependencies**:

```toml
[dependencies]
napi = "2"
napi-derive = "2"
# FFmpeg integrated via vendored ffmpeg-audio + soundtouch-rs
```

**Usage**:

```typescript
import { FfmpegPlayer } from 'echo-ffmpeg-player'

const player = new FfmpegPlayer()
player.load('https://example.com/song.mp3')
player.play()
player.setVolume(80)
player.setEq([0, 2, -1, 3, 0, 1, 2, 0, -2, 1])
```

### echo-media-controls — System Media Control

Integrates each operating system's native media control APIs.

**Core Features**:

| Platform | API | Description |
|------|-----|------|
| macOS | MPNowPlayingInfoCenter | Control Center media info display |
| macOS | MPRemoteCommandCenter | Respond to system media keys |
| Windows | SMTC | System Media Transport Controls |
| Linux | MPRIS | D-Bus media player interface |

**Usage**:

```typescript
import { MediaControls } from 'echo-media-controls'

const controls = new MediaControls()
controls.setMetadata({
  title: 'Song Name',
  artist: 'Artist',
  album: 'Album',
  duration: 240,  // seconds
})
controls.setPlaybackState('playing')
controls.on('play', () => { /* play */ })
controls.on('pause', () => { /* pause */ })
controls.on('next', () => { /* next */ })
controls.on('previous', () => { /* previous */ })
```

### echo-sqlite-store — Local Storage

Lightweight local persistent storage based on SQLite.

**Core Features**:

| Feature | Description |
|------|------|
| Key-value store | General K-V storage with serialization support |
| Play queue | Persistent play queue and state |
| Playback history | Record playback history |
| Favorites management | Song/playlist favorites list |
| Settings storage | Application preferences |

**Usage**:

```typescript
import { Storage } from 'echo-sqlite-store'

const db = new Storage()
await db.open('echo-music.db')

// Store settings
await db.set('settings', { theme: 'dark', volume: 80 })

// Read settings
const settings = await db.get('settings')

// Playback history
await db.addHistory({ songId: 'xxx', playedAt: Date.now() })
const history = await db.getHistory({ limit: 50 })
```

## Developing Native Modules

### Adding a New Native Module

1. Create a new crate under `native/`:

```bash
cd native
npx @napi-rs/cli new my-new-addon
```

2. Configure dependencies in Cargo.toml
3. Use `#[napi]` macro in lib.rs to export functions
4. Load the `.node` file in the Electron main process

### Compilation

```bash
# Debug build
cd native/<module>
cargo build

# Release build (optimized)
cargo build --release
```

### Cross-Platform Compilation Notes

- **macOS**: `.dylib` → rename to `.node`
- **Linux**: `.so` → rename to `.node`
- **Windows**: `.dll` → rename to `.node`

`.node` files are excluded in `.gitignore` — recompile after each clone.

## Debugging Tips

- Use `println!()` macro for debug output (outputs to the Electron main process console)
- Use `napi::bindgen_prelude::console_log!()` in Rust code to output to the Node.js console
- Recommended: VS Code + rust-analyzer for development

## References

- [napi-rs Official Documentation](https://napi.rs/)
- [FFmpeg Official Documentation](https://ffmpeg.org/documentation.html)
- [SoundTouch Audio Processing Library](https://www.surina.net/soundtouch/)
- [MPRIS Specification](https://specifications.freedesktop.org/mpris-spec/latest/)