---
title: 使用指南
---

# 📖 使用指南

欢迎使用 EchoMusic！本指南将帮助你快速上手，全面掌握 EchoMusic 的各项功能。

## ✨ 功能一览

<div class="feature-cards">

<div class="feature-card">

### 🎵 进阶播放能力

播放队列管理、列表/单曲/随机模式、音量调节、进度拖动、倍速播放（0.5x–2.0x）、淡入淡出切歌。

[了解更多 →](/guide/playback)

</div>

<div class="feature-card">

### 📝 歌词系统

LRC/YRC 逐字歌词解析，精准滚动同步，全屏歌词与桌面歌词悬浮窗。

[了解更多 →](/guide/lyrics)

</div>

<div class="feature-card">

### 🎚️ 音频增强

10 段 EQ 均衡器、基于 LUFS 的音量均衡、蝰蛇母带/全景声/超清等音效，Hi-Res/SQ/HQ/标准多档音质。

[了解更多 →](/guide/audio)

</div>

<div class="feature-card">

### 🎧 私人 FM

智能推荐个性化电台，根据你的听歌偏好持续优化推荐。

[了解更多 →](/guide/personal-fm)

</div>

<div class="feature-card">

### 🎤 听歌识曲

麦克风和系统音频捕获，快速识别正在播放的歌曲。

[了解更多 →](/guide/music-recognition)

</div>

<div class="feature-card">

### 🔍 多维搜索

歌曲、歌手、专辑、歌单全方位搜索，快速定位目标内容。

[了解更多 →](/guide/search)

</div>

<div class="feature-card">

### 💬 歌曲详情与评论

查看歌曲档案与播放详情，浏览乐评，支持评论楼层跳转。

[了解更多 →](/guide/song-detail)

</div>

<div class="feature-card">

### 🧩 插件系统

类 VS Code 的高自由度扩展，46 款社区插件覆盖美化/歌词/音频/效率。

[了解更多 →](/guide/plugins/)

</div>

<div class="feature-card">

### 🌐 空间音效

导入 IR 脉冲响应文件，实时渲染空间音效，模拟不同声学环境。

[了解更多 →](/guide/audio#空间音效)

</div>

<div class="feature-card">

### 🖥️ 跨平台与系统集成

完整适配 macOS/Windows/Linux，托盘、全局快捷键、系统媒体控制。

[了解更多 →](/guide/settings)

</div>

</div>

<style>
.feature-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
  margin: 16px 0 24px;
}
.feature-card {
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  padding: 16px 20px;
  transition: border-color 0.25s, box-shadow 0.25s;
}
.feature-card:hover {
  border-color: var(--vp-c-brand);
  box-shadow: 0 2px 12px var(--vp-c-brand-soft);
}
.feature-card h3 {
  margin-top: 0;
  font-size: 1.05em;
}
.feature-card a {
  font-size: 0.9em;
}
</style>

## 🚀 快速导航

### 新手入门

如果你是第一次使用 EchoMusic，建议按以下顺序阅读：

- [快速开始](/guide/getting-started) — 下载、安装与登录
- [播放控制](/guide/playback) — 掌握基本播放操作
- [发现音乐](/guide/music-discovery) — 浏览推荐内容与排行榜
- [搜索](/guide/search) — 快速找到你想要的音乐

### 进阶使用

熟悉基础功能后，可以深入了解这些高级特性：

- [歌词系统](/guide/lyrics) — LRC/YRC 歌词、全屏歌词、桌面歌词
- [音频设置](/guide/audio) — EQ 均衡器、音效模式、音质选择
- [私人 FM](/guide/personal-fm) — 个性化电台推荐
- [听歌识曲](/guide/music-recognition) — 识别正在播放的歌曲
- [歌曲详情与评论](/guide/song-detail) — 查看歌曲档案与乐评
- [播放历史](/guide/settings#数据管理) — 查看和管理听歌记录
- [插件系统](/guide/plugins/) — 扩展功能、安装与管理插件

### 个性化配置

- [个性化设置](/guide/settings) — 外观主题、快捷键、系统托盘

### 遇到问题？

- [常见问题](/faq/) — 常见问题解答

## 文档结构

```:no-line-numbers
guide/
├── getting-started.md        ← 下载、安装、首次启动
├── playback.md                ← 播放控制与队列管理
├── music-discovery.md         ← 发现音乐、排行榜、推荐
├── search.md                  ← 搜索歌曲/歌手/专辑/歌单
├── lyrics.md                  ← 歌词显示与设置
├── audio.md                   ← EQ、音效、音质
├── personal-fm.md             ← 私人 FM 电台
├── music-recognition.md       ← 听歌识曲
├── song-detail.md             ← 歌曲详情与评论
├── settings.md                ← 个性化设置
├── plugins/                   ← 插件系统（4 个子页面）
└── faq.md                     ← 常见问题解答
```
