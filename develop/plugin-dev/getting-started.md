---
title: 快速开始
outline: [2, 4]
---

# 🚀 快速开始

本指南带你从零创建一个 EchoMusic 插件，只需 5 分钟。

## 前提条件

- 已安装 **EchoMusic ≥ 2.2.6-beta.9**
- 一个文本编辑器（VS Code 推荐）
- 基础的 JavaScript 知识

## 第一步：创建插件目录

在文件管理器中打开 EchoMusic 的插件目录，新建一个文件夹：

```
EchoMusic/
  plugins/              ← 插件根目录
    hello-echo/         ← 你的插件目录
```

> 💡 在 EchoMusic 设置 → 插件 → 点击"打开插件目录"可以快速定位。

## 第二步：编写 manifest.json

在 `hello-echo/` 中创建 `manifest.json`：

```json
{
  "id": "hello-echo",
  "name": "Hello Echo",
  "version": "1.0.0",
  "description": "我的第一个 EchoMusic 插件",
  "author": "你的名字",
  "main": "index.js",
  "requires": {
    "echoMusicVersion": ">=2.2.6-beta.9"
  }
}
```

### manifest.json 最小字段

| 字段 | 说明 |
|------|------|
| `id` | 插件唯一标识，建议使用 `kebab-case`，如 `hello-echo` |
| `name` | 在插件管理页显示的插件名称 |
| `version` | [语义化版本号](https://semver.org/lang/zh-CN/)，如 `1.0.0` |
| `main` | 入口文件，通常是 `index.js` |

这三个字段是必填的。其他字段（description、author、icon 等）可选但推荐填写。

## 第三步：编写入口文件

在 `hello-echo/` 中创建 `index.js`：

```js
// hello-echo/index.js

/**
 * 插件启用时调用
 * @param {object} ctx — 插件上下文，所有 API 的入口
 */
export function activate(ctx) {
  // 显示一条欢迎提示
  ctx.toast.success(`🎉 ${ctx.manifest.name} 已启用！`);

  // 在控制台输出插件信息
  console.log(`[${ctx.manifest.id}] 插件已激活，版本 ${ctx.manifest.version}`);

  // 监听歌曲切换
  ctx.events.onTrackChange((track) => {
    console.log(`[${ctx.manifest.id}] 正在播放：${track.title}`);
  });
}

/**
 * 插件禁用或卸载前调用
 * 用于清理资源（定时器、DOM 修改等）
 */
export function deactivate(ctx) {
  console.log(`[${ctx.manifest.id}] 插件已停用`);

  // 大多数注册的资源（事件监听、页面、设置、菜单等）
  // 会被 EchoMusic 自动清理，无需手动移除
}
```

### 入口文件规则

| 规则 | 说明 |
|------|------|
| **ESM 格式** | 入口文件以浏览器 ESM 方式加载，使用 `export` 导出 |
| **两个导出函数** | `activate(ctx)` 和 `deactivate(ctx)`，均为异步安全的 |
| **无 bare import** | 不能写 `import { ref } from 'vue'`，要用 `ctx.vue.ref` |
| **文件名** | 由 manifest 的 `main` 字段指定，支持 `.js` 和 `.mjs` |

## 第四步：测试插件

1. **重启 EchoMusic**（或打开插件管理页，EchoMusic 会自动扫描新插件）
2. 进入 **设置 → 插件管理**
3. 找到 "Hello Echo"，点击**启用**
4. 应该看到右下角弹出 "🎉 Hello Echo 已启用！"

### 快速重载

开发过程中频繁修改代码时：

- 在插件管理页**禁用再重新启用**插件
- 修改 `manifest.json` 后需要重启才能生效
- 修改 `index.js` 后重新启用即可加载新代码

## 第五步：添加更多功能

现在你已经有了一个可以运行的插件。接下来可以逐步添加功能：

```js
export function activate(ctx) {
  // 1. 添加鼠标右键菜单
  ctx.ui.addSongContextMenuItem({
    id: "copy-song-info",
    label: "复制歌曲信息",
    async onSelect(song) {
      const info = `${song.title} - ${song.artist}`;
      await navigator.clipboard.writeText(info);
      ctx.toast.success("已复制歌曲信息");
    },
  });

  // 2. 注册插件设置面板
  const SettingsPanel = {
    setup() {
      return () =>
        ctx.vue.h("div", { style: "padding: 12px;" }, [
          ctx.vue.h("p", "这是我的第一个插件 🎉"),
        ]);
    },
  };

  ctx.ui.settings.define({
    title: "Hello Echo 设置",
    component: SettingsPanel,
  });

  // 3. 注册页面
  ctx.ui.addPage({
    id: "hello-page",
    title: "Hello Echo",
    icon: "🎵",
    component: {
      setup() {
        return () =>
          ctx.vue.h("div", { class: "page-container" }, [
            ctx.vue.h("h1", "Hello Echo"),
            ctx.vue.h("p", `当前时间：${new Date().toLocaleString()}`),
          ]);
      },
    },
  });
}
```

## 目录结构全貌

完成以上步骤后，你的插件目录应该是这样的：

```
hello-echo/
  manifest.json      ← 插件描述、版本、权限声明
  index.js           ← 插件入口（ESM）
```

可选扩展：

```
hello-echo/
  manifest.json
  index.js
  style.css          ← 可选：注入页面的样式
  icon.svg           ← 可选：插件图标（SVG/PNG）
  float.html         ← 可选：浮窗页面（需在 manifest 中配置 contributes.windows）
```

## 调试技巧

### 使用开发者工具

1. 在 EchoMusic 中按 `F12` 或 `Ctrl+Shift+I` 打开开发者工具
2. 切换到 **Console** 标签页查看 `console.log` 输出
3. 错误信息会以红色显示，点击可以跳转到源码位置

### 常见错误排查

| 错误现象 | 可能原因 | 解决方法 |
|----------|----------|----------|
| 插件未出现在列表中 | `manifest.json` 格式错误 | 检查 JSON 语法，确保字段名用双引号 |
| 提示"版本不兼容" | `echoMusicVersion` 范围不符 | 更新 EchoMusic 或放宽版本要求 |
| 启用后无反应 | `index.js` 有语法错误 | 打开 DevTools Console 查看报错 |
| 插件名称显示为 id | 缺少 `name` 字段 | 在 manifest 中添加 `name` |
| `ctx.xxx` is undefined | 缺少对应的 capabilities 声明 | 在 manifest 中添加对应的 capability |

## 下一步

- [Manifest 配置参考 →](./manifest) — 了解 manifest 的所有字段
- [上下文 API 参考 →](./context-api) — 浏览完整的 `ctx` API
- [UI 扩展指南 →](./ui-extension) — 学习如何定制界面
- [播放器与音频 →](./player-audio) — 播放控制和音频处理
