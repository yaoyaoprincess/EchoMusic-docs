---
title: 播放状态与持久化
outline: [2, 4]
---

# 📡 播放状态与持久化

播放状态快照、播放队列/历史/键值的持久化存储、应用内 API 服务、主进程代理 HTTP 客户端。

> ⚠️ 历史版本文档中的 `ctx.events`（`onTrackChange` / `onPlayStateChange` / `onVolumeChange`）在 preload 中**不存在**。播放事件请订阅 `electron.player.on*`（见[音频引擎](audio-engine)的音频事件一节）；供桌面歌词/迷你播放器等窗口消费的状态同步使用 `electron.nowPlaying.syncSnapshot`（见[窗口与交互管理](window-management)）。

---

## 播放状态存储（electron.storage.\*）

基于 `echo-sqlite-store`（SQLite）的持久化操作，重启后可恢复。preload `electron.storage` 全量 API：

### 播放快照与多队列

| API | 说明 |
|-----|------|
| `getPlaybackSnapshot()` | 全量快照：`{ queues[], activeQueueId, lastNonFmQueueId }` |
| `getPlaybackQueue({ queueId })` | 单个队列（`StoragePlaybackQueueState \| null`） |
| `replacePlaybackQueue({ queue, activeQueueId, lastNonFmQueueId })` | 替换队列（含归属信息） |
| `appendPlaybackQueueItems({ queue, songs, ... })` | 向队列追加歌曲 |
| `updatePlaybackQueueMeta({ queue, ... })` | 更新队列元数据 |
| `clearPlaybackQueue({ queue, ... })` | 清空队列内容 |
| `removePlaybackQueue({ queueId })` | 删除整个队列 |
| `removePlaybackQueueItem({ queueId, songId, ... })` | 移除队列内歌曲 |
| `reorderPlaybackQueueItems({ queueId, songs })` | 重排队列 |
| `setQueueCurrentTrack({ queueId?, trackId? })` | 设置队列当前曲目 |
| `setActiveQueue(queueId)` | 切换活动队列 |

EchoMusic 采用**多队列模型**：私人 FM、默认播放、歌单、每日推荐等各自是独立队列（`type` 为 `default` / `fm` / `playlist` / `daily-recommend` / `home-discover` / `style-recommend` / `ranking` / `album` / `artist` / `search` / `history` / `cloud` / `listen-together` / `manual` / `purchased` / `free-listen` 之一），快照统一记录 `activeQueueId` 与 `lastNonFmQueueId`（从 FM 返回普通播放的凭据）。每条队列含 `songs`（`StorageSong[]`）、`currentTrackId`、`queuedNextTrackIds`、`filteredInvalidCount`、`dynamic`、`meta` 等字段；除 `getPlaybackSnapshot` / `removePlaybackQueue` 外的写操作返回 `StorageResetResult`（重置影响摘要）。

### 播放历史

| API | 说明 |
|-----|------|
| `getHistoryEntries(payload?)` | 查询历史（`StorageHistoryEntry[]`，按歌曲聚合） |
| `recordHistoryPlay(payload)` | 记录一次播放（返回最新条目） |
| `removeHistoryEntries(payload)` | 删除指定历史 |
| `clearHistory()` | 清空历史 |

### 键值存储

| API | 说明 |
|-----|------|
| `getKv<T>(key)` | 读取任意 JSON 值（反序列化后返回） |
| `setKv(key, value)` | 写入 JSON 值 |
| `deleteKv(key)` | 删除键 |
| `resetAll()` | 清空全部存储（键值 + 队列 + 历史） |

### 对应的 SQLite 表结构

`echo-sqlite-store` 的 `initialize` 建表（见[原生模块](/develop/native-addons)）：

| 表 | 用途 |
|----|------|
| `app_kv` | 键值存储（`key` / `value_json` / `updated_at`） |
| `playback_queues` | 多队列元数据（含 `active` / `last_non_fm` / `current_track_id` / `meta_json` 等） |
| `songs` | 歌曲池（`song_key` 主键去重，`payload_json` 存完整曲目） |
| `queue_items` | 队列条目（`(queue_id, position)` 主键，外键级联删除） |
| `play_history` | 播放历史（`song_key` 主键、`history_key` 唯一、`play_count`、`last_played_at`） |

> ⚠️ **没有收藏表**——收藏属于云端酷狗账号数据，不经本地 SQLite 持久化。

插件侧对主数据库的受控 SQL 访问由 `echo-sqlite-store` 的 `plugin_sqlite_*` 系列函数（`plugin_sqlite_all` / `run` / `exec` / `transaction` / `open` / `close` 等）支撑，经主进程 `src/main/plugins/sqlite.ts` 封装后以 `electron.plugins.sqlite.*` 暴露给插件（文档见[插件 SQLite 存储](/develop/plugin-dev/filesystem-storage)）。

---

## 应用内 API 服务（electron.apiServer）

这里的 `apiServer` **不是**本地 HTTP 服务：它是酷狗 API 子模块（KuGouMusicApi）的**进程内宿主**，以 IPC 直连方式调用，**没有 HTTP 端口**（架构说明见[酷狗 API 参考](/develop/kugou-api)）。

| API | 说明 |
|-----|------|
| `start()` | 启动进程内 API 宿主 |
| `status()` | `{ state: "idle" \| "starting" \| "ready" \| "failed", error?, updatedAt }` |
| `identity()` | 设备身份 `{ guid, mac, serverDev, mid }` |

> ⚠️ 历史版本文档写的 `status() → { running, port }` 不正确：当前实现返回上述 `ApiServerStatus` 四态结构，且无可监听端口。

---

## 设置备份（electron.settingsBackup）

| API | 说明 |
|-----|------|
| `export(request)` | 导出设置与数据（`SettingsBackupExportResult`） |
| `inspect()` | 检查当前备份文件（`SettingsBackupInspectResult`） |
| `import(request)` | 从备份恢复（`SettingsBackupImportResult`） |

备份内容覆盖应用设置、播放队列、历史等本地数据。插件级备份（`plugins.backups.create/inspect/restore`）是独立机制，见[插件数据与备份](/develop/plugin-dev/backups)。

---

## HTTP 请求（electron.api.request）

主进程代理的 HTTP 客户端，走酷狗 API 宿主的网络栈（自动套用[网络设置](system-features)的代理策略）。

```js
const result = await electron.api.request({
  method: "GET",
  url: "https://api.example.com/data",
  params: { page: 1 },
  headers: { "X-Custom": "value" },
  data: { /* 请求体 */ },
});
console.log(result.data);
```

| 参数 | 类型 | 必选 | 说明 |
|------|------|:--:|------|
| `method` | `string` | ✅ | HTTP 方法 |
| `url` | `string` | ✅ | 请求 URL |
| `params` | `object` | ❌ | URL 查询参数 |
| `data` | `any` | ❌ | 请求体；`ArrayBuffer`/视图等二进制体走结构化克隆透传（如听歌识曲 PCM），JSON 对象做普通序列化 |
| `headers` | `object` | ❌ | 自定义请求头 |

---

## 📂 相关文档

- [内部 API 概览](/develop/internal-api/) — 模块总览
- [音频引擎](/develop/internal-api/audio-engine) — 引擎事件与控制
- [窗口与交互管理](/develop/internal-api/window-management) — nowPlaying 快照同步
- [系统功能集成](/develop/internal-api/system-features) — 网络设置与诊断
