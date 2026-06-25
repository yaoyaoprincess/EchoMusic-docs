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
- Electron 主进程自动启动
- Vue DevTools 自动启用
- 原生模块在首次启动时编译

## 生产构建

````bash
# 编译前端 + 打包 Electron 应用
pnpm build
````

构建流程：

1. **前端编译**：Vite 将 Vue 组件编译为静态资源
2. **TypeScript 编译**：编译主进程和后端 TypeScript 代码
3. **Rust 编译**：编译所有原生模块（release 模式）
4. **Electron Builder 打包**：打包为各平台安装包
5. **打包后处理**：执行 `build/afterPack.js` 脚本

### 打包后处理 (afterPack.js)

`build/afterPack.js` 在 Electron Builder 打包完成后执行，负责：

- 清理不需要的构建产物
- 调整平台特定的文件结构
- 处理符号链接和权限

## 打包产物

构建完成后，`release/` 目录下会生成各平台安装包：

| 平台 | 格式 | 文件 |
|------|------|------|
| **macOS** | DMG 安装包 | `EchoMusic-{version}.dmg` |
| **macOS** | ZIP 包 | `EchoMusic-{version}-mac.zip` |
| **Windows** | NSIS 安装程序 | `EchoMusic-Setup-{version}.exe` |
| **Windows** | 便携版 | `EchoMusic-{version}-portable.exe` |
| **Linux** | deb 包 | `EchoMusic_{version}_amd64.deb` |
| **Linux** | rpm 包 | `EchoMusic-{version}.x86_64.rpm` |
| **Linux** | AppImage | `EchoMusic-{version}.AppImage` |
| **Linux** | tar.gz | `EchoMusic-{version}.tar.gz` |

## 构建配置

Electron Builder 配置文件：`electron-builder.yml`

关键配置：

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

## CI/CD 自动构建

EchoMusic 使用 GitHub Actions 进行持续集成与发布，配置文件位于 `.github/workflows/` 目录下。

### 工作流概览

| 工作流 | 文件 | 说明 |
|--------|------|------|
| 构建发布 | `build.yml` (21KB) | 多平台自动构建与 GitHub Release 发布 |
| AI 标签 | `issue-ai-labeler.yml` | 使用 AI 自动为 Issue 添加分类标签 |
| 自动关闭 | `issue-closer.yml` | 自动关闭长时间无活动的 Issue |

### 构建发布工作流

当推送 `v*` 格式的 Tag 时（如 `v1.0.0`），自动触发多平台构建。

**构建矩阵**：

| 平台 | Runner | 产物 |
|------|--------|------|
| macOS x64 | `macos-13` | dmg + zip |
| macOS arm64 | `macos-latest` | dmg + zip |
| Windows x64 | `windows-latest` | NSIS installer + portable |
| Linux x64 | `ubuntu-latest` | deb + rpm + AppImage + tar.gz |

**CI 构建流程**：

1. 检出代码（含 submodules）
2. 安装 pnpm + Node.js 20
3. 安装项目依赖（`pnpm install`）
4. 编译 Rust 原生模块（各平台交叉编译）
5. 编译前端资源（`pnpm build`）
6. Electron Builder 打包
7. 上传构建产物到 GitHub Releases
8. 生成 Release Notes

### Issue 管理自动化

**AI 标签器 (issue-ai-labeler.yml)**：

- 触发条件：新建 Issue 时
- 功能：使用 AI 分析 Issue 内容，自动添加分类标签
- 标签类型：bug、enhancement、documentation 等

**自动关闭 (issue-closer.yml)**：

- 触发条件：定时执行
- 功能：自动关闭长时间无活动且未标记 `bug` 或 `enhancement` 标签的 Issue
- 关闭前会添加 `stale` 标签并留言提醒

## 发布新版本

1. 确保所有改动已提交并测试通过
2. 更新 `package.json` 中的版本号
3. 更新 `CHANGELOG.md` 记录本次变更
4. 创建 Git Tag：

````bash
git tag v1.0.0
git push origin v1.0.0
````

5. GitHub Actions 自动构建并发布到 Releases

## 自动更新

EchoMusic 内置应用更新检测功能（`electron/updater.ts`）：

- 启动时检查 GitHub Releases 是否有新版本
- 支持静默下载更新包
- 下载完成后提示用户安装
- 跨平台支持（macOS/Windows/Linux）

## 平台特定注意事项

### macOS

- 需在 macOS 环境下编译，交叉编译受限
- 需要 Apple Developer 证书进行代码签名（可选）
- 如未签名，用户需手动绕过 Gatekeeper
- 分 x64 和 arm64 两个构建目标

### Windows

- 需要在 Windows 环境下编译
- 建议使用 NSIS 安装程序（用户体验更好）
- 便携版适合放在 U 盘中随身使用

### Linux

- 可在 Ubuntu 环境下编译
- AppImage 兼容性最好，推荐优先使用
- deb/rpm 适合对应发行版的包管理
