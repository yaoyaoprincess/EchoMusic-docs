---
title: 内部 API 参考
outline: [2, 4]
---

# 🔧 内部 API 参考

> ⚠️ **本文档仅供核心开发参考。** 以下 API 属于 EchoMusic 主进程/渲染进程内部接口，**不暴露给插件**（插件有独立的受限 API 子集）。插件开发请参阅 [插件 API 总览 →](/develop/plugin-dev/context-api)。

EchoMusic 的内部 API 通过 preload 脚本 `src/preload/index.ts` 的唯一 `contextBridge.exposeInMainWorld('electron', ...)` 暴露为 `window.electron`，覆盖音频引擎、窗口管理、系统集成、持久化等 25+ 个 API 组。按功能分为四类：

| 模块 | 说明 | 入口 |
|------|------|:--:|
| 🎵 音频引擎 | Rust 引擎：加载/无缝切歌、歌曲过渡、EQ、音效与 DSP Provider、音频图、设备、事件 | [→](/develop/internal-api/audio-engine) |
| 📡 播放状态与持久化 | 多队列存储、历史、键值、设置备份、API 服务、HTTP 请求代理 | [→](/develop/internal-api/playback-state) |
| 🖥️ 窗口与交互管理 | 任务栏四件套、网络投放（DLNA/AirPlay）、桌面歌词、Mini 播放器、窗口控制、托盘 | [→](/develop/internal-api/window-management) |
| ⚙️ 系统功能集成 | 快捷键、电源、网络设置、更新、日志诊断、音效文件、窗口合成等 | [→](/develop/internal-api/system-features) |

---

## API 组总览

`window.electron` 实际暴露的全部 API 组（另含顶层字段 `platform`、`isWayland`、`notifyPageMounted()` 与启动参数注入的 `echoInitialDark` / `echoWindowBackground`）：

### 有专页的 API 组

| API 组 | 一句话说明 | 文档 |
|--------|------------|:--:|
| `player` | 音频引擎全量控制：加载/切换源、过渡、EQ、音效、设备、事件 | [音频引擎](/develop/internal-api/audio-engine) |
| `storage` | 播放快照/多队列/历史/键值的持久化读写 | [播放状态与持久化](/develop/internal-api/playback-state) |
| `apiServer` | 酷狗 API 进程内宿主（`start` / `status` / `identity`） | [播放状态与持久化](/develop/internal-api/playback-state) |
| `settingsBackup` | 设置与数据备份导出/检查/导入 | [播放状态与持久化](/develop/internal-api/playback-state) |
| `desktopLyric` | 桌面歌词悬浮窗（含拖拽/缩放会话） | [窗口与交互管理](/develop/internal-api/window-management) |
| `nowPlaying` | 正在播放快照同步与命令通道 | [窗口与交互管理](/develop/internal-api/window-management) |
| `taskbarLyric` | Windows 任务栏歌词（状态/设置/宽度） | [窗口与交互管理](/develop/internal-api/window-management) |
| `miniPlayer` | Mini 播放器悬浮窗 | [窗口与交互管理](/develop/internal-api/window-management) |
| `windowControl` | 当前窗口最小化/最大化/关闭/全屏 | [窗口与交互管理](/develop/internal-api/window-management) |
| `output` | 网络投放（DLNA / AirPlay 目标发现与会话） | [窗口与交互管理](/develop/internal-api/window-management) |
| `tray` | 托盘播放状态同步与播放模式 | [窗口与交互管理](/develop/internal-api/window-management) |
| `shortcuts` | 应用内与插件全局快捷键 | [系统功能集成](/develop/internal-api/system-features) |
| `power` | 唤醒通知与睡眠定时器动作 | [系统功能集成](/develop/internal-api/system-features) |
| `network` | 代理设置（5 种模式） | [系统功能集成](/develop/internal-api/system-features) |
| `updater` | 应用更新下载/取消/安装/状态 | [系统功能集成](/develop/internal-api/system-features) |
| `appInfo` | 版本信息、更新日志、重启、打开设置 | [系统功能集成](/develop/internal-api/system-features) |
| `log` / `logging` | 结构化日志与日志设置 | [系统功能集成](/develop/internal-api/system-features) |
| `diagnostics` | 内存与进程诊断快照 | [系统功能集成](/develop/internal-api/system-features) |
| `audioEffects` | 音效资源导入/下载/删除/同步 | [系统功能集成](/develop/internal-api/system-features) |

### 本页简述的 API 组

| API 组 | 一句话说明 |
|--------|------------|
| `ipcRenderer` | 受限的 `send` / `invoke` / `on` / `off` 直通层（payload 统一做可序列化净化），一般不直接使用 |
| `api` | 主进程代理 HTTP 客户端 `api.request(config)`，支持二进制体透传 |
| `cloud` | 云盘上传的文件挑选与读取（`pickUploadFiles` / `readUploadFileData` / `clearUploadFiles`） |
| `share` | 文本复制、剪贴板读取、区域截图（`captureRectToClipboard`）与分享目标打开 |
| `fonts` | 系统字体枚举（`getAll()`） |
| `opencc` | 歌词简繁批量转换 `convertBatch(texts, profile)`（5 种 profile，底层 echo-opencc） |
| `recognize` | 听歌识曲采集（设备枚举/启动/停止/取消，底层 echo-audio-capture，PCM 经 `api.request` 二进制通道上传） |
| `audioSpectrum` | 引擎频谱订阅（`getStatus` / `getSnapshot` / `subscribe(options, fn)`，返回句柄） |
| `external` | 外部歌单/链接解析 `resolvePlaylist(req)`（酷狗/网易/QQ/汽水/Spotify/Apple Music 等） |
| `mediaControls` | 系统媒体控制同步（元数据/状态/时间轴/快进步长，底层 SMTC / MPRIS / MPNowPlayingInfoCenter） |
| `plugins` | 插件系统全量接口（安装/市场/文件/网络/数据库/窗口/备份等）——**有独立专页**，见[插件 API 总览](/develop/plugin-dev/context-api) |

> 插件市场的匿名统计上报（安装量等聚合数据）由主进程 `src/main/plugins/marketplaceStats.ts` 收集，机制见[插件市场统计上报](/develop/plugin-dev/marketplace-stats)。

---

## 📂 相关文档

- [插件 API 总览](/develop/plugin-dev/context-api) — 插件可用的正式 API
- [项目架构](/develop/architecture) — EchoMusic 整体架构
- [项目结构](/develop/project-structure) — 完整目录结构
- [原生模块](/develop/native-addons) — Rust NAPI 原生扩展
- [KuGou API 参考](/develop/kugou-api) — 酷狗音乐公开 API
