---
title: 播放器与音频引擎
outline: [2, 4]
---

# 🎵 播放器与音频引擎

插件可以与 EchoMusic 的播放系统和底层 mpv 音频引擎深度集成。本文档涵盖播放控制、播放队列、音频引擎高级控制、音频事件、歌词系统和自定义音源。

---

## 播放控制（ctx.player）

`ctx.player` 提供了操作播放器的便捷 API。

### 播放状态（computed 属性，只读）

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
| `setSpeed(speed)` | 设置播放速率（0.5-3.0） |
| `setPlayMode(mode)` | 设置播放模式 |
| `setAudioQuality(q)` | 设置音频品质 |
| `setAudioEffect(e)` | 设置音效 |

```js
// 5 秒后跳转到副歌
ctx.player.seek(90);

// 设置音量和速率
ctx.player.setVolume(80);
ctx.player.setSpeed(1.0);

// 循环模式
ctx.player.setPlayMode("loop");
```

---

## 播放队列管理

`ctx.player.playlist` 提供对播放队列的完整控制。

| API | 说明 |
|-----|------|
| `getQueue()` | 获取当前播放队列列表 |
| `append(items)` | 追加歌曲到队尾 |
| `remove(songId)` | 移除指定歌曲 |
| `clear()` | 清空队列 |
| `replace(items)` | 替换整个队列 |
| `reorder(from, to)` | 重排歌曲位置 |
| `setCurrentTrack(songId)` | 切到指定歌曲 |

```js
// 追加歌曲到队列
ctx.player.playlist.append([song1, song2]);

// 清空后替换
ctx.player.playlist.clear();
ctx.player.playlist.replace(recommendedSongs);

// 切换到第 5 首
const queue = ctx.player.playlist.getQueue();
ctx.player.playlist.setCurrentTrack(queue[4].id);
```

---

## 音频引擎高级控制（ctx.audio）

EchoMusic 底层使用 **libmpv** 作为音频引擎，插件可以通过 `ctx.audio` 访问其高级功能。

### 均衡器（EQ）

18 段参数化均衡器，每段独立控制增益。

```js
// 获取/设置 18 段 EQ（-12 到 +12 dB）
ctx.audio.setEqualizer([
  0,   // 32 Hz
  2,   // 64 Hz
  3,   // 125 Hz
  1,   // 250 Hz
  0,   // 500 Hz
  -1,  // 1 kHz
  0,   // 2 kHz
  2,   // 4 kHz
  1,   // 8 kHz
  0,   // 16 kHz
]);
```

| 参数 | 类型 | 范围 | 说明 |
|------|------|------|------|
| `gains` | `number[]` | `[-12, 12]` dB | 每段只的增益值 |

EQ 频段对应关系：
`32 / 64 / 125 / 250 / 500 / 1k / 2k / 4k / 8k / 16k` Hz

### 空间音效（Spatial Audio）

```js
// 设置空间音效
ctx.audio.setSpatialAudio({
  preset: "hall",   // "hall" | "church" | "studio" | "theater"
  dryWet: 0.5,      // 干湿比 (0.0 = 纯原声, 1.0 = 纯效果)
});

// 关闭空间音效
ctx.audio.setSpatialAudio({ preset: null });
```

### 脉冲响应（IR Convolution）

```js
// 使用已导入的 IR 文件
ctx.audio.setImpulseResponse({
  path: "path/to/ir-file.wav",
  dryWet: 0.6,
});

// 或直接传路径字符串（使用默认干湿比）
ctx.audio.setImpulseResponse("path/to/ir-file.wav");
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `path` | `string` | IR 音频文件的绝对路径 |
| `dryWet` | `number`（0-1）| 干湿混合比 |

### 音频设备控制

```js
// 获取所有音频设备
const devices = await ctx.audio.getAudioDevices();
// [{ name: "Speakers", description: "Realtek Audio" }, ...]

// 切换到指定设备
await ctx.audio.setAudioDevice("Speakers");

// 独占模式（绕过系统混音器）
await ctx.audio.setExclusive(true);
```

| API | 说明 |
|-----|------|
| `getAudioDevices()` | 获取可用音频设备列表 |
| `setAudioDevice(name)` | 切换音频输出设备 |
| `setExclusive(bool)` | 独占模式开关 |
| `getAudioFilter()` | 获取当前生效的音效滤波器名 |

### 音量渐变（Fade）

```js
// 从当前音量渐变到 30，持续 2000ms
ctx.audio.fade(ctx.player.volume, 30, 2000);

// 取消正在进行的渐变
ctx.audio.cancelFade();

// 带渐变的暂停（先降音量再暂停）
ctx.audio.pauseWithFade(20, 1500);

// 带渐变的播放（先启动再升音量）
ctx.audio.playWithFade(currentVolume, 1000);
```

| API | 说明 |
|-----|------|
| `fade(from, to, durationMs)` | 从 `from` 渐变到 `to`，持续 `durationMs` 毫秒 |
| `cancelFade()` | 取消渐变 |
| `pauseWithFade(savedVol, durationMs)` | 渐弱暂停 |
| `playWithFade(targetVol, durationMs)` | 渐强恢复 |

### 响度归一化

```js
// 设置归一化增益
ctx.audio.setNormalizationGain(-3.5); // dB
```

### 文件和循环

```js
// 加载音频文件
ctx.audio.loadFile("file:///C:/Music/song.flac");
ctx.audio.loadFile("file:///path/to/video.mkv", 2); // MKV 的第 2 个音轨

// 获取 MKV 轨道列表
const tracks = await ctx.audio.getTrackList();

// 单曲循环
ctx.audio.setLoopFile(true);

// 设置媒体标题
ctx.audio.setMediaTitle("Custom Title");
```

### 引擎控制

| API | 说明 |
|-----|------|
| `available()` | 检查 mpv 引擎是否可用 |
| `restart()` | 重启播放引擎 |
| `getState()` | 获取引擎内部状态 |

---

## 音频事件

`ctx.audio` 提供丰富的播放事件监听，全部返回取消函数。

### 核心事件

| API | 回调参数 | 说明 |
|-----|----------|------|
| `onTimeUpdate(fn)` | `(time: number)` | 播放时间更新（秒） |
| `onDurationChange(fn)` | `(duration: number)` | 歌曲时长变化 |
| `onStateChange(fn)` | `(state: {playing?, paused?})` | 播放/暂停状态变化 |
| `onPlaybackEnd(fn)` | `(reason: string)` | 播放结束（"eof"/"stop"/"error"） |
| `onError(fn)` | `(message: string)` | mpv 引擎错误 |

```js
export function activate(ctx) {
  // 跟踪播放进度
  ctx.audio.onTimeUpdate((time) => {
    document.getElementById("progress").style.width =
      `${(time / ctx.player.duration) * 100}%`;
  });

  // 播放结束时自动下一首
  ctx.audio.onPlaybackEnd((reason) => {
    if (reason === "eof") {
      console.log("歌曲播放完毕");
    }
  });

  // mpv 错误
  ctx.audio.onError((msg) => {
    ctx.toast.error("播放引擎错误：" + msg);
  });
}
```

### 设备事件

| API | 回调参数 | 说明 |
|-----|----------|------|
| `onAudioDeviceListChanged(fn)` | `(devices: AudioDevice[])` | 音频设备列表变化（拔插耳机等） |
| `onImpulseResponseDisabled(fn)` | `(payload: {path?, reason?})` | IR 音效被自动禁用时通知 |

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
  priority: 50,                  // 优先级（越高越先使用）
  async resolve(song) {
    // song = { id, title, artist, album, ... }
    const lyrics = await fetchLyricsFromMySource(song);
    return lyrics;               // 返回 LRC 格式或纯文本
  },
});
```

| 参数 | 类型 | 必选 | 说明 |
|------|------|:--:|------|
| `id` | `string` | ✅ | 解析器唯一 ID |
| `name` | `string` | ✅ | 显示名称 |
| `priority` | `number` | ❌ | 优先级，默认 0 |
| `resolve(song)` | `function` | ✅ | 返回歌词字符串或 null |

> `resolve` 返回 `null` 表示无法处理该歌曲，EchoMusic 会尝试下一个解析器。

### 获取/订阅歌词快照

```js
const snapshot = ctx.lyrics.getSnapshot();
console.log(snapshot.currentLine, snapshot.lines);

ctx.lyrics.onSnapshot((snapshot) => {
  console.log("歌词更新：", snapshot.currentLine);
});
```

---

## 歌词视觉效果

> 需要 capability：`lyricEffects: true`

注册自定义歌词视觉动效：

```js
ctx.lyricEffects.register({
  id: "my-bounce-effect",
  name: "弹跳歌词",
  cssClass: "bounce-lyric",    // 注入到每行歌词的 CSS class
  overlay: MyOverlayComponent, // 可选：歌词区域的装饰层组件
});
```

| 参数 | 类型 | 必选 | 说明 |
|------|------|:--:|------|
| `id` | `string` | ✅ | 动效唯一 ID |
| `name` | `string` | ✅ | 显示名称 |
| `cssClass` | `string` | ❌ | 注入到歌词行的 CSS class |
| `overlay` | `Component` | ❌ | 歌词区域的装饰层组件 |

### CSS 动效示例

```css
/* 随 style.css 一起注入 */
.bounce-lyric {
  animation: bounce 0.3s ease-out;
}

@keyframes bounce {
  0%   { transform: scale(1); }
  50%  { transform: scale(1.08); }
  100% { transform: scale(1); }
}
```

---

## 自定义音源

> 需要 capability：`audioSource: true`

接管特定平台或特定歌曲的音源解析：

```js
ctx.player.audioSource.register({
  platform: "my-platform",
  async resolve(songId) {
    const response = await fetch(`https://api.example.com/song/${songId}`);
    const data = await response.json();
    return { url: data.streamUrl };
  },
});
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `platform` | `string` | 平台标识 |
| `resolve(songId)` | `(songId: string) => Promise<{url}>` | 解析音源 URL |

---

## 下一步

| 文档 | 内容 |
|------|------|
| [音频频谱 →](./audio-spectrum) | 实时 FFT 频谱数据订阅与可视化 |
| [文件存储与数据 →](./filesystem-storage) | 文件系统、KV 存储、播放队列持久化 |
| [窗口与系统 →](./windows-system) | 浮窗、桌面歌词、Mini 播放器 |
| [API 总览 →](./context-api) | ctx 完整 ~120 个 API 速查 |
