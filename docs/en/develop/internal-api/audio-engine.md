---
title: Audio Engine (electron.player)
outline: [2, 4]
---

# 🎵 Audio Engine (electron.player)

EchoMusic's playback core is the **Rust engine** `echo-audio-player` (vendored FFmpeg decoding + dual-engine tempo processing, embedded in-process via Rust NAPI — no external FFmpeg executable needed). The renderer controls it through the preload-exposed `electron.player.*`, with the main-process wrapper in `src/main/player/` (`controller.ts` etc.).

Engine pipeline: `FFmpeg decode → format conversion → DspHost (EQ/convolution/provider) → tempo → output gain → device output`.

> ⚠️ `setSpatialAudio({preset})`, `setImpulseResponse({path, dryWet})`, `getAudioFilter()` and `onImpulseResponseDisabled()` from older revisions of this document **do not exist** in the current source; they have all been superseded by the `setAudioEffect` effect model.

---

## Loading and Source Switching

### Basic loading

| API | Description |
|-----|-------------|
| `load(url, requestId?)` | Load an audio URL or local file |
| `loadMkvTrack(url, trackId, requestId?)` | Load a specific audio track from an MKV container |
| `getTrackList(url?)` | List container audio tracks (MKV multi-track) |
| `setLoopFile(bool)` | Loop the current file |
| `setMediaTitle(title)` | Set the title shown in system media controls |

### Gapless / source switching

The engine implements a "source change" protocol which, combined with [track transitions](#track-transition-settings), enables uninterrupted source swaps and track changes:

| API | Description |
|-----|-------------|
| `beginSourceChange()` | Declare a source change (freezes the old source's state) |
| `switchSource(url, trackId?)` | Switch the audio source URL within the same playback session |
| `beginNextSourcePreparation()` | Start preparing the next track, returns `requestId` |
| `cancelNextSourcePreparation(requestId)` | Cancel preparation |
| `prepareNextSource(url, requestId, trackId?, normalizationGainDb?)` | Pre-decode the next track (with loudness normalization pre-applied) |
| `commitPreparedNextSource(transitionMs?)` | Commit the prepared next track within the transition window (seamless handover) |
| `clearPreparedNextSource()` | Discard prepared content |

> Preparation should complete before the current track ends — `getTransitionSettings()` returns `prefetchLeadSecs`, the recommended lead time. The transition decision (gapless / fade / automix) is computed by the engine's `transition/` subsystem from **8 JSON transition plans** (`simple_filter`, `three_band`, `simple_exchange`, `filter_eq`, `fallback_exchange`, `echo_tail`, `smooth_filter`, `layered_filter`).

---

## Track Transition Settings

```js
await electron.player.setTransitionSettings({
  mode: "gapless",     // "none" | "gapless" | "fade" | "automix-basic" | "automix-pro"
  fadeSecs: 4,         // fade duration (0–15s in fade mode)
  matchTempo: true,    // automix-pro tempo matching
});
```

| API | Returns | Description |
|-----|---------|-------------|
| `setTransitionSettings(options)` | — | Set transition mode / fade seconds / tempo matching |
| `getTransitionSettings()` | `{ mode, fadeSecs, matchTempo, prefetchLeadSecs }` | Current settings (including the suggested preparation lead time) |
| `getTransitionDiagnostics()` | `string \| null` | Diagnostics (JSON) of the most recent transition |

The five modes: `none` (hard cut), `gapless` (skip leading/trailing silence, sample-continuous butt splice), `fade` (linear-amplitude overlap 0–15s), `automix-basic` (content-aware cue points, tempo unchanged, gain/bass exchange), `automix-pro` (beat-matched cue points + multi-band filtering + optional tempo alignment).

---

## Playback Control

| API | Description |
|-----|-------------|
| `play(requestId?)` / `pause()` / `stop()` | Play / pause / stop |
| `seek(time)` | Seek to a position in seconds |
| `setVolume(volume)` | Set volume (the app-layer volume scale, same as the UI volume) |
| `setSpeed(speed)` | Tempo change, range **0.1x – 5x**. Dual engine: spectral phase vocoder (extreme speeds) + SoundTouch WSOLA (normal speeds) |

---

## Equalizer (EQ)

10-band parametric equalizer with independent gain per band (-12 to +12 dB):

```js
await electron.player.setEqualizer([
  0,   // 31 Hz
  2,   // 62 Hz
  3,   // 125 Hz
  1,   // 250 Hz
  0,   // 500 Hz
  -1,  // 1 kHz
  0,   // 2 kHz
  2,   // 4 kHz
  1,   // 8 kHz
  0,   // 16 kHz
]);
```

The band frequencies are `31 / 62 / 125 / 250 / 500 / 1000 / 2000 / 4000 / 8000 / 16000` Hz. The EQ cascade measures its own headroom; live changes crossfade the old and new filter states over 15ms without clicks.

---

## Loudness Normalization

```js
await electron.player.setNormalizationGain(-3.5); // dB, from per-song loudness analysis
```

---

## Volume Fade

| API | Description |
|-----|-------------|
| `fade(from, to, durationMs)` | Fade volume from `from` to `to` |
| `cancelFade()` | Cancel an in-progress fade |
| `pauseWithFade(savedVolume, durationMs)` | Fade out and pause (remembers the original volume) |
| `playWithFade(targetVolume, durationMs, requestId?)` | Fade in and resume |

---

## Effect Model (setAudioEffect)

A single effect entry point covering both the built-in convolution (IR) and external DSP providers:

```ts
await electron.player.setAudioEffect({
  // —— Built-in Basic DSP (IR convolution) ——
  impulseResponsePath: "path/to/effect.irs" | null,
  impulseResponseMix: 1.0,               // 0 (dry) – 1 (wet), Basic DSP only
  // —— External DSP provider ——
  providerPath: "path/to/audio-provider.dll" | null,
  providerPresetJson: "...",             // provider-owned preset JSON
  providerResources: [{ kind: "vpf", path: "..." }],  // resources passed through (e.g. VPF)
  providerMode: "headphone" | "speaker", // defaults to "speaker"
} | null);                                // null = turn all effects off
```

### IR convolution (built-in Basic DSP)

- Accepts **mono / stereo / four-channel true-stereo** IRS files (channel order `[LL, LR, RL, RR]`); any other channel layout is rejected rather than silently remixed;
- IR length is capped at **8 seconds** (`MAX_IR_SECONDS = 8.0`); longer files are rejected; leading silence beyond 50ms is trimmed;
- Partitioned convolver (256-frame early block + 1024-frame late block) with ~5.3ms algorithmic latency at 48kHz; the dry path is delay-aligned before mixing to avoid comb filtering;
- Defaults to **fully wet** (`impulseResponseMix = 1.0`), preserving the IR's original gain; a stereo-linked limiter only intervenes on clipping risk;
- The host EQ is bypassed while a provider owns the graph and restored when playback returns to Basic DSP.

### DSP Provider (hot-pluggable external effect engines)

External native effect engines are loaded into the player process via a C ABI (`EchoDspApi`, currently v2) and own the complete DSP graph (vendor effects beyond EQ/convolution/limiting). Architecture details: upstream `docs/dsp-provider-architecture.md`.

| API | Description |
|-----|-------------|
| `selectDspProvider(mode)` | Select an installed provider (`"headphone" \| "speaker"`, default `"speaker"`), returns `DspProviderRecord \| null` |
| `listDspProviders()` | List installed providers |
| `inspectDspProvider(path)` | Validate a provider file before import (ABI / manifest / capabilities) |
| `deleteDspProvider(providerId)` | Delete a provider (switches back to Basic DSP first, then retires the binary asynchronously) |

`DspProviderRecord` includes `providerId` (logical identity, cross-platform), `providerVersion`, `latencyFrames`, `preferredBlockFrames`, `maxChannels`, `manifestJson`, `stateJson`, `path`, `contentHash` (SHA-256 content-addressed immutable version), etc. Installed binaries are addressed by content hash; re-importing identical content reuses the existing version, and same-ID different content goes through a rollback-capable "candidate version → validate → atomically advance metadata" transaction.

For effect file import/download/delete see Audio Effects Management in [System Features](system-features).

---

## Audio Graph

Runtime snapshot and online tuning of the engine's processing graph (EQ cascade headroom, convolution mix, provider state, etc. all appear in the snapshot):

| API | Description |
|-----|-------------|
| `getAudioGraph()` | `Promise<PlayerAudioGraphSnapshot \| null>` current graph snapshot |
| `setAudioGraphParameter(patch)` | Adjust a single node parameter at runtime |
| `setAudioGraphPlan(plan)` | Adjust the processing plan |
| `onAudioGraphChange(fn)` | Graph structure/state change push |

---

## Audio Devices and Output

| API | Description |
|-----|-------------|
| `getAudioDevices()` | Device list `{ name, description, isDefault? }[]` |
| `setAudioOutput(deviceName, exclusive)` | Switch output device; `exclusive=true` requests exclusive mode (WASAPI / CoreAudio / ALSA exclusive, bypassing the system mixer) |
| `setPauseOnDeviceDisconnect(bool)` | Auto-pause when the device disconnects (unplugged headphones) |
| `onAudioDeviceListChanged(fn)` | Device hot-plug notification (with change kind and disconnected devices) |

---

## Engine-level Networking and Buffering

| API | Level | Description |
|-----|-------|-------------|
| `setStallTimeout(seconds)` | preload | Playback stall detection timeout |
| `set_http_proxy(proxy)` / `set_http_proxies(proxies[])` | Engine (called from the main process via echo-audio-player) | Engine streaming HTTP proxy (pushed automatically from the main process [network settings](system-features)) |
| `set_network_timeout(seconds)` | Engine | Engine network timeout |

| Event | Description |
|-------|-------------|
| `onStall(fn)` | Playback stalled (reports current position) |
| `onPacketCacheStats(fn)` | Forward/backward cache bytes, seekable ranges, EOF state, etc. |

---

## Session and State

| API | Description |
|-----|-------------|
| `available()` | Whether the engine is available (native module loaded) |
| `restart()` | Restart the engine (crash recovery), returns success |
| `getState()` | Engine internal state |
| `getRuntimeSession()` | Read the runtime session (for restart recovery) |
| `syncRuntimeSession(session)` | Write the runtime session |
| `getEmbeddedMetadata(request)` | Read embedded metadata (tags/cover, cover cached) |

---

## Audio Events

| API | Callback payload | Description |
|-----|------------------|-------------|
| `onTimeUpdate(fn)` | `number \| { time?, trackSeq?, generation?, sampledAt? }` | Playback progress (seconds) |
| `onDurationChange(fn)` | `(duration: number)` | Duration change |
| `onStateChange(fn)` | `{ playing?, paused?, timePos?, ... }` | Play/pause state |
| `onPlaybackEnd(fn)` | `(reason, context?)` | Playback ended (eof / stop / error, with trackSeq/generation) |
| `onError(fn)` | `(payload: PlayerErrorPayload)` | Engine error |
| `onSeeked(fn)` | `(time: number)` | Seek completed |
| `onSeekStateChange(fn)` | `{ active, time?, ... }` | Seek-in-progress state |
| `onPlaybackRestart(fn)` | `{ time?, reason? }` | Engine/playback restart recovery |
| `onFileLoaded(fn)` | `{ path?, seq?, trackSeq?, generation?, startTime?, transition? }` | File loaded (with transition info) |
| `onCoreStateChange(fn)` | `{ state?, reason?, ... }` | Engine core state |
| `onAoStateChange(fn)` | `{ paused?, bufferingState?, bufferedSecs?, targetSecs?, ... }` | Output-side buffering/pause state |
| `onAudioOutputStats(fn)` | `{ backend, sampleRate, channels, format, bufferSecs, delaySecs, underruns, ... }` | Output stats (backend/buffer/underruns) |
| `onAudioGraphChange(fn)` | `PlayerAudioGraphSnapshot?` | Audio graph changed |
| `onStall(fn)` / `onPacketCacheStats(fn)` | See above | Network and cache |
| `onAudioDeviceListChanged(fn)` | See above | Device hot-plug |

All event listeners return an unsubscribe function. `trackSeq` / `generation` distinguish which track and engine generation an event belongs to, preventing async events from crossing streams.

---

## 📂 Related Documents

- [Internal API Overview](/en/develop/internal-api/) — module map
- [Playback State & Persistence](/en/develop/internal-api/playback-state) — queue persistence and API server
- [Window & Interaction Management](/en/develop/internal-api/window-management) — window components and network casting
- [System Features](/en/develop/internal-api/system-features) — effect file management, network settings
- [Native Addons](/en/develop/native-addons) — echo-audio-player crate details
