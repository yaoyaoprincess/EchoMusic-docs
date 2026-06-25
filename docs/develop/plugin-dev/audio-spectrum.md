---
title: 音频频谱
outline: [2, 4]
---

# 📊 音频频谱

> 需要 capability：`audioSpectrum: true`

`ctx.audio.spectrum` 提供对 EchoMusic 实时音频频谱数据的访问。底层由 `echo-spectrum-capture` native addon 驱动，从系统音频输出捕获 FFT 数据。

## API 概览

| API | 说明 | 返回 |
|-----|------|------|
| `getStatus()` | 获取频谱捕获状态 | `Promise<AudioSpectrumStatus>` |
| `getSnapshot()` | 获取当前单帧频谱数据 | `Promise<AudioSpectrumFrame \| null>` |
| `subscribe(options, handler, meta?)` | 订阅实时频谱数据流 | `() => void`（取消函数） |

---

## getStatus()

获取频谱捕获引擎的当前状态。

```js
const status = await ctx.audio.spectrum.getStatus();
// {
//   capturing: true,      // 是否正在捕获
//   sampleRate: 44100,    // 当前采样率
//   fftSize: 2048,        // 当前 FFT 窗口大小
//   subscriptions: 2,     // 活跃订阅数
// }
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `capturing` | `boolean` | 频谱捕获是否处于活动状态 |
| `sampleRate` | `number` | 音频采样率（Hz） |
| `fftSize` | `number` | FFT 变换窗口大小 |
| `subscriptions` | `number` | 当前活跃的订阅数 |

---

## getSnapshot()

获取一帧即时的频谱数据。如果频谱捕获未启动，返回 `null`。

```js
const frame = await ctx.audio.spectrum.getSnapshot();
if (frame) {
  // frame.frequencyData: Float32Array — 频域数据
  // frame.timeData: Float32Array      — 时域数据
  // frame.sampleRate: number          — 采样率
  console.log("频域数据长度:", frame.frequencyData.length);
}
```

**适用场景：** 只需要偶尔读取频谱数据（如制作截图表），而不是持续实时更新。

---

## subscribe(options, handler)

订阅实时频谱数据。每当系统捕获到新一帧频谱时，会调用 `handler`。

### 参数

| 参数 | 类型 | 必选 | 说明 |
|------|------|:--:|------|
| `options.fftSize` | `number` | ❌ | FFT 窗口大小（32-32768，必须是 2 的幂），默认 2048 |
| `options.smoothingTimeConstant` | `number` | ❌ | 平滑系数（0-1），默认 0.8。值越小响应越快 |
| `options.interval` | `number` | ❌ | 数据推送最小间隔（ms），默认 50 |
| `handler` | `(frame) => void` | ✅ | 频谱数据回调 |
| `meta.pluginId` | `string` | ❌ | 订阅者标识，默认自动填充当前插件 ID |

### 频谱帧结构（AudioSpectrumFrame）

```ts
interface AudioSpectrumFrame {
  frequencyData: Float32Array;  // 频域数据（长度 = fftSize / 2）
  timeData: Float32Array;       // 时域数据（长度 = fftSize）
  sampleRate: number;           // 采样率（Hz）
}
```

| 字段 | 说明 |
|------|------|
| `frequencyData` | `[0, fftSize/2)` — 每个 bin 代表一段频率区间的幅度（非 dB，线性值 0-1） |
| `timeData` | `[0, fftSize)` — 原始 PCM 波形采样值 |
| `sampleRate` | 实际捕获的音频采样率 |

### 返回值

`subscribe()` 返回一个**取消函数**。调用它即可停止此订阅。插件禁用/卸载时也会自动取消所有订阅：

```js
const unsubscribe = ctx.audio.spectrum.subscribe(
  { fftSize: 1024, interval: 30 },
  (frame) => {
    drawBars(frame.frequencyData);
  }
);

// 稍后手动取消
unsubscribe();
```

### 按需启停频谱捕获

为避免不必要的性能开销，建议在播放时才订阅频谱：

```js
export function activate(ctx) {
  let unsubscribe = null;

  ctx.events.onPlayStateChange((isPlaying) => {
    if (isPlaying && !unsubscribe) {
      unsubscribe = ctx.audio.spectrum.subscribe(
        { fftSize: 2048 },
        (frame) => renderSpectrum(frame)
      );
    } else if (!isPlaying && unsubscribe) {
      unsubscribe();
      unsubscribe = null;
    }
  });
}
```

---

## 完整示例

### 示例一：频谱柱状图

```js
export function activate(ctx) {
  // 创建 Canvas
  const canvas = document.createElement("canvas");
  canvas.width = 300;
  canvas.height = 100;
  canvas.style.cssText = `
    position: fixed; bottom: 60px; right: 20px; z-index: 9999;
    border-radius: 8px; background: rgba(0,0,0,0.6);
  `;
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

  ctx.dispose(() => canvas.remove());
}
```

### 示例二：波形可视化

使用 `timeData` 绘制原始波形：

```js
ctx.audio.spectrum.subscribe(
  { fftSize: 1024, smoothingTimeConstant: 0, interval: 30 },
  (frame) => {
    const { timeData } = frame;
    ctx2d.clearRect(0, 0, width, height);
    ctx2d.beginPath();
    ctx2d.strokeStyle = "#00ff88";
    ctx2d.lineWidth = 1;

    for (let i = 0; i < timeData.length; i++) {
      const x = (i / timeData.length) * width;
      const y = (0.5 + timeData[i] * 0.45) * height;
      if (i === 0) ctx2d.moveTo(x, y);
      else ctx2d.lineTo(x, y);
    }
    ctx2d.stroke();
  }
);
```

### 示例三：VU 表（响度监测）

```js
let peak = 0;

ctx.audio.spectrum.subscribe(
  { fftSize: 512, interval: 100 },
  (frame) => {
    // 计算 RMS 作为响度指标
    let sum = 0;
    for (let i = 0; i < frame.timeData.length; i++) {
      sum += frame.timeData[i] * frame.timeData[i];
    }
    const rms = Math.sqrt(sum / frame.timeData.length);
    peak = Math.max(peak, rms);

    // 更新 VU 表 UI
    updateVUMeter(rms, peak);

    // 逐渐衰减峰值
    peak *= 0.99;
  }
);
```

---

## 常见问题

### 频谱数据的 bin 如何对应频率？

对于 FFT 大小 N：`frequencyData[k]` 对应频率约为 `k * sampleRate / N` Hz。

例如 `fftSize=2048`、`sampleRate=44100`：
- `frequencyData[0]` → ~0 Hz（DC）
- `frequencyData[1]` → ~21.5 Hz
- `frequencyData[511]` → ~11,025 Hz（奈奎斯特频率）

低频的 bin 频率分辨率更高。如需在低频段获得更细致的分频，请增大 fftSize。

### interval 和实际帧率的关系？

`interval` 是最小推送间隔。实际帧率取决于系统音频缓冲区大小：
- 默认 50ms → 每秒最多 20 帧
- 设为 16 → 每秒最多 ~60 帧（高刷新率可视化）
- 设为 100 → 每秒最多 10 帧（省电模式）

### 频谱捕获对性能有多大影响？

- 仅在有活跃订阅时才会启动底层系统音频环回捕获
- 所有订阅共享同一帧捕获（不会为每个订阅单独捕获）
- fftSize 越大 → CPU 使用越高，但更精确；建议根据需求选最小值
- 100ms interval + fftSize=512 的 CPU 开销非常低，适合后台运行

---

## 下一步

| 文档 | 内容 |
|------|------|
| [播放器与音频引擎 →](./player-audio) | 播放控制、EQ、空间音效、IR 卷积 |
| [API 总览 →](./context-api) | ctx 完整 API 列表 |
| [窗口与系统 →](./windows-system) | 浮窗、桌面歌词、Mini 播放器 |
