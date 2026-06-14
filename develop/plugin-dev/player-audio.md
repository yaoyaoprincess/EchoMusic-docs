---
title: 播放器与音频
outline: [2, 4]
---

# 🎵 播放器与音频

插件可以与 EchoMusic 的播放器和音频系统深度集成。本文档涵盖播放控制、音频频谱和歌词系统。

## 播放器控制

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
      // 每秒触发（取决于播放器的更新频率）
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
| `playTrack(track)` | 播放指定歌曲 |
| `toggle()` | 播放 / 暂停切换 |
| `stop()` | 停止播放 |
| `next()` | 下一首 |
| `prev()` | 上一首 |
| `seek(time)` | 跳转到指定时间（秒） |
| `setVolume(vol)` | 设置音量（0-100） |
| `setPlaybackRate(rate)` | 设置播放速率 |
| `setPlayMode(mode)` | 设置播放模式 |
| `setAudioQuality(q)` | 设置音频品质 |
| `setAudioEffect(e)` | 设置音效 |

```js
// 搜索并播放歌曲
async function searchAndPlay(keyword) {
  const results = await ctx.kugou.search(keyword);
  if (results.length > 0) {
    ctx.player.playTrack(results[0]);
    ctx.toast.info(`正在播放：${results[0].title}`);
  }
}

// 5 秒后跳转到副歌
ctx.player.seek(90);

// 设置音量和速率
ctx.player.setVolume(80);
ctx.player.setPlaybackRate(1.0);
```

### playTrack 参数格式

```js
ctx.player.playTrack({
  id: "song_hash_or_id",    // 歌曲唯一标识
  title: "歌曲名称",
  artist: "歌手",
  album: "专辑",
  // ... 其他字段
});
```

---

## 音频频谱

> 需要 capability：`audioSpectrum: true`

`ctx.audio.spectrum` 提供音频频谱数据的访问。

### API

| 方法 | 说明 |
|------|------|
| `getStatus()` | 获取频谱捕获状态 |
| `getSnapshot()` | 获取当前频谱快照 |
| `subscribe(options, handler)` | 订阅实时频谱数据 |

### subscribe 选项

```js
ctx.audio.spectrum.subscribe(
  {
    fftSize: 2048,       // FFT 窗口大小，必须是 2 的幂（32-32768）
    smoothingTimeConstant: 0.8,  // 平滑系数（0-1）
    interval: 50,        // 数据推送间隔（毫秒）
  },
  (data) => {
    // data 结构：
    // {
    //   frequencyData: Float32Array,  // 频域数据
    //   timeData: Float32Array,       // 时域数据
    //   sampleRate: number,           // 采样率
    // }
    updateVisualizer(data.frequencyData);
  }
);
```

### 完整示例：频谱可视化器

```js
export function activate(ctx) {
  // 创建一个 Canvas 用于绘制频谱
  const canvas = document.createElement("canvas");
  canvas.width = 300;
  canvas.height = 100;
  canvas.style.cssText = "position: fixed; bottom: 60px; right: 20px; z-index: 9999; border-radius: 8px; background: rgba(0,0,0,0.6);";
  document.body.appendChild(canvas);

  const ctx2d = canvas.getContext("2d");

  ctx.audio.spectrum.subscribe(
    { fftSize: 256, interval: 50 },
    (data) => {
      const { frequencyData } = data;
      const width = canvas.width;
      const height = canvas.height;
      const barWidth = width / frequencyData.length;

      ctx2d.clearRect(0, 0, width, height);

      for (let i = 0; i < frequencyData.length; i++) {
        const barHeight = frequencyData[i] * height;
        const x = i * barWidth;
        const hue = (i / frequencyData.length) * 120 + 200;

        ctx2d.fillStyle = `hsl(${hue}, 80%, 60%)`;
        ctx2d.fillRect(x, height - barHeight, barWidth - 1, barHeight);
      }
    }
  );

  // 清理
  ctx.dispose(() => {
    canvas.remove();
  });
}
```

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
    // 返回歌词文本（LRC 格式或纯文本）
    const lyrics = await fetchLyricsFromMySource(song);
    return lyrics;
  },
});
```

#### 参数

| 参数 | 类型 | 必选 | 说明 |
|------|------|:--:|------|
| `id` | `string` | ✅ | 解析器唯一 ID |
| `name` | `string` | ✅ | 显示名称 |
| `priority` | `number` | ❌ | 优先级，默认 0 |
| `resolve(song)` | `function` | ✅ | 返回歌词字符串或 null |

> `resolve` 返回 `null` 表示无法处理该歌曲，EchoMusic 会尝试下一个解析器。

### 获取/订阅歌词快照

```js
// 获取当前歌词快照
const snapshot = ctx.lyrics.getSnapshot();
console.log(snapshot.currentLine, snapshot.lines);

// 订阅歌词变化
ctx.lyrics.onSnapshot((snapshot) => {
  console.log("歌词更新：", snapshot.currentLine);
});
```

---

## 歌词视觉效果

> 需要 capability：`lyricEffects: true`

注册自定义歌词视觉动效，用于在歌词显示区域叠加动画或特效。

```js
ctx.lyricEffects.register({
  id: "my-bounce-effect",
  name: "弹跳歌词",
  cssClass: "bounce-lyric",    // 注入到每行歌词的 CSS class
  overlay: MyOverlayComponent, // 可选：歌词区域的装饰层组件
});
```

#### 参数

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

## 下一步

| 文档 | 内容 |
|------|------|
| [文件存储与事件 →](./filesystem-events) | 本地文件读写、KV 存储、事件监听 |
| [UI 扩展指南 →](./ui-extension) | 页面、设置面板、右键菜单 |
| [发布与分发 →](./publishing) | 发布插件到在线插件源 |
