---
title: Player & Audio
outline: [2, 4]
---

# 🎵 Player & Audio

Plugins can deeply integrate with EchoMusic's playback system. This document covers playback control, the playback queue, custom audio sources, and the lyrics system.

> ℹ️ Advanced audio engine controls (EQ / effects / IR / devices / fades / engine events) are internal APIs, not part of the plugin surface. See [Internal API Reference →](../internal-api/audio-engine) for core development.

---

## Playback Control (ctx.player)

`ctx.player` provides a complete API for operating the player.

### Playback State (computed properties, read-only)

| Property | Type | Description |
|------|:--:|------|
| `currentTrack` | `computed` | Currently playing song object |
| `currentTrackId` | `computed` | Current song ID |
| `currentTime` | `computed` | Playback progress (seconds), latest discrete value pushed by the engine |
| `duration` | `computed` | Total song duration (seconds) |
| `isPlaying` | `computed` | Whether currently playing |
| `isLoading` | `computed` | Whether loading |
| `playbackState` | `computed` | Display state: `loading` / `playing` / `paused` / `ended` / `error` |
| `playbackTargetTrackId` | `computed` | Target track ID (about to play) |
| `playbackRate` | `computed` | Playback rate (0.5-3.0) |
| `volume` | `computed` | Volume (0-100) |
| `playMode` | `computed` | Play mode |
| `audioQuality` | `computed` | `{effective, resolved, override}` quality info |
| `audioEffect` | `computed` | `{current, resolved}` effect info |

```js
export function activate(ctx) {
  // Reactively watch playback progress
  ctx.vue.watch(
    () => ctx.player.currentTime,
    (time) => {
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

### Playback Controls (functions)

| Method | Description |
|------|------|
| `play(trackId?, options?)` | Play a specific track (`options?: {autoPlay?, sourceQueueId?}`) or resume |
| `pause()` | Pause playback |
| `toggle()` | Toggle play/pause |
| `prev()` | Previous track within the queue |
| `next()` | Next track within the queue |
| `stop()` | Stop playback |
| `seek(time)` | Seek to a specific time (seconds) |
| `setVolume(vol)` | Set volume (0-100) |
| `setPlaybackRate(rate)` | Set playback rate (0.5-3.0) |
| `setPlayMode(mode)` | Set play mode |
| `setAudioQuality(q)` | Set audio quality |
| `setAudioEffect(e)` | Set audio effect |
| `playTrack(trackId, options?)` | Play a specific track by ID |
| `playSong(song, opts?)` | Play a song object (enqueue and play) |
| `playNext(song, opts?)` / `playLast(song, opts?)` | Insert a song after the current one / at the end |
| `replaceQueueAndPlay(songs, options?)` | Replace the queue and play |
| `dislikePersonalFm()` | Dislike in Personal FM |
| `toggleLyricView(open?)` | Toggle the lyrics view |

```js
// Seek to 90 seconds
ctx.player.seek(90);

// Set volume and rate
ctx.player.setVolume(80);
ctx.player.setPlaybackRate(1.0);

// Play mode
ctx.player.setPlayMode("loop");

// Play a track by ID
ctx.player.playTrack("song_001");
```

---

## Queue Management

`ctx.playlist` provides full control over the playback queue, with a **multi-queue** model (`queues` holds all queues, `activeQueue` is the currently active one; operations target the active queue by default).

| API | Description |
|-----|------|
| `getActiveQueue()` | Get the active queue |
| `getQueue(queueId)` / `getQueueSongs(queueId?)` | Get a specific queue / its songs |
| `queues` / `activeQueue` | All queues / the active queue (computed) |
| `setActiveQueue(queueId)` | Switch the active queue |
| `append(songs, options?)` | Append songs to the end |
| `remove(songId, queueId?)` | Remove a song |
| `clear(queueId?)` | Clear a queue |
| `replace(songs, options?)` | Replace the entire queue |
| `reorder(fromIndex, toIndex, queueId?)` | Reorder songs |
| `playNext(song, options?)` | Insert (play next) |
| `playSong(song, options?)` / `playLast(song, options?)` | Play a song object / append to the end |
| `enqueuePlayNext(songId)` / `enqueuePlayNextSequential(songId)` | Enqueue by ID (overwriting / sequential) |
| `replaceAndPlay(songs, options?)` | Replace the queue and play |

```js
// Append songs to the queue
ctx.playlist.append([{ id: "001", title: "Song", artist: "Artist" }]);

// Insert (play next)
ctx.playlist.playNext({ id: "urgent", title: "Urgent insert" });

// Clear and replace
ctx.playlist.clear();
ctx.playlist.replace(recommendedSongs);
```

---

## Audio Spectrum

> Requires capability: `audioSpectrum: true`

`ctx.audio.spectrum` provides real-time FFT spectrum data.

| API | Description | Details |
|-----|------|:--:|
| `getStatus()` | Get capture status | [Audio Spectrum →](./audio-spectrum) |
| `getSnapshot()` | Single-frame spectrum snapshot | [Audio Spectrum →](./audio-spectrum) |
| `subscribe(opts, cb)` | Subscribe to real-time spectrum data | [Audio Spectrum →](./audio-spectrum) |

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
  order: 200,                    // Priority (ascending; lower = tried first)
  match({ track }) {             // Whether this track matches
    return Boolean(track?.hash);
  },
  async resolve({ track }) {
    const result = await fetchLyricsFromMySource(track);
    return result?.lyric || null; // Return LRC text or null (cannot handle)
  },
});
```

| Parameter | Type | Required | Description |
|------|------|:--:|------|
| `id` | `string` | ✅ | Unique resolver ID |
| `order` | `number` | ❌ | Priority, ascending — **lower is tried first** |
| `match({track})` | `function` | ❌ | Whether the track matches |
| `resolve({track})` | `async function` | ✅ | Return `{source, lyric}` or null |

> Returning `null` from `resolve` means "cannot handle this track" and EchoMusic falls through to the next resolver.

### Getting/Subscribing to Lyrics Snapshots

```js
const snapshot = ctx.lyrics.getSnapshot();
console.log(snapshot.currentLine, snapshot.lines);

ctx.lyrics.onSnapshot((snapshot) => {
  console.log("Lyrics updated:", snapshot.currentLine);
});
```

### Sending Commands

```js
// Available commands: toggleTranslation / toggleRomanization /
// lyricOffsetBackward / lyricOffsetForward / lyricOffsetReset / seekForward / seekBackward
ctx.lyrics.command("toggleTranslation");
ctx.lyrics.command("lyricOffsetForward");
```

---

## Lyric Visual Effects

> Requires capability: `lyricEffects: true`

Register custom lyric visual effects for both page lyrics and desktop lyrics. Desktop lyrics require `runtime.desktopLyric: true` in the manifest. See [EchoMusicPlugins docs/floating-windows.md](https://github.com/hoowhoami/EchoMusicPlugins/blob/main/docs/floating-windows.md).

```js
// Page lyrics effect
ctx.lyricEffects.register({
  id: "water",
  title: "Water Wave Lyrics",
  scope: "page",
  layer: "decorator",
  className: "my-water-lyrics",
  css: `.my-water-lyrics [data-echo-lyric-line] { font-style: italic; }`,
  mount(host) {
    // Optional: create a decorator layer (SVG / Canvas)
    return () => { /* cleanup */ };
  },
});

// Desktop lyrics effect (requires runtime.desktopLyric: true)
ctx.lyricEffects.register({
  id: "vertical-desktop",
  title: "Vertical Desktop Lyrics",
  scope: "desktop",
  layer: "style",
  css: `.desktop-lyric { writing-mode: vertical-rl; }`,
});
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--:|------|
| `id` | `string` | ✅ | Unique effect ID |
| `title` | `string` | ✅ | Display name |
| `scope` | `string \| string[]` | ✅ | `"page"` (page lyrics), `"desktop"` (desktop lyrics), or an array of both |
| `order` | `number` | ❌ | Ordering when multiple effects share one host |
| `layer` | `string` | ❌ | `"style"` or `"decorator"` |
| `className` | `string` | ❌ | CSS class injected into the host node |
| `css` | `string` | ❌ | Global CSS to inject |
| `mount(host)` | `function` | ❌ | Called on host mount, returns cleanup function |

The `host` passed to `mount()` is a rich interface: besides the mount node it provides `getSnapshot()` (snapshot with word-by-word lyrics, timeline, and appearance), `subscribe(fn)`, `setAutoScrollHandler(fn)` (take over auto-scrolling), and `requestUpdate()`.

> ℹ️ The desktop lyric window is an independent renderer process. Use `ctx.desktopLyric` to detect the current runtime environment.

---

## Custom Audio Sources

> Requires capability: `audioSource: true`

Take over audio source resolution for specific platforms or tracks, with **staged takeover** (`position`) and **candidate transformation** (`transform`):

```js
ctx.player.audioSource.register({
  id: "webdav-audio",
  position: "after-catalog",   // fallback level: before-catalog / after-catalog / final-fallback
  order: 100,                  // ascending within a stage (shared with transform)
  match({ track }) {
    return Boolean(track?.hash);
  },
  async resolve({ track, quality }) {
    const url = await resolveWebDAVUrl(track.id, quality);
    return url || null;        // return a URL string, a Partial<ResolvedAudioSource>, or null to decline
  },
  // Optional: transform each candidate produced by the given stages (replace, modify, or reject)
  transform({ source, stage }) {
    if (stage === "cloud") return { ...source, url: source.url.replace("http://", "https://") };
  },
});
```

| Parameter | Type | Description |
|------|------|------|
| `id` | `string` | Unique resolver ID |
| `order` | `number` | Ascending within a stage; lower runs first |
| `position` | `string` | Fallback level: `before-catalog` / `after-catalog` / `final-fallback` |
| `match({track, ...})` | `async` | Whether to handle the track |
| `resolve({track, quality, effect, forceReload, position})` | `async` | Return a URL string, a `Partial<ResolvedAudioSource>`, or null |
| `transformStages` | `string \| string[]` | Limit transform to specific stages (defaults to all) |
| `transform({source, stage, ...})` | `async` | Transform candidates: return a string (replace URL), partial fields (merge), or `false` (reject) |

> Returning `null`/`undefined` keeps the current candidate; `false` rejects it and continues the player's fallback chain.

---

## Next Steps

| Document | Content |
|----------|------|
| [Audio Spectrum →](./audio-spectrum) | Real-time FFT spectrum subscription & visualization |
| [Filesystem & Storage →](./filesystem-storage) | Filesystem, KV storage, appearance subscription |
| [Windows & System →](./windows-system) | Floating windows, Now Playing, process, icons |
| [Context API Reference →](./context-api) | Full plugin API quick reference |
