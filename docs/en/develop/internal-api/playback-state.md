---
title: Playback State & Persistence
outline: [2, 4]
---

# 📡 Playback State & Persistence

Playback lifecycle event listening, queue persistent storage, local HTTP API server, main-process HTTP request proxy.

---

## Core Events (ctx.events)

Main player core event subscriptions (distinct from `ctx.audio.on*` mpv engine events).

| API | Callback Parameters | Description |
|-----|----------|------|
| `onTrackChange(fn)` | `(track)` | Track change |
| `onPlayStateChange(fn)` | `(isPlaying)` | Play/pause state |
| `onVolumeChange(fn)` | `(volume)` | Volume change |

```js
ctx.events.onTrackChange((track) => {
  console.log(`${track.title} - ${track.artist}`);
});
```

Registered listeners are automatically removed on window unload.

---

## Playback Queue Persistence (ctx.storage.playback\*)

Unlike `ctx.player.playlist` (runtime queue), `playback*` provides persistent storage operations that survive restarts.

| API | Description |
|-----|------|
| `playbackGetSnapshot()` | Get current playback state snapshot |
| `playbackGetQueue()` | Get the full playback queue |
| `playbackReplaceQueue(items)` | Replace the entire queue |
| `playbackAppendQueueItems(items)` | Append tracks |
| `playbackRemoveQueueItem(songId)` | Remove a track |
| `playbackReorderQueueItems(from, to)` | Reorder track positions |
| `playbackSetCurrentTrack(songId)` | Set the current track |
| `playbackUpdateMeta(meta)` | Update queue metadata |

```js
// Snapshot example
const snap = await ctx.storage.playbackGetSnapshot();
console.log(snap.currentTrack, snap.queue.length);

// Append tracks
await ctx.storage.playbackAppendQueueItems([
  { songId: "xxx", title: "...", artist: "..." }
]);
```

---

## API Server (ctx.apiServer)

EchoMusic's built-in local HTTP API server.

| API | Description |
|-----|------|
| `start()` | Start the local HTTP API server |
| `status()` | Get runtime status `{ running, port }` |

```js
const { running, port } = await ctx.apiServer.status();
if (!running) await ctx.apiServer.start();
```

---

## HTTP Requests (ctx.api.request)

Internal HTTP client proxied by the main process.

```js
const result = await ctx.api.request({
  method: "GET",
  url: "https://api.example.com/data",
  params: { page: 1 },
  headers: { "X-Custom": "value" },
});
console.log(result.data);
```

| Parameter | Type | Required | Description |
|------|------|:--:|------|
| `method` | `string` | ✅ | HTTP method (GET / POST / PUT / DELETE) |
| `url` | `string` | ✅ | Request URL |
| `params` | `object` | ❌ | URL query parameters |
| `data` | `any` | ❌ | Request body data |
| `headers` | `object` | ❌ | Custom request headers |

---

## 📂 Related Documents

- [Internal API Overview →](./) — Quick overview of the four modules
- [Audio Engine →](audio-engine) — Full mpv engine control
- [Window & Interaction Management →](window-management) — Window component management
- [System Features Integration →](system-features) — Shortcuts, updates, logging, etc.
