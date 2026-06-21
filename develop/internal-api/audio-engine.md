---
title: 音频引擎（ctx.audio）
outline: [2, 4]
---

# 🎵 音频引擎（ctx.audio）

EchoMusic 底层使用 **libmpv** 作为音频引擎，通过 `ctx.audio` 在同一渲染进程中控制。

---

## 均衡器（EQ）

18 段参数化均衡器，每段独立控制增益（-12 ~ +12 dB）。

```js
ctx.audio.setEqualizer([
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

EQ 频段：`32 / 64 / 125 / 250 / 500 / 1k / 2k / 4k / 8k / 16k` Hz

---

## 空间音效（Spatial Audio）

```js
ctx.audio.setSpatialAudio({
  preset: "hall",     // "hall" | "church" | "studio" | "theater"
  dryWet: 0.5,        // 干湿比 (0.0 = 纯原声, 1.0 = 纯效果)
});
// 关闭：{ preset: null }
```

---

## 脉冲响应（IR Convolution）

```js
ctx.audio.setImpulseResponse({
  path: "path/to/ir-file.wav",
  dryWet: 0.6,
});
// 或直接传路径：ctx.audio.setImpulseResponse("path/to/ir-file.wav")
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `path` | `string` | IR 音频文件的绝对路径 |
| `dryWet` | `number` (0-1) | 干湿混合比 |

---

## 音频设备控制

| API | 说明 |
|-----|------|
| `getAudioDevices()` | 获取可用音频设备列表 |
| `setAudioDevice(name)` | 切换音频输出设备 |
| `setExclusive(bool)` | 独占模式开关（绕过系统混音器） |
| `getAudioFilter()` | 获取当前生效的音效滤波器名 |

```js
const devices = await ctx.audio.getAudioDevices();
await ctx.audio.setAudioDevice("Speakers");
await ctx.audio.setExclusive(true);
```

---

## 音量渐变（Fade）

| API | 说明 |
|-----|------|
| `fade(from, to, durationMs)` | 从 `from` 渐变到 `to` |
| `cancelFade()` | 取消正在进行的渐变 |
| `pauseWithFade(savedVol, durationMs)` | 渐弱暂停 |
| `playWithFade(targetVol, durationMs)` | 渐强恢复 |

```js
ctx.audio.fade(currentVol, 30, 2000);
ctx.audio.pauseWithFade(20, 1500);
ctx.audio.playWithFade(80, 1000);
```

---

## 响度归一化

```js
ctx.audio.setNormalizationGain(-3.5); // dB
```

---

## 文件和轨道

| API | 说明 |
|-----|------|
| `loadFile(url, track?)` | 加载音频文件或 MKV 音轨 |
| `getTrackList()` | 获取 MKV 轨道列表 |
| `setLoopFile(bool)` | 单曲循环 |
| `setMediaTitle(title)` | 设置媒体标题 |

---

## 引擎控制

| API | 说明 |
|-----|------|
| `available()` | 检查 mpv 引擎是否可用 |
| `restart()` | 重启播放引擎 |
| `getState()` | 获取引擎内部状态 |

---

## 音频事件

| API | 回调参数 | 说明 |
|-----|----------|------|
| `onTimeUpdate(fn)` | `(time: number)` | 播放时间更新（秒） |
| `onDurationChange(fn)` | `(duration: number)` | 歌曲时长变化 |
| `onStateChange(fn)` | `({playing?, paused?})` | 播放/暂停状态变化 |
| `onPlaybackEnd(fn)` | `(reason: string)` | 播放结束 ("eof" / "stop" / "error") |
| `onError(fn)` | `(message: string)` | mpv 引擎错误 |
| `onAudioDeviceListChanged(fn)` | `(devices[])` | 设备列表变化（拔插耳机） |
| `onImpulseResponseDisabled(fn)` | `({path?, reason?})` | IR 被自动禁用通知 |

所有事件监听器返回取消函数。

---

## 📂 相关文档

- [内部 API 概览 →](./) — 四大模块速览
- [播放状态与持久化 →](playback-state) — 播放事件与队列持久化
- [窗口与交互管理 →](window-management) — 窗口组件管理
- [系统功能集成 →](system-features) — 快捷键、更新、日志等
