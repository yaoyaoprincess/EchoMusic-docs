---
title: 插件开发概览
outline: [2, 4]
---

# 🔌 插件开发概览

EchoMusic 插件系统提供了一套高自由度的本地扩展机制，定位类似 VS Code 或 Obsidian 的插件体系。插件可以定制界面、扩展功能、处理音频数据，并与播放器深度集成。

## 插件系统架构

### 整体架构

```
┌────────────────────────────────────────┐
│              EchoMusic 主应用           │
│  ┌──────────┐  ┌──────────┐            │
│  │ 主窗口    │  │ Mini 播放器│            │
│  │ (Electron)│  │ (独立窗口) │            │
│  ├──────────┤  ├──────────┤            │
│  │ 插件 A    │  │ 插件 A    │ ← 若开启   │
│  │ 插件 B    │  │          │   miniPlayer│
│  │ 插件 C    │  │          │            │
│  └──────────┘  └──────────┘            │
│  ┌──────────┐                          │
│  │ 桌面歌词  │                          │
│  │ (独立窗口) │                          │
│  ├──────────┤                          │
│  │ 插件 A    │ ← 若开启 desktopLyric    │
│  └──────────┘                          │
│       ▲                                │
│       │ ctx 对象注入                    │
│       │                                │
│  ┌────┴─────┐                          │
│  │ 插件管理器 │  加载 / 卸载 / 生命周期   │
│  └──────────┘                          │
└────────────────────────────────────────┘
```

### ctx API 体系

`ctx` 是插件的核心入口对象，按功能分为 7 大模块：

```
ctx
├── 🏗️ 宿主运行时       → vue / app / router / pinia
├── 📦 状态管理         → stores.player / playlist / lyric / settings / theme
├── 🎨 UI 扩展          → addPage / settings / 右键菜单 / 播放器按钮 / mount / teleport
├── 🎵 播放 & 音频       → 播放控制 / 播放队列 / mpv 引擎 / 频谱 / 音源 / 歌词
├── 💾 数据 & 文件       → KV 存储 / 文件系统 / 播放队列持久化 / HTTP 请求
├── 🪟 窗口 & 系统       → 浮窗 / 桌面歌词 / Mini / NowPlaying / 快捷键 / 图标 / 电源
└── 📋 插件管理          → 生命周期 / 市场 / 安装 / 故障上报 / 日志
```

> 完整的 ~120 个 API 速查请见 [API 总览 →](./context-api)

### 多窗口模型

EchoMusic 有三个独立的渲染窗口，**彼此不共享 JS 内存**：

| 窗口 | 说明 | 插件参与方式 |
|------|------|:--:|
| **主窗口** | 完整的播放器界面、设置、插件管理等 | 默认加载所有已启用插件 |
| **Mini 播放器** | 精简的迷你播放窗口 | 需在 manifest 中声明 `runtime.miniPlayer: true` |
| **桌面歌词** | 悬浮桌面歌词窗口 | 需在 manifest 中声明 `runtime.desktopLyric: true` |

> 如果插件只操作主窗口（例如添加设置面板、注册页面），无需开启 miniPlayer 或 desktopLyric。

### 插件生命周期

```
  [用户启用插件]
       │
       ▼
  ┌─────────────┐     ┌──────────────────┐
  │ 加载 manifest │ ──▶ │ 校验 version /   │
  │              │     │ capabilities     │
  └─────────────┘     └──────┬───────────┘
                             │
                    ┌────────▼──────────┐
                    │ 版本不符？          │
                    │ → 提示"版本不兼容"   │
                    │ 阻止启用            │
                    └────────┬──────────┘
                             │ 通过
                    ┌────────▼──────────┐
                    │ 加载入口 JS (ESM)  │
                    │ 注入 ctx 对象      │
                    └────────┬──────────┘
                             │
                    ┌────────▼──────────┐
                    │ activate(ctx)     │
                    │ 插件注册资源        │
                    └────────┬──────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
         正常运行      用户禁用/卸载      崩溃/异常
              │              │              │
              │       ┌──────▼──────┐       │
              │       │deactivate() │       │
              │       │自动清理资源  │       │
              │       │ctx.dispose()│       │
              │       └──────┴──────┘       │
              │                             │
              └──────────────┬──────────────┘
                             │
                    ┌────────▼──────────┐
                    │ 插件停止            │
                    │ 卸载时删除插件目录   │
                    │ 清除 KV 数据和故障记录│
                    └───────────────────┘
```

## 安全模型

### 信任边界

- 插件是**用户主动启用**的本地代码，运行在 Electron 渲染进程中
- EchoMusic 不对插件做沙箱隔离——插件可以访问主渲染进程的所有 API
- 因此必须**只启用来源可信的插件**

### 能力声明（Capabilities）

插件对敏感 API 的访问采用**显式声明**机制。在 manifest 中声明需要的 capability 后，对应的 `ctx` API 才会可用：

| Capability | 授予的 API 访问 |
|------------|----------------|
| `audioSource` | `ctx.player.audioSource.register()` — 接管音源解析 |
| `audioSpectrum` | `ctx.audio.spectrum` — 读取/订阅音频频谱数据 |
| `kugouApi` | `ctx.kugou` — 调用酷狗 API |
| `localFiles` | `ctx.fs` — 扫描/读写本地文件 |
| `lyricEffects` | `ctx.lyricEffects.register()` — 注册歌词动效 |
| `lyrics` | `ctx.lyrics.registerResolver()` — 提供自定义歌词 |
| `process` | `ctx.process.launch()` — 启动插件目录内的程序 |

> 遵循**最小权限原则**：只声明插件实际需要的 capability，多余的不要开启。

### 网络安全

从 v2.2.7 起，manifest 支持 `permissions.http` 声明插件的网络访问范围，帮助用户了解插件的联网行为。

## 开发环境要求

- **Node.js**：建议 18+
- **代码环境**：浏览器 ESM（不支持 Node.js 内置模块如 `fs`、`path`）
- **Vue 依赖**：通过 `ctx.vue` 获取，**不要**使用 bare import（如 `import { ref } from 'vue'`）
- **构建工具**（可选）：如需使用 TypeScript 或 Vue SFC，使用 Vite / esbuild 打包为单文件 ESM

## 文档导航

### 入门

| 文档 | 适合人群 | 内容 |
|------|:--:|------|
| [快速开始 →](./getting-started) | 新手 | 从零搭建第一个插件（5 分钟） |
| [Manifest 配置参考 →](./manifest) | 所有人 | manifest.json 完整字段说明 |
| [API 总览 →](./context-api) | 所有人 | `ctx` 对象完整 ~120 个 API 速查表 |

### 深入

| 文档 | 内容 |
|------|------|
| [UI 扩展指南 →](./ui-extension) | 页面、设置面板、右键菜单、播放器按钮、组件注入、CSS 动态注入 |
| [播放器与音频引擎 →](./player-audio) | 播放控制、播放队列、mpv 底层引擎（EQ/空间音效/IR）、歌词系统 |
| [音频频谱 →](./audio-spectrum) | 实时 FFT 频谱数据订阅、可视化、VU 表 |
| [文件存储与数据 →](./filesystem-storage) | 文件系统读写、KV 存储、播放队列持久化、HTTP 请求、事件监听、外观订阅 |
| [窗口与系统 →](./windows-system) | 浮窗、桌面歌词、Mini 播放器、NowPlaying、快捷键、托盘、图标、进程、电源 |
| [发布与分发 →](./publishing) | 插件源、版本管理、在线安装、安全模式、故障上报、TypeScript/Vue SFC 打包 |

---

- [EchoMusic 主仓库 →](https://github.com/hoowhoami/EchoMusic)
- [EchoMusicPlugins 仓库 →](https://github.com/hoowhoami/EchoMusicPlugins)
- [使用指南：插件系统 →](/guide/plugins)
