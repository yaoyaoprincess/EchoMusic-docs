---
title: Graphics
---

# 🖼️ Graphics

`ctx.graphics` provides general-purpose drawing primitives for plugins: standalone canvases, WebGPU rendering, animation scheduling, size adaptation, display capability notifications, and lifecycle cleanup. Use it for spectrum visualizations, graphics animations, and custom shader effects; HDR highlights are one optional output capability — plain SDR drawing works too.

The host manages the canvas and output pipeline; the plugin creates the actual graphics, shaders, and GPU resources. This is a low-level drawing API — it ships no ready-made scenes, particles, filters, or graphics components. When WebGPU is unavailable a Canvas2D fallback is provided; whatever the fallback draws is up to the plugin.

> 💡 This interface requires **no extra manifest capability**. Plugins depending on it should feature-detect `ctx.graphics?.createCanvas` and pin `requires.echoMusicVersion` to a host version that actually ships the API. Do not infer GPU availability from the Electron version alone.

## Quick Start: Plain SDR Drawing

```js
async function mountGraphic(ctx, container) {
  if (!ctx.graphics?.createCanvas) throw new Error('Current EchoMusic does not support the Graphics API');
  const surface = await ctx.graphics.createCanvas({ dynamicRange: 'sdr' });
  container.appendChild(surface.canvas); // container must have explicit CSS dimensions
  if (surface.context2d) {
    surface.resize();
    surface.context2d.fillStyle = ctx.graphics.toSdrColor({ r: 0.1, g: 0.3, b: 0.6 });
    surface.context2d.fillRect(0, 0, surface.canvas.width, surface.canvas.height);
    // In Canvas2D mode, redrawing after size changes is the plugin's responsibility
  } else {
    surface.render(({ encoder, view }) => {
      const pass = encoder.beginRenderPass({
        colorAttachments: [{
          view,
          clearValue: { r: 0.1, g: 0.3, b: 0.6, a: 1 },
          loadOp: 'clear',
          storeOp: 'store',
        }],
      });
      pass.end();
    });
  }
  return () => surface.dispose();
}
```

Call the returned cleanup function when the component unmounts. Use `surface.start(draw)` for animations; if you already run your own render loop, call `surface.render(draw)`. With `dynamicRange: 'auto'`, the host picks HDR or SDR output based on display capabilities.

## Capability Detection

```js
const capabilities = await ctx.graphics.getCapabilities();
const off = ctx.graphics.onCapabilitiesChanged((caps) => console.log(caps));

// Actively retry GPU probing (e.g. after a device recovers):
await ctx.graphics.getCapabilities({ refresh: true });
```

| Field | Meaning |
|------|------|
| `webgpu` | A GPU adapter and device can be created |
| `hdrCanvas` | A probe canvas actually accepts `rgba16float` + `extended` with no validation errors |
| `displayHighDynamicRange` | Browser `(dynamic-range: high)` media query result |
| `colorGamut` | Browser-reported `srgb` / `p3` / `rec2020` capability |
| `hdrEligible` | HDR canvas config and display capability are both satisfied — ready to attempt HDR output |
| `outputVerification` | Always `unverified` (the host cannot measure actual screen brightness) |
| `reason` | `null` or a fallback reason string |

> ⚠️ `hdrEligible: true` does not mean system HDR is actually on, nor that the window currently outputs any brightness — media queries report **capability**, not measured brightness.

The first subscription pushes the state asynchronously; afterwards changes are pushed when HDR/gamut media queries change, on window resize/focus/pageshow, or on visibility changes. `off()` cancels the subscription; plugin unloading cancels it automatically.

## Creating a Canvas

```js
const surface = await ctx.graphics.createCanvas({
  dynamicRange: 'auto',   // default auto; 'sdr' forces SDR
  alphaMode: 'opaque',    // default opaque; 'premultiplied' allows transparency
  maxDimension: 4096,     // default 4096, caps the actual pixel width/height
});
container.appendChild(surface.canvas);
```

The container must have explicit layout dimensions (e.g. `width: 320px; height: 180px`). The returned canvas defaults to 100% of the container and is not auto-mounted to the DOM.

| Member | Description |
|------|------|
| `surface.canvas` | The canvas DOM element |
| `surface.device` | `GPUDevice` on the WebGPU branch (`null` on the 2D fallback) — create your own shaders/pipelines/buffers with it |
| `surface.context2d` | SDR `CanvasRenderingContext2D` when WebGPU is unavailable (`null` on the GPU branch) |
| `surface.getState()` | `{backend: 'webgpu'|'canvas2d', status: 'ready'|'lost'|'disposed', dynamicRange, reason, outputVerification}` |
| `surface.onStateChanged(cb)` | Pushes the current state immediately, then notifies on HDR/SDR switches and device loss; returns a cancel function |
| `surface.resize(width?, height?, pixelRatio?)` | Resize the backing store immediately; omit dimensions to read the layout, then keep tracking the DOM layout |
| `surface.dispose()` | Stop animations, release resources, remove the canvas; safe to call repeatedly, runs automatically on unload |

`reason` values include `webgpu-unavailable`, `adapter-unavailable`, `gpu-initialization-failed`, `hdr-canvas-unavailable`, `display-reports-sdr`, `sdr-requested`, `device-lost`. Branch on `backend` and `status`; the reason strings are for diagnostics.

## Color & Drawing Conventions

Plugins draw into a **`rgba16float`, linear-sRGB, straight-alpha** render target provided by the host:

- RGB `1.0` is the SDR reference white; `2.0`, `4.0`, etc. are highlights relative to that reference white — not physical nits;
- Do **not** apply sRGB gamma encoding, SDR tone mapping, or alpha premultiplication on input — the host handles the final output conversion;
- The HDR branch uses a float canvas with extended tone mapping, preserving values beyond SDR and letting the browser/OS adapt them to the actual display;
- The SDR branch applies smooth highlight compression inside the canvas (linear RGB peaks at or below `0.75` are untouched);
- In both modes the plugin render target is always `rgba16float` — no pipeline rebuild is needed when crossing displays;
- The current API does not provide PQ/HLG decoding, P3 output, or fixed-nit brightness control.

```js
surface.render(({ encoder, view, width, height, time, device, format }) => {
  // Encode commands synchronously; format is always rgba16float
  const pass = encoder.beginRenderPass({
    colorAttachments: [{
      view,
      clearValue: { r: 4, g: 1, b: 0.25, a: 1 },
      loadOp: 'clear',
      storeOp: 'store',
    }],
  });
  // pass.setPipeline(pluginPipeline); ...
  pass.end();
  // Do NOT call encoder.finish() / queue.submit() — the host composes and submits
});
```

`render()` returns whether a draw was submitted. The callback must be synchronous and cannot be `async`; prepare shaders/pipelines/resources ahead of time. The host clears the input texture every frame; the most recent draw callback is re-invoked when canvas size or HDR state changes, so the callback must be re-runnable — use `time` (milliseconds) for animation timing instead of implicit counters.

## Next Steps

| Document | Content |
|------|------|
| [Audio Spectrum →](./audio-spectrum) | Combine with Graphics for spectrum visualizations |
| [Network & Downloads →](./network) | Fetch remote textures/shader resources |
| [Context API →](./context-api) | Full ctx API quick reference |
