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
import urllib.request
import urllib.error
from datetime import datetime

# ── 配置 ──────────────────────────────────────────────

DOCS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGINS_JSON_URL = 'https://raw.githubusercontent.com/hoowhoami/EchoMusicPlugins/main/echo-plugins.json'
CHANGELOG_URL = 'https://raw.githubusercontent.com/hoowhoami/EchoMusic/main/CHANGELOG.md'
PLUGINS_REPO_RAW = 'https://raw.githubusercontent.com/hoowhoami/EchoMusicPlugins/main'

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
        'zh_desc': '热门排序 + 隐藏歌单 + 歌词隐藏控制栏 + 隐藏听歌识曲 + 顶部插件按钮 + 桌面特效',
        'en_desc': 'Hot sort, hide playlist, lyric area hide control bar, hide music recognition, top plugin button, desktop effects',
        'json_author': '张三',
        'category': 4,
    },
}


# ── 工具函数 ──────────────────────────────────────────

def fetch_json(url):
    """Fetch and parse JSON from URL."""
    req = urllib.request.Request(url, headers={'User-Agent': 'EchoMusic-docs-sync/1.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))


def fetch_text(url):
    """Fetch raw text from URL."""
    req = urllib.request.Request(url, headers={'User-Agent': 'EchoMusic-docs-sync/1.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode('utf-8')


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


def get_plugin_meta(plugin_entry):
    """Get full metadata for a plugin from echo-plugins.json entry.
    Returns dict with id, zh_name, en_name, zh_desc, en_desc, author, category, link.
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
        # If JSON name contains Chinese, use plugin_id as English fallback
        if any('\u4e00' <= c <= '\u9fff' for c in json_name):
            en_name = plugin_id
            en_desc = '(No English description yet) ' + json_desc
        else:
            en_name = json_name
            en_desc = json_desc
    else:
        # New plugin without any metadata - fetch manifest
        manifest_name, manifest_desc, _ = fetch_manifest(plugin_entry)
        zh_name = manifest_name or plugin_id
        en_name = manifest_name or plugin_id
        zh_desc = manifest_desc or ''
        en_desc = manifest_desc or ''

    # Category
    if 'category' in curated:
        category = curated['category']
    else:
        tags = plugin_entry.get('tags', [])
        category = categorize_by_tags(tags)

    return {
        'id': plugin_id,
        'zh_name': zh_name,
        'en_name': en_name,
        'zh_desc': zh_desc,
        'en_desc': en_desc,
        'author': author if author else '',
        'category': category,
        'link': link,
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
            sections.append('| 插件 | 说明 | 作者 |')
        else:
            sections.append('| Plugin | Description | Author |')
        sections.append('|------|------|------|')

        for p in cat_plugins:
            name = p['zh_name'] if lang == 'zh' else p['en_name']
            desc = p['zh_desc'] if lang == 'zh' else p['en_desc']
            sections.append('| [{}]({}) | {} | {} |'.format(
                name, p['link'], desc, p['author']
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


def sync_changelog():
    """Sync changelog from upstream CHANGELOG.md."""
    print('[1/3] 获取上游更新日志...')
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

    # Read existing changelog (zh)
    changelog_path = os.path.join(DOCS_DIR, 'docs', 'changelog', 'index.md')
    if not os.path.exists(changelog_path):
        print('  ✗ 文件不存在: {}'.format(changelog_path))
        return False

    with open(changelog_path, 'r', encoding='utf-8') as f:
        existing = f.read()

    # Check if latest version already exists
    if '## [{}]'.format(latest_ver) in existing:
        print('  ✓ 版本 {} 已存在，无需更新'.format(latest_ver))
        return False

    # Find which versions are new
    new_entries = []
    for ver, date, body in upstream_versions:
        if '## [{}]'.format(ver) not in existing:
            new_entries.append((ver, date, body))
        else:
            break

    if not new_entries:
        print('  ✓ 无新版本')
        return False

    print('[2/3] 发现 {} 个新版本: {}'.format(
        len(new_entries), ', '.join(v[0] for v in new_entries)
    ))

    # Build new entries markdown
    new_section = '\n\n'.join(body for _, _, body in new_entries)

    print('[3/3] 写入文件...')
    changed = False

    # ── 中文 changelog ──
    if os.path.exists(changelog_path):
        with open(changelog_path, 'r', encoding='utf-8') as f:
            old = f.read()

        header_end = old.find('## [')
        if header_end == -1:
            header_end = old.rfind('\n\n') + 2

        new_content = old[:header_end] + new_section + '\n\n' + old[header_end:]

        if not DRY_RUN:
            with open(changelog_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print('  ✓ 中文更新日志已更新')
        else:
            print('  ○ 中文更新日志有变更 (dry-run)')
        changed = True

    # ── 英文 changelog ──
    # 上游 CHANGELOG.md 是中文，直接写入英文页面会导致中文内容。
    # 英文版本需人工翻译后手动更新，此处只插入 TODO 标记。
    en_changelog_path = os.path.join(DOCS_DIR, 'docs', 'en', 'changelog', 'index.md')
    if os.path.exists(en_changelog_path):
        with open(en_changelog_path, 'r', encoding='utf-8') as f:
            en_old = f.read()

        new_versions_str = ', '.join(v[0] for v in new_entries)
        todo_block = '\n\n> **🔔 New versions detected: {}**\n> This section is auto-generated from the upstream CHANGELOG (Chinese). Please translate manually or use the Chinese changelog as reference.\n>'.format(new_versions_str)

        # Insert TODO after the first header line
        first_header_line = en_old.find('\n', en_old.find('# Changelog')) + 1
        if first_header_line > 0:
            # put after the header block (before first ## [)
            insert_pos = en_old.find('## [')
            if insert_pos == -1:
                insert_pos = first_header_line

            if todo_block not in en_old:
                en_new = en_old[:insert_pos] + todo_block + '\n\n' + en_old[insert_pos:]
                if not DRY_RUN:
                    with open(en_changelog_path, 'w', encoding='utf-8') as f:
                        f.write(en_new)
                    print('  ⚠ 英文更新日志已标记待翻译 ({})'.format(new_versions_str))
                else:
                    print('  ○ 英文更新日志将标记待翻译 ({})'.format(new_versions_str))
            else:
                print('  ✓ 英文更新日志已有待翻译标记')

    return changed


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
    changelog_changed = sync_changelog()

    print()
    print('=' * 60)
    if plugin_changed or changelog_changed:
        print('✓ 检测到变更')
        if DRY_RUN:
            print('  (dry-run: 未实际写入)')
        sys.exit(0)
    else:
        print('✓ 所有内容已是最新')
        sys.exit(0)


if __name__ == '__main__':
    main()
