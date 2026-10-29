---
title: Graphics 绘图
---

# 🖼️ Graphics 绘图

`ctx.graphics` 为插件提供通用绘图基础能力：独立画布、WebGPU 渲染、动画调度、尺寸适配、显示能力通知及生命周期清理。可用于频谱、图形动画和自定义着色器效果；HDR 高光是可选输出能力，普通 SDR 绘图也可使用。

宿主管理画布和输出流程，插件负责具体图形、着色器及 GPU 资源的创建。这是底层绘图 API，不包含现成的场景、粒子、滤镜或图形组件。WebGPU 不可用时提供 Canvas2D 回退接口。

> 💡 本接口**不需要额外的 manifest capability**。依赖它的插件应检测 `ctx.graphics?.createCanvas` 是否存在，并用 `requires.echoMusicVersion` 限定到实际包含该接口的宿主版本。不要仅根据 Electron 版本号推断 GPU 可用。

## 快速开始：普通 SDR 绘图

```js
async function mountGraphic(ctx, container) {
  if (!ctx.graphics?.createCanvas) throw new Error('当前 EchoMusic 不支持 Graphics API');
  const surface = await ctx.graphics.createCanvas({ dynamicRange: 'sdr' });
  container.appendChild(surface.canvas); // container 需有明确 CSS 尺寸
  if (surface.context2d) {
    surface.resize();
    surface.context2d.fillStyle = ctx.graphics.toSdrColor({ r: 0.1, g: 0.3, b: 0.6 });
    surface.context2d.fillRect(0, 0, surface.canvas.width, surface.canvas.height);
    // Canvas2D 模式下，尺寸变化后的重绘由插件负责
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

组件卸载时调用返回的清理函数。需要动画时使用 `surface.start(draw)`；已有自己的渲染循环则调用 `surface.render(draw)`。设置 `dynamicRange: 'auto'` 后，宿主会按显示能力自动选择 HDR 或 SDR 输出。

## 能力检测

```js
const capabilities = await ctx.graphics.getCapabilities();
const off = ctx.graphics.onCapabilitiesChanged((caps) => console.log(caps));

// 可主动重试 GPU 探测（如设备恢复后）：
await ctx.graphics.getCapabilities({ refresh: true });
```

| 字段 | 含义 |
|------|------|
| `webgpu` | GPU adapter 和 device 能成功创建 |
| `hdrCanvas` | 临时画布实际接受 `rgba16float` + `extended`，且无配置验证错误 |
| `displayHighDynamicRange` | 浏览器 `(dynamic-range: high)` 媒体查询结果 |
| `colorGamut` | 浏览器报告的 `srgb` / `p3` / `rec2020` 能力 |
| `hdrEligible` | HDR 画布配置和显示能力都满足，具备尝试 HDR 输出的条件 |
| `outputVerification` | 固定为 `unverified`（宿主无法测量实际屏幕亮度） |
| `reason` | `null` 或回退原因字符串 |

> ⚠️ `hdrEligible: true` 不表示系统 HDR 一定已开启，也不表示当前窗口已输出某个亮度值——媒体查询报告的是**能力**，不是亮度测量。

首次订阅会异步推送状态，之后在 HDR/色域媒体查询变化、窗口 resize/focus/pageshow 或文档可见性变化时重新读取并推送。`off()` 取消订阅，插件卸载时也会自动取消。

## 创建画布

```js
const surface = await ctx.graphics.createCanvas({
  dynamicRange: 'auto',   // 默认 auto；'sdr' 强制使用 SDR
  alphaMode: 'opaque',    // 默认 opaque；'premultiplied' 允许画布透明
  maxDimension: 4096,     // 默认 4096，限制实际像素宽高
});
container.appendChild(surface.canvas);
```

容器必须有明确的布局尺寸（如 `width: 320px; height: 180px`）。返回的 canvas 默认为容器尺寸的 100%，不会自动挂载到 DOM。

| 成员 | 说明 |
|------|------|
| `surface.canvas` | 画布 DOM 元素 |
| `surface.device` | WebGPU 分支的 `GPUDevice`（2D 回退分支为 `null`），可用于创建插件自己的 shader/pipeline/buffer |
| `surface.context2d` | WebGPU 不可用时的 SDR `CanvasRenderingContext2D`（GPU 分支为 `null`） |
| `surface.getState()` | `{backend: 'webgpu'|'canvas2d', status: 'ready'|'lost'|'disposed', dynamicRange, reason, outputVerification}` |
| `surface.onStateChanged(cb)` | 立即推送当前状态，之后通知 HDR/SDR 切换与设备丢失；返回取消函数 |
| `surface.resize(width?, height?, pixelRatio?)` | 立即调整 backing store；不传尺寸则读取布局，之后仍跟随 DOM 布局自动调整 |
| `surface.dispose()` | 停止动画、释放资源、移除画布；可重复调用，插件卸载时自动执行 |

`reason` 取值包括 `webgpu-unavailable`、`adapter-unavailable`、`gpu-initialization-failed`、`hdr-canvas-unavailable`、`display-reports-sdr`、`sdr-requested`、`device-lost`。用 `backend` 和 `status` 决定分支，原因字符串用于诊断。

## 颜色与绘制约定

插件向宿主提供的 **`rgba16float`、线性 sRGB、直通 alpha（straight alpha）** 渲染目标绘制：

- RGB `1.0` 表示 SDR 参考白，`2.0`、`4.0` 等表示相对参考白的高光（非物理尼特值）；
- 输入**不要**再做 sRGB gamma 编码、SDR tone mapping 或 alpha 预乘，宿主负责最终输出转换；
- HDR 分支使用浮点画布与 extended tone mapping，保留超出 SDR 范围的值，由浏览器/系统适配实际显示范围；
- SDR 分支在画布内应用平滑高光压缩（线性 RGB 峰值不超过 `0.75` 时不改变）；
- 两种模式下插件渲染目标始终是 `rgba16float`，跨屏切换无需重建 pipeline；
- 当前接口不提供 PQ/HLG 解码、P3 输出或固定尼特亮度控制。

```js
surface.render(({ encoder, view, width, height, time, device, format }) => {
  // 同步编码命令；format 固定为 rgba16float
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
  // 不要调用 encoder.finish() / queue.submit()，宿主负责合成与提交
});
```

`render()` 返回是否提交了绘制。回调必须同步、不可 `async`；shader/pipeline/资源应提前准备。每帧宿主先清空输入纹理；画布尺寸或 HDR 状态变化时会重新调用最近一次绘制回调，因此回调应可重复执行，动画计时请使用 `time`（毫秒）而不是隐式计数。

## 下一步

| 文档 | 内容 |
|------|------|
| [音频频谱 →](./audio-spectrum) | 与 Graphics 结合做频谱可视化 |
| [网络与下载 →](./network) | 拉取远程纹理/着色器资源 |
| [Context API →](./context-api) | ctx 完整 API 速查 |
