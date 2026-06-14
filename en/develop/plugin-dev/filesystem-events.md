---
title: File Storage & Events
outline: [2, 4]
---

# 📁 File Storage & Events

This document covers file system access, KV storage, event listeners, and appearance subscription for plugins.

## File System

> Requires capability: `localFiles: true`

`ctx.fs` provides access to the local file system.

### API

| Method | Description | Returns |
|--------|------|------|
| `listFiles(dir)` | Scan directory, return file list | `Promise<FileEntry[]>` |
| `readTextFile(path)` | Read text file content | `Promise<string>` |
| `readFileBytes(path)` | Read binary file | `Promise<ArrayBuffer>` |
| `getFileUrl(path)` | Get a playable URL for a file | `Promise<string>` |
| `writeFile(relativePath, content)` | Write file within plugin directory | `Promise<void>` |

### Scanning Local Music Directories

```js
export function activate(ctx) {
  // Scan Music directory for audio files
  async function scanMusicDir() {
    try {
      const files = await ctx.fs.listFiles("C:\\Users\\User\\Music");
      const audioFiles = files.filter(f =>
        f.name.endsWith(".mp3") || f.name.endsWith(".flac") || f.name.endsWith(".wav")
      );
      console.log(`Found ${audioFiles.length} audio files`);
      return audioFiles;
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
  // url is a playable file:// or blob:// URL
  ctx.player.playTrack({
    id: filePath,
    title: filePath.split("\\").pop(),
    url: url,
  });
}
```

### Writing Plugin Data

```js
// Write configuration to plugin directory
await ctx.fs.writeFile("user-config.json", JSON.stringify({
  theme: "dark",
  fontSize: 14,
}, null, 2));
```

> ⚠️ `writeFile` can only write files **within the plugin directory**. External paths are not allowed.

---

## KV Storage

`ctx.storage` provides a simple key-value store with persistent, per-plugin isolation.

| Method | Description | Returns |
|--------|------|------|
| `get(key)` | Read a value by key | `Promise<any>` |
| `set(key, value)` | Write a value by key | `Promise<void>` |

### Basic Usage

```js
export function activate(ctx) {
  // Write settings
  await ctx.storage.set("theme", "dark");
  await ctx.storage.set("playbackSpeed", 1.25);
  await ctx.storage.set("recentSearches", ["Jay Chou", "Taylor Swift"]);

  // Read settings
  const theme = await ctx.storage.get("theme");
  const recent = await ctx.storage.get("recentSearches");

  console.log("Theme:", theme);        // "dark"
  console.log("Recent searches:", recent); // ["Jay Chou", "Taylor Swift"]
}
```

### Use Cases

| Scenario | Example |
|----------|--------|
| User settings | Toggle states, font size, color preferences |
| Cached data | Search results, song metadata, custom playlists |
| Plugin state | First-run flag, feature toggles |

### Best Practices

```js
// ✅ Recommended: structured storage
await ctx.storage.set("settings", {
  theme: "dark",
  autoScroll: true,
  fontSize: 14,
});

// ✅ Recommended: version your storage schema
await ctx.storage.set("version", 2);
const currentVersion = await ctx.storage.get("version") || 1;

// ⚠️ Note: values must be JSON-serializable
// Functions, Date objects, Map, Set, etc. are not supported
```

---

## Event Listeners

`ctx.events` provides subscriptions to core player events.

| API | Parameter | Description |
|-----|-----------|------|
| `onTrackChange(handler)` | `(track) => void` | Fires on track change |
| `onPlayStateChange(handler)` | `(isPlaying) => void` | Play/pause state change |
| `onVolumeChange(handler)` | `(volume) => void` | Volume change |

### Usage Example

```js
export function activate(ctx) {
  // Track change
  ctx.events.onTrackChange((track) => {
    console.log(`🎵 Now playing: ${track.title} - ${track.artist}`);
    // Update custom UI
    updateNowPlaying(track);
  });

  // Play state change
  ctx.events.onPlayStateChange((isPlaying) => {
    console.log(isPlaying ? "▶ Playing" : "⏸ Paused");
  });

  // Volume change
  ctx.events.onVolumeChange((volume) => {
    console.log(`🔊 Volume: ${volume}%`);
  });
}
```

### Event Lifecycle

- Listeners registered via `ctx.events` are **automatically removed** when the plugin is disabled/uninstalled
- No need to manually unregister in `deactivate()`

---

## Appearance Subscription

`ctx.appearance` allows plugins to respond to theme and appearance changes.

| API | Description |
|-----|------|
| `getSnapshot()` | Get current appearance snapshot |
| `onSnapshot(handler)` | Subscribe to appearance changes |

### Appearance Snapshot Structure

```js
const snapshot = await ctx.appearance.getSnapshot();
// {
//   themeColor: "#FF6B6B",     // Theme color
//   darkMode: true,            // Whether dark mode is active
//   fontFamily: "Microsoft YaHei", // Font family
//   fontSize: 14,              // Font size
// }
```

### Responding to Theme Changes

```js
export function activate(ctx) {
  async function updateTheme() {
    const { themeColor, darkMode } = await ctx.appearance.getSnapshot();
    // Adjust plugin UI colors
    document.documentElement.style.setProperty("--plugin-accent", themeColor);
    document.documentElement.style.setProperty("--plugin-bg", darkMode ? "#1a1a1a" : "#ffffff");
  }

  // Initial application
  updateTheme();

  // Subscribe to changes
  ctx.appearance.onSnapshot((newTheme) => {
    document.documentElement.style.setProperty("--plugin-accent", newTheme.themeColor);
    document.documentElement.style.setProperty("--plugin-bg", newTheme.darkMode ? "#1a1a1a" : "#ffffff");
  });
}
```

> Using host-provided CSS variables like `var(--theme-color)` is simpler for following theme changes without JS subscriptions.

---

## Complete Example: Playback Stats Plugin with Storage

```js
export function activate(ctx) {
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

  async function showStats() {
    const stats = (await ctx.storage.get(STAT_KEY)) || {};
    const entries = Object.values(stats)
      .sort((a, b) => b.playCount - a.playCount)
      .slice(0, 10);

    console.table(
      entries.map(e => ({
        Song: e.title,
        Artist: e.artist,
        Plays: e.playCount,
        "Last Played": e.lastPlayed?.slice(0, 10),
      }))
    );
  }

  // Record every track change
  ctx.events.onTrackChange(recordPlay);

  // Register a page to show stats
  const { h } = ctx.vue;
  const StatsPage = ctx.vue.defineComponent({
    setup() {
      const { ref, onMounted } = ctx.vue;
      const topTracks = ref([]);

      onMounted(async () => {
        const stats = (await ctx.storage.get(STAT_KEY)) || {};
        topTracks.value = Object.values(stats)
          .sort((a, b) => b.playCount - a.playCount)
          .slice(0, 20);
      });

      return () =>
        h("div", { class: "page-container" }, [
          h("h1", "📊 Playback Stats"),
          h("div", { class: "track-list" },
            topTracks.value.map(t =>
              h("div", { class: "track-item" }, [
                h("span", t.title),
                h("span", { style: "color: var(--color-text-secondary); margin-left: 8px;" }, `${t.playCount} plays`),
              ])
            )
          ),
        ]);
    },
  });

  ctx.ui.addPage({
    id: "play-stats",
    title: "Playback Stats",
    icon: "📊",
    component: StatsPage,
  });
}
```

---

## Next Steps

| Document | Content |
|----------|------|
| [Publishing & Distribution →](./publishing) | Publish plugins to the online registry |
| [Player & Audio →](./player-audio) | Playback control, spectrum, lyrics system |
| [Plugin Development Overview →](./) | Back to overview |
