---
title: UI 扩展指南
outline: [2, 4]
---

# 🎨 UI 扩展指南

插件可以通过多种方式扩展 EchoMusic 的用户界面。本文档深入介绍每种 UI 扩展机制。

## 注册独立页面

使用 `ctx.ui.addPage()` 注册一个独立页面，并可同时把它挂到侧边栏。

### 基本用法

```js
ctx.ui.addPage({
  id: "my-custom-page",
  title: "我的自定义页面",
  icon: "🎵",
  component: {
    setup() {
      const { ref } = ctx.vue;
      const count = ref(0);

      return () =>
        ctx.vue.h("div", { class: "page-container" }, [
          ctx.vue.h("h1", "我的页面"),
          ctx.vue.h("p", `点击次数：${count.value}`),
          ctx.vue.h("button", {
            onClick: () => count.value++,
          }, "点我 +1"),
        ]);
    },
  },
  order: 100,
});
```

### 完整参数

| 参数 | 类型 | 必选 | 说明 |
|------|------|:--:|------|
| `id` | `string` | ✅ | 页面唯一标识，用作路由路径 |
| `title` | `string` | ✅ | 侧边栏显示文本 |
| `icon` | `string \| IconifyIcon` | ❌ | 图标，支持 Iconify 图标名或图标对象 |
| `component` | `Component` | ✅ | 页面内容组件 |
| `order` | `number` | ❌ | 排序权重，越小越靠前（默认 1000） |
| `sidebar` | `boolean \| SidebarOptions` | ❌ | 同时注册侧边栏入口；`true` 使用页面 id/title/icon，默认归入 `plugins` 分组 |

### sidebar 选项

`sidebar` 传对象时可精细控制侧边栏入口：

| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | `string` | 侧边栏入口 id，默认与页面 id 相同 |
| `title` | `string` | 入口显示文本，默认与页面 title 相同 |
| `icon` | `string \| IconifyIcon` | 入口图标，默认与页面 icon 相同 |
| `section` | `string` | 所属分组 id，默认 `"plugins"`（内置分组：`discover` / `library` / `plugins`，也可自定义） |
| `sectionTitle` | `string` | 自定义分组的显示名称 |
| `sectionOrder` | `number` | 自定义分组的排序 |
| `collapsible` | `boolean` | 分组是否可折叠 |
| `order` | `number` | 组内排序权重，默认取页面的 `order` |
| `before` / `after` | `string` | 按某个入口 id 插到它之前/之后 |
| `visible` | `boolean \| () => boolean` | 是否显示（支持函数做响应式判断） |
| `disabled` | `boolean \| () => boolean` | 是否置灰 |

```js
ctx.ui.addPage({
  id: "lyric-tools",
  title: "歌词工具箱",
  icon: "🛠️",
  component: LyricTools,
  sidebar: {
    section: "library",
    order: 50,
    visible: () => ctx.settings.localMusicEnabled !== false,
  },
});
```

### 页面生命周期

- **注册时机**：建议在 `activate()` 中注册
- **自动清理**：插件禁用/卸载时，页面与侧边栏入口自动移除
- **重复注册**：相同 `id` 再次注册会覆盖旧条目（更新式注册）

---

## 侧边栏快捷卡片（ui.sidebar.shortcuts）

快捷卡片展示在侧边栏「插件」区域的卡片位，适合做功能入口或状态摘要。

```js
ctx.ui.sidebar.shortcuts.register({
  id: "quick-import",
  title: "快速导入",
  icon: "📥",
  // pageId 与 onClick 二选一：pageId 跳转到本插件页面，onClick 执行自定义逻辑
  onClick: () => ctx.toast.info("开始导入"),
});
```

| 参数 | 类型 | 必选 | 说明 |
|------|------|:--:|------|
| `id` | `string` | ✅ | 卡片唯一 id |
| `title` | `string` | ✅ | 卡片标题 |
| `icon` | `string \| IconifyIcon` | ❌ | 卡片图标 |
| `pageId` | `string` | ➖ | 点击后跳转的页面 id（与 `onClick` 必须提供其一） |
| `onClick` | `() => void \| Promise<void>` | ➖ | 点击回调（与 `pageId` 必须提供其一） |
| `order` | `number` | ❌ | 排序权重（默认 1000） |
| `visible` | `boolean \| () => boolean` | ❌ | 是否显示 |
| `disabled` | `boolean \| () => boolean` | ❌ | 是否置灰 |

---

## 侧边栏入口（sidebar.addItem）

除 `addPage({ sidebar })` 外，还可以用 `ctx.ui.sidebar.addItem()` 注册不对应插件的、可跳转任意路由的侧边栏入口。

| 参数 | 类型 | 必选 | 说明 |
|------|------|:--:|------|
| `id` | `string` | ➖ | 入口 id，缺省时取 `pageId` |
| `title` | `string` | ✅ | 显示文本 |
| `icon` | `string \| IconifyIcon` | ❌ | 图标 |
| `section` | `string` | ❌ | 所属分组，默认 `"plugins"` |
| `sectionTitle` / `sectionOrder` / `collapsible` | — | ❌ | 分组设置，同 addPage |
| `pageId` | `string` | ❌ | 插件页面 id |
| `path` | `string` | ❌ | 宿主内部路由路径（如 `"/playlist"`） |
| `onClick` | `() => void \| Promise<void>` | ❌ | 点击回调 |
| `order` / `before` / `after` | — | ❌ | 排序控制 |
| `visible` / `disabled` | `boolean \| () => boolean` | ❌ | 显隐与置灰 |

---

## 设置面板

使用 `ctx.ui.settings.define()` 在插件管理页中添加设置区域。

### 基本示例

```js
const SettingsPanel = ctx.vue.defineComponent({
  setup() {
    const { ref } = ctx.vue;
    const autoScroll = ref(true);
    const fontSize = ref(14);

    // 恢复已保存的设置
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
      ctx.toast.info("设置已保存");
    };

    const { h, defineAsyncComponent } = ctx.vue;
    const Button = defineAsyncComponent(ctx.ui.components.Button);
    const Switch = defineAsyncComponent(ctx.ui.components.Switch);
    const Input = defineAsyncComponent(ctx.ui.components.Input);

    return () =>
      h("div", { style: "display: grid; gap: 16px; padding: 8px 0;" }, [
        h("label", { style: "display: flex; justify-content: space-between; align-items: center;" }, [
          h("span", "自动滚动歌词"),
          h(Switch, {
            modelValue: autoScroll.value,
            "onUpdate:modelValue": (v) => { autoScroll.value = Boolean(v); },
          }),
        ]),
        h("label", { style: "display: flex; justify-content: space-between; align-items: center;" }, [
          h("span", "字号"),
          h(Input, {
            modelValue: String(fontSize.value),
            type: "number",
            "onUpdate:modelValue": (v) => { fontSize.value = Number(v); },
            style: "width: 80px;",
          }),
        ]),
        h(Button, { size: "xs", onClick: save }, { default: () => "保存设置" }),
      ]);
  },
});

ctx.ui.settings.define({
  title: "歌词设置",
  component: SettingsPanel,
});
```

### 参数说明

| 参数 | 类型 | 必选 | 说明 |
|------|------|:--:|------|
| `id` | `string` | ❌ | 设置区块 id，默认 `"default"` |
| `title` | `string` | ❌ | 设置区域标题 |
| `description` | `string` | ❌ | 设置区域描述 |
| `component` | `Component` | ✅ | 设置面板组件 |

> ⚠️ 旧版 `sections` / `fields` / `onChange` 声明式设置已被移除，宿主会直接抛错；请统一改用 `component`。

### 最佳实践

- 使用 `ctx.storage.set/get` 持久化用户的设置
- 在 `setup()` 中异步加载已有设置，避免阻塞 UI
- 提供"保存"按钮，让用户明确提交更改
- 避免在设置面板中放置过于复杂的逻辑——复杂的界面请注册独立页面

---

## 歌曲右键菜单

使用 `ctx.ui.addSongContextMenuItem()` 向歌曲列表的右键菜单添加自定义选项。

```js
ctx.ui.addSongContextMenuItem({
  id: "add-to-collection",
  label: "添加到我的收藏",
  order: 10,
  async onSelect(song) {
    try {
      // song 对象包含歌曲的完整信息
      const { id, title, artist, album } = song;

      // 自定义处理
      await myCollectionService.addSong(id);

      ctx.toast.success(`已添加「${title}」到收藏`);
    } catch (err) {
      ctx.toast.danger("添加失败：" + err.message);
    }
  },
});
```

### 参数

| 参数 | 类型 | 必选 | 说明 |
|------|------|:--:|------|
| `id` | `string` | ✅ | 菜单项唯一 ID |
| `label` | `string` | ✅ | 菜单项显示文本 |
| `onSelect` | `(song) => void \| Promise<void>` | ✅ | 点击回调，参数是当前右键的歌曲对象 |
| `order` | `number` | ❌ | 排序权重（默认 1000），相同 order 按标题排序 |
| `danger` | `boolean` | ❌ | 以危险样式（红色）渲染 |
| `visible` | `(song) => boolean` | ❌ | 是否显示该项（按歌曲判断；抛错时按不显示处理） |
| `enabled` | `(song) => boolean` | ❌ | 是否可用（按歌曲判断；抛错时按禁用处理） |

### 注意事项

- `onSelect` 可以是 `async` 函数，抛错会被宿主捕获并上报，不会影响其他菜单项
- 多个插件可以注册不同的右键菜单项，EchoMusic 会自动合并
- 菜单项的内部 key 是 `插件ID:菜单项id`，**不同插件使用相同的 `id` 不会互相覆盖**；只有同一插件重复注册相同 `id` 时才会替换旧项

---

## 播放栏按钮（ui.playerbar）

`ctx.ui.playerbar.register()` 在底部播放栏注册操作按钮。

```js
let unread = 0;

ctx.ui.playerbar.register({
  id: "inbox",
  title: "消息中心",
  icon: "mdi:email-outline",
  tooltip: "查看消息",
  badge: () => (unread > 0 ? unread : null),
  badgeTitle: "未读消息",
  defaultPlacement: "right",
  onClick: () => {
    unread = 0;
    ctx.toast.info("已全部标记为已读");
  },
});
```

### 参数

| 参数 | 类型 | 必选 | 说明 |
|------|------|:--:|------|
| `id` | `string` | ✅ | 操作唯一 id |
| `title` | `string` | ✅ | 操作名称（同时是无 tooltip 时的提示文本） |
| `icon` | `string \| IconifyIcon` | ✅ | 图标 |
| `onClick` | `() => void \| Promise<void>` | ✅ | 点击回调（执行期间按钮自动显示忙碌态） |
| `tooltip` | `string` | ❌ | 悬停提示，默认取 `title` |
| `badge` | `string \| number \| (() => ...)` | ❌ | 徽标内容；函数形式可动态计算，返回 `null`/空串隐藏 |
| `badgeTitle` | `string` | ❌ | 徽标的辅助说明（无障碍提示） |
| `badgeDefaultVisible` | `boolean` | ❌ | 徽标默认是否显示（默认 `true`） |
| `trigger` | `"click" \| "hover"` | ❌ | 触发方式，默认 `"click"` |
| `defaultPlacement` | `"left" \| "center" \| "right" \| "more"` | ❌ | 默认摆放区域，默认 `"more"`（更多菜单） |
| `order` | `number` | ❌ | 排序权重（默认 1000） |
| `visible` / `disabled` | `boolean \| () => boolean` | ❌ | 显隐与置灰（支持函数） |

用户可以在宿主的「固定按钮」管理里把按钮在工具区与更多菜单之间拖动调整；`defaultPlacement` 只是首次注册时的默认位置。

---

## 标题栏按钮（ui.titlebar）

`ctx.ui.titlebar.register()` 在主窗口标题栏（工具区或「更多」菜单）注册操作。

```js
ctx.ui.titlebar.register({
  id: "quick-tools",
  title: "快捷工具",
  icon: "mdi:magic-staff",
  tooltip: "打开快捷工具",
  defaultPlacement: "toolbar",
  onClick: () => ctx.toast.info("快捷工具"),
});
```

### 参数

| 参数 | 类型 | 必选 | 说明 |
|------|------|:--:|------|
| `id` | `string` | ✅ | 操作唯一 id |
| `title` | `string` | ✅ | 操作名称 |
| `icon` | `string \| IconifyIcon` | ✅ | 图标 |
| `onClick` | `() => void \| Promise<void>` | ✅ | 点击回调（自动忙碌态） |
| `tooltip` | `string` | ❌ | 悬停提示，默认取 `title` |
| `defaultPlacement` | `"toolbar" \| "more"` | ❌ | 默认区域：工具栏按钮或「更多」菜单，默认 `"more"` |
| `order` | `number` | ❌ | 排序权重（默认 1000） |
| `visible` / `disabled` | `boolean \| () => boolean` | ❌ | 显隐与置灰（支持函数） |

---

## 歌词页换肤（ui.lyricsPage）

插件可以注册一个自定义歌词页皮肤，替换宿主歌词页的渲染组件。

> 需要 capability：`lyricsPage: true`

```js
ctx.ui.lyricsPage.register({
  id: "my-skin",
  title: "我的皮肤",
  preview: "preview.png",              // 换肤面板预览图（插件内路径）
  component: MyLyricPage,              // Vue 组件
  titlebar: "host",                    // 顶部标题栏：host=宿主提供 / none=插件自绘
  tools: "host",                       // 右侧歌词工具按钮：host / none
  settings: {                          // 可选：皮肤设置（渲染在宿主设置抽屉）
    defaults: { fontSize: 20 },
    // component: MySkinSettings,
    // validate: (values) => true,
  },
});

// 在歌词页/设置组件的 setup() 中：
const page = ctx.ui.lyricsPage.usePage();   // 歌词页上下文（播放/歌词状态）
const skin = ctx.ui.lyricsPage.useSkin();   // 当前皮肤配置句柄（按皮肤隔离持久化）
ctx.ui.lyricsPage.openSkins();              // 打开宿主换肤面板（自绘 UI 时提供换肤入口）
```

注册项：`id` 与 `component` 必填，`title?`、`preview?`、`titlebar?`（默认 `"host"`）、`tools?`（默认 `"host"`）、`settings?`（`defaults` 必填，`component?` / `validate?` 可选）。皮肤异常时宿主会自动回退到内置皮肤；完整 API 与上下文说明见官方插件仓库 [主题示例](https://github.com/hoowhoami/EchoMusicPlugins/tree/main/app-theme-example)。

---

## 组件挂载（mount）

使用 `ctx.ui.mount()` 将 Vue 组件挂载到页面的指定 DOM 位置。

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

  // 挂载到播放器底部区域
  ctx.ui.mount("#player-footer", Widget, {
    position: "append",
    className: "my-plugin-widget",
    id: "footer-widget",
  });
}
```

### 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `target` | `string \| Element` | 目标 DOM 位置（CSS 选择器或 DOM 元素） |
| `component` | `Component` | 要挂载的 Vue 组件 |
| `options.props` | `Record<string, unknown>` | 传给组件的 props |
| `options.position` | `"append" \| "prepend" \| "before" \| "after" \| "replace"` | 插入方式，默认 `"append"` |
| `options.className` | `string` | 附加到挂载容器的类名 |
| `options.id` | `string` | 挂载容器标记（写入 `data-echo-plugin-mount`），便于后续查找 |

挂载返回清理函数并自动登记：插件禁用/卸载时组件自动卸载、容器移除。挂载的组件与宿主共享 Pinia 与 Router，可直接使用宿主状态与 `<Icon>` 组件。

---

## 组件浮层（teleport）

使用 `ctx.ui.teleport()` 把组件挂载到 `document.body` 下，适合通知条、悬浮球等全局浮层——不受宿主布局容器的 overflow 裁剪影响。

```js
const dispose = ctx.ui.teleport(
  FloatingBall,                       // 第一个参数就是组件
  { props: { size: 48 }, className: "my-floating-ball" },
);
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `component` | `Component` | 要挂载的 Vue 组件 |
| `options.props` | `Record<string, unknown>` | 传给组件的 props |
| `options.className` | `string` | 附加类名（容器自带 `echo-plugin-teleport`） |
| `options.id` | `string` | 挂载容器标记（可选） |

**与 `mount` 的区别：**
- `mount` 需要指定目标元素，支持五种插入位置；目标不存在时抛错
- `teleport` 固定挂载到 `document.body` 末尾，无需目标元素，适合全局浮层

---

## 预置组件（ui.components）

`ctx.ui.components` 自动暴露宿主的全部可复用组件，无需手动登记：宿主新增组件即可直接使用。覆盖三类目录：

| 目录 | 内容 |
|------|------|
| `ui/` | 基础控件：`Button`、`Switch`、`Input`、`Select`、`Slider` 等 |
| `music/` | 音乐业务组件：`SongList`、`CoverCard`、`BarrageControls` 等 |
| `player/` | 播放器弹层组件 |

另有三个歌词页专用组件：`LyricScroller`（歌词滚动列表）、`LyricPlayerControls`（歌词页控制条）、`BarrageControls`（弹幕控制）。

每个条目都是 `() => Promise<Component>` 异步加载器，用 `defineAsyncComponent` 消费：

```js
const { h, defineAsyncComponent } = ctx.vue;
const Button = defineAsyncComponent(ctx.ui.components.Button);
const SongList = defineAsyncComponent(ctx.ui.components.SongList);
const LyricScroller = defineAsyncComponent(ctx.ui.components.LyricScroller);
```

> 组件的 props 契约以宿主源码为准（`src/renderer/components/`），跨版本可能演进；建议在 `requires.echoMusicVersion` 中锁定测试过的版本范围。

---

## CSS 注入

使用 `ctx.css.inject()` 动态注入 CSS 样式。

```js
ctx.css.inject(`
  .my-plugin-panel {
    border-radius: 12px;
    background: var(--color-bg-secondary);
    padding: 16px;
  }
`);
```

- 注入的 CSS 在插件禁用/卸载时**自动移除**
- 传入 `{ id: "unique-id" }` 可按 id 去重更新（同 id 再次注入会替换旧样式）
- 适合注入少量动态样式；大量样式推荐使用 manifest 的 `style` 字段

---

## DOM 查询与监听

`ctx.dom` 提供受管的 DOM 查询与出现监听。

```js
// 单个 / 全部查询
const container = ctx.dom.query(".playlist-container");
const items = ctx.dom.queryAll(".song-item");

// 监听元素出现
const stop = ctx.dom.observe(
  ".playlist-container",
  (element) => {
    console.log("播放列表已渲染", element);
    // 可选：返回清理函数，元素从文档移除或监听结束时调用
    return () => console.log("播放列表已卸载");
  },
  { root: document.querySelector("#app"), once: false },
);
```

| API | 说明 |
|-----|------|
| `query(selector)` | `querySelector` 封装，未匹配返回 `null` |
| `queryAll(selector)` | `querySelectorAll` 封装，返回数组 |
| `observe(selector, handler, options?)` | 监听匹配元素出现，返回停止函数 |

`observe` 的 `options`：

| 选项 | 类型 | 说明 |
|------|------|------|
| `root` | `Element \| Document` | 监听根节点，默认 `document.body`；传元素时该元素脱离文档会自动清理 |
| `once` | `boolean` | 首次匹配后自动停止 |

`handler` 返回函数时作为该元素的清理回调：元素被移除、根节点脱离文档或监听停止时调用，适合注销事件绑定、断开 IntersectionObserver 等。监听在插件禁用/卸载时自动解除。

---

## 滚动控制（scroll）

`ctx.scroll` 提供宿主滚动容器的查询、滚动与出现监听。宿主的内容区滚动容器带有 `data-echo-scroll-container` 标记（`ctx.scroll.selector` 即该选择器）。

```js
// 查询滚动容器；visible: false 时包含不可见（被缓存/遮挡）的容器
const containers = ctx.scroll.queryContainers({ role: "main", visible: true });

// 滚动：target 支持 "top" / "bottom" / 像素值
ctx.scroll.scrollTo(container, "bottom", { behavior: "smooth" });

// 快捷方法（缺省元素时使用当前可见容器）
ctx.scroll.scrollToTop();
ctx.scroll.scrollToBottom();

// 监听容器出现，handler 返回清理函数（元素销毁或监听停止时调用）
const stop = ctx.scroll.observeContainers((element, state) => {
  console.log("容器出现", state);   // { scrollTop, scrollHeight, clientHeight, distanceToBottom, canScroll, atTop, atBottom }
  const onScroll = () => console.log(element.scrollTop);
  element.addEventListener("scroll", onScroll);
  return () => element.removeEventListener("scroll", onScroll);
});
```

| API | 说明 |
|-----|------|
| `selector` | 滚动容器的 CSS 选择器常量 |
| `queryContainers({ role?, visible? })` | 查询容器；`role` 按 `data-echo-scroll-role` 过滤，`visible` 默认只返回可见容器 |
| `getCurrentContainer()` | 第一个可见容器 |
| `getState(el?)` | 读取滚动状态快照 |
| `scrollTo(el, target, options?)` | 滚动到顶部/底部/指定像素位置，默认平滑滚动 |
| `scrollToTop(el?)` / `scrollToBottom(el?)` | 快捷方法 |
| `observeContainers(handler)` | 监听容器出现；每个容器只回调一次 |

适合做「滚动到底部自动加载更多」「点击回到顶部」等交互。

---

## 下一步

| 文档 | 内容 |
|------|------|
| [播放器与音频引擎 →](./player-audio) | `ctx.player`、音频频谱、歌词系统 |
| [API 总览 →](./context-api) | ctx 完整 API 列表 |
| [发布与分发 →](./publishing) | 发布插件到在线插件源 |
