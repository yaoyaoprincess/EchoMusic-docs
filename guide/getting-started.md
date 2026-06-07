---
title: 快速开始
---

# 🚀 快速开始

本指南将帮助你下载、安装并启动 EchoMusic。

## 下载安装包

访问 [GitHub Releases](https://github.com/hoowhoami/EchoMusic/releases) 页面，下载对应平台的安装包：

| 平台 | 安装包格式 |
|------|-----------|
| **macOS** | `.dmg`（推荐）、`.zip` |
| **Windows** | `.exe` 安装程序（推荐） |
| **Linux** | `.deb`、`.rpm`、`.AppImage`（推荐）、`.tar.gz` |

如果你不确定你应该下载哪个格式的安装包，可以使用点击下面的按钮下载！
::: info 建议
推荐使用预发布版本，更新频率较快，能使用新功能以及更快的修复bug
:::

<DownloadButton version="both" type="card" :show-version="true" />

### macOS 安装

1. 下载 `.dmg` 文件
2. 双击打开，将 `EchoMusic.app` 拖入 `Applications` 文件夹
3. 首次打开时，如果提示"无法验证开发者"，请执行：
   ```bash
   xattr -cr /Applications/EchoMusic.app
   ```
   或在 **系统设置 → 隐私与安全性** 中点击「仍要打开」

### Windows 安装

1. 下载 `.exe` 安装程序
2. 双击运行，按照向导完成安装
3. 安装完成后，桌面和开始菜单会创建快捷方式


### Linux 安装

**AppImage（推荐）**：

```bash
chmod +x EchoMusic-*.AppImage
./EchoMusic-*.AppImage
```

**deb 包**：

```bash
sudo dpkg -i EchoMusic-*.deb
```

**rpm 包**：

```bash
sudo rpm -i EchoMusic-*.rpm
```

## 首次启动

1. 启动 EchoMusic 应用
2. 首次启动会进入登录页面，使用你的酷狗账号登录
3. 登录成功后，即可开始探索音乐世界

::: tip 提示
EchoMusic 的数据直连酷狗官方服务器，不会经过任何第三方。你的账号信息安全有保障。
:::

## 系统要求

| 组件 | 最低要求 |
|------|----------|
| 操作系统 | macOS 11+ / Windows 10+ / Linux (主流发行版) |
| 内存 | 4GB RAM |
| 存储 | 200MB 可用空间 |
| 网络 | 需要网络连接（在线播放） |

## 下一步

- [播放控制](/guide/playback) — 学习基本的播放操作
- [发现音乐](/guide/music-discovery) — 探索推荐与排行榜
- [常见问题](/guide/faq) — 遇到问题来这里找答案