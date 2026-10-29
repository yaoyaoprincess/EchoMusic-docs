---
title: Lyrics Page Skin
---

# 🎨 Lyrics Page Skin

`ctx.ui.lyricsPage` lets plugins **replace the entire page lyrics** (not just overlay effects) and plug into the host's skin panel as a "skin", sharing the same selection and settings mechanism as the built-in skins (Cover / Portrait / Lyrics / Apple Music). Requires capability: `lyricsPage: true`.

## Registering a Lyrics Page

```js
ctx.ui.lyricsPage.register({
  id: "my-lyric-page",
  title: "My Lyric Page",
  preview: "https://example.com/preview.png",  // skin panel preview; a placeholder card is used when omitted
  component: MyLyricPage,                       // Vue component (fills the whole lyrics page)
  titlebar: "host",                             // 'host' uses the host header | 'none' draws your own
  tools: "host",                                // right-side lyric tool buttons (source/translate/romanize/copy/offset)
  settings: {                                   // optional: skin settings
    defaults: { fontSize: 24, glow: true },
    component: SkinSettingsPanel,               // rendered inside the host settings drawer
    validate(values) {
      return values.fontSize >= 12 || { errors: ["Font size must be at least 12"] };
    },
  },
});
```

| Parameter | Type | Description |
|------|------|------|
| `id` | `string` | Skin ID (unique within the plugin) |
| `title` | `string` | Name shown in the skin panel (defaults to the plugin name) |
| `preview` | `string` | Panel preview image |
| `component` | `Component` | The lyrics page component, taking over the entire page |
| `titlebar` | `'host' \| 'none'` | Header: the host-provided lyric overlay header (not the main window nav bar) |
| `tools` | `'host' \| 'none'` | Right-side tool buttons; with `'none'` the plugin provides its own |
| `settings.defaults` | `object` | Default skin configuration |
| `settings.component` | `Component` | Settings panel component (rendered inside the host settings drawer) |
| `settings.validate(values)` | `function` | Config validation — return `true` to pass or `{errors: string[]}` |

## usePage() — Page Context

Call inside the lyrics page component's `setup()` (throws outside a component); returns the host-injected page context (current playback, lyrics data, etc. — evolves with host versions):

```js
export default defineComponent({
  setup() {
    const page = ctx.ui.lyricsPage.usePage();
    // render your custom lyrics page from the data page provides
  },
});
```

## useSkin() — Skin Configuration

Call inside the lyrics page component **or the settings panel component**; returns the current skin's configuration handle. The host isolates config per skin — patches pass through the skin's `validate` before persisting:

```js
const skin = ctx.ui.lyricsPage.useSkin();
skin.values;             // current config (merged with defaults)
skin.patch({ fontSize: 28 }); // update config (validated then persisted)
```

## openSkins() — Open the Skin Panel

Fully custom (`titlebar: 'none'`) lyric pages can call this from their own UI to open the host skin panel:

```js
ctx.ui.lyricsPage.openSkins();
```

## Notes

- Skin cards in the panel include previews; when a page fails to render, the host falls back to the cover skin and the panel offers a retry;
- Skin config is persisted isolated by `pluginId + id`; uninstalling a plugin automatically cleans up its orphaned configs;
- If you only need to overlay effects on the existing lyrics, [`ctx.lyricEffects`](./player-audio#lyric-visual-effects) (the `lyricEffects` capability) is much lighter — `lyricsPage` is for replacing the layout and rendering entirely;
- After editing this Chinese page, sync the English mirror.

## Next Steps

| Document | Content |
|------|------|
| [Lyric Visual Effects →](./player-audio#lyric-visual-effects) | Lightweight lyric effect overlays |
| [UI Extension →](./ui-extension) | Other UI contribution points |
| [Context API →](./context-api) | Full ctx API quick reference |
