---
title: 开发指南
---

# 🛠️ 开发指南

欢迎来到 EchoMusic 开发文档。本节面向希望参与项目开发或了解内部实现的开发者。

## 技术栈

| 类别 | 技术 |
|------|------|
| 桌面框架 | Electron 43.7 |
| 前端框架 | Vue 3.5 + Composition API |
| 类型系统 | TypeScript 5.9 |
| 构建工具 | Vite 8 |
| 状态管理 | Pinia 4 + 自研 SQLite 持久化插件（`sqlitePersist`） |
| UI 组件库 | Reka UI |
| CSS 框架 | Tailwind CSS v4.3（经 `@tailwindcss/vite` 插件接入） |
| 路由 | Vue Router |
| 包管理 | pnpm 9+（workspace 包含 `server` 子模块） |
| 后端服务 | Node.js（KuGouMusicApi 以 git 子模块形式进程内加载，IPC 直连调用） |
| 音频引擎 | echo-audio-player（vendored FFmpeg 解码 + SoundTouch 变速，Rust NAPI 进程内嵌入） |
| 原生扩展 | napi-rs（Rust → Node.js 原生模块） |
| 本地存储 | SQLite（通过 echo-sqlite-store addon） |
| 许可证 | GPL-3.0-only |

## 核心架构

EchoMusic 采用 Electron 双进程架构，通过 Rust NAPI 原生扩展（napi-rs）实现高性能音频播放。渲染进程与主进程通过 IPC 直连通信，酷狗 API 服务以子模块形式在主进程内加载，无独立 HTTP 端口：

```
┌──────────────────────────────────────────────────┐
│                  Electron Shell                   │
│  ┌────────────────┐    ┌───────────────────────┐ │
│  │  Main Process  │IPC │   Renderer Process    │ │
│  │  (Node.js)     │◄──►│     (Vue 3 + Vite)    │ │
│  │                │    │                       │ │
│  │  ┌──────────┐  │    │  ┌─────────────────┐  │ │
│  │  │ KuGou API│  │    │  │      Pinia      │  │ │
│  │  │ (子模块, │  │    │  │  25+ Store +    │  │ │
│  │  │  进程内) │  │    │  │ sqlitePersist   │  │ │
│  │  └──────────┘  │    │  └─────────────────┘  │ │
│  │  ┌──────────┐  │    │  ┌─────────────────┐  │ │
│  │  │  Native  │  │    │  │   Tailwind v4   │  │ │
│  │  │  Addons  │  │    │  └─────────────────┘  │ │
│  │  │  (Rust)  │  │    │                       │ │
│  │  └──────────┘  │    │                       │ │
│  └────────────────┘    └───────────────────────┘ │
└──────────────────────────────────────────────────┘
```

### 原生模块总览

EchoMusic 共包含 9 个 Rust 原生模块：8 个随安装包分发，1 个仅作为内部依赖：

| 模块 | 功能 | 分发平台 |
|------|------|----------|
| `echo-audio-player` | 播放、解码及音效处理（FFmpeg + SoundTouch） | macOS / Windows / Linux |
| `echo-audio-capture` | 系统音频和麦克风采集（听歌识曲） | macOS / Windows / Linux |
| `echo-media-controls` | 系统媒体控制（SMTC / MPRIS / MPNowPlayingInfoCenter） | macOS / Windows / Linux |
| `echo-sqlite-store` | SQLite 持久化存储 | macOS / Windows / Linux |
| `echo-opencc` | 歌词简繁转换 | macOS / Windows / Linux |
| `echo-upnp` | DLNA / UPnP 设备控制 | macOS / Windows / Linux |
| `echo-airplay` | AirPlay 设备发现与音频发送 | macOS / Windows / Linux |
| `echo-platform-adaptor` | 系统窗口、任务栏等平台适配 | macOS / Windows（Linux 无需构建） |
| `echo-native-log`（内部依赖） | 原生日志，供其他 crate 依赖，不随安装包分发 | — |

各模块的构建方式见[本地开发环境](/develop/local-dev)，模块 API 与实现细节见[原生模块](/develop/native-addons)。

## 技术亮点

| 特性 | 说明 |
|------|------|
| 音频引擎 | vendored FFmpeg + SoundTouch，Rust NAPI 进程内嵌入，零延迟直接函数调用，无需安装系统 FFmpeg |
| 音质支持 | Hi-Res、SQ(flac)、HQ(320kbps)、标准(128kbps) |
| 音效引擎 | 内置跨平台音效引擎：10 段均衡器（频响前级补偿）、LUFS 响度标准化、WAV/IRS 空间音效，支持导入兼容 DSP Provider 与社区音效 |
| 播放格式 | 标准音频 + LRC/YRC 逐字歌词解析 |
| 网络投放 | DLNA / UPnP 与 AirPlay 设备发现与投放，保留本机播放队列 |
| 插件扩展 | 在线插件源浏览安装与本地插件加载，插件浮窗运行在独立窗口进程中 |
| 平台输出 | macOS (dmg/zip)、Windows (nsis，x64/arm64)、Linux (AppImage/deb/pacman/rpm/tar.gz) |

## 文档索引

- [项目架构](/develop/architecture) — 深入了解整体架构设计
- [项目结构](/develop/project-structure) — 完整的目录结构说明
- [本地开发环境](/develop/local-dev) — 搭建本地开发环境
- [原生模块](/develop/native-addons) — Rust NAPI 原生扩展开发
- [编译构建](/develop/build) — 多平台打包构建
- [贡献指南](/develop/contributing) — 参与项目贡献
- [酷狗 API 参考](/develop/kugou-api) — 酷狗音乐公开 API 说明
- [内部 API 参考](/develop/internal-api/) — 主应用内部 API（FFmpeg 引擎、桌面歌词等）
