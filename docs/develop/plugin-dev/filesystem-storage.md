---
title: 文件存储与数据
outline: [2, 4]
---

# 📁 文件存储与数据

本文档介绍插件的文件系统访问、KV 存储和外观订阅。

> ℹ️ 播放队列持久化、HTTP 请求、核心事件监听等属于内部 API，不在插件范围内。详见 [内部 API 参考 →](../internal-api/)。

---

## 文件系统

> 需要 capability：`localFiles: true`（大部分操作）

`ctx.fs` 提供访问本地文件系统的能力。

### API

| 方法 | 说明 | 返回 |
|------|------|------|
| `listFiles(directory, opts?)` | 扫描目录，支持 `recursive`、`kinds`、`extensions`、`limit`、`maxDepth`、`includeHidden` | `Promise<{ok, files[]}>` |
| `listImageFiles(directory, opts?)` | 扫描图片文件 | `Promise<{ok, files[]}>` |
| `readTextFile(path, opts?)` | 读取文本文件，默认最大 1 MB | `Promise<{ok, text}>` |
| `readFileBytes(path, opts?)` | 读取二进制文件，默认最大 1 MB | `Promise<{ok, data}>` |
| `writeFile(path, data, opts?)` | 写入文件到插件目录，最大 8 MB | `Promise<{ok, path}>` |
| `deleteFile(path)` | 删除插件目录内文件 | `Promise<{ok}>` |
| `getFileUrl(path)` | 获取文件的 `file://` 播放 URL | `Promise<{ok, url}>` |

### 扫描本地音乐目录

```js
export async function activate(ctx) {
  const result = await ctx.fs.listFiles("C:\\Users\\User\\Music", {
    recursive: true,
    kinds: ["audio", "lyric", "image", "playlist", "cue"],
    limit: 5000,
  });

  if (result.ok) {
    console.log(`找到 ${result.files.length} 个文件`);
  }
}
```

### 播放本地文件

```js
async function playLocalFile(filePath) {
  const urlResult = await ctx.fs.getFileUrl(filePath);
  if (urlResult?.ok) {
    ctx.player.playTrack({
      id: filePath,
      title: filePath.split("\\").pop(),
      url: urlResult.url,
    });
  }
}
```

### 读取和写入文件

```js
// 读取文本文件
const textResult = await ctx.fs.readTextFile("C:\\logs\\app.log");

// 读取二进制文件的一部分
const bytesResult = await ctx.fs.readFileBytes("C:\\Data\\large.dat", {
  maxBytes: 1024,
});

// 写入配置到插件目录
const writeResult = await ctx.fs.writeFile("user-config.json", JSON.stringify({
  theme: "dark",
  fontSize: 14,
}, null, 2));

// 覆盖已有文件
await ctx.fs.writeFile("cache.json", data, { overwrite: true });

// 删除文件
await ctx.fs.deleteFile("old-cache.json");
```

> ⚠️ `writeFile` 和 `deleteFile` 只能操作**插件目录内**的文件（自动限制安全范围）。`readTextFile` / `readFileBytes` 可读取任意用户选定的路径。读取大音频文件请使用 `getFileUrl()`，不要通过 `readFileBytes()` 读取整段音频。

---

## KV 存储

`ctx.storage` 提供按插件隔离的持久化键值存储。

| API | 说明 | 返回 |
|-----|------|------|
| `get(key)` | 读取键值 | `Promise<any>` |
| `set(key, value)` | 写入键值 | `Promise<void>` |

### 基本用法

```js
export async function activate(ctx) {
  // 写入设置
  await ctx.storage.set("theme", "dark");
  await ctx.storage.set("playbackSpeed", 1.25);
  await ctx.storage.set("recentSearches", ["周杰伦", "Taylor Swift"]);

  // 读取设置（不存在时返回 undefined）
  const theme = (await ctx.storage.get("theme")) || "light";
  const recent = await ctx.storage.get("recentSearches");

  console.log("主题：", theme);        // "dark"
  console.log("最近搜索：", recent);    // ["周杰伦", "Taylor Swift"]
}
```

### 最佳实践

```js
// ✅ 推荐：结构化存储
await ctx.storage.set("settings", {
  theme: "dark",
  autoScroll: true,
  fontSize: 14,
});

// ✅ 推荐：使用版本号管理存储结构
const version = (await ctx.storage.get("version")) || 1;
if (version < 2) {
  // 迁移旧数据结构
  await ctx.storage.set("version", 2);
}

// ✅ 推荐：读取时提供默认值
const settings = (await ctx.storage.get("settings")) || defaults;

// ⚠️ 注意：value 必须是 JSON 可序列化的
// 不能存储函数、Date 对象、Map、Set、DOM 节点等
```

### 生命周期

- 插件**卸载**时，该插件的所有 KV 数据会被**自动清除**
- 插件更新（升级版本）时，KV 数据保留
- 插件禁用后重新启用，KV 数据保留

---

## SQLite 数据库

> 需要 capability：`sqlite: true`

`ctx.sqlite` 提供插件私有的 SQLite 数据库，由宿主创建并托管在 EchoMusic 的用户数据目录下，按插件 id 隔离。插件只能通过库名访问自己的数据库，不能传入任意本地路径。

### 打开数据库

```js
const db = await ctx.sqlite.open({
  name: "library",                        // 可选，默认 "main"
  migrations: [                           // 可选，版本迁移
    { version: 1, sql: `CREATE TABLE IF NOT EXISTS songs (
      id TEXT PRIMARY KEY,
      title TEXT NOT NULL,
      artist TEXT NOT NULL,
      play_count INTEGER DEFAULT 0
    )` },
    { version: 2, sql: `ALTER TABLE songs ADD COLUMN rating INTEGER DEFAULT 0` }
  ]
});
```

数据库名只能包含字母、数字、点、下划线和短横线，且必须以字母或数字开头。

### CRUD 操作

| API | 说明 |
|-----|------|
| `db.run(sql, params?)` | 执行 INSERT/UPDATE/DELETE，返回 `{ changes: n }` |
| `db.get(sql, params?)` | 查询一行，返回 `{ ok, row? }` 或 `null` |
| `db.all(sql, params?)` | 查询多行，返回 `{ ok, rows }` |
| `db.exec(sql)` | 执行任意 SQL（CREATE TABLE 等） |

```js
// 写入
await db.run("INSERT OR REPLACE INTO songs (id, title, artist, play_count) VALUES (?, ?, ?, ?)",
  ["1001", "晴天", "周杰伦", 42]);

// 查询单行
const row = await db.get("SELECT * FROM songs WHERE id = ?", ["1001"]);
console.log(row.row?.title); // "晴天"

// 查询多行
const list = await db.all("SELECT * FROM songs ORDER BY play_count DESC");
for (const item of list.rows) {
  console.log(item.title, item.play_count);
}
```

### 参数与 BLOB

参数支持 `string`、`number`、`boolean` 和 `null`。写入二进制使用对象包装：

```js
// 写入 BLOB（hex 或 base64 均可）
await db.run("INSERT INTO covers (id, data) VALUES (?, ?)", [
  "album-cover",
  { type: "base64", data: "iVBORw0KGgo=" }
]);

// 查询 BLOB，统一返回 hex 字符串
const row = await db.get("SELECT data FROM covers WHERE id = ?", ["album-cover"]);
console.log(row.row?.data); // { type: "hex", data: "89504e47..." }
```

### 事务

```js
await db.transaction([
  ["UPDATE songs SET play_count = play_count + 1 WHERE id = ?", ["1001"]],
  ["INSERT INTO play_log (song_id, time) VALUES (?, ?)", ["1001", Date.now()]]
]);
```

每个事务最多 500 条语句，单条 SQL 最长约 256 KB，单次查询最多 5000 行，结果 JSON 最大约 8 MB。

### 数据库管理

| API | 说明 |
|-----|------|
| `ctx.sqlite.listDatabases()` | 列出该插件的所有数据库名 |
| `ctx.sqlite.deleteDatabase(name?)` | 删除指定数据库（默认 `main`） |
| `db.close()` | 关闭当前连接 |

```js
const databases = await ctx.sqlite.listDatabases();
// ["main", "library", "cache"]

await ctx.sqlite.deleteDatabase("cache");
```

### 生命周期

- 插件安装后首次 `ctx.sqlite.open()` 时创建数据库文件
- 插件禁用、安全模式或 EchoMusic 退出时自动关闭连接
- 插件**卸载**时删除该插件的整个 SQLite 私有目录
- 插件更新（升级版本）时数据库保留
- 宿主拦截 `ATTACH`、`DETACH`、`VACUUM INTO`、`load_extension()` 等越界语句

---

## 外观订阅

`ctx.appearance` 允许插件响应主题和外观变化。

| API | 说明 |
|-----|------|
| `getSnapshot()` | 获取当前外观快照 |
| `onSnapshot(fn)` | 订阅外观变化，返回取消函数 |

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
export async function activate(ctx) {
  function applyTheme({ themeColor, darkMode }) {
    document.documentElement.style.setProperty("--plugin-accent", themeColor);
    document.documentElement.style.setProperty(
      "--plugin-bg",
      darkMode ? "#1a1a1a" : "#ffffff"
    );
  }

  applyTheme(await ctx.appearance.getSnapshot());

  ctx.appearance.onSnapshot(applyTheme);
}
```

---

## 主题 API

`ctx.theme` 提供对 EchoMusic 界面样式的深度定制。详见插件仓库 [README](https://github.com/hoowhoami/EchoMusicPlugins)。

### 表面样式（ctx.theme.surface）

```js
ctx.theme.surface.set({
  enabled: true,
  mainOpacity: 82,
  sidebarOpacity: 82,
  cardOpacity: 86,
  elevatedOpacity: 88,
  dialogOpacity: 90,
  playerOpacity: 92,
  backdropFilter: "blur(10px)",
  playerBackdropFilter: "blur(20px) saturate(180%)",
});
ctx.theme.surface.clear(); // 恢复默认
```

### 页面过渡动画（ctx.theme.pageTransition）

```js
ctx.theme.pageTransition.set({
  enabled: true,
  mode: "out-in",
  appear: true,
  durationMs: 450,
  easing: "ease-out",
  enterOpacity: 0,
  leaveOpacity: 0,
  enterTranslateY: 6,
});
ctx.theme.pageTransition.clear();
```

### 主题色渐变（ctx.theme.accentGradient）

```js
ctx.theme.accentGradient.set({
  color: "#ff5c8a",
  angle: 180,
  height: "46%",
  peakOpacity: 0.28,
  midOpacity: 0.1,
  dark: { peakOpacity: 0.4, midOpacity: 0.16 },
});
ctx.theme.accentGradient.clear();
```

---

## 滚动画布

`ctx.scroll` 提供页面滚动容器的高级控制。

| API | 说明 |
|-----|------|
| `queryContainers()` | 获取所有滚动容器 |
| `getCurrentContainer()` | 获取当前焦点容器 |
| `getState(el?)` | 获取滚动状态 |
| `scrollToTop(el?)` | 滚动到顶部 |
| `scrollToBottom(el?)` | 滚动到底部 |
| `observeContainers(handler)` | 监听滚动容器变化 |

---

## 完整示例：带存储的播放统计插件

```js
export async function activate(ctx) {
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

  // 通过 computed 监听切歌
  ctx.vue.watch(
    () => ctx.player.currentTrackId,
    (newId, oldId) => {
      if (newId && newId !== oldId) {
        recordPlay(ctx.player.currentTrack);
      }
    }
  );

  const { h, ref, onMounted } = ctx.vue;
  const StatsPage = ctx.vue.defineComponent({
    setup() {
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
          ...topTracks.value.map(t =>
            h("div", { class: "track-item" }, [
              h("span", t.title),
              h("span", { style: "color: var(--color-text-secondary); margin-left: 8px;" },
                `${t.playCount} 次`),
            ])
          ),
        ]);
    },
  });

  ctx.ui.addPage({
    id: "play-stats",
    title: "播放统计",
    component: StatsPage,
  });
}
```

---

## 下一步

| 文档 | 内容 |
|------|------|
| [播放器与音频引擎 →](./player-audio) | 播放控制、播放队列、频谱、歌词系统 |
| [窗口与系统 →](./windows-system) | 浮窗、Now Playing、进程、图标 |
| [API 总览 →](./context-api) | ctx 完整插件 API 列表 |
| [内部 API 参考 →](../internal-api/) | 内部 API（持久化/事件/HTTP 等） |
