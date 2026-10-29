---
title: Playback State & Persistence
outline: [2, 4]
---

# 📡 Playback State & Persistence

Playback state snapshots, persisted queues/history/key-value storage, the in-app API server, and the main-process proxied HTTP client.

> ⚠️ The `ctx.events` group (`onTrackChange` / `onPlayStateChange` / `onVolumeChange`) from older revisions **does not exist** in the preload. Subscribe to playback events via `electron.player.on*` (see the audio events section of [Audio Engine](audio-engine)); state pushed to desktop lyrics / mini player windows uses `electron.nowPlaying.syncSnapshot` (see [Window & Interaction Management](window-management)).

---

## Playback state storage (electron.storage.\*)

Persistence built on `echo-sqlite-store` (SQLite), restored after restart. The full preload `electron.storage` API:

### Snapshot and multi-queue

| API | Description |
|-----|-------------|
| `getPlaybackSnapshot()` | Full snapshot: `{ queues[], activeQueueId, lastNonFmQueueId }` |
| `getPlaybackQueue({ queueId })` | A single queue (`StoragePlaybackQueueState \| null`) |
| `replacePlaybackQueue({ queue, activeQueueId, lastNonFmQueueId })` | Replace a queue (with ownership info) |
| `appendPlaybackQueueItems({ queue, songs, ... })` | Append songs to a queue |
| `updatePlaybackQueueMeta({ queue, ... })` | Update queue metadata |
| `clearPlaybackQueue({ queue, ... })` | Clear a queue's contents |
| `removePlaybackQueue({ queueId })` | Delete an entire queue |
| `removePlaybackQueueItem({ queueId, songId, ... })` | Remove a song from a queue |
| `reorderPlaybackQueueItems({ queueId, songs })` | Reorder a queue |
| `setQueueCurrentTrack({ queueId?, trackId? })` | Set a queue's current track |
| `setActiveQueue(queueId)` | Switch the active queue |

EchoMusic uses a **multi-queue model**: Personal FM, default playback, playlists, daily recommendations etc. are each independent queues (`type` is one of `default` / `fm` / `playlist` / `daily-recommend` / `home-discover` / `style-recommend` / `ranking` / `album` / `artist` / `search` / `history` / `cloud` / `listen-together` / `manual` / `purchased` / `free-listen`). The snapshot records `activeQueueId` and `lastNonFmQueueId` (the anchor for returning from FM to normal playback). Each queue carries `songs` (`StorageSong[]`), `currentTrackId`, `queuedNextTrackIds`, `filteredInvalidCount`, `dynamic`, `meta`, etc.; writes other than `getPlaybackSnapshot` / `removePlaybackQueue` return `StorageResetResult` (a reset impact summary).

### Play history

| API | Description |
|-----|-------------|
| `getHistoryEntries(payload?)` | Query history (`StorageHistoryEntry[]`, aggregated per song) |
| `recordHistoryPlay(payload)` | Record one play (returns the latest entry) |
| `removeHistoryEntries(payload)` | Remove specific history entries |
| `clearHistory()` | Clear history |

### Key-value store

| API | Description |
|-----|-------------|
| `getKv<T>(key)` | Read any JSON value (returned deserialized) |
| `setKv(key, value)` | Write a JSON value |
| `deleteKv(key)` | Delete a key |
| `resetAll()` | Wipe all storage (KV + queues + history) |

### Underlying SQLite tables

Tables created by `echo-sqlite-store`'s `initialize` (see [Native Addons](/en/develop/native-addons)):

| Table | Purpose |
|-------|---------|
| `app_kv` | Key-value store (`key` / `value_json` / `updated_at`) |
| `playback_queues` | Multi-queue metadata (`active` / `last_non_fm` / `current_track_id` / `meta_json` etc.) |
| `songs` | Song pool (deduplicated by `song_key` primary key, full track in `payload_json`) |
| `queue_items` | Queue entries (`(queue_id, position)` primary key, cascading foreign keys) |
| `play_history` | Play history (`song_key` primary key, unique `history_key`, `play_count`, `last_played_at`) |

> ⚠️ **There is no favorites table** — favorites are cloud-side KuGou account data, not persisted in local SQLite.

Plugins' controlled SQL access to the main database is provided by the `echo-sqlite-store` `plugin_sqlite_*` functions (`plugin_sqlite_all` / `run` / `exec` / `transaction` / `open` / `close`, etc.), wrapped by the main process in `src/main/plugins/sqlite.ts` and exposed to plugins as `electron.plugins.sqlite.*` (documented in [Plugin SQLite Storage](/en/develop/plugin-dev/filesystem-storage)).

---

## In-app API server (electron.apiServer)

This `apiServer` is **not** a local HTTP server: it is the **in-process host** of the KuGou API submodule (KuGouMusicApi), called via direct IPC with **no HTTP port** (architecture in the [Kugou API Reference](/en/develop/kugou-api)).

| API | Description |
|-----|-------------|
| `start()` | Start the in-process API host |
| `status()` | `{ state: "idle" \| "starting" \| "ready" \| "failed", error?, updatedAt }` |
| `identity()` | Device identity `{ guid, mac, serverDev, mid }` |

> ⚠️ The `status() → { running, port }` shape in older revisions is incorrect: the current implementation returns the four-state `ApiServerStatus` above, with no listenable port.

---

## Settings backup (electron.settingsBackup)

| API | Description |
|-----|-------------|
| `export(request)` | Export settings and data (`SettingsBackupExportResult`) |
| `inspect()` | Inspect the current backup file (`SettingsBackupInspectResult`) |
| `import(request)` | Restore from a backup (`SettingsBackupImportResult`) |

Backups cover app settings, playback queues, history and other local data. Plugin-level backups (`plugins.backups.create/inspect/restore`) are a separate mechanism — see [Plugin Data & Backups](/en/develop/plugin-dev/backups).

---

## HTTP requests (electron.api.request)

Main-process proxied HTTP client running on the KuGou API host's network stack (automatically subject to the [network settings](system-features) proxy policy).

```js
const result = await electron.api.request({
  method: "GET",
  url: "https://api.example.com/data",
  params: { page: 1 },
  headers: { "X-Custom": "value" },
  data: { /* request body */ },
});
console.log(result.data);
```

| Parameter | Type | Required | Description |
|-----------|------|:--:|-------------|
| `method` | `string` | ✅ | HTTP method |
| `url` | `string` | ✅ | Request URL |
| `params` | `object` | ❌ | URL query parameters |
| `data` | `any` | ❌ | Request body; binary bodies (`ArrayBuffer`/views, e.g. recognition PCM) are passed through via structured clone, JSON objects are serialized normally |
| `headers` | `object` | ❌ | Custom request headers |

---

## 📂 Related Documents

- [Internal API Overview](/en/develop/internal-api/) — module map
- [Audio Engine](/en/develop/internal-api/audio-engine) — engine events and control
- [Window & Interaction Management](/en/develop/internal-api/window-management) — nowPlaying snapshot sync
- [System Features](/en/develop/internal-api/system-features) — network settings and diagnostics
