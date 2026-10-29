---
title: 音频频谱
outline: [2, 4]
---

# 📊 音频频谱

> 需要 capability：`audioSpectrum: true`

`ctx.audio.spectrum` 提供对 EchoMusic 实时音频频谱数据的访问。频谱分析由播放引擎（Rust 原生模块 `echo-audio-player`）在播放管线内直接完成，宿主把多个订阅者的参数合并成一份引擎配置并按帧广播，插件之间共享同一条数据流。

> ℹ️ 完整示例可参考官方插件仓库中的 [spectrum-visualizer](https://github.com/hoowhoami/EchoMusicPlugins/tree/main/spectrum-visualizer)（频谱可视化）插件。

## API 概览

| API | 说明 | 返回 |
|-----|------|------|
| `getStatus()` | 获取频谱引擎当前状态 | `Promise<AudioSpectrumStatus>` |
| `getSnapshot()` | 获取当前单帧频谱数据 | `Promise<AudioSpectrumFrame \| null>` |
| `subscribe(options, handler)` | 订阅实时频谱数据流 | `() => void`（清理函数） |

调用任何频谱 API 前必须在 manifest 中声明 `capabilities.audioSpectrum: true`，否则会抛出「插件未声明音频频谱能力」错误。

---

## getStatus()

获取频谱引擎的当前状态：

```js
const status = await ctx.audio.spectrum.getStatus();
// {
//   available: true,        // 频谱 API 是否可用
//   running: true,          // 是否正在采集并广播帧
//   provider: "player",     // 数据来源
//   reason: undefined,      // 未运行时的原因说明
//   subscriberCount: 2,     // 当前订阅数
// }
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `available` | `boolean` | 频谱 API 是否可用（旧版本宿主上为 `false`） |
| `running` | `boolean` | 是否处于采集状态 |
| `provider` | `"player" \| "unavailable"` | 频谱数据来源；当前实现固定为播放引擎 |
| `reason` | `string?` | 未运行时的原因，如 `"订阅者均已暂停"`、`"播放引擎未初始化"` |
| `subscriberCount` | `number?` | 当前订阅者数量 |

`running` 为 `false` 的常见原因：没有任何活跃订阅、所有订阅者都被暂停（页面不可见/窗口隐藏）、播放引擎尚未初始化。

---

## getSnapshot()

获取一帧即时的频谱数据。如果当前没有可用帧，返回 `null`。

```js
const frame = await ctx.audio.spectrum.getSnapshot();
if (frame) {
  console.log("频段数:", frame.bins.length, "RMS:", frame.rms);
}
```

**适用场景**：只需要偶尔读取频谱数据（如封面随节奏微动），而不是持续实时绘制。持续渲染请用 `subscribe()`。

---

## subscribe(options, handler)

订阅实时频谱数据流。宿主按合并后的帧率推送新帧，每帧调用一次 `handler`。

```js
const dispose = ctx.audio.spectrum.subscribe(
  { fps: 30, binCount: 64, includeWaveform: true },
  (frame) => {
    drawBars(frame.bins);
    drawWave(frame.waveform);
  },
);

// 需要停止时调用清理函数
dispose();
```

### 订阅选项（AudioSpectrumOptions）

| 选项 | 类型 | 范围 | 默认 | 说明 |
|------|------|------|------|------|
| `fps` | `number` | 1–60 | 30 | 目标帧率 |
| `binCount` | `number` | 8–512 | 128 | 频段数量（`bins` 数组长度） |
| `fftSize` | `number` | — | 2048 | FFT 窗口大小；由宿主统一固定，插件无需设置 |
| `smoothing` | `number` | 0–0.95 | 0.65 | 频谱平滑系数，越小响应越快、抖动越大 |
| `minFrequency` | `number` | 1–20000 | 20 | 分析频带下限（Hz） |
| `maxFrequency` | `number` | 2–24000 | 20000 | 分析频带上限（Hz） |
| `scale` | `"linear" \| "log" \| "mel"` | — | `"log"` | 频率轴刻度；宿主当前合并配置固定使用对数刻度 |
| `includeWaveform` | `boolean` | — | `false` | 是否附带时域波形数据（`frame.waveform`） |

### 多订阅者参数合并

所有活跃订阅共享一条频谱流，宿主按「最苛刻并集」合并参数：

- `fps` / `binCount` / `maxFrequency`：取所有订阅中的**最大值**
- `minFrequency` / `smoothing`：取所有订阅中的**最小值**
- `includeWaveform`：任一订阅为 `true` 即开启

被暂停的订阅（见下文「生命周期」）不参与合并，也不会收到帧——不可见的插件不会抬高其他订阅者的帧率和载荷。

### 频谱帧结构（AudioSpectrumFrame）

```ts
interface AudioSpectrumFrame {
  source: "player" | "silence" | "unavailable";
  state: "playing" | "paused" | "idle";
  timestamp: number;              // 帧时间戳（秒）
  timePos: number | null;         // 当前播放位置（秒），未知时为 null
  sampleRate: number;             // 采样率（当前为 48000）
  fftSize: number;                // FFT 窗口大小（2048）
  minFrequency: number;           // 本帧分析频带下限
  maxFrequency: number;           // 本帧分析频带上限
  /** 频段幅度，已归一化到 0..1，长度 = binCount */
  bins: number[];
  /** 时域波形，归一化到 -1..1；仅 includeWaveform: true 时存在 */
  waveform?: number[];
  rms: number;                    // 均方根响度（0..1）
  peak: number;                   // 峰值电平（0..1）
}
```

| 字段 | 说明 |
|------|------|
| `bins` | 每个元素对应 `minFrequency`–`maxFrequency` 内的一个频段幅度，线性值 0–1（非 dB） |
| `waveform` | 原始 PCM 波形采样，用于示波器式绘制；需要显式开启 |
| `rms` / `peak` | 整帧响度指标，适合 VU 表、呼吸灯等低频驱动的效果 |
| `state` | 播放状态，可用于暂停时冻结画面或渐隐 |
| `timePos` | 与帧同步的播放位置，可用于节奏对齐 |

---

## 生命周期与自动暂停

`subscribe()` 返回一个**清理函数**，调用即退订。插件禁用/卸载时，宿主会自动清理该插件的所有订阅。

在插件页面的 Vue 组件 `setup()` 中创建的订阅还会与组件生命周期绑定：

- 组件被 KeepAlive 缓存（不可见）时**暂停投递**，重新激活时恢复
- 组件卸载时彻底退订
- 宿主窗口最小化/隐藏时，所有订阅统一暂停

订阅本身保留在订阅表中（便于恢复），不会因为暂时不可见而丢失状态：

```js
// 组件 setup 内订阅 —— 自动随页面显隐暂停/恢复
export function setupPage(ctx) {
  const dispose = ctx.audio.spectrum.subscribe({ binCount: 48 }, renderFrame);
  // 也可以手动在组件卸载时 dispose()
}
```

若在插件 `activate()` 阶段（组件外）订阅，则为普通订阅，随插件停用统一清理。

---

## 最小示例

下面是一个可直接运行的完整插件入口：在屏幕右下角绘制一个 64 段的频谱柱状图。

```js
export function activate(ctx) {
  const canvas = document.createElement("canvas");
  canvas.width = 320;
  canvas.height = 96;
  canvas.style.cssText = `
    position: fixed; bottom: 72px; right: 16px; z-index: 9999;
    border-radius: 8px; background: rgba(0,0,0,0.55); pointer-events: none;
  `;
  document.body.appendChild(canvas);
  const ctx2d = canvas.getContext("2d");

  const dispose = ctx.audio.spectrum.subscribe(
    { fps: 30, binCount: 64 },
    (frame) => {
      const { bins } = frame;
      const width = canvas.width;
      const height = canvas.height;
      const barWidth = width / bins.length;

      ctx2d.clearRect(0, 0, width, height);
      for (let i = 0; i < bins.length; i++) {
        const barHeight = Math.max(1, bins[i] * height);
        ctx2d.fillStyle = `hsl(${200 + (i / bins.length) * 120}, 80%, 60%)`;
        ctx2d.fillRect(i * barWidth, height - barHeight, barWidth - 1, barHeight);
      }
    },
  );

  ctx.dispose(() => {
    dispose();
    canvas.remove();
  });
}
```

---

## 进阶示例

### 示例一：波形示波器

开启 `includeWaveform` 后用 `frame.waveform` 绘制时域波形：

```js
ctx.audio.spectrum.subscribe(
  { fps: 60, binCount: 32, smoothing: 0.2, includeWaveform: true },
  (frame) => {
    const wave = frame.waveform;
    if (!wave || wave.length < 2) return;

    ctx2d.clearRect(0, 0, width, height);
    ctx2d.beginPath();
    ctx2d.strokeStyle = "#00ff88";
    ctx2d.lineWidth = 1.5;

    for (let i = 0; i < wave.length; i++) {
      const x = (i / (wave.length - 1)) * width;
      const y = (0.5 - wave[i] * 0.45) * height;
      if (i === 0) ctx2d.moveTo(x, y);
      else ctx2d.lineTo(x, y);
    }
    ctx2d.stroke();
  },
);
```

### 示例二：VU 表（响度监测）

`rms` / `peak` 由播放引擎直接给出，无需自己计算：

```js
let peakHold = 0;

ctx.audio.spectrum.subscribe({ fps: 30 }, (frame) => {
  peakHold = Math.max(frame.peak, peakHold * 0.98);
  updateVUMeter(frame.rms, peakHold);
});
```

### 示例三：按播放状态冻结画面

```js
let lastBins = [];

ctx.audio.spectrum.subscribe({ binCount: 64 }, (frame) => {
  if (frame.state === "playing" || frame.bins.some((v) => v > 0)) {
    lastBins = frame.bins;
  }
  renderBars(lastBins); // 暂停时保持最后一帧画面
});
```

---

## 常见问题

### bins 如何对应频率？

`bins[i]` 覆盖 `[minFrequency, maxFrequency]` 区间按当前 `scale` 刻度划分出的第 `i` 个频段。默认对数刻度下低频段更细、高频段更宽，贴近听感。帧上的 `minFrequency` / `maxFrequency` 是**合并后**的实际取值（可能被其他订阅者放宽/收紧），做频率标注时应读取帧字段而不是自己保存的选项。

### fps 和实际帧率的关系？

`fps` 是目标帧率（1–60），宿主按 `1000 / fps` ms 轮询播放引擎快照。实际回调频率还受引擎快照更新节奏影响；相同 `timestamp` 的帧不会重复广播。

### 频谱采集对性能有多大影响？

- 只要有活跃订阅，宿主才会启动引擎频谱分析；没有订阅时完全停表，零开销
- 所有订阅共享同一条数据流（一次 FFT、一次 IPC 广播）
- `binCount` 越大、`fps` 越高开销越大；不可见页面建议暂停订阅（组件级订阅会自动暂停）
- 暂停的订阅不参与参数合并，因此不会把别人的帧率抬上去

### 为什么收不到帧？

依次检查：

1. manifest 是否声明了 `capabilities.audioSpectrum: true`
2. `getStatus()` 的 `running` / `reason`——常见原因是播放引擎未初始化或订阅者均已暂停
3. 当前是否处于播放状态（`frame.state`）
4. `includeWaveform` 是否开启——未开启时 `frame.waveform` 为 `undefined`，不是空数组

---

## 下一步

| 文档 | 内容 |
|------|------|
| [播放器与音频引擎 →](./player-audio) | 播放控制、EQ、空间音效、IR 卷积 |
| [API 总览 →](./context-api) | ctx 完整 API 列表 |
| [窗口与系统 →](./windows-system) | 浮窗、桌面歌词、Mini 播放器 |
