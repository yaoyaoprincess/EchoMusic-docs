---
title: UI Extension Guide
outline: [2, 4]
---

# 🎨 UI Extension Guide

Plugins can extend EchoMusic's user interface in several ways. This document covers each UI extension mechanism in depth.

## Registering Pages

Use `ctx.ui.addPage()` to register a standalone page and optionally attach it to the sidebar.

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
|------|------|:--:|------|
| `id` | `string` | ✅ | Unique page id, used as the route path |
| `title` | `string` | ✅ | Sidebar display text |
| `icon` | `string \| IconifyIcon` | ❌ | Icon: Iconify icon name or icon object |
| `component` | `Component` | ✅ | Page content component |
| `order` | `number` | ❌ | Sort weight; lower comes first (default 1000) |
| `sidebar` | `boolean \| SidebarOptions` | ❌ | Also register a sidebar entry; `true` reuses the page id/title/icon and puts it in the `plugins` section |

### Sidebar Options

Pass an object as `sidebar` to control the sidebar entry in detail:

| Parameter | Type | Description |
|------|------|------|
| `id` | `string` | Sidebar entry id, defaults to the page id |
| `title` | `string` | Entry text, defaults to the page title |
| `icon` | `string \| IconifyIcon` | Entry icon, defaults to the page icon |
| `section` | `string` | Section id, defaults to `"plugins"` (built-in sections: `discover` / `library` / `plugins`; custom sections are allowed) |
| `sectionTitle` | `string` | Display name of a custom section |
| `sectionOrder` | `number` | Sort order of a custom section |
| `collapsible` | `boolean` | Whether the section is collapsible |
| `order` | `number` | Sort weight within the section, defaults to the page's `order` |
| `before` / `after` | `string` | Insert before/after the entry with the given id |
| `visible` | `boolean \| () => boolean` | Whether to show (function form is reactive) |
| `disabled` | `boolean \| () => boolean` | Whether to gray out |

```js
ctx.ui.addPage({
  id: "lyric-tools",
  title: "Lyric Toolbox",
  icon: "🛠️",
  component: LyricTools,
  sidebar: {
    section: "library",
    order: 50,
    visible: () => ctx.settings.localMusicEnabled !== false,
  },
});
```

### Page Lifecycle

- **When to register**: ideally inside `activate()`
- **Auto cleanup**: the page and its sidebar entry are removed automatically when the plugin is disabled/uninstalled
- **Re-registration**: registering the same `id` again replaces the old entry (upsert)

---

## Sidebar Shortcut Cards (ui.sidebar.shortcuts)

Shortcut cards appear in the sidebar "plugins" card area — good for feature entries or status summaries.

```js
ctx.ui.sidebar.shortcuts.register({
  id: "quick-import",
  title: "Quick Import",
  icon: "📥",
  // Provide exactly one of pageId or onClick: pageId navigates to a plugin page, onClick runs custom logic
  onClick: () => ctx.toast.info("Import started"),
});
```

| Parameter | Type | Required | Description |
|------|------|:--:|------|
| `id` | `string` | ✅ | Unique card id |
| `title` | `string` | ✅ | Card title |
| `icon` | `string \| IconifyIcon` | ❌ | Card icon |
| `pageId` | `string` | ➖ | Page id to navigate to on click (one of `pageId`/`onClick` is required) |
| `onClick` | `() => void \| Promise<void>` | ➖ | Click handler (one of `pageId`/`onClick` is required) |
| `order` | `number` | ❌ | Sort weight (default 1000) |
| `visible` | `boolean \| () => boolean` | ❌ | Whether to show |
| `disabled` | `boolean \| () => boolean` | ❌ | Whether to gray out |

---

## Sidebar Entries (sidebar.addItem)

Besides `addPage({ sidebar })`, `ctx.ui.sidebar.addItem()` registers a sidebar entry that can navigate to any route without a plugin page.

| Parameter | Type | Required | Description |
|------|------|:--:|------|
| `id` | `string` | ➖ | Entry id, defaults to `pageId` |
| `title` | `string` | ✅ | Display text |
| `icon` | `string \| IconifyIcon` | ❌ | Icon |
| `section` | `string` | ❌ | Section, defaults to `"plugins"` |
| `sectionTitle` / `sectionOrder` / `collapsible` | — | ❌ | Section settings, same as addPage |
| `pageId` | `string` | ❌ | Plugin page id |
| `path` | `string` | ❌ | Host internal route path (e.g. `"/playlist"`) |
| `onClick` | `() => void \| Promise<void>` | ❌ | Click handler |
| `order` / `before` / `after` | — | ❌ | Ordering |
| `visible` / `disabled` | `boolean \| () => boolean` | ❌ | Visibility and disabled state |

---

## Settings Panel

Use `ctx.ui.settings.define()` to add a settings section to the plugin management page.

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
        h(Button, { size: "xs", onClick: save }, { default: () => "Save" }),
      ]);
  },
});

ctx.ui.settings.define({
  title: "Lyrics",
  component: SettingsPanel,
});
```

### Parameters

| Parameter | Type | Required | Description |
|------|------|:--:|------|
| `id` | `string` | ❌ | Settings section id, defaults to `"default"` |
| `title` | `string` | ❌ | Section title |
| `description` | `string` | ❌ | Section description |
| `component` | `Component` | ✅ | Settings panel component |

> ⚠️ The legacy declarative `sections` / `fields` / `onChange` settings have been removed and the host throws on them; always use `component`.

### Best Practices

- Persist user settings with `ctx.storage.set/get`
- Load existing settings asynchronously in `setup()` to avoid blocking the UI
- Provide a "Save" button so changes are submitted explicitly
- Avoid overly complex logic in settings panels — register a standalone page for complex UIs

---

## Song Context Menu

Use `ctx.ui.addSongContextMenuItem()` to add custom entries to the song list's context menu.

```js
ctx.ui.addSongContextMenuItem({
  id: "add-to-collection",
  label: "Add to my collection",
  order: 10,
  async onSelect(song) {
    try {
      // song is the full song object
      const { id, title, artist, album } = song;

      // Custom handling
      await myCollectionService.addSong(id);

      ctx.toast.success(`Added "${title}" to collection`);
    } catch (err) {
      ctx.toast.danger("Failed: " + err.message);
    }
  },
});
```

### Parameters

| Parameter | Type | Required | Description |
|------|------|:--:|------|
| `id` | `string` | ✅ | Unique menu item id |
| `label` | `string` | ✅ | Display text |
| `onSelect` | `(song) => void \| Promise<void>` | ✅ | Click handler; the argument is the song object under the cursor |
| `order` | `number` | ❌ | Sort weight (default 1000); ties are broken by label |
| `danger` | `boolean` | ❌ | Render in danger style (red) |
| `visible` | `(song) => boolean` | ❌ | Whether to show the item (per song; throwing hides the item) |
| `enabled` | `(song) => boolean` | ❌ | Whether the item is enabled (per song; throwing disables it) |

### Notes

- `onSelect` may be an `async` function; thrown errors are captured and reported by the host without affecting other menu items
- Multiple plugins can register menu items; EchoMusic merges them automatically
- The internal key of a menu item is `pluginId:itemId`, so **the same `id` across different plugins never overwrites each other**; only re-registering the same `id` within the same plugin replaces the old entry

---

## Player Bar Buttons (ui.playerbar)

`ctx.ui.playerbar.register()` registers an action button in the bottom player bar.

```js
let unread = 0;

ctx.ui.playerbar.register({
  id: "inbox",
  title: "Inbox",
  icon: "mdi:email-outline",
  tooltip: "View messages",
  badge: () => (unread > 0 ? unread : null),
  badgeTitle: "Unread messages",
  defaultPlacement: "right",
  onClick: () => {
    unread = 0;
    ctx.toast.info("All marked as read");
  },
});
```

### Parameters

| Parameter | Type | Required | Description |
|------|------|:--:|------|
| `id` | `string` | ✅ | Unique action id |
| `title` | `string` | ✅ | Action name (also the fallback tooltip) |
| `icon` | `string \| IconifyIcon` | ✅ | Icon |
| `onClick` | `() => void \| Promise<void>` | ✅ | Click handler (the button shows a busy state while it runs) |
| `tooltip` | `string` | ❌ | Hover tooltip, defaults to `title` |
| `badge` | `string \| number \| (() => ...)` | ❌ | Badge content; a function computes it dynamically, returning `null`/empty string hides it |
| `badgeTitle` | `string` | ❌ | Accessible label for the badge |
| `badgeDefaultVisible` | `boolean` | ❌ | Whether the badge is visible by default (default `true`) |
| `trigger` | `"click" \| "hover"` | ❌ | Trigger mode, default `"click"` |
| `defaultPlacement` | `"left" \| "center" \| "right" \| "more"` | ❌ | Default area, default `"more"` (the overflow menu) |
| `order` | `number` | ❌ | Sort weight (default 1000) |
| `visible` / `disabled` | `boolean \| () => boolean` | ❌ | Visibility and disabled state (function forms supported) |

Users can rearrange buttons between the toolbar and the overflow menu via the host's pin management; `defaultPlacement` only sets the initial position on first registration.

---

## Title Bar Buttons (ui.titlebar)

`ctx.ui.titlebar.register()` registers an action in the main window's title bar (toolbar or "more" menu).

```js
ctx.ui.titlebar.register({
  id: "quick-tools",
  title: "Quick Tools",
  icon: "mdi:magic-staff",
  tooltip: "Open quick tools",
  defaultPlacement: "toolbar",
  onClick: () => ctx.toast.info("Quick tools"),
});
```

### Parameters

| Parameter | Type | Required | Description |
|------|------|:--:|------|
| `id` | `string` | ✅ | Unique action id |
| `title` | `string` | ✅ | Action name |
| `icon` | `string \| IconifyIcon` | ✅ | Icon |
| `onClick` | `() => void \| Promise<void>` | ✅ | Click handler (automatic busy state) |
| `tooltip` | `string` | ❌ | Hover tooltip, defaults to `title` |
| `defaultPlacement` | `"toolbar" \| "more"` | ❌ | Default area: toolbar button or "more" menu, default `"more"` |
| `order` | `number` | ❌ | Sort weight (default 1000) |
| `visible` / `disabled` | `boolean \| () => boolean` | ❌ | Visibility and disabled state (function forms supported) |

---

## Lyrics Page Skins (ui.lyricsPage)

A plugin can register a custom lyrics page skin that replaces the host lyrics page's rendering component.

> Requires capability: `lyricsPage: true`

```js
ctx.ui.lyricsPage.register({
  id: "my-skin",
  title: "My Skin",
  preview: "preview.png",              // skin panel preview image (plugin-relative path)
  component: MyLyricPage,              // Vue component
  titlebar: "host",                    // header: host = provided by host / none = self-drawn
  tools: "host",                       // right-side lyric tool buttons: host / none
  settings: {                          // optional: skin settings (rendered in the host settings drawer)
    defaults: { fontSize: 20 },
    // component: MySkinSettings,
    // validate: (values) => true,
  },
});

// Inside the lyrics page / settings component's setup():
const page = ctx.ui.lyricsPage.usePage();   // lyrics page context (playback / lyric state)
const skin = ctx.ui.lyricsPage.useSkin();   // current skin settings handle (persisted per skin)
ctx.ui.lyricsPage.openSkins();              // open the host skin panel (for fully self-drawn UIs)
```

Registration options: `id` and `component` are required; `title?`, `preview?`, `titlebar?` (default `"host"`), `tools?` (default `"host"`) and `settings?` (`defaults` required; `component?` / `validate?` optional). When a skin fails, the host falls back to a built-in skin; see the official [theme example](https://github.com/hoowhoami/EchoMusicPlugins/tree/main/app-theme-example) for the full API and context.

---

## Component Mounting (mount)

Use `ctx.ui.mount()` to mount a Vue component at a specific DOM location.

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

  // Mount into the player footer area
  ctx.ui.mount("#player-footer", Widget, {
    position: "append",
    className: "my-plugin-widget",
    id: "footer-widget",
  });
}
```

### Parameters

| Parameter | Type | Description |
|------|------|------|
| `target` | `string \| Element` | Target DOM location (CSS selector or DOM element) |
| `component` | `Component` | The Vue component to mount |
| `options.props` | `Record<string, unknown>` | Props passed to the component |
| `options.position` | `"append" \| "prepend" \| "before" \| "after" \| "replace"` | Insertion mode, default `"append"` |
| `options.className` | `string` | Extra class added to the mount container |
| `options.id` | `string` | Mount container marker (written to `data-echo-plugin-mount`) for later lookup |

Mounting returns a dispose function and registers it automatically: the component unmounts and the container is removed when the plugin is disabled/uninstalled. Mounted components share Pinia and Router with the host, so host state and the `<Icon>` component work out of the box.

---

## Floating Overlays (teleport)

Use `ctx.ui.teleport()` to mount a component under `document.body` — ideal for notifications, floating balls, and other global overlays that must not be clipped by host layout containers.

```js
const dispose = ctx.ui.teleport(
  FloatingBall,                       // the first argument is the component
  { props: { size: 48 }, className: "my-floating-ball" },
);
```

| Parameter | Type | Description |
|------|------|------|
| `component` | `Component` | The Vue component to mount |
| `options.props` | `Record<string, unknown>` | Props passed to the component |
| `options.className` | `string` | Extra class (the container also gets `echo-plugin-teleport`) |
| `options.id` | `string` | Mount container marker (optional) |

**Differences from `mount`:**
- `mount` requires a target element and supports five insertion positions; it throws when the target does not exist
- `teleport` always mounts to the end of `document.body`, needs no target element, and suits global overlays

---

## Preset Components (ui.components)

`ctx.ui.components` automatically exposes every reusable host component with no manual registration: new host components become available immediately. It covers three directories:

| Directory | Contents |
|------|------|
| `ui/` | Base controls: `Button`, `Switch`, `Input`, `Select`, `Slider`, etc. |
| `music/` | Music business components: `SongList`, `PlaylistCard`, `BarrageControls`, etc. |
| `player/` | Player popover components |

There are also three lyrics-page components: `LyricScroller` (scrolling lyric list), `LyricPlayerControls` (lyrics page control bar), and `BarrageControls` (barrage controls).

Each entry is a `() => Promise<Component>` async loader; consume it with `defineAsyncComponent`:

```js
const { h, defineAsyncComponent } = ctx.vue;
const Button = defineAsyncComponent(ctx.ui.components.Button);
const SongList = defineAsyncComponent(ctx.ui.components.SongList);
const LyricScroller = defineAsyncComponent(ctx.ui.components.LyricScroller);
```

> Component prop contracts follow the host sources (`src/renderer/components/`) and may evolve between versions; lock the tested range with `requires.echoMusicVersion`.

---

## CSS Injection

Use `ctx.css.inject()` to inject CSS styles dynamically.

```js
ctx.css.inject(`
  .my-plugin-panel {
    border-radius: 12px;
    background: var(--color-bg-secondary);
    padding: 16px;
  }
`);
```

- Injected CSS is **removed automatically** when the plugin is disabled/uninstalled
- Pass `{ id: "unique-id" }` to deduplicate by id (re-injecting the same id replaces the old styles)
- Best for small dynamic styles; prefer the manifest `style` field for large stylesheets

---

## DOM Queries and Observation

`ctx.dom` provides managed DOM queries and appearance observation.

```js
// Single / all queries
const container = ctx.dom.query(".playlist-container");
const items = ctx.dom.queryAll(".song-item");

// Observe element appearance
const stop = ctx.dom.observe(
  ".playlist-container",
  (element) => {
    console.log("playlist rendered", element);
    // Optional: return a cleanup function, called when the element is removed or observation stops
    return () => console.log("playlist unmounted");
  },
  { root: document.querySelector("#app"), once: false },
);
```

| API | Description |
|-----|------|
| `query(selector)` | `querySelector` wrapper; returns `null` when nothing matches |
| `queryAll(selector)` | `querySelectorAll` wrapper; returns an array |
| `observe(selector, handler, options?)` | Observe matching elements appearing; returns a stop function |

`observe` options:

| Option | Type | Description |
|------|------|------|
| `root` | `Element \| Document` | Observation root, default `document.body`; when an element is given and it leaves the document, everything is cleaned up automatically |
| `once` | `boolean` | Stop automatically after the first match |

If `handler` returns a function it becomes that element's cleanup callback: it runs when the element is removed, the root leaves the document, or observation stops — perfect for unbinding events or disconnecting IntersectionObservers. Observation is released automatically when the plugin is disabled/uninstalled.

---

## Scroll Control (scroll)

`ctx.scroll` queries, scrolls, and observes the host's scroll containers. Host content scroll containers carry a `data-echo-scroll-container` marker (`ctx.scroll.selector` holds that selector).

```js
// Query containers; visible: false includes invisible (cached/covered) containers
const containers = ctx.scroll.queryContainers({ role: "main", visible: true });

// Scroll: target accepts "top" / "bottom" / a pixel value
ctx.scroll.scrollTo(container, "bottom", { behavior: "smooth" });

// Shortcuts (default to the current visible container)
ctx.scroll.scrollToTop();
ctx.scroll.scrollToBottom();

// Observe containers appearing; handler may return a cleanup function
const stop = ctx.scroll.observeContainers((element, state) => {
  console.log("container appeared", state);   // { scrollTop, scrollHeight, clientHeight, distanceToBottom, canScroll, atTop, atBottom }
  const onScroll = () => console.log(element.scrollTop);
  element.addEventListener("scroll", onScroll);
  return () => element.removeEventListener("scroll", onScroll);
});
```

| API | Description |
|-----|------|
| `selector` | The scroll container CSS selector constant |
| `queryContainers({ role?, visible? })` | Query containers; `role` filters by `data-echo-scroll-role`, `visible` defaults to visible containers only |
| `getCurrentContainer()` | The first visible container |
| `getState(el?)` | Read a scroll state snapshot |
| `scrollTo(el, target, options?)` | Scroll to top/bottom/a pixel position; smooth by default |
| `scrollToTop(el?)` / `scrollToBottom(el?)` | Shortcuts |
| `observeContainers(handler)` | Observe containers appearing; each container is reported once |

Great for "load more when scrolled to the bottom" and "back to top" interactions.

---

## Next Steps

| Document | Content |
|------|------|
| [Player & Audio Engine →](./player-audio) | `ctx.player`, audio spectrum, lyrics system |
| [API Overview →](./context-api) | Full ctx API list |
| [Publishing & Distribution →](./publishing) | Publish plugins to online registries |
