---
title: Project Structure
---

# 📁 Project Structure

This document details the directory structure of the EchoMusic project and the responsibility of each module. The structure below reflects the actual code on the `main` branch.

## Directory Tree

```
EchoMusic/
├── .github/                        # GitHub CI/CD and community configuration
│   ├── ISSUE_TEMPLATE/             # Issue templates (bug_report / feature_request)
│   └── workflows/                  # GitHub Actions workflows
│       ├── build.yml               # Multi-platform build & Release publishing (tag-triggered)
│       ├── build-native.yml        # Native module CI artifacts (manual trigger)
│       ├── issue-ai-labeler.yml    # AI-based Issue validity check
│       └── issue-closer.yml        # Auto-close invalid Issues
├── .vscode/
│   └── extensions.json             # Recommended VS Code extensions
├── build/                          # Packaging resources (electron-builder buildResources)
│   ├── entitlements.mac.plist      # macOS signing entitlements
│   ├── entitlements.mac.inherit.plist
│   ├── installer.nsh               # NSIS installer hook script
│   └── icons/                      # App and tray icons
├── cloudflare/
│   └── plugin-marketplace-worker/  # Plugin marketplace Cloudflare Worker
├── docs/                           # In-repo development docs (DSP provider, plugin system, packaging notes, etc.)
├── native/                         # Rust native modules (napi-rs), 9 crates
│   ├── echo-audio-player/          # Playback, decoding, and audio effects (embedded FFmpeg/SoundTouch vendor)
│   ├── echo-audio-capture/         # System audio and microphone capture
│   ├── echo-media-controls/        # System media controls (SMTC / MPRIS / MPNowPlayingInfoCenter)
│   ├── echo-sqlite-store/          # SQLite persistence
│   ├── echo-opencc/                # Lyric Simplified/Traditional Chinese conversion
│   ├── echo-upnp/                  # DLNA / UPnP device control
│   ├── echo-airplay/               # AirPlay device discovery and audio streaming
│   ├── echo-platform-adaptor/      # Platform adaptation (system windows, taskbar; macOS / Windows)
│   └── echo-native-log/            # Native logging (internal dependency crate, not distributed)
├── scripts/                        # Development helper scripts (tray icon generation, taskbar diagnostics, etc.)
├── screenshots/                    # README screenshots
├── server/                         # Kugou API service: KuGouMusicApi git submodule
│   └── module/                     # 235 API modules (routes derived from file names)
├── src/                            # App source code (main / renderer / shared)
│   ├── main/                       # Electron main process
│   ├── preload/                    # Preload scripts (contextBridge)
│   ├── renderer/                   # Vue 3 renderer
│   ├── shared/                     # Shared types and utilities for main/renderer
│   ├── desktop-lyric/              # Desktop lyric window entry (App.vue + main.ts)
│   ├── plugin-window/              # Plugin floating window process entry
│   └── shims-vue.d.ts
├── tests/                          # node:test native tests (275 *.test.ts / *.test.mjs files)
├── desktop-lyric.html              # Desktop lyric window HTML entry
├── index.html                      # Main window HTML entry
├── plugin-window.html              # Plugin floating window HTML entry
├── taskbar-player.html             # Taskbar player HTML entry
├── eslint.config.js                # ESLint flat config
├── .eslintrc.json                  # Legacy ESLint config (kept alongside)
├── .prettierrc / .prettierignore   # Prettier formatting config
├── .npmrc                          # npm/pnpm configuration
├── .gitmodules                     # Git submodule config (server → KuGouMusicApi)
├── pnpm-workspace.yaml             # pnpm workspace (root project + server)
├── vite.config.mts                 # Vite config (Vue / Tailwind / Electron multi-entry)
├── tsconfig.json / tsconfig.node.json
├── CHANGELOG.md                    # Release changelog
├── THIRD_PARTY_NOTICES.md          # Third-party dependency notices
├── LICENSE / LICENSES/             # GPL-3.0 and third-party licenses
├── package.json                    # Project config (packaging config lives in the build key)
└── pnpm-lock.yaml                  # Dependency lockfile
```

## src/ Application Source Code

### src/main/ — Electron Main Process

The main process is organized into subsystems with the entry at `index.ts`:

| Directory/File | Description |
|-----------|------|
| `ipc/` | IPC handlers split by domain: `player.ts`, `settings.ts` (includes auto-update), `plugins.ts`, `window.ts`, `output.ts`, `server.ts` (`api:request`) and 20+ more, registered via `registry.ts` |
| `server.ts` | Loads the `server/` submodule in-process and handles renderer API requests |
| `player/` | Playback controller, session, DSP provider registry, embedded cover cache |
| `mediaTransport/` | DLNA/UPnP discovery and control, RAOP (AirPlay) adapter |
| `outputs/` | Session management and command gating for local/cast outputs |
| `plugins/` | Plugin install transactions, marketplace cache, file grants, plugin network/TCP/SQLite channels, plugin floating windows (`windows.ts`) |
| `window/` | Window creation and background materials (Mica/Acrylic/Hyprland), fullscreen, window modes |
| `storage/` | KV storage, settings, playback queues, history (via echo-sqlite-store) |
| `desktopLyric/` | Desktop lyric window management |
| `external/` | External playlist import (Netease, QQ Music, Kuwo, Qishui, Spotify, Apple Music, etc.) |
| `media/` | Local music file scanning and metadata |
| `downloads/` | Download engine |
| `opencc/` | Chinese conversion (echo-opencc wrapper) |
| `diagnostics/` | Memory diagnostics |
| `app.ts` | Application lifecycle orchestration (tray, taskbar, shortcuts, protocol handling, etc.) |
| `tray.ts`, `mediaControls.ts`, `taskbarMediaBar.ts`, `miniPlayer.ts`, etc. | Single-file system integration modules |

### src/renderer/ — Vue 3 Renderer

| Directory/File | Description |
|-----------|------|
| `main.ts`, `App.vue` | App entry and root component |
| `views/` | Page components: `Home.vue`, `Explore.vue`, `Search.vue`, `Cloud.vue`, `FreeListen.vue`, `PersonalFm.vue`, `Recognize.vue`, `Settings.vue`, `Ranking.vue`, `History.vue`, etc.; `details/` holds song/artist/album/playlist/MV detail pages, `lyric/` is the fullscreen lyric page (AMLL mode and skin system), `settings/`, `plugins/`, `search/` split components by feature |
| `stores/` | Pinia stores: `player.ts` (with 20+ files under `player/`), `playlist.ts` (with the `playlist/` subdirectory), `user.ts`, `setting.ts`, `auth.ts`, `lyric.ts`, `theme.ts`, `output.ts`, `historyStore.ts`, `sqlitePersist.ts` (custom persistence plugin) and 25+ more |
| `components/` | Shared components (120+ files): player bar, queue, lyric panel, etc. |
| `composables/` | Composables (27+ files) |
| `api/` | Kugou API request wrappers (`music.ts`, `search.ts`, `user.ts`, `playlist.ts`, `artist.ts`, etc., split by domain) |
| `services/` | Renderer-side services |
| `router/` | Vue Router configuration |
| `taskbarPlayer/`, `miniPlayer/`, `nowPlaying/` | Taskbar player, mini mode, now-playing UI |
| `plugins/` | Plugin runtime (renderer side) |
| `theme/`, `constants/`, `layouts/`, `models/`, `utils/`, `tasks/` | Theme, constants, layouts, models, utilities (66+ files), background tasks |

### src/shared/ and src/preload/

| Directory | Description |
|------|------|
| `src/shared/` | Code shared by main/renderer (70+ files): types, playback decisions, persistence protocol, update notes, theme, window strategies, etc., keeping both sides consistent |
| `src/preload/` | `index.ts` is the preload entry (contextBridge API surface), `pluginResources.ts` is the plugin resource preload |

### Standalone Window Entries

| File/Directory | Description |
|-----------|------|
| `index.html` + `src/renderer/` | Main window |
| `desktop-lyric.html` + `src/desktop-lyric/` | Desktop lyric window |
| `taskbar-player.html` + `src/renderer/taskbarPlayer/` | Taskbar player window (Windows) |
| `plugin-window.html` + `src/plugin-window/` | Plugin floating window (separate window process) |

## server/ Submodule

`server/` is a git submodule of [MakcRe/KuGouMusicApi](https://github.com/MakcRe/KuGouMusicApi) (declared in `.gitmodules`) and is also a pnpm workspace member, so a root-level `pnpm install` installs its dependencies too. It is not a self-written routing service:

- API routes are derived from `module/*.js` file names (e.g. `song_url.js` → `/song/url`); the pinned version has 235 modules
- The main process `src/main/server.ts` loads and calls these modules in-process with no standalone HTTP server
- See the [Kugou API Reference](/en/develop/kugou-api) for details

## Native Modules (native/)

Each native module is an independent Rust crate compiled via napi-rs into a same-named `.node` file (e.g. `native/echo-audio-capture/echo-audio-capture.node`) and loaded directly in the Electron main process. `echo-audio-player` embeds `vendor/ffmpeg-audio` (an FFmpeg decoding library unpacked at build time from the vendored `ffmpeg_slim.zip`, so no system FFmpeg is required). See [Local Dev Setup](/en/develop/local-dev) for build instructions and [Native Addons](/en/develop/native-addons) for module APIs.

## Key Files

### Entry Files

| File | Description |
|------|------|
| `index.html` | Vite main entry, loads `src/renderer/main.ts` |
| `src/main/index.ts` | Electron main process entry (protocol registration, GPU/high-DPI settings, loads `app.ts`) |
| `src/preload/index.ts` | Preload script exposing `window.electron.api` via contextBridge |

### Configuration Files

| File | Description |
|------|------|
| `vite.config.mts` | Vite build config: 4 HTML entries, `@vitejs/plugin-vue`, Tailwind (`@tailwindcss/vite`), `vite-plugin-electron` (main + preload), bundle analysis |
| `package.json` | Project and dependency config; the multi-platform packaging config is embedded in the `build` key (appId, extraResources, nsis/dmg/deb, etc.) |
| `pnpm-workspace.yaml` | Workspace members: the root project and `server` |
| `tsconfig.json` / `tsconfig.node.json` | TypeScript compiler options |
| `eslint.config.js` | ESLint flat config (`.eslintrc.json` is a legacy config kept alongside) |
| `.prettierrc` / `.prettierignore` | Prettier formatting config |
| `.npmrc` | npm/pnpm mirror and configuration |
| `.gitmodules` | Submodule config: `server` → MakcRe/KuGouMusicApi |

### Packaging Resources (build/)

| File | Description |
|------|------|
| `build/entitlements.mac.plist` | macOS hardened runtime entitlements |
| `build/entitlements.mac.inherit.plist` | Entitlements inherited by child processes |
| `build/installer.nsh` | NSIS installer hook script (Windows install customization) |
| `build/icons/` | App icons, tray template icons (`IconTemplate.png`, etc.), and icon sources |

### GitHub Workflows

| File | Description |
|------|------|
| `.github/workflows/build.yml` | Tag-triggered 6-target build matrix (macOS/Linux/Windows × x64/arm64), draft Release publishing, Telegram/QQ group notifications |
| `.github/workflows/build-native.yml` | Manually triggered native module build workflow that produces per-platform CI artifacts (no Release publishing) |
| `.github/workflows/issue-ai-labeler.yml` | Uses AI to check whether new Issues follow the template rules and labels non-compliant ones `invalid` |
| `.github/workflows/issue-closer.yml` | Daily scheduled job that closes Issues labeled `invalid` |
