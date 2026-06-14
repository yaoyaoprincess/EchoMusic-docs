---
title: Player & Audio
outline: [2, 4]
---

# 🎵 Player & Audio

Plugins can deeply integrate with EchoMusic's player and audio system. This document covers playback control, audio spectrum, and the lyrics system.

## Playback Control

`ctx.player` provides convenient APIs for controlling the player.

### Playback State (computed properties, read-only)

| Property | Type | Description |
|----------|:--:|------|
| `currentTrack` | `computed` | Currently playing song object |
| `currentTrackId` | `computed` | Current song ID |
| `currentTime` | `computed` | Current playback progress (seconds) |
| `duration` | `computed` | Total song duration (seconds) |
| `isPlaying` | `computed` | Whether currently playing |
| `playbackRate` | `computed` | Playback rate (0.5 / 0.75 / 1.0 / 1.25 / 1.5) |
| `volume` | `computed` | Volume (0-100) |
| `playMode` | `computed` | Play mode |

```js
export function activate(ctx) {
  // Reactively watch playback progress
  ctx.vue.watch(
    () => ctx.player.currentTime,
    (time) => {
      // Fires per update (depends on player refresh rate)
      if (Math.floor(time) % 10 === 0) {
        console.log(`Played ${Math.floor(time)} seconds`);
      }
    }
  );

  // Watch for track changes
  ctx.vue.watch(
    () => ctx.player.currentTrackId,
    (newId, oldId) => {
      if (newId !== oldId) {
        console.log("Track changed:", ctx.player.currentTrack?.title);
      }
    }
  );
}
```

### Playback Control (functions)

| Method | Description |
|--------|------|
| `play()` | Start playback |
| `playTrack(track)` | Play a specific track |
| `toggle()` | Toggle play/pause |
| `stop()` | Stop playback |
| `next()` | Next track |
| `prev()` | Previous track |
| `seek(time)` | Seek to a specific time (seconds) |
| `setVolume(vol)` | Set volume (0-100) |
| `setPlaybackRate(rate)` | Set playback rate |
| `setPlayMode(mode)` | Set play mode |
| `setAudioQuality(q)` | Set audio quality |
| `setAudioEffect(e)` | Set audio effect |

```js
// Search and play a song
async function searchAndPlay(keyword) {
  const results = await ctx.kugou.search(keyword);
  if (results.length > 0) {
    ctx.player.playTrack(results[0]);
    ctx.toast.info(`Now playing: ${results[0].title}`);
  }
}

// Seek to 90 seconds
ctx.player.seek(90);

// Set volume and rate
ctx.player.setVolume(80);
ctx.player.setPlaybackRate(1.0);
```

### playTrack Parameter Format

```js
ctx.player.playTrack({
  id: "song_hash_or_id",    // Unique song identifier
  title: "Song Title",
  artist: "Artist",
  album: "Album",
  // ... other fields
});
```

---

## Audio Spectrum

> Requires capability: `audioSpectrum: true`

`ctx.audio.spectrum` provides access to audio spectrum data.

### API

| Method | Description |
|--------|------|
| `getStatus()` | Get spectrum capture status |
| `getSnapshot()` | Get current spectrum snapshot |
| `subscribe(options, handler)` | Subscribe to real-time spectrum data |

### subscribe Options

```js
ctx.audio.spectrum.subscribe(
  {
    fftSize: 2048,       // FFT window size, must be a power of 2 (32-32768)
    smoothingTimeConstant: 0.8,  // Smoothing coefficient (0-1)
    interval: 50,        // Data push interval (milliseconds)
  },
  (data) => {
    // data structure:
    // {
    //   frequencyData: Float32Array,  // Frequency domain data
    //   timeData: Float32Array,       // Time domain data
    //   sampleRate: number,           // Sample rate
    // }
    updateVisualizer(data.frequencyData);
  }
);
```

### Complete Example: Spectrum Visualizer

```js
export function activate(ctx) {
  // Create a canvas for spectrum visualization
  const canvas = document.createElement("canvas");
  canvas.width = 300;
  canvas.height = 100;
  canvas.style.cssText = "position: fixed; bottom: 60px; right: 20px; z-index: 9999; border-radius: 8px; background: rgba(0,0,0,0.6);";
  document.body.appendChild(canvas);

  const ctx2d = canvas.getContext("2d");

  ctx.audio.spectrum.subscribe(
    { fftSize: 256, interval: 50 },
    (data) => {
      const { frequencyData } = data;
      const width = canvas.width;
      const height = canvas.height;
      const barWidth = width / frequencyData.length;

      ctx2d.clearRect(0, 0, width, height);

      for (let i = 0; i < frequencyData.length; i++) {
        const barHeight = frequencyData[i] * height;
        const x = i * barWidth;
        const hue = (i / frequencyData.length) * 120 + 200;

        ctx2d.fillStyle = `hsl(${hue}, 80%, 60%)`;
        ctx2d.fillRect(x, height - barHeight, barWidth - 1, barHeight);
      }
    }
  );

  // Cleanup
  ctx.dispose(() => {
    canvas.remove();
  });
}
```

---

## Lyrics System

### Reading Lyrics State

```js
// ctx.lyric is equivalent to ctx.stores.lyric
const currentLine = ctx.lyric.currentLine;   // Currently highlighted lyric line
const allLines = ctx.lyric.lines;            // All lyric lines
const timeOffset = ctx.lyric.timeOffset;     // Time offset (seconds)
```

### Registering a Lyrics Resolver

> Requires capability: `lyrics: true`

```js
ctx.lyrics.registerResolver({
  id: "my-lyrics-source",        // Unique resolver ID
  name: "My Lyrics Source",      // Display name
  priority: 50,                  // Priority (higher = tried first)
  async resolve(song) {
    // song = { id, title, artist, album, ... }
    // Return lyrics text (LRC format or plain text)
    const lyrics = await fetchLyricsFromMySource(song);
    return lyrics;
  },
});
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--:|------|
| `id` | `string` | ✅ | Unique resolver ID |
| `name` | `string` | ✅ | Display name |
| `priority` | `number` | ❌ | Priority, default 0 |
| `resolve(song)` | `function` | ✅ | Return lyrics string or null |

> If `resolve` returns `null`, EchoMusic falls through to the next resolver.

### Getting/Subscribing to Lyrics Snapshots

```js
// Get current lyrics snapshot
const snapshot = ctx.lyrics.getSnapshot();
console.log(snapshot.currentLine, snapshot.lines);

// Subscribe to lyrics changes
ctx.lyrics.onSnapshot((snapshot) => {
  console.log("Lyrics updated:", snapshot.currentLine);
});
```

---

## Lyric Visual Effects

> Requires capability: `lyricEffects: true`

Register custom lyric visual effects for overlaying animations or effects on the lyrics display area.

```js
ctx.lyricEffects.register({
  id: "my-bounce-effect",
  name: "Bounce Lyrics",
  cssClass: "bounce-lyric",    // CSS class injected on each lyric line
  overlay: MyOverlayComponent, // Optional: decoration layer component for lyric area
});
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--:|------|
| `id` | `string` | ✅ | Unique effect ID |
| `name` | `string` | ✅ | Display name |
| `cssClass` | `string` | ❌ | CSS class injected on lyric lines |
| `overlay` | `Component` | ❌ | Decoration layer component for lyric area |

### CSS Effect Example

```css
/* Injected alongside style.css */
.bounce-lyric {
  animation: bounce 0.3s ease-out;
}

@keyframes bounce {
  0%   { transform: scale(1); }
  50%  { transform: scale(1.08); }
  100% { transform: scale(1); }
}
```

---

## Next Steps

| Document | Content |
|----------|------|
| [File Storage & Events →](./filesystem-events) | Local file I/O, KV storage, event listeners |
| [UI Extension Guide →](./ui-extension) | Pages, settings panels, context menus |
| [Publishing & Distribution →](./publishing) | Publish plugins to the online registry |
