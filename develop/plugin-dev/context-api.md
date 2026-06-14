---
title: 上下文 API 参考
outline: [2, 4]
---

# 🔧 上下文 API 参考

`ctx` 对象是插件的核心入口，由 EchoMusic 在调用 `activate(ctx)` 时注入。本文档按类别整理 `ctx` 上的所有可用属性和方法。

## 宿主运行时

EchoMusic 构建在 Vue 3 + Pinia + Vue Router 之上。插件可以通过 `ctx` 直接访问这些框架的运行时实例。

### ctx.vue

Vue 3 运行时，提供 `defineComponent`、`h`、`ref`、`computed`、`watch` 等核心 API。

```js
const { defineComponent, h, ref, computed, watch, onMounted, onUnmounted } = ctx.vue;
```

| 属性 / 方法 | 类型 | 说明 |
|-------------|:--:|------|
| `defineComponent(options)` | 函数 | 定义一个 Vue 组件 |
| `h(tag, props, children)` | 函数 | 渲染函数（VNode） |
| `ref(value)` | 函数 | 创建响应式引用 |
| `computed(getter)` | 函数 | 创建计算属性 |
| `watch(source, callback)` | 函数 | 监听响应式数据变化 |
| `onMounted(fn)` | 函数 | 组件挂载后回调 |
| `onUnmounted(fn)` | 函数 | 组件卸载前回调 |
| `defineAsyncComponent(source)` | 函数 | 定义异步组件 |

> ⚠️ **不要**写 `import { ref } from 'vue'`。插件运行环境中没有 `vue` 模块的 bare import 支持。始终通过 `ctx.vue` 获取。

### ctx.app

| 类型 | 说明 |
|:--:|------|
| Vue App 实例 | 主应用的 Vue 应用实例 |

### ctx.router

| 类型 | 说明 |
|:--:|------|
| Router 实例 | Vue Router 实例 |

### ctx.pinia

| 类型 | 说明 |
|:--:|------|
| Pinia 实例 | Pinia 状态管理实例 |

---

## Stores（状态管理）

通过 `ctx.stores` 可以访问 EchoMusic 的核心状态：

| Store | 说明 |
|-------|------|
| `ctx.stores.player` | 播放器状态：当前歌曲、播放进度、音量、播放模式等 |
| `ctx.stores.playlist` | 播放队列状态：队列列表、添加/移除歌曲 |
| `ctx.stores.lyric` | 歌词状态：当前歌词行、时间偏移 |
| `ctx.stores.settings` | 用户设置状态：主题、音质、快捷键等 |
| `ctx.stores.theme` | 主题状态：主题色、深浅模式 |

```js
export function activate(ctx) {
  // 读取播放状态
  console.log("当前音量：", ctx.stores.player.volume);

  // 监听设置变化
  ctx.vue.watch(
    () => ctx.stores.settings.someKey,
    (newVal) => {
      console.log("设置已变更为：", newVal);
    }
  );
}
```

---

## ctx.manifest

| 类型 | 说明 |
|:--:|------|
| `object` | 当前插件的 manifest 对象（只读） |

```js
console.log(ctx.manifest.id);      // "my-plugin"
console.log(ctx.manifest.name);    // "My Plugin"
console.log(ctx.manifest.version); // "1.0.0"
```

---

## UI 组件

### ctx.ui.components

EchoMusic 预置了几个常用的 UI 组件，插件可以直接复用：

| 组件 | 说明 |
|------|------|
| `ctx.ui.components.Button` | 按钮组件 |
| `ctx.ui.components.Switch` | 开关组件 |
| `ctx.ui.components.Input` | 输入框组件 |

```js
const { defineAsyncComponent } = ctx.vue;
const Button = defineAsyncComponent(ctx.ui.components.Button);
const Switch = defineAsyncComponent(ctx.ui.components.Switch);
const Input = defineAsyncComponent(ctx.ui.components.Input);

// 在渲染函数中使用
ctx.vue.h(Button, { size: "xs", onClick: handleClick }, { default: () => "保存" });
ctx.vue.h(Switch, { modelValue: enabled.value, "onUpdate:modelValue": (v) => { enabled.value = Boolean(v); } });
```

### ctx.ui.addPage(options)

注册一个独立的侧边栏页面。

| 参数 | 类型 | 必选 | 说明 |
|------|------|:--:|------|
| `options.id` | `string` | ✅ | 页面唯一 ID |
| `options.title` | `string` | ✅ | 页面标题（显示在侧边栏） |
| `options.icon` | `string` | ❌ | 侧边栏图标（Emoji 或 SVG） |
| `options.component` | `Component` | ✅ | Vue 组件 |
| `options.order` | `number` | ❌ | 排序权重，数字越小越靠前 |

```js
ctx.ui.addPage({
  id: "my-page",
  title: "我的页面",
  icon: "🎵",
  component: MyPageComponent,
  order: 100,
});
```

### ctx.ui.settings.define(options)

注册插件的设置面板，显示在 EchoMusic 的插件管理页中。

| 参数 | 类型 | 必选 | 说明 |
|------|------|:--:|------|
| `options.title` | `string` | ✅ | 设置面板标题 |
| `options.component` | `Component` | ✅ | Vue 组件 |

```js
ctx.ui.settings.define({
  title: "我的插件设置",
  component: SettingsPanel,
});
```

### ctx.ui.addSongContextMenuItem(options)

向歌曲右键菜单添加自定义选项。

| 参数 | 类型 | 必选 | 说明 |
|------|------|:--:|------|
| `options.id` | `string` | ✅ | 菜单项唯一 ID |
| `options.label` | `string` | ✅ | 菜单项显示文本 |
| `options.onSelect` | `(song) => void` | ✅ | 点击回调，`song` 为当前歌曲对象 |

```js
ctx.ui.addSongContextMenuItem({
  id: "copy-song-id",
  label: "复制歌曲 ID",
  async onSelect(song) {
    await navigator.clipboard.writeText(song.id || "");
    ctx.toast.success("已复制歌曲 ID");
  },
});
```

### ctx.ui.mount(el, component)

将 Vue 组件挂载到指定的 DOM 元素。

| 参数 | 类型 | 说明 |
|------|------|------|
| `el` | `string \| HTMLElement` | CSS 选择器或 DOM 元素 |
| `component` | `Component` | Vue 组件 |

> 插件禁用/卸载时会自动清理通过 `mount` 挂载的组件。

### ctx.ui.teleport(selector, component)

将 Vue 组件传送到指定的 CSS 选择器位置（使用 Vue 的 `<Teleport>`）。

| 参数 | 类型 | 说明 |
|------|------|------|
| `selector` | `string` | CSS 选择器 |
| `component` | `Component` | Vue 组件 |

---

## Toast 提示

| API | 说明 |
|-----|------|
| `ctx.toast.success(msg)` | 显示绿色成功提示 |
| `ctx.toast.info(msg)` | 显示蓝色信息提示 |
| `ctx.toast.error(msg)` | 显示红色错误提示 |

```js
ctx.toast.success("操作成功");
ctx.toast.info("正在处理...");
ctx.toast.error("发生错误，请重试");
```

---

## ctx.dispose(fn)

注册清理函数。插件禁用或卸载时自动调用。

| 参数 | 类型 | 说明 |
|------|------|------|
| `fn` | `() => void` | 清理回调 |

```js
// 注册自行管理的副作用清理
let timer = setInterval(() => { /* ... */ }, 1000);

ctx.dispose(() => {
  clearInterval(timer);
  console.log("定时器已清除");
});
```

> EchoMusic 会自动清理通过宿主 API 注册的资源（页面、设置、菜单、事件监听、挂载组件等）。只有**直接修改 DOM** 或**注册了宿主无法感知的副作用**时，才需要 `ctx.dispose()`。

---

## 下一步

| 文档 | 内容 |
|------|------|
| [UI 扩展指南 →](./ui-extension) | 界面定制的深入实践 |
| [播放器与音频 →](./player-audio) | `ctx.player`、音频频谱、歌词系统 |
| [文件存储与事件 →](./filesystem-events) | 本地文件、KV 存储、事件监听 |
