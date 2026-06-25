---
title: UI Extension Guide
outline: [2, 4]
---

# 🎨 UI Extension Guide

Plugins can extend EchoMusic's user interface in multiple ways. This document covers each UI extension mechanism in depth.

## Registering Pages

Use `ctx.ui.addPage()` to add a standalone page to the sidebar.

### Basic Usage

```js
ctx.ui.addPage({
  id: "my-custom-page",
  title: "My Custom Page",
  icon: "🎵",
  component: {
    setup() {
      const { ref } = ctx.vue;
      const count = ref(0);

      return () =>
        ctx.vue.h("div", { class: "page-container" }, [
          ctx.vue.h("h1", "My Page"),
          ctx.vue.h("p", `Click count: ${count.value}`),
          ctx.vue.h("button", {
            onClick: () => count.value++,
          }, "Click +1"),
        ]);
    },
  },
  order: 100,
});
```

### Full Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--:|------|
| `id` | `string` | ✅ | Unique page identifier, used as the route path |
| `title` | `string` | ✅ | Sidebar display text |
| `icon` | `string` | ❌ | Sidebar icon, supports Emoji |
| `component` | `Component` | ✅ | Page content component |
| `order` | `number` | ❌ | Sort weight, smaller values appear first |

### Using Vue SFC Components

If your plugin includes pre-compiled Vue SFCs (bundled via Vite), you can use them directly:

```js
import MyPage from './components/MyPage.vue';

ctx.ui.addPage({
  id: "my-page",
  title: "My Page",
  icon: "🎵",
  component: MyPage,
});
```

### Page Lifecycle

- **Registration timing**: Register in `activate()`
- **Auto cleanup**: Pages are automatically removed from the sidebar and routes when the plugin is disabled/uninstalled
- **Hot reload**: Re-enabling the plugin re-registers the page

---

## Settings Panels

Use `ctx.ui.settings.define()` to add a settings section to the plugin manager.

### Basic Example

```js
const SettingsPanel = ctx.vue.defineComponent({
  setup() {
    const { ref } = ctx.vue;
    const autoScroll = ref(true);
    const fontSize = ref(14);

    // Restore saved settings
    ctx.storage.get("settings").then((saved) => {
      if (saved) {
        autoScroll.value = saved.autoScroll !== false;
        fontSize.value = saved.fontSize || 14;
      }
    });

    const save = async () => {
      await ctx.storage.set("settings", {
        autoScroll: autoScroll.value,
        fontSize: fontSize.value,
      });
      ctx.toast.info("Settings saved");
    };

    const { h, defineAsyncComponent } = ctx.vue;
    const Button = defineAsyncComponent(ctx.ui.components.Button);
    const Switch = defineAsyncComponent(ctx.ui.components.Switch);
    const Input = defineAsyncComponent(ctx.ui.components.Input);

    return () =>
      h("div", { style: "display: grid; gap: 16px; padding: 8px 0;" }, [
        h("label", { style: "display: flex; justify-content: space-between; align-items: center;" }, [
          h("span", "Auto-scroll lyrics"),
          h(Switch, {
            modelValue: autoScroll.value,
            "onUpdate:modelValue": (v) => { autoScroll.value = Boolean(v); },
          }),
        ]),
        h("label", { style: "display: flex; justify-content: space-between; align-items: center;" }, [
          h("span", "Font size"),
          h(Input, {
            modelValue: String(fontSize.value),
            type: "number",
            "onUpdate:modelValue": (v) => { fontSize.value = Number(v); },
            style: "width: 80px;",
          }),
        ]),
        h(Button, { size: "xs", onClick: save }, { default: () => "Save Settings" }),
      ]);
  },
});

ctx.ui.settings.define({
  title: "Lyrics Settings",
  component: SettingsPanel,
});
```

### Parameter Reference

| Parameter | Type | Required | Description |
|-----------|------|:--:|------|
| `title` | `string` | ✅ | Settings section title |
| `component` | `Component` | ✅ | Settings panel component |

### Best Practices

- Use `ctx.storage` to persist user settings
- Load existing settings asynchronously in `setup()` to avoid blocking the UI
- Provide a "Save" button for explicit user confirmation
- Avoid overly complex logic in settings panels — register a standalone page for complex UIs

---

## Song Context Menu

Use `ctx.ui.addSongContextMenuItem()` to add custom options to the song list right-click menu.

```js
ctx.ui.addSongContextMenuItem({
  id: "add-to-collection",
  label: "Add to My Collection",
  async onSelect(song) {
    try {
      // song object contains complete song info
      const { id, title, artist, album } = song;

      // Custom handling
      await myCollectionService.addSong(id);

      ctx.toast.success(`Added "${title}" to collection`);
    } catch (err) {
      ctx.toast.error("Failed: " + err.message);
    }
  },
});
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--:|------|
| `id` | `string` | ✅ | Unique menu item ID |
| `label` | `string` | ✅ | Menu item display text |
| `onSelect` | `(song) => void` | ✅ | Click callback, parameter is the right-clicked song object |

### Notes

- `onSelect` can be an `async` function
- Multiple plugins can register different right-click menu items; EchoMusic auto-merges them
- If `id` conflicts with another plugin, **the later-registered one overrides the earlier**

---

## Component Mounting

Use `ctx.ui.mount()` to mount a Vue component at a specific DOM location on the page.

```js
export function activate(ctx) {
  const { h } = ctx.vue;

  const Widget = ctx.vue.defineComponent({
    setup() {
      return () =>
        h("div", { class: "my-widget" }, [
          h("span", "Hello from plugin!"),
        ]);
    },
  });

  // Mount to the player footer area
  ctx.ui.mount("#player-footer", Widget);
}
```

### Parameters

| Parameter | Type | Description |
|-----------|------|------|
| `el` | `string \| HTMLElement` | Target DOM location (CSS selector or DOM element) |
| `component` | `Component` | Vue component to mount |

---

## Component Teleport

Use `ctx.ui.teleport()` to teleport component content anywhere on the page (backed by Vue's `<Teleport>`).

```js
ctx.ui.teleport("#app-header", MyHeaderWidget);
```

| Parameter | Type | Description |
|-----------|------|------|
| `selector` | `string` | CSS selector, Teleport target |
| `component` | `Component` | Vue component to teleport |

**Difference from `mount`:**
- `mount` directly mounts the component onto the target DOM (target element is replaced)
- `teleport` uses Vue Teleport; the component's DOM is moved inside the target, while the component's reactivity system remains within the original plugin context

---

## Custom Styles

In addition to injecting CSS files via the `style` field, you can dynamically add styles in code:

```js
// Inject custom CSS
const styleEl = document.createElement("style");
styleEl.textContent = `
  .my-widget {
    padding: 8px;
    border-radius: 8px;
    background: var(--color-bg-secondary);
  }
`;
document.head.appendChild(styleEl);

// Register cleanup
ctx.dispose(() => {
  styleEl.remove();
});
```

> Prefer using the manifest `style` field. Only inject styles in code when dynamic styling is required.

---

## Next Steps

| Document | Content |
|----------|------|
| [Player & Audio →](./player-audio) | `ctx.player`, audio spectrum, lyrics system |
| [Context API Reference →](./context-api) | Complete ctx API listing |
| [Publishing & Distribution →](./publishing) | Publish plugins to the online registry |
