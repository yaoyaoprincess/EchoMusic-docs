---
title: Audio Spectrum
outline: [2, 4]
---

# 📊 Audio Spectrum

> Requires capability: `audioSpectrum: true`

`ctx.audio.spectrum` provides access to EchoMusic's real-time audio spectrum data. Spectrum analysis is performed by the playback engine (the Rust native module `echo-audio-player`) directly inside the playback pipeline. The host merges all subscribers' options into a single engine configuration and broadcasts frames, so plugins share one data stream.

> ℹ️ For a complete example, see the [spectrum-visualizer](https://github.com/hoowhoami/EchoMusicPlugins/tree/main/spectrum-visualizer) plugin in the official plugin repository.

## API Overview

| API | Description | Returns |
|-----|------|------|
| `getStatus()` | Get spectrum engine status | `Promise<AudioSpectrumStatus>` |
| `getSnapshot()` | Get current single-frame spectrum data | `Promise<AudioSpectrumFrame \| null>` |
| `subscribe(options, handler)` | Subscribe to real-time spectrum stream | `() => void` (dispose function) |

Every spectrum API requires `capabilities.audioSpectrum: true` in the manifest, otherwise it throws a "plugin does not declare the audio spectrum capability" error.

---

## getStatus()

Get the current status of the spectrum engine:

```js
const status = await ctx.audio.spectrum.getStatus();
// {
//   available: true,        // whether the spectrum API is available
//   running: true,          // whether frames are being captured and broadcast
//   provider: "player",     // data source
//   reason: undefined,      // why it is not running
//   subscriberCount: 2,     // current subscriber count
// }
```

| Field | Type | Description |
|------|------|------|
| `available` | `boolean` | Whether the spectrum API is available (`false` on older hosts) |
| `running` | `boolean` | Whether capture is active |
| `provider` | `"player" \| "unavailable"` | Spectrum data source; currently always the playback engine |
| `reason` | `string?` | Why it is not running, e.g. `"订阅者均已暂停"` (all subscribers paused), `"播放引擎未初始化"` (playback engine not initialized) |
| `subscriberCount` | `number?` | Current subscriber count |

Common reasons for `running: false`: no active subscribers, all subscribers paused (page hidden / window hidden), or the playback engine has not been initialized.

---

## getSnapshot()

Get one immediate frame of spectrum data. Returns `null` when no frame is available.

```js
const frame = await ctx.audio.spectrum.getSnapshot();
if (frame) {
  console.log("bin count:", frame.bins.length, "RMS:", frame.rms);
}
```

**Use case**: occasionally reading spectrum data (e.g. a cover that pulses with the beat) instead of continuous rendering. For continuous rendering use `subscribe()`.

---

## subscribe(options, handler)

Subscribe to the real-time spectrum stream. The host pushes new frames at the merged frame rate and calls `handler` once per frame.

```js
const dispose = ctx.audio.spectrum.subscribe(
  { fps: 30, binCount: 64, includeWaveform: true },
  (frame) => {
    drawBars(frame.bins);
    drawWave(frame.waveform);
  },
);

// Call the dispose function to stop
dispose();
```

### Subscription options (AudioSpectrumOptions)

| Option | Type | Range | Default | Description |
|------|------|------|------|------|
| `fps` | `number` | 1–60 | 30 | Target frame rate |
| `binCount` | `number` | 8–512 | 128 | Number of frequency bins (`bins` array length) |
| `fftSize` | `number` | — | 2048 | FFT window size; fixed by the host, no need to set |
| `smoothing` | `number` | 0–0.95 | 0.65 | Spectrum smoothing factor; lower is faster but more jittery |
| `minFrequency` | `number` | 1–20000 | 20 | Lower bound of the analysis band (Hz) |
| `maxFrequency` | `number` | 2–24000 | 20000 | Upper bound of the analysis band (Hz) |
| `scale` | `"linear" \| "log" \| "mel"` | — | `"log"` | Frequency axis scale; the host currently always merges to log scale |
| `includeWaveform` | `boolean` | — | `false` | Whether to include time-domain waveform data (`frame.waveform`) |

### Multi-subscriber option merging

All active subscribers share one spectrum stream; the host merges options by "strictest union":

- `fps` / `binCount` / `maxFrequency`: **maximum** across all subscribers
- `minFrequency` / `smoothing`: **minimum** across all subscribers
- `includeWaveform`: enabled if any subscriber requests it

Paused subscribers (see "Lifecycle" below) are excluded from merging and receive no frames — invisible plugins never raise other subscribers' frame rate or payload.

### Frame structure (AudioSpectrumFrame)

```ts
interface AudioSpectrumFrame {
  source: "player" | "silence" | "unavailable";
  state: "playing" | "paused" | "idle";
  timestamp: number;              // frame timestamp (seconds)
  timePos: number | null;         // current playback position (seconds), null when unknown
  sampleRate: number;             // sample rate (currently 48000)
  fftSize: number;                // FFT window size (2048)
  minFrequency: number;           // actual lower bound of this frame's band
  maxFrequency: number;           // actual upper bound of this frame's band
  /** Bin magnitudes normalized to 0..1, length = binCount */
  bins: number[];
  /** Time-domain waveform normalized to -1..1; only present with includeWaveform: true */
  waveform?: number[];
  rms: number;                    // RMS loudness (0..1)
  peak: number;                   // peak level (0..1)
}
```

| Field | Description |
|------|------|
| `bins` | Each element is the magnitude of one band across `minFrequency`–`maxFrequency`, linear 0–1 (not dB) |
| `waveform` | Raw PCM waveform samples for oscilloscope-style drawing; must be enabled explicitly |
| `rms` / `peak` | Per-frame loudness metrics, suitable for VU meters, breathing lights, etc. |
| `state` | Playback state; use it to freeze or fade out visuals while paused |
| `timePos` | Playback position aligned with the frame, useful for beat alignment |

---

## Lifecycle and auto-pause

`subscribe()` returns a **dispose function**; calling it unsubscribes. When a plugin is disabled or uninstalled, the host automatically cleans up all of its subscriptions.

Subscriptions created inside a plugin page's Vue component `setup()` are also bound to the component lifecycle:

- When the component is cached by KeepAlive (invisible), delivery is **paused** and resumes on reactivation
- When the component unmounts, the subscription is fully disposed
- When the host window is minimized or hidden, all subscriptions pause together

The subscription itself stays in the subscription table (so it can resume), and a temporarily invisible plugin never loses state:

```js
// Subscribe inside a component's setup — automatically pauses/resumes with visibility
export function setupPage(ctx) {
  const dispose = ctx.audio.spectrum.subscribe({ binCount: 48 }, renderFrame);
  // You can also dispose() manually when the component unmounts
}
```

If you subscribe in `activate()` (outside a component), it behaves as a plain subscription cleaned up when the plugin is disabled.

---

## Minimal example

Below is a complete, runnable plugin entry: draw a 64-bar spectrum in the bottom-right corner of the screen.

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

## Advanced examples

### Example 1: waveform oscilloscope

Enable `includeWaveform` and draw `frame.waveform` as a time-domain waveform:

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

### Example 2: VU meter (loudness monitoring)

`rms` / `peak` are provided directly by the playback engine — no need to compute them yourself:

```js
let peakHold = 0;

ctx.audio.spectrum.subscribe({ fps: 30 }, (frame) => {
  peakHold = Math.max(frame.peak, peakHold * 0.98);
  updateVUMeter(frame.rms, peakHold);
});
```

### Example 3: freeze visuals while paused

```js
let lastBins = [];

ctx.audio.spectrum.subscribe({ binCount: 64 }, (frame) => {
  if (frame.state === "playing" || frame.bins.some((v) => v > 0)) {
    lastBins = frame.bins;
  }
  renderBars(lastBins); // keep the last frame while paused
});
```

---

## FAQ

### How do bins map to frequencies?

`bins[i]` covers the i-th band of `[minFrequency, maxFrequency]` divided by the current `scale`. With the default log scale, low frequencies get finer resolution, matching human hearing. `minFrequency` / `maxFrequency` on the frame are the **merged** values (possibly widened/narrowed by other subscribers) — read them from the frame for frequency labeling instead of caching your own options.

### How does fps relate to the actual frame rate?

`fps` is the target rate (1–60); the host polls the engine snapshot every `1000 / fps` ms. Actual callback frequency also depends on the engine's snapshot cadence. Frames with the same `timestamp` are not broadcast twice.

### How much does spectrum capture cost?

- The engine only analyzes the spectrum while there is at least one active subscriber; with no subscribers the timer fully stops — zero cost
- All subscribers share one data stream (one FFT, one IPC broadcast)
- Higher `binCount` and `fps` cost more; pause subscriptions on invisible pages (component-bound subscriptions pause automatically)
- Paused subscribers are excluded from option merging, so they never raise someone else's frame rate

### Why am I not receiving frames?

Check in order:

1. Does the manifest declare `capabilities.audioSpectrum: true`?
2. Check `getStatus()`'s `running` / `reason` — common causes are an uninitialized playback engine or all subscribers paused
3. Is something actually playing (`frame.state`)?
4. Did you enable `includeWaveform`? Without it `frame.waveform` is `undefined`, not an empty array

---

## Next steps

| Document | Content |
|------|------|
| [Player & Audio Engine →](./player-audio) | Playback control, EQ, spatial audio, IR convolution |
| [API Overview →](./context-api) | Full ctx API list |
| [Windows & System →](./windows-system) | Floating windows, desktop lyric, mini player |
