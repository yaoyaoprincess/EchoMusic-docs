---
title: 播放状态与持久化
outline: [2, 4]
---

# 📡 播放状态与持久化

播放生命周期事件监听、队列持久化存储、本地 HTTP API 服务、主进程 HTTP 请求代理。

---

## 核心事件（ctx.events）

主要播放器核心事件订阅（区别于 `ctx.audio.on*` mpv 引擎事件）。

| API | 回调参数 | 说明 |
|-----|----------|------|
| `onTrackChange(fn)` | `(track)` | 歌曲切换 |
| `onPlayStateChange(fn)` | `(isPlaying)` | 播放/暂停状态 |
| `onVolumeChange(fn)` | `(volume)` | 音量变化 |

```js
ctx.events.onTrackChange((track) => {
  console.log(`${track.title} - ${track.artist}`);
});
```

注册的监听器在窗口卸载时自动移除。

---

## 播放队列持久化（ctx.storage.playback\*）

与 `ctx.player.playlist`（运行时队列）不同，`playback*` 是持久化的存储操作，支持重启后恢复。

| API | 说明 |
|-----|------|
| `playbackGetSnapshot()` | 当前播放状态快照 |
| `playbackGetQueue()` | 完整播放队列 |
| `playbackReplaceQueue(items)` | 替换整个队列 |
| `playbackAppendQueueItems(items)` | 追加歌曲 |
| `playbackRemoveQueueItem(songId)` | 移除歌曲 |
| `playbackReorderQueueItems(from, to)` | 重排歌曲位置 |
| `playbackSetCurrentTrack(songId)` | 设置当前曲目 |
| `playbackUpdateMeta(meta)` | 更新队列元数据 |

```js
// 快照示例
const snap = await ctx.storage.playbackGetSnapshot();
console.log(snap.currentTrack, snap.queue.length);

// 追加歌曲
await ctx.storage.playbackAppendQueueItems([
  { songId: "xxx", title: "...", artist: "..." }
]);
```

---

## API 服务器（ctx.apiServer）

EchoMusic 内置的本地 HTTP API 服务。

| API | 说明 |
|-----|------|
| `start()` | 启动本地 HTTP API 服务 |
| `status()` | 获取运行状态 `{ running, port }` |

```js
const { running, port } = await ctx.apiServer.status();
if (!running) await ctx.apiServer.start();
```

---

## HTTP 请求（ctx.api.request）

主进程代理的内部 HTTP 客户端。

```js
const result = await ctx.api.request({
  method: "GET",
  url: "https://api.example.com/data",
  params: { page: 1 },
  headers: { "X-Custom": "value" },
});
console.log(result.data);
```

| 参数 | 类型 | 必选 | 说明 |
|------|------|:--:|------|
| `method` | `string` | ✅ | HTTP 方法（GET / POST / PUT / DELETE） |
| `url` | `string` | ✅ | 请求 URL |
| `params` | `object` | ❌ | URL 查询参数 |
| `data` | `any` | ❌ | 请求体数据 |
| `headers` | `object` | ❌ | 自定义请求头 |

---

## 📂 相关文档

- [内部 API 概览 →](./) — 四大模块速览
- [音频引擎 →](audio-engine) — mpv 引擎完整控制
- [窗口与交互管理 →](window-management) — 窗口组件管理
- [系统功能集成 →](system-features) — 快捷键、更新、日志等
