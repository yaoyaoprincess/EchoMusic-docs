---
title: 窗口与系统
outline: [2, 4]
---

# 🪟 窗口与系统

本文档介绍插件如何控制 EchoMusic 的各类窗口以及访问系统级 API。

> ℹ️ 托盘、电源、更新器、日志等属于内部 API，不在插件范围内。Mini 播放器与桌面歌词已开放给插件，见下文 [Mini 播放器](#mini-播放器) 与 [桌面歌词](#桌面歌词)。

---

## 浮窗管理

声明在 `contributes.windows` 中的浮窗可以通过 `ctx.windows` 编程式控制。**所有方法都要求第一个参数传入浮窗的 `windowId`**（manifest 中 `contributes.windows[].id`）——插件可以声明多个浮窗，也可以借此操作自己声明的任意窗口（不能操作其他插件的窗口）。

| API | 说明 |
|-----|------|
| `ctx.windows.show(windowId, options?)` | 显示浮窗（未创建时先创建）；返回 `{ ok, window, bounds }` |
| `ctx.windows.hide(windowId)` | 隐藏浮窗 |
| `ctx.windows.close(windowId)` | 关闭浮窗 |
| `ctx.windows.move(windowId, bounds)` | 移动/调整窗口，`bounds` 为 `{ x?, y?, width?, height? }` |
| `ctx.windows.getBounds(windowId)` | 获取窗口位置和尺寸 `{ x, y, width, height }` |
| `ctx.windows.setIgnoreMouseEvents(windowId, ignore)` | 鼠标穿透开关 |
| `ctx.windows.showOnTop(windowId, options?)` | 把窗口抬到最前一次（不改变置顶状态） |

```js
// 显示浮窗（可临时覆盖 manifest 默认值）
await ctx.windows.show("island", {
  width: 420,
  height: 72,
  x: 100,
  y: 0,
  alwaysOnTop: true,
  allowOutsideWorkArea: true,
});

// 隐藏 / 关闭
await ctx.windows.hide("island");
await ctx.windows.close("island");

// 移动到指定位置并调整大小
await ctx.windows.move("island", { x: 100, y: 200, width: 360, height: 64 });

// 读取位置尺寸
const result = await ctx.windows.getBounds("island");
if (result.ok) console.log(result.bounds);

// 鼠标穿透（锁定后的歌词条）
await ctx.windows.setIgnoreMouseEvents("island", true);
```

`show()` 的 `options`：

| 选项 | 类型 | 说明 |
|------|------|------|
| `width` / `height` | `number` | 临时覆盖显示尺寸（仍受 manifest `min*/max*` 与显示器范围约束） |
| `x` / `y` | `number` | 临时覆盖位置 |
| `alwaysOnTop` | `boolean` | 运行时切换置顶（macOS 需要切换窗口类型时宿主会自动重建窗口） |
| `allowOutsideWorkArea` | `boolean` | 是否允许使用完整显示器范围（可贴近或覆盖任务栏区域） |

浮窗的 manifest 字段（`type`、`transparent`、`rememberBounds`、`position` 等）见 [Manifest 配置参考](./manifest#contributeswindows)。

### 拖动与缩放（windows.drag / windows.resize）

在主插件入口中把某个浮窗的窗口拖动/缩放会话绑定到**主窗口内**的 DOM 元素并不常见；这两个 API 主要供底层集成使用，常规做法是在浮窗入口内使用 `ctx.window.drag.bind(element)`（见下文「浮窗专用上下文」）。

```js
// 低层会话 API（windowId 显式传入）
await ctx.windows.drag.start("island", sessionId);
ctx.windows.drag.move("island", sessionId, screenX, screenY);
await ctx.windows.drag.end("island", sessionId);
await ctx.windows.drag.cancel("island", sessionId);

// 也可以把主窗口中的元素绑定为拖动/缩放区域
const stopDrag = ctx.windows.drag.bind("island", titlebarElement);
const stopResize = ctx.windows.resize.bind("panel", handleElement, {
  direction: "se",           // n / ne / e / se / s / sw / w / nw
  minWidth: 240,
  minHeight: 120,
});
```

`bind()` 返回清理函数；manifest 设置 `resizable: false` 时宿主会拒绝缩放会话。

### 抬到最前（showOnTop）

```js
await ctx.windows.showOnTop("island");                  // 抢焦点并激活
await ctx.windows.showOnTop("island", { focus: false }); // 不抢焦点，仅抬升层级
```

`showOnTop()` 把窗口抬到最前一次，但**不改变置顶状态**：窗口隐藏时先显示、最小化时先还原，再抬层。适合「呼出/聚焦」这类一次性动作。

---

## 浮窗专用上下文

浮窗入口（`contributes.windows[].main` 指向的脚本）运行在独立的 Electron 窗口中，导出 `activateWindow(ctx)` / `activate(ctx)` 或默认函数后由宿主调用。**它不是主插件上下文的复用**：没有 `ctx.ui`、`ctx.player`、`ctx.playlist` 等，只提供窗口渲染所需的子集。

```js
// island.js —— 浮窗入口
export function activateWindow(ctx) {
  const { h, createApp, ref, onMounted } = ctx.vue;

  const App = {
    setup() {
      const text = ref("EchoMusic");
      const update = (snapshot) => {
        text.value = snapshot?.lyric?.lines[snapshot?.lyric?.currentIndex ?? -1]?.text
          || snapshot?.playback?.title
          || "EchoMusic";
      };
      onMounted(async () => {
        update(await ctx.nowPlaying.getSnapshot());
        ctx.nowPlaying.onSnapshot(update);
      });
      return () => h("div", { class: "island" }, text.value);
    },
  };

  createApp(App).mount(ctx.container);
}
```

### 上下文成员

| 成员 | 说明 |
|------|------|
| `id` / `pluginId` / `windowId` | 插件与窗口标识 |
| `manifest` / `descriptor` / `windowDescriptor` | 插件与窗口描述符 |
| `vue` / `icons` / `container` | Vue 命名空间、Iconify 图标集、挂载容器 |
| `nowPlaying` | 当前播放快照 API（同主入口） |
| `fonts` / `cover` | 系统字体、主题图标封面 |
| `audio.spectrum` | 频谱 API 子集（`getStatus` / `getSnapshot` / `subscribe(options, handler)`，需 `audioSpectrum` 能力） |
| `storage` | `get` / `set` / `delete`，与主入口共享同一份插件数据 |
| `backups` | 备份 API（只读消费，不能注册备份提供者） |
| `fs` | 文件 API 子集（`listFiles` / `listImageFiles` / `getFileUrl` / `readTextFile` / `readFileBytes` / `readAudioMetadata`） |
| `process` | `launch` / `terminate`（需 `process` 能力） |
| `net` / `webServer` / `sqlite` | 原生网络请求、本地 Web 服务、SQLite（能力要求同主入口） |
| `css` | `inject(cssText, { id? })`，样式随窗口销毁自动移除 |
| `electron` | 完整 preload 桥接（高级用法） |
| `dispose(fn)` | 登记清理函数，窗口销毁时统一调用 |

### 当前窗口控制（ctx.window）

浮窗上下文中的 `ctx.window` **只控制当前浮窗自身**，因此不需要 `windowId` 参数：

| API | 说明 |
|-----|------|
| `getBounds()` | 获取当前窗口位置尺寸 |
| `move(bounds)` | 移动/调整当前窗口 |
| `drag.bind(element)` | 把元素绑定为拖动区域（推荐，自动处理 pointer capture、取消、失焦与多屏 DPI） |
| `drag.start/move/end/cancel(sessionId)` | 低层拖动会话 |
| `resize.bind(element, options?)` | 把元素绑定为缩放手柄，`options` 支持 `direction` / `minWidth` / `minHeight` / `maxWidth` / `maxHeight` |
| `resize.start/resize/end/cancel(sessionId, ...)` | 低层缩放会话 |
| `onCancelInteraction(listener)` | 订阅宿主取消当前拖动/缩放会话（例如窗口被关闭时），回调参数为回滚后的 bounds |
| `hide()` / `close()` | 隐藏 / 关闭当前窗口 |
| `setIgnoreMouseEvents(ignore)` | 鼠标穿透开关 |
| `setAlwaysOnTop(alwaysOnTop)` | 切换置顶（建议先把状态写入自己的存储再调用） |
| `showOnTop(options?)` | 抬到最前一次，`options.focus` 默认 `true` |

```js
// 浮窗入口内的典型自拖动标题栏
export function activateWindow(ctx) {
  const titlebar = ctx.container.querySelector(".titlebar");
  const disposeDrag = ctx.window.drag.bind(titlebar);
  ctx.dispose(disposeDrag);

  ctx.window.onCancelInteraction((bounds) => {
    // 宿主已回滚原生窗口位置，这里只需清理渲染层状态
  });
}
```

### 呼出宿主窗口（ctx.host）

主入口与浮窗入口都提供 `ctx.host.showOnTop(target?, options?)`，把**宿主窗口**抬到最前（不改变置顶状态）：

```js
await ctx.host.showOnTop();                     // 等价于 'main'，呼出主窗口
await ctx.host.showOnTop("mini-player");        // 呼出 mini 播放器（未开启时返回 ok: false）
await ctx.host.showOnTop("main", { focus: false });
```

`target` 为 `'main' | 'mini-player'`，默认 `'main'`；`options.focus` 默认 `true`。

---

## Now Playing 快照

`ctx.nowPlaying` 读取与订阅「正在播放」的播放、歌词与外观状态。主插件入口和浮窗入口都可用。

| API | 说明 |
|-----|------|
| `getSnapshot()` | 获取当前状态快照 `{ playback, lyric, appearance, updatedAt }` |
| `onSnapshot(fn)` | 订阅快照变化，返回取消函数 |
| `command(cmd)` | 发送播放/歌词命令（异步投递） |
| `invokeCommand(cmd)` | 同 `command`，但等主进程确认投递后才 resolve |

```js
// 监听播放与歌词状态
ctx.nowPlaying.onSnapshot((snapshot) => {
  console.log("Now Playing:", snapshot.playback?.title, snapshot.appearance?.accentColor);
});

// 命令：字符串命令 + 对象命令
ctx.nowPlaying.command("togglePlayback");
ctx.nowPlaying.command("toggleTranslation");
ctx.nowPlaying.command({ type: "seek", value: 42 });        // 跳到指定秒数
ctx.nowPlaying.command({ type: "setVolume", value: 35 });   // 绝对音量 0-100
ctx.nowPlaying.command({ type: "adjustVolume", delta: -10 }); // 相对音量
```

`playback.currentTime` 是播放引擎最近一次推送的离散进度；歌词滚动等时序敏感场景应结合 `playback.updatedAt` 与 `playback.playbackRate` 本地推算进度。快照各字段类型见官方插件仓库浮窗文档。

---

## Mini 播放器

`ctx.miniPlayer` 控制 EchoMusic 的 Mini 播放器悬浮窗。

> 需要 manifest 声明 `runtime.miniPlayer: true` 的插件才会在 Mini 播放器中运行入口脚本；控制 Mini 播放器窗口本身使用下述 API 即可。

| API | 说明 |
|-----|------|
| `getSnapshot()` | 获取快照 `{ playback, appearance?, window?, queue?, lyric? }` |
| `show()` / `hide()` / `toggle()` | 显示 / 隐藏 / 切换 Mini 播放器 |
| `setExpanded(expanded)` | 展开或收起（展开显示播放队列） |
| `setAlwaysOnTop(alwaysOnTop)` | 切换置顶 |
| `getBounds()` | 获取窗口位置尺寸 |
| `seek(value)` | 跳到指定播放位置（秒） |
| `setVolume(value, requestId?)` | 设置音量 0–100；`requestId` 可关联浮窗滑块请求，避免 UI 抖动 |
| `adjustVolume(delta)` | 相对调整音量（结果 clamp 到 0–100） |
| `onSnapshot(fn)` | 订阅快照变化，返回清理函数 |
| `command(cmd)` | 发送 Mini 播放器命令 |

```js
await ctx.miniPlayer.show();
await ctx.miniPlayer.setExpanded(true);
ctx.miniPlayer.onSnapshot((snapshot) => {
  console.log("Mini 播放中:", snapshot.playback?.title, "音量:", snapshot.playback?.volume);
});
```

`playback` 包含曲目信息、进度、音量、我喜欢状态等；`appearance` 包含深浅色、主题色与 Mini 歌词样式；`window` 包含置顶与展开方向；`queue` / `lyric` 提供队列与歌词数据。`command` 支持 `togglePlayback` / `previousTrack` / `nextTrack` / `toggleFavorite` / `toggleMute` / `toggleDesktopLyric` / `showMainWindow` / `closeMiniPlayer`，以及对象形式 `{ type: 'seek' | 'setVolume' | 'adjustVolume' | 'playQueueTrack', ... }`。

---

## 桌面歌词

`ctx.desktopLyric` 控制 EchoMusic 的桌面歌词窗口。

| API | 说明 |
|-----|------|
| `getSnapshot()` | 获取完整快照 |
| `getWindow()` | 获取桌面歌词窗口 bounds |
| `show()` / `hide()` | 显示 / 隐藏 |
| `toggleLock()` | 切换锁定（锁定后鼠标穿透，需通过宿主解锁） |
| `updateSettings(payload)` | 更新设置（传入 `Partial<DesktopLyricSettings>`，如字体、颜色、对齐、双行/单行等） |
| `updateWindow(bounds)` | 调整窗口位置尺寸 `{ x?, y?, width?, height? }` |
| `onSnapshot(fn)` | 订阅快照变化（全量或增量补丁），返回清理函数 |
| `command(cmd)` | 发送桌面歌词命令 |

```js
const snapshot = await ctx.desktopLyric.getSnapshot();
console.log("桌面歌词已开启:", snapshot.settings.enabled, "锁定:", snapshot.settings.locked);

// 切换显示并调整外观
await ctx.desktopLyric.show();
await ctx.desktopLyric.updateSettings({ opacity: 0.8, activeFontSize: 44 });

ctx.desktopLyric.onSnapshot((message) => {
  // message 是完整快照或增量补丁
});
```

快照包含三段数据：

- **播放段**：`playback`（当前曲目、封面、进度、播放状态、倍速）
- **歌词段**：`lyrics` / `currentIndex` / `lyricTimeOffset` / `lyricsTrackId` / `lockPhase` / `lyricSyncWarning`
- **外观段**：`settings`（字体、字号、颜色、描边、阴影、横竖排、翻译/音译开关等）

完整类型定义见宿主源码 `src/shared/desktopLyric.ts`。`command` 支持 `togglePlayback` / `previousTrack` / `nextTrack` / `toggleLyricsMode` / `cycleLyricsMode` / `openLyricSource` / `toggleTranslation` / `toggleRomanization` / `lyricOffsetBackward` / `lyricOffsetForward` / `lyricOffsetReset` / `openSettings`。

---

## 进程管理

> 需要 capability：`process: true`

`ctx.process` 允许插件启动和终止**插件目录内**的本机可执行程序。

| API | 说明 |
|-----|------|
| `launch(options)` | 启动插件目录内的程序 |
| `terminate(pid)` | 终止已启动的进程（`pid` 必填，来自 `launch` 返回值） |

```js
// 启动程序
const result = await ctx.process.launch({
  executable: "tools/my-helper.exe",  // 相对插件目录的可执行文件路径
  args: ["--port", "12345"],
  env: { CUSTOM_VAR: "value" },
  cwd: "tools/",                      // 相对插件目录的工作目录
});

if (result.ok) {
  const pid = result.pid;
  // 稍后终止
  await ctx.process.terminate(pid);
}
```

| 参数 | 类型 | 必选 | 说明 |
|------|------|:--:|------|
| `executable` | `string` | ✅ | 可执行文件路径（相对插件目录，不能是任意系统路径） |
| `args` | `string[]` | ❌ | 命令行参数 |
| `env` | `Record<string, string>` | ❌ | 额外环境变量（数量与长度受限） |
| `cwd` | `string` | ❌ | 工作目录（相对路径，且必须位于插件目录内） |

### 授权确认流程

为防止恶意插件静默执行本机程序，宿主对每次 `launch` 实施授权确认：

1. **首次启动**：宿主弹出系统对话框「允许插件启动本地程序？」，展示插件名、插件 id 与程序路径，用户选择「允许并记住」后才会启动
2. **哈希绑定**：授权记录与可执行文件的 **SHA-256 哈希**（`executableHash`）绑定；插件更新、版本变化或程序文件内容变化后，会**重新请求确认**
3. **Windows 限制**：Windows 上只允许 `.exe` / `.com` 可执行文件；其他平台要求文件具备执行权限
4. 安全模式开启、插件被禁用或版本不兼容时，`launch` 直接失败

环境变量中会自动注入 `ECHOMUSIC_PLUGIN_ID` 与 `ECHOMUSIC_PLUGIN_DIR`；部分敏感环境变量（如代理凭证类）会被过滤。插件停用/卸载或应用退出时，由插件启动的子进程会被宿主回收（先 SIGTERM，超时后 SIGKILL）。

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

EchoMusic 为插件提供了 `BroadcastChannel` 用于跨窗口通信（主窗口 ↔ Mini 播放器 ↔ 插件浮窗）。

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
