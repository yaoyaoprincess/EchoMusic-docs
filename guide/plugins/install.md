---
title: 安装插件
---

# 📥 安装插件

## 在线插件源（推荐）

EchoMusic 内置了在线插件源，可以直接浏览和安装：

1. 打开 EchoMusic，进入「**插件管理**」
2. 点击「**在线插件**」标签页
3. 浏览可用插件列表
4. 点击「**安装**」按钮，插件会自动下载并安装

## 一键更新

v2.2.7 新增了**一键更新插件**功能。当已安装的插件有新版本时，插件管理页会提示更新，点击即可一键升级到最新版本。

## 添加第三方插件源

你可以添加其他 GitHub 仓库作为插件源：

1. 在「插件管理」→「在线插件」中点击「**添加源**」
2. 输入插件源地址，例如：
   ```
   https://github.com/username/echo-plugins-source
   ```
3. 刷新后即可看到该源提供的插件

## 手动安装

1. 在「插件管理」中点击「**打开目录**」
2. 将下载的插件文件夹（包含 `manifest.json`）复制进去
3. 返回 EchoMusic，插件会自动出现在列表中

```
<EchoMusic 插件目录>/
  hello-echo/
    manifest.json
    index.js
    style.css
```

## 💡 插件目录在哪里

- **Windows**: `%APPDATA%/echomusic/plugins/`
- **macOS**: `~/Library/Application Support/echomusic/plugins/`
- **Linux**: `~/.config/echomusic/plugins/`

也可以通过「插件管理」→「打开目录」一键跳转。

---

- [← 插件系统概览](./)
- [📋 插件列表 →](./list)
