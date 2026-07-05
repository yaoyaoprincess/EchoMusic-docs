---
title: Audio Engine (ctx.audio)
outline: [2, 4]
---

# 🎵 Audio Engine (ctx.audio)

EchoMusic uses **libmpv** as its underlying audio engine, controlled within the same renderer process via `ctx.audio`.

---

## Equalizer (EQ)

An 18-band parametric equalizer, with each band independently controllable (-12 ~ +12 dB).

```js
ctx.audio.setEqualizer([
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

EQ bands: `32 / 64 / 125 / 250 / 500 / 1k / 2k / 4k / 8k / 16k` Hz

---

## Spatial Audio

```js
ctx.audio.setSpatialAudio({
  preset: "hall",     // "hall" | "church" | "studio" | "theater"
  dryWet: 0.5,        // Dry/wet ratio (0.0 = dry only, 1.0 = wet only)
});
// Disable: { preset: null }
```

---

## Impulse Response (IR Convolution)

```js
ctx.audio.setImpulseResponse({
  path: "path/to/ir-file.wav",
  dryWet: 0.6,
});
// Or pass path directly: ctx.audio.setImpulseResponse("path/to/ir-file.wav")
```

| Parameter | Type | Description |
|------|------|------|
| `path` | `string` | Absolute path to the IR audio file |
| `dryWet` | `number` (0-1) | Dry/wet mix ratio |

---

## Audio Device Control

| API | Description |
|-----|------|
| `getAudioDevices()` | Get the list of available audio devices |
| `setAudioDevice(name)` | Switch audio output device |
| `setExclusive(bool)` | Toggle exclusive mode (bypasses system mixer) |
| `getAudioFilter()` | Get the currently active audio effect filter name |

```js
const devices = await ctx.audio.getAudioDevices();
await ctx.audio.setAudioDevice("Speakers");
await ctx.audio.setExclusive(true);
```

---

## Volume Fade

| API | Description |
|-----|------|
| `fade(from, to, durationMs)` | Fade from `from` to `to` volume |
| `cancelFade()` | Cancel an ongoing fade |
| `pauseWithFade(savedVol, durationMs)` | Fade-out before pausing |
| `playWithFade(targetVol, durationMs)` | Fade-in on resume |

```js
ctx.audio.fade(currentVol, 30, 2000);
ctx.audio.pauseWithFade(20, 1500);
ctx.audio.playWithFade(80, 1000);
```

---

## Loudness Normalization

```js
ctx.audio.setNormalizationGain(-3.5); // dB
```

---

## Files & Tracks

| API | Description |
|-----|------|
| `loadFile(url, track?)` | Load an audio file or MKV track |
| `getTrackList()` | Get the MKV track list |
| `setLoopFile(bool)` | Toggle single-track loop |
| `setMediaTitle(title)` | Set media title |

---

## Engine Control

| API | Description |
|-----|------|
| `available()` | Check if the mpv engine is available |
| `restart()` | Restart the playback engine |
| `getState()` | Get the engine's internal state |

---

## Audio Events

| API | Callback Parameters | Description |
|-----|----------|------|
| `onTimeUpdate(fn)` | `(time: number)` | Playback time update (seconds) |
| `onDurationChange(fn)` | `(duration: number)` | Track duration change |
| `onStateChange(fn)` | `({playing?, paused?})` | Play/pause state change |
| `onPlaybackEnd(fn)` | `(reason: string)` | Playback ended ("eof" / "stop" / "error") |
| `onError(fn)` | `(message: string)` | mpv engine error |
| `onAudioDeviceListChanged(fn)` | `(devices[])` | Device list changed (headphone plug/unplug) |
| `onImpulseResponseDisabled(fn)` | `({path?, reason?})` | IR auto-disabled notification |

All event listeners return a cancel function.

---

## 📂 Related Documents

- [Internal API Overview →](./) — Quick overview of the four modules
- [Playback State & Persistence →](playback-state) — Playback events & queue persistence
- [Window & Interaction Management →](window-management) — Window component management
- [System Features Integration →](system-features) — Shortcuts, updates, logging, etc.
