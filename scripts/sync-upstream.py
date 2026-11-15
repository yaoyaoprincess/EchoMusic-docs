#!/usr/bin/env python3
"""
EchoMusic Docs Auto-Sync Script
同步上游插件列表 (echo-plugins.json) 和更新日志 (CHANGELOG.md)。
检测变更后更新对应文档页面。

Usage: python scripts/sync-upstream.py [--dry-run] [--icons-only] [--rebuild-only]
"""

import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from collections import OrderedDict
from datetime import datetime

# ── 配置 ──────────────────────────────────────────────

DOCS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGINS_JSON_URL = 'https://raw.githubusercontent.com/hoowhoami/EchoMusicPlugins/main/echo-plugins.json'
CHANGELOG_URL = 'https://raw.githubusercontent.com/hoowhoami/EchoMusic/main/CHANGELOG.md'
PLUGINS_REPO_RAW = 'https://raw.githubusercontent.com/hoowhoami/EchoMusicPlugins/main'
PLUGINS_REPO = 'https://github.com/hoowhoami/EchoMusicPlugins'
# ── 社区插件源配置 ──────────────────────────────────
# 每个源: { 'name', 'en_name', 'homepage', 'json_url', 'raw_base', 'curated': {...}, 'featured': bool }
COMMUNITY_SOURCES = [
    {
        'name': 'ZHCOOL520 猎奇插件源',
        'en_name': 'ZHCOOL520 Plugin Source',
        'homepage': 'https://github.com/ZHCOOL520/EchoMusicPluginst',
        'json_url': 'https://raw.githubusercontent.com/ZHCOOL520/EchoMusicPluginst/master/echo-plugins.json',
        'raw_base': 'https://raw.githubusercontent.com/ZHCOOL520/EchoMusicPluginst/master',
        'featured': False,
        'curated': {
            'echo-ad-system': {
                'zh_name': '广告系统',
                'en_name': 'Ad System',
                'zh_desc': '开屏广告 + 播放中插播广告 + 启动音效，支持 Bing 每日壁纸、自定义图片与弹窗时间',
                'en_desc': 'Splash screen ads + in-app advertising + startup sound, with Bing daily wallpaper, custom images, and popup timer',
                'author': 'ZHCOOL520',
            },
            'genshin-launcher': {
                'zh_name': '原神启动器',
                'en_name': 'Genshin Launcher',
                'zh_desc': '游戏启动器、云游戏集成',
                'en_desc': 'Game launcher and cloud gaming integration',
                'author': 'ZHCOOL520',
            },
            'echomusic-stress-test': {
                'zh_name': '究极双挖',
                'en_name': 'Stress Test',
                'zh_desc': '系统压力测试工具',
                'en_desc': 'System stress testing tool',
                'author': 'ZHCOOL520',
            },
            'prank-system': {
                'zh_name': '恶搞系统',
                'en_name': 'Prank System',
                'zh_desc': '关机、蓝屏、冻结窗口等恶搞功能',
                'en_desc': 'Shutdown, blue screen, window freeze, and other prank features',
                'author': 'ZHCOOL520',
            },
            'music-downloader': {
                'zh_name': '音乐下载',
                'en_name': 'Music Downloader',
                'zh_desc': '酷狗概念版音乐搜索与下载：多选批量下载，快捷下载按钮，内联音质选择，自定义链接，融合原生下载引擎',
                'en_desc': 'Kugou Concept Edition music search and download: batch multi-select, quick download button, inline quality selection, custom links, integrated with native download engine',
                'author': 'ZHCOOL520',
            },
            'avatar-nickname-self-comfort': {
                'zh_name': '头像昵称自慰',
                'en_name': 'Avatar & Nickname Self-Comfort',
                'zh_desc': '本地修改头像和昵称显示',
                'en_desc': 'Locally modify avatar and nickname display',
                'author': 'ZHCOOL520',
            },
        },
    },
]

DRY_RUN = '--dry-run' in sys.argv
ICONS_ONLY = '--icons-only' in sys.argv
REBUILD_ONLY = '--rebuild-only' in sys.argv

# ── 分类定义 ──────────────────────────────────────────

CATEGORIES = [
    ('🎨 界面美化', 'UI & Themes'),
    ('🎵 歌词与播放', 'Lyrics & Playback'),
    ('🔊 音频增强', 'Audio Enhancement'),
    ('☁️ 音源与存储', 'Audio Sources & Storage'),
    ('🛠️ 效率工具', 'Productivity Tools'),
    ('📚 开发示例', 'Development Examples'),
]

# 标签 → 分类索引 (用于自动归类新插件)
TAG_TO_CAT = {
    'appearance': 0, 'theme': 0, 'beautify': 0, 'miuix': 0,
    'liquidglass': 0, 'icons': 0, 'splash-screen': 0,

    'lyrics': 1, 'lyric-effects': 1, 'floating-window': 1,
    'player-bar': 1, 'now-playing': 1, 'mini-player': 1,
    'winisland': 1, 'server': 1, 'cover': 1, 'animation': 1,

    'audio': 2, 'spectrum': 2,

    'audio-source': 3, 'webdav': 3, 'cloud-music': 3, 'local': 3,

    'productivity': 4, 'navigation': 4, 'scroll': 4,
    'page-transition': 4, 'plugin-panel': 4,

    'demo': 5, 'example': 5,
}

# ── 已知插件元数据（人工维护层）─────────────────────────
# 键 = echo-plugins.json 中的 id
# 作者：echo-plugins.json 中有 author 字段的直接取；否则从 manifest.json 获取

CURATED = {
    'example-plugin': {
        'zh_name': '示例插件',
        'en_name': 'Example Plugin',
        'zh_desc': '官方示例插件，展示歌词动效、浮窗、Now Playing 等完整功能',
        'en_desc': 'Official example plugin demonstrating lyric effects, floating windows, Now Playing, and more',
        'author': 'hoowhoami',
        'category': 5,
    },
    'water-lyrics': {
        'zh_name': '水波歌词',
        'en_name': 'Water Lyrics',
        'zh_desc': '页面歌词水波动效，演示 ctx.lyricEffects.register() 的接入方式',
        'en_desc': 'Water ripple effect on lyrics page, demonstrates ctx.lyricEffects.register()',
        'author': 'hoowhoami',
        'category': 1,
    },
    'page-motion': {
        'zh_name': '页面转场动效',
        'en_name': 'Page Motion',
        'zh_desc': '页面转场动画效果',
        'en_desc': 'Page transition animation effects',
        'author': 'hoowhoami',
        'category': 4,
    },
    'scroll-assistant': {
        'zh_name': '滚动辅助',
        'en_name': 'Scroll Assistant',
        'zh_desc': '滚动辅助工具，提升长列表浏览体验',
        'en_desc': 'Scroll assist tool for better long-list browsing',
        'author': 'hoowhoami',
        'category': 4,
    },
    'cover-fallback': {
        'zh_name': '封面回退',
        'en_name': 'Cover Fallback',
        'zh_desc': '为无封面歌曲提供默认封面替代方案，适配迷你播放器',
        'en_desc': 'Default cover fallback for songs without covers, mini player compatible',
        'author': 'hoowhoami',
        'category': 4,
    },
    'lyric-info-scroll': {
        'zh_name': '歌词信息滚动',
        'en_name': 'Lyric Info Scroll',
        'zh_desc': '在播放栏区域滚动显示歌词信息，同时适配迷你播放器',
        'en_desc': 'Scroll lyric information in the playback bar area, also adapts to mini player',
        'author': 'hoowhoami',
        'category': 1,
    },
    'spectrum-visualizer': {
        'zh_name': '频谱可视化',
        'en_name': 'Spectrum Visualizer',
        'zh_desc': '音频频谱可视化，支持播放栏、迷你播放器和歌词页面多场景展示',
        'en_desc': 'Audio spectrum visualization supporting playback bar, mini player, and lyrics page views',
        'author': 'hoowhoami',
        'category': 2,
    },
    'webdav-music': {
        'zh_name': 'WebDAV 音乐',
        'en_name': 'WebDAV Music',
        'zh_desc': '通过 WebDAV 协议播放云端存储的音乐文件，支持浏览、搜索和在线播放',
        'en_desc': 'Play music files stored on cloud storage via WebDAV protocol, with browsing, search, and online playback',
        'author': 'hoowhoami',
        'category': 3,
    },
    'echomusic-vinyl-rotation': {
        'zh_name': '黑胶唱片旋转',
        'en_name': 'Vinyl Rotation',
        'zh_desc': '黑胶唱片旋转动效，基于封面图片实时渲染',
        'en_desc': 'Vinyl record rotation effect with real-time cover image rendering',
        'author': 'hoowhoami',
        'category': 2,
    },
    # ── 以下插件在 echo-plugins.json 中有完整元数据 ──
    'echo-miuix-plugin': {
        'zh_name': 'Echo Miuix',
        'en_name': 'Echo Miuix',
        'zh_desc': '将 EchoMusic 界面改为 MIUIX（小米澎湃）风格',
        'en_desc': 'Transform EchoMusic UI to MIUIX (Xiaomi HyperOS) style',
        'json_author': '天影大侠',
        'category': 0,
    },
    'echo-liquid-glass': {
        'zh_name': 'Echo 液态折射',
        'en_name': 'Echo Liquid Glass',
        'zh_desc': '为底部音乐控件添加液态折射效果，可调整参数至 iOS 或鸿蒙风格。需配合 echo-miuix-plugin 使用',
        'en_desc': 'Add liquid refraction effect to the bottom music controls, adjustable from iOS to HarmonyOS style. Requires echo-miuix-plugin',
        'json_author': '天影大侠',
        'category': 0,
    },
    'echo_music-blue_archive-theme': {
        'zh_name': 'Blue Archive 主题包',
        'en_name': 'Blue Archive Theme',
        'zh_desc': '蔚蓝档案主题包，可自定义调整',
        'en_desc': 'Blue Archive theme pack with customizable adjustments',
        'json_author': 'venti1112',
        'category': 0,
    },
    'custom-icon': {
        'zh_name': '自定义图标',
        'en_name': 'Custom Icon',
        'zh_desc': '自定义托盘图标、窗口标题栏图标、任务栏图标、桌面快捷方式图标及启动画面',
        'en_desc': 'Customize tray icon, title bar icon, taskbar icon, desktop shortcut icon, and splash screen',
        'json_author': 'Oneday5799',
        'category': 0,
        'link_prefix': 'https://github.com/oneday5799/EchoMusicPlugins/tree/main/custom-icon',
    },
    'taskbar-lyric': {
        'zh_name': '任务栏歌词',
        'en_name': 'Taskbar Lyric',
        'zh_desc': '在任务栏上方显示当前歌词和专辑封面的透明浮窗，自动检测任务栏位置并贴靠',
        'en_desc': 'Display current lyrics and album cover in a transparent floating window above the taskbar, auto-detect taskbar position and snap to it',
        'json_author': 'yaoyaoprincess',
        'category': 1,
    },
    'plugin-panel': {
        'zh_name': '插件面板',
        'en_name': 'Plugin Panel',
        'zh_desc': '在侧边栏添加插件面板快捷入口，一键跳转到插件管理',
        'en_desc': 'Add a plugin panel shortcut in the sidebar, one-click jump to Plugin Manager',
        'json_author': 'yaoyaoprincess',
        'category': 4,
    },
    'cover-color-lyric': {
        'zh_name': '取色歌词',
        'en_name': 'Cover Color Lyric',
        'zh_desc': '桌面歌词颜色自动跟随歌曲封面主色调，支持深浅色归一化与频谱律动',
        'en_desc': 'Desktop lyrics color automatically follows the album cover dominant color, with lightness normalization and spectrum pulsing',
        'json_author': '小栀',
        'category': 1,
    },
    'echo-local-simple': {
        'zh_name': '简单本地音乐',
        'en_name': 'Echo Local Simple',
        'zh_desc': '简单实现的本地音乐播放',
        'en_desc': 'Simple local music file playback',
        'json_author': '天影大侠',
        'category': 3,
    },
    'Record-player': {
        'zh_name': '唱片播放器',
        'en_name': 'Record Player',
        'zh_desc': '仿酷狗唱片播放器，黑胶唱片风格播放界面',
        'en_desc': 'Kugou-style vinyl record player interface',
        'json_author': 'xiaotian2333',
        'category': 1,
    },
    'Lyrics-bridge': {
        'zh_name': 'Lyrics-bridge',
        'en_name': 'Lyrics-bridge',
        'zh_desc': '通过 WinIsland 实现外部歌词桥接服务',
        'en_desc': 'External lyrics bridging service via WinIsland',
        'author': 'xiaotian2333',
        'category': 1,
    },
    'xiaotoolkit': {
        'zh_name': '小功能',
        'en_name': 'XiaoToolkit',
        'zh_desc': '热门排序 + 单击播放 + 歌词沉浸 + 顶部插件按钮 + 桌面特效 + 搜索历史 + 多账号切换',
        'en_desc': 'Hot sort, single-click play, immersive lyrics, top plugin button, desktop effects, search history, multi-account switching',
        'json_author': 'Max8808',
        'category': 4,
        'link_prefix': 'https://github.com/Max8808/xiaotoolkit',
        # 仅文档收录（不在上游 JSON 中），分享链接需人工预置（version 取自其仓库 manifest）
        'share': 'https://hoowhoami.github.io/EchoMusic/share/?target=echomusic%3A%2F%2Fplugin%2Fxiaotoolkit%3FsourceId%3Dgithub%253Amax8808%252Fxiaotoolkit%26source%3Dhttps%253A%252F%252Fgithub.com%252FMax8808%252Fxiaotoolkit%26version%3D1.5.3%26homepage%3Dhttps%253A%252F%252Fgithub.com%252FMax8808%252Fxiaotoolkit',
    },
    'apple-music-lyrics': {
        'zh_name': 'Apple Music 歌词弹跳',
        'en_name': 'Apple Music Lyrics',
        'zh_desc': '模仿 Apple Music 的弹簧手感，为页面歌词行切换加入轻盈回弹动画',
        'en_desc': 'Mimics Apple Music spring physics for lightweight bounce animation when lyrics lines switch',
        'author': 'hoowhoami',
        'category': 1,
    },
    'channel-wander': {
        'zh_name': '频道漫游',
        'en_name': 'Channel Wander',
        'zh_desc': '频道漫游，无限发现音乐',
        'en_desc': 'Channel wander for endless music discovery',
        'json_author': 'xiaotian2333',
        'category': 3,
    },
    'player-frontend': {
        'zh_name': '3D 歌词',
        'en_name': '3D Lyrics',
        'zh_desc': '仿 Mineradio 歌词页',
        'en_desc': 'Mineradio-style lyrics page',
        'json_author': 'xiaotian2333',
        'category': 1,
        'link_prefix': 'https://github.com/EchoMusic-org/player-frontend',
    },
    'old-xiami-lyric-styles': {
        'zh_name': '旧版虾米歌词风格',
        'en_name': 'Old Xiami Lyric Styles',
        'zh_desc': '将页面歌词替换为旧版虾米风格：当前行高亮放大带辉光、上下行渐隐、平滑滚动跟随',
        'en_desc': 'Replace page lyrics with classic Xiami style: current line highlighted with glow, surrounding lines fade out, smooth scroll follow',
        'json_author': 'Oneday5799',
        'category': 1,
    },
    'vertical-lyric-scroll': {
        'zh_name': '竖幅歌词',
        'en_name': 'Vertical Lyric Scroll',
        'zh_desc': '竖排文字桌面歌词浮窗',
        'en_desc': 'Vertical text desktop lyrics floating window',
        'author': 'hoowhoami',
        'category': 1,
    },
    # ── 2026-10 同步新增（元数据来自上游 echo-plugins.json / 插件 manifest.json）──
    'openrgb': {
        'zh_name': 'OpenRGB 音乐灯效',
        'en_name': 'OpenRGB Music Lighting',
        'zh_desc': '将当前播放的音乐映射到 OpenRGB 灯光设备，支持频谱铺展、音量律动和低频节拍',
        'en_desc': 'Map currently playing music to OpenRGB lighting devices, with spectrum spread, volume pulsing, and bass beat effects',
        'author': 'EchoMusic',
        'category': 2,
    },
    'mv-enhancer': {
        'zh_name': 'MV 功能优化',
        'en_name': 'MV Enhancer',
        'zh_desc': '在 MV 页面横向展示歌曲的全部视频版本，优先播放最高画质的 H.265 片源',
        'en_desc': 'Show all video versions of a song on the MV page and prefer the highest-quality H.265 stream',
        'author': 'Codex Sol',
        'category': 1,
    },
    'webdav-backup': {
        'zh_name': 'WebDAV 备份',
        'en_name': 'WebDAV Backup',
        'zh_desc': '将应用设置、插件及插件数据备份到自己的 WebDAV 存储，支持恢复与同步',
        'en_desc': 'Back up app settings, plugins, and plugin data to your own WebDAV storage, with restore and sync support',
        'author': 'EchoMusic',
        'category': 3,
    },
    'theme-static': {
        'zh_name': '静态主题',
        'en_name': 'Static Themes',
        'zh_desc': '静态主题包，内置恋空、哈尼粉等主题',
        'en_desc': 'Static theme pack featuring Liankong and Honey Pink presets',
        'author': 'EchoMusic',
        'category': 0,
    },
    'theme-dynamic': {
        'zh_name': '动态主题',
        'en_name': 'Dynamic Themes',
        'zh_desc': '动态主题包，内置秋日枫叶、幻彩、金丝带、杨柳依依、旋转摩天轮等主题',
        'en_desc': 'Dynamic theme pack with Autumn Maple, Iridescent, Golden Ribbon, Swaying Willow, and Rotating Ferris Wheel presets',
        'author': 'EchoMusic',
        'category': 0,
    },
    'taskbar-lyric-with-spectrum-visualizer': {
        'zh_name': '任务栏歌词 + 频谱',
        'en_name': 'Taskbar Lyric + Spectrum',
        'zh_desc': '在任务栏歌词浮窗基础上加入频谱律动，使用前需先安装频谱可视化插件',
        'en_desc': 'Adds a spectrum visualizer to the taskbar lyric floating window. Requires the Spectrum Visualizer plugin',
        'json_author': 'etn',
        'category': 1,
    },
    'auto-team-vip': {
        'zh_name': '自动组队领 VIP',
        'en_name': 'Auto Team VIP',
        'zh_desc': '自动参加酷狗概念版官方活动「组队瓜分畅听 VIP」并自动组队，活动详情见官方说明',
        'en_desc': 'Automatically joins and teams up for the official Kugou Concept "team up to split VIP listening" event; see official rules for details',
        'json_author': 'Oneday5799',
        'category': 4,
    },
    'settings-simplifier': {
        'zh_name': '设置简化器',
        'en_name': 'Settings Simplifier',
        'zh_desc': '简化主应用设置页，通过开关控制每个设置分组及其子项的显示与隐藏',
        'en_desc': 'Simplify the main settings page by toggling the visibility of each settings group and its items',
        'json_author': 'Oneday5799',
        'category': 0,
    },
    'mouse-gesture': {
        'zh_name': '鼠标手势',
        'en_name': 'Mouse Gestures',
        'zh_desc': '使用鼠标手势控制播放、导航和滚动等操作',
        'en_desc': 'Control playback, navigation, and scrolling with mouse gestures',
        'json_author': 'Oneday5799',
        'category': 4,
    },
    'github-accelerator': {
        'zh_name': 'GitHub 加速源',
        'en_name': 'GitHub Accelerator',
        'zh_desc': '为应用更新与插件下载提供 GitHub 公益加速源选择、测速与一键应用（移植自 XIU2 Github Enhancement，GPL-3.0）',
        'en_desc': 'Pick, benchmark, and apply public GitHub mirror accelerators for app updates and plugin downloads (ported from XIU2 Github Enhancement, GPL-3.0)',
        'json_author': 'T-T2333',
        'category': 4,
    },
    'music-card-share': {
        'zh_name': '歌曲卡片分享',
        'en_name': 'Music Card Share',
        'zh_desc': '生成精美的歌曲卡片，优雅地分享正在听的音乐',
        'en_desc': 'Generate beautiful song cards to elegantly share what you are listening to',
        'json_author': 'xiaotian2333',
        'category': 4,
    },
    'taskbar-lyrics': {
        'zh_name': '任务栏歌词 · 微光',
        'en_name': 'Taskbar Lyrics · Glimmer',
        'zh_desc': '将同步歌词、动态封面与快捷播放操作融入 Windows 任务栏，支持多屏显示、智能配色与个性化外观',
        'en_desc': 'Bring synced lyrics, dynamic album art, and quick playback controls into the Windows taskbar, with multi-monitor support, smart colors, and customizable looks',
        'json_author': 'CarsonGame',
        'category': 1,
    },
    'comment-badges': {
        'zh_name': '会员徽章样式优化',
        'en_name': 'VIP Badge Restyle',
        'zh_desc': '优化评论区会员徽章显示，采用酷狗官方图标样式',
        'en_desc': 'Restyle VIP badges in comments with the official Kugou icon look',
        'json_author': 'stinaCN',
        'category': 0,
    },
    'local-music': {
        'zh_name': '本地音乐',
        'en_name': 'Local Music',
        'zh_desc': '扫描并播放本地文件夹中的音乐',
        'en_desc': 'Scan and play music from local folders',
        'json_author': 'stinaCN',
        'category': 3,
    },
    'volume-wheel': {
        'zh_name': '滚轮音量调节',
        'en_name': 'Volume Wheel',
        'zh_desc': '将鼠标悬停在主播放栏或歌词页底部的音量按钮上滚动滚轮，即可调节音量',
        'en_desc': 'Scroll the mouse wheel over the volume button in the playback bar or lyrics page to adjust the volume',
        'json_author': 'xiaotian2333',
        'category': 4,
    },
    'echo-smartisan-plugin': {
        'zh_name': 'Echo Smartisan',
        'en_name': 'Echo Smartisan',
        'zh_desc': '将 EchoMusic 界面改为 Smartisan（锤子科技）拟物风格',
        'en_desc': 'Transform EchoMusic UI to Smartisan (Hammer) skeuomorphic style',
        'json_author': '天影大侠',
        'category': 0,
    },
    'folia-style': {
        'zh_name': 'Folia 歌词',
        'en_name': 'Folia Lyrics',
        'zh_desc': '基于 Folia 的播放页，拥有多种绚丽的歌词动画效果',
        'en_desc': 'Folia-based playback page with a variety of stunning lyric animations',
        'json_author': 'Oneday5799',
        'category': 1,
    },
    'apple-music-style': {
        'zh_name': 'Apple Music 风格播放页',
        'en_name': 'Apple Music Style Player',
        'zh_desc': '将播放页面替换为 Apple Music 风格的双栏布局，使用 AMLL 渲染歌词',
        'en_desc': 'Replace the playback page with an Apple Music-style dual-column layout using AMLL for lyric rendering',
        'json_author': 'Oneday5799',
        'category': 1,
    },
    'cloud-priority': {
        'zh_name': '云盘优先',
        'en_name': 'Cloud Priority',
        'zh_desc': '播放歌曲时，若该歌曲存在于云盘文件则优先播放云盘版本',
        'en_desc': 'When playing a song, prefer the cloud-drive version if the song exists there',
        'json_author': 'Oneday5799',
        'category': 3,
    },
    'tingfm-radio': {
        'zh_name': '听FM网络电台',
        'en_name': 'TingFM Radio',
        'zh_desc': '接入听FM海量网络电台直播源，支持搜索添加全国各地电台',
        'en_desc': "Access TingFM's vast live radio streams, with search to add stations from across the country",
        'json_author': 'xiaotian2333',
        'category': 3,
    },
    'echo-remote': {
        'zh_name': '局域网远程遥控',
        'en_name': 'Echo Remote',
        'zh_desc': '通过局域网 WebUI 遥控 EchoMusic：播放控制、进度拖拽、切歌、音量、歌曲信息与封面显示，支持局域网搜索点歌与播放列表查看（自动定位当前播放）',
        'en_desc': 'Control EchoMusic over LAN via a WebUI: playback, progress dragging, track switching, volume, song info and cover display, plus LAN song search and playlist view (auto-locates the current track)',
        'json_author': 'yuanqian, lm379',
        'category': 4,
    },
    'echo-menu-lyrics': {
        'zh_name': 'Mac 菜单栏歌词',
        'en_name': 'macOS Menu Bar Lyrics',
        'zh_desc': '在 macOS 菜单栏显示当前播放歌词，随时瞄一眼正在唱到哪一句',
        'en_desc': 'Show the currently playing lyrics in the macOS menu bar for a glance at the current line',
        'json_author': 'whuyfk',
        'category': 1,
    },
    'echo-acrylic': {
        'zh_name': '亚克力分层材质',
        'en_name': 'Acrylic Layering',
        'zh_desc': '给按钮、卡片、列表行、播放栏等可交互元素铺一层染色亚克力板材（半透明 + 背后磨砂 + 主题色染色），不改背景与壁纸。四组分区各自可开关，并可独立调颜色、浓度、磨砂',
        'en_desc': 'Add a tinted acrylic layer to interactive elements (buttons, cards, list rows, the player bar): translucent with backdrop frost and theme-color tint, without touching the background or wallpaper. Four separate zones, each toggleable with independent color, opacity, and frost controls',
        'category': 0,
    },
}

# 社区源插件统一归入一个分类
CATEGORY_COMMUNITY = len(CATEGORIES)


# ── 工具函数 ──────────────────────────────────────────

def fetch_json(url):
    """Fetch and parse JSON from URL with retry."""
    req = urllib.request.Request(url, headers={'User-Agent': 'EchoMusic-docs-sync/1.0'})
    last_err = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            last_err = e
            if attempt < 2:
                wait = 2 ** attempt  # 1s, 2s, 4s
                print('  Retrying ({}/3) after {}s: {}'.format(attempt + 1, wait, e))
                time.sleep(wait)
    raise last_err


def fetch_text(url):
    """Fetch raw text from URL with retry."""
    req = urllib.request.Request(url, headers={'User-Agent': 'EchoMusic-docs-sync/1.0'})
    last_err = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode('utf-8')
        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            last_err = e
            if attempt < 2:
                wait = 2 ** attempt  # 1s, 2s, 4s
                print('  Retrying ({}/3) after {}s: {}'.format(attempt + 1, wait, e))
                time.sleep(wait)
    raise last_err


# ── 插件图标本地镜像 ──────────────────────────────────
# raw.githubusercontent / jsDelivr 在国内访问不稳定，浏览器端多级回退仍会出现裂图
# （且 hydration 前加载失败会漏掉 @error 处理）。由同步脚本把图标下载到
# docs/public/plugin-icons/ 作为本地镜像，组件优先本地加载，零外网依赖。

ICON_EXTS = ('.png', '.jpg', '.jpeg', '.svg', '.webp', '.gif', '.ico')


def icon_ext_from_url(url):
    """Guess the icon file extension from its URL (default: .png)."""
    lower = url.split('?')[0].split('#')[0].lower()
    for ext in ICON_EXTS:
        if lower.endswith(ext):
            return ext
    return '.png'


def fetch_icon_bytes(url):
    """Download icon bytes with retry. Returns bytes or None."""
    req = urllib.request.Request(url, headers={'User-Agent': 'EchoMusic-docs-sync/1.0'})
    last_err = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                if data:
                    return data
                last_err = IOError('empty response body')
        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            last_err = e
            if attempt < 2:
                time.sleep(2 ** attempt)
    print('    ✗ 图标下载失败: {}'.format(last_err))
    return None


def load_prev_plugin_data():
    """Read the current plugins.json (before this run overwrites it) to know
    each plugin's previously synced version — unchanged versions skip download."""
    path = os.path.join(DOCS_DIR, '.vitepress', 'data', 'plugins.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return {p['id']: p for p in data.get('plugins', [])}
    except Exception:
        return {}


def download_plugin_icons(plugins):
    """Mirror official plugin icons into docs/public/plugin-icons/.

    Sets p['iconExt'] on success (written into plugins.json for the component);
    on failure the remote icon URL is kept and the component falls back to the
    jsDelivr → raw → initial-letter chain. Returns whether any file was written.
    """
    icons_dir = os.path.join(DOCS_DIR, 'docs', 'public', 'plugin-icons')
    prev = load_prev_plugin_data()
    kept = set()
    downloaded = 0
    for p in plugins:
        icon_url = p.get('icon')
        if not icon_url:
            continue
        ext = p.get('iconExt') or icon_ext_from_url(icon_url)
        fname = p['id'] + ext
        fpath = os.path.join(icons_dir, fname)
        prev_version = (prev.get(p['id']) or {}).get('version')
        # 版本未变且本地镜像已存在时跳过（每小时定时同步不重复打扰上游）
        if (os.path.exists(fpath)
                and p.get('version')
                and p.get('version') == prev_version):
            kept.add(fname)
            p['iconExt'] = ext
            continue
        data = fetch_icon_bytes(icon_url)
        if data is None:
            continue  # 下载失败：保留远程链接，组件走回退链
        if not DRY_RUN:
            os.makedirs(icons_dir, exist_ok=True)
            with open(fpath, 'wb') as f:
                f.write(data)
        kept.add(fname)
        p['iconExt'] = ext
        downloaded += 1
        print('  ✓ {} ({}, {} KB)'.format(fname, p.get('version') or '?', max(1, len(data) // 1024)))

    # 清理已下架 / 图标改扩展名插件的孤儿文件
    if not DRY_RUN and os.path.isdir(icons_dir):
        for name in sorted(os.listdir(icons_dir)):
            _, ext = os.path.splitext(name)
            if ext.lower() in ICON_EXTS and name not in kept:
                os.remove(os.path.join(icons_dir, name))
                print('  - 移除孤儿图标 {}'.format(name))

    if DRY_RUN:
        print('  ○ 图标本地镜像 {} 个（dry-run，跳过写入）'.format(len(kept)))
    elif downloaded:
        print('  ✓ 图标本地镜像：新增/更新 {} 个，共 {} 个'.format(downloaded, len(kept)))
    else:
        print('  ✓ 图标本地镜像无变化（共 {} 个）'.format(len(kept)))
    return downloaded > 0


def sync_icons_only():
    """--icons-only: 只根据现有 plugins.json 补齐/刷新图标本地镜像，不拉取上游。"""
    path = os.path.join(DOCS_DIR, '.vitepress', 'data', 'plugins.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print('✗ 读取 plugins.json 失败: {}'.format(e))
        sys.exit(1)
    official = [p for p in data.get('plugins', [])
                if p.get('source') == 'official' and p.get('icon')]
    print('官方插件 {} 个（带图标），检查本地镜像...'.format(len(official)))
    before = json.dumps(data, ensure_ascii=False, sort_keys=True)
    download_plugin_icons(official)
    after = json.dumps(data, ensure_ascii=False, sort_keys=True)
    if before != after:
        if not DRY_RUN:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
        print('✓ plugins.json 已更新 iconExt 字段')
    else:
        print('✓ plugins.json 无变化')


def fetch_heat_scores(pairs):
    """Fetch current heat scores for (sourceId, pluginId) pairs from the stats API.
    Returns {(sourceId, pluginId): score} — empty dict on failure."""
    body = json.dumps({
        'plugins': [{'sourceId': s, 'pluginId': p} for s, p in pairs]
    }).encode('utf-8')
    req = urllib.request.Request(
        STATS_API_URL, data=body,
        headers={'User-Agent': 'EchoMusic-docs-sync/1.0', 'Content-Type': 'application/json'}
    )
    last_err = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            return {
                (item.get('sourceId'), item.get('pluginId')): (item.get('stats') or {}).get('score')
                for item in data.get('plugins', [])
            }
        except (urllib.error.URLError, urllib.error.HTTPError, ValueError) as e:
            last_err = e
            if attempt < 2:
                time.sleep(2 ** attempt)
    print('  ⚠ 热度快照获取失败，插件目录保持分类/ID 序: {}'.format(last_err))
    return {}


def fetch_manifest(plugin_entry):
    """Fetch manifest.json for a plugin that lacks metadata.
    Returns (name, description, author) tuple, or (None, None, None) on failure.

    Author priority:
    1. echo-plugins.json author field (already handled by caller)
    2. manifest.json author field
    3. Infer from repo URL owner
    4. Fallback: repo owner name
    """
    plugin_id = plugin_entry.get('id', '')
    path = plugin_entry.get('path', '')
    repo = plugin_entry.get('repo', '')

    if repo:
        owner_repo = repo.replace('https://github.com/', '').rstrip('/')
        manifest_url = 'https://raw.githubusercontent.com/{}/main/manifest.json'.format(owner_repo)
    else:
        if path:
            manifest_url = '{}/{}/manifest.json'.format(PLUGINS_REPO_RAW, path)
        else:
            return None, None, None

    try:
        manifest = fetch_json(manifest_url)
        name = manifest.get('name', '')
        description = manifest.get('description', '')
        author = manifest.get('author', '')
        # If author is still empty, infer from repo
        if not author and repo:
            parts = repo.replace('https://github.com/', '').rstrip('/').split('/')
            author = parts[0] if parts else ''
        elif not author:
            author = 'hoowhoami'
        return name, description, author
    except Exception as e:
        print('  Warning: manifest fetch failed ({}): {}'.format(manifest_url, e))
        return None, None, None


def categorize_by_tags(tags):
    """Auto-categorize a plugin based on its tags."""
    for tag in tags:
        cat = TAG_TO_CAT.get(tag.lower())
        if cat is not None:
            return cat
    return 4  # Default: 效率工具


def get_plugin_link(plugin_entry, plugin_id):
    """Get the best URL to link the plugin name to."""
    homepage = plugin_entry.get('homepage', '')
    repo = plugin_entry.get('repo', '')
    path = plugin_entry.get('path', '')
    if homepage:
        return homepage
    if repo:
        return repo
    if path:
        return 'https://github.com/hoowhoami/EchoMusicPlugins/tree/main/{}'.format(path)
    return 'https://github.com/hoowhoami/EchoMusicPlugins'


def fetch_plugin_info(plugin_entry, raw_base=None):
    """Fetch manifest.json info.
    Returns (version, icon_url, echo_music_version) — 'unknown'/None when unavailable.
    Accepts optional raw_base for community sources."""
    path = plugin_entry.get('path', '')
    repo = plugin_entry.get('repo', '')

    if raw_base:
        # Community source: use raw_base
        if path:
            manifest_url = '{}/{}/manifest.json'.format(raw_base, path)
        else:
            manifest_url = '{}/manifest.json'.format(raw_base)
    elif repo:
        owner_repo = repo.replace('https://github.com/', '').rstrip('/')
        if not path:
            # Independent repo, manifest at root
            manifest_url = 'https://raw.githubusercontent.com/{}/main/manifest.json'.format(owner_repo)
        else:
            manifest_url = 'https://raw.githubusercontent.com/{}/main/{}/manifest.json'.format(owner_repo, path)
    elif path:
        manifest_url = '{}/{}/manifest.json'.format(PLUGINS_REPO_RAW, path)
    else:
        return 'unknown', None

    try:
        manifest = fetch_json(manifest_url)
        version = manifest.get('version', 'unknown')
        icon = manifest.get('icon') or None
        icon_url = None
        if icon:
            icon_url = '{}/{}'.format(manifest_url.rsplit('/', 1)[0], icon)
        echo_ver = (manifest.get('requires') or {}).get('echoMusicVersion') or None
        return version, icon_url, echo_ver
    except Exception:
        return 'unknown', None, None


def repo_to_source_id(repo_url):
    """Extract sourceId from repo URL: github:owner/repo (lowercase)."""
    m = re.search(r'github\.com/([^/]+/[^/]+)', repo_url, re.IGNORECASE)
    if m:
        return 'github:' + m.group(1).lower()
    return 'unknown'


def build_share_link(plugin_id, source_url, plugin_path, version, plugin_homepage=None):
    """Build the wrapped echomusic:// plugin share link."""
    from urllib.parse import quote, urlencode

    source_id = repo_to_source_id(source_url)
    if plugin_homepage is None:
        plugin_homepage = '{}/tree/main/{}'.format(source_url.rstrip('/'), plugin_path) if plugin_path else source_url

    # Build deep link: param values must be URL-encoded (they are decoded by the app)
    params = {
        'sourceId': source_id,
        'source': source_url,
        'version': version,
        'homepage': plugin_homepage,
    }
    deep_link = 'echomusic://plugin/{}?{}'.format(plugin_id, urlencode(params, safe=''))
    target = quote(deep_link, safe='')
    return 'https://hoowhoami.github.io/EchoMusic/share/?target={}'.format(target)


def get_plugin_meta(plugin_entry):
    """Get full metadata for a plugin from echo-plugins.json entry.
    Returns dict with id, zh_name, en_name, zh_desc, en_desc, author, category, link, share.
    """
    plugin_id = plugin_entry.get('id', '')
    curated = CURATED.get(plugin_id, {})

    # Link
    link = curated.get('link_prefix') or get_plugin_link(plugin_entry, plugin_id)

    # Author - echo-plugins.json author takes priority
    json_author = plugin_entry.get('author', '')
    if json_author:
        author = json_author
    elif 'author' in curated:
        author = curated['author']
    elif 'json_author' in curated:
        author = curated['json_author']
    else:
        # Unknown plugin - fetch manifest for author
        _, _, manifest_author = fetch_manifest(plugin_entry)
        author = manifest_author or ''

    # Name & Description
    json_name = plugin_entry.get('name', '')
    json_desc = plugin_entry.get('description', '')

    if 'zh_name' in curated:
        # Known plugin - use curated translations
        zh_name = curated['zh_name']
        en_name = curated['en_name']
        zh_desc = curated.get('zh_desc', json_desc)
        en_desc = curated.get('en_desc', json_desc)
    elif json_name:
        # Has metadata in JSON but not in curated - use JSON data
        zh_name = json_name
        zh_desc = json_desc
        # If JSON name contains Chinese, try auto-translate as fallback
        if any('\u4e00' <= c <= '\u9fff' for c in json_name):
            en_name = translate_to_english(json_name) or plugin_id
            if json_desc:
                en_desc = translate_to_english(json_desc) or ('(No English description) ' + json_desc)
            else:
                en_desc = ''
        else:
            en_name = json_name
            en_desc = json_desc
    else:
        # New plugin without any metadata - fetch manifest
        manifest_name, manifest_desc, _ = fetch_manifest(plugin_entry)
        zh_name = manifest_name or plugin_id
        zh_desc = manifest_desc or ''
        # If manifest name contains Chinese, try auto-translate as fallback
        if manifest_name and any('\u4e00' <= c <= '\u9fff' for c in manifest_name):
            en_name = translate_to_english(manifest_name) or plugin_id
            en_desc = translate_to_english(manifest_desc or '') or ('(No English description) ' + (manifest_desc or ''))
        else:
            en_name = manifest_name or plugin_id
            en_desc = manifest_desc or ''

    # Category
    if 'category' in curated:
        category = curated['category']
    else:
        tags = plugin_entry.get('tags', [])
        category = categorize_by_tags(tags)

    # ── 构建分享链接 ─────────────────────────────
    path = plugin_entry.get('path', '')
    repo = plugin_entry.get('repo', '')
    source_url = repo if repo else PLUGINS_REPO
    version, icon_url, echo_ver = fetch_plugin_info(plugin_entry)
    homepage = plugin_entry.get('homepage', '')
    share_link = build_share_link(plugin_id, source_url, path, version, homepage or None)

    # 统计查询的 sourceId：官方列表插件的安装统计统一记录在官方源名下
    # （实测：带自有 repo 的插件其 repo 名下统计为 0），不能按 repo 字段推导
    return {
        'id': plugin_id,
        'sourceId': repo_to_source_id(PLUGINS_REPO),
        'zh_name': zh_name,
        'en_name': en_name,
        'zh_desc': zh_desc,
        'en_desc': en_desc,
        'author': author if author else '',
        'category': category,
        'link': link,
        'share': share_link,
        'version': version,
        'icon': icon_url,
        'echoMusicVersion': echo_ver,
        'tags': plugin_entry.get('tags', []),
    }


# ── 插件同步 ──────────────────────────────────────────

def sync_plugins():
    """Sync plugin metadata from upstream echo-plugins.json (for plugins.json)."""
    print('[1/4] 获取插件源索引...')
    try:
        data = fetch_json(PLUGINS_JSON_URL)
    except Exception as e:
        print('  ✗ 获取失败: {}'.format(e))
        return False, []

    plugins_json = data.get('plugins', [])
    print('  ✓ 获取到 {} 个插件'.format(len(plugins_json)))

    # Build plugin metadata for all entries in echo-plugins.json
    print('[2/4] 解析插件元数据...')
    upstream_plugins = []
    for entry in plugins_json:
        pid = entry.get('id', '')
        print('  -> {}... '.format(pid), end='')
        try:
            meta = get_plugin_meta(entry)
            upstream_plugins.append(meta)
            print('{}'.format(meta['author']))
        except Exception as e:
            print('✗ {}'.format(e))

    # Add extra plugins (in CURATED but NOT in upstream JSON)
    upstream_ids = {p['id'] for p in upstream_plugins}
    curated_ids = list(CURATED.keys())
    for pid in curated_ids:
        if pid in upstream_ids:
            continue
        curated = CURATED[pid]
        if 'zh_name' not in curated:
            continue
        # Build link for extra plugin
        if 'link_prefix' in curated:
            link = curated['link_prefix']
        else:
            link = None  # 必须显式设置 link_prefix

        author = curated.get('author') or curated.get('json_author') or ''
        extra = {
            'id': pid,
            # 仅文档收录插件没有上游 repo，sourceId 从 link_prefix 推导（供热度查询用）
            'sourceId': repo_to_source_id(link) if link else 'unknown',
            'zh_name': curated['zh_name'],
            'en_name': curated['en_name'],
            'zh_desc': curated['zh_desc'],
            'en_desc': curated['en_desc'],
            'author': author,
            'category': curated['category'],
            'link': link,
            # 仅文档收录的插件无上游 path/repo 可自动构建分享链接，
            # 使用 CURATED 中人工预置的 share（若有），避免渲染成 "#"
            'share': curated.get('share', '#'),
            'version': None,
            'icon': None,
            'echoMusicVersion': None,
            'tags': [],
        }
        upstream_plugins.append(extra)
        print('  + {} (仅文档收录)'.format(pid))

    # Sort: by category, then by ID
    upstream_plugins.sort(key=lambda p: (p['category'], p['id'].lower()))

    # 插件列表页已由插件市场页（/plugins/，PluginMarketplace 组件）替代，
    # 这里只同步插件元数据供 plugins.json 使用
    return upstream_plugins


# ── 更新日志同步 ──────────────────────────────────────
# 页面不再直接镜像上游 CHANGELOG，而是由本地条目仓库重建：
# - changelog-raw.json：上游原始条目仓库（append-only，已收录条目不再更新）
# - 按版本系列合并去重：每系列（去掉 -beta.N 的基础版本号）一条，正式版吸收同系列
#   beta 内容（上游 beta 条目或为累计重复、或为增量说明，正式版条目又常是占位）
# - 首页只保留最新 N 个系列，其余进入归档页 archive.md
# - 英文页按系列缓存译文（changelog-translations.json），上游数据未变则直接复用

CHANGELOG_RAW_PATH = os.path.join(DOCS_DIR, '.vitepress', 'data', 'changelog-raw.json')
CHANGELOG_TRANS_PATH = os.path.join(DOCS_DIR, '.vitepress', 'data', 'changelog-translations.json')
ZH_CHANGELOG_PATH = os.path.join(DOCS_DIR, 'docs', 'changelog', 'index.md')
ZH_ARCHIVE_PATH = os.path.join(DOCS_DIR, 'docs', 'changelog', 'archive.md')
EN_CHANGELOG_PATH = os.path.join(DOCS_DIR, 'docs', 'en', 'changelog', 'index.md')
EN_ARCHIVE_PATH = os.path.join(DOCS_DIR, 'docs', 'en', 'changelog', 'archive.md')

# 首页保留的最新系列数（从新到旧），其余系列进入归档页
INDEX_SERIES_LIMIT = 4

# 中文小节标题 → 英文固定映射（不交给翻译引擎，保证各页面一致）
SECTION_HEAD_EN = {
    '新增': 'Added',
    '优化': 'Improved',
    '修复': 'Fixed',
    '重构': 'Refactored',
    '已知变更': 'Known Changes',
}

# 旧英文页小节标题是翻译产物、拼写不一，回收旧译文前先归一化到 SECTION_HEAD_EN 的值
EN_HEADING_REVERSE = {
    'New': 'Added', 'Added': 'Added',
    'Improvements': 'Improved', 'Improvement': 'Improved', 'Improved': 'Improved',
    'Optimization': 'Improved', 'Optimized': 'Improved',
    'Fix': 'Fixed', 'Fixes': 'Fixed', 'Fixed': 'Fixed',
    'Refactored': 'Refactored', 'Refactor': 'Refactored',
    'Known Changes': 'Known Changes',
}


def normalize_en_section_headings(body):
    """把英文正文里的各小节标题变体归一化为标准拼写。"""
    def repl(m):
        name = m.group(1).strip()
        return '### ' + EN_HEADING_REVERSE.get(name, name)
    return re.sub(r'^### (.+)$', repl, body, flags=re.MULTILINE)

PAGE_HEADER_ZH = '''---
title: 更新日志
sidebar: false
---

# 更新日志

本页记录 EchoMusic 的主要版本更新内容。完整更新日志请参阅 [GitHub Releases](https://github.com/hoowhoami/EchoMusic/releases)。

> ⚠️ 本软件完全免费且开源，请勿通过任何付费渠道下载。
>
> 🤡 如果你是付费获取的，说明你被骗了。'''

PAGE_FOOTER_INDEX_ZH = '''## 更早版本

更早版本的更新内容请参阅 [更新日志归档](/changelog/archive)，或到 [GitHub Releases](https://github.com/hoowhoami/EchoMusic/releases) 查看完整历史。'''

PAGE_HEADER_ARCHIVE_ZH = '''---
title: 更新日志归档
sidebar: false
---

# 更新日志归档

{intro}最新版本更新请参阅 [更新日志](/changelog/)。'''

PAGE_FOOTER_ARCHIVE_ZH = '''## 更早版本

更早的测试版本（2.1.5 及以下）请参阅 [GitHub Releases](https://github.com/hoowhoami/EchoMusic/releases)。'''

PAGE_HEADER_EN = '''---
title: Changelog
sidebar: false
---

# Changelog

This page records the major version updates for EchoMusic. For the complete changelog, see [GitHub Releases](https://github.com/hoowhoami/EchoMusic/releases).

> ⚠️ This software is completely free and open-source. Do not obtain it through any paid channels.
>
> 🤡 If you acquired it by paying, you've been scammed.'''

PAGE_FOOTER_INDEX_EN = '''## Earlier Versions

For earlier versions, see the [changelog archive](/en/changelog/archive), or check [GitHub Releases](https://github.com/hoowhoami/EchoMusic/releases) for the complete history.'''

PAGE_HEADER_ARCHIVE_EN = '''---
title: Changelog Archive
sidebar: false
---

# Changelog Archive

{intro}For recent versions, see the [Changelog](/en/changelog/).'''

PAGE_FOOTER_ARCHIVE_EN = '''## Earlier Versions

For test versions (2.1.5 and below), please see [GitHub Releases](https://github.com/hoowhoami/EchoMusic/releases).'''

TRANSLATION_PENDING_EN = '''> **🔔 Translation pending: {bases}**
> Automatic translation failed for these versions, so their notes below are shown in Chinese. Please refer to the Chinese changelog for reference.'''


def parse_changelog_versions(text):
    """Parse version entries from CHANGELOG.md.
    Returns list of (version, date, content) tuples."""
    pattern = re.compile(
        r'^## \[([^\]]+)\]\s*-\s*(\d{4}-\d{2}-\d{2})\s*\n(.*?)(?=^## \[|\Z)',
        re.MULTILINE | re.DOTALL
    )
    versions = []
    for match in pattern.finditer(text):
        versions.append((match.group(1), match.group(2), match.group(0).strip()))
    return versions


def translate_to_english(text):
    """Translate a short Chinese text to English using Google Translate.
    Returns None if deep_translator is unavailable or text is already English."""
    if not text or not any('\u4e00' <= c <= '\u9fff' for c in text):
        return None
    try:
        from deep_translator import GoogleTranslator
        return GoogleTranslator(source='zh-CN', target='en').translate(text)
    except ImportError:
        return None
    except Exception as e:
        print('  ⚠ 翻译失败 ({}): {}'.format(text[:30], e))
        return None


_TRANSLATION_REACHABLE = None  # None=未探测，True/False=探测结果


def translation_service_reachable():
    """探测 translate.google.com 是否可达（本地环境常被墙，探测一次避免反复超时）。"""
    global _TRANSLATION_REACHABLE
    if _TRANSLATION_REACHABLE is None:
        try:
            req = urllib.request.Request(
                'https://translate.google.com', headers={'User-Agent': 'Mozilla/5.0'})
            urllib.request.urlopen(req, timeout=8)
            _TRANSLATION_REACHABLE = True
        except Exception:
            print('  ⚠ translate.google.com 不可达，本次跳过自动翻译')
            _TRANSLATION_REACHABLE = False
    return _TRANSLATION_REACHABLE


def translate_changelog_body(body):
    """Translate a merged changelog series body (Chinese) to English.
    Section headings use the fixed SECTION_HEAD_EN map; the remaining text is
    grouped into ~4000-char chunks and sent to Google Translate.
    Returns None if deep_translator is unavailable or a chunk fails."""
    if not translation_service_reachable():
        return None
    try:
        from deep_translator import GoogleTranslator
    except ImportError:
        print('  ⚠ deep_translator 未安装，跳过翻译')
        return None

    if not any('\u4e00' <= c <= '\u9fff' for c in body):
        return body

    # 按行分组为「小节标题（固定映射）/ 文本段（送翻译）」，标题不进翻译引擎
    paragraphs = []  # ('head', name) | ('text', text)
    cur_text = []
    for line in body.split('\n'):
        if line.startswith('### '):
            if cur_text:
                paragraphs.append(('text', '\n'.join(cur_text)))
                cur_text = []
            name = line[4:].strip()
            paragraphs.append(('head', SECTION_HEAD_EN.get(name, name)))
        elif line.strip():
            cur_text.append(line)
        elif cur_text:
            paragraphs.append(('text', '\n'.join(cur_text)))
            cur_text = []
    if cur_text:
        paragraphs.append(('text', '\n'.join(cur_text)))

    translated_parts = []
    chunk, chunk_len = [], 0

    def flush_chunk():
        nonlocal chunk, chunk_len
        if not chunk:
            return
        text = '\n\n'.join(chunk).strip()
        if any('\u4e00' <= c <= '\u9fff' for c in text):
            try:
                text = GoogleTranslator(source='zh-CN', target='en').translate(text)
            except Exception as e:
                print('  ⚠ 翻译块失败: {}'.format(e))
                raise
        translated_parts.append(text)
        chunk, chunk_len = [], 0

    try:
        for kind, val in paragraphs:
            if kind == 'head':
                flush_chunk()
                translated_parts.append('### ' + val)
                continue
            if chunk and chunk_len + len(val) > 3800:
                flush_chunk()
            chunk.append(val)
            chunk_len += len(val)
        flush_chunk()
    except Exception:
        return None

    return '\n\n'.join(translated_parts)


def base_version(version):
    """去掉 -beta.N 等预发布后缀的基础版本号。"""
    return version.split('-')[0]


def version_sort_key(version):
    """版本排序键（数值元组），用于系列间排序。"""
    parts = []
    for part in base_version(version).split('.'):
        try:
            parts.append(int(part))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def beta_number(version):
    """beta 序号，非 beta 返回 0。"""
    m = re.search(r'-beta\.(\d+)', version)
    return int(m.group(1)) if m else 0


def normalize_entry_body(body):
    """去掉条目头部的 `## [version] - date` 行，只留正文。
    正文里再出现 `## ` 开头的行（如页面底部「更早版本」栏被最后一个条目
    吞进来）一律截断丢弃。"""
    lines = body.strip().split('\n')
    if lines and lines[0].startswith('## ['):
        lines = lines[1:]
    for i, line in enumerate(lines):
        if line.startswith('## ') and i > 0:
            lines = lines[:i]
            break
    return '\n'.join(lines).strip()


def merge_series_entries(raw_entries):
    """按版本系列合并原始条目：每系列一条，内容取并集。

    - 系列内先正式版后 beta（旧→新），按首次出现顺序保留；
    - 小节（### 新增 等）内与条目开头的叙述行均按整行精确去重；
    - 返回按系列版本号新→旧排序的列表：
      [{'base', 'version', 'date', 'body'}]，body 不含 `## [` 标题行。
    """
    series = OrderedDict()
    for entry in raw_entries:
        series.setdefault(base_version(entry['version']), []).append(entry)

    merged = []
    for base, entries in series.items():
        stables = [e for e in entries if '-beta' not in e['version']]
        betas = sorted((e for e in entries if '-beta' in e['version']),
                       key=lambda e: beta_number(e['version']))
        ordered = stables + betas

        if stables:
            title_version = stables[0]['version']
            title_date = stables[0]['date']
        else:
            latest = max(betas, key=lambda e: beta_number(e['version']))
            title_version = latest['version']
            title_date = latest['date']

        top_lines, sections, seen = [], OrderedDict(), set()
        cur_section = None
        for entry in ordered:
            for line in normalize_entry_body(entry['body']).split('\n'):
                line = line.rstrip()
                if not line.strip():
                    continue
                if line.startswith('### '):
                    cur_section = line[4:].strip()
                    sections.setdefault(cur_section, [])
                    continue
                if line in seen:
                    continue
                seen.add(line)
                if cur_section is None:
                    top_lines.append(line)
                else:
                    sections[cur_section].append(line)

        body_lines = []
        if top_lines:
            body_lines.extend(top_lines)
            body_lines.append('')
        for name, items in sections.items():
            body_lines.append('### ' + name)
            body_lines.append('')
            body_lines.extend(items)
            body_lines.append('')
        body = '\n'.join(body_lines).strip()

        merged.append({'base': base, 'version': title_version,
                       'date': title_date, 'body': body})

    merged.sort(key=lambda m: version_sort_key(m['base']), reverse=True)
    return merged


def audit_changelog_integrity(raw_entries, merged):
    """自检：条目仓库的每一行正文（非小节标题）都应出现在合并结果中。"""
    expected = set()
    for entry in raw_entries:
        for line in normalize_entry_body(entry['body']).split('\n'):
            line = line.rstrip()
            if line.strip() and not line.startswith('### '):
                expected.add(line)
    rendered = set()
    for m in merged:
        for line in m['body'].split('\n'):
            if line.strip() and not line.startswith('### '):
                rendered.add(line)
    missing = expected - rendered
    if missing:
        print('  ⚠ 自检：{} 行正文在合并时丢失，例如: {}'.format(
            len(missing), ' / '.join(sorted(missing)[:3])))
        return False
    return True


def save_changelog_raw(entries):
    os.makedirs(os.path.dirname(CHANGELOG_RAW_PATH), exist_ok=True)
    with open(CHANGELOG_RAW_PATH, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
        f.write('\n')


def load_changelog_raw():
    """加载本地条目仓库；缺失时从现有中文更新日志页播种（该页存的是上游原文）。"""
    if os.path.exists(CHANGELOG_RAW_PATH):
        with open(CHANGELOG_RAW_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    if not os.path.exists(ZH_CHANGELOG_PATH):
        return []
    with open(ZH_CHANGELOG_PATH, 'r', encoding='utf-8') as f:
        text = f.read()
    entries = [{'version': v, 'date': d, 'body': normalize_entry_body(b)}
               for v, d, b in parse_changelog_versions(text)]
    print('  ✓ changelog-raw.json 缺失，从现有中文页播种 {} 个条目'.format(len(entries)))
    if not DRY_RUN and entries:
        save_changelog_raw(entries)
    return entries


def load_translation_cache():
    if os.path.exists(CHANGELOG_TRANS_PATH):
        with open(CHANGELOG_TRANS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_translation_cache(cache):
    os.makedirs(os.path.dirname(CHANGELOG_TRANS_PATH), exist_ok=True)
    with open(CHANGELOG_TRANS_PATH, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
        f.write('\n')


def load_existing_en_series():
    """从磁盘上现有英文页提取合并后的系列正文（缓存缺失时的回收来源）。
    旧英文页小节标题是翻译产物、拼写不一（New/Added、Fix/Fixes/Fixed 等），
    先归一化再合并，避免同名小节被拆分。"""
    parsed = {}
    for path in (EN_CHANGELOG_PATH, EN_ARCHIVE_PATH):
        if not os.path.exists(path):
            continue
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        for v, d, b in parse_changelog_versions(text):
            parsed.setdefault(base_version(v), []).append(
                {'version': v, 'date': d,
                 'body': normalize_en_section_headings(normalize_entry_body(b))})
    return {base: merge_series_entries(entries)[0]
            for base, entries in parsed.items()}


def translate_series_body(m, cache, en_existing):
    """单个系列的英文正文：缓存命中直接复用；未命中则尝试翻译；
    翻译不可用时，仅当缓存完全缺失该系列且现有英文页有同版本条目时回收旧译文。
    返回 (正文, 是否完整翻译, 缓存是否有改动)。"""
    cached = cache.get(m['base'])
    if cached and cached.get('zh') == m['body'] and cached.get('en'):
        return cached['en'], cached.get('complete', True), False

    translated = translate_changelog_body(m['body'])
    if translated is not None:
        cache[m['base']] = {'zh': m['body'], 'en': translated, 'complete': True}
        return translated, True, True

    if cached is None and m['base'] in en_existing:
        old = en_existing[m['base']]
        if old['version'] == m['version'] and old['date'] == m['date']:
            print('  ⚠ 翻译不可用，{} 沿用现有英文内容'.format(m['base']))
            cache[m['base']] = {'zh': m['body'], 'en': old['body'], 'complete': True}
            return old['body'], True, True

    if cached is None:
        cache[m['base']] = {'zh': m['body'], 'en': m['body'], 'complete': False}
    print('  ⚠ {} 翻译失败，暂以中文展示'.format(m['base']))
    return m['body'], False, False


def render_series_entry(m, body):
    if body:
        return '## [{}] - {}\n\n{}'.format(m['version'], m['date'], body)
    return '## [{}] - {}'.format(m['version'], m['date'])


def assemble_page(header, entry_bodies, footer, reminder=None):
    parts = [header]
    if reminder:
        parts.append(reminder)
    parts.extend(entry_bodies)
    parts.append(footer)
    return '\n\n'.join(parts) + '\n'


def write_if_changed(path, content, label):
    old = ''
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            old = f.read()
    if old == content:
        print('  ✓ {}已是最新'.format(label))
        return False
    if DRY_RUN:
        print('  ○ {}有变更 (dry-run)'.format(label))
        return True
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('  ✓ {}已更新'.format(label))
    return True


def rebuild_changelog_pages(raw_entries):
    """按系列合并重建中英更新日志首页与归档页。"""
    merged = merge_series_entries(raw_entries)
    audit_changelog_integrity(raw_entries, merged)

    index_series = merged[:INDEX_SERIES_LIMIT]
    archive_series = merged[INDEX_SERIES_LIMIT:]
    if not archive_series:
        print('  ⚠ 归档页无内容，请检查 INDEX_SERIES_LIMIT 设置')

    # ── 中文 ──
    zh_index = assemble_page(
        PAGE_HEADER_ZH,
        [render_series_entry(m, m['body']) for m in index_series],
        PAGE_FOOTER_INDEX_ZH)
    changed = write_if_changed(ZH_CHANGELOG_PATH, zh_index, '中文更新日志')

    archive_intro_zh = ''
    if archive_series:
        archive_intro_zh = '{} 及更早版本的历史更新内容。'.format(archive_series[0]['version'])
    zh_archive = assemble_page(
        PAGE_HEADER_ARCHIVE_ZH.format(intro=archive_intro_zh),
        [render_series_entry(m, m['body']) for m in archive_series],
        PAGE_FOOTER_ARCHIVE_ZH)
    changed |= write_if_changed(ZH_ARCHIVE_PATH, zh_archive, '中文更新日志归档')

    # ── 英文 ──
    cache = load_translation_cache()
    en_existing = load_existing_en_series()
    cache_dirty = False
    incomplete_index, incomplete_archive = [], []

    en_index_bodies = []
    for m in index_series:
        body, complete, dirty = translate_series_body(m, cache, en_existing)
        cache_dirty |= dirty
        if not complete:
            incomplete_index.append(m['base'])
        en_index_bodies.append(render_series_entry(m, body))

    en_archive_bodies = []
    for m in archive_series:
        body, complete, dirty = translate_series_body(m, cache, en_existing)
        cache_dirty |= dirty
        if not complete:
            incomplete_archive.append(m['base'])
        en_archive_bodies.append(render_series_entry(m, body))

    en_index = assemble_page(
        PAGE_HEADER_EN, en_index_bodies, PAGE_FOOTER_INDEX_EN,
        TRANSLATION_PENDING_EN.format(bases=', '.join(incomplete_index)) if incomplete_index else None)
    changed |= write_if_changed(EN_CHANGELOG_PATH, en_index, '英文更新日志')

    archive_intro_en = ''
    if archive_series:
        archive_intro_en = 'Historical release notes for {} and earlier. '.format(archive_series[0]['version'])
    en_archive = assemble_page(
        PAGE_HEADER_ARCHIVE_EN.format(intro=archive_intro_en), en_archive_bodies, PAGE_FOOTER_ARCHIVE_EN,
        TRANSLATION_PENDING_EN.format(bases=', '.join(incomplete_archive)) if incomplete_archive else None)
    changed |= write_if_changed(EN_ARCHIVE_PATH, en_archive, '英文更新日志归档')

    if cache_dirty and not DRY_RUN:
        save_translation_cache(cache)

    return changed


def sync_changelog():
    """同步更新日志：追加上游新条目到本地仓库，再按系列合并重建页面。"""
    raw_entries = load_changelog_raw()

    if REBUILD_ONLY:
        print('[1/2] --rebuild-only: 跳过上游拉取，仅使用本地 changelog-raw.json')
    else:
        print('[1/2] 获取上游更新日志...')
        try:
            upstream = fetch_text(CHANGELOG_URL)
        except Exception as e:
            print('  ✗ 获取失败: {}'.format(e))
            return False
        upstream_versions = parse_changelog_versions(upstream)
        if not upstream_versions:
            print('  ✗ 未能解析版本信息')
            return False

        latest_ver, latest_date, _ = upstream_versions[0]
        print('  ✓ 最新版本: {} ({})'.format(latest_ver, latest_date))

        existing = {e['version'] for e in raw_entries}
        new_entries = [{'version': v, 'date': d, 'body': normalize_entry_body(b)}
                       for v, d, b in upstream_versions if v not in existing]
        if new_entries:
            print('  发现 {} 个新版本: {}'.format(
                len(new_entries), ', '.join(e['version'] for e in new_entries)))
            raw_entries.extend(new_entries)
            if not DRY_RUN:
                save_changelog_raw(raw_entries)
        else:
            print('  ✓ 上游无新版本')

    print('[2/2] 重建更新日志页面...')
    return rebuild_changelog_pages(raw_entries)


# ── 社区插件源同步 ──────────────────────────────────

def sync_community_sources():
    """Sync community plugin sources, building a combined community page.
    Returns (changed, community_plugins)."""
    all_plugins = []  # (source_index, plugin_dict)
    featured_idx = None

    for idx, src in enumerate(COMMUNITY_SOURCES):
        if src.get('featured'):
            featured_idx = idx
        print('[1/{}] 获取社区源: {}...'.format(len(COMMUNITY_SOURCES) * 2, src['name']))
        try:
            data = fetch_json(src['json_url'])
        except Exception as e:
            print('  ✗ 获取失败: {}'.format(e))
            continue

        source_name = data.get('name', src['name'])
        plugins_json = data.get('plugins', [])
        print('  ✓ 获取到 {} 个插件 (源: {})'.format(len(plugins_json), source_name))

        for entry in plugins_json:
            pid = entry.get('id', '')
            curated = src['curated'].get(pid, {})
            link = entry.get('homepage', '') or '{}/{}/'.format(src['raw_base'], entry.get('path', ''))

            if 'zh_name' in curated:
                zh_name = curated['zh_name']
                en_name = curated['en_name']
                zh_desc = curated.get('zh_desc', entry.get('description', ''))
                en_desc = curated.get('en_desc', entry.get('description', ''))
            else:
                path = entry.get('path', '')
                if path:
                    manifest_url = '{}/{}/manifest.json'.format(src['raw_base'], path)
                    try:
                        manifest = fetch_json(manifest_url)
                        zh_name = manifest.get('name', pid)
                        zh_desc = manifest.get('description', '')
                    except Exception:
                        zh_name = pid
                        zh_desc = ''
                else:
                    zh_name = pid
                    zh_desc = ''
                en_name = translate_to_english(zh_name) or pid
                en_desc = translate_to_english(zh_desc) if zh_desc else ''

            author = curated.get('author', entry.get('author', ''))

            # Build share link for community plugin
            src_repo = src.get('repo_url', src['homepage'])
            path = entry.get('path', '')
            version, icon_url, echo_ver = fetch_plugin_info(entry, raw_base=src['raw_base'])
            # Let build_share_link construct homepage from source_url + path
            share = build_share_link(pid, src_repo, path, version, None)

            all_plugins.append({
                'source_idx': idx,
                'id': pid,
                'sourceId': repo_to_source_id(src_repo),
                'zh_name': zh_name,
                'en_name': en_name,
                'zh_desc': zh_desc,
                'en_desc': en_desc,
                'author': author if author else src['name'],
                'link': link,
                'share': share,
                'version': version,
                'icon': icon_url,
                'echoMusicVersion': echo_ver,
                'tags': entry.get('tags', []),
            })
            print('  -> {}... {}'.format(pid, author or src['name']))

    # Build markdown
    print('[{}] 生成社区插件源页面...'.format(len(COMMUNITY_SOURCES) + 1))
    zh_list = build_community_page(all_plugins, 'zh', featured_idx)
    en_list = build_community_page(all_plugins, 'en', featured_idx)

    # Write files
    zh_path = os.path.join(DOCS_DIR, 'docs', 'guide', 'plugins', 'community.md')
    en_path = os.path.join(DOCS_DIR, 'docs', 'en', 'guide', 'plugins', 'community.md')

    changed = False
    for path, content, label in [(zh_path, zh_list, '中文'), (en_path, en_list, '英文')]:
        old = ''
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                old = f.read()
        if old.strip() == content.strip():
            print('  ✓ {} 社区插件源页面无变化'.format(label))
        else:
            changed = True
            if DRY_RUN:
                print('  ○ {} 社区插件源页面有变更 (dry-run, 跳过写入)'.format(label))
            else:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print('  ✓ {} 社区插件源页面已更新'.format(label))

    return changed, all_plugins


# ── 插件数据 JSON（供 PluginExplorer 组件构建时使用）──────────

STATS_API_URL = 'https://echomusic-plugin-marketplace.hoowhoami.dpdns.org/v1/plugins/stats'


def write_plugins_json(upstream_plugins, community_plugins):
    """Write .vitepress/data/plugins.json consumed by the PluginExplorer component.

    The component statically imports this file, so the full catalog is rendered
    at build time (SSG/SEO friendly); heat data is fetched client-side from the
    plugin marketplace stats API at runtime.
    """
    categories = [
        {'idx': i, 'zh': zh, 'en': en}
        for i, (zh, en) in enumerate(CATEGORIES)
    ]
    plugins = []
    for p in upstream_plugins:
        cat = p['category']
        in_range = 0 <= cat < len(CATEGORIES)
        plugins.append({
            'id': p['id'],
            'sourceId': p.get('sourceId', 'unknown'),
            'zhName': p['zh_name'],
            'enName': p['en_name'],
            'zhDesc': p['zh_desc'],
            'enDesc': p['en_desc'],
            'author': p['author'],
            'category': cat,
            'categoryZh': CATEGORIES[cat][0] if in_range else '',
            'categoryEn': CATEGORIES[cat][1] if in_range else '',
            'link': p.get('link') or '',
            'share': p.get('share', '#'),
            'version': p.get('version'),
            'icon': p.get('icon'),
            'iconExt': p.get('iconExt'),
            'echoMusicVersion': p.get('echoMusicVersion'),
            'tags': p.get('tags', []),
            'source': 'official',
            'sourceZh': '官方插件源',
            'sourceEn': 'Official Source',
        })
    for p in community_plugins:
        src = COMMUNITY_SOURCES[p['source_idx']]
        plugins.append({
            'id': p['id'],
            'sourceId': p.get('sourceId', 'unknown'),
            'zhName': p['zh_name'],
            'enName': p['en_name'],
            'zhDesc': p['zh_desc'],
            'enDesc': p['en_desc'],
            'author': p['author'],
            'category': None,
            'categoryZh': '',
            'categoryEn': '',
            'link': p.get('link') or '',
            'share': p.get('share', '#'),
            'version': p.get('version'),
            'icon': p.get('icon'),
            'iconExt': p.get('iconExt'),
            'echoMusicVersion': p.get('echoMusicVersion'),
            'tags': p.get('tags', []),
            'source': 'community',
            'sourceZh': src['name'],
            'sourceEn': src['en_name'],
        })

    data = {
        'generatedAt': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'statsApi': STATS_API_URL,
        'categories': categories,
        'plugins': plugins,
    }

    path = os.path.join(DOCS_DIR, '.vitepress', 'data', 'plugins.json')
    content = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    changed = True
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            changed = f.read() != content
    if changed and not DRY_RUN:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    if DRY_RUN:
        print('  ○ plugins.json {} (dry-run, 跳过写入)'.format('有变更' if changed else '无变化'))
    elif changed:
        print('  ✓ plugins.json 已更新 (官方 {} + 社区 {} 款)'.format(
            len(upstream_plugins), len(community_plugins)))
    else:
        print('  ✓ plugins.json 无变化')
    return changed


def build_community_page(plugins, lang='zh', featured_idx=None):
    """Build the community plugin sources page."""
    if lang == 'zh':
        header = (
            '---\n'
            'title: 社区插件源\n'
            '---\n\n'
            '# 社区插件源\n\n'
            '社区插件源是由社区开发者维护的第三方插件仓库。'
            '在 EchoMusic 的插件管理界面中添加来源地址即可接入。\n\n'
            '> ⚠️ **免责声明**：以下插件来自社区第三方源，非官方维护。'
            '安装前请仔细评估安全风险。\n\n'
        )
    else:
        header = (
            '---\n'
            'title: Community Plugin Sources\n'
            '---\n\n'
            '# Community Plugin Sources\n\n'
            'Community plugin sources are third-party plugin repositories maintained by community developers. '
            'Add a source URL in EchoMusic\'s plugin management panel to access them.\n\n'
            '> ⚠️ **Disclaimer**: The plugins listed below are from community third-party sources, NOT officially maintained. '
            'Please carefully assess security risks before installation.\n\n'
        )

    sections = [header]

    # Split plugins by source, order: featured first, then rest
    by_source = {}
    for p in plugins:
        sidx = p['source_idx']
        if sidx not in by_source:
            by_source[sidx] = []
        by_source[sidx].append(p)

    # Order: featured source first, then others preserving COMMUNITY_SOURCES order
    ordered_indices = []
    if featured_idx is not None and featured_idx in by_source:
        ordered_indices.append(featured_idx)
    for idx in range(len(COMMUNITY_SOURCES)):
        if idx in by_source and idx not in ordered_indices:
            ordered_indices.append(idx)

    for sidx in ordered_indices:
        src = COMMUNITY_SOURCES[sidx]
        src_plugins = by_source[sidx]
        src_plugins.sort(key=lambda p: p['id'].lower())

        src_name = src['name' if lang == 'zh' else 'en_name']
        src_link = src['homepage']
        is_featured = src.get('featured', False)

        if is_featured:
            icon = '⭐' if lang == 'zh' else '\u2b50'
        else:
            icon = ''

        if lang == 'zh':
            sections.append('## {icon} {name}\n'.format(icon=icon + ' ' if icon else '', name=src_name))
            sections.append('> {}：`{}`\n'.format('推荐 · 添加地址' if is_featured else '添加地址', src_link))
        else:
            sections.append('## {icon} {name}\n'.format(icon=icon + ' ' if icon else '', name=src_name))
            sections.append('> {}：`{}`\n'.format('Featured · Source URL' if is_featured else 'Source URL', src_link))

        if lang == 'zh':
            sections.append('| 插件 | 说明 | 作者 | 分享 |')
        else:
            sections.append('| Plugin | Description | Author | Share |')
        sections.append('|------|------|------|------|')

        for p in src_plugins:
            name = p['zh_name'] if lang == 'zh' else p['en_name']
            desc = p['zh_desc'] if lang == 'zh' else p['en_desc']
            share_label = '安装' if lang == 'zh' else 'Install'
            sections.append('| [{}]({}) | {} | {} | <span class="nowrap">[{}]({})</span> |'.format(
                name, p['link'], desc, p['author'], share_label, p.get('share', '#')
            ))

        sections.append('')

    # Footer navigation
    if lang == 'zh':
        sections.append('---\n')
        sections.append('- [← 返回插件市场](/plugins/)')
    else:
        sections.append('---\n')
        sections.append('- [← Back to Marketplace](/en/plugins/)')

    return '\n'.join(sections) + '\n'


# ── 主流程 ────────────────────────────────────────────

def main():
    # Ensure UTF-8 output on all platforms (including Windows)
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    print('=' * 60)
    print('EchoMusic Docs Auto-Sync')
    print('时间: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    if DRY_RUN:
        print('模式: DRY-RUN (不写入文件)')
    if ICONS_ONLY:
        print('模式: ICONS-ONLY (仅刷新图标本地镜像)')
    print('=' * 60)

    if ICONS_ONLY:
        sync_icons_only()
        sys.exit(0)

    if REBUILD_ONLY:
        print('模式: REBUILD-ONLY (跳过上游拉取，仅从本地仓库重建更新日志页面)')
        changed = sync_changelog()
        print()
        print('=' * 60)
        print('✓ 更新日志页面重建完成' if changed else '✓ 更新日志页面无需变更')
        sys.exit(0)

    # sync_plugins 只返回插件元数据列表；元数据变化体现在 plugins.json 的
    # 文件 diff（json_changed）里，不再单独报 changed
    upstream_plugins = sync_plugins()
    print()
    # 热度快照：按同步时的热度降序排列官方插件目录，使构建期/首屏直出的
    # 目录序即热度序（消除市场页打开时"先默认序、数据到达后跳变到热度序"）。
    # 快照只用于排序、不写入 plugins.json，避免分数微小变化造成无谓的文件 diff
    print('[heat] 获取热度快照...')
    heat_scores = fetch_heat_scores([(p['sourceId'], p['id']) for p in upstream_plugins])
    if heat_scores:
        for p in upstream_plugins:
            p['heatScore'] = heat_scores.get((p['sourceId'], p['id']))
        upstream_plugins.sort(key=lambda p: (
            p.get('heatScore') is None,
            -(p['heatScore'] or 0),
            p['category'],
            p['id'].lower(),
        ))
        print('  ✓ 已按热度快照排序（{} 个有分数，无分数的排尾部）'.format(
            sum(1 for p in upstream_plugins if p.get('heatScore') is not None)))
    print()
    community_changed, community_plugins = sync_community_sources()
    print()
    changelog_changed = sync_changelog()
    print()
    # 图标本地镜像需在写 plugins.json 之前执行：为插件元数据补 iconExt 字段
    icons_changed = download_plugin_icons(upstream_plugins)
    json_changed = write_plugins_json(upstream_plugins, community_plugins)

    print()
    print('=' * 60)
    if community_changed or changelog_changed or icons_changed or json_changed:
        print('✓ 检测到变更')
        if DRY_RUN:
            print('  (dry-run: 未实际写入)')
        sys.exit(0)
    else:
        print('✓ 所有内容已是最新')
        sys.exit(0)


if __name__ == '__main__':
    main()
