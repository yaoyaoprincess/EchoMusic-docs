---
title: 内部 API 参考
outline: [2, 4]
---

# 🔧 内部 API 参考

> ⚠️ **本文档仅供核心开发参考。** 以下 API 属于 EchoMusic 主进程/渲染进程内部接口，**不暴露给插件**。插件开发请参阅 [插件 API 总览 →](../plugin-dev/context-api)。

EchoMusic 内部 API 覆盖音频引擎、窗口管理、系统集成、播放状态持久化等核心模块。按功能分为四类：

| 模块 | 说明 | 入口 |
|------|------|:--:|
| 🎵 音频引擎 | mpv 引擎：均衡器、空间音效、IR 卷积、设备控制、事件监听 | [→](audio-engine) |
| 📡 播放状态与持久化 | 播放事件、队列持久化、本地 API 服务、HTTP 请求代理 | [→](playback-state) |
| 🖥️ 窗口与交互管理 | 桌面歌词、Mini 播放器、窗口控制、系统托盘 | [→](window-management) |
| ⚙️ 系统功能集成 | 快捷键、电源管理、应用更新、日志、音效管理 | [→](system-features) |

---

## 模块概览

### 🎵 音频引擎（`ctx.audio`）

底层 libmpv 引擎的完整操作面。18 段参数均衡器、空间音效预设、IR 脉冲响应卷积、音频设备切换、音量渐变、响度归一化、MKV 轨道选择、引擎生命周期管理等。

### 📡 播放状态与持久化（`ctx.events` / `ctx.storage` / `ctx.apiServer` / `ctx.api`）

播放生命周期事件（切歌/播放暂停/音量变化）、播放队列的持久化存储（重启恢复）、本地 HTTP API 服务启停、主进程代理 HTTP 客户端。

### 🖥️ 窗口与交互管理（`ctx.desktopLyric` / `ctx.miniPlayer` / `ctx.windowControl` / `ctx.tray`）

桌面歌词悬浮窗的显示/隐藏/锁定/穿透、Mini 播放器窗口的展开/置顶/位置控制、当前窗口最小化/最大化/全屏、系统托盘图标状态同步。

### ⚙️ 系统功能集成（`ctx.shortcuts` / `ctx.power` / `ctx.updater` / `ctx.appInfo` / `ctx.logger` / `ctx.audioEffects`）

全局快捷键注册与监听、系统休眠/唤醒响应、应用自动更新下载安装、版本/平台信息查询、结构化日志、IR 脉冲响应文件管理。

---

## 📂 相关文档

- [插件 API 总览 →](../plugin-dev/context-api) — 插件可用的正式 API
- [项目架构 →](../architecture) — EchoMusic 整体架构
- [项目结构 →](../project-structure) — 完整目录结构
- [KuGou API 参考 →](../api) — 酷狗音乐公开 API
