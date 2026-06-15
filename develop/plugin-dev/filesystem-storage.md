---
title: 文件存储与数据
outline: [2, 4]
---

# 📁 文件存储与数据

本文档介绍插件的文件系统访问、KV 存储、播放队列持久化、HTTP 请求、事件监听和外观订阅。

---

## 文件系统

> 需要 capability：`localFiles: true`

`ctx.fs` 提供访问本地文件系统的能力。

### API

| 方法 | 参数 | 说明 | 返回 |
|------|------|------|------|
| `listFiles(options)` | `{ directory?, extensions?, recursive? }` | 扫描目录，列出音频文件 | `Promise<FileEntry[]>` |
| `listImageFiles(options)` | `{ directory?, extensions?, recursive? }` | 扫描目录，列出图片文件 | `Promise<FileEntry[]>` |
| `readTextFile(options)` | `{ path, encoding? }` | 读取文本文件内容 | `Promise<string>` |
| `readFileBytes(options)` | `{ path, offset?, length? }` | 读取二进制文件 | `Promise<ArrayBuffer>` |
| `writeFile(options)` | `{ path, data, encoding? }` | 写入文件到插件目录 | `Promise<void>` |
| `deleteFile(path)` | `path: string` | 删除插件目录内的文件 | `Promise<boolean>` |
| `getFileUrl(path)` | `path: string` | 获取文件的播放 URL | `Promise<string>` |

### 扫描本地音乐目录

```js
export function activate(ctx) {
  async function scanMusicDir() {
    try {
      const files = await ctx.fs.listFiles({
        directory: "C:\\Users\\User\\Music",
        extensions: [".mp3", ".flac", ".wav"],
        recursive: true,
      });
      console.log(`找到 ${files.length} 个音频文件`);
      return files;
    } catch (err) {
      ctx.toast.error("扫描目录失败：" + err.message);
      return [];
    }
  }

  scanMusicDir();
}
```

### 播放本地文件

```js
async function playLocalFile(filePath) {
  const url = await ctx.fs.getFileUrl(filePath);
  ctx.player.playTrack({
    id: filePath,
    title: filePath.split("\\").pop(),
    url: url,
  });
}
```

### 读取和写入文件

```js
// 读取文本文件
const text = await ctx.fs.readTextFile({ path: "C:\\logs\\app.log" });

// 读取二进制文件的一部分
const bytes = await ctx.fs.readFileBytes({
  path: "C:\\Data\\large.dat",
  offset: 0,
  length: 1024,
});

// 写入配置到插件目录
await ctx.fs.writeFile({
  path: "user-config.json",
  data: JSON.stringify({ theme: "dark", fontSize: 14 }, null, 2),
});

// 删除文件
await ctx.fs.deleteFile("old-cache.json");
```

> ⚠️ `writeFile` 和 `deleteFile` 只能操作**插件目录内**的文件。`readTextFile` / `readFileBytes` 可以读取任意路径。

---

## KV 存储

`ctx.storage` 提供按插件隔离的持久化键值存储。

| API | 说明 | 返回 |
|-----|------|------|
| `kvGet(key)` | 读取键值 | `Promise<any>` |
| `kvSet(key, value)` | 写入键值 | `Promise<void>` |
| `kvDelete(key)` | 删除键值 | `Promise<void>` |

### 基本用法

```js
export function activate(ctx) {
  // 写入设置
  await ctx.storage.kvSet("theme", "dark");
  await ctx.storage.kvSet("playbackSpeed", 1.25);
  await ctx.storage.kvSet("recentSearches", ["周杰伦", "Taylor Swift"]);

  // 读取设置
  const theme = await ctx.storage.kvGet("theme");
  const recent = await ctx.storage.kvGet("recentSearches");

  console.log("主题：", theme);        // "dark"
  console.log("最近搜索：", recent);    // ["周杰伦", "Taylor Swift"]

  // 删除
  await ctx.storage.kvDelete("temp-cache");
}
```

### 最佳实践

```js
// ✅ 推荐：结构化存储
await ctx.storage.kvSet("settings", {
  theme: "dark",
  autoScroll: true,
  fontSize: 14,
});

// ✅ 推荐：使用版本号管理存储结构
await ctx.storage.kvSet("version", 2);
const currentVersion = (await ctx.storage.kvGet("version")) || 1;
if (currentVersion < 2) {
  // 迁移旧数据结构
}

// ⚠️ 注意：value 必须是 JSON 可序列化的
// 不能存储函数、Date 对象、Map、Set 等
```

### 生命周期

- 插件**卸载**时，该插件的所有 KV 数据会被**自动清除**
- 插件更新（升级版本）时，KV 数据保留
- 插件禁用后重新启用，KV 数据保留

---

## 播放队列持久化

`ctx.storage.playback*` 系列 API 用于操作持久化的播放队列。

| API | 说明 |
|-----|------|
| `playbackGetSnapshot()` | 获取当前播放状态快照 |
| `playbackGetQueue()` | 获取完整播放队列 |
| `playbackReplaceQueue(items)` | 替换整个队列 |
| `playbackAppendQueueItems(items)` | 追加歌曲到队尾 |
| `playbackRemoveQueueItem(songId)` | 移除队列中的歌曲 |
| `playbackReorderQueueItems(from, to)` | 重排歌曲位置 |
| `playbackSetCurrentTrack(songId)` | 设置当前播放曲目 |
| `playbackUpdateMeta(meta)` | 更新队列元数据（如队列名称） |

```js
// 保存当前播放状态
const snapshot = await ctx.storage.playbackGetSnapshot();
console.log("当前歌曲:", snapshot.currentTrack);

// 获取完整队列
const queue = await ctx.storage.playbackGetQueue();

// 添加歌曲并保持顺序
await ctx.storage.playbackAppendQueueItems([newTrack]);

// 将第 3 首移到第 1 首
await ctx.storage.playbackReorderQueueItems(2, 0);
```

> 与 `ctx.player.playlist.*` 的区别：`playback*` 是持久化的存储操作（重启后恢复），而 `ctx.player.playlist.*` 是运行时的播放队列操作。

---

## HTTP 请求

`ctx.api.request()` 提供统一的 HTTP 客户端。

```js
const result = await ctx.api.request({
  method: "GET",
  url: "https://api.example.com/data",
  params: { page: 1, limit: 20 },
  headers: {
    "X-Custom-Header": "value",
  },
});

console.log(result.data);

// POST 请求
await ctx.api.request({
  method: "POST",
  url: "https://api.example.com/submit",
  data: { name: "test", value: 123 },
});
```

| 参数 | 类型 | 必选 | 说明 |
|------|------|:--:|------|
| `method` | `string` | ✅ | HTTP 方法 |
| `url` | `string` | ✅ | 请求 URL |
| `params` | `object` | ❌ | URL 查询参数 |
| `data` | `any` | ❌ | 请求体数据 |
| `headers` | `Record<string, string>` | ❌ | 自定义请求头 |

---

## 事件监听

`ctx.events` 提供播放器核心事件订阅。

| API | 回调参数 | 说明 |
|-----|----------|------|
| `onTrackChange(fn)` | `(track) => void` | 歌曲切换 |
| `onPlayStateChange(fn)` | `(isPlaying) => void` | 播放/暂停状态 |
| `onVolumeChange(fn)` | `(volume) => void` | 音量变化 |

```js
export function activate(ctx) {
  ctx.events.onTrackChange((track) => {
    console.log(`🎵 正在播放：${track.title} - ${track.artist}`);
    updateNowPlaying(track);
  });

  ctx.events.onPlayStateChange((isPlaying) => {
    console.log(isPlaying ? "▶ 播放中" : "⏸ 已暂停");
  });

  ctx.events.onVolumeChange((volume) => {
    console.log(`🔊 音量：${volume}%`);
  });
}
```

- 通过 `ctx.events` 注册的监听器在**插件禁用/卸载时自动移除**
- 无需在 `deactivate()` 中手动取消监听

---

## 外观订阅

`ctx.appearance` 允许插件响应主题和外观变化。

| API | 说明 |
|-----|------|
| `getSnapshot()` | 获取当前外观快照 |
| `onSnapshot(fn)` | 订阅外观变化 |

### 外观快照结构

```js
const snapshot = await ctx.appearance.getSnapshot();
// {
//   themeColor: "#FF6B6B",        // 主题色
//   darkMode: true,               // 是否深色模式
//   fontFamily: "Microsoft YaHei", // 字体
//   fontSize: 14,                 // 字号
// }
```

### 响应主题变化

```js
export function activate(ctx) {
  async function updateTheme() {
    const { themeColor, darkMode } = await ctx.appearance.getSnapshot();
    document.documentElement.style.setProperty("--plugin-accent", themeColor);
    document.documentElement.style.setProperty("--plugin-bg",
      darkMode ? "#1a1a1a" : "#ffffff"
    );
  }

  updateTheme();

  ctx.appearance.onSnapshot((newTheme) => {
    document.documentElement.style.setProperty("--plugin-accent", newTheme.themeColor);
  });
}
```

> 使用 CSS 变量 `var(--theme-color)` 等宿主提供的变量，可以更简单地跟随主题变化，无需 JS 订阅。

---

## 完整示例：带存储的播放统计插件

```js
export function activate(ctx) {
  const STAT_KEY = "playStats";

  async function recordPlay(track) {
    const stats = (await ctx.storage.kvGet(STAT_KEY)) || {};
    const trackKey = `${track.id || track.title}`;

    stats[trackKey] = stats[trackKey] || {
      title: track.title,
      artist: track.artist,
      playCount: 0,
      lastPlayed: null,
    };

    stats[trackKey].playCount++;
    stats[trackKey].lastPlayed = new Date().toISOString();

    await ctx.storage.kvSet(STAT_KEY, stats);
  }

  async function showStats() {
    const stats = (await ctx.storage.kvGet(STAT_KEY)) || {};
    const entries = Object.values(stats)
      .sort((a, b) => b.playCount - a.playCount)
      .slice(0, 10);

    console.table(
      entries.map(e => ({
        歌曲: e.title,
        歌手: e.artist,
        播放次数: e.playCount,
        最后播放: e.lastPlayed?.slice(0, 10),
      }))
    );
  }

  // 每次切歌时记录
  ctx.events.onTrackChange(recordPlay);

  // 注册页面展示统计
  const { h } = ctx.vue;
  const StatsPage = ctx.vue.defineComponent({
    setup() {
      const { ref, onMounted } = ctx.vue;
      const topTracks = ref([]);

      onMounted(async () => {
        const stats = (await ctx.storage.kvGet(STAT_KEY)) || {};
        topTracks.value = Object.values(stats)
          .sort((a, b) => b.playCount - a.playCount)
          .slice(0, 20);
      });

      return () =>
        h("div", { class: "page-container" }, [
          h("h1", "📊 播放统计"),
          h("div", { class: "track-list" },
            topTracks.value.map(t =>
              h("div", { class: "track-item" }, [
                h("span", t.title),
                h("span", { style: "color: var(--color-text-secondary); margin-left: 8px;" },
                  `${t.playCount} 次`),
              ])
            )
          ),
        ]);
    },
  });

  ctx.ui.addPage({
    id: "play-stats",
    title: "播放统计",
    icon: "📊",
    component: StatsPage,
  });
}
```

---

## 下一步

| 文档 | 内容 |
|------|------|
| [播放器与音频引擎 →](./player-audio) | 播放控制、EQ、空间音效、歌词系统 |
| [窗口与系统 →](./windows-system) | 浮窗、桌面歌词、Mini 播放器 |
| [API 总览 →](./context-api) | ctx 完整 API 列表 |
