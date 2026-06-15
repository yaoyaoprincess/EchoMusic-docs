---
title: Audio Spectrum
outline: [2, 4]
---

# 📊 Audio Spectrum

> Requires capability: `audioSpectrum: true`

`ctx.audio.spectrum` provides access to EchoMusic's real-time audio spectrum data. The underlying `echo-spectrum-capture` native addon captures FFT data from the system audio output.

## API Overview

| API | Description | Returns |
|-----|------|------|
| `getStatus()` | Get spectrum capture status | `Promise<AudioSpectrumStatus>` |
| `getSnapshot()` | Get current single-frame spectrum data | `Promise<AudioSpectrumFrame \| null>` |
| `subscribe(options, handler, meta?)` | Subscribe to real-time spectrum stream | `() => void` (cancellation function) |

---

## getStatus()

Get the current state of the spectrum capture engine.

```js
const status = await ctx.audio.spectrum.getStatus();
// {
//   capturing: true,      // Whether currently capturing
//   sampleRate: 44100,    // Current sample rate
//   fftSize: 2048,        // Current FFT window size
//   subscriptions: 2,     // Active subscription count
// }
```

| Field | Type | Description |
|------|------|------|
| `capturing` | `boolean` | Whether spectrum capture is active |
| `sampleRate` | `number` | Audio sample rate (Hz) |
| `fftSize` | `number` | FFT transform window size |
| `subscriptions` | `number` | Current active subscription count |

---

## getSnapshot()

Get a single instantaneous frame of spectrum data. Returns `null` if capture is not started.

```js
const frame = await ctx.audio.spectrum.getSnapshot();
if (frame) {
  // frame.frequencyData: Float32Array — frequency domain data
  // frame.timeData: Float32Array      — time domain data
  // frame.sampleRate: number          — sample rate
  console.log("Frequency data length:", frame.frequencyData.length);
}
```

**Use case:** When you only need occasional spectrum readings (e.g., making screenshots) rather than continuous real-time updates.

---

## subscribe(options, handler)

Subscribe to real-time spectrum data. `handler` is called whenever a new spectrum frame is captured.

### Parameters

| Parameter | Type | Required | Description |
|------|------|:--:|------|
| `options.fftSize` | `number` | ❌ | FFT window size (32-32768, must be power of 2), default 2048 |
| `options.smoothingTimeConstant` | `number` | ❌ | Smoothing coefficient (0-1), default 0.8. Lower = faster response |
| `options.interval` | `number` | ❌ | Minimum data push interval (ms), default 50 |
| `handler` | `(frame) => void` | ✅ | Spectrum data callback |
| `meta.pluginId` | `string` | ❌ | Subscriber identifier, auto-filled with current plugin ID |

### Spectrum Frame Structure (AudioSpectrumFrame)

```ts
interface AudioSpectrumFrame {
  frequencyData: Float32Array;  // Frequency domain data (length = fftSize / 2)
  timeData: Float32Array;       // Time domain data (length = fftSize)
  sampleRate: number;           // Sample rate (Hz)
}
```

| Field | Description |
|------|------|
| `frequencyData` | `[0, fftSize/2)` — each bin represents a frequency range amplitude (linear 0-1, not dB) |
| `timeData` | `[0, fftSize)` — raw PCM waveform samples |
| `sampleRate` | Actual captured audio sample rate |

### Return Value

`subscribe()` returns a **cancellation function**. Call it to stop this subscription. All subscriptions are automatically cancelled when the plugin is disabled/uninstalled:

```js
const unsubscribe = ctx.audio.spectrum.subscribe(
  { fftSize: 1024, interval: 30 },
  (frame) => {
    drawBars(frame.frequencyData);
  }
);

// Manually unsubscribe later
unsubscribe();
```

### On-Demand Spectrum Capture

To avoid unnecessary performance overhead, subscribe to spectrum only during playback:

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

## Full Examples

### Example 1: Spectrum Bar Chart

```js
export function activate(ctx) {
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

### Example 2: Waveform Visualization

Using `timeData` to draw raw waveform:

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

### Example 3: VU Meter (Loudness Monitor)

```js
let peak = 0;

ctx.audio.spectrum.subscribe(
  { fftSize: 512, interval: 100 },
  (frame) => {
    // Calculate RMS as loudness indicator
    let sum = 0;
    for (let i = 0; i < frame.timeData.length; i++) {
      sum += frame.timeData[i] * frame.timeData[i];
    }
    const rms = Math.sqrt(sum / frame.timeData.length);
    peak = Math.max(peak, rms);

    updateVUMeter(rms, peak);

    // Gradually decay peak
    peak *= 0.99;
  }
);
```

---

## FAQ

### How do spectrum bins map to frequencies?

For FFT size N: `frequencyData[k]` corresponds to approximately `k * sampleRate / N` Hz.

For example, `fftSize=2048`, `sampleRate=44100`:
- `frequencyData[0]` → ~0 Hz (DC)
- `frequencyData[1]` → ~21.5 Hz
- `frequencyData[511]` → ~11,025 Hz (Nyquist frequency)

Lower frequency bins have higher resolution. For finer frequency separation in the low end, increase fftSize.

### What's the relationship between interval and actual frame rate?

`interval` is the minimum push interval. Actual frame rate depends on the system audio buffer size:
- Default 50ms → max ~20 fps
- Set to 16 → max ~60 fps (high refresh visualization)
- Set to 100 → max ~10 fps (power saving)

### How much performance impact does spectrum capture have?

- Underlying system audio loopback capture only starts when there are active subscriptions
- All subscriptions share the same frame capture (no duplicate capture per subscription)
- Larger fftSize → higher CPU usage but more precision; choose the minimum for your needs
- 100ms interval + fftSize=512 has very low CPU overhead, suitable for background operation

---

## Next Steps

| Document | Content |
|------|------|
| [Player & Audio Engine →](./player-audio) | Playback controls, EQ, spatial audio, IR convolution |
| [API Reference →](./context-api) | Complete ctx API listing |
| [Windows & System →](./windows-system) | Floating windows, desktop lyric, Mini player |
