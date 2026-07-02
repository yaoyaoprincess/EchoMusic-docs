---
title: Filesystem & Storage
outline: [2, 4]
---

# 📁 Filesystem & Storage

This document covers plugin access to the filesystem, KV storage, playback queue persistence, HTTP requests, event listeners, and appearance subscriptions.

---

## Filesystem

> Requires capability: `localFiles: true`

`ctx.fs` provides access to the local filesystem.

### API

| Method | Parameters | Description | Returns |
|------|------|------|------|
| `listFiles(options)` | `{ directory?, extensions?, recursive? }` | Scan directory for audio files | `Promise<FileEntry[]>` |
| `listImageFiles(options)` | `{ directory?, extensions?, recursive? }` | Scan directory for image files | `Promise<FileEntry[]>` |
| `readTextFile(options)` | `{ path, encoding? }` | Read text file content | `Promise<string>` |
| `readFileBytes(options)` | `{ path, offset?, length? }` | Read binary file | `Promise<ArrayBuffer>` |
| `writeFile(options)` | `{ path, data, encoding? }` | Write file to plugin directory | `Promise<void>` |
| `deleteFile(path)` | `path: string` | Delete file in plugin directory | `Promise<boolean>` |
| `getFileUrl(path)` | `path: string` | Get file playback URL | `Promise<string>` |

### Scanning Local Music

```js
export function activate(ctx) {
  async function scanMusicDir() {
    try {
      const files = await ctx.fs.listFiles({
        directory: "C:\\Users\\User\\Music",
        extensions: [".mp3", ".flac", ".wav"],
        recursive: true,
      });
      console.log(`Found ${files.length} audio files`);
      return files;
    } catch (err) {
      ctx.toast.error("Failed to scan directory: " + err.message);
      return [];
    }
  }

  scanMusicDir();
}
```

### Playing Local Files

```js
async function playLocalFile(filePath) {
  const url = await ctx.fs.getFileUrl(filePath);
  ctx.player.playTrack({
    id: filePath,
    title: filePath.split("\\").pop(),
    url: url,
  });
}
```

### Reading and Writing Files

```js
// Read text file
const text = await ctx.fs.readTextFile({ path: "C:\\logs\\app.log" });

// Read portion of binary file
const bytes = await ctx.fs.readFileBytes({
  path: "C:\\Data\\large.dat",
  offset: 0,
  length: 1024,
});

// Write config to plugin directory
await ctx.fs.writeFile({
  path: "user-config.json",
  data: JSON.stringify({ theme: "dark", fontSize: 14 }, null, 2),
});

// Delete file
await ctx.fs.deleteFile("old-cache.json");
```

> ⚠️ `writeFile` and `deleteFile` can only operate on files **within the plugin directory**. `readTextFile` / `readFileBytes` can read from any path.

---

## KV Storage

`ctx.storage` provides per-plugin isolated persistent key-value storage.

| API | Description | Returns |
|-----|------|------|
| `kvGet(key)` | Read key-value | `Promise<any>` |
| `kvSet(key, value)` | Write key-value | `Promise<void>` |
| `kvDelete(key)` | Delete key-value | `Promise<void>` |

### Basic Usage

```js
export function activate(ctx) {
  // Write settings
  await ctx.storage.kvSet("theme", "dark");
  await ctx.storage.kvSet("playbackSpeed", 1.25);
  await ctx.storage.kvSet("recentSearches", ["Jay Chou", "Taylor Swift"]);

  // Read settings
  const theme = await ctx.storage.kvGet("theme");
  const recent = await ctx.storage.kvGet("recentSearches");

  console.log("Theme:", theme);        // "dark"
  console.log("Recent searches:", recent);    // ["Jay Chou", "Taylor Swift"]

  // Delete
  await ctx.storage.kvDelete("temp-cache");
}
```

### Best Practices

```js
// ✅ Recommended: structured storage
await ctx.storage.kvSet("settings", {
  theme: "dark",
  autoScroll: true,
  fontSize: 14,
});

// ✅ Recommended: version-controlled storage structure
await ctx.storage.kvSet("version", 2);
const currentVersion = (await ctx.storage.kvGet("version")) || 1;
if (currentVersion < 2) {
  // Migrate old data structure
}

// ⚠️ Note: values must be JSON-serializable
// Cannot store functions, Date objects, Map, Set, etc.
```

### Lifecycle

- When the plugin is **uninstalled**, all KV data is **automatically cleared**
- When the plugin is updated (version upgrade), KV data is preserved
- When the plugin is disabled then re-enabled, KV data is preserved

---

## SQLite Database

> Requires capability: `sqlite: true`

`ctx.sqlite` provides a plugin-private SQLite database, created and managed by the host in EchoMusic's user data directory. Databases are isolated by plugin ID — plugins can only access their own named databases and cannot pass arbitrary local paths.

### Opening a Database

```js
const db = await ctx.sqlite.open({
  name: "library",                        // Optional, defaults to "main"
  migrations: [                           // Optional, versioned migration
    { version: 1, sql: `CREATE TABLE IF NOT EXISTS songs (
      id TEXT PRIMARY KEY,
      title TEXT NOT NULL,
      artist TEXT NOT NULL,
      play_count INTEGER DEFAULT 0
    )` },
    { version: 2, sql: `ALTER TABLE songs ADD COLUMN rating INTEGER DEFAULT 0` }
  ]
});
```

Database names can only contain letters, digits, dots, underscores, and hyphens, and must start with a letter or digit.

### CRUD Operations

| API | Description |
|-----|------|
| `db.run(sql, params?)` | Execute INSERT/UPDATE/DELETE, returns `{ changes: n }` |
| `db.get(sql, params?)` | Query a single row, returns `{ ok, row? }` or `null` |
| `db.all(sql, params?)` | Query multiple rows, returns `{ ok, rows }` |
| `db.exec(sql)` | Execute arbitrary SQL (CREATE TABLE, etc.) |

```js
// Write
await db.run("INSERT OR REPLACE INTO songs (id, title, artist, play_count) VALUES (?, ?, ?, ?)",
  ["1001", "Sunny Day", "Jay Chou", 42]);

// Query single row
const row = await db.get("SELECT * FROM songs WHERE id = ?", ["1001"]);
console.log(row.row?.title); // "Sunny Day"

// Query multiple rows
const list = await db.all("SELECT * FROM songs ORDER BY play_count DESC");
for (const item of list.rows) {
  console.log(item.title, item.play_count);
}
```

### Parameters & BLOBs

Parameters support `string`, `number`, `boolean`, and `null`. For binary data, wrap in an object:

```js
// Write BLOB (hex or base64)
await db.run("INSERT INTO covers (id, data) VALUES (?, ?)", [
  "album-cover",
  { type: "base64", data: "iVBORw0KGgo=" }
]);

// Query BLOB, always returns hex string
const row = await db.get("SELECT data FROM covers WHERE id = ?", ["album-cover"]);
console.log(row.row?.data); // { type: "hex", data: "89504e47..." }
```

### Transactions

```js
await db.transaction([
  ["UPDATE songs SET play_count = play_count + 1 WHERE id = ?", ["1001"]],
  ["INSERT INTO play_log (song_id, time) VALUES (?, ?)", ["1001", Date.now()]]
]);
```

Up to 500 statements per transaction, max ~256 KB per SQL statement, max 5000 rows per query, max ~8 MB result JSON.

### Database Management

| API | Description |
|-----|------|
| `ctx.sqlite.listDatabases()` | List all database names for this plugin |
| `ctx.sqlite.deleteDatabase(name?)` | Delete a named database (defaults to `main`) |
| `db.close()` | Close the current connection |

```js
const databases = await ctx.sqlite.listDatabases();
// ["main", "library", "cache"]

await ctx.sqlite.deleteDatabase("cache");
```

### Lifecycle

- Database files are created on the first `ctx.sqlite.open()` after plugin install
- Connections are automatically closed when the plugin is disabled, in safe mode, or EchoMusic exits
- Plugin **uninstall** deletes the entire SQLite private directory for that plugin
- Plugin update (version upgrade) preserves databases
- The host intercepts `ATTACH`, `DETACH`, `VACUUM INTO`, `load_extension()`, and other boundary-violating statements

---

## Playback Queue Persistence

The `ctx.storage.playback*` API family operates on the persistent playback queue.

| API | Description |
|-----|------|
| `playbackGetSnapshot()` | Get current playback state snapshot |
| `playbackGetQueue()` | Get complete playback queue |
| `playbackReplaceQueue(items)` | Replace entire queue |
| `playbackAppendQueueItems(items)` | Append tracks to queue end |
| `playbackRemoveQueueItem(songId)` | Remove track from queue |
| `playbackReorderQueueItems(from, to)` | Reorder track positions |
| `playbackSetCurrentTrack(songId)` | Set current playing track |
| `playbackUpdateMeta(meta)` | Update queue metadata (e.g., queue name) |

```js
// Save current playback state
const snapshot = await ctx.storage.playbackGetSnapshot();
console.log("Current track:", snapshot.currentTrack);

// Get full queue
const queue = await ctx.storage.playbackGetQueue();

// Add tracks and maintain order
await ctx.storage.playbackAppendQueueItems([newTrack]);

// Move 3rd track to 1st position
await ctx.storage.playbackReorderQueueItems(2, 0);
```

> Difference from `ctx.player.playlist.*`: `playback*` APIs are persistent storage operations (restored after restart), while `ctx.player.playlist.*` are runtime queue operations.

---

## HTTP Requests

`ctx.api.request()` provides a unified HTTP client.

```js
const result = await ctx.api.request({
  method: "GET",
  url: "https://api.example.com/data",
  params: { page: 1, limit: 20 },
  headers: {
    "X-Custom-Header": "value",
  },
});

console.log(result.data);

// POST request
await ctx.api.request({
  method: "POST",
  url: "https://api.example.com/submit",
  data: { name: "test", value: 123 },
});
```

| Parameter | Type | Required | Description |
|------|------|:--:|------|
| `method` | `string` | ✅ | HTTP method |
| `url` | `string` | ✅ | Request URL |
| `params` | `object` | ❌ | URL query parameters |
| `data` | `any` | ❌ | Request body data |
| `headers` | `Record<string, string>` | ❌ | Custom headers |

---

## Event Listeners

`ctx.events` provides core player event subscriptions.

| API | Callback Parameters | Description |
|-----|----------|------|
| `onTrackChange(fn)` | `(track) => void` | Track change |
| `onPlayStateChange(fn)` | `(isPlaying) => void` | Play/pause state |
| `onVolumeChange(fn)` | `(volume) => void` | Volume change |

```js
export function activate(ctx) {
  ctx.events.onTrackChange((track) => {
    console.log(`🎵 Now playing: ${track.title} - ${track.artist}`);
    updateNowPlaying(track);
  });

  ctx.events.onPlayStateChange((isPlaying) => {
    console.log(isPlaying ? "▶ Playing" : "⏸ Paused");
  });

  ctx.events.onVolumeChange((volume) => {
    console.log(`🔊 Volume: ${volume}%`);
  });
}
```

- Listeners registered via `ctx.events` are **automatically removed** when the plugin is disabled/uninstalled
- No need to manually cancel listeners in `deactivate()`

---

## Appearance Subscription

`ctx.appearance` allows plugins to respond to theme and appearance changes.

| API | Description |
|-----|------|
| `getSnapshot()` | Get current appearance snapshot |
| `onSnapshot(fn)` | Subscribe to appearance changes |

### Appearance Snapshot Structure

```js
const snapshot = await ctx.appearance.getSnapshot();
// {
//   themeColor: "#FF6B6B",        // Theme color
//   darkMode: true,               // Whether dark mode
//   fontFamily: "Microsoft YaHei", // Font
//   fontSize: 14,                 // Font size
// }
```

### Responding to Theme Changes

```js
export function activate(ctx) {
  async function updateTheme() {
    const { themeColor, darkMode } = await ctx.appearance.getSnapshot();
    document.documentElement.style.setProperty("--plugin-accent", themeColor);
    document.documentElement.style.setProperty("--plugin-bg",
      darkMode ? "#1a1a1a" : "#ffffff"
    );
  }

  updateTheme();

  ctx.appearance.onSnapshot((newTheme) => {
    document.documentElement.style.setProperty("--plugin-accent", newTheme.themeColor);
  });
}
```

> Using CSS variables like `var(--theme-color)` provided by the host is simpler for following theme changes and doesn't require JS subscriptions.

---

## Complete Example: Play Stats Plugin with Storage

```js
export function activate(ctx) {
  const STAT_KEY = "playStats";

  async function recordPlay(track) {
    const stats = (await ctx.storage.kvGet(STAT_KEY)) || {};
    const trackKey = `${track.id || track.title}`;

    stats[trackKey] = stats[trackKey] || {
      title: track.title,
      artist: track.artist,
      playCount: 0,
      lastPlayed: null,
    };

    stats[trackKey].playCount++;
    stats[trackKey].lastPlayed = new Date().toISOString();

    await ctx.storage.kvSet(STAT_KEY, stats);
  }

  async function showStats() {
    const stats = (await ctx.storage.kvGet(STAT_KEY)) || {};
    const entries = Object.values(stats)
      .sort((a, b) => b.playCount - a.playCount)
      .slice(0, 10);

    console.table(
      entries.map(e => ({
        Song: e.title,
        Artist: e.artist,
        Plays: e.playCount,
        LastPlayed: e.lastPlayed?.slice(0, 10),
      }))
    );
  }

  // Record on every track change
  ctx.events.onTrackChange(recordPlay);

  // Register a page to display stats
  const { h } = ctx.vue;
  const StatsPage = ctx.vue.defineComponent({
    setup() {
      const { ref, onMounted } = ctx.vue;
      const topTracks = ref([]);

      onMounted(async () => {
        const stats = (await ctx.storage.kvGet(STAT_KEY)) || {};
        topTracks.value = Object.values(stats)
          .sort((a, b) => b.playCount - a.playCount)
          .slice(0, 20);
      });

      return () =>
        h("div", { class: "page-container" }, [
          h("h1", "📊 Play Stats"),
          h("div", { class: "track-list" },
            topTracks.value.map(t =>
              h("div", { class: "track-item" }, [
                h("span", t.title),
                h("span", { style: "color: var(--color-text-secondary); margin-left: 8px;" },
                  `${t.playCount} plays`),
              ])
            )
          ),
        ]);
    },
  });

  ctx.ui.addPage({
    id: "play-stats",
    title: "Play Stats",
    icon: "📊",
    component: StatsPage,
  });
}
```

---

## Next Steps

| Document | Content |
|------|------|
| [Player & Audio Engine →](./player-audio) | Playback controls, EQ, spatial audio, lyrics system |
| [Windows & System →](./windows-system) | Floating windows, desktop lyric, Mini player |
| [API Reference →](./context-api) | Complete ctx API listing |
