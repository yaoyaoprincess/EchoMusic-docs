---
title: 文件存储与事件
outline: [2, 4]
---

# 📁 文件存储与事件

本文档介绍插件的文件系统访问、KV 存储、事件监听和外观订阅。

## 文件系统

> 需要 capability：`localFiles: true`

`ctx.fs` 提供访问本地文件系统的能力。

### API

| 方法 | 说明 | 返回 |
|------|------|------|
| `listFiles(dir)` | 扫描目录，返回文件列表 | `Promise<FileEntry[]>` |
| `readTextFile(path)` | 读取文本文件内容 | `Promise<string>` |
| `readFileBytes(path)` | 读取二进制文件 | `Promise<ArrayBuffer>` |
| `getFileUrl(path)` | 获取文件的 URL（用于播放） | `Promise<string>` |
| `writeFile(relativePath, content)` | 写入插件目录内文件 | `Promise<void>` |

### 扫描本地音乐目录

```js
export function activate(ctx) {
  // 扫描下载目录中的音频文件
  async function scanMusicDir() {
    try {
      const files = await ctx.fs.listFiles("C:\\Users\\User\\Music");
      const audioFiles = files.filter(f =>
        f.name.endsWith(".mp3") || f.name.endsWith(".flac") || f.name.endsWith(".wav")
      );
      console.log(`找到 ${audioFiles.length} 个音频文件`);
      return audioFiles;
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
  // url 是一个可播放的 file:// 或 blob:// URL
  ctx.player.playTrack({
    id: filePath,
    title: filePath.split("\\").pop(),
    url: url,
  });
}
```

### 写入插件数据

```js
// 写入配置到插件目录
await ctx.fs.writeFile("user-config.json", JSON.stringify({
  theme: "dark",
  fontSize: 14,
}, null, 2));
```

> ⚠️ `writeFile` 只能写入**插件目录内**的文件。不能写入外部路径。

---

## KV 存储

`ctx.storage` 提供一个简单的键值存储，数据持久化且按插件隔离。

| 方法 | 说明 | 返回 |
|------|------|------|
| `get(key)` | 读取键值 | `Promise<any>` |
| `set(key, value)` | 写入键值 | `Promise<void>` |

### 基本用法

```js
export function activate(ctx) {
  // 写入设置
  await ctx.storage.set("theme", "dark");
  await ctx.storage.set("playbackSpeed", 1.25);
  await ctx.storage.set("recentSearches", ["周杰伦", "Taylor Swift"]);

  // 读取设置
  const theme = await ctx.storage.get("theme");
  const recent = await ctx.storage.get("recentSearches");

  console.log("主题：", theme);        // "dark"
  console.log("最近搜索：", recent);    // ["周杰伦", "Taylor Swift"]
}
```

### 使用场景

| 场景 | 示例 |
|------|------|
| 用户设置 | 按钮开关状态、字体大小、颜色偏好 |
| 缓存数据 | 搜索结果、歌曲元数据、自定义歌单 |
| 插件状态 | 是否首次运行、功能开关 |

### 最佳实践

```js
// ✅ 推荐：结构化存储
await ctx.storage.set("settings", {
  theme: "dark",
  autoScroll: true,
  fontSize: 14,
});

// ✅ 推荐：使用版本号管理存储结构
await ctx.storage.set("version", 2);
const currentVersion = await ctx.storage.get("version") || 1;

// ⚠️ 注意：value 必须是 JSON 可序列化的
// 不能存储函数、Date 对象、Map、Set 等
```

---

## 事件监听

`ctx.events` 提供播放器核心事件的订阅。

| API | 参数 | 说明 |
|-----|------|------|
| `onTrackChange(handler)` | `(track) => void` | 歌曲切换时触发 |
| `onPlayStateChange(handler)` | `(isPlaying) => void` | 播放/暂停状态变化 |
| `onVolumeChange(handler)` | `(volume) => void` | 音量变化时触发 |

### 使用示例

```js
export function activate(ctx) {
  // 歌曲切换
  ctx.events.onTrackChange((track) => {
    console.log(`🎵 正在播放：${track.title} - ${track.artist}`);
    // 更新自定义 UI
    updateNowPlaying(track);
  });

  // 播放状态变化
  ctx.events.onPlayStateChange((isPlaying) => {
    console.log(isPlaying ? "▶ 播放中" : "⏸ 已暂停");
  });

  // 音量变化
  ctx.events.onVolumeChange((volume) => {
    console.log(`🔊 音量：${volume}%`);
  });
}
```

### 事件生命周期

- 通过 `ctx.events` 注册的监听器在**插件禁用/卸载时自动移除**
- 无需在 `deactivate()` 中手动取消监听

---

## 外观订阅

`ctx.appearance` 允许插件响应主题和外观变化。

| API | 说明 |
|-----|------|
| `getSnapshot()` | 获取当前外观快照 |
| `onSnapshot(handler)` | 订阅外观变化 |

### 外观快照结构

```js
const snapshot = await ctx.appearance.getSnapshot();
// {
//   themeColor: "#FF6B6B",     // 主题色
//   darkMode: true,            // 是否深色模式
//   fontFamily: "Microsoft YaHei", // 字体
//   fontSize: 14,              // 字号
// }
```

### 响应主题变化

```js
export function activate(ctx) {
  async function updateTheme() {
    const { themeColor, darkMode } = await ctx.appearance.getSnapshot();
    // 调整插件 UI 的颜色
    document.documentElement.style.setProperty("--plugin-accent", themeColor);
    document.documentElement.style.setProperty("--plugin-bg", darkMode ? "#1a1a1a" : "#ffffff");
  }

  // 初始应用
  updateTheme();

  // 订阅变化
  ctx.appearance.onSnapshot((newTheme) => {
    document.documentElement.style.setProperty("--plugin-accent", newTheme.themeColor);
    document.documentElement.style.setProperty("--plugin-bg", newTheme.darkMode ? "#1a1a1a" : "#ffffff");
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
    const stats = (await ctx.storage.get(STAT_KEY)) || {};
    const trackKey = `${track.id || track.title}`;

    stats[trackKey] = stats[trackKey] || {
      title: track.title,
      artist: track.artist,
      playCount: 0,
      lastPlayed: null,
    };

    stats[trackKey].playCount++;
    stats[trackKey].lastPlayed = new Date().toISOString();

    await ctx.storage.set(STAT_KEY, stats);
  }

  async function showStats() {
    const stats = (await ctx.storage.get(STAT_KEY)) || {};
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
        const stats = (await ctx.storage.get(STAT_KEY)) || {};
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
                h("span", { style: "color: var(--color-text-secondary); margin-left: 8px;" }, `${t.playCount} 次`),
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
| [发布与分发 →](./publishing) | 将插件发布到在线插件源 |
| [播放器与音频 →](./player-audio) | 播放控制、频谱、歌词系统 |
| [插件开发概览 →](./) | 返回插件开发总览 |
