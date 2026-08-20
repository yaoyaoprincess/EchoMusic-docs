---
title: Local Dev Setup
---

# 🖥️ Local Dev Setup

This guide covers setting up the EchoMusic local development environment.

## Prerequisites

Before starting, ensure your system has the following tools installed:

| Tool | Minimum Version | Description |
|------|----------|------|
| Node.js | 18+ | JavaScript runtime |
| pnpm | 9+ | Package manager |
| Rust | 1.70+ | Required for compiling native modules |
| FFmpeg dev libraries | — | Audio decoding (no external ffmpeg binary needed at runtime) |
| LLVM / libclang (Windows only) | — | Required for compiling echo-ffmpeg-player |

### Installing FFmpeg Dev Libraries

**macOS**:

```bash
brew install ffmpeg
```

**Linux (Debian/Ubuntu)**:

```bash
sudo apt install libavcodec-dev libavformat-dev libavutil-dev libswresample-dev
```

**Windows**:

LLVM and libclang are required to compile echo-ffmpeg-player:

```powershell
winget install LLVM.LLVM
```

Set the environment variable:

```powershell
$env:LIBCLANG_PATH = "C:\Program Files\LLVM\bin"
```

## Clone the Project

```bash
git clone https://github.com/hoowhoami/EchoMusic.git
cd EchoMusic
git submodule update --init --recursive
```

## Install Dependencies

```bash
# Install frontend and Electron dependencies
pnpm install

# Install backend service dependencies
cd server && npm install && cd ..
```

### Electron Issues on Linux

If you encounter the following error on Linux:

```
Error: ENOENT: no such file or directory, open '.../electron/path.txt'
```

You need to manually download Electron to the appropriate directory:

```bash
cd node_modules/.pnpm/electron@42.3.1/node_modules/electron/
mkdir -p dist
curl -L -o /tmp/electron.zip "https://npmmirror.com/mirrors/electron/v42.3.1/electron-v42.3.1-linux-x64.zip"
unzip -o /tmp/electron.zip -d dist/
printf '%s' './electron' > path.txt
```

## Compile Rust Native Modules

If you encounter "missing .node file" errors on startup:

```
Error: Cannot find module '.../echo-ffmpeg-player/echo-ffmpeg-player.node'
[error] [FfmpegController] Failed to load echo-ffmpeg-player addon
```

You need to manually compile the Rust native modules (`.node` files are excluded in `.gitignore`). Use the napi-rs build scripts included with each addon to generate the platform-specific `.node`:

```bash
# Compile echo-ffmpeg-player
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

`echo-ffmpeg-player` has built-in real-time spectrum analysis, with spectrum data output directly through the playback engine. The playback engine supports audio device switching and exclusive output mode.

## Start Dev Server

```bash
pnpm dev
```

In development mode, the Electron main process automatically launches the local server:

1. Electron main process starts
2. Main process loads and initializes Rust native modules
3. Main process starts the Node.js backend server
4. Main process creates BrowserWindow and loads the Vite dev server
5. Renderer process communicates with the backend server via HTTP

### Linux Distribution Packaging

If a distribution package uses the system Electron to launch EchoMusic (e.g., Arch/Manjaro's `electron42 /usr/lib/echo-music/app.asar`), the entry script should use the project-provided `build/linux-system-electron-wrapper.sh` template for compatibility.

You can directly install and use:

- `build/linux-system-electron-wrapper.sh`: system Electron entry wrapper template

The same wrapper is automatically installed during the `afterPack` phase of `electron-builder` builds.

## Debugging

### Recommended IDE

The project provides recommended VS Code extensions (`.vscode/extensions.json`). VS Code will prompt to install them when opening the project. Recommended extensions include Vue (Volar), TypeScript, Rust Analyzer, ESLint, Prettier, Tailwind CSS IntelliSense, and more.

The project also includes `.claude/settings.json` for optimized AI-assisted development with Claude Code.

### Frontend Debugging

- Press `Ctrl + Shift + I` (Windows/Linux) or `Cmd + Option + I` (macOS) in the Electron window to open DevTools
- Vue DevTools is automatically enabled in development mode

### Backend Debugging

- Backend server logs output in the Electron main process console
- Viewable through DevTools' main process console

### Rust Module Debugging

- Compile with `cargo build` (without `--release`) for more debug information
- We recommend using VS Code + rust-analyzer for development

## Common Issues

### pnpm install Fails

Ensure you're using pnpm 9+:

```bash
pnpm --version
# If version is too low
npm install -g pnpm@latest
```

### Slow Rust Compilation

First-time Rust module compilation can be slow (downloading dependencies + compilation). Subsequent incremental compilations will be much faster. Set up a Chinese mirror for speedup:

```bash
# ~/.cargo/config.toml
[source.crates-io]
replace-with = 'mirror'

[source.mirror]
registry = "sparse+https://mirrors.tuna.tsinghua.edu.cn/crates.io-index/"
```

### Port Conflict

If port 3000 is in use (Vite dev server), modify the port configuration in `vite.config.ts`.