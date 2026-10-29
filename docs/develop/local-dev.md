---
title: 本地开发环境
---

# 🖥️ 本地开发环境

本文介绍如何搭建 EchoMusic 的本地开发环境。

## 前置要求

在开始之前，请确保你的系统已安装以下工具：

| 工具 | 版本 | 说明 |
|------|------|------|
| Node.js | 22.12+ | JavaScript 运行时 |
| pnpm | 9+ | 包管理器 |
| Rust | stable | 编译原生模块（音频模块 `echo-audio-player` 声明最低 Rust 1.87，建议使用当前 stable） |
| C/C++ 编译工具链 | — | 原生依赖编译需要（Windows 为 MSVC，macOS 为 Xcode CLT，Linux 为 build-essential） |
| LLVM / libclang | — | 所有平台的 `bindgen` 生成绑定都需要 |

### 安装工具链

**macOS**：

安装 Xcode Command Line Tools 和 LLVM（以下依赖安装命令使用 Homebrew）：

```bash
xcode-select --install
brew install llvm pkg-config
export LIBCLANG_PATH="$(brew --prefix llvm)/lib"
```

已安装 Command Line Tools 时跳过第一条命令。在设置了 `LIBCLANG_PATH` 的同一终端中执行后续构建。

**Windows**：

安装 Visual Studio Build Tools 的“使用 C++ 的桌面开发”工作负载及 Windows SDK，使用 MSVC Rust 工具链；编译 ARM64 时还需安装对应的 ARM64 C++ 工具。LLVM/libclang 可通过以下 PowerShell 命令安装、配置：

```powershell
winget install LLVM.LLVM
$env:LIBCLANG_PATH = "C:\Program Files\LLVM\bin"
```

`LIBCLANG_PATH` 必须指向包含 `libclang.dll` 的目录。以上设置立即作用于当前终端；如需持久化，可再执行 `setx LIBCLANG_PATH "C:\Program Files\LLVM\bin"`，新终端才会读取该持久化设置。也可使用 Visual Studio 自带 LLVM 的相应目录。

**Linux**：

以 Debian / Ubuntu 为例，安装编译工具、libclang 和音频后端开发库；后半部分为运行 Electron 所需的桌面依赖：

```bash
sudo apt-get update
sudo apt-get install -y build-essential pkg-config clang libclang-dev \
  libasound2-dev libpulse-dev libpipewire-0.3-dev \
  libgtk-3-dev libnotify-dev libnss3 libxss1 libxtst6 xdg-utils
```

其他发行版安装对应软件包。播放引擎的 Linux 后端同时启用 ALSA、PulseAudio 和 PipeWire，不能只安装其中一个后端的开发库。

### 关于 FFmpeg

EchoMusic **无需**安装系统 FFmpeg 开发库。播放引擎使用的 FFmpeg 以 vendored 方式内嵌在仓库中：`native/echo-audio-player/vendor/ffmpeg-audio/crates/ffmpeg_audio_sys/vendor/` 目录下的 `ffmpeg_slim.zip`（预编译 FFmpeg 库）与 `configs.zip`（构建配置），构建时自动解包链接。

仅当 vendored 构建出现问题时，才可设置 `FFMPEG_MODE=system` 回退到系统 FFmpeg——这会引入额外的开发库及运行时动态库依赖，默认不需要。

## 克隆项目

```bash
git clone https://github.com/hoowhoami/EchoMusic.git
cd EchoMusic
git submodule update --init --recursive
```

## 安装依赖

```bash
pnpm install
```

> `server` 子模块已作为 pnpm workspace 成员管理（见 `pnpm-workspace.yaml`），上述命令会自动一并安装其运行依赖，无需再进入 `server` 目录执行 `npm install`。

### Linux 下的 Electron 问题

如果在 Linux 下遇到以下错误：

```
Error: ENOENT: no such file or directory, open '.../node_modules/electron/path.txt'
```

需要手动下载 Electron 到对应目录（版本号以 `pnpm-lock.yaml` 实际安装的为准）：

```bash
cd node_modules/.pnpm/electron@43.7.6/node_modules/electron/
mkdir -p dist
curl -L -o /tmp/electron.zip "https://npmmirror.com/mirrors/electron/v43.7.6/electron-v43.7.6-linux-x64.zip"
unzip -o /tmp/electron.zip -d dist/
printf '%s' './electron' > path.txt
```

## 编译 Rust 原生模块

`*.node` 产物不随源码提交。**首次开发、修改 Rust 代码或切换系统/CPU 架构后，都需要手动构建对应模块。根目录的 `pnpm install` 只覆盖根项目和 `server` workspace，`pnpm dev` / `pnpm build` 不会自动编译原生模块。**

如果启动时出现缺少 `.node` 文件的错误：

```
Error: Cannot find module '.../echo-audio-player/echo-audio-player.node'
```

需要按下表逐个编译（Linux 无需构建 `echo-platform-adaptor`，其余平台 8 个全部构建）：

| 模块目录 | 用途 |
|----------|------|
| `native/echo-audio-player` | 播放、解码及音效处理 |
| `native/echo-audio-capture` | 系统音频和麦克风采集 |
| `native/echo-media-controls` | 系统媒体控制 |
| `native/echo-sqlite-store` | SQLite 持久化存储 |
| `native/echo-opencc` | 歌词简繁转换 |
| `native/echo-upnp` | DLNA / UPnP 设备控制 |
| `native/echo-airplay` | AirPlay 设备发现与音频发送 |
| `native/echo-platform-adaptor` | 系统窗口、任务栏等平台适配（macOS / Windows） |

每个模块在其自身目录执行 `npm install` 安装构建依赖，再执行 `npm run build`（即 `napi build --release --no-const-enum`）。

**macOS / Linux（Bash，从仓库根目录执行）**：

```bash
bash <<'BASH'
set -e
addons=(echo-audio-player echo-audio-capture echo-media-controls echo-sqlite-store echo-opencc echo-upnp echo-airplay)
if [[ "$(uname -s)" == "Darwin" ]]; then
  addons+=(echo-platform-adaptor)
fi
for addon in "${addons[@]}"; do
  (
    cd "native/$addon"
    npm install
    npm run build
  )
done
BASH
```

**Windows（PowerShell）**：

```powershell
$addons = @("echo-audio-player", "echo-audio-capture", "echo-media-controls", "echo-sqlite-store", "echo-opencc", "echo-upnp", "echo-airplay", "echo-platform-adaptor")
foreach ($addon in $addons) {
  Push-Location "native/$addon"
  try {
    npm install
    if ($LASTEXITCODE -ne 0) { throw "安装 $addon 构建依赖失败" }
    npm run build
    if ($LASTEXITCODE -ne 0) { throw "构建 $addon 失败" }
  } finally {
    Pop-Location
  }
}
```

每个模块会在自身目录生成同名 `.node`，例如 `native/echo-audio-capture/echo-audio-capture.node`。仅执行 `cargo build --release` 不会把产物转换并放到应用期望的路径，必须使用上述 napi-rs 构建脚本。

交叉编译时，需先准备目标工具链、SDK 并执行 `rustup target add <target>`，再在**每个模块目录**运行 `npx napi build --release --no-const-enum --target <target>`。x64 与 arm64 产物不能混用，可参考 [CI 构建矩阵](https://github.com/hoowhoami/EchoMusic/blob/main/.github/workflows/build.yml)。

> 重编译后需完全退出并重新启动 EchoMusic——已加载的 Native 模块不会随前端热更新重新加载。

## 启动开发服务器

```bash
pnpm dev
```

开发模式下的启动流程：

1. Vite 启动开发服务器，`vite-plugin-electron` 编译并拉起 Electron 主进程
2. 主进程加载并初始化 Rust 原生模块
3. 主进程在进程内初始化酷狗 API 服务（`server/` 子模块，扫描 `module/` 路由表）
4. 主进程创建 BrowserWindow，加载 Vite 开发服务器页面
5. 渲染进程通过 IPC（`api:request`）直连主进程完成 API 调用，无 HTTP 端口

## 内存诊断

需要观察 Electron 主进程、Renderer、GPU 等进程的内存变化时，可以开启启动阶段内存诊断日志：

```bash
# macOS / Linux
ECHOMUSIC_MEMORY_DIAGNOSTICS=1 pnpm dev

# Windows PowerShell
$env:ECHOMUSIC_MEMORY_DIAGNOSTICS = "1"
pnpm dev
```

日志会写入 Electron 日志文件，例如 macOS 下为：

```text
~/Library/Logs/EchoMusic/echo-music-YYYY-MM-DD.log
```

## 开发调试

### 推荐 IDE

项目提供 `.vscode/extensions.json` 推荐扩展配置，打开项目时 VS Code 会提示安装。推荐的扩展包括 Vue (Volar)、ESLint、Prettier、Tailwind CSS IntelliSense 和 Iconify。

### 前端调试

- 在 Electron 窗口中按 `Ctrl + Shift + I`（Windows/Linux）或 `Cmd + Option + I`（macOS）打开开发者工具
- Vue DevTools 在开发模式下自动启用

### 主进程与 API 服务调试

- 主进程与 API 服务（server 子模块）日志通过 electron-log 输出
- 可通过开发者工具或日志文件查看 `[IPC-Server]` 前缀的 API 路由加载日志

### Rust 模块调试

- 编译时使用 `cargo build`（不加 `--release`）可获得更多调试信息
- 推荐安装 `rust-analyzer` 进行代码提示与调试

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

### Unable to find libclang

检查 LLVM/libclang 安装与 `LIBCLANG_PATH`；它应指向包含 `libclang.dll`（Windows）或 libclang 库所在目录（macOS/Linux），而不是可执行文件。

### FFmpeg 提示回退到系统 FFmpeg

如果构建日志出现 `Falling back to attempting to link the system's FFmpeg`，检查 `native/echo-audio-player/vendor/ffmpeg-audio/crates/ffmpeg_audio_sys/vendor/` 中的 `ffmpeg_slim.zip` 和 `configs.zip` 是否完整。默认构建无需系统 FFmpeg，也不需要设置 `FFMPEG_MODE=system`。

### Linux 报 ALSA / PulseAudio / PipeWire 的 pkg-config 错误

补齐前置要求中的音频后端开发库（三者缺一不可），并确认 `pkg-config` 能找到目标架构的库。

### 端口冲突

Vite 开发服务器端口可在 `vite.config.mts` 的 `server` 配置段中修改。
