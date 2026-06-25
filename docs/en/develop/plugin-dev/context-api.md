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

## Next Steps

| Document | Content |
|----------|------|
| [UI Extension Guide →](./ui-extension) | Deep dive into UI customization |
| [Player & Audio →](./player-audio) | `ctx.player`, audio spectrum, lyrics system |
| [Filesystem & Storage →](./filesystem-storage) | Local files, KV storage, event listeners |
