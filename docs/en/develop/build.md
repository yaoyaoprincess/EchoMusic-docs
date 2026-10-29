---
title: Build & Packaging
---

# 🏗️ Build & Packaging

This guide covers EchoMusic's build process and multi-platform packaging.

## Development Mode

````bash
# Start the dev server (hot reload)
pnpm dev
````

Dev mode features:

- Vite dev server provides hot module replacement (HMR)
- The Electron main process is compiled and launched automatically by `vite-plugin-electron`
- Vue DevTools is enabled automatically
- **Native modules are never compiled automatically**: neither `pnpm dev` nor `pnpm build` compiles the Rust modules — build them manually first as described in [Local Dev Setup](/en/develop/local-dev#build-the-rust-native-modules)

## Production Build

````bash
# Type check + frontend build + electron-builder packaging
pnpm build
````

`pnpm build` runs the following in order:

1. **Type check**: `vue-tsc --noEmit`
2. **Frontend build**: Vite builds the 4 entries (main window, desktop lyrics, taskbar player, plugin floating window) plus the main process and preload
3. **Electron Builder packaging**: output goes to the `release/` directory

> Note: `build.npmRebuild` is disabled in `package.json`, so packaging **only copies the existing `.node` artifacts and never compiles them for you**. Before packaging, make sure all native modules have been built for the target platform/architecture — Windows / macOS require all 8 modules, and Linux requires the 7 modules other than `echo-platform-adaptor`.

Platform shortcut scripts are also available (they reinstall the server runtime dependencies with `--omit=dev` before packaging):

````bash
pnpm build:win    # Windows x64
pnpm build:mac    # macOS
pnpm build:linux  # Linux
````

## Build Artifacts

There are 6 build targets (3 platforms × x64/arm64); artifacts are generated in the `release/` directory:

| Platform | Arch | Format | Example File |
|------|------|------|----------|
| **macOS** | arm64 / x64 | DMG installer | `EchoMusic-{version}-macOS-arm64.dmg` |
| **macOS** | arm64 / x64 | ZIP archive | `EchoMusic-{version}-mac.zip` |
| **Windows** | x64 / arm64 | NSIS installer | `EchoMusic-{version}-Windows-Setup-{arch}.exe` |
| **Linux** | x64 / arm64 | AppImage | `EchoMusic-{version}-{os}-{arch}.AppImage` |
| **Linux** | x64 / arm64 | deb package | `EchoMusic_{version}_amd64.deb` |
| **Linux** | x64 / arm64 | pacman package | `EchoMusic-{version}-{os}-{arch}.pkg.tar.zst` |
| **Linux** | x64 / arm64 | rpm package | `EchoMusic-{version}.{arch}.rpm` |
| **Linux** | x64 / arm64 | tar.gz | `EchoMusic-{version}-{os}-{arch}.tar.gz` |

## Build Configuration

The packaging config is not a standalone file — it is embedded in the `build` key of `package.json` (electron-builder configuration). Key settings:

````jsonc
{
  "build": {
    "appId": "com.hoowhoami.echomusic",
    "productName": "EchoMusic",
    "publish": [{ "provider": "github", "owner": "hoowhoami", "repo": "EchoMusic" }],
    "npmRebuild": false,
    "directories": { "output": "release", "buildResources": "build" },
    "protocols": [{ "name": "EchoMusic Share", "schemes": ["echomusic"] }],
    "files": ["dist", "dist-electron"],
    "extraResources": [
      // 7 native module .node files (echo-audio-player, echo-audio-capture, echo-media-controls,
      // echo-sqlite-store, echo-opencc, echo-upnp, echo-airplay)
      // macOS / Windows platform configs additionally bundle echo-platform-adaptor.node
      // plus server/module, server/util, server/node_modules, build/icons, CHANGELOG, LICENSE, etc.
    ],
    "mac": { "target": ["zip", "dmg"], "hardenedRuntime": true, "entitlements": "build/entitlements.mac.plist" },
    "win": { "target": ["nsis"] },
    "linux": { "target": ["AppImage", "deb", "pacman", "rpm", "tar.gz"] },
    "nsis": { "oneClick": false, "allowToChangeInstallationDirectory": true, "include": "build/installer.nsh" }
  }
}
````

The related resource files live in the `build/` directory:

| File | Description |
|------|------|
| `build/installer.nsh` | NSIS installer hook script (Windows install customization) |
| `build/entitlements.mac.plist` | macOS hardened runtime entitlements |
| `build/entitlements.mac.inherit.plist` | Entitlements inherited by child processes |
| `build/icons/` | App and tray icons |

The app registers the `echomusic://` protocol ("EchoMusic Share") for opening share links.

## CI/CD Automated Builds

The project uses GitHub Actions for continuous integration and publishing; there are 4 workflows under `.github/workflows/`.

### Workflow Overview

| Workflow | File | Trigger | Description |
|--------|------|------|------|
| Build & Release | `build.yml` | `v*` tag push / manual | 6-target build matrix + Release publishing + Telegram/QQ group notifications |
| Native artifacts | `build-native.yml` | Manual only | Compiles native modules per platform and uploads CI artifacts (no Release) |
| AI labeler | `issue-ai-labeler.yml` | Issue opened/edited | AI checks whether the Issue follows the template rules and labels non-compliant ones `invalid` |
| Auto close | `issue-closer.yml` | Daily schedule | Closes Issues labeled `invalid` |

### Build & Release Workflow (build.yml)

Triggered automatically when a `v*` tag (e.g. `v1.0.0`) is pushed. The flow:

1. **prepare-release**: checks whether the previous Release is missing `latest*.yml` update metadata and converts it to a draft first, so electron-updater never sees an incomplete version
2. **build (6-target matrix)**:

| Target | Runner | Artifacts |
|------|--------|------|
| macOS arm64 | `macos-14` | dmg + zip (ad-hoc signing, `identity=-`) |
| macOS x64 | `macos-14` | dmg + zip (ad-hoc signing) |
| Linux x64 | `ubuntu-22.04` | AppImage + deb + pacman + rpm + tar.gz |
| Linux arm64 | `ubuntu-22.04-arm` | AppImage + deb + pacman + rpm + tar.gz |
| Windows x64 | `windows-latest` | NSIS installer |
| Windows arm64 | `windows-11-arm` | NSIS installer |

3. Each target builds the native modules in parallel (macOS uses `rustup target` cross/native compilation), then runs `vue-tsc`, `vite build`, and `electron-builder --publish never`
4. Artifact verification: macOS/Linux verify that `echo-audio-player.node` does not link system FFmpeg; each package and its update metadata are validated
5. **release**: extracts the version notes from `CHANGELOG.md`, uploads all artifacts as a draft first, then publishes (tags containing `-` are marked prerelease)
6. **notify / notify-qq**: after a successful release, pushes an update summary to the Telegram channel and the QQ group (OneBot API)

### Native Module CI Artifacts (build-native.yml)

Open GitHub Actions and click **Run workflow**; you can toggle macOS arm64/x64, Linux arm64/x64, and Windows arm64/x64 independently (all enabled by default). The selected targets are compiled in parallel in separate matrix jobs, and each target produces its own artifact (e.g. `EchoMusic-native-macos-arm64`). This workflow only uploads CI artifacts and never creates a Release; the artifact root directory is `native`, so after downloading and extracting it into the repository root, the `.node` layout required for local packaging is restored. Linux includes 7 modules; macOS / Windows additionally include `echo-platform-adaptor`.

## Publishing a New Version

1. Make sure all changes are committed and tested
2. Update the version number in `package.json`
3. Update `CHANGELOG.md` with the changes (CI extracts the Release notes and notification summary from it)
4. Create the Git tag:

````bash
git tag v1.0.0
git push origin v1.0.0
````

5. GitHub Actions builds and publishes to Releases automatically (tags containing `-` are marked as prereleases)

## Auto Update

The update logic lives in the main process at `src/main/ipc/settings.ts` (based on `electron-updater`):

- `autoDownload = false`: after a new version is detected, the user confirms before download; once downloaded, the update installs from inside the app
- Prerelease support: follows the in-app prerelease toggle (`allowPrerelease`); versions whose tags contain `-` are prereleases
- GitHub accelerator: a GitHub accelerator URL can be configured; if the accelerator fails, the updater automatically falls back to the official GitHub Releases
- macOS: the current distribution is ad-hoc signed and **does not support Squirrel.Mac automatic update installation**; the app offers a DMG manual download entry instead (Apple Silicon → arm64, Intel → x64)
- Arch Linux: no built-in installer is used; the app prompts to download the pacman package manually (`pacman -U`) or the tar.gz archive
- Online updates are disabled in dev mode

## Platform-Specific Notes

### macOS

- Must be built on macOS; CI uses the `x86_64-apple-darwin` / `aarch64-apple-darwin` targets respectively
- The current distribution is ad-hoc signed (`identity=-`) without an Apple Developer certificate; if the app fails to open after installation, run:

  ```bash
  xattr -cr /Applications/EchoMusic.app && codesign --force --deep --sign - /Applications/EchoMusic.app
  ```

### Windows

- Must be built on Windows (CI uses the `windows-latest` / `windows-11-arm` runners)
- Only an NSIS installer is provided (`oneClick: false`, custom install directory allowed); there is no portable build
- arm64 builds require the ARM64 C++ toolchain

### Linux

- CI uses `ubuntu-22.04` (x64) and `ubuntu-22.04-arm` (arm64)
- Artifacts include AppImage, deb, pacman (`.pkg.tar.zst`), rpm, and tar.gz
- AppImage has the best compatibility; deb/rpm/pacman suit their respective distributions' package management
