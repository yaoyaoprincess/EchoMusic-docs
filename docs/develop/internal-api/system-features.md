---
title: 系统功能集成
outline: [2, 4]
---

# ⚙️ 系统功能集成

快捷键、电源管理、网络设置、应用更新、日志与诊断、音效资源管理、窗口合成、下载引擎、本地音乐扫描等主进程能力。

---

## 快捷键（electron.shortcuts）

| API | 说明 |
|-----|------|
| `register({ enabled, shortcutMap })` | 注册应用内快捷键映射（`ShortcutRegistrationResult`） |
| `refresh()` | 重新应用当前注册 |
| `setLocalEditableActive(active)` | 通知主进程输入框编辑态（应用内快捷键在编辑文本时让位） |
| `registerPluginGlobal(payload)` | 注册**插件全局**快捷键（系统级，应用后台也生效） |
| `unregisterPluginGlobal({ pluginId, registrationId })` | 注销插件全局快捷键 |
| `onTrigger(fn)` | 应用内快捷键触发（回调为命令名） |
| `onPluginGlobalTrigger(fn)` | 插件全局快捷键触发（回调含 `pluginId` / `registrationId`） |

```js
electron.shortcuts.register({
  enabled: true,
  shortcutMap: { "toggle-visualizer": "Ctrl+Shift+V" },
});
electron.shortcuts.onTrigger((command) => { /* ... */ });
```

按键组合兼容 Electron accelerator 语法（`Ctrl+Shift+Key`、`CommandOrControl+Key` 等）。插件全局快捷键面向插件开放（`ctx.shortcuts`），见[插件快捷键](/develop/plugin-dev/context-api)。

---

## 电源管理（electron.power）

| API | 说明 |
|-----|------|
| `onResume(fn)` | 系统从休眠唤醒，返回取消函数 |
| `executeSleepTimerAction(action)` | 执行睡眠定时器动作（`"pause" \| "quit" \| "shutdown"` 中除 `"pause"` 外的动作），返回 `{ ok } \| { ok: false, error }` |

> ⚠️ 历史版本文档中的 `onSuspend` **不存在**：渲染进程只接收 `power:resume` 广播。休眠前的处理完全在主进程。

主进程 `src/main/powerMonitor.ts` 职责：

- **suspend**：若在播放则暂停（让音频输出干净 idle）并释放 power-save-blocker；
- **resume**：恢复网络会话（代理重应用）、重建音频输出设备、按需恢复播放，并广播 `power:resume` 让渲染进程重新枚举设备；
- Windows 上 `unlock-screen` 仅作为"已确认 suspend 但 resume 丢失"的兜底，普通锁屏解锁不打断播放。

睡眠定时器（主进程 `sleepTimer`）到点后通过 `executeSleepTimerAction` 落地 `pause` / `quit` / `shutdown` 三种动作。

---

## 定时关机（systemShutdown.ts）

主进程模块，`requestSystemShutdown()` 按平台调用固定命令（无 shell、无 sudo、不强制关闭应用）：

| 平台 | 命令 |
|------|------|
| macOS | `/usr/bin/osascript -e 'tell application "System Events" to shut down'` |
| Windows | `shutdown.exe /s /t 0` |
| Linux | `/usr/bin/systemctl poweroff` |

---

## 网络设置（electron.network）

| API | 说明 |
|-----|------|
| `get()` | `Promise<NetworkSettingsState>` 当前网络设置 |
| `update(request)` | 更新设置（带密码等敏感字段，`NetworkSettingsUpdateRequest`） |

五种代理模式（`src/shared/network.ts` 的 `NetworkProxyMode`）：`'system'`（跟随系统）、`'direct'`（直连）、`'auto_detect'`（自动检测）、`'pac_script'`（PAC 脚本）、`'fixed_servers'`（固定代理规则，支持 bypass 列表与认证）。

主进程 `src/main/networkSettings.ts` + `src/main/networkPolicy.ts` 将代理**统一覆盖**：酷狗 API 请求、封面/图片、音频直链、应用更新（electron-updater）、插件网络请求。实现上按用途划分 Electron session 分区（`echo-app-network` / `echo-kugou-api` / `echo-community-audio` / `persist:desktop-lyric` / `electron-updater`），分别套用代理与凭证；引擎级流媒体代理另经 `echo-audio-player` 的 `set_http_proxy(s)` 下发（见[音频引擎](audio-engine)）。唤醒后的网络恢复也在此层完成（见电源管理）。

---

## 更新器（electron.updater）

| API | 说明 |
|-----|------|
| `download()` | 开始下载最新更新 |
| `cancelDownload()` | 取消下载 |
| `install(silent?)` | 安装更新（`silent=true` 不弹窗） |
| `getState()` | `Promise<UpdateState>` 当前更新状态 |
| `onDownloadStatus(fn)` | 下载进度监听，返回取消函数 |

---

## 应用信息（electron.appInfo）

| API | 说明 |
|-----|------|
| `get()` | 版本、平台、架构等 `{ version, platform, arch, ... }` |
| `getChangelog()` | 更新日志文本 |
| `relaunch()` | 重启应用（返回是否受理） |
| `onOpenSettings(fn)` | 主进程请求打开设置页（可带 section），返回取消函数 |

---

## 日志与诊断（electron.log / electron.logging / electron.diagnostics）

```js
// 结构化日志（electron-log 渲染端封装）
electron.log.info("操作成功");
electron.log.error("处理失败", { details: "..." });
```

| API | 说明 |
|-----|------|
| `logging.get()` / `logging.update(settings)` | 日志设置（级别等，`LogSettings`） |
| `diagnostics.getMemory(label?)` | 内存诊断快照：渲染进程内存（工作集/私有/堆）、`performance.memory`、`webFrame` 资源用量、全部应用进程指标 |

主进程侧配套 `src/main/eventLoopMonitor.ts`（事件循环阻塞监测）与 `src/main/diagnostics/`（`memory.ts` 进程内存采样）。原生日志经 echo-native-log 桥接进统一日志流（见[原生模块](/develop/native-addons)）。

---

## 音频特效管理（electron.audioEffects）

管理 IRS / VPF 等音效资源文件（生效走 `player.setAudioEffect`，见[音频引擎](audio-engine)）：

| API | 说明 |
|-----|------|
| `importImpulseResponse()` | 打开文件选择器导入音效文件（`ImportImpulseResponseResult`） |
| `downloadCommunityAudioEffect(payload)` | 下载社区音效（`DownloadCommunityAudioEffectRequest/Result`） |
| `deleteAudioEffect(filePath)` | 删除音效文件 |
| `reconcileAudioEffects(files)` | 以渲染侧列表为准同步音效文件（清理孤儿文件，返回存活条目） |

> ⚠️ 历史版本文档中的 `deleteImpulseResponse` / `reconcileImpulseResponses` **不存在**，实际为 `deleteAudioEffect` / `reconcileAudioEffects`。

---

## 窗口合成与背景（主进程）

跨平台窗口背景/合成策略，preload 无直接 API，由设置页经 IPC 间接触发：

| 模块 | 平台 | 说明 |
|------|------|------|
| `src/main/window/windowsComposition.ts` | Windows | DWM 透明 / Accent 亚克力合成（与 `echo-platform-adaptor` 协同，含 Win11 22H2+ `setBackgroundMaterial` 与 Win10 Accent 模式） |
| `src/main/window/backgroundMaterial.ts` | Windows | Electron `setBackgroundMaterial` 封装 |
| `src/main/window/hyprlandBackground.ts`（+ `hyprlandBlurQueue.ts`） | Linux | Hyprland 合成器窗口模糊（layer-shell 协议，队列化避免闪烁） |
| `src/main/window/macComposition.ts` | macOS | macOS 振动材质/透明背景 |
| `src/main/windowDrag.ts` / `windowSizing.ts` | 全平台 | 自绘标题栏拖拽与窗口尺寸约束 |
| `src/main/windowBoundsPersistence.ts` | 全平台 | 窗口位置尺寸持久化 |
| `src/main/windowBackgroundThrottling.ts` | 全平台 | 背景窗口节流控制 |

窗口透明失败时回退纯色背景；诊断信息可在 Windows 外观设置中一键复制（Accent/DWM backdrop/分层样式读回）。

---

## 其他主进程能力

| 模块 | 说明 |
|------|------|
| `src/main/macBackgroundMode.ts` | macOS 后台运行：按关闭偏好隐藏 Dock（`app.dock.hide()`）与菜单栏，托盘可见性联动，退出时恢复 |
| `src/main/downloads/engine.ts`（+ `files.ts`） | 下载引擎：歌曲/文件下载任务、进度与落盘管理 |
| `src/main/localMusic.ts` + `src/main/media/fileScanner.ts` + `src/main/media/audioMetadata.ts` | 本地音乐：目录扫描、去重、内嵌元数据（标签/封面）解析 |
| `src/main/avatarUpload.ts` | 头像上传（文件读取与尺寸校验） |
| `src/main/plugins/index.ts` 等 | 插件运行时与**安全模式**：`plugins.setSafeMode(enabled)`，应用可带 `--safe-mode` 启动禁用全部插件（故障恢复），详见[插件系统](/develop/plugin-dev/getting-started) |
| `src/main/share.ts` / `src/main/ipc/cloud.ts` | 剪贴板/截图分享、云盘文件选择与读取（`electron.share` / `electron.cloud`） |
| `src/main/opencc/` + `src/main/ipc/opencc.ts` | 歌词简繁转换（`electron.opencc.convertBatch`，底层 echo-opencc） |
| `src/main/audioCapture.ts` + `src/main/ipc/recognize.ts` | 听歌识曲采集（`electron.recognize.*`，底层 echo-audio-capture） |
| `src/main/audioSpectrum.ts` | 音频频谱订阅分发（`electron.audioSpectrum.*`，底层引擎频谱） |
| `src/main/external/index.ts` | 外部歌单/链接解析（`electron.external.resolvePlaylist`，支持酷狗/网易/QQ/汽水/Spotify/Apple 等 providers） |

---

## 📂 相关文档

- [内部 API 概览](/develop/internal-api/) — 模块总览
- [音频引擎](/develop/internal-api/audio-engine) — 音效生效路径与引擎网络
- [播放状态与持久化](/develop/internal-api/playback-state) — 设置备份与 API 服务
- [窗口与交互管理](/develop/internal-api/window-management) — 任务栏集成与窗口控制
- [原生模块](/develop/native-addons) — echo-platform-adaptor 平台适配
