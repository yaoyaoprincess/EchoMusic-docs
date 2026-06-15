---
title: UI 扩展指南
outline: [2, 4]
---

# 🎨 UI 扩展指南

插件可以通过多种方式扩展 EchoMusic 的用户界面。本文档深入介绍每种 UI 扩展机制。

## 注册独立页面

使用 `ctx.ui.addPage()` 在侧边栏中添加一个独立页面。

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
| `icon` | `string` | ❌ | 侧边栏图标，支持 Emoji |
| `component` | `Component` | ✅ | 页面内容组件 |
| `order` | `number` | ❌ | 排序权重，越小越靠前 |

### 使用 Vue SFC 风格组件

如果插件中包含了预编译的 Vue SFC（通过 Vite 打包），可以直接使用：

```js
import MyPage from './components/MyPage.vue';

ctx.ui.addPage({
  id: "my-page",
  title: "My Page",
  icon: "🎵",
  component: MyPage,
});
```

### 页面生命周期

- **注册时机**：建议在 `activate()` 中注册
- **自动清理**：插件禁用/卸载时，页面自动从侧边栏和路由中移除
- **热重载**：重新启用插件会重新注册页面

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
    ctx.storage.kvGet("settings").then((saved) => {
      if (saved) {
        autoScroll.value = saved.autoScroll !== false;
        fontSize.value = saved.fontSize || 14;
      }
    });

    const save = async () => {
      await ctx.storage.kvSet("settings", {
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
| `title` | `string` | ✅ | 设置区域标题 |
| `component` | `Component` | ✅ | 设置面板组件 |

### 最佳实践

- 使用 `ctx.storage.kvSet/kvGet` 持久化用户的设置
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
  async onSelect(song) {
    try {
      // song 对象包含歌曲的完整信息
      const { id, title, artist, album } = song;

      // 自定义处理
      await myCollectionService.addSong(id);

      ctx.toast.success(`已添加「${title}」到收藏`);
    } catch (err) {
      ctx.toast.error("添加失败：" + err.message);
    }
  },
});
```

### 参数

| 参数 | 类型 | 必选 | 说明 |
|------|------|:--:|------|
| `id` | `string` | ✅ | 菜单项唯一 ID |
| `label` | `string` | ✅ | 菜单项显示文本 |
| `onSelect` | `(song) => void` | ✅ | 点击回调，参数是当前右键的歌曲对象 |

### 注意事项

- `onSelect` 可以是 `async` 函数
- 多个插件可以注册不同的右键菜单项，EchoMusic 会自动合并
- 如果 `id` 与其他插件冲突，**后注册的会覆盖先注册的**

---

## 播放器按钮

使用 `ctx.ui.addPlayerButton()` 在播放器控制栏中添加自定义按钮。

```js
ctx.ui.addPlayerButton({
  id: "my-action",
  icon: "❤️",
  label: "收藏",
  onClick() {
    const track = ctx.player.currentTrack;
    if (track) {
      addToFavorites(track);
      ctx.toast.success("已添加到收藏");
    }
  },
  order: 50,
});
```

| 参数 | 类型 | 必选 | 说明 |
|------|------|:--:|------|
| `id` | `string` | ✅ | 按钮唯一标识 |
| `icon` | `string` | ✅ | 按钮图标（Emoji 或 SVG） |
| `label` | `string` | ❌ | 悬停提示文本 |
| `onClick` | `() => void` | ✅ | 点击回调 |
| `order` | `number` | ❌ | 排序权重，越小越靠左 |

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
  ctx.ui.mount("#player-footer", Widget);
}
```

### 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `el` | `string \| HTMLElement` | 目标 DOM 位置（CSS 选择器或 DOM 元素） |
| `component` | `Component` | 要挂载的 Vue 组件 |

---

## 组件传送（teleport）

使用 `ctx.ui.teleport()` 将组件内容传送到页面任意位置（底层是 Vue 的 `<Teleport>`）。

```js
ctx.ui.teleport("#app-header", MyHeaderWidget);
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `selector` | `string` | CSS 选择器，作为 Teleport 的目标 |
| `component` | `Component` | 要传送的 Vue 组件 |

**与 `mount` 的区别：**
- `mount` 直接将组件挂载到目标 DOM（目标元素被替换）
- `teleport` 使用 Vue Teleport，组件的 DOM 被移动到目标内部，组件自身的响应式系统仍归属于原插件上下文

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
- 适合注入少量动态样式；大量样式推荐使用 manifest 的 `style` 字段

---

## DOM 监听

使用 `ctx.dom.observe()` 监听 DOM 节点的插入/移除。

```js
ctx.dom.observe(".playlist-container", (element) => {
  // element 是匹配选择器的 DOM 元素
  console.log("播放列表已渲染", element);
});
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `selector` | `string` | CSS 选择器 |
| `callback` | `(el: HTMLElement) => void` | 节点匹配时的回调 |

- 当匹配选择器的元素**首次出现**时触发回调
- 监听在插件禁用/卸载时**自动解除**

---

## 自定义样式

除了通过 `style` 字段注入 CSS 文件外，还可以在代码中动态添加样式：

```js
// 注入自定义 CSS
const styleEl = document.createElement("style");
styleEl.textContent = `
  .my-widget {
    padding: 8px;
    border-radius: 8px;
    background: var(--color-bg-secondary);
  }
`;
document.head.appendChild(styleEl);

// 注册清理
ctx.dispose(() => {
  styleEl.remove();
});
```

> 推荐优先使用 `ctx.css.inject()` 或 manifest 的 `style` 字段。只在需要动态计算样式时才手动创建 `<style>` 标签。

---

## 下一步

| 文档 | 内容 |
|------|------|
| [播放器与音频引擎 →](./player-audio) | `ctx.player`、音频频谱、歌词系统 |
| [API 总览 →](./context-api) | ctx 完整 API 列表 |
| [发布与分发 →](./publishing) | 发布插件到在线插件源 |
