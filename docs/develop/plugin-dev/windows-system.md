---
title: 窗口与系统
outline: [2, 4]
---

# 🪟 窗口与系统

本文档介绍插件如何控制 EchoMusic 的各类窗口以及访问系统级 API。

> ℹ️ 桌面歌词、Mini 播放器、快捷键、托盘、电源、更新器、日志等属于内部 API，不在插件范围内。详见 [内部 API 参考 →](../internal-api/)。

---

## 浮窗管理

声明在 `contributes.windows` 中的浮窗可以通过 `ctx.windows` 编程式控制。

| API | 说明 |
|-----|------|
| `ctx.windows.show()` | 显示浮窗 |
| `ctx.windows.hide()` | 隐藏浮窗 |
| `ctx.windows.close()` | 关闭浮窗 |
| `ctx.windows.move(x, y)` | 移动窗口到指定坐标 |
| `ctx.windows.getBounds()` | 获取窗口位置和尺寸 `{ x, y, width, height }` |
| `ctx.windows.setIgnoreMouseEvents(bool)` | 鼠标穿透开关 |

```js
// 显示浮窗
ctx.windows.show();
// 隐藏浮窗
ctx.windows.hide();
// 移动
ctx.windows.move(100, 200);
```

> 在浮窗内调用 `ctx.windows` 时，操作的是当前浮窗自身。

---

## Now Playing 浮窗

`ctx.nowPlaying` 操作正在播放信息浮窗，支持同步播放与歌词状态。

| API | 说明 |
|-----|------|
| `getSnapshot()` | 获取当前状态快照 |
| `onSnapshot(fn)` | 订阅状态变化 |
| `onCommand(fn)` | 订阅命令 |
| `syncPlayback(state)` | 同步播放状态 |
| `syncLyric(state)` | 同步歌词状态 |

```js
// 监听播放状态
ctx.nowPlaying.onSnapshot((snapshot) => {
  console.log("Now Playing:", snapshot.title, snapshot.artist);
});

// 同步歌词
ctx.nowPlaying.syncLyric({ currentLine: 5, lines: [...] });
```

---

## 进程管理

> 需要 capability：`process: true`

`ctx.process` 允许插件启动和终止本机可执行程序。

| API | 说明 |
|-----|------|
| `launch(options)` | 启动插件目录内的程序 |
| `terminate(pid?)` | 终止已启动的进程 |

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

`ctx.appIcons` 管理应用窗口和任务栏图标。通过 `ctx.storage` 配置自定义图标路径后调用 `refresh()` 生效。

| API | 说明 |
|-----|------|
| `refresh()` | 刷新所有图标缓存（重新读取配置的图标文件） |
| `setRuntimeWindowIcon(iconPath)` | 设置运行时窗口图标（插件目录内路径） |
| `restoreDefaultWindowIcon()` | 恢复 EchoMusic 默认窗口图标 |
| `restoreDefaultDesktopIcon()` | 恢复默认桌面图标 |
| `restoreDefaultTaskbarIcon()` | 恢复默认任务栏图标 |

```js
// 配置自定义图标
await ctx.storage.set("appIcons", {
  trayIconPath: "generated/tray.png",
  taskbarIconPath: "generated/taskbar.ico",
  desktopIconPath: "generated/desktop.ico",
});
const result = await ctx.appIcons.refresh();
if (!result.desktopApplied && result.desktopError) {
  ctx.toast.warning(result.desktopError);
}
```

支持按平台分别配置：

```js
await ctx.storage.set("appIcons", {
  win32: { trayIconPath: "icons/tray.ico", taskbarIconPath: "icons/taskbar.ico" },
  linux: { trayIconPath: "icons/tray.png", taskbarIconPath: "icons/taskbar.png" },
  darwin: { trayIconPath: "icons/trayTemplate.png", taskbarIconPath: "icons/dock.icns" },
});
await ctx.appIcons.refresh();
```

### 图标库（ctx.icons）

`ctx.icons` 提供 Iconify 图标对象，可直接传入 `Icon` 组件使用：

```js
const Icon = ctx.vue.resolveComponent("Icon");
h(Icon, { icon: ctx.icons.iconPictureInPicture, width: 16, height: 16 });
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
| [播放器与音频引擎 →](./player-audio) | 播放控制、播放队列、频谱、歌词系统 |
| [音频频谱 →](./audio-spectrum) | 实时频谱数据订阅与可视化 |
| [文件存储与数据 →](./filesystem-storage) | 文件系统、KV 存储、外观订阅 |
| [API 总览 →](./context-api) | ctx 完整插件 API 列表 |
| [内部 API 参考 →](../internal-api/) | 内部 API（桌面歌词/Mini/快捷键等） |
