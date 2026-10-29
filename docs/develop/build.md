---
title: 编译与构建
---

# 🏗️ 编译与构建

本文介绍 EchoMusic 的编译构建流程和多平台打包方式。

## 开发模式

````bash
# 启动开发服务器（热重载）
pnpm dev
````

开发模式特点：

- Vite 开发服务器提供热模块替换（HMR）
- Electron 主进程由 `vite-plugin-electron` 自动编译并拉起
- Vue DevTools 自动启用
- **原生模块不会自动编译**：`pnpm dev` / `pnpm build` 都不会编译 Rust 模块，需先按[本地开发环境](/develop/local-dev#编译-rust-原生模块)手动构建

## 生产构建

````bash
# 类型检查 + 前端构建 + electron-builder 打包
pnpm build
````

`pnpm build` 依次执行：

1. **类型检查**：`vue-tsc --noEmit`
2. **前端编译**：Vite 构建 4 个入口（主窗口、桌面歌词、任务栏播放器、插件浮窗）与主进程/preload
3. **Electron Builder 打包**：输出到 `release/` 目录

> 注意：`package.json` 中 `build.npmRebuild` 已关闭，打包过程**只复制现有的 `.node` 产物，不会替你补编译**。打包前请确认所有原生模块已在目标平台/架构下构建完成——Windows / macOS 需包含全部 8 个模块，Linux 需包含除 `echo-platform-adaptor` 外的 7 个模块。

也可以使用平台快捷脚本（会先以 `--omit=dev` 重装 server 运行时依赖再打包）：

````bash
pnpm build:win    # Windows x64
pnpm build:mac    # macOS
pnpm build:linux  # Linux
````

## 打包产物

共 6 个构建目标（3 平台 × x64/arm64），构建完成后在 `release/` 目录生成：

| 平台 | 架构 | 格式 | 文件示例 |
|------|------|------|----------|
| **macOS** | arm64 / x64 | DMG 安装包 | `EchoMusic-{version}-macOS-arm64.dmg` |
| **macOS** | arm64 / x64 | ZIP 包 | `EchoMusic-{version}-mac.zip` |
| **Windows** | x64 / arm64 | NSIS 安装程序 | `EchoMusic-{version}-Windows-Setup-{arch}.exe` |
| **Linux** | x64 / arm64 | AppImage | `EchoMusic-{version}-{os}-{arch}.AppImage` |
| **Linux** | x64 / arm64 | deb 包 | `EchoMusic_{version}_amd64.deb` |
| **Linux** | x64 / arm64 | pacman 包 | `EchoMusic-{version}-{os}-{arch}.pkg.tar.zst` |
| **Linux** | x64 / arm64 | rpm 包 | `EchoMusic-{version}.{arch}.rpm` |
| **Linux** | x64 / arm64 | tar.gz | `EchoMusic-{version}-{os}-{arch}.tar.gz` |

## 打包配置

打包配置不在独立文件中，而是内嵌在 `package.json` 的 `build` 键（electron-builder 配置）。关键配置：

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
      // 7 个原生模块 .node（echo-audio-player、echo-audio-capture、echo-media-controls、
      // echo-sqlite-store、echo-opencc、echo-upnp、echo-airplay）
      // macOS / Windows 的平台配置额外附带 echo-platform-adaptor.node
      // server/module、server/util、server/node_modules、build/icons、CHANGELOG、LICENSE 等
    ],
    "mac": { "target": ["zip", "dmg"], "hardenedRuntime": true, "entitlements": "build/entitlements.mac.plist" },
    "win": { "target": ["nsis"] },
    "linux": { "target": ["AppImage", "deb", "pacman", "rpm", "tar.gz"] },
    "nsis": { "oneClick": false, "allowToChangeInstallationDirectory": true, "include": "build/installer.nsh" }
  }
}
````

相关资源文件位于 `build/` 目录：

| 文件 | 说明 |
|------|------|
| `build/installer.nsh` | NSIS 安装器钩子脚本（Windows 安装逻辑定制） |
| `build/entitlements.mac.plist` | macOS 硬化运行时 entitlements |
| `build/entitlements.mac.inherit.plist` | 子进程继承的 entitlements |
| `build/icons/` | 应用与托盘图标 |

应用注册 `echomusic://` 协议（"EchoMusic Share"），用于分享链接唤起。

## CI/CD 自动构建

项目使用 GitHub Actions 进行持续集成与发布，`.github/workflows/` 下共 4 个工作流。

### 工作流概览

| 工作流 | 文件 | 触发 | 说明 |
|--------|------|------|------|
| 构建发布 | `build.yml` | 推送 `v*` Tag / 手动 | 6 目标构建矩阵 + Release 发布 + Telegram/QQ 群通知 |
| 原生模块产物 | `build-native.yml` | 仅手动 | 按平台编译原生模块并上传 CI artifact（不发布 Release） |
| AI 标签 | `issue-ai-labeler.yml` | Issue 新建/编辑 | AI 判定 Issue 是否符合模板规范，不合规标记 `invalid` |
| 自动关闭 | `issue-closer.yml` | 每日定时 | 关闭被标记 `invalid` 的 Issue |

### 构建发布工作流（build.yml）

推送 `v*` 格式的 Tag（如 `v1.0.0`）时自动触发，流程：

1. **prepare-release**：检查旧 Release 是否缺少 `latest*.yml` 更新元数据，缺失则先转为草稿，避免 electron-updater 读到不完整的版本
2. **build（6 目标矩阵）**：

| 目标 | Runner | 产物 |
|------|--------|------|
| macOS arm64 | `macos-14` | dmg + zip（ad-hoc 签名，`identity=-`） |
| macOS x64 | `macos-14` | dmg + zip（ad-hoc 签名） |
| Linux x64 | `ubuntu-22.04` | AppImage + deb + pacman + rpm + tar.gz |
| Linux arm64 | `ubuntu-22.04-arm` | AppImage + deb + pacman + rpm + tar.gz |
| Windows x64 | `windows-latest` | NSIS 安装程序 |
| Windows arm64 | `windows-11-arm` | NSIS 安装程序 |

3. 各目标并行编译原生模块（macOS 通过 `rustup target` 交叉/原生编译），随后执行 `vue-tsc`、`vite build`、`electron-builder --publish never`
4. 产物校验：macOS/Linux 校验 `echo-audio-player.node` 未链接系统 FFmpeg，校验各平台安装包与更新元数据
5. **release**：从 `CHANGELOG.md` 提取对应版本说明，先以草稿上传全部产物，再发布（Tag 含 `-` 时标记为预发布）
6. **notify / notify-qq**：发布成功后向 Telegram 频道与 QQ 群（OneBot API）推送更新摘要

### 原生模块 CI 产物（build-native.yml）

进入 GitHub Actions 手动点击 **Run workflow**，可分别勾选 macOS arm64/x64、Linux arm64/x64、Windows arm64/x64（默认全选）。选中的目标在独立矩阵任务中并行编译，每个目标生成一个独立 artifact（如 `EchoMusic-native-macos-arm64`）。该流程只上传 CI artifact、不创建 Release；artifact 内目录根为 `native`，下载解压到仓库根目录即可恢复本地打包所需的 `.node` 布局。Linux 包含 7 个模块，macOS / Windows 额外包含 `echo-platform-adaptor`。

## 发布新版本

1. 确保所有改动已提交并测试通过
2. 更新 `package.json` 中的版本号
3. 更新 `CHANGELOG.md` 记录本次变更（CI 从中提取 Release Notes 与通知摘要）
4. 创建 Git Tag：

````bash
git tag v1.0.0
git push origin v1.0.0
````

5. GitHub Actions 自动构建并发布到 Releases（Tag 含 `-` 会标记为预发布版本）

## 自动更新

更新逻辑位于主进程 `src/main/ipc/settings.ts`（基于 `electron-updater`）：

- `autoDownload = false`：检测到新版本后由用户确认再下载，下载完成后在应用内安装
- 支持预发布：跟随设置中的预发布开关（`allowPrerelease`），Tag 含 `-` 的版本即预发布
- GitHub 加速源：支持配置 GitHub 加速地址，加速源失败时自动回退官方 GitHub Releases
- macOS：当前发行版为 ad-hoc 签名，**不支持 Squirrel.Mac 自动安装更新**，应用内提供 DMG 手动下载入口（Apple Silicon 选 arm64，Intel 选 x64）
- Arch Linux：不使用内置安装器，提示手动下载 pacman 包（`pacman -U`）或 tar.gz 安装
- 开发模式不支持在线更新

## 平台特定注意事项

### macOS

- 需在 macOS 环境下编译；CI 中 x64/arm64 分别使用 `x86_64-apple-darwin` / `aarch64-apple-darwin` 目标
- 当前发行版使用 ad-hoc 签名（`identity=-`），未配置 Apple Developer 证书；如安装后无法打开，执行：

  ```bash
  xattr -cr /Applications/EchoMusic.app && codesign --force --deep --sign - /Applications/EchoMusic.app
  ```

### Windows

- 需要在 Windows 环境下编译（CI 使用 `windows-latest` / `windows-11-arm` runner）
- 仅提供 NSIS 安装程序（`oneClick: false`，允许自定义安装目录），无便携版
- arm64 构建需要 ARM64 C++ 工具链

### Linux

- CI 使用 `ubuntu-22.04`（x64）与 `ubuntu-22.04-arm`（arm64）
- 产物包含 AppImage、deb、pacman（`.pkg.tar.zst`）、rpm、tar.gz 五种格式
- AppImage 兼容性最好，deb/rpm/pacman 适合对应发行版的包管理
