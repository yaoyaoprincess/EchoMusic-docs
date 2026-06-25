---
title: 原生模块 (Rust NAPI)
---

# 🦀 原生模块 (Rust NAPI)

EchoMusic 使用 Rust 编写原生扩展，通过 [napi-rs](https://napi.rs/) 框架编译为 Node.js 可调用的原生模块。原生模块运行在 Electron 主进程中，提供高性能的底层能力。

## 为什么用 Rust？

| 优势 | 说明 |
|------|------|
| **零延迟调用** | 进程内直接函数调用，无 IPC 开销 |
| **高性能** | Rust 编译为原生机器码，执行效率接近 C/C++ |
| **内存安全** | Rust 的所有权系统保证内存安全，无 GC 停顿 |
| **丰富生态** | 通过 FFI 可调用 C 库（如 libmpv） |

## 模块概览

### echo-mpv-player — 播放引擎

封装 libmpv 播放器，提供完整音频播放能力。

**核心功能**：

| 功能 | 说明 |
|------|------|
| 播放控制 | 播放/暂停/停止/跳转 |
| 音量控制 | 音量调节、静音 |
| 倍速播放 | 0.5x - 2.0x 倍速 |
| 淡入淡出 | 平滑的切歌过渡 |
| EQ 均衡器 | 10 段图形化 EQ |
| 音量均衡 | 基于 LUFS 的响度标准化 |
| 事件回调 | 播放进度、状态变化等回调 |

**依赖**：

```toml
[dependencies]
napi = "2"
napi-derive = "2"
# libmpv 通过 FFI 绑定调用
```

**调用方式**：

```typescript
import { MpvPlayer } from 'echo-mpv-player'

const player = new MpvPlayer()
player.load('https://example.com/song.mp3')
player.play()
player.setVolume(80)
player.setEq([0, 2, -1, 3, 0, 1, 2, 0, -2, 1])
```

### echo-media-controls — 系统媒体控制

集成各操作系统的原生媒体控制 API。

**核心功能**：

| 平台 | API | 说明 |
|------|-----|------|
| macOS | MPNowPlayingInfoCenter | 控制中心媒体信息展示 |
| macOS | MPRemoteCommandCenter | 响应系统媒体键 |
| Windows | SMTC | 系统媒体传输控制 |
| Linux | MPRIS | D-Bus 媒体播放器接口 |

**调用方式**：

```typescript
import { MediaControls } from 'echo-media-controls'

const controls = new MediaControls()
controls.setMetadata({
  title: '歌曲名',
  artist: '歌手',
  album: '专辑',
  duration: 240,  // 秒
})
controls.setPlaybackState('playing')
controls.on('play', () => { /* 播放 */ })
controls.on('pause', () => { /* 暂停 */ })
controls.on('next', () => { /* 下一首 */ })
controls.on('previous', () => { /* 上一首 */ })
```

### echo-storage — 本地存储

基于 SQLite 的轻量级本地持久化存储。

**核心功能**：

| 功能 | 说明 |
|------|------|
| 键值存储 | 通用 K-V 存储，支持序列化 |
| 播放队列 | 持久化播放队列与状态 |
| 播放历史 | 记录播放历史 |
| 收藏管理 | 歌曲/歌单收藏列表 |
| 设置存储 | 应用偏好设置 |

**调用方式**：

```typescript
import { Storage } from 'echo-storage'

const db = new Storage()
await db.open('echo-music.db')

// 设置存储
await db.set('settings', { theme: 'dark', volume: 80 })

// 读取设置
const settings = await db.get('settings')

// 播放历史
await db.addHistory({ songId: 'xxx', playedAt: Date.now() })
const history = await db.getHistory({ limit: 50 })
```

## 开发原生模块

### 添加新的原生模块

1. 在 `native/` 下创建新 crate：

```bash
cd native
npx @napi-rs/cli new my-new-addon
```

2. 在 Cargo.toml 中配置依赖
3. 在 lib.rs 中使用 `#[napi]` 宏导出函数
4. 在 Electron 主进程中加载 `.node` 文件

### 编译

```bash
# Debug 编译
cd native/<module>
cargo build

# Release 编译（优化后）
cargo build --release
```

### 跨平台编译注意事项

- **macOS**：`.dylib` → 重命名为 `.node`
- **Linux**：`.so` → 重命名为 `.node`
- **Windows**：`.dll` → 重命名为 `.node`

`.node` 文件在 `.gitignore` 中被排除，每次克隆后需重新编译。

## 调试技巧

- 使用 `println!()` 宏输出调试信息（会输出到 Electron 主进程控制台）
- 在 Rust 代码中使用 `napi::bindgen_prelude::console_log!()` 输出到 Node.js 控制台
- 推荐使用 VS Code + rust-analyzer 进行开发

## 参考资源

- [napi-rs 官方文档](https://napi.rs/)
- [mpv 官方文档](https://mpv.io/manual/stable/)
- [MPRIS 规范](https://specifications.freedesktop.org/mpris-spec/latest/)