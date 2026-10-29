---
title: Local Dev Setup
---

# 🖥️ Local Dev Setup

This guide covers setting up the EchoMusic local development environment.

## Prerequisites

Before you start, make sure the following tools are installed:

| Tool | Version | Notes |
|------|---------|------|
| Node.js | 22.12+ | JavaScript runtime |
| pnpm | 9+ | Package manager |
| Rust | stable | For building native modules (the audio module `echo-audio-player` declares a minimum of Rust 1.87; current stable is recommended) |
| C/C++ toolchain | — | Required by native dependencies (MSVC on Windows, Xcode CLT on macOS, build-essential on Linux) |
| LLVM / libclang | — | Required on all platforms for `bindgen` binding generation |

### Installing the Toolchain

**macOS**:

Install the Xcode Command Line Tools and LLVM (dependency install commands below use Homebrew):

```bash
xcode-select --install
brew install llvm pkg-config
export LIBCLANG_PATH="$(brew --prefix llvm)/lib"
```

Skip the first command if the Command Line Tools are already installed. Run subsequent builds in the same terminal where `LIBCLANG_PATH` is set.

**Windows**:

Install the "Desktop development with C++" workload of Visual Studio Build Tools along with the Windows SDK, and use the MSVC Rust toolchain; building for ARM64 additionally requires the ARM64 C++ tools. LLVM/libclang can be installed and configured with the following PowerShell commands:

```powershell
winget install LLVM.LLVM
$env:LIBCLANG_PATH = "C:\Program Files\LLVM\bin"
```

`LIBCLANG_PATH` must point to the directory containing `libclang.dll`. The setting above applies to the current terminal only; to persist it, run `setx LIBCLANG_PATH "C:\Program Files\LLVM\bin"` (new terminals will pick it up). The LLVM bundled with Visual Studio works too.

**Linux**:

On Debian / Ubuntu, for example, install the build tools, libclang, and the audio backend dev libraries; the latter half covers the desktop dependencies required to run Electron:

```bash
sudo apt-get update
sudo apt-get install -y build-essential pkg-config clang libclang-dev \
  libasound2-dev libpulse-dev libpipewire-0.3-dev \
  libgtk-3-dev libnotify-dev libnss3 libxss1 libxtst6 xdg-utils
```

Other distributions ship equivalent packages. The playback engine's Linux backend enables ALSA, PulseAudio, and PipeWire simultaneously — installing just one backend's dev libraries is not enough.

### About FFmpeg

EchoMusic does **not** require system FFmpeg dev libraries. The FFmpeg used by the playback engine is vendored inside the repository: `ffmpeg_slim.zip` (prebuilt FFmpeg libraries) and `configs.zip` (build configuration) under `native/echo-audio-player/vendor/ffmpeg-audio/crates/ffmpeg_audio_sys/vendor/`, unpacked and linked automatically during the build.

Only as a fallback when the vendored build fails can you set `FFMPEG_MODE=system` to link against system FFmpeg — this introduces extra dev library and runtime dynamic library dependencies and is not needed by default.

## Clone the Project

```bash
git clone https://github.com/hoowhoami/EchoMusic.git
cd EchoMusic
git submodule update --init --recursive
```

## Install Dependencies

```bash
pnpm install
```

> The `server` submodule is managed as a pnpm workspace member (see `pnpm-workspace.yaml`); the command above installs its runtime dependencies automatically. There is no need to run `npm install` inside the `server` directory.

### Electron Issue on Linux

If you hit the following error on Linux:

```
Error: ENOENT: no such file or directory, open '.../node_modules/electron/path.txt'
```

Manually download Electron into the target directory (use the version actually installed per `pnpm-lock.yaml`):

```bash
cd node_modules/.pnpm/electron@43.7.6/node_modules/electron/
mkdir -p dist
curl -L -o /tmp/electron.zip "https://npmmirror.com/mirrors/electron/v43.7.6/electron-v43.7.6-linux-x64.zip"
unzip -o /tmp/electron.zip -d dist/
printf '%s' './electron' > path.txt
```

## Build the Rust Native Modules

The `*.node` artifacts are not committed to the repository. **You must build them manually on first setup, after modifying Rust code, or after switching system/CPU architecture. A root-level `pnpm install` only covers the root project and the `server` workspace; `pnpm dev` / `pnpm build` never compile the native modules automatically.**

If startup fails with a missing `.node` file error:

```
Error: Cannot find module '.../echo-audio-player/echo-audio-player.node'
```

build the modules one by one per the table below (Linux skips `echo-platform-adaptor`; all other platforms build all 8):

| Module Directory | Purpose |
|----------|------|
| `native/echo-audio-player` | Playback, decoding, and audio effect processing |
| `native/echo-audio-capture` | System audio and microphone capture |
| `native/echo-media-controls` | System media controls |
| `native/echo-sqlite-store` | SQLite persistence |
| `native/echo-opencc` | Lyric Simplified/Traditional Chinese conversion |
| `native/echo-upnp` | DLNA / UPnP device control |
| `native/echo-airplay` | AirPlay device discovery and audio streaming |
| `native/echo-platform-adaptor` | Platform adaptation (system windows, taskbar; macOS / Windows) |

In each module directory run `npm install` to fetch its build dependencies, then `npm run build` (which is `napi build --release --no-const-enum`).

**macOS / Linux (Bash, from the repository root)**:

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

**Windows (PowerShell)**:

```powershell
$addons = @("echo-audio-player", "echo-audio-capture", "echo-media-controls", "echo-sqlite-store", "echo-opencc", "echo-upnp", "echo-airplay", "echo-platform-adaptor")
foreach ($addon in $addons) {
  Push-Location "native/$addon"
  try {
    npm install
    if ($LASTEXITCODE -ne 0) { throw "Failed to install build dependencies for $addon" }
    npm run build
    if ($LASTEXITCODE -ne 0) { throw "Failed to build $addon" }
  } finally {
    Pop-Location
  }
}
```

Each module produces a same-named `.node` in its own directory, e.g. `native/echo-audio-capture/echo-audio-capture.node`. Running only `cargo build --release` does not produce the artifact at the path the app expects — always use the napi-rs build scripts above.

For cross-compilation, prepare the target toolchain and SDK, run `rustup target add <target>`, then execute `npx napi build --release --no-const-enum --target <target>` in **each module directory**. x64 and arm64 artifacts must not be mixed; refer to the [CI build matrix](https://github.com/hoowhoami/EchoMusic/blob/main/.github/workflows/build.yml).

> After recompiling, quit EchoMusic completely and restart it — already loaded native modules are not reloaded by frontend hot updates.

## Start the Dev Server

```bash
pnpm dev
```

The dev-mode startup flow:

1. Vite starts the dev server, and `vite-plugin-electron` compiles and launches the Electron main process
2. The main process loads and initializes the Rust native modules
3. The main process initializes the Kugou API service in-process (the `server/` submodule, scanning the `module/` route table)
4. The main process creates the BrowserWindow, which loads the Vite dev server page
5. The renderer makes all API calls over IPC (`api:request`) directly to the main process — there is no HTTP port

## Memory Diagnostics

To observe memory changes of the Electron main, Renderer, and GPU processes, enable startup-phase memory diagnostics:

```bash
# macOS / Linux
ECHOMUSIC_MEMORY_DIAGNOSTICS=1 pnpm dev

# Windows PowerShell
$env:ECHOMUSIC_MEMORY_DIAGNOSTICS = "1"
pnpm dev
```

Logs are written to the Electron log file, e.g. on macOS:

```text
~/Library/Logs/EchoMusic/echo-music-YYYY-MM-DD.log
```

## Debugging

### Recommended IDE

The project ships a `.vscode/extensions.json` with recommended extensions; VS Code will prompt to install them when you open the project. Recommended extensions include Vue (Volar), ESLint, Prettier, Tailwind CSS IntelliSense, and Iconify.

### Frontend Debugging

- Press `Ctrl + Shift + I` (Windows/Linux) or `Cmd + Option + I` (macOS) inside the Electron window to open DevTools
- Vue DevTools is enabled automatically in dev mode

### Main Process & API Service Debugging

- Main process and API service (server submodule) logs are written via electron-log
- Check the DevTools or the log file for `[IPC-Server]`-prefixed API route loading logs

### Rust Module Debugging

- Build with `cargo build` (without `--release`) for richer debug information
- `rust-analyzer` is recommended for code intelligence and debugging

## FAQ

### pnpm install fails

Make sure pnpm 9+ is installed:

```bash
pnpm --version
# If the version is too old
npm install -g pnpm@latest
```

### Slow Rust compilation

The first Rust build is slow (dependency download + compilation); incremental builds are much faster. A domestic mirror can speed up downloads:

```bash
# ~/.cargo/config.toml
[source.crates-io]
replace-with = 'mirror'

[source.mirror]
registry = "sparse+https://mirrors.tuna.tsinghua.edu.cn/crates.io-index/"
```

### Unable to find libclang

Check the LLVM/libclang installation and `LIBCLANG_PATH`; it should point to the directory containing `libclang.dll` (Windows) or the libclang library (macOS/Linux), not an executable.

### FFmpeg falls back to system FFmpeg

If the build log shows `Falling back to attempting to link the system's FFmpeg`, verify that `ffmpeg_slim.zip` and `configs.zip` under `native/echo-audio-player/vendor/ffmpeg-audio/crates/ffmpeg_audio_sys/vendor/` are intact. The default build needs no system FFmpeg and no `FFMPEG_MODE=system`.

### pkg-config errors for ALSA / PulseAudio / PipeWire on Linux

Install all three audio backend dev libraries listed in the prerequisites (none can be skipped), and make sure `pkg-config` can find libraries of the target architecture.

### Port conflict

The Vite dev server port can be changed in the `server` section of `vite.config.mts`.
