---
title: 项目结构
---

# 📁 项目结构

本文详细介绍 EchoMusic 项目的目录结构和各模块职责。

## 目录树

```
EchoMusic/
├── .claude/                    # Claude Code 配置
│   └── settings.json           # Claude Code 项目设置
├── .github/                    # GitHub CI/CD 与社区配置
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md       # Bug 报告模板
│   │   └── feature_request.md  # 功能请求模板
│   └── workflows/
│       ├── build.yml           # 多平台构建与发布
│       ├── issue-ai-labeler.yml # AI 自动分类 Issue
│       └── issue-closer.yml    # 自动关闭过期 Issue
├── .vscode/
│   └── extensions.json         # 推荐 VS Code 扩展
├── build/                      # 构建配置与资源
│   ├── icons/                  # 应用图标
│   └── afterPack.js            # Electron Builder 打包后处理
├── electron/                   # Electron 主进程代码
│   ├── main.ts                 # 主进程入口
│   ├── preload.ts              # 预加载脚本
│   └── updater.ts              # 自动更新逻辑
├── native/                     # Rust 原生模块（napi-rs）
│   ├── echo-mpv-player/        # libmpv 播放引擎封装
│   │   ├── src/
│   │   │   ├── lib.rs          # 模块入口
│   │   │   ├── player.rs       # 播放器核心逻辑
│   │   │   ├── eq.rs           # EQ 均衡器
│   │   │   └── fade.rs         # 淡入淡出控制
│   │   └── Cargo.toml
│   ├── echo-media-controls/    # 系统媒体控制
│   │   ├── src/
│   │   │   ├── lib.rs
│   │   │   ├── macos.rs        # macOS 实现
│   │   │   ├── windows.rs      # Windows 实现
│   │   │   └── linux.rs        # Linux 实现
│   │   └── Cargo.toml
│   └── echo-storage/           # SQLite 本地存储
│       ├── src/
│       │   ├── lib.rs
│       │   ├── db.rs           # 数据库操作
│       │   ├── models.rs       # 数据模型
│       │   └── migrations.rs   # 数据库迁移
│       └── Cargo.toml
├── server/                     # Node.js 后端服务
│   ├── index.ts                # 服务入口
│   ├── routes/                 # API 路由
│   │   ├── song.ts             # 歌曲相关接口
│   │   ├── search.ts           # 搜索接口
│   │   ├── playlist.ts         # 歌单接口
│   │   ├── artist.ts           # 歌手接口
│   │   ├── album.ts            # 专辑接口
│   │   ├── lyric.ts            # 歌词接口
│   │   └── user.ts             # 用户相关接口
│   ├── services/               # 业务逻辑层
│   │   ├── kugou.ts            # 酷狗 API 调用封装
│   │   └── cache.ts            # 缓存逻辑
│   └── package.json
├── src/                        # Vue 3 前端代码
│   ├── App.vue                 # 根组件
│   ├── main.ts                 # 前端入口
│   ├── router/                 # 路由配置
│   │   └── index.ts
│   ├── stores/                 # Pinia 状态管理
│   │   ├── player.ts           # 播放器状态
│   │   ├── user.ts             # 用户状态
│   │   ├── settings.ts         # 设置状态
│   │   └── search.ts           # 搜索状态
│   ├── views/                  # 页面组件
│   │   ├── HomeView.vue        # 首页
│   │   ├── DiscoverView.vue    # 发现页
│   │   ├── SearchView.vue      # 搜索页
│   │   ├── FMView.vue          # 私人 FM
│   │   ├── RecognizeView.vue   # 听歌识曲
│   │   ├── SongDetailView.vue  # 歌曲详情
│   │   ├── PlaylistView.vue    # 歌单详情
│   │   ├── ArtistView.vue      # 歌手详情
│   │   ├── AlbumView.vue       # 专辑详情
│   │   ├── SettingsView.vue    # 设置页
│   │   └── ProfileView.vue     # 个人中心
│   ├── components/             # 通用组件
│   │   ├── PlayerBar.vue       # 底部播放栏
│   │   ├── PlayQueue.vue       # 播放队列
│   │   ├── LyricPanel.vue      # 歌词面板
│   │   ├── LyricDesktop.vue    # 桌面歌词
│   │   ├── EqPanel.vue         # EQ 面板
│   │   ├── SongCard.vue        # 歌曲卡片
│   │   ├── SearchInput.vue     # 搜索输入框
│   │   └── ...
│   ├── composables/            # 组合式函数
│   │   ├── usePlayer.ts        # 播放器逻辑
│   │   ├── useAudio.ts         # 音频设备
│   │   ├── useLyric.ts         # 歌词处理
│   │   ├── useSearch.ts        # 搜索逻辑
│   │   └── useTheme.ts         # 主题切换
│   ├── api/                    # API 请求封装
│   │   ├── index.ts            # Axios 实例
│   │   ├── song.ts
│   │   ├── search.ts
│   │   └── ...
│   ├── utils/                  # 工具函数
│   ├── types/                  # TypeScript 类型定义
│   └── assets/                 # 静态资源
├── resources/                  # 应用资源文件
├── .eslintrc.json              # ESLint 代码检查配置
├── .prettierrc                 # Prettier 代码格式化配置
├── .prettierignore             # Prettier 忽略规则
├── .npmrc                      # npm/pnpm 配置
├── .gitmodules                 # Git 子模块配置
├── CHANGELOG.md                # 版本更新日志
├── package.json                # 项目配置
├── pnpm-lock.yaml              # 依赖锁定
├── vite.config.ts              # Vite 配置
├── electron-builder.yml        # Electron Builder 配置
├── tsconfig.json               # TypeScript 配置
├── tailwind.config.ts          # Tailwind CSS 配置
├── LICENSE                     # MIT 许可证
└── README.md                   # 项目 README
```

## 关键文件说明

### 入口文件

| 文件 | 说明 |
|------|------|
| `electron/main.ts` | Electron 主进程入口，创建窗口、初始化服务、管理开机自启 |
| `src/main.ts` | Vue 3 应用入口，挂载根组件和插件 |

### 配置文件

| 文件 | 说明 |
|------|------|
| `vite.config.ts` | Vite 构建配置，含 Electron 插件 |
| `electron-builder.yml` | 多平台打包配置 |
| `tailwind.config.ts` | Tailwind CSS 主题定制 |
| `tsconfig.json` | TypeScript 编译选项 |
| `.eslintrc.json` | ESLint 代码风格检查规则 |
| `.prettierrc` | Prettier 代码格式化配置 |
| `.npmrc` | npm/pnpm 镜像与配置 |

### 开发者工具配置

| 文件/目录 | 说明 |
|-----------|------|
| `.claude/` | Claude Code 项目级别配置（AI 辅助开发） |
| `.vscode/extensions.json` | 推荐的 VS Code 扩展列表 |

### GitHub 工作流

| 文件 | 说明 |
|------|------|
| `.github/workflows/build.yml` | 多平台自动构建与 Release 发布（macOS/Windows/Linux） |
| `.github/workflows/issue-ai-labeler.yml` | 使用 AI 自动为 Issue 添加分类标签 |
| `.github/workflows/issue-closer.yml` | 自动关闭长时间无活动的 Issue |
| `.github/ISSUE_TEMPLATE/` | Issue 模板（Bug 报告 / 功能请求） |

### 构建相关

| 文件 | 说明 |
|------|------|
| `build/afterPack.js` | Electron Builder 打包后处理脚本 |

### Rust 原生模块

每个原生模块都是独立的 Rust crate，通过 napi-rs 编译为 `.node` 文件，在 Electron 主进程中直接加载调用。
