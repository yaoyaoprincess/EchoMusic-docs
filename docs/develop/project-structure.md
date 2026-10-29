---
title: 项目结构
---

# 📁 项目结构

本文详细介绍 EchoMusic 项目的目录结构和各模块职责。以下结构以 `main` 分支实际代码为准。

## 目录树

```
EchoMusic/
├── .github/                        # GitHub CI/CD 与社区配置
│   ├── ISSUE_TEMPLATE/             # Issue 模板（bug_report / feature_request）
│   └── workflows/                  # GitHub Actions 工作流
│       ├── build.yml               # 多平台构建与 Release 发布（Tag 触发）
│       ├── build-native.yml        # 原生模块 CI 产物（手动触发）
│       ├── issue-ai-labeler.yml    # AI 判定 Issue 合规性
│       └── issue-closer.yml        # 自动关闭无效 Issue
├── .vscode/
│   └── extensions.json             # 推荐 VS Code 扩展
├── build/                          # 打包资源（electron-builder buildResources）
│   ├── entitlements.mac.plist      # macOS 签名 entitlements
│   ├── entitlements.mac.inherit.plist
│   ├── installer.nsh               # NSIS 安装器钩子脚本
│   └── icons/                      # 应用与托盘图标
├── cloudflare/
│   └── plugin-marketplace-worker/  # 插件源市场 Cloudflare Worker
├── docs/                           # 仓库内开发文档（DSP Provider、插件系统、打包说明等）
├── native/                         # Rust 原生模块（napi-rs），9 个 crate
│   ├── echo-audio-player/          # 播放、解码及音效处理（内嵌 FFmpeg/SoundTouch vendor）
│   ├── echo-audio-capture/         # 系统音频与麦克风采集
│   ├── echo-media-controls/        # 系统媒体控制（SMTC / MPRIS / MPNowPlayingInfoCenter）
│   ├── echo-sqlite-store/          # SQLite 持久化存储
│   ├── echo-opencc/                # 歌词简繁转换
│   ├── echo-upnp/                  # DLNA / UPnP 设备控制
│   ├── echo-airplay/               # AirPlay 设备发现与音频发送
│   ├── echo-platform-adaptor/      # 系统窗口、任务栏等平台适配（macOS / Windows）
│   └── echo-native-log/            # 原生日志（内部依赖 crate，不随安装包分发）
├── scripts/                        # 开发辅助脚本（托盘图标生成、任务栏诊断等）
├── screenshots/                    # README 界面截图
├── server/                         # 酷狗 API 服务：KuGouMusicApi git 子模块
│   └── module/                     # 235 个 API module（路由按文件名派生）
├── src/                            # 应用源码（主进程 / 渲染进程 / 共享代码）
│   ├── main/                       # Electron 主进程
│   ├── preload/                    # 预加载脚本（contextBridge）
│   ├── renderer/                   # Vue 3 渲染进程
│   ├── shared/                     # 主/渲染进程共享类型与工具
│   ├── desktop-lyric/              # 桌面歌词窗口入口（App.vue + main.ts）
│   ├── plugin-window/              # 插件浮窗进程入口
│   └── shims-vue.d.ts
├── tests/                          # node:test 原生测试（275 个 *.test.ts / *.test.mjs）
├── desktop-lyric.html              # 桌面歌词窗口 HTML 入口
├── index.html                      # 主窗口 HTML 入口
├── plugin-window.html              # 插件浮窗 HTML 入口
├── taskbar-player.html             # 任务栏播放器 HTML 入口
├── eslint.config.js                # ESLint 扁平配置
├── .eslintrc.json                  # 旧版 ESLint 配置（并存）
├── .prettierrc / .prettierignore   # Prettier 格式化配置
├── .npmrc                          # npm/pnpm 配置
├── .gitmodules                     # Git 子模块配置（server → KuGouMusicApi）
├── pnpm-workspace.yaml             # pnpm workspace（根项目 + server）
├── vite.config.mts                 # Vite 配置（Vue / Tailwind / Electron 多入口）
├── tsconfig.json / tsconfig.node.json
├── CHANGELOG.md                    # 版本更新日志
├── THIRD_PARTY_NOTICES.md          # 第三方依赖授权说明
├── LICENSE / LICENSES/             # GPL-3.0 与第三方许可证
├── package.json                    # 项目配置（打包配置在 build 键中）
└── pnpm-lock.yaml                  # 依赖锁定
```

## src/ 应用源码

### src/main/ — Electron 主进程

主进程按子系统划分，入口为 `index.ts`：

| 目录/文件 | 说明 |
|-----------|------|
| `ipc/` | IPC 处理器按域拆分：`player.ts`、`settings.ts`（含自动更新）、`plugins.ts`、`window.ts`、`output.ts`、`server.ts`（`api:request`）等 20+ 文件，统一在 `registry.ts` 注册 |
| `server.ts` | 进程内加载 `server/` 子模块，处理渲染进程的 API 请求 |
| `player/` | 播放控制器、会话、DSP Provider 注册、内嵌封面缓存 |
| `mediaTransport/` | DLNA/UPnP 发现与控制、RAOP（AirPlay）适配 |
| `outputs/` | 本机/投放输出的会话管理与命令门控 |
| `plugins/` | 插件安装事务、市场缓存、文件授权、插件网络/TCP/SQLite 通道、插件浮窗（`windows.ts`） |
| `window/` | 窗口创建与背景材质（Mica/Acrylic/Hyprland）、全屏、窗口模式 |
| `storage/` | KV 存储、设置、播放队列、历史（经 echo-sqlite-store） |
| `desktopLyric/` | 桌面歌词窗口管理 |
| `external/` | 外部平台歌单导入（网易云、QQ 音乐、酷我、汽水、Spotify、Apple Music 等） |
| `media/` | 本地音乐文件扫描与元数据 |
| `downloads/` | 下载引擎 |
| `opencc/` | 简繁转换（echo-opencc 调用封装） |
| `diagnostics/` | 内存诊断 |
| `app.ts` | 应用生命周期编排（托盘、任务栏、快捷键、协议处理等） |
| `tray.ts`、`mediaControls.ts`、`taskbarMediaBar.ts`、`miniPlayer.ts` 等 | 系统集成单文件模块 |

### src/renderer/ — Vue 3 渲染进程

| 目录/文件 | 说明 |
|-----------|------|
| `main.ts`、`App.vue` | 应用入口与根组件 |
| `views/` | 页面组件：`Home.vue`、`Explore.vue`、`Search.vue`、`Cloud.vue`、`FreeListen.vue`、`PersonalFm.vue`、`Recognize.vue`、`Settings.vue`、`Ranking.vue`、`History.vue` 等；`details/` 存放歌曲/歌手/专辑/歌单/MV 详情页，`lyric/` 为全屏歌词页（含 AMLL 模式与皮肤系统），`settings/`、`plugins/`、`search/` 按功能拆分组件 |
| `stores/` | Pinia 状态：`player.ts`（含 `player/` 子模块 20+ 文件）、`playlist.ts`（含 `playlist/` 子目录）、`user.ts`、`setting.ts`、`auth.ts`、`lyric.ts`、`theme.ts`、`output.ts`、`historyStore.ts`、`sqlitePersist.ts`（自研持久化插件）等 25+ |
| `components/` | 通用组件（120+ 文件）：播放栏、队列、歌词面板等 |
| `composables/` | 组合式函数（27+ 文件） |
| `api/` | 酷狗 API 请求封装（`music.ts`、`search.ts`、`user.ts`、`playlist.ts`、`artist.ts` 等，按域拆分） |
| `services/` | 渲染层服务 |
| `router/` | Vue Router 路由配置 |
| `taskbarPlayer/`、`miniPlayer/`、`nowPlaying/` | 任务栏播放器、mini 模式、正在播放界面 |
| `plugins/` | 插件运行时（渲染进程侧） |
| `theme/`、`constants/`、`layouts/`、`models/`、`utils/`、`tasks/` | 主题、常量、布局、模型、工具（66+ 文件）、后台任务 |

### src/shared/ 与 src/preload/

| 目录 | 说明 |
|------|------|
| `src/shared/` | 主/渲染进程共享代码（70+ 文件）：类型定义、播放决策、持久化协议、更新笔记、主题、窗口策略等，保证两端行为一致 |
| `src/preload/` | `index.ts` 为 preload 入口（contextBridge 暴露 API 面），`pluginResources.ts` 为插件资源 preload |

### 独立窗口入口

| 文件/目录 | 说明 |
|-----------|------|
| `index.html` + `src/renderer/` | 主窗口 |
| `desktop-lyric.html` + `src/desktop-lyric/` | 桌面歌词窗口 |
| `taskbar-player.html` + `src/renderer/taskbarPlayer/` | 任务栏播放器窗口（Windows） |
| `plugin-window.html` + `src/plugin-window/` | 插件浮窗（独立窗口进程） |

## server/ 子模块

`server/` 是 [MakcRe/KuGouMusicApi](https://github.com/MakcRe/KuGouMusicApi) 的 git 子模块（`.gitmodules` 声明），同时是 pnpm workspace 成员，根目录 `pnpm install` 会一并安装其依赖。它不是自研路由服务：

- API 路由由 `module/*.js` 文件名派生（如 `song_url.js` → `/song/url`），锁定版本共 235 个模块
- 主进程 `src/main/server.ts` 在进程内加载并调用这些 module，无独立 HTTP 服务
- 详见[酷狗 API 参考](/develop/kugou-api)

## 原生模块（native/）

每个原生模块都是独立的 Rust crate，通过 napi-rs 编译为同名 `.node` 文件（如 `native/echo-audio-capture/echo-audio-capture.node`），在 Electron 主进程中直接加载调用。`echo-audio-player` 内嵌 `vendor/ffmpeg-audio`（FFmpeg 解码库，构建时从 vendored 的 `ffmpeg_slim.zip` 解包，无需系统 FFmpeg）。构建方式见[本地开发环境](/develop/local-dev)，模块 API 见[原生模块](/develop/native-addons)。

## 关键文件说明

### 入口文件

| 文件 | 说明 |
|------|------|
| `index.html` | Vite 主入口，加载 `src/renderer/main.ts` |
| `src/main/index.ts` | Electron 主进程入口（协议注册、GPU/高 DPI 设置、加载 `app.ts`） |
| `src/preload/index.ts` | 预加载脚本，contextBridge 暴露 `window.electron.api` |

### 配置文件

| 文件 | 说明 |
|------|------|
| `vite.config.mts` | Vite 构建配置：4 个 HTML 入口、`@vitejs/plugin-vue`、Tailwind（`@tailwindcss/vite`）、`vite-plugin-electron`（主进程 + preload）、bundle 分析 |
| `package.json` | 项目与依赖配置；多平台打包配置内嵌在 `build` 键中（appId、extraResources、nsis/dmg/deb 等） |
| `pnpm-workspace.yaml` | workspace 成员：根项目与 `server` |
| `tsconfig.json` / `tsconfig.node.json` | TypeScript 编译选项 |
| `eslint.config.js` | ESLint 扁平配置（`.eslintrc.json` 为旧版并存配置） |
| `.prettierrc` / `.prettierignore` | Prettier 代码格式化配置 |
| `.npmrc` | npm/pnpm 镜像与配置 |
| `.gitmodules` | 子模块配置：`server` → MakcRe/KuGouMusicApi |

### 打包资源（build/）

| 文件 | 说明 |
|------|------|
| `build/entitlements.mac.plist` | macOS 硬化运行时 entitlements |
| `build/entitlements.mac.inherit.plist` | 子进程继承的 entitlements |
| `build/installer.nsh` | NSIS 安装器钩子脚本（Windows 安装逻辑定制） |
| `build/icons/` | 应用图标、托盘模板图标（`IconTemplate.png` 等）与图标源文件 |

### GitHub 工作流

| 文件 | 说明 |
|------|------|
| `.github/workflows/build.yml` | Tag 推送触发的 6 目标构建矩阵（macOS/Linux/Windows × x64/arm64）、Release 草稿发布、Telegram/QQ 群通知 |
| `.github/workflows/build-native.yml` | 手动触发的原生模块编译工作流，按平台产出 CI artifact（不发布 Release） |
| `.github/workflows/issue-ai-labeler.yml` | 使用 AI 判定新 Issue 是否符合模板规范，不合规自动标记 `invalid` |
| `.github/workflows/issue-closer.yml` | 每日定时关闭被标记 `invalid` 的 Issue |
