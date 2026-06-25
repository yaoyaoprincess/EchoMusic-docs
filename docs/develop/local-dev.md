---
title: 本地开发环境
---

# 🖥️ 本地开发环境

本文介绍如何搭建 EchoMusic 的本地开发环境。

## 前置要求

在开始之前，请确保你的系统已安装以下工具：

| 工具 | 最低版本 | 说明 |
|------|----------|------|
| Node.js | 18+ | JavaScript 运行时 |
| pnpm | 9+ | 包管理器 |
| Rust | 1.70+ | 编译原生模块需要 |
| mpv / libmpv | — | 音频播放引擎 |

### 安装 mpv / libmpv

**macOS**：

```bash
brew install mpv
```

**Linux（Debian/Ubuntu）**：

```bash
sudo apt install libmpv-dev
```

**Windows**：

从 [mpv.io](https://mpv.io/installation/) 下载并安装，或将 `mpv-1.dll` 放入系统 PATH 目录。

## 克隆项目

```bash
git clone https://github.com/hoowhoami/EchoMusic.git
cd EchoMusic
git submodule update --init --recursive
```

## 安装依赖

```bash
# 安装前端与 Electron 依赖
pnpm install

# 安装后端服务依赖
cd server && npm install && cd ..
```

### Linux 下的 Electron 问题

如果在 Linux 下遇到以下错误：

```
Error: ENOENT: no such file or directory, open '.../electron/path.txt'
```

需要手动下载 Electron 到对应目录：

```bash
cd node_modules/.pnpm/electron@42.0.1/node_modules/electron/
mkdir -p dist
curl -L -o /tmp/electron.zip "https://npmmirror.com/mirrors/electron/v42.0.1/electron-v42.0.1-linux-x64.zip"
unzip -o /tmp/electron.zip -d dist/
printf '%s' './electron' > path.txt
```

## 编译 Rust 原生模块

如果启动时出现缺少 `.node` 文件的错误：

```
Error: Cannot find module '.../echo-mpv-player/echo-mpv-player.node'
[error] [MpvController] Failed to load echo-mpv-player addon
```

需要手动编译 Rust 原生模块（`.node` 文件在 `.gitignore` 中被排除）：

```bash
# 编译 echo-mpv-player
cd native/echo-mpv-player
cargo build --release
# Windows
cp target/release/echo_mpv_player.dll echo-mpv-player.node
# macOS / Linux
cp target/release/libecho_mpv_player.so echo-mpv-player.node
# macOS
cp target/release/libecho_mpv_player.dylib echo-mpv-player.node

cd ../..

# 编译 echo-media-controls
cd native/echo-media-controls
cargo build --release
# Windows
cp target/release/echo_media_controls.dll echo-media-controls.node
# macOS / Linux
cp target/release/libecho_media_controls.so echo-media-controls.node

cd ../..

# 编译 echo-storage
cd native/echo-storage
cargo build --release
# Windows
cp target/release/echo_storage.dll echo-storage.node
# macOS / Linux
cp target/release/libecho_storage.so echo-storage.node

cd ../..
```

## 启动开发服务器

```bash
pnpm dev
```

开发模式下会由 Electron 主进程自动拉起本地服务端：

1. Electron 主进程启动
2. 主进程加载并初始化 Rust 原生模块
3. 主进程启动 Node.js 后端服务器
4. 主进程创建 BrowserWindow，加载 Vite 开发服务器
5. 渲染进程通过 HTTP 与后端服务器通信

## 开发调试

### 推荐 IDE

项目提供 VS Code 推荐扩展配置（`.vscode/extensions.json`），打开项目时 VS Code 会提示安装。推荐的扩展包括 Vue (Volar)、TypeScript、Rust Analyzer、ESLint、Prettier、Tailwind CSS IntelliSense 等。

项目还包含 `.claude/settings.json`，使用 Claude Code 时可直接获得针对 EchoMusic 优化的 AI 编程辅助。

### 前端调试

- 在 Electron 窗口中按 `Ctrl + Shift + I`（Windows/Linux）或 `Cmd + Option + I`（macOS）打开开发者工具
- Vue DevTools 在开发模式下自动启用

### 后端调试

- 后端服务器日志输出在 Electron 主进程的控制台中
- 可通过开发者工具的主进程控制台查看

### Rust 模块调试

- 编译时使用 `cargo build`（不加 `--release`）可获得更多调试信息
- 推荐使用 `rust-analyzer` 进行代码提示与调试

## 常见问题

### pnpm install 失败

确保使用 pnpm 9+ 版本：

```bash
pnpm --version
# 如版本过低
npm install -g pnpm@latest
```

### Rust 编译缓慢

首次编译 Rust 模块会较慢（下载依赖 + 编译），后续增量编译会快很多。可以设置国内镜像加速：

```bash
# ~/.cargo/config.toml
[source.crates-io]
replace-with = 'mirror'

[source.mirror]
registry = "sparse+https://mirrors.tuna.tsinghua.edu.cn/crates.io-index/"
```

### 端口冲突

如果 3000 端口被占用（Vite 开发服务器），修改 `vite.config.ts` 中的端口配置。