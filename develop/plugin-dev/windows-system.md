---
title: 窗口与系统
outline: [2, 4]
---

# 🪟 窗口与系统

本文档介绍插件如何控制 EchoMusic 的各类窗口以及访问系统级 API。

---

## 浮窗管理

声明在 `contributes.windows` 中的浮窗可以通过 `ctx.window` 编程式控制。

### API

| API | 说明 |
|-----|------|
| `ctx.window.show(pluginId, windowId, options?)` | 显示指定浮窗 |
| `ctx.window.hide(pluginId, windowId)` | 隐藏指定浮窗 |
| `ctx.window.getContext()` | 获取当前浮窗的上下文（仅在浮窗内调用时可用） |

```js
// 显示浮窗
ctx.window.show("my-plugin", "my-float", {
  width: 400,
  height: 300,
});

// 隐藏浮窗
ctx.window.hide("my-plugin", "my-float");
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `pluginId` | `string` | 插件 ID（`ctx.manifest.id`） |
| `windowId` | `string` | 在 manifest 中声明的浮窗 `id` |
| `options` | `object` | 可选，覆盖 manifest 中的默认尺寸 |

---

## 桌面歌词

`ctx.desktopLyric` 提供对桌面歌词悬浮窗的完整控制。

### 状态查询与控制

| API | 返回 | 说明 |
|-----|------|------|
| `getSnapshot()` | `Promise<DesktopLyricSnapshot>` | 获取当前歌词状态快照 |
| `show()` | `Promise<DesktopLyricSnapshot>` | 显示桌面歌词 |
| `hide()` | `Promise<DesktopLyricSnapshot>` | 隐藏桌面歌词 |
| `toggleLock()` | `Promise<DesktopLyricSnapshot>` | 切换锁定状态 |
| `updateSettings(settings)` | `Promise<DesktopLyricSnapshot>` | 更新歌词设置 |
| `command(cmd)` | `void` | 发送命令（如调整字体大小） |
| `setIgnoreMouseEvents(ignore)` | `void` | 鼠标穿透开关（`true` 时点击穿透） |

### 订阅歌词状态

```js
ctx.desktopLyric.onSnapshot((snapshot) => {
  console.log("歌词状态:", snapshot);
  // { visible, locked, lines, currentLine, ... }
});
```

返回值是一个取消函数，插件禁用时自动取消。

### 同步状态

```js
// 将歌词状态同步给其他窗口
ctx.desktopLyric.syncSnapshot({
  locked: true,
  // ... 其他需要同步的字段
});
```

---

## Mini 播放器

`ctx.miniPlayer` 控制迷你播放器窗口。

### 状态查询与控制

| API | 返回 | 说明 |
|-----|------|------|
| `getSnapshot()` | `Promise<MiniPlayerSnapshot>` | 获取当前状态 |
| `show()` / `hide()` / `toggle()` | `Promise<MiniPlayerSnapshot>` | 显示/隐藏/切换 |
| `setExpanded(bool)` | `Promise<MiniPlayerSnapshot>` | 展开/收缩 |
| `setAlwaysOnTop(bool)` | `Promise<MiniPlayerSnapshot>` | 置顶开关 |
| `getBounds()` | `Promise<{x,y,width,height}>` | 获取窗口位置和尺寸 |
| `move(x, y)` | `void` | 移动窗口到指定坐标 |
| `applyExpandBounds()` | `Promise<MiniPlayerSnapshot>` | 应用展开尺寸 |
| `command(cmd)` | `void` | 发送命令 |
| `notifyLyricVisibility(bool)` | `void` | 通知歌词可见性 |

### 订阅

```js
// 状态变化
ctx.miniPlayer.onSnapshot((snapshot) => {
  console.log("Mini 播放器状态:", snapshot);
});

// 命令监听
ctx.miniPlayer.onCommand((cmd) => {
  console.log("接收到命令:", cmd);
});

// 歌词可见性变化
ctx.miniPlayer.onLyricVisibility((visible) => {
  console.log("歌词是否可见:", visible);
});
```

---

## Now Playing 浮窗

`ctx.nowPlaying` 操作正在播放信息浮窗。

| API | 说明 |
|-----|------|
| `getSnapshot()` | 获取当前状态快照 |
| `syncSnapshot(patch)` | 同步状态 |
| `command(cmd)` | 发送命令 |
| `onSnapshot(fn)` | 订阅状态变化 |
| `onCommand(fn)` | 订阅命令 |

```js
// 监听歌词显示状态
ctx.nowPlaying.onSnapshot((snapshot) => {
  console.log("Now Playing:", snapshot.title, snapshot.artist);
});

// 发送命令
ctx.nowPlaying.command("toggleLyrics");
```

---

## 快捷键

`ctx.shortcuts` 允许插件注册和管理全局快捷键。

| API | 说明 |
|-----|------|
| `register({ enabled, shortcutMap })` | 注册快捷键映射 |
| `refresh()` | 刷新快捷键注册（用于更新后重新绑定） |
| `onTrigger(fn)` | 监听快捷键触发，回调参数为命令名 |

```js
// 注册快捷键
ctx.shortcuts.register({
  enabled: true,
  shortcutMap: {
    "toggle-visualizer": "Ctrl+Shift+V",
    "next-theme": "Ctrl+Shift+T",
  },
});

// 监听触发
ctx.shortcuts.onTrigger((command) => {
  switch (command) {
    case "toggle-visualizer":
      toggleVisualizer();
      break;
    case "next-theme":
      cycleTheme();
      break;
  }
});
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `enabled` | `boolean` | 是否启用快捷键 |
| `shortcutMap` | `Record<string, string>` | 命令名 → 按键组合 |

按键组合格式：`Ctrl+Shift+Key`、`Alt+Key`、`CommandOrControl+Key` 等，兼容 Electron accelerator 语法。

---

## 窗口控制

`ctx.windowControl` 操作当前窗口。

```js
ctx.windowControl("minimize");   // 最小化
ctx.windowControl("maximize");   // 最大化
ctx.windowControl("close");      // 关闭
ctx.windowControl("fullscreen"); // 全屏
```

> 仅在主窗口和 Mini 播放器中可用，浮窗内不可调用。

---

## 系统托盘

`ctx.tray` 与系统托盘交互。

```js
// 同步播放状态到托盘图标
ctx.tray.syncPlayback({
  isPlaying: true,
  playMode: "loop",
  volume: 80,
});

// 监听托盘播放模式切换
ctx.tray.onSetPlayMode((playMode) => {
  console.log("播放模式切换为:", playMode);
});
```

---

## 电源事件

`ctx.power` 响应系统休眠/唤醒。

| API | 说明 |
|-----|------|
| `onSuspend(fn)` | 系统即将休眠时回调，返回取消函数 |
| `onResume(fn)` | 系统从休眠中唤醒时回调，返回取消函数 |

```js
ctx.power.onSuspend(() => {
  console.log("系统即将休眠，保存状态...");
  ctx.storage.kvSet("lastState", getCurrentState());
});

ctx.power.onResume(() => {
  console.log("系统已唤醒");
  // 恢复界面
});
```

---

## 进程管理

> 需要 capability：`process: true`

`ctx.process` 允许插件启动和终止本机可执行程序。

| API | 说明 |
|-----|------|
| `launch(options)` | 启动插件目录内的程序 |
| `terminate()` | 终止已启动的进程 |

```js
// 启动程序
const result = await ctx.process.launch({
  command: "tools/my-helper.exe",
  args: ["--port", "12345"],
  env: { CUSTOM_VAR: "value" },
  cwd: "tools/",
});

// 稍后终止
ctx.process.terminate();
```

| 参数 | 类型 | 必选 | 说明 |
|------|------|:--:|------|
| `command` | `string` | ✅ | 可执行文件相对路径（相对于插件目录） |
| `args` | `string[]` | ❌ | 命令行参数 |
| `env` | `Record<string, string>` | ❌ | 额外环境变量 |
| `cwd` | `string` | ❌ | 工作目录（相对路径） |

> ⚠️ 程序路径必须是**插件目录内的相对路径**，不能访问任意系统路径。

---

## 应用图标

`ctx.icons` 管理应用窗口和任务栏图标。

| API | 说明 |
|-----|------|
| `refresh()` | 刷新所有图标缓存（重新读取图标文件） |
| `setRuntimeWindowIcon(iconPath)` | 设置运行时窗口图标（插件目录内路径） |
| `restoreDefaultWindowIcon()` | 恢复 EchoMusic 默认窗口图标 |
| `restoreDefaultDesktopIcon()` | 恢复默认桌面图标 |
| `restoreDefaultTaskbarIcon()` | 恢复默认任务栏图标 |

```js
// 切换为自定义窗口图标
ctx.icons.setRuntimeWindowIcon("icons/alt-icon.png");

// 恢复默认
ctx.icons.restoreDefaultWindowIcon();
```

---

## 应用信息

`ctx.appInfo` 获取 EchoMusic 应用信息。

| API | 说明 |
|-----|------|
| `get()` | 获取版本号、平台等应用信息 |
| `getChangelog()` | 获取更新日志文本 |

```js
const info = await ctx.appInfo.get();
// { version: "2.2.7", platform: "win32", arch: "x64", ... }

const changelog = await ctx.appInfo.getChangelog();
```

---

## 更新器

`ctx.updater` 控制 EchoMusic 的自动更新流程。

| API | 说明 |
|-----|------|
| `download()` | 下载最新更新 |
| `install(silent?)` | 安装已下载的更新（`silent=true` 时不弹窗） |
| `onDownloadStatus(fn)` | 下载进度监听，返回取消函数 |

```js
ctx.updater.onDownloadStatus((status) => {
  console.log(`下载进度: ${status.percent}%`);
  if (status.complete) {
    ctx.toast.info("更新已下载，重启后生效");
  }
});

// 手动触发下载
ctx.updater.download();
```

---

## API 服务器

`ctx.apiServer` 控制 EchoMusic 的内置本地 API 服务。

| API | 说明 |
|-----|------|
| `start()` | 启动本地 HTTP API 服务 |
| `status()` | 获取服务运行状态 |

```js
const { running, port } = await ctx.apiServer.status();
if (!running) {
  await ctx.apiServer.start();
}
```

---

## 字体

`ctx.fonts` 获取系统可用字体。

```js
const fonts = await ctx.fonts.getAll();
// ["Microsoft YaHei", "SimSun", "Arial", ...]
```

---

## 音频特效管理

`ctx.audioEffects` 管理脉冲响应（IR）音效文件。

| API | 说明 |
|-----|------|
| `importImpulseResponse()` | 打开文件选择器导入 IR 音频文件 |
| `deleteImpulseResponse(filePath)` | 删除已导入的 IR 文件 |
| `reconcileImpulseResponses(files)` | 同步 IR 文件列表 |

---

## 日志

`ctx.logging` 和 `ctx.logger` 提供日志功能。

```js
// 结构化日志（自动带插件 ID 前缀）
ctx.logger.info("用户执行了操作");
ctx.logger.error("处理失败", { details: "..." });
ctx.logger.warn("即将废弃的 API");

// 日志设置
const settings = await ctx.logging.get();
await ctx.logging.update({ level: "debug" });
```

---

## 跨窗口通信（BroadcastChannel）

EchoMusic 为插件提供了 `BroadcastChannel` 用于跨窗口通信（主窗口 ↔ Mini 播放器 ↔ 桌面歌词）。

```js
// 主窗口中的插件
const channel = new BroadcastChannel("my-plugin-channel");
channel.postMessage({ type: "sync", data: {...} });

// Mini 播放器中的同一插件（如果 runtime.miniPlayer: true）
const channel = new BroadcastChannel("my-plugin-channel");
channel.onmessage = (event) => {
  console.log("收到同步消息:", event.data);
};
```

> channel 名称建议以插件 ID 为前缀，避免与其他插件冲突。

---

## 下一步

| 文档 | 内容 |
|------|------|
| [播放器与音频引擎 →](./player-audio) | 播放控制、EQ、空间音效、IR 卷积 |
| [音频频谱 →](./audio-spectrum) | 实时频谱数据订阅与可视化 |
| [文件存储与数据 →](./filesystem-storage) | FS、KV 存储、播放队列 |
| [API 总览 →](./context-api) | ctx 完整 API 列表 |
