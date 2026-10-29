---
title: 歌词页换肤
---

# 🎨 歌词页换肤

`ctx.ui.lyricsPage` 允许插件**替换整个页面歌词**（不只是叠加动效），并作为"皮肤"接入宿主的换肤面板，与内置皮肤（封面 / 写真 / 歌词 / Apple Music）共用同一套选择与设置机制。需要 capability：`lyricsPage: true`。

## 注册歌词页

```js
ctx.ui.lyricsPage.register({
  id: "my-lyric-page",
  title: "我的歌词页",
  preview: "https://example.com/preview.png",  // 换肤面板预览图，缺省用占位卡片
  component: MyLyricPage,                       // Vue 组件（占满整个歌词页）
  titlebar: "host",                             // 'host' 用宿主顶栏 | 'none' 插件自绘
  tools: "host",                                // 右侧歌词工具按钮（来源/翻译/音译/复制/偏移）
  settings: {                                   // 可选：皮肤设置
    defaults: { fontSize: 24, glow: true },
    component: SkinSettingsPanel,               // 渲染在宿主设置抽屉内
    validate(values) {
      return values.fontSize >= 12 || { errors: ["字号至少 12"] };
    },
  },
});
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | `string` | 皮肤唯一 ID（插件内） |
| `title` | `string` | 换肤面板显示名称（缺省用插件名） |
| `preview` | `string` | 面板预览图 |
| `component` | `Component` | 歌词页组件，接管整个歌词页 |
| `titlebar` | `'host' \| 'none'` | 顶部栏：宿主提供的歌词 overlay 头部（非主窗口导航栏） |
| `tools` | `'host' \| 'none'` | 右侧工具按钮组；设为 `'none'` 时插件自行提供 |
| `settings.defaults` | `object` | 皮肤配置默认值 |
| `settings.component` | `Component` | 设置面板组件（渲染在宿主设置抽屉内） |
| `settings.validate(values)` | `function` | 配置校验，通过返回 `true`，失败返回 `{errors: string[]}` |

## usePage() — 页面上下文

在歌词页组件的 `setup()` 中调用（组件外调用抛错），返回宿主注入的页面上下文（当前播放、歌词数据等，随宿主版本演进）：

```js
export default defineComponent({
  setup() {
    const page = ctx.ui.lyricsPage.usePage();
    // 用 page 提供的播放/歌词数据渲染自定义歌词页
  },
});
```

## useSkin() — 皮肤配置

在歌词页组件**或设置面板组件**的 `setup()` 中调用，返回当前皮肤的配置句柄。宿主按皮肤隔离配置，`patch` 先经过皮肤的 `validate` 再持久化：

```js
const skin = ctx.ui.lyricsPage.useSkin();
skin.values;             // 当前配置（合并 defaults 后）
skin.patch({ fontSize: 28 }); // 更新配置（经 validate 校验后持久化）
```

## openSkins() — 打开换肤面板

完全自定义（`titlebar: 'none'`）的歌词页可在自己的 UI 中调用，打开宿主换肤面板：

```js
ctx.ui.lyricsPage.openSkins();
```

## 注意事项

- 换肤面板里的皮肤卡片自带预览；渲染失败时宿主自动回退到封面皮肤，面板中可重试；
- 皮肤配置按 `pluginId + id` 隔离持久化；卸载插件时宿主自动清理其孤儿配置；
- 若只需在现有歌词上叠加动效，用 [`ctx.lyricEffects`](./player-audio#歌词视觉效果)（`lyricEffects` 能力）更轻量；`lyricsPage` 适合整体替换布局与渲染方式；
- 修改中文页面后需同步英文镜像。

## 下一步

| 文档 | 内容 |
|------|------|
| [歌词视觉效果 →](./player-audio#歌词视觉效果) | 轻量级歌词动效叠加 |
| [UI 扩展 →](./ui-extension) | 其他 UI 贡献点 |
| [Context API →](./context-api) | ctx 完整 API 速查 |
