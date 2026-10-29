---
title: Filesystem & Storage
outline: [2, 4]
---

# 📁 Filesystem & Storage

This document covers plugin access to the filesystem, KV storage, and appearance subscriptions.

> ℹ️ Playback queue persistence, HTTP requests, core event listeners, and similar facilities are internal APIs and out of scope for plugins. See [Internal API Reference →](../internal-api/).

---

## Filesystem

> Requires capability: `localFiles: true` (most operations)

`ctx.fs` provides access to the local filesystem.

### API

| Method | Description | Returns |
|------|------|------|
| `listFiles(directory, opts?)` | Scan a directory; supports `recursive`, `kinds`, `extensions`, `limit`, `maxDepth`, `includeHidden`; the directory can be a path or a `DirectoryRef` | `Promise<{ok, files[]}>` |
| `listImageFiles(directory, opts?)` | Scan for image files | `Promise<{ok, files[]}>` |
| `readTextFile(path, opts?)` | Read a text file, 1 MB default cap; path or `FileRef` | `Promise<{ok, text}>` |
| `readFileBytes(path, opts?)` | Read a binary file, 1 MB default cap; path or `FileRef` | `Promise<{ok, data}>` |
| `readAudioMetadata(path)` | Read title, duration, cover, and other metadata from an audio file; path or `FileRef` | `Promise<{ok, metadata}>` |
| `writeFile(path, data, opts?)` | Write a file into the plugin directory, 8 MB cap | `Promise<{ok, path}>` |
| `deleteFile(path)` | Delete a file inside the plugin directory | `Promise<{ok}>` |
| `getFileUrl(path)` | Get the file's `file://` playback URL | `Promise<{ok, url}>` |

Besides these "bare path" APIs there is a set of **grant-based** file and directory APIs — see the next section, "Granted files & directories".

### Scanning local music directories

```js
export async function activate(ctx) {
  const result = await ctx.fs.listFiles("C:\\Users\\User\\Music", {
    recursive: true,
    kinds: ["audio", "lyric", "image", "playlist", "cue"],
    limit: 5000,
  });

  if (result.ok) {
    console.log(`Found ${result.files.length} files`);
  }
}
```

### Playing local files

```js
async function playLocalFile(filePath) {
  const urlResult = await ctx.fs.getFileUrl(filePath);
  if (urlResult?.ok) {
    ctx.player.playTrack({
      id: filePath,
      title: filePath.split("\\").pop(),
      url: urlResult.url,
    });
  }
}
```

### Reading and writing files

```js
// Read a text file
const textResult = await ctx.fs.readTextFile("C:\\logs\\app.log");

// Read part of a binary file
const bytesResult = await ctx.fs.readFileBytes("C:\\Data\\large.dat", {
  maxBytes: 1024,
});

// Write config into the plugin directory
const writeResult = await ctx.fs.writeFile("user-config.json", JSON.stringify({
  theme: "dark",
  fontSize: 14,
}, null, 2));

// Overwrite an existing file
await ctx.fs.writeFile("cache.json", data, { overwrite: true });

// Delete a file
await ctx.fs.deleteFile("old-cache.json");
```

> ⚠️ `writeFile` and `deleteFile` can only operate on files **inside the plugin directory** (automatically confined to the safe scope). `readTextFile` / `readFileBytes` can read any user-selected path. For large audio files use `getFileUrl()`; never read a whole audio file through `readFileBytes()`.

---

## Granted files & directories

Large files outside the plugin directory (videos, lyric libraries, export folders) should not be accessed with bare paths. The host provides grant-based file APIs: after the user authorizes a directory or file through the system picker, the plugin receives references (`DirectoryRef` / `FileRef`), and all subsequent operations use the reference id plus relative paths — never bare paths.

> Requires capability: `localFiles: true`. The first selection only opens the system picker; once a selection succeeds the host registers the grant with no extra confirmation dialog. Users can review and revoke all grants per plugin in "Granted files & directories" at the top of the plugin management page.

### Requesting grants

```js
// Request directory access
const selection = await ctx.fs.requestDirectory({
  access: "read-write",        // "read" | "read-write"
  purpose: "Save plugin assets", // purpose shown to the user
  persist: true,               // default true; false lasts only for this main-process session
});
if (selection.ok && !selection.canceled) {
  const directory = selection.directory; // DirectoryRef
  console.log("Granted directory:", directory.name, directory.displayPath);
}

// Request file access
const picked = await ctx.fs.requestFiles({
  purpose: "Use as video theme background",
  persist: true,
  multiple: false,
  filters: [{ name: "Videos", extensions: ["mp4", "webm", "mov", "m4v"] }],
});
if (picked.ok && !picked.canceled) {
  const file = picked.files[0]; // FileRef
}
```

`requestDirectory` / `requestFiles` return result objects: `{ ok: true, canceled: true }` or `{ ok: true, canceled: false, directory }` / `{ ok: true, canceled: false, files: FileRef[] }`; on failure `{ ok: false, error }`.

### Reference structure

```ts
interface DirectoryRef {
  id: string;
  name: string;
  access: "read" | "read-write";
  kind: "user" | "data" | "cache";
  available: boolean;
  displayPath?: string;   // for display only
}

type FileRef =
  | { kind: "directory-file"; directoryId: string; relativePath: string }
  | { kind: "selected-file"; fileId: string };
```

Relative paths reject escaping, absolute paths, symlinks, Windows device names, and anything else that cannot be safely written to disk. Plugins should persist the `DirectoryRef.id` and file relative paths, then reconstruct `FileRef` objects on the next launch.

### Grant management

| API | Description |
|-----|------|
| `listDirectoryGrants()` | List registered directory grants (including unavailable/revoked entries; no single-file grants) |
| `reauthorizeDirectoryGrant(id, request)` | Reopen the picker to renew the grant; the same path keeps its id, picking a different directory yields a new id |
| `revokeDirectoryGrant(id)` | Revoke a directory grant (keeps the actual files; aborts related transfers and closes media leases) |
| `revokeFileGrant(id)` | Revoke a single-file grant |

These methods **throw** errors carrying `code` / `message` / `retryable` on failure (unlike the result-object convention of `request*`).

### Private directories and file operations

```js
// Plugin-private directories created and managed by the host — no picker, not listed in grant management
const dataDir = await ctx.fs.getPrivateDirectory({ kind: "data" });  // or "cache"
const video = { kind: "directory-file", directoryId: dataDir.id, relativePath: "videos/bg.mp4" };

// File operations on references
const stat = await ctx.fs.stat(video);        // { file, name, size, modifiedAt, directory }
await ctx.fs.mkdir({ kind: "directory-file", directoryId: dataDir.id, relativePath: "videos" });

// Large-file streaming copy (no 8 MB cap); returns the same handle as download tasks
const task = await ctx.fs.copyFile(sourceFileRef, { directoryId: dataDir.id, relativePath: "copy.mp4" }, {
  conflict: "rename",   // "fail" (default) | "rename" | "replace"
});
await task.wait();

// Open a media lease: turn a file into a URL usable by <video>/<audio>/<img>
const lease = await ctx.fs.openMedia(video);
videoElement.src = lease.url;
// Release when unmounting or switching sources
// videoElement.pause(); videoElement.removeAttribute("src"); videoElement.load();
lease.release();
```

| API | Description |
|-----|------|
| `getPrivateDirectory({ kind })` | Get this installation identity's private directory, `kind` is `"data"` or `"cache"` |
| `stat(file)` | Read name, size, modified time, and whether it is a directory |
| `mkdir(file)` | Create subdirectories inside a granted directory (including parents) |
| `copyFile(source, target, { conflict? })` | Streaming copy in the main process; returns a task handle supporting `wait()`/`subscribe()` |
| `openMedia(file)` | Create a media lease `{ id, url, release() }`; the URL is a short-term lease — never persist it |

> ⚠️ The media URL is a **short-term lease of the current plugin context**: disabling, safe mode, or an update closes the old context's leases. On each startup, check the local file with `stat()` first and call `openMedia()` again; keep media URLs in memory only.

### Reading audio metadata

```js
// Bare path overload
const meta = await ctx.fs.readAudioMetadata("D:\\Music\\song.flac");
if (meta.ok) {
  console.log(meta.title, meta.kind, meta.relativePath);
}

// FileRef overload (throws errors carrying a code)
try {
  const meta = await ctx.fs.readAudioMetadata(fileRef);
  console.log(meta.title);
} catch (error) {
  console.error(error.code, error.message);
}
```

Metadata parsing depends on the host version; plugins relying on it should declare a version floor via `requires.echoMusicVersion`.

---

## KV Storage

`ctx.storage` provides per-plugin isolated persistent key-value storage.

| API | Description | Returns |
|-----|------|------|
| `get(key)` | Read a key | `Promise<any>` (`null` when missing) |
| `set(key, value)` | Write a key | `Promise<void>` |
| `delete(key)` | Delete a key | `Promise<void>` |

### Basic Usage

```js
export async function activate(ctx) {
  // Write settings
  await ctx.storage.set("theme", "dark");
  await ctx.storage.set("playbackSpeed", 1.25);
  await ctx.storage.set("recentSearches", ["Jay Chou", "Taylor Swift"]);

  // Read settings (returns null when missing)
  const theme = (await ctx.storage.get("theme")) || "light";
  const recent = await ctx.storage.get("recentSearches");

  // Delete keys you no longer need
  await ctx.storage.delete("recentSearches");

  console.log("Theme:", theme);              // "dark"
  console.log("Recent searches:", recent);   // ["Jay Chou", "Taylor Swift"]
}
```

### Best Practices

```js
// ✅ Recommended: structured storage
await ctx.storage.set("settings", {
  theme: "dark",
  autoScroll: true,
  fontSize: 14,
});

// ✅ Recommended: version your storage structure
const version = (await ctx.storage.get("version")) || 1;
if (version < 2) {
  // Migrate the old data structure
  await ctx.storage.set("version", 2);
}

// ✅ Recommended: provide defaults when reading
const settings = (await ctx.storage.get("settings")) || defaults;

// ⚠️ Note: values must be JSON-serializable
// You cannot store functions, Date objects, Maps, Sets, DOM nodes, etc.
```

### Lifecycle

- When a plugin is **uninstalled**, all of its KV data is **cleared automatically**
- Plugin updates (version upgrades) preserve KV data
- Disabling and re-enabling a plugin preserves KV data

---

## SQLite Database

> Requires capability: `sqlite: true`

`ctx.sqlite` provides plugin-private SQLite databases, created and managed by the host under EchoMusic's user data directory, isolated by plugin id. Plugins can only access their own named databases and cannot pass arbitrary local paths.

### Opening a Database

```js
const db = await ctx.sqlite.open({
  name: "library",                        // optional, defaults to "main"
  migrations: [                           // optional, versioned migrations
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

Database names may only contain letters, digits, dots, underscores, and hyphens, and must start with a letter or digit.

### CRUD Operations

| API | Description |
|-----|------|
| `db.run(sql, params?)` | Execute INSERT/UPDATE/DELETE, returns `{ changes: n }` |
| `db.get(sql, params?)` | Query one row, returns `{ ok, row? }` or `null` |
| `db.all(sql, params?)` | Query many rows, returns `{ ok, rows }` |
| `db.exec(sql)` | Execute arbitrary SQL (CREATE TABLE, etc.) |

```js
// Write
await db.run("INSERT OR REPLACE INTO songs (id, title, artist, play_count) VALUES (?, ?, ?, ?)",
  ["1001", "Sunny Day", "Jay Chou", 42]);

// Query a single row
const row = await db.get("SELECT * FROM songs WHERE id = ?", ["1001"]);
console.log(row.row?.title); // "Sunny Day"

// Query many rows
const list = await db.all("SELECT * FROM songs ORDER BY play_count DESC");
for (const item of list.rows) {
  console.log(item.title, item.play_count);
}
```

### Parameters & BLOBs

Parameters support `string`, `number`, `boolean`, and `null`. Wrap binary data in an object:

```js
// Write a BLOB (hex or base64)
await db.run("INSERT INTO covers (id, data) VALUES (?, ?)", [
  "album-cover",
  { type: "base64", data: "iVBORw0KGgo=" }
]);

// Query a BLOB; always returned as a hex string
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

Up to 500 statements per transaction, ~256 KB max per SQL statement, up to 5000 rows per query, and ~8 MB max result JSON.

### Database Management

| API | Description |
|-----|------|
| `ctx.sqlite.listDatabases()` | List all databases for this plugin |
| `ctx.sqlite.deleteDatabase(name?)` | Delete a database (defaults to `main`) |
| `db.close()` | Close the current connection |

```js
const databases = await ctx.sqlite.listDatabases();
// ["main", "library", "cache"]

await ctx.sqlite.deleteDatabase("cache");
```

### Lifecycle

- Database files are created on the plugin's first `ctx.sqlite.open()` after installation
- Connections close automatically when the plugin is disabled, safe mode is on, or EchoMusic exits
- Plugin **uninstall** deletes the plugin's entire SQLite private directory
- Plugin updates (version upgrades) preserve databases
- The host intercepts out-of-bounds statements such as `ATTACH`, `DETACH`, `VACUUM INTO`, and `load_extension()`

---

## Appearance Subscription

`ctx.appearance` lets plugins react to theme and appearance changes.

| API | Description |
|-----|------|
| `getSnapshot()` | Get the current appearance snapshot |
| `onSnapshot(fn)` | Subscribe to appearance changes; returns a dispose function |

### Appearance snapshot structure

```js
const snapshot = await ctx.appearance.getSnapshot();
// {
//   accentColor: "#31cfa1",          // accent color
//   isDark: true,                    // whether dark mode
//   fontFamily: "Microsoft YaHei",   // global font (may be absent)
//   colors: { ... },                 // theme palette (may be absent)
//   floatingSurfaceFrosted: true,    // whether floating surfaces are frosted (may be absent)
// }
```

### Responding to theme changes

```js
export async function activate(ctx) {
  function applyTheme({ accentColor, isDark }) {
    document.documentElement.style.setProperty("--plugin-accent", accentColor);
    document.documentElement.style.setProperty(
      "--plugin-bg",
      isDark ? "#1a1a1a" : "#ffffff"
    );
  }

  applyTheme(await ctx.appearance.getSnapshot());

  ctx.appearance.onSnapshot(applyTheme);
}
```

---

## Theme API

`ctx.theme` provides deep customization of EchoMusic's interface styling. See the plugin repository [README](https://github.com/hoowhoami/EchoMusicPlugins) for details.

### Surface styles (ctx.theme.surface)

```js
ctx.theme.surface.set({
  enabled: true,
  mainOpacity: 82,
  sidebarOpacity: 82,
  cardOpacity: 86,
  elevatedOpacity: 88,
  dialogOpacity: 90,
  playerOpacity: 92,
  backdropFilter: "blur(10px)",
  playerBackdropFilter: "blur(20px) saturate(180%)",
});
ctx.theme.surface.clear(); // restore defaults
```

### Page transitions (ctx.theme.pageTransition)

```js
ctx.theme.pageTransition.set({
  enabled: true,
  mode: "out-in",
  appear: true,
  durationMs: 450,
  easing: "ease-out",
  enterOpacity: 0,
  leaveOpacity: 0,
  enterTranslateY: 6,
});
ctx.theme.pageTransition.clear();
```

### Accent gradient (ctx.theme.accentGradient)

```js
ctx.theme.accentGradient.set({
  color: "#ff5c8a",
  angle: 180,
  height: "46%",
  peakOpacity: 0.28,
  midOpacity: 0.1,
  dark: { peakOpacity: 0.4, midOpacity: 0.16 },
});
ctx.theme.accentGradient.clear();
```

---

## Scroll control

`ctx.scroll` provides advanced control over the host's page scroll containers.

| API | Description |
|-----|------|
| `queryContainers()` | Get all scroll containers |
| `getCurrentContainer()` | Get the current focused container |
| `getState(el?)` | Get the scroll state |
| `scrollToTop(el?)` | Scroll to the top |
| `scrollToBottom(el?)` | Scroll to the bottom |
| `observeContainers(handler)` | Observe scroll container changes |

See [UI Extension Guide →](./ui-extension) for the full scroll API (`selector`, `scrollTo`, `queryContainers({ role?, visible? })`, `observeContainers`).

---

## Complete Example: Play Stats Plugin with Storage

```js
export async function activate(ctx) {
  const STAT_KEY = "playStats";

  async function recordPlay(track) {
    const stats = (await ctx.storage.get(STAT_KEY)) || {};
    const trackKey = `${track.id || track.title}`;

    stats[trackKey] = stats[trackKey] || {
      title: track.title,
      artist: track.artist,
      playCount: 0,
      lastPlayed: null,
    };

    stats[trackKey].playCount++;
    stats[trackKey].lastPlayed = new Date().toISOString();

    await ctx.storage.set(STAT_KEY, stats);
  }

  // Watch track changes through a computed
  ctx.vue.watch(
    () => ctx.player.currentTrackId,
    (newId, oldId) => {
      if (newId && newId !== oldId) {
        recordPlay(ctx.player.currentTrack);
      }
    }
  );

  const { h, ref, onMounted } = ctx.vue;
  const StatsPage = ctx.vue.defineComponent({
    setup() {
      const topTracks = ref([]);

      onMounted(async () => {
        const stats = (await ctx.storage.get(STAT_KEY)) || {};
        topTracks.value = Object.values(stats)
          .sort((a, b) => b.playCount - a.playCount)
          .slice(0, 20);
      });

      return () =>
        h("div", { class: "page-container" }, [
          h("h1", "📊 Play Stats"),
          ...topTracks.value.map(t =>
            h("div", { class: "track-item" }, [
              h("span", t.title),
              h("span", { style: "color: var(--color-text-secondary); margin-left: 8px;" },
                `${t.playCount} plays`),
            ])
          ),
        ]);
    },
  });

  ctx.ui.addPage({
    id: "play-stats",
    title: "Play Stats",
    component: StatsPage,
  });
}
```

---

## Next Steps

| Document | Content |
|------|------|
| [Player & Audio Engine →](./player-audio) | Playback control, play queue, spectrum, lyrics system |
| [Windows & System →](./windows-system) | Floating windows, Now Playing, processes, icons |
| [API Overview →](./context-api) | Full plugin ctx API list |
| [Internal API Reference →](../internal-api/) | Internal APIs (persistence/events/HTTP, etc.) |
