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
| FFmpeg 开发库 | — | 音频解码库（运行时不需要外部 ffmpeg 可执行文件） |
| LLVM / libclang（仅 Windows） | — | 编译 echo-ffmpeg-player 需要 |

### 安装 FFmpeg 开发库

**macOS**：

```bash
brew install ffmpeg
```

**Linux（Debian/Ubuntu）**：

```bash
sudo apt install libavcodec-dev libavformat-dev libavutil-dev libswresample-dev
```

**Windows**：

需要安装 LLVM 和 libclang 以编译 echo-ffmpeg-player：

```powershell
winget install LLVM.LLVM
```

同时设置环境变量：

```powershell
$env:LIBCLANG_PATH = "C:\Program Files\LLVM\bin"
```

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
cd node_modules/.pnpm/electron@42.3.1/node_modules/electron/
mkdir -p dist
curl -L -o /tmp/electron.zip "https://npmmirror.com/mirrors/electron/v42.3.1/electron-v42.3.1-linux-x64.zip"
unzip -o /tmp/electron.zip -d dist/
printf '%s' './electron' > path.txt
```

## 编译 Rust 原生模块

如果启动时出现缺少 `.node` 文件的错误：

```
Error: Cannot find module '.../echo-ffmpeg-player/echo-ffmpeg-player.node'
[error] [FfmpegController] Failed to load echo-ffmpeg-player addon
```

需要手动编译 Rust 原生模块（`.node` 文件在 `.gitignore` 中被排除）。推荐使用各 addon 自带的 napi-rs 构建脚本生成平台对应的 `.node`：

```bash
# 编译 echo-ffmpeg-player
cd native/echo-ffmpeg-player
pnpm install --ignore-workspace
pnpm exec napi build --release --no-const-enum

cd ../echo-media-controls
npm install
npm run build

cd ../echo-sqlite-store
npm install
npm run build

cd ../..
```

`echo-ffmpeg-player` 内建实时频谱分析能力，频谱数据通过播放引擎直接输出。播放引擎支持音频设备切换和独占输出模式。

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

### Linux 发行版打包说明

如果发行版包使用系统 Electron 启动 EchoMusic（例如 Arch/Manjaro 的 `electron42 /usr/lib/echo-music/app.asar`），入口脚本必须通过兼容方式处理原生模块加载，建议使用项目提供的 `build/linux-system-electron-wrapper.sh` 模板。

可直接安装并使用：

- `build/linux-system-electron-wrapper.sh`：系统 Electron 启动入口模板

`electron-builder` 产物会在 `afterPack` 阶段自动安装同一套 wrapper。

## 内存诊断

开发模式下可通过环境变量启用内存诊断：

```bash
# Windows PowerShell
$env:ECHOMUSIC_MEMORY_DIAGNOSTICS = "1"
pnpm dev
```

日志文件位于 `~/Library/Logs/EchoMusic/echo-music-YYYY-MM-DD.log`。

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