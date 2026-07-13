---
title: Build & Packaging
---

# 🏗️ Build & Packaging

This guide covers EchoMusic's build process and multi-platform packaging.

## Development Mode

````bash
# Start dev server with hot reload
pnpm dev
````

Development mode features:
- Vite dev server with Hot Module Replacement (HMR)
- Electron main process auto-starts
- Vue DevTools enabled by default
- Native modules compiled on first launch

## Production Build

````bash
# Compile frontend + package Electron app
pnpm build
````

Build process:

1. **Frontend compilation**: Vite compiles Vue components to static assets
2. **TypeScript compilation**: Compiles main process and backend TypeScript code
3. **Rust compilation**: Compiles all native modules (release mode)
4. **Electron Builder packaging**: Packages into platform-specific installers
5. **Post-packaging**: Runs `build/afterPack.js` hook script

### Post-Packaging Hook (afterPack.js)

`build/afterPack.js` executes after Electron Builder completes packaging, handling:

- Cleaning up unnecessary build artifacts
- Adjusting platform-specific file structures
- Handling symlinks and permissions

## Build Artifacts

After a successful build, the `release/` directory contains:

| Platform | Format | File |
|------|------|------|
| **macOS** | DMG installer | `EchoMusic-{version}.dmg` |
| **macOS** | ZIP archive | `EchoMusic-{version}-mac.zip` |
| **Windows** | NSIS installer | `EchoMusic-Setup-{version}.exe` |
| **Windows** | Portable | `EchoMusic-{version}-portable.exe` |
| **Linux** | deb package | `EchoMusic_{version}_amd64.deb` |
| **Linux** | rpm package | `EchoMusic-{version}.x86_64.rpm` |
| **Linux** | AppImage | `EchoMusic-{version}.AppImage` |
| **Linux** | tar.gz | `EchoMusic-{version}.tar.gz` |

## Build Configuration

Electron Builder config file: `electron-builder.yml`

Key settings:

````yaml
appId: com.echomusic.app
productName: EchoMusic
directories:
  output: release
mac:
  target:
    - dmg
    - zip
  icon: build/icons/icon.icns
win:
  target:
    - nsis
    - portable
  icon: build/icons/icon.ico
linux:
  target:
    - deb
    - rpm
    - AppImage
    - tar.gz
  icon: build/icons/icon.png
````

## CI/CD Automated Builds

EchoMusic uses GitHub Actions for continuous integration and release publishing. Config files are in `.github/workflows/`.

### Workflow Overview

| Workflow | File | Description |
|--------|------|------|
| Build & Release | `build.yml` (21KB) | Multi-platform auto-build & GitHub Release publishing |
| AI Labeler | `issue-ai-labeler.yml` | AI-powered automatic issue labeling |
| Auto Close | `issue-closer.yml` | Auto-close long-inactive issues |

### Build & Release Workflow

Automatically triggers when a `v*` tag is pushed (e.g., `v1.0.0`).

**Build Matrix**:

| Platform | Runner | Artifacts |
|------|--------|------|
| macOS x64 | `macos-13` | dmg + zip |
| macOS arm64 | `macos-latest` | dmg + zip |
| Windows x64 | `windows-latest` | NSIS installer + portable |
| Linux x64 | `ubuntu-latest` | deb + rpm + AppImage + tar.gz |

**CI Pipeline**:

1. Checkout code (with submodules)
2. Setup pnpm + Node.js 20
3. Install dependencies (`pnpm install`)
4. Compile Rust native modules (cross-platform builds)
5. Compile frontend assets (`pnpm build`)
6. Electron Builder packaging
7. Upload artifacts to GitHub Releases
8. Generate Release Notes

### Issue Management Automation

**AI Labeler (issue-ai-labeler.yml)**:

- Trigger: On new Issue creation
- Function: AI analyzes Issue content and auto-applies classification labels
- Labels: bug, enhancement, documentation, etc.

**Auto Closer (issue-closer.yml)**:

- Trigger: Scheduled periodic execution
- Function: Auto-closes issues without `bug` or `enhancement` labels that have been inactive for a long period
- Adds `stale` label and comment reminder before closing

## Publishing a New Version

1. Ensure all changes are committed and tested
2. Update version number in `package.json`
3. Update `CHANGELOG.md` with changes
4. Create a Git tag:

````bash
git tag v1.0.0
git push origin v1.0.0
````

5. GitHub Actions will auto-build and publish to Releases

## Auto-Update

EchoMusic has built-in update detection (`electron/updater.ts`):

- Checks GitHub Releases for new versions on launch
- Supports silent download of update packages
- Prompts user to install after download
- Cross-platform support (macOS/Windows/Linux)

## Platform-Specific Notes

### macOS

- Must compile on macOS — cross-compilation is limited
- Apple Developer certificate required for code signing (optional)
- Unsigned builds require manual Gatekeeper bypass:

  ```bash
  xattr -cr /Applications/EchoMusic.app && codesign --force --deep --sign - /Applications/EchoMusic.app
  ```

- Separate x64 and arm64 build targets

### Windows

- Must compile on Windows
- NSIS installer recommended (better user experience)
- Portable version suitable for USB drives

### Linux

- Compile on Ubuntu environment
- AppImage offers best compatibility — recommended as first choice
- deb/rpm for distro-native package management
