---
title: 窗口与交互管理
outline: [2, 4]
---

# 🖥️ 窗口与交互管理

桌面歌词悬浮窗、Mini 播放器、主窗口控制、系统托盘状态同步。

---

## 桌面歌词（ctx.desktopLyric）

控制桌面歌词悬浮窗。

| API | 返回 | 说明 |
|-----|------|------|
| `getSnapshot()` | `Promise<Snapshot>` | 获取当前歌词状态 |
| `show()` / `hide()` | `Promise<Snapshot>` | 显示 / 隐藏 |
| `toggleLock()` | `Promise<Snapshot>` | 切换锁定状态 |
| `updateSettings(s)` | `Promise<Snapshot>` | 更新歌词设置 |
| `onSnapshot(fn)` | 取消函数 | 订阅状态变化 |
| `command(cmd)` | `void` | 发送命令 |
| `setIgnoreMouseEvents(bool)` | `void` | 鼠标穿透开关 |

```js
ctx.desktopLyric.show();
ctx.desktopLyric.onSnapshot((snap) => {
  console.log("歌词可见:", snap.visible, "锁定:", snap.locked);
});
```

---

## Mini 播放器（ctx.miniPlayer）

控制迷你播放器窗口。

| API | 返回 | 说明 |
|-----|------|------|
| `getSnapshot()` | `Promise<Snapshot>` | 获取当前状态 |
| `show()` / `hide()` / `toggle()` | `Promise<Snapshot>` | 显示 / 隐藏 / 切换 |
| `setExpanded(bool)` | `Promise<Snapshot>` | 展开 / 收缩 |
| `setAlwaysOnTop(bool)` | `Promise<Snapshot>` | 置顶开关 |
| `getBounds()` | `Promise<{x,y,w,h}>` | 窗口位置和尺寸 |
| `move(x, y)` | `void` | 移动窗口 |
| `applyExpandBounds()` | `Promise<Snapshot>` | 应用展开尺寸 |
| `onSnapshot(fn)` | 取消函数 | 订阅状态 |
| `onCommand(fn)` | 取消函数 | 命令监听 |
| `notifyLyricVisibility(bool)` | `void` | 通知歌词可见性 |
| `onLyricVisibility(fn)` | 取消函数 | 歌词可见性变化 |
| `command(cmd)` | `void` | 发送命令 |

```js
ctx.miniPlayer.show();
ctx.miniPlayer.setAlwaysOnTop(true);
ctx.miniPlayer.setExpanded(true);
```

---

## 窗口控制（ctx.windowControl）

操作当前窗口的窗口状态。

```js
ctx.windowControl("minimize");   // 最小化
ctx.windowControl("maximize");   // 最大化
ctx.windowControl("close");      // 关闭
ctx.windowControl("fullscreen"); // 全屏
```

> 仅在主窗口和 Mini 播放器中可用。

---

## 系统托盘（ctx.tray）

| API | 说明 |
|-----|------|
| `syncPlayback(state)` | 同步播放状态到托盘（`{ isPlaying, playMode, volume }`） |
| `onSetPlayMode(fn)` | 监听托盘播放模式切换 |

---

## 📂 相关文档

- [内部 API 概览 →](./) — 四大模块速览
- [音频引擎 →](audio-engine) — mpv 引擎完整控制
- [播放状态与持久化 →](playback-state) — 播放事件与队列持久化
- [系统功能集成 →](system-features) — 快捷键、更新、日志等
