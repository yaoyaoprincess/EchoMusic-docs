---
title: 音频引擎（electron.player）
outline: [2, 4]
---

# 🎵 音频引擎（electron.player）

EchoMusic 底层使用 **Rust 播放引擎** `echo-audio-player`（vendored FFmpeg 解码 + 双引擎变速，Rust NAPI 进程内嵌入，无需外部 FFmpeg 可执行文件）。渲染进程通过 preload 暴露的 `electron.player.*` 控制，主进程封装在 `src/main/player/`（`controller.ts` 等）。

引擎处理链：`FFmpeg 解码 → 格式转换 → DspHost（EQ/卷积/Provider）→ 变速 → 输出增益 → 设备输出`。

> ⚠️ 历史版本文档中的 `setSpatialAudio({preset})`、`setImpulseResponse({path, dryWet})`、`getAudioFilter()`、`onImpulseResponseDisabled()` 在当前源码中**不存在**，均已由 `setAudioEffect` 音效模型取代。

---

## 加载与音源切换

### 基础加载

| API | 说明 |
|-----|------|
| `load(url, requestId?)` | 加载音频 URL 或本地文件 |
| `loadMkvTrack(url, trackId, requestId?)` | 加载 MKV 容器中的指定音轨 |
| `getTrackList(url?)` | 获取容器音轨列表（MKV 多音轨） |
| `setLoopFile(bool)` | 单曲循环 |
| `setMediaTitle(title)` | 设置系统媒体控制显示标题 |

### 无缝切歌 / 音源切换

引擎内建"源切换"协议，配合[歌曲过渡](#歌曲过渡设置)实现不中断播放的换源与切歌：

| API | 说明 |
|-----|------|
| `beginSourceChange()` | 声明进入换源流程（冻结旧源状态） |
| `switchSource(url, trackId?)` | 在同一播放会话内切换音源 URL |
| `beginNextSourcePreparation()` | 开始预备下一首，返回 `requestId` |
| `cancelNextSourcePreparation(requestId)` | 取消预备 |
| `prepareNextSource(url, requestId, trackId?, normalizationGainDb?)` | 预解码下一首（含响度归一化预置） |
| `commitPreparedNextSource(transitionMs?)` | 在过渡窗口内提交预备好的下一首（无缝交接） |
| `clearPreparedNextSource()` | 丢弃预备内容 |

> 预备应在当前曲目临近结束时完成——`getTransitionSettings()` 返回的 `prefetchLeadSecs` 即建议的提前量。切歌决策（是否 gapless / 淡入淡出 / automix）由引擎 `transition/` 子系统依据 **8 个 JSON 过渡计划**（`simple_filter`、`three_band`、`simple_exchange`、`filter_eq`、`fallback_exchange`、`echo_tail`、`smooth_filter`、`layered_filter`）计算。

---

## 歌曲过渡设置

```js
await electron.player.setTransitionSettings({
  mode: "gapless",     // "none" | "gapless" | "fade" | "automix-basic" | "automix-pro"
  fadeSecs: 4,         // 淡入淡出时长（fade 模式 0–15s）
  matchTempo: true,    // automix-pro 是否节奏匹配（变速对齐）
});
```

| API | 返回 | 说明 |
|-----|------|------|
| `setTransitionSettings(options)` | — | 设置过渡模式 / 淡入淡出秒数 / 节奏匹配 |
| `getTransitionSettings()` | `{ mode, fadeSecs, matchTempo, prefetchLeadSecs }` | 当前设置（含建议预备提前量） |
| `getTransitionDiagnostics()` | `string \| null` | 最近一次过渡的诊断信息（JSON） |

五种模式：`none`（硬切）、`gapless`（跳过首尾静音、采样级无缝拼接）、`fade`（线性交叠淡入淡出 0–15s）、`automix-basic`（内容感知出点，节奏/增益不变，低频-增益交换）、`automix-pro`（节拍对齐出点 + 多段滤波 + 可选变速对齐）。

---

## 播放控制

| API | 说明 |
|-----|------|
| `play(requestId?)` / `pause()` / `stop()` | 播放 / 暂停 / 停止 |
| `seek(time)` | 跳转到指定秒 |
| `setVolume(volume)` | 设置音量（应用层音量刻度，与 UI 音量一致） |
| `setSpeed(speed)` | 变速，范围 **0.1x – 5x**。双引擎：谱减相位声码器（极端速度）+ SoundTouch WSOLA（常规速度），音质与时延自动取舍 |

---

## 均衡器（EQ）

10 段参数化均衡器，每段独立增益（-12 ~ +12 dB）：

```js
await electron.player.setEqualizer([
  0,   // 31 Hz
  2,   // 62 Hz
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

频点为 `31 / 62 / 125 / 250 / 500 / 1000 / 2000 / 4000 / 8000 / 16000` Hz。EQ 级联会自动测量 headroom；实时调整以 15ms 交叉渐变切换滤波器状态，无爆音。

---

## 响度归一化

```js
await electron.player.setNormalizationGain(-3.5); // dB，取自歌曲响度分析
```

---

## 音量渐变（Fade）

| API | 说明 |
|-----|------|
| `fade(from, to, durationMs)` | 音量从 `from` 渐变到 `to` |
| `cancelFade()` | 取消进行中的渐变 |
| `pauseWithFade(savedVolume, durationMs)` | 渐弱后暂停（记住原音量） |
| `playWithFade(targetVolume, durationMs, requestId?)` | 渐强恢复播放 |

---

## 音效模型（setAudioEffect）

统一的音效入口，覆盖内置卷积（IR）与外部 DSP Provider 两种路径：

```ts
await electron.player.setAudioEffect({
  // —— 内置 Basic DSP（IR 卷积）——
  impulseResponsePath: "path/to/effect.irs" | null,
  impulseResponseMix: 1.0,               // 0（全干）– 1（全湿），仅 Basic DSP 生效
  // —— 外部 DSP Provider ——
  providerPath: "path/to/audio-provider.dll" | null,
  providerPresetJson: "...",             // Provider 自有预设 JSON
  providerResources: [{ kind: "vpf", path: "..." }],  // 资源透传（如 VPF）
  providerMode: "headphone" | "speaker", // 缺省 "speaker"
} | null);                                // null = 关闭全部音效
```

### IR 卷积（内置 Basic DSP）

- 支持 **mono / stereo / 四声道真立体**（通道序 `[LL, LR, RL, RR]`）IRS 文件，其余声道布局直接拒绝而非重混音；
- IR 时长上限 **8 秒**（`MAX_IR_SECONDS = 8.0`），超长直接拒绝；超过 50ms 的前导静音会被裁剪；
- 分块卷积器（256 帧早块 + 1024 帧晚块），算法延迟约 5.3ms @48kHz，干路按报告延迟对齐后混合，避免梳状滤波；
- 默认**全湿**（`impulseResponseMix = 1.0`），保留 IR 原始增益；立体声联动限幅器只在削波风险时介入；
- EQ 在 Provider 激活时被旁路（Provider 拥有完整 DSP 图），切回 Basic DSP 后恢复。

### DSP Provider（热插拔外部音效引擎）

外部原生音效引擎以 C ABI（`EchoDspApi`，当前 v2）动态加载进播放器进程，托管完整 DSP 图（EQ/卷积/限幅之外的供应商特效）。架构详见上游 `docs/dsp-provider-architecture.md`。

| API | 说明 |
|-----|------|
| `selectDspProvider(mode)` | 选择已安装 Provider（`"headphone" \| "speaker"`，缺省 `"speaker"`），返回 `DspProviderRecord \| null` |
| `listDspProviders()` | 已安装 Provider 列表 |
| `inspectDspProvider(path)` | 导入前检查 Provider 文件（ABI / manifest / 能力） |
| `deleteDspProvider(providerId)` | 删除 Provider（先切回 Basic DSP，再异步回收二进制） |

`DspProviderRecord` 含 `providerId`（逻辑身份，跨平台）、`providerVersion`、`latencyFrames`、`preferredBlockFrames`、`maxChannels`、`manifestJson`、`stateJson`、`path`、`contentHash`（SHA-256 内容寻址的不可变版本）等。已安装二进制以内容哈希编址，重复导入相同内容不重写，同 ID 不同内容走"候选版本 → 校验 → 原子推进元数据"的可回滚事务。

音效文件（IRS/VPF）的导入、下载与删除见[系统功能集成](system-features)的音频特效管理。

---

## 音频图（Audio Graph）

引擎处理图的实时快照与在线调参（EQ 级联增益、卷积混音比、Provider 状态等都在快照中）：

| API | 说明 |
|-----|------|
| `getAudioGraph()` | `Promise<PlayerAudioGraphSnapshot \| null>` 当前图快照 |
| `setAudioGraphParameter(patch)` | 运行时调整单个节点参数 |
| `setAudioGraphPlan(plan)` | 调整处理计划 |
| `onAudioGraphChange(fn)` | 图结构/状态变化推送 |

---

## 音频设备与输出

| API | 说明 |
|-----|------|
| `getAudioDevices()` | 设备列表 `{ name, description, isDefault? }[]` |
| `setAudioOutput(deviceName, exclusive)` | 切换输出设备；`exclusive=true` 为独占模式（WASAPI / CoreAudio / ALSA 独占，绕过系统混音器） |
| `setPauseOnDeviceDisconnect(bool)` | 设备断开（拔耳机）时自动暂停 |
| `onAudioDeviceListChanged(fn)` | 设备热插拔通知（含变化类型与断开设备列表） |

---

## 引擎级网络与缓冲

| API | 层级 | 说明 |
|-----|------|------|
| `setStallTimeout(seconds)` | preload | 播放停滞判定超时 |
| `set_http_proxy(proxy)` / `set_http_proxies(proxies[])` | 引擎（主进程经 echo-audio-player 调用） | 引擎流媒体 HTTP 代理（配合主进程[网络设置](system-features)自动下发） |
| `set_network_timeout(seconds)` | 引擎 | 引擎网络超时 |

| 事件 | 说明 |
|------|------|
| `onStall(fn)` | 播放停滞（参数为当前位置） |
| `onPacketCacheStats(fn)` | 前向/后向缓存字节数、可 seek 区间、EOF 状态等 |

---

## 会话与状态

| API | 说明 |
|-----|------|
| `available()` | 引擎是否可用（原生模块加载成功） |
| `restart()` | 重启引擎（崩溃恢复），返回是否成功 |
| `getState()` | 引擎内部状态 |
| `getRuntimeSession()` | 读取运行时会话（供重启恢复） |
| `syncRuntimeSession(session)` | 写入运行时会话 |
| `getEmbeddedMetadata(request)` | 读取内嵌元数据（标签/封面，封面有缓存） |

---

## 音频事件

| API | 回调参数 | 说明 |
|-----|----------|------|
| `onTimeUpdate(fn)` | `number \| { time?, trackSeq?, generation?, sampledAt? }` | 播放进度（秒） |
| `onDurationChange(fn)` | `(duration: number)` | 时长变化 |
| `onStateChange(fn)` | `{ playing?, paused?, timePos?, ... }` | 播放/暂停状态 |
| `onPlaybackEnd(fn)` | `(reason, context?)` | 播放结束（eof / stop / error，附 trackSeq/generation） |
| `onError(fn)` | `(payload: PlayerErrorPayload)` | 引擎错误 |
| `onSeeked(fn)` | `(time: number)` | seek 完成 |
| `onSeekStateChange(fn)` | `{ active, time?, ... }` | seek 过程状态 |
| `onPlaybackRestart(fn)` | `{ time?, reason? }` | 引擎/播放重启恢复 |
| `onFileLoaded(fn)` | `{ path?, seq?, trackSeq?, generation?, startTime?, transition? }` | 文件加载完成（含过渡信息） |
| `onCoreStateChange(fn)` | `{ state?, reason?, ... }` | 引擎核心状态 |
| `onAoStateChange(fn)` | `{ paused?, bufferingState?, bufferedSecs?, targetSecs?, ... }` | 输出端缓冲/暂停状态 |
| `onAudioOutputStats(fn)` | `{ backend, sampleRate, channels, format, bufferSecs, delaySecs, underruns, ... }` | 输出统计（后端/缓冲/欠载） |
| `onAudioGraphChange(fn)` | `PlayerAudioGraphSnapshot?` | 音频图变化 |
| `onStall(fn)` / `onPacketCacheStats(fn)` | 见上节 | 网络与缓存 |
| `onAudioDeviceListChanged(fn)` | 见上节 | 设备热插拔 |

所有事件监听器返回取消函数。`trackSeq` / `generation` 用于区分事件归属的曲目与引擎代际，防止异步事件串轨。

---

## 📂 相关文档

- [内部 API 概览](/develop/internal-api/) — 模块总览
- [播放状态与持久化](/develop/internal-api/playback-state) — 队列持久化与 API 服务
- [窗口与交互管理](/develop/internal-api/window-management) — 窗口组件与网络投放
- [系统功能集成](/develop/internal-api/system-features) — 音效文件管理、网络设置
- [原生模块](/develop/native-addons) — echo-audio-player crate 细节
