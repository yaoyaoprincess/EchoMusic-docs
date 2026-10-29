---
title: 原生模块 (Rust NAPI)
---

# 🦀 原生模块 (Rust NAPI)

EchoMusic 的性能敏感与平台敏感能力由 **9 个 Rust crate** 承担，通过 [napi-rs](https://napi.rs/) 框架（**NAPI 3**）编译为 Node.js 原生模块（`.node`），在 **Electron 主进程**中直接加载调用。渲染进程不直接接触原生模块——所有调用都经主进程封装后通过 IPC（`window.electron`）暴露。

- Rust 工具链要求 **rust-version 1.87**（各 crate 统一）。
- NAPI 依赖统一为 `napi = { version = "3", features = ["napi9", ...] }`：播放器额外启用 `serde-json` 与 `tokio_rt`，需要异步运行时的模块启用 `tokio_rt`。
- 每个 crate 构建产物是**与 crate 同名的 `.node` 文件**（如 `native/echo-audio-capture/echo-audio-capture.node`），由 napi-rs CLI 生成并附带 `index.d.ts` 类型声明，**不是**手动的 `index.node` 重命名。

## 模块总览

8 个随安装包分发，1 个仅作为内部依赖：

| 模块 | 功能 | 分发平台 |
|------|------|----------|
| `echo-audio-player` | 播放、解码及音效处理（FFmpeg + SoundTouch） | macOS / Windows / Linux |
| `echo-audio-capture` | 系统音频和麦克风采集（听歌识曲） | macOS / Windows / Linux |
| `echo-media-controls` | 系统媒体控制（SMTC / MPRIS / MPNowPlayingInfoCenter） | macOS / Windows / Linux |
| `echo-sqlite-store` | SQLite 持久化存储 | macOS / Windows / Linux |
| `echo-opencc` | 歌词简繁转换 | macOS / Windows / Linux |
| `echo-upnp` | DLNA / UPnP 设备控制 | macOS / Windows / Linux |
| `echo-airplay` | AirPlay 设备发现与音频发送 | macOS / Windows / Linux |
| `echo-platform-adaptor` | 系统窗口、任务栏等平台适配 | macOS / Windows（Linux 不构建、不打包） |
| `echo-native-log`（内部依赖） | 原生 → 主进程日志桥，供其他 crate 依赖 | —（不随安装包分发） |

> 各 crate 均为**函数式导出**（`#[napi]` 标注的自由函数），不使用类封装。下文按 crate 逐一说明用途、平台与导出的 NAPI 函数签名。

---

## echo-audio-player — 播放引擎

核心播放引擎：FFmpeg 解码 + 音效处理 + 输出。全部 DSP 在播放进程内完成，无 sidecar 进程、无 PCM IPC。

```toml
[dependencies]
napi = { version = "3", features = ["napi9", "serde-json", "tokio_rt"] }
ffmpeg_audio = { path = "vendor/ffmpeg-audio/crates/ffmpeg_audio", features = ["http"] }
cpal = "0.18"
fundsp = "0.23"
libloading = "0.8"
rubato = "0.16"
rustfft = "6.4"
soundtouch-rs = { path = "vendor/soundtouch-rs" }
```

### 关键依赖与子系统

| 依赖 / 子系统 | 说明 |
|---------------|------|
| FFmpeg（vendored） | 完整路径 `native/echo-audio-player/vendor/ffmpeg-audio/crates/ffmpeg_audio_sys/vendor/`。`ffmpeg-audio` 本身也是 vendored 的（含 `ffmpeg_audio` / `ffmpeg_audio_sys` / `ffmpeg_wasm` / `soundtouch` crates），构建时从 `ffmpeg_slim.zip` 解包，无需系统 FFmpeg |
| cpal 0.18 | 跨平台音频输出。Linux 启用 `pipewire` / `pulseaudio` features（PipeWire / PulseAudio 后端）；Windows WASAPI、macOS CoreAudio、Linux ALSA 提供独占输出（`src/output/wasapi.rs`、`coreaudio_exclusive.rs`、`alsa_exclusive.rs`、`cpal_shared.rs`） |
| fundsp + rustfft | 内置均衡器与 IR 卷积等基础 DSP（`src/dsp/basic.rs`、`src/dsp/limiter.rs`） |
| soundtouch-rs（vendored） | 变速（WSOLA）引擎 |
| rubato | 高质量重采样 |
| libloading | 运行时动态加载外部 DSP Provider（`src/dsp/provider.rs`） |
| `src/transition/` | 歌曲过渡子系统：8 个 JSON 过渡计划（`plans/` 下 `echo_tail`、`fallback_exchange`、`filter_eq`、`layered_filter`、`simple_exchange`、`simple_filter`、`smooth_filter`、`three_band`）+ 分析（`analysis.rs`）、决策（`decide.rs`）、混音（`mixer.rs`）、计划（`plan.rs`）、效果（`effects.rs`） |
| `src/tempo.rs` | 变速双引擎：谱减相位声码器（spectral phase vocoder）+ SoundTouch（WSOLA），速度范围 **0.1x – 5x**（`MIN_SPEED = 0.1`，`MAX_SPEED = 5.0`） |
| `src/audio_graph.rs` | 音频处理图快照与运行时参数/计划调整 |
| `src/stream/` | HTTP 流（含代理、超时、暂停缓存）、本地文件、URL 解析 |
| `src/device/` | 输出设备枚举/选择/热插拔监听（`watcher.rs`、`selection.rs`、各平台 `platform_*.rs`） |
| `src/spectrum.rs` | 引擎内置实时频谱（供音频频谱可视化订阅） |
| `src/embedded_metadata.rs` | 内嵌元数据（标签/封面）读取 |
| `src/output/airplay_tap.rs` | AirPlay 发送时的输出分接 |

### 导出的 NAPI 函数

初始化与事件：

| 函数 | 签名 | 说明 |
|------|------|------|
| `initialize` | `(config: PlayerConfigOptions \| null) → void` | 初始化引擎（缓冲、采样率/声道/格式策略、无缝策略、缓存、网络超时、HTTP 代理等，见 `src/config.rs`） |
| `destroy` | `() → void` | 释放引擎 |
| `register_event_handler` | `(callback: EventCallback) → void` | 注册播放事件回调（进度、状态、结束、错误、设备变化等） |
| `register_log_handler` | `(callback) → void` | 注册日志回调（经 echo-native-log 桥接到主进程 electron-log） |

加载与音源切换（无缝切歌 / 音源切换组）：

| 函数 | 签名 |
|------|------|
| `begin_source_change` | `() → void` |
| `load_file` | `(url: string, seq?: number) → AsyncTask` |
| `load_mkv_track` | `(url: string, track_id: number, seq?: number) → AsyncTask` |
| `switch_source` | `(url: string, track_id?: number \| null, ...) → AsyncTask` |
| `begin_next_source_preparation` | `() → number`（返回 requestId） |
| `cancel_next_source_preparation` | `(request_id: number) → boolean` |
| `prepare_next_source` | `(url: string, request_id: number, track_id?: number \| null, normalization_gain_db?: number) → AsyncTask` |
| `commit_prepared_next_source` | `(transition_ms?: number) → ...` |
| `clear_prepared_next_source` | `() → void` |
| `get_track_list` | `(url?: string) → AsyncTask` |

播放控制与基础处理：

| 函数 | 签名 |
|------|------|
| `play` / `pause` / `stop` | `() → AsyncTask / void` |
| `seek` | `(time: f64) → AsyncTask` |
| `set_volume` | `(volume: f64) → void` |
| `set_speed` | `(speed: f64) → AsyncTask`（0.1x – 5x，双引擎） |
| `set_equalizer` | `(gains: Vec<f64>) → AsyncTask`（10 段） |
| `set_audio_effect` | `(payload: JSON) → AsyncTask`（IR / VPF 资源 + DSP Provider 配置） |
| `set_normalization_gain` | `(gain_db: f64) → AsyncTask` |
| `fade` / `cancel_fade` / `pause_with_fade` / `play_with_fade` | 音量渐变组 |
| `set_loop_file` | `(loop_file: bool) → void` |
| `get_state` | `() → PlayerState` |
| `get_embedded_metadata` | `(request) → ...` |

输出设备与网络：

| 函数 | 签名 |
|------|------|
| `set_audio_output` | `(device_name: string, exclusive: bool) → AsyncTask` |
| `get_audio_devices` | `() → AsyncTask` |
| `set_pause_on_device_disconnect` | `(enabled: bool) → void` |
| `set_stall_timeout` | `(seconds: f64) → void` |
| `set_network_timeout` | `(seconds: f64) → void` |
| `set_http_proxy` | `(proxy: string) → void` |
| `set_http_proxies` | `(proxies: Vec<string>) → void` |

音频图 / 过渡 / 频谱 / Provider：

| 函数 | 签名 |
|------|------|
| `get_audio_graph` / `set_audio_graph_parameter` / `set_audio_graph_plan` | 音频图快照与运行时调整 |
| `set_transition_settings` / `get_transition_settings` / `get_transition_diagnostics` | 歌曲过渡模式（`none` / `gapless` / `fade` / `automix-basic` / `automix-pro`）、淡入淡出时长、节奏匹配 |
| `inspect_dsp_provider` | `(path: string) → AsyncTask`（导入前检查外部 Provider） |
| `configure_spectrum` / `get_spectrum_status` / `get_spectrum_snapshot` | 频谱配置与帧快照 |

### JS 侧封装

主进程封装位于 `src/main/player/`：`controller.ts`（约 44KB，引擎生命周期与 IPC 命令映射）、`session.ts`（运行时会话）、`dspProviderRegistry.ts`（已安装 Provider 注册表）、`audioEffectCommand.ts`、`embeddedMetadata.ts` 等。渲染进程通过 `electron.player.*`（preload）调用，详见[音频引擎](/develop/internal-api/audio-engine)。

---

## echo-media-controls — 系统媒体控制

对接各操作系统的原生媒体控制 API，函数式导出：

| 平台 | API |
|------|-----|
| Windows | SMTC（WinRT `SystemMediaTransportControls`，`windows` 0.62 crate） |
| Linux | MPRIS（D-Bus，`mpris-server` crate） |
| macOS | MPNowPlayingInfoCenter / MPRemoteCommandCenter（`objc2-media-player`） |

**NAPI 导出**：

| 函数 | 签名 | 说明 |
|------|------|------|
| `initialize` | `(app_name: string) → void` | 初始化媒体控制会话 |
| `shutdown` | `() → void` | 关闭会话 |
| `register_log_handler` | `(callback) → void` | 日志桥接 |
| `update_metadata` | `(payload: { title, artist, album, coverUrl?, durationMs? }) → AsyncTask` | 更新曲目元数据（封面按 URL 加载） |
| `update_play_state` | `(payload: { status, playbackRate }) → void` | 播放/暂停状态 |
| `update_timeline` | `(payload: { currentTimeMs, totalTimeMs, isPlaying, playbackRate }) → void` | 进度条 |
| `update_skip_intervals` | `(payload: { forwardMs, backwardMs }) → void` | 快进/快退步长 |
| `register_event_handler` | `(callback: ThreadsafeFunction<MediaControlEvent>) → void` | 系统媒体键事件（play/pause/next/previous/seek 等） |

主进程封装为 `src/main/mediaControls.ts`，preload 暴露为 `electron.mediaControls.*`。

---

## echo-sqlite-store — SQLite 持久化

基于 `rusqlite 0.32`（`bundled` + `backup` features，SQLite 静态编译进二进制）的持久化存储。**函数式导出**（无 `Storage` 类），payload 与返回值均为 JSON 字符串（`serde_json`），由主进程 `src/main/storage/native.ts` 封装。

**数据库表**（`initialize` 时创建）：

| 表 | 主要列 | 说明 |
|----|--------|------|
| `app_kv` | `key` PK, `value_json`, `updated_at` | 通用键值存储 |
| `playback_queues` | `id` PK, `title`, `subtitle`, `cover_url`, `type`, `active`, `last_non_fm`, `current_track_id`, `filtered_invalid_count`, `queued_next_track_ids_json`, `dynamic`, `meta_json`, 时间戳 | **多队列**模型（FM / 默认 / 歌单等各自成队列） |
| `songs` | `song_key` PK, `source_id`, `hash`, `title`, `artist`, `album`, `cover_url`, `duration`, `payload_json` | 歌曲去重池 |
| `queue_items` | `(queue_id, position)` PK, `song_key`, `added_at`，外键级联 | 队列条目（有序） |
| `play_history` | `song_key` PK, `history_key` UNIQUE, `last_played_at`, `play_count` | 播放历史（按歌曲聚合） |

> ⚠️ **没有收藏表**。收藏数据属于云端酷狗账号，不经此模块持久化。

**NAPI 导出**：

```rust
initialize(database_path: String)            close()
kv_get(key) / kv_set(key, value_json)        kv_apply_batch(mutations_json)
kv_delete(key) / reset_all()
playback_get_snapshot(hydrate_all_songs?)    playback_get_queue(payload_json)
playback_replace_queue(payload_json)         playback_append_queue_items(payload_json)
playback_update_queue_meta(payload_json)     playback_clear_queue(payload_json)
playback_remove_queue(payload_json)          playback_remove_queue_item(payload_json)
playback_reorder_queue_items(payload_json)   playback_set_queue_current_track(payload_json)
playback_set_active_queue(queue_id)
history_get_entries(payload_json?)           history_record_play(payload_json)
history_remove_entries(payload_json)         history_clear()
plugin_sqlite_open(plugin_id, ...)           plugin_sqlite_close(database_id)
plugin_sqlite_close_by_prefix(prefix)        plugin_sqlite_exec(database_id, sql)
plugin_sqlite_run(database_id, sql, params?) plugin_sqlite_all(database_id, sql, params?, ...)
plugin_sqlite_transaction(database_id, statements_json)
plugin_sqlite_backup(source_path, destination_path)
```

`plugin_sqlite_*` 系列为**插件数据库**（`src/main/plugins/sqlite.ts` 消费）提供独立的库文件管理与 SQL 执行，插件侧 API 见[插件 SQLite 存储](/develop/plugin-dev/filesystem-storage)。preload 暴露为 `electron.storage.*`，API 详见[播放状态与持久化](/develop/internal-api/playback-state)。

---

## echo-audio-capture — 系统音频采集

系统音频 + 麦克风采集，用于**听歌识曲**。基于 `cpal 0.18` 采集，`rubato 0.16` 做 PCM 重采样，双声源（`system` loopback / `input` 麦克风）可混音或单选。

**NAPI 导出**：

| 函数 | 签名 | 说明 |
|------|------|------|
| `list_input_devices` | `() → Vec<CaptureDevice>` | 列出采集设备 |
| `start_capture` | `(options: CaptureStartOptions) → CaptureStatus` | 启动采集（声源、设备、采样率等） |
| `snapshot_capture` | `(options: CaptureReadOptions?) → CapturedAudio` | 读取当前已捕获的 PCM 快照 |
| `stop_capture` | `(options: CaptureReadOptions?) → CapturedAudio` | 停止并取回完整 PCM |
| `cancel_capture` | `() → void` | 取消并丢弃 |
| `get_capture_status` | `() → CaptureStatus` | 查询采集状态 |

主进程封装为 `src/main/audioCapture.ts`，preload 暴露为 `electron.recognize.*`。

---

## echo-opencc — 歌词简繁转换

基于 `opencc-fmmseg 0.12` 的中文简繁转换，供歌词渲染使用。

**NAPI 导出**：

| 函数 | 签名 | 说明 |
|------|------|------|
| `convert` | `(text: string, profile: string) → string` | 单条转换 |
| `convert_batch` | `(texts: Vec<string>, profile: string) → Vec<string>` | 批量转换（preload `opencc.convertBatch`） |

**支持的 5 种 profile**：`s2t`（简→繁）、`s2t-variants`（简→繁，含异体字变体，`tw2t(s2t(text))` 两段合成）、`t2s`（繁→简）、`s2tw`（简→台湾正体）、`s2hk`（简→香港繁体）。词典见 `native/echo-opencc/dicts/`。

主进程封装为 `src/main/opencc/` + `src/main/ipc/opencc.ts`。

---

## echo-upnp — DLNA / UPnP

包装 vendored 的 `rupnp 3.0`（`vendor/rupnp`，启用 `full_device_spec` feature），为**网络投放（DLNA）**提供设备发现与控制。

**NAPI 导出**：

| 函数 | 签名 | 说明 |
|------|------|------|
| `load_device` | `async (description_url: string) → UpnpDeviceSnapshot` | 加载设备描述文档（含缓存） |
| `action` | `async (description_url, service_id, action_name, args_xml) → string` | 调用 UPnP 服务动作 |
| `clear_device_cache` | `() → void` | 清除设备描述缓存 |

> `vendor/` 下还 vendored 了 `airplay2-rs`（拆分为 `airplay-client` / `airplay-audio` / `airplay-discovery` / `airplay-core` 等 crates），由 `echo-airplay` 复用。

主进程封装为 `src/main/mediaTransport/upnpClient.ts`（DLNA 适配器、GENA 事件订阅等在 `src/main/mediaTransport/`）。

---

## echo-airplay — AirPlay 发送端

AirPlay 音频发送端。Cargo 描述：**"EchoMusic AirPlay sender. ALAC 44100 Hz 16-bit from post-DSP i16 PCM."**——即从 DSP 处理后的 i16 PCM 编码为 ALAC 44.1kHz 16-bit 推流。复用 `echo-upnp/vendor/airplay2-rs` 的 client / audio / discovery / core crates。

**NAPI 导出**：

| 函数 | 签名 | 说明 |
|------|------|------|
| `discovery_backend` | `() → string` | 当前发现后端标识 |
| `discover` | `async (timeout_ms: u32) → Vec<AirplayFound>` | 发现 AirPlay 接收端 |
| `discover_each` | `async (...)` | 逐个发现（增量回调） |
| `connect` | `async (id: string, pin: string, initial_volume?: f64) → AirplayLink` | 连接（支持配对 PIN） |
| `disconnect` / `pause` / `resume` / `stop` | `async () → void` | 会话控制 |
| `seek` | `async (seconds: f64) → u32` | 跳转 |
| `set_volume` | `async (volume: f64) → void` | 接收端音量 |
| `flush_track` | `async () → u32` | 冲刷当前曲目 |
| `status` | `() → AirplayState` | 会话状态 |
| `clear_records` | `() → void` | 清除记录 |
| `register_log_handler` | `(callback) → void` | 日志桥接 |

主进程封装位于 `src/main/outputs/`（`outputHost.ts` 约 75KB，统一管理 DLNA / AirPlay 输出会话），preload 暴露为 `electron.output.*`，见[窗口与交互管理](/develop/internal-api/window-management)的网络投放一节。

---

## echo-platform-adaptor — 平台窗口适配

Windows 与 macOS 桌面窗口集成，负责 HWND/DWM 行为与 AppKit 本地鼠标监听；**不含** SMTC/MPRIS/Now Playing 生命周期与音频逻辑（那是 `echo-media-controls` 的事）。

| 平台 | 能力 |
|------|------|
| Windows | DWM 透明/亚克力合成（`window_composition.rs`：DWM alpha clear 与 Accent BlurBehind 后端，Win11 22H2+ 与 Electron `setBackgroundMaterial` 协同）、**任务栏歌词嵌入**（`windows/taskbar/lyric.rs`，reparent 到主任务栏 `Shell_TrayWnd`，UIA 结构通知 + WinEvent 布局）、DWM 缩略图 / Aero Peek 封面预览（`taskbar/thumbnail.rs`，BGRA/GDI 有界缓存）、原生双击监听（`double_click.rs`）、HWND 销毁顺序修正（`taskbar/window_lifecycle.rs`） |
| macOS | 主窗口本地鼠标按下监听（`macos/window_pointer.rs`，原样转发事件，不监听其他应用、无需辅助功能权限） |
| Linux | **不构建、不打包**（Linux 上不存在此 `.node`） |

上游自带的详细 README（`native/echo-platform-adaptor/README.md`）涵盖合成模式（mode 5/10/11/12）、Explorer 重启崩溃修正（Explorer 重启时 lyric HWND 只收到 `WM_NCDESTROY` 而缺 `WM_DESTROY`，导致 Chromium 观察者析构 CHECK 崩溃；`window_lifecycle.rs` 用 subclass 补齐缺失的 `WM_DESTROY` 阶段）、Windows 10 已知失败场景与诊断方法。

**关键 NAPI 导出**（按平台条件编译）：

| 函数 | 平台 | 说明 |
|------|------|------|
| `set_window_composition` | Windows | 设置合成模式（`handle, mode, keep_on_blur?, tint?`） |
| `get_window_composition_diagnostics` | Windows | 读取 Accent / DWM backdrop / 分层样式等诊断 |
| `set_window_force_active_appearance` | Windows | 失焦保持毛玻璃（WCA_FORCE_ACTIVEWINDOW_APPEARANCE） |
| `taskbar_thumbnail_enable` / `_disable` / `_set_cover` | Windows | DWM 缩略图/Peek 启停与封面位图 |
| `taskbar_lyric_mounted_taskbar` 等（`TaskbarLyricSession`） | Windows | 任务栏歌词嵌入会话（挂载/布局更新/停止） |
| `start_windows_double_click_monitor` / `stop_...` / `get_windows_double_click_diagnostics` | Windows | 原生双击监听 |
| `start_window_pointer_monitor` / `stop_...` | macOS | 本地鼠标监听 |

主进程封装为 `src/main/native/platform.ts`（共享加载器 + API 校验）与 `src/main/native/logging.ts`（日志桥接）。

---

## echo-native-log — 原生日志桥（内部依赖）

共享的 **native → 主进程** 日志桥 crate。它不是 `.node` addon，而是被其他 crate 以路径依赖引用（`echo-native-log = { path = "../echo-native-log" }`）的普通 Rust 库：

- `set_log_handler(callback)`：由宿主 addon 启动时注册（每个 addon 暴露 `register_log_handler` 转发到这里）；
- `emit(level, message)`：各 crate 内部调用，经 `ThreadsafeFunction` 回调主进程。

主进程侧 `src/main/native/logging.ts` 把回调归一化为 `debug | info | warn | error` 后写入 electron-log，统一出现在主进程日志中。**不随安装包分发**（它被静态链进各个 `.node`）。

---

## 开发原生模块

### 构建单个模块

```bash
# 依赖安装（首次）
cd native/<module>
npm install

# Debug / Release 构建（napi-rs CLI，产物为 <crate 名>.node + index.d.ts）
npm run build          # 或 npx napi build --release
```

各 crate 的 `Cargo.lock` 已提交，保证依赖可复现解析。跨目标类型检查（如在 macOS 上检查 Windows target）：

```bash
cargo check --manifest-path native/<module>/Cargo.toml --target x86_64-pc-windows-msvc --locked
```

### 在主进程中加载

- 开发态：从仓库 `native/<module>/<module>.node` 直接加载；
- 打包后：位于 `resources/native/<module>.node`（如 `echo-platform-adaptor` 由 `src/main/native/platform.ts` 按 `app.isPackaged` 分支选择路径）。
- 重建 addon 后需要**重启应用**才能生效。

### 调试技巧

- 各 addon 通过 `register_log_handler` 把 Rust 侧日志桥接到主进程 electron-log（见 echo-native-log），在主进程日志里统一查看，**不要**依赖 `println!`（打包后不可见）。
- 推荐 VS Code + rust-analyzer；Windows 平台行为（DWM、任务栏、独占输出）必须在真实桌面环境验证，跨平台 `cargo check` 与浏览器 fixture 无法替代。

## 参考资源

- [napi-rs 官方文档](https://napi.rs/)
- [FFmpeg 官方文档](https://ffmpeg.org/documentation.html)
- [SoundTouch 音频处理库](https://www.surina.net/soundtouch/)
- [MPRIS 规范](https://specifications.freedesktop.org/mpris-spec/latest/)
- [上游 DSP Provider 架构](https://github.com/hoowhoami/EchoMusic/blob/main/docs/dsp-provider-architecture.md)（仓库 `docs/`）
- [上游平台适配 README](https://github.com/hoowhoami/EchoMusic/blob/main/native/echo-platform-adaptor/README.md)
