# EchoMusic 文档仓库结构说明

本仓库是 EchoMusic（酷狗第三方客户端）的文档站，基于 **VitePress** 构建（`srcDir: 'docs'`，包管理器 pnpm@10.30.3）。所有正文内容位于 `docs/` 下，支持中文/English 双语。

## 常用命令

| 命令 | 说明 |
|------|------|
| `pnpm docs:dev` | 本地开发服务器 |
| `pnpm docs:build` | 构建生产版本 |
| `pnpm docs:preview` | 预览构建结果 |

## 根目录文件
| 文件 | 说明 |
|------|------|
| `README.md` | 项目说明：文档仓库用途、本地开发方法和贡献指南 |
| `package.json` | Node.js 项目配置（VitePress + Mermaid + Tabs 等插件） |
| `pnpm-lock.yaml` | pnpm 依赖锁定文件 |
| `LICENSE` | 开源许可证文件 |

## 文件夹结构详述

### `.vitepress/` — VitePress 站点配置（位于仓库根，不在 docs/ 内）
| 文件/文件夹 | 说明 |
|-------------|------|
| `config.mts` | VitePress 核心配置：中文（root）+ English 双语 nav/sidebar、本地搜索、mermaid / tabs / 链接预览插件 |
| `theme/index.ts` | 主题入口：扩展默认主题，注册 Tabs、链接预览、阅读增强和 DownloadButton 组件 |
| `theme/style.css` | 自定义样式 |
| `components/DownloadButton.vue` | 下载按钮组件：从 GitHub Releases 获取正式版/预发布版 |
| `components/DownloadCore.vue` | 下载按钮核心实现（含镜像测速、按系统/架构匹配安装包） |
| `components/PluginMarketplace.vue` | 插件市场卡片页组件：软件内市场风格的卡片网格（图标/版本/标签/三数据/分享·仓库·安装），仅官方源插件，与 `usePluginCatalog.js` 共用 |
| `components/usePluginCatalog.js` | 插件目录共享逻辑：目录数据、搜索/分类/排序状态、热度加载（缓存+超时+重试），供 PluginMarketplace 使用 |
| `data/plugins.json` | 🤖 自动生成的插件目录数据（官方源插件，含 sourceId/version/icon/iconExt/tags），勿手改 |

> `.vitepress/cache/` 与 `docs/.vitepress/dist/` 为构建产物（已 gitignore），不要提交或手改。

### `docs/index.md` — 首页
VitePress Hero 首页：产品简介、功能特性、快速入口和社区信息。内嵌 canvas 星星粒子特效，并随机替换头图（含低概率出现的隐藏款 `114514.png`）。

### `docs/guide/` — 用户使用指南（简体中文）
| 文件 | 说明 |
|------|------|
| `index.md` | 使用指南总览 |
| `getting-started.md` | 下载安装与快速开始 |
| `playback.md` | 播放控制与队列管理 |
| `music-discovery.md` | 音乐发现与推荐 |
| `search.md` | 搜索功能 |
| `personal-fm.md` | 私人 FM |
| `music-recognition.md` | 听歌识曲 |
| `lyrics.md` | 歌词系统 |
| `audio.md` | 音频增强设置 |
| `song-detail.md` | 歌曲详情与评论 |
| `settings.md` | 偏好设置 |

#### `docs/guide/plugins/` — 插件系统
| 文件 | 说明 |
|------|------|
| `index.md` | 插件系统概览 |
| `install.md` | 安装插件 |
| `community.md` | 社区插件源（🤖 自动生成，勿手改） |
| `manage.md` | 插件管理与安全 |

> 插件列表页（`list.md`，表格版）已移除——插件浏览统一由顶部导航"插件市场"页（`docs/plugins/`，PluginMarketplace 卡片组件）承担；`docs/public/guide/plugins/list/` 保留旧链接重定向。

### `docs/faq/` — 常见问题（简体中文）
| 文件 | 说明 |
|------|------|
| `index.md` | 常见问题总览 |
| `install.md` | 安装与启动 |
| `playback.md` | 播放与音质 |
| `account.md` | 账号与会员 |
| `features.md` | 功能使用 |
| `updates.md` | 更新与反馈 |
| `platform.md` | 平台限制 |

### `docs/develop/` — 开发文档（简体中文）
| 文件 | 说明 |
|------|------|
| `index.md` | 开发指南总览 |
| `architecture.md` | 架构设计 |
| `project-structure.md` | 项目结构 |
| `local-dev.md` | 本地开发环境搭建 |
| `native-addons.md` | Rust NAPI 原生模块 |
| `build.md` | 编译与构建 |
| `contributing.md` | 贡献指南 |
| `kugou-api.md` | 酷狗 API 参考（原 `api.md`） |

#### `docs/develop/internal-api/` — 内部 API 参考
| 文件 | 说明 |
|------|------|
| `index.md` | 内部 API 概览 |
| `audio-engine.md` | 音频引擎 |
| `playback-state.md` | 播放状态与持久化 |
| `window-management.md` | 窗口与交互管理 |
| `system-features.md` | 系统功能集成 |

#### `docs/develop/plugin-dev/` — 插件开发
| 文件 | 说明 |
|------|------|
| `index.md` | 插件开发概览 |
| `getting-started.md` | 快速开始 |
| `manifest.md` | Manifest 配置 |
| `context-api.md` | 插件 API 总览 |
| `ui-extension.md` | UI 扩展 |
| `player-audio.md` | 播放器与音频引擎 |
| `audio-spectrum.md` | 音频频谱 |
| `filesystem-storage.md` | 文件存储与数据 |
| `windows-system.md` | 窗口与系统 |
| `publishing.md` | 发布与分发 |
| `marketplace-stats.md` | 插件热度与统计：上报链路、热度口径（score 公式）、公开查询接口 |
| `network.md` | 网络与下载：主进程请求 / TCP 客户端 / 断点续传下载引擎 |
| `graphics.md` | Graphics 绘图：WebGPU/HDR 画布与 Canvas2D 回退 |
| `server-intercept.md` | 服务请求拦截：拦截器链、Mock/转发、fail-open 语义 |
| `tasks.md` | 任务面板：会话式任务注册、保留策略、操作按钮 |
| `backups.md` | 备份与恢复：命令式 API 与存储提供方 |
| `lyrics-page.md` | 歌词页换肤：自定义歌词页注册与皮肤配置 |

### `docs/plugins/` — 插件市场（卡片视图，从顶部导航"插件市场"进入）
| 文件 | 说明 |
|------|------|
| `index.md` | 插件市场卡片页：`aside: false` 整页无侧栏，内容为 PluginMarketplace 卡片组件（对齐软件内市场布局） |

### `docs/changelog/index.md` — 更新日志（🤖 自动同步，勿手改）
由脚本从上游 `CHANGELOG.md` 增量同步。

### `docs/en/` — 英文版文档
与中文版完全镜像：`guide/`（含 `plugins/`）、`faq/`、`develop/`（含 `internal-api/`、`plugin-dev/`）、`plugins/`、`changelog/`。

> ⚠️ **注意**：en/ 英文文档是通过翻译中文内容得来，应最大程度与中文内容保持同步。修改中文页面后需同步更新对应的英文页面。

### `docs/public/` — 静态资源
| 文件/文件夹 | 说明 |
|-------------|------|
| `title_img/` | 首页标题图片（含隐藏款 `114514.png`） |
| `favicon.svg`、`icon.ico` | 站点图标 |
| `plugin-icons/` | 🤖 官方插件图标本地镜像（`<插件id>.<ext>`，由同步脚本下载生成，勿手改；插件市场卡片优先本地加载，避免 raw.githubusercontent/jsDelivr 国内不稳定导致裂图） |
| `community/index.html`、`en/community/index.html` | 静态跳转页（meta-refresh）：社区板块已删除，旧路由重定向到首页 |
| `features/index.html`、`en/features/index.html` | 静态跳转页：功能介绍板块已删除，旧路由重定向到首页 |
| `develop/api/index.html`、`en/develop/api/index.html` | 静态跳转页：旧 `api.md` 已改名 `kugou-api.md`，重定向到新地址 |

> `features/`、`community/` 等内容板块已从文档中移除，仅保留上述静态跳转页兜底旧链接，不要为它们重建目录。

## 自动化

### `scripts/sync-upstream.py` — 上游自动同步脚本
从上游仓库拉取数据并更新文档（支持 `--dry-run`、`--icons-only` 仅刷新图标镜像）：
- 拉取 `echo-plugins.json`，生成社区插件源页（中英文，即 `docs/guide/plugins/community.md` 及其英文对应文件）与插件目录数据 `.vitepress/data/plugins.json`（供插件市场卡片页使用；插件列表页已由插件市场页替代）；
- 下载官方插件图标到 `docs/public/plugin-icons/` 本地镜像（版本未变时跳过下载，自动清理孤儿文件），并在 plugins.json 记录 `iconExt` 字段；
- 拉取 `CHANGELOG.md`，增量追加到更新日志页（中英文）；
- 英文内容用 `deep_translator` 自动翻译；
- 内含 `CURATED` 人工翻译元数据表，用于覆盖自动翻译的插件名称/描述。

### `.github/workflows/`
| 文件 | 说明 |
|------|------|
| `deploy.yml` | push 到 main 后自动构建并部署到 GitHub Pages |
| `auto-sync.yml` | 每小时运行一次同步脚本，检测到变更后自动开 PR |

## 自动生成文件一览（勿手改）
| 文件 | 生成方式 |
|------|----------|
| `.vitepress/data/plugins.json` | 同上（官方源插件目录数据，含 sourceId/version/icon/iconExt/tags，供插件市场卡片页构建时读取与热度查询） |
| `docs/guide/plugins/community.md` 及 `docs/en/guide/plugins/community.md` | 同上（社区插件源页） |
| `docs/changelog/index.md` 及 `docs/en/changelog/index.md` | 同上（从上游 `CHANGELOG.md` 增量同步） |
