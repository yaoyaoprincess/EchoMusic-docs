#!/usr/bin/env python3
"""
EchoMusic Docs Auto-Sync Script
同步上游插件列表 (echo-plugins.json) 和更新日志 (CHANGELOG.md)。
检测变更后更新对应文档页面。

Usage: python scripts/sync-upstream.py [--dry-run]
"""

import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
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
        'name': '不知名插件源',
        'en_name': 'Anonymous Plugin Source',
        'homepage': 'https://github.com/yunzaiorg/kugou-sign',
        'json_url': 'https://raw.githubusercontent.com/yunzaiorg/kugou-sign/main/echo-plugins.json',
        'raw_base': 'https://raw.githubusercontent.com/yunzaiorg/kugou-sign/main',
        'featured': True,
        'curated': {
            'kugou-sign': {
                'zh_name': '签到',
                'en_name': 'KuGou Sign-in',
                'zh_desc': '酷狗概念版自动签到',
                'en_desc': 'Auto KuGou Concept Edition sign-in',
                'author': 'Anonymous',
            },
        },
    },
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
    'echo-history-plus': {
        'zh_name': '播放历史增强',
        'en_name': 'Playback History Plus',
        'zh_desc': '本地播放历史记录与统计分析，完全本地运行，无需登录',
        'en_desc': 'Local playback history recording and statistics analysis, fully offline, no login required',
        'author': 'yaoyaoprincess',
        'category': 4,
    },
    'xiaotoolkit': {
        'zh_name': '小功能',
        'en_name': 'XiaoToolkit',
        'zh_desc': '热门排序 + 隐藏歌单 + 歌词隐藏控制栏和工具栏 + 隐藏听歌识曲 + 顶部插件按钮 + 桌面特效',
        'en_desc': 'Hot sort, hide playlist, lyric area hide control & toolbar, hide music recognition, top plugin button, desktop effects',
        'json_author': 'Max8808',
        'category': 4,
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
        'link_prefix': 'https://github.com/xiaotian2333/EchoMusic-player-frontend',
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


def fetch_plugin_version(plugin_entry, raw_base=None):
    """Fetch plugin version from manifest.json. Returns version string or 'unknown'.
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
        return 'unknown'

    try:
        manifest = fetch_json(manifest_url)
        return manifest.get('version', 'unknown')
    except Exception:
        return 'unknown'


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
    version = fetch_plugin_version(plugin_entry)
    homepage = plugin_entry.get('homepage', '')
    share_link = build_share_link(plugin_id, source_url, path, version, homepage or None)

    return {
        'id': plugin_id,
        'zh_name': zh_name,
        'en_name': en_name,
        'zh_desc': zh_desc,
        'en_desc': en_desc,
        'author': author if author else '',
        'category': category,
        'link': link,
        'share': share_link,
    }


def build_plugin_list_md(plugins, lang='zh'):
    """Build the plugin list markdown page for given language."""
    total = len(plugins)

    if lang == 'zh':
        header = (
            '---\n'
            'title: 插件列表\n'
            '---\n\n'
            '# 📋 插件列表\n\n'
            '以下是官方插件源中已收录的插件（共 {} 款）：\n'
        ).format(total)
    else:
        header = (
            '---\n'
            'title: Plugin List\n'
            '---\n\n'
            '# 📋 Plugin List\n\n'
            'Below are plugins available in the official plugin source ({} total):\n'
        ).format(total)

    # Group by category
    grouped = {}
    for p in plugins:
        cat_idx = p['category']
        grouped.setdefault(cat_idx, []).append(p)

    sections = [header]

    for cat_idx in range(len(CATEGORIES)):
        if cat_idx not in grouped:
            continue
        cat_plugins = grouped[cat_idx]
        zh_emoji, zh_name = CATEGORIES[cat_idx][0].split(' ', 1)
        en_name = CATEGORIES[cat_idx][1]

        if lang == 'zh':
            cat_title = '## {} {}\n'.format(CATEGORIES[cat_idx][0].split()[0], zh_name)
        else:
            cat_title = '## {} {}\n'.format(zh_emoji, en_name)

        sections.append(cat_title)

        if lang == 'zh':
            sections.append('| 插件 | 说明 | 作者 | 分享 |')
        else:
            sections.append('| Plugin | Description | Author | Share |')
        sections.append('|------|------|------|------|')

        for p in cat_plugins:
            name = p['zh_name'] if lang == 'zh' else p['en_name']
            desc = p['zh_desc'] if lang == 'zh' else p['en_desc']
            share_label = '安装' if lang == 'zh' else 'Install'
            sections.append('| [{}]({}) | {} | {} | <span class="nowrap">[{}]({})</span> |'.format(
                name, p['link'], desc, p['author'], share_label, p.get('share', '#')
            ))

    # Footer navigation
    sections.append('\n---\n')
    if lang == 'zh':
        sections.append('- [← 安装插件](./install)')
        sections.append('- [⚙️ 管理与安全 →](./manage)')
    else:
        sections.append('- [← Installing Plugins](./install)')
        sections.append('- [⚙️ Management & Safety →](./manage)')

    return '\n'.join(sections) + '\n'


# ── 插件同步 ──────────────────────────────────────────

def sync_plugins():
    """Sync plugin list from upstream echo-plugins.json."""
    print('[1/4] 获取插件源索引...')
    try:
        data = fetch_json(PLUGINS_JSON_URL)
    except Exception as e:
        print('  ✗ 获取失败: {}'.format(e))
        return False

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
        elif pid == 'echo-history-plus':
            link = 'https://github.com/yaoyaoprincess/echo-history-plus'
        else:
            link = 'https://github.com/yaoyaoprincess/{}'.format(pid)

        author = curated.get('author') or curated.get('json_author') or ''
        extra = {
            'id': pid,
            'zh_name': curated['zh_name'],
            'en_name': curated['en_name'],
            'zh_desc': curated['zh_desc'],
            'en_desc': curated['en_desc'],
            'author': author,
            'category': curated['category'],
            'link': link,
        }
        upstream_plugins.append(extra)
        print('  + {} (仅文档收录)'.format(pid))

    # Sort: by category, then by ID
    upstream_plugins.sort(key=lambda p: (p['category'], p['id'].lower()))

    # Generate markdown
    print('[3/4] 生成插件列表...')
    zh_list = build_plugin_list_md(upstream_plugins, 'zh')
    en_list = build_plugin_list_md(upstream_plugins, 'en')

    # Compare with existing
    print('[4/4] 对比现有文件...')
    zh_path = os.path.join(DOCS_DIR, 'docs', 'guide', 'plugins', 'list.md')
    en_path = os.path.join(DOCS_DIR, 'docs', 'en', 'guide', 'plugins', 'list.md')

    changed = False
    for path, content, label in [(zh_path, zh_list, '中文'), (en_path, en_list, '英文')]:
        old = ''
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                old = f.read()
        if old.strip() == content.strip():
            print('  ✓ {} 插件列表无变化'.format(label))
        else:
            changed = True
            if DRY_RUN:
                print('  ○ {} 插件列表有变更 (dry-run, 跳过写入)'.format(label))
            else:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print('  ✓ {} 插件列表已更新'.format(label))

    return changed


# ── 更新日志同步 ──────────────────────────────────────

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


def translate_changelog_body(body):
    """Translate a changelog version body from Chinese to English using Google Translate.
    Preserves version headers and markdown structure.
    Returns None if deep_translator is unavailable."""
    try:
        from deep_translator import GoogleTranslator
    except ImportError:
        print('  ⚠ deep_translator 未安装，跳过翻译')
        return None

    lines = body.split('\n')
    if not lines:
        return body

    # Extract and preserve version header line
    header_line = ''
    content_start = 0
    if lines[0].startswith('## ['):
        header_line = lines[0]
        content_start = 1

    # Build body content (everything after the header)
    body_content = '\n'.join(lines[content_start:]).strip()
    if not body_content or not any('\u4e00' <= c <= '\u9fff' for c in body_content):
        return body

    # Translate in chunks (Google Translate endpoint ~5000 char limit)
    max_chunk = 4000
    paragraphs = re.split(r'(\n\n+)', body_content)
    translated_parts = []
    current_chunk = []
    current_len = 0

    for para in paragraphs:
        if current_len + len(para) > max_chunk and current_chunk:
            chunk_text = ''.join(current_chunk)
            try:
                translated = GoogleTranslator(source='zh-CN', target='en').translate(chunk_text)
                translated_parts.append(translated)
            except Exception as e:
                print('  ⚠ 翻译块失败，保留原文: {}'.format(e))
                return None
            current_chunk = []
            current_len = 0
        current_chunk.append(para)
        current_len += len(para)

    if current_chunk:
        chunk_text = ''.join(current_chunk)
        try:
            translated = GoogleTranslator(source='zh-CN', target='en').translate(chunk_text)
            translated_parts.append(translated)
        except Exception as e:
            print('  ⚠ 翻译块失败，保留原文: {}'.format(e))
            return None

    translated_body = ''.join(translated_parts)

    if header_line:
        return header_line + '\n' + translated_body
    return translated_body


def sync_changelog():
    """Sync changelog from upstream CHANGELOG.md."""
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

    print('[2/2] 处理更新日志...')
    changed = False

    # ── 中文 changelog ──
    zh_path = os.path.join(DOCS_DIR, 'docs', 'changelog', 'index.md')
    if os.path.exists(zh_path):
        with open(zh_path, 'r', encoding='utf-8') as f:
            zh_old = f.read()

        # Use regex to extract existing version numbers
        existing_versions = set(re.findall(r'^## \[([^\]]+)\]', zh_old, re.MULTILINE))
        zh_new_entries = []
        for ver, date, body in upstream_versions:
            if ver not in existing_versions:
                zh_new_entries.append((ver, date, body))
            else:
                break

        if zh_new_entries:
            print('  发现 {} 个新版本: {}'.format(
                len(zh_new_entries), ', '.join(v[0] for v in zh_new_entries)
            ))
            zh_section = '\n\n'.join(body for _, _, body in zh_new_entries)
            header_end = zh_old.find('## [')
            if header_end == -1:
                found = zh_old.rfind('\n\n')
                header_end = found + 2 if found != -1 else len(zh_old)
            zh_new_content = zh_old[:header_end] + zh_section + '\n\n' + zh_old[header_end:]

            if not DRY_RUN:
                with open(zh_path, 'w', encoding='utf-8') as f:
                    f.write(zh_new_content)
                print('  ✓ 中文更新日志已更新 ({})'.format(
                    ', '.join(v[0] for v in zh_new_entries)))
            else:
                print('  ○ 中文更新日志有变更 (dry-run)')
            changed = True
        else:
            print('  ✓ 中文更新日志已是最新')
    else:
        print('  ✗ 中文更新日志文件不存在: {}'.format(zh_path))

    # ── 英文 changelog ──
    # 使用 Google Translate 自动翻译上游中文 CHANGELOG
    # 如果 deep_translator 不可用则回退到翻译提醒标记
    en_changelog_path = os.path.join(DOCS_DIR, 'docs', 'en', 'changelog', 'index.md')
    try:
        if os.path.exists(en_changelog_path):
            with open(en_changelog_path, 'r', encoding='utf-8') as f:
                en_old = f.read()

            existing_en_versions = set(re.findall(r'^## \[([^\]]+)\]', en_old, re.MULTILINE))
            en_new_entries = []
            for ver, date, body in upstream_versions:
                if ver not in existing_en_versions:
                    en_new_entries.append((ver, date, body))
                else:
                    break

            if en_new_entries:
                print('  发现 {} 个新版本需要翻译: {}'.format(
                    len(en_new_entries), ', '.join(v[0] for v in en_new_entries)
                ))

                # Attempt auto-translation
                en_sections = []
                translation_ok = True
                for ver, date, body in en_new_entries:
                    print('  -> 翻译 {}... '.format(ver), end='')
                    translated = translate_changelog_body(body)
                    if translated is None:
                        print('✗')
                        translation_ok = False
                        break
                    en_sections.append(translated)
                    print('✓')

                if translation_ok and en_sections:
                    # Insert translated entries
                    en_section_text = '\n\n'.join(en_sections)
                    first_version_pos = en_old.find('## [')
                    if first_version_pos == -1:
                        title_pos = en_old.find('# Changelog')
                        if title_pos != -1:
                            nl = en_old.find('\n', title_pos)
                            first_version_pos = nl + 1 if nl != -1 else len(en_old)
                        else:
                            first_version_pos = len(en_old)

                    # Remove stale reminder blocks
                    en_old_clean = re.sub(
                        r'\n*> \*\*🔔 New versions detected[^\n]*\n(?:> [^\n]*\n)*',
                        '\n', en_old
                    )

                    en_new = en_old_clean[:first_version_pos] + en_section_text + '\n\n' + en_old_clean[first_version_pos:]

                    if not DRY_RUN:
                        with open(en_changelog_path, 'w', encoding='utf-8') as f:
                            f.write(en_new)
                        print('  ✓ 英文更新日志已翻译并更新')
                    else:
                        print('  ○ 英文更新日志将翻译更新 (dry-run)')
                    changed = True
                else:
                    # Fallback: insert reminder block
                    print('  ⚠ 自动翻译不可用，回退到翻译提醒')
                    en_missing = [v[0] for v in en_new_entries]
                    todo_block = '\n\n> **🔔 New versions detected: {}**\n> This section is auto-generated from the upstream CHANGELOG (Chinese). Please translate manually or use the Chinese changelog as reference.\n>'.format(', '.join(en_missing))

                    first_version_pos = en_old.find('## [')
                    if first_version_pos == -1:
                        title_pos = en_old.find('# Changelog')
                        if title_pos == -1:
                            first_version_pos = 0
                        else:
                            nl = en_old.find('\n', title_pos)
                            first_version_pos = nl + 1 if nl != -1 else len(en_old)

                    if first_version_pos > 0 and todo_block not in en_old:
                        en_new = en_old[:first_version_pos] + todo_block + '\n\n' + en_old[first_version_pos:]
                        if not DRY_RUN:
                            with open(en_changelog_path, 'w', encoding='utf-8') as f:
                                f.write(en_new)
                            print('  ⚠ 英文更新日志已标记待翻译 ({})'.format(', '.join(en_missing)))
                            changed = True
                        else:
                            print('  ○ 英文更新日志将标记待翻译 ({})'.format(', '.join(en_missing)))
            else:
                print('  ✓ 英文更新日志已是最新')
        else:
            print('  ✗ 英文更新日志文件不存在: {}'.format(en_changelog_path))
    except Exception as e:
        print('  ✗ 英文更新日志处理失败: {}'.format(e))

    return changed


# ── 社区插件源同步 ──────────────────────────────────

def sync_community_sources():
    """Sync community plugin sources, building a combined community page."""
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
            version = fetch_plugin_version(entry, raw_base=src['raw_base'])
            # Let build_share_link construct homepage from source_url + path
            share = build_share_link(pid, src_repo, path, version, None)

            all_plugins.append({
                'source_idx': idx,
                'id': pid,
                'zh_name': zh_name,
                'en_name': en_name,
                'zh_desc': zh_desc,
                'en_desc': en_desc,
                'author': author if author else src['name'],
                'link': link,
                'share': share,
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
        sections.append('- [← 返回插件列表](./list)')
    else:
        sections.append('---\n')
        sections.append('- [← Back to Plugin List](./list)')

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
    print('=' * 60)

    plugin_changed = sync_plugins()
    print()
    community_changed = sync_community_sources()
    print()
    changelog_changed = sync_changelog()

    print()
    print('=' * 60)
    if plugin_changed or community_changed or changelog_changed:
        print('✓ 检测到变更')
        if DRY_RUN:
            print('  (dry-run: 未实际写入)')
        sys.exit(0)
    else:
        print('✓ 所有内容已是最新')
        sys.exit(0)


if __name__ == '__main__':
    main()
