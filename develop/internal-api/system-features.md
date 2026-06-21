---
title: 系统功能集成
outline: [2, 4]
---

# ⚙️ 系统功能集成

全局快捷键、电源管理、应用更新、版本信息、日志系统、音效资源管理。

---

## 快捷键（ctx.shortcuts）

| API | 说明 |
|-----|------|
| `register({ enabled, shortcutMap })` | 注册快捷键映射 |
| `refresh()` | 刷新快捷键注册 |
| `onTrigger(fn)` | 监听快捷键触发，回调参数为命令名 |

```js
ctx.shortcuts.register({
  enabled: true,
  shortcutMap: {
    "toggle-visualizer": "Ctrl+Shift+V",
    "next-theme": "Ctrl+Shift+T",
  },
});
ctx.shortcuts.onTrigger((command) => {
  switch (command) {
    case "toggle-visualizer": /* ... */ break;
    case "next-theme": /* ... */ break;
  }
});
```

按键组合兼容 Electron accelerator 语法（`Ctrl+Shift+Key`、`CommandOrControl+Key` 等）。

---

## 电源管理（ctx.power）

| API | 说明 |
|-----|------|
| `onSuspend(fn)` | 系统即将休眠，返回取消函数 |
| `onResume(fn)` | 系统从休眠唤醒，返回取消函数 |

```js
ctx.power.onSuspend(() => {
  // 保存当前状态
});
ctx.power.onResume(() => {
  // 恢复状态
});
```

---

## 更新器（ctx.updater）

控制 EchoMusic 的自动更新流程。

| API | 说明 |
|-----|------|
| `download()` | 下载最新更新 |
| `install(silent?)` | 安装更新（`silent=true` 不弹窗） |
| `onDownloadStatus(fn)` | 下载进度监听，返回取消函数 |

```js
ctx.updater.onDownloadStatus((status) => {
  console.log(`进度: ${status.percent}%`);
});
ctx.updater.download();
```

---

## 应用信息（ctx.appInfo）

| API | 说明 |
|-----|------|
| `get()` | 获取版本号、平台等 `{ version, platform, arch, ... }` |
| `getChangelog()` | 获取更新日志文本 |

---

## 日志系统（ctx.logger / ctx.logging）

```js
// 结构化日志（自动带来源前缀）
ctx.logger.info("操作成功");
ctx.logger.error("处理失败", { details: "..." });
ctx.logger.warn("即将废弃的 API");
ctx.logger.debug("调试信息");
```

```js
// 日志级别设置
const settings = await ctx.logging.get();
await ctx.logging.update({ level: "debug" });  // debug | info | warn | error
```

---

## 音频特效管理（ctx.audioEffects）

管理 IR 脉冲响应音效文件。

| API | 说明 |
|-----|------|
| `importImpulseResponse()` | 打开文件选择器导入 IR 文件 |
| `deleteImpulseResponse(path)` | 删除已导入的 IR 文件 |
| `reconcileImpulseResponses(files)` | 同步 IR 文件列表 |

---

## UI 组件注入（ctx.ui.addPlayerButton）

在主播放器控制栏添加自定义按钮。

```js
ctx.ui.addPlayerButton({
  id: "my-button",
  icon: "tabler:heart",
  label: "收藏",
  onClick() { /* ... */ },
  order: 50,
});
```

> 此 API 为内部接口，插件使用 `ctx.ui.mount()` 挂载到播放器区域实现类似效果。

---

## 📂 相关文档

- [内部 API 概览 →](./) — 四大模块速览
- [音频引擎 →](audio-engine) — mpv 引擎完整控制
- [播放状态与持久化 →](playback-state) — 播放事件与队列持久化
- [窗口与交互管理 →](window-management) — 窗口组件管理
