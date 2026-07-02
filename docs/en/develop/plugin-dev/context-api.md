---
title: Context API Reference
outline: [2, 4]
---

# 🔧 Context API Reference

The `ctx` object is the core entry point for plugins, injected by EchoMusic when calling `activate(ctx)`. This document organizes all available properties and methods on `ctx` by category.

## Host Runtime

EchoMusic is built on Vue 3 + Pinia + Vue Router. Plugins can access these framework runtime instances directly via `ctx`.

### ctx.vue

Vue 3 runtime, providing `defineComponent`, `h`, `ref`, `computed`, `watch`, and other core APIs.

```js
const { defineComponent, h, ref, computed, watch, onMounted, onUnmounted } = ctx.vue;
```

| Property / Method | Type | Description |
|-------------------|:--:|------|
| `defineComponent(options)` | Function | Define a Vue component |
| `h(tag, props, children)` | Function | Render function (VNode) |
| `ref(value)` | Function | Create a reactive reference |
| `computed(getter)` | Function | Create a computed property |
| `watch(source, callback)` | Function | Watch reactive data changes |
| `onMounted(fn)` | Function | Callback after component mount |
| `onUnmounted(fn)` | Function | Callback before component unmount |
| `defineAsyncComponent(source)` | Function | Define an async component |

> ⚠️ Do **not** write `import { ref } from 'vue'`. The plugin runtime has no bare import support for `vue`. Always use `ctx.vue` instead.

### ctx.app

| Type | Description |
|:--:|------|
| Vue App instance | The main application's Vue app instance |

### ctx.router

| Type | Description |
|:--:|------|
| Router instance | Vue Router instance |

### ctx.pinia

| Type | Description |
|:--:|------|
| Pinia instance | Pinia state management instance |

---

## Stores

Access EchoMusic's core state through `ctx.stores`:

| Store | Description |
|-------|------|
| `ctx.stores.player` | Player state: current song, progress, volume, play mode, etc. |
| `ctx.stores.playlist` | Playlist state: queue list, add/remove songs |
| `ctx.stores.lyric` | Lyrics state: current lyric line, time offset |
| `ctx.stores.settings` | User settings state: theme, audio quality, shortcuts, etc. |
| `ctx.stores.theme` | Theme state: theme color, dark/light mode |

```js
export function activate(ctx) {
  // Read playback state
  console.log("Current volume:", ctx.stores.player.volume);

  // Watch settings changes
  ctx.vue.watch(
    () => ctx.stores.settings.someKey,
    (newVal) => {
      console.log("Setting changed to:", newVal);
    }
  );
}
```

---

## ctx.manifest

| Type | Description |
|:--:|------|
| `object` | Current plugin's manifest object (read-only) |

```js
console.log(ctx.manifest.id);      // "my-plugin"
console.log(ctx.manifest.name);    // "My Plugin"
console.log(ctx.manifest.version); // "1.0.0"
```

---

## UI Components

### ctx.ui.components

EchoMusic provides several built-in UI components that plugins can reuse:

| Component | Description |
|-----------|------|
| `ctx.ui.components.Button` | Button component |
| `ctx.ui.components.Switch` | Switch/toggle component |
| `ctx.ui.components.Input` | Input field component |

```js
const { defineAsyncComponent } = ctx.vue;
const Button = defineAsyncComponent(ctx.ui.components.Button);
const Switch = defineAsyncComponent(ctx.ui.components.Switch);
const Input = defineAsyncComponent(ctx.ui.components.Input);

// Use in render functions
ctx.vue.h(Button, { size: "xs", onClick: handleClick }, { default: () => "Save" });
ctx.vue.h(Switch, { modelValue: enabled.value, "onUpdate:modelValue": (v) => { enabled.value = Boolean(v); } });
```

### ctx.ui.addPage(options)

Register an independent sidebar page.

| Parameter | Type | Required | Description |
|-----------|------|:--:|------|
| `options.id` | `string` | ✅ | Unique page ID |
| `options.title` | `string` | ✅ | Page title (displayed in sidebar) |
| `options.icon` | `string` | ❌ | Sidebar icon (Emoji or SVG) |
| `options.component` | `Component` | ✅ | Vue component |
| `options.order` | `number` | ❌ | Sort weight, smaller values appear first |

```js
ctx.ui.addPage({
  id: "my-page",
  title: "My Page",
  icon: "🎵",
  component: MyPageComponent,
  order: 100,
});
```

### ctx.ui.settings.define(options)

Register a plugin settings panel, displayed in EchoMusic's plugin manager.

| Parameter | Type | Required | Description |
|-----------|------|:--:|------|
| `options.title` | `string` | ✅ | Settings panel title |
| `options.component` | `Component` | ✅ | Vue component |

```js
ctx.ui.settings.define({
  title: "My Plugin Settings",
  component: SettingsPanel,
});
```

### ctx.ui.addSongContextMenuItem(options)

Add custom options to the song right-click context menu.

| Parameter | Type | Required | Description |
|-----------|------|:--:|------|
| `options.id` | `string` | ✅ | Unique menu item ID |
| `options.label` | `string` | ✅ | Menu item display text |
| `options.onSelect` | `(song) => void` | ✅ | Click callback, `song` is the current song object |

```js
ctx.ui.addSongContextMenuItem({
  id: "copy-song-id",
  label: "Copy Song ID",
  async onSelect(song) {
    await navigator.clipboard.writeText(song.id || "");
    ctx.toast.success("Song ID copied");
  },
});
```

### ctx.ui.mount(el, component)

Mount a Vue component onto a specified DOM element.

| Parameter | Type | Description |
|-----------|------|------|
| `el` | `string \| HTMLElement` | CSS selector or DOM element |
| `component` | `Component` | Vue component |

> Components mounted via `mount` are automatically cleaned up when the plugin is disabled/uninstalled.

### ctx.ui.teleport(selector, component)

Teleport a Vue component to a specified CSS selector location (uses Vue's `<Teleport>`).

| Parameter | Type | Description |
|-----------|------|------|
| `selector` | `string` | CSS selector |
| `component` | `Component` | Vue component |

---

## Toast Notifications

| API | Description |
|-----|------|
| `ctx.toast.success(msg)` | Show green success toast |
| `ctx.toast.info(msg)` | Show blue info toast |
| `ctx.toast.error(msg)` | Show red error toast |

```js
ctx.toast.success("Operation successful");
ctx.toast.info("Processing...");
ctx.toast.error("An error occurred, please try again");
```

---

## ctx.dispose(fn)

Register a cleanup function. Called automatically when the plugin is disabled or uninstalled.

| Parameter | Type | Description |
|-----------|------|------|
| `fn` | `() => void` | Cleanup callback |

```js
// Register cleanup for self-managed side effects
let timer = setInterval(() => { /* ... */ }, 1000);

ctx.dispose(() => {
  clearInterval(timer);
  console.log("Timer cleared");
});
```

> EchoMusic automatically cleans up resources registered via host APIs (pages, settings, menus, event listeners, mounted components, etc.). Only use `ctx.dispose()` for **direct DOM modifications** or **side effects the host can't track**.

---

## Local HTTP Server

> Requires capability: `webServer: true`

Create a local HTTP server accessible by other software on the same machine (Wallpaper Engine, OBS, local scripts, etc.) to read EchoMusic state, lyrics, or visualizer pages.

| API | Description |
|-----|------|
| `ctx.webServer.listen(handler, opts?)` | Start HTTP server on `127.0.0.1`, returns port number |
| `ctx.webServer.status()` | Get current server status |
| `ctx.webServer.close()` | Stop the server |
| `ctx.webServer.onRequest(handler)` | Register request handler |

```js
ctx.webServer.listen(async (req) => {
  return { status: 200, body: JSON.stringify({ playing: ctx.player.currentTrack }) }
}).then(port => console.log('Server on port', port));
```

> The server automatically releases its port when the plugin is disabled, uninstalled, or EchoMusic exits.

---

## Desktop Lyrics

> The desktop lyric window is an independent renderer process. Requires `runtime.desktopLyric: true` in the manifest.

| API | Description |
|-----|------|
| `ctx.desktopLyric` | Desktop lyric window context, used to detect the current runtime environment |
| `ctx.lyricEffects.register({ scope: "desktop", ... })` | Register visual effects for the desktop lyric window (requires `lyricEffects: true`) |

```js
// Detect desktop lyric environment
if (ctx.desktopLyric) {
  ctx.lyricEffects.register({
    id: "vertical-desktop",
    title: "Vertical Desktop Lyrics",
    scope: "desktop",
    layer: "style",
    css: `.desktop-lyric { writing-mode: vertical-rl; }`,
  });
}
```

---

## SQLite Database

> Requires capability: `sqlite: true`

Plugin-private SQLite database, isolated by plugin ID and managed by the host.

| API | Description |
|-----|------|
| `ctx.sqlite.open({name?, migrations?})` | Open/create a database, defaults to `main` |
| `ctx.sqlite.listDatabases()` | List all databases |
| `ctx.sqlite.deleteDatabase(name?)` | Delete a named database |
| `db.exec(sql)` | Execute SQL |
| `db.run(sql, params?)` | Execute INSERT/UPDATE/DELETE |
| `db.get(sql, params?)` | Query a single row |
| `db.all(sql, params?)` | Query multiple rows |
| `db.transaction(fn)` | Execute within a transaction |
| `db.close()` | Close the connection |

```js
const db = await ctx.sqlite.open({ name: "library" });
await db.run("CREATE TABLE IF NOT EXISTS songs (id TEXT PRIMARY KEY, title TEXT)");
await db.run("INSERT OR REPLACE INTO songs (id, title) VALUES (?, ?)", ["1", "My Song"]);
const row = await db.get("SELECT * FROM songs WHERE id = ?", ["1"]);
console.log(row.row?.title); // "My Song"
```

> Supports BLOB parameters: `{ type: "hex", data }` or `{ type: "base64", data }` for writes. Queries return BLOBs as hex strings.

---

## Next Steps

| Document | Content |
|----------|------|
| [UI Extension Guide →](./ui-extension) | Deep dive into UI customization |
| [Player & Audio →](./player-audio) | `ctx.player`, audio spectrum, lyrics system |
| [Filesystem & Storage →](./filesystem-storage) | Local files, KV storage, event listeners |
