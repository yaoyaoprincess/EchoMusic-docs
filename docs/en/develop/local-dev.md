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
| mpv / libmpv | — | Audio playback engine |

### Installing mpv / libmpv

**macOS**:

```bash
brew install mpv
```

**Linux (Debian/Ubuntu)**:

```bash
sudo apt install libmpv-dev
```

**Windows**:

Download `libmpv-2.dll` and place it in the `build\mpv` directory.

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
cd node_modules/.pnpm/electron@42.0.1/node_modules/electron/
mkdir -p dist
curl -L -o /tmp/electron.zip "https://npmmirror.com/mirrors/electron/v42.0.1/electron-v42.0.1-linux-x64.zip"
unzip -o /tmp/electron.zip -d dist/
printf '%s' './electron' > path.txt
```

## Compile Rust Native Modules

If you encounter "missing .node file" errors on startup:

```
Error: Cannot find module '.../echo-mpv-player/echo-mpv-player.node'
[error] [MpvController] Failed to load echo-mpv-player addon
```

You need to manually compile the Rust native modules (`.node` files are excluded in `.gitignore`). Use the napi-rs build scripts included with each addon to generate the platform-specific `.node`:

```bash
# Compile echo-mpv-player
cd native/echo-mpv-player
npm install
npm run build

cd ../echo-media-controls
npm install
npm run build

cd ../echo-storage
npm install
npm run build

cd ../..
```

`echo-mpv-player` integrates real-time spectrum analysis and optionally supports system audio capture: Windows uses WASAPI loopback, Linux uses ALSA monitor, macOS uses ScreenCaptureKit. On macOS, when using system-level spectrum capture for the first time, you need to authorize EchoMusic in "System Settings → Privacy & Security → Screen & System Audio Recording"; in development mode, you may also need to authorize Terminal, Electron, or the current launch process.

Building the system audio capture module on Linux requires ALSA development libraries:

```bash
# Debian/Ubuntu
sudo apt install libasound2-dev
```

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

If a distribution package uses the system Electron to launch EchoMusic (e.g., Arch/Manjaro's `electron42 /usr/lib/echo-music/app.asar`), the entry script must preload the system FFmpeg/libav libraries before starting Electron. Otherwise, Electron's built-in stripped `libffmpeg.so` may conflict with system `libmpv`, causing HTTP audio streams to fail.

You can directly install and use:

- `build/linux-libmpv-env.sh`: shared libmpv environment fix script
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