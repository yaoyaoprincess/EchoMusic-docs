---
title: 播放器与音频引擎
outline: [2, 4]
---

# 🎵 播放器与音频引擎

插件可以与 EchoMusic 的播放系统深度集成。本文档涵盖播放控制、播放队列、自定义音源、歌词系统和音频频谱。

> ℹ️ mpv 引擎高级控制（EQ/空间音效/IR/设备/渐变/引擎事件等）属于内部 API，不在插件范围内。核心开发参考请见 [内部 API 参考 →](../internal-api/audio-engine)。

---

## 播放控制（ctx.player）

`ctx.player` 提供了操作播放器的完整 API。

### 播放状态（computed 属性，只读响应式）

| 属性 | 类型 | 说明 |
|------|:--:|------|
| `currentTrack` | `computed` | 当前正在播放的歌曲对象 |
| `currentTrackId` | `computed` | 当前歌曲 ID |
| `currentTime` | `computed` | 当前播放进度（秒） |
| `duration` | `computed` | 歌曲总时长（秒） |
| `isPlaying` | `computed` | 是否正在播放 |
| `playbackRate` | `computed` | 播放速率（0.5 / 0.75 / 1.0 / 1.25 / 1.5） |
| `volume` | `computed` | 音量（0-100） |
| `playMode` | `computed` | 播放模式 |

```js
export function activate(ctx) {
  // 响应式监听播放进度
  ctx.vue.watch(
    () => ctx.player.currentTime,
    (time) => {
      if (Math.floor(time) % 10 === 0) {
        console.log(`已播放 ${Math.floor(time)} 秒`);
      }
    }
  );

  // 监听歌曲切换
  ctx.vue.watch(
    () => ctx.player.currentTrackId,
    (newId, oldId) => {
      if (newId !== oldId) {
        console.log("歌曲已切换：", ctx.player.currentTrack?.title);
      }
    }
  );
}
```

### 播放控制（函数）

| 方法 | 说明 |
|------|------|
| `play()` | 开始播放 |
| `pause()` | 暂停播放 |
| `toggle()` | 播放 / 暂停切换 |
| `prev()` | 上一首 |
| `next()` | 下一首 |
| `stop()` | 停止播放 |
| `seek(time)` | 跳转到指定时间（秒） |
| `setVolume(vol)` | 设置音量（0-100） |
| `setPlaybackRate(rate)` | 设置播放速率（0.5-3.0） |
| `setPlayMode(mode)` | 设置播放模式 |
| `setAudioQuality(q)` | 设置音频品质 |
| `setAudioEffect(e)` | 设置音效 |
| `playTrack(track)` | 播放指定歌曲 |
| `playNext()` | 播放下一首（跳过队列） |
| `playLast()` | 播放上一首 |
| `replaceQueueAndPlay(items)` | 替换队列并播放 |
| `dislikePersonalFm()` | 私人 FM 点"不喜欢" |
| `toggleLyricView(open?)` | 切换歌词视图 |

```js
// 5 秒后跳转到副歌
ctx.player.seek(90);

// 设置音量和速率
ctx.player.setVolume(80);
ctx.player.setPlaybackRate(1.0);

// 循环模式
ctx.player.setPlayMode("loop");

// 播放指定歌曲
ctx.player.playTrack({ id: "song_001", title: "歌名", url: "..." });
```

---

## 播放队列管理

`ctx.playlist` 提供对播放队列的完整控制。

| API | 说明 |
|-----|------|
| `getQueue()` | 获取当前播放队列列表 |
| `addTrack(track)` | 添加歌曲到队尾 |
| `removeTrack(songId)` | 移除指定歌曲 |
| `clear()` | 清空队列 |
| `replaceQueue(items)` | 替换整个队列 |
| `reorder(from, to)` | 重排歌曲位置 |
| `playNext(track)` | 插播（下一首优先播放） |

```js
// 追加歌曲到队列
ctx.playlist.addTrack({ id: "001", title: "歌名", artist: "歌手" });

// 插播（下一首播放）
ctx.playlist.playNext({ id: "urgent", title: "紧急插播" });

// 清空后替换
ctx.playlist.clear();
ctx.playlist.replaceQueue(recommendedSongs);
```

---

## 音频频谱

> 需要 capability：`audioSpectrum: true`

`ctx.audio.spectrum` 提供实时 FFT 频谱数据。

| API | 说明 | 详见 |
|-----|------|:--:|
| `getStatus()` | 获取捕获状态 | [音频频谱 →](./audio-spectrum) |
| `getSnapshot()` | 单帧频谱快照 | [音频频谱 →](./audio-spectrum) |
| `subscribe(opts, cb)` | 实时订阅频谱数据 | [音频频谱 →](./audio-spectrum) |

---

## 歌词系统

### 读取歌词状态

```js
// ctx.lyric 等价于 ctx.stores.lyric
const currentLine = ctx.lyric.currentLine;   // 当前高亮的歌词行
const allLines = ctx.lyric.lines;            // 所有歌词行
const timeOffset = ctx.lyric.timeOffset;     // 时间偏移（秒）
```

### 注册歌词解析器

> 需要 capability：`lyrics: true`

```js
ctx.lyrics.registerResolver({
  id: "my-lyrics-source",        // 解析器唯一 ID
  name: "我的歌词源",             // 显示名称
  order: 200,                    // 优先级（越大越先使用）
  match({ track }) {             // 是否匹配此歌曲
    return Boolean(track?.hash);
  },
  async resolve({ track }) {
    const result = await fetchLyricsFromMySource(track);
    return result?.lyric || null; // 返回 LRC 格式或 null（无法处理）
  },
});
```

| 参数 | 类型 | 必选 | 说明 |
|------|------|:--:|------|
| `id` | `string` | ✅ | 解析器唯一 ID |
| `name` | `string` | ✅ | 显示名称 |
| `order` | `number` | ❌ | 优先级，越大越优先 |
| `match({track})` | `function` | ❌ | 判断是否匹配 |
| `resolve({track})` | `async function` | ✅ | 返回 `{ source, lyric }` 或 null |

> `resolve` 返回 `null` 表示无法处理该歌曲，EchoMusic 会尝试下一个解析器。

### 获取/订阅歌词快照

```js
const snapshot = ctx.lyrics.getSnapshot();
console.log(snapshot.currentLine, snapshot.lines);

ctx.lyrics.onSnapshot((snapshot) => {
  console.log("歌词更新：", snapshot.currentLine);
});
```

### 发送命令

```js
ctx.lyrics.command("scrollDown");
ctx.lyrics.command("scrollUp");
```

---

## 歌词视觉效果

> 需要 capability：`lyricEffects: true`

注册自定义歌词视觉动效。详见 [EchoMusicPlugins docs/windows.md](https://github.com/hoowhoami/EchoMusicPlugins/blob/main/docs/windows.md)。

```js
ctx.lyricEffects.register({
  id: "water",
  title: "水波歌词",
  scope: "page",
  layer: "decorator",
  className: "my-water-lyrics",
  css: `.my-water-lyrics [data-echo-lyric-line] { font-style: italic; }`,
  mount(host) {
    // 可选：创建装饰层（SVG / Canvas）
    return () => { /* 清理 */ };
  },
});
```

| 参数 | 类型 | 必选 | 说明 |
|------|------|:--:|------|
| `id` | `string` | ✅ | 动效唯一 ID |
| `title` | `string` | ✅ | 显示名称 |
| `scope` | `string` | ✅ | 当前支持 `"page"`（页面歌词） |
| `layer` | `string` | ❌ | `"style"` 或 `"decorator"` |
| `className` | `string` | ❌ | 注入到 host 节点的 CSS class |
| `css` | `string` | ❌ | 注入的全局 CSS |
| `mount(host)` | `function` | ❌ | host 挂载时调用，返回清理函数 |

---

## 自定义音源

> 需要 capability：`audioSource: true`

接管特定平台或特定歌曲的音源解析：

```js
ctx.player.audioSource.register({
  id: "webdav-audio",
  name: "WebDAV 音源",
  order: 100,
  async resolve({ songId }) {
    const url = await resolveWebDAVUrl(songId);
    return url ? { url } : null;
  },
});
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | `string` | 解析器唯一 ID |
| `name` | `string` | 显示名称 |
| `order` | `number` | 优先级 |
| `resolve({ songId })` | `async` | 返回 `{ url }` 或 null |

---

## 下一步

| 文档 | 内容 |
|------|------|
| [音频频谱 →](./audio-spectrum) | 实时 FFT 频谱数据订阅与可视化 |
| [文件存储与数据 →](./filesystem-storage) | 文件系统、KV 存储、外观订阅 |
| [窗口与系统 →](./windows-system) | 浮窗、Now Playing、进程、图标 |
| [API 总览 →](./context-api) | ctx 完整插件 API 速查 |
| [内部 API 参考 →](../internal-api/) | 内部 API（mpv 引擎/桌面歌词等） |
