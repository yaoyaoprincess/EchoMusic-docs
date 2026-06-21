---
title: 开发指南
---

# 🛠️ 开发指南

欢迎来到 EchoMusic 开发文档。本节面向希望参与项目开发或了解内部实现的开发者。

## 技术栈

| 类别 | 技术 |
|------|------|
| 桌面框架 | Electron 42 |
| 前端框架 | Vue 3 + Composition API |
| 类型系统 | TypeScript 5.7 |
| 构建工具 | Vite |
| 状态管理 | Pinia + pinia-plugin-persistedstate |
| UI 组件库 | Reka UI |
| CSS 框架 | Tailwind CSS v4 |
| 路由 | Vue Router |
| 包管理 | pnpm 9+ |
| 后端服务 | Node.js（内置本地服务，进程内直接调用） |
| 音频引擎 | libmpv（通过 Rust NAPI addon 进程内嵌入） |
| 原生扩展 | napi-rs（Rust → Node.js 原生模块） |
| 本地存储 | SQLite（通过 echo-storage addon） |
| 许可证 | MIT |

## 核心架构

EchoMusic 采用 Electron 经典的双进程架构，通过 Rust NAPI 原生扩展实现高性能音频播放：

```
┌─────────────────────────────────────────┐
│              Electron Shell              │
│  ┌──────────────┐  ┌─────────────────┐  │
│  │  Main Process │  │ Renderer Process │  │
│  │  (Node.js)    │  │   (Vue 3 + Vite)│  │
│  │               │  │                  │  │
│  │  ┌─────────┐  │  │  ┌────────────┐  │  │
│  │  │ Server  │  │  │  │   Pinia    │  │  │
│  │  │ (API)   │◄─┼──┼─►│  (Store)   │  │  │
│  │  └─────────┘  │  │  └────────────┘  │  │
│  │  ┌─────────┐  │  │  ┌────────────┐  │  │
│  │  │ Native  │  │  │  │  Tailwind  │  │  │
│  │  │ Addons  │  │  │  │  CSS v4    │  │  │
│  │  │ (Rust)  │  │  │  └────────────┘  │  │
│  │  └─────────┘  │  │                  │  │
│  └──────────────┘  └─────────────────┘  │
└─────────────────────────────────────────┘
```

### 三个原生模块

| 模块 | 功能 | 技术 |
|------|------|------|
| `echo-mpv-player` | libmpv 播放引擎封装 | Rust + libmpv |
| `echo-media-controls` | 系统媒体控制集成 | Rust + OS API |
| `echo-storage` | SQLite 本地持久化 | Rust + rusqlite |

## 文档索引

- [项目架构](/develop/architecture) — 深入了解整体架构设计
- [项目结构](/develop/project-structure) — 完整的目录结构说明
- [本地开发环境](/develop/local-dev) — 搭建本地开发环境
- [原生模块](/develop/native-addons) — Rust NAPI 原生扩展开发
- [编译构建](/develop/build) — 多平台打包构建
- [贡献指南](/develop/contributing) — 参与项目贡献
- [酷狗 API 参考](/develop/api) — 酷狗音乐公开 API 说明
- [内部 API 参考](/develop/internal-api/) — 主应用内部 API（mpv 引擎、桌面歌词等）