---
title: 窗口与交互管理
outline: [2, 4]
---

# 🖥️ 窗口与交互管理

任务栏歌词/进度/预览、网络投放（DLNA / AirPlay）、桌面歌词、Mini 播放器、主窗口控制、系统托盘。

---

## Windows 任务栏四件套

四个主进程模块构成 Windows 任务栏集成，底层能力来自 `echo-platform-adaptor`（DWM 缩略图、`Shell_TrayWnd` 子窗口、UIA 布局）：

| 模块 | 功能 |
|------|------|
| `src/main/taskbarMediaBar.ts` | **任务栏歌词**：把歌词窗口作为子窗口嵌入主任务栏，在任务栏空白区渲染滚动歌词与封面 |
| `src/main/taskbarProgress.ts` | **任务栏进度条**：Windows 任务栏图标上的播放进度（`TaskbarList` 进度状态） |
| `src/main/taskbarThumbnail.ts` | **DWM 封面预览**：鼠标悬停任务栏图标时的封面缩略图与 Aero Peek（位图主进程解码、限 512px、premultiplied BGRA 下发） |
| `src/main/thumbar.ts` | **缩略图工具栏按钮**：任务栏预览上的上一首/播放暂停/下一首按钮 |

### 任务栏歌词 API（electron.taskbarLyric）

| API | 说明 |
|-----|------|
| `getState()` | `Promise<TaskbarLyricState>` 当前状态 |
| `setEnabled(enabled)` | 开关任务栏歌词 |
| `setSettings(settings)` | 更新设置（`position: 'auto'\|'left'\|'right'`、`maxWidth`、`fontSize`、`showCover`、`showTranslation`、`wordByWord`） |
| `setContentWidth(width)` | 上报内容宽度（原生布局据此排布） |
| `showMain()` | 请求显示主窗口 |
| `onStateChange(fn)` | 状态推送订阅 |

实现要点（详见上游 `docs/taskbar-child-window-pitfalls.md` 与 `docs/taskbar-explorer-investigation.md`）：

- 窗口首次绘制后 reparent 到主任务栏 `Shell_TrayWnd`，保持 Electron 窗口类型并追加 layered/tool-window/no-activate 样式（`WS_EX_LAYERED` 必须在 `SetParent` **之后**添加，否则渲染进程收不到任何鼠标事件）；
- Win11 用 UIA 结构通知 + WinEvent 定位任务栏空闲区间；Win10 在原生任务列表保留/恢复空间。未知、垂直、拥挤与全屏布局会隐藏歌词子窗口；
- **Explorer 重启恢复**：监听 `WM_TASKBARCREATED`（`TaskbarCreated`）丢弃旧 shell 绑定并重新嵌入；Explorer 重启时 lyric HWND 可能只收到 `WM_NCDESTROY` 而缺 `WM_DESTROY`，原生层 `window_lifecycle.rs` 以 subclass 补齐缺失的销毁阶段，避免 Chromium 析构 CHECK 崩溃；主进程在 `closed` 后延迟重建窗口与会话；
- UIA 消息抑制：对 explorer 的 `WM_GETOBJECT` 返回 0，避免跨进程 UIA 遍历挂起 explorer。

---

## 网络投放（electron.output）

把当前播放投送到 DLNA（UPnP）或 AirPlay 接收设备。

| API | 说明 |
|-----|------|
| `listTargets()` | 列出可发现的投放目标 |
| `refresh()` | 重新扫描 |
| `connect(targetId, pin?)` | 连接目标（AirPlay 支持配对 PIN） |
| `disconnect()` | 断开当前会话 |
| `setEnabled(enabled)` | 开启/关闭投放功能（设备发现） |
| `setBrowsing(open)` | 打开/关闭浏览（持续发现） |
| `setTrackMeta(meta)` | 同步曲目元数据 `{ title?, artist?, album?, artwork?, durationMs?, mime?, headers? }`（封面经媒体服务器提供） |
| `getSession()` | 当前会话状态 |
| `clearRecords()` | 清除连接记录 |
| `onEvent(fn)` | 会话事件订阅 `{ type, payload? }` |

架构：`src/main/mediaTransport/`（`discovery.ts` 设备发现、`dlnaAdapter.ts` DLNA 适配、`raopAdapter.ts` AirPlay/RAOP 适配、`mediaServer.ts` 音频 HTTP 服务、`genaReceiver.ts` UPnP 事件订阅、`didlLite.ts` DIDL-Lite 元数据、`delivery.ts` 投送流程、`upnpClient.ts` echo-upnp 封装）+ `src/main/outputs/`（`outputHost.ts` 约 75KB，输出会话宿主；`sessionManager.ts`、`commandGate.ts`、`airplayBonjourDiagnostics.ts` 等）。原生层由 `echo-upnp`（rupnp）与 `echo-airplay`（ALAC 44.1kHz 16-bit，post-DSP i16 PCM）承担，见[原生模块](/develop/native-addons)。

---

## 正在播放快照（electron.nowPlaying）

主窗口向桌面歌词、迷你播放器等辅助窗口广播播放状态的统一通道：

| API | 说明 |
|-----|------|
| `getSnapshot()` | 取当前完整快照 |
| `syncSnapshot(payload)` | 主窗口推送增量补丁（`NowPlayingSnapshotPatch`） |
| `onSnapshot(fn)` | 辅助窗口订阅完整快照 |
| `command(cmd)` / `invokeCommand(cmd)` | 发送播放命令（异步/同步两种） |
| `onCommand(fn)` | 辅助窗口接收命令 |

快照为嵌套结构：`snapshot.playback`（`trackId`、`title`、`artist`、`album?`、`coverUrl?`、`duration`、`currentTime`、`isPlaying`、`isFavorite`、`isPersonalFM`、`playbackRate`、`clock?` 等）、`snapshot.lyric`（逐行歌词、翻译/音译模式、偏移）、`snapshot.appearance`（暗色、强调色、字体）。

命令集是快捷键命令的超集（`togglePlayback` / `nextTrack` / `toggleTranslation` / `lyricOffsetForward` ...），另支持对象命令 `{ type: 'seek' | 'setVolume', value }` 与 `{ type: 'adjustVolume', delta }`。

---

## 桌面歌词（electron.desktopLyric）

控制桌面歌词悬浮窗（独立透明窗口，主进程 `src/main/desktopLyric/`）。

| API | 返回 | 说明 |
|-----|------|------|
| `getSnapshot()` / `getSessionNonce()` / `getWindow()` / `getHover()` | — | 读取状态、会话 nonce、窗口位置尺寸、悬停状态 |
| `show()` / `hide()` / `toggleLock()` | `Promise<Snapshot>` | 显示 / 隐藏 / 锁定切换 |
| `updateSettings(payload)` | `Promise<Snapshot>` | 更新歌词设置 |
| `updateWindow(bounds)` | — | 更新窗口位置尺寸 |
| `startDrag(sessionId)` → `move(sessionId, x, y)` → `endDrag(sessionId)` | — | 拖拽会话（幂等令牌防串话） |
| `startResize(sessionId)` → `resize(sessionId, bounds)` → `endResize(sessionId)` | — | 缩放会话 |
| `cancelDrag(sessionId)` / `cancelResize(sessionId)` | — | 取消拖拽/缩放（返回回滚边界） |
| `onCancelDrag(fn)` / `onCancelResize(fn)` | 取消函数 | 主进程强制取消时的通知 |
| `syncSnapshot(patch)` | `void` | 主窗口推送歌词内容补丁 |
| `onSnapshot(fn)` | 取消函数 | 订阅快照 |
| `setIgnoreMouseEvents(bool)` | `void` | 鼠标穿透开关 |
| `setUnlockButtonBounds(rect \| null)` | `void` | 锁定态解锁按钮的命中区域 |
| `command(cmd)` | `void` | 发送命令 |

---

## Mini 播放器（electron.miniPlayer）

控制迷你播放器窗口（插件侧封装 `ctx.miniPlayer` 的细节见[插件窗口与系统集成](/develop/plugin-dev/windows-system)，此处保持速查简版）：

| API | 返回 | 说明 |
|-----|------|------|
| `getSnapshot()` / `show()` / `hide()` / `toggle()` | `Promise<Snapshot>` | 状态读取与显示切换 |
| `setExpanded(bool)` / `setAlwaysOnTop(bool)` | `Promise<Snapshot>` | 展开 / 置顶 |
| `getBounds()` / `applyExpandBounds()` | — | 位置尺寸 / 应用展开尺寸 |
| `startDrag(sessionId)` → `move(x, y)` → `endDrag(sessionId)` / `cancelDrag(sessionId)` | — | 拖拽会话 |
| `syncSnapshot(patch)` / `onSnapshot(fn)` | — | 快照同步 |
| `command(cmd)` / `onCommand(fn)` | — | 命令通道 |
| `notifyLyricVisibility(bool)` / `onLyricVisibility(fn)` | — | 歌词可见性联动 |

---

## 窗口控制（electron.windowControl）

操作当前窗口的窗口状态。

```js
electron.windowControl("minimize");   // 最小化
electron.windowControl("maximize");   // 最大化
electron.windowControl("close");      // 关闭
electron.windowControl("fullscreen"); // 全屏
```

> 仅在主窗口和 Mini 播放器中可用。

---

## 系统托盘（electron.tray）

| API | 说明 |
|-----|------|
| `syncPlayback(state)` | 同步播放状态到托盘菜单（`{ isPlaying?, playMode?, volume?, trackTitle?, trackArtist? }`） |
| `onSetPlayMode(fn)` | 监听托盘播放模式切换 |

---

## 📂 相关文档

- [内部 API 概览](/develop/internal-api/) — 模块总览
- [音频引擎](/develop/internal-api/audio-engine) — 引擎事件与控制
- [播放状态与持久化](/develop/internal-api/playback-state) — 队列持久化与 API 服务
- [系统功能集成](/develop/internal-api/system-features) — 窗口合成与背景材质
