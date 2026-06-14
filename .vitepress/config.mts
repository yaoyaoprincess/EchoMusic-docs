import { defineConfig } from 'vitepress'
import { MermaidPlugin, MermaidMarkdown } from "vitepress-plugin-mermaid"
import { tabsMarkdownPlugin } from "vitepress-plugin-tabs"
import { InlineLinkPreviewElementTransform } from '@nolebase/vitepress-plugin-inline-link-preview/markdown-it'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  base: '/',
  title: "EchoMusic Docs",
  description: "EchoMusic Usage Guide",
  ignoreDeadLinks: 'localhostLinks',
  locales: {
    root: {
      label: '简体中文',
      lang: 'zh-CN',
      title: 'EchoMusic 文档中心',
      description: 'EchoMusic 使用指南',
      themeConfig: {
        editLink: {
          pattern: "https://github.com/yaoyaoprincess/EchoMusic-docs/edit/main/:path",
          text: "在 GitHub 上编辑此页"
        },
        lastUpdated: {
          text: "最后更新",
          formatOptions: {
            dateStyle: "short",
            timeStyle: "short",
          },
        },
        nav: [
          { text: '首页', link: '/' },
          { text: '功能特性', link: '/features/' },
          {
            text: '使用指南',
            items: [
              { text: '快速开始', link: '/guide/getting-started' },
              { text: '播放控制', link: '/guide/playback' },
              { text: '发现音乐', link: '/guide/music-discovery' },
              { text: '搜索', link: '/guide/search' },
              { text: '歌词系统', link: '/guide/lyrics' },
              { text: '音频设置', link: '/guide/audio' },
              { text: '私人FM', link: '/guide/personal-fm' },
              { text: '听歌识曲', link: '/guide/music-recognition' },
              { text: '歌曲详情', link: '/guide/song-detail' },
              { text: '个性化设置', link: '/guide/settings' },
              { text: '常见问题', link: '/guide/faq' },
              { text: '插件系统', link: '/guide/plugins' },
            ]
          },
          {
            text: '开发文档',
            items: [
              { text: '开发概览', link: '/develop/' },
              { text: '项目架构', link: '/develop/architecture' },
              { text: '项目结构', link: '/develop/project-structure' },
              { text: '本地开发', link: '/develop/local-dev' },
              { text: '原生模块', link: '/develop/native-addons' },
              { text: '编译构建', link: '/develop/build' },
              { text: '贡献指南', link: '/develop/contributing' },
              { text: 'API 参考', link: '/develop/api' },
              { text: '插件开发', link: '/develop/plugin-dev/' },
            ]
          },
          { text: '社区', link: '/community/' },
          { text: '更新日志', link: '/changelog/' },
          {
            text: 'GitHub',
            items: [
              { text: 'EchoMusic', link: 'https://github.com/hoowhoami/EchoMusic' },
              { text: 'EchoMusicPlugins', link: 'https://github.com/hoowhoami/EchoMusicPlugins' },
              { text: 'EchoMusic Docs', link: 'https://github.com/yaoyaoprincess/EchoMusic-docs' },
            ]
          },
        ],
        sidebar: {
          '/guide/': [
            {
              text: '📖 使用指南',
              collapsed: false,
              items: [
                { text: '快速开始', link: '/guide/getting-started' },
                { text: '播放控制', link: '/guide/playback' },
                { text: '发现音乐', link: '/guide/music-discovery' },
                { text: '搜索', link: '/guide/search' },
                { text: '歌词系统', link: '/guide/lyrics' },
                { text: '音频设置', link: '/guide/audio' },
                { text: '私人 FM', link: '/guide/personal-fm' },
                { text: '听歌识曲', link: '/guide/music-recognition' },
                { text: '歌曲详情与评论', link: '/guide/song-detail' },
                { text: '个性化设置', link: '/guide/settings' },
                { text: '常见问题', link: '/guide/faq' },
                { text: '插件系统', link: '/guide/plugins' },
              ]
            },
          ],
          '/develop/': [
            {
              text: '🛠️ 开发指南',
              collapsed: false,
              items: [
                { text: '开发概览', link: '/develop/' },
                { text: '项目架构', link: '/develop/architecture' },
                { text: '项目结构', link: '/develop/project-structure' },
                { text: '本地开发环境', link: '/develop/local-dev' },
                { text: '原生模块 (Rust NAPI)', link: '/develop/native-addons' },
                { text: '编译与构建', link: '/develop/build' },
                { text: '贡献指南', link: '/develop/contributing' },
                { text: 'API 参考', link: '/develop/api' },
                { text: '插件开发', link: '/develop/plugin-dev/' },
              ]
            },
            {
              text: '🔌 插件开发',
              collapsed: false,
              items: [
                { text: '插件开发概览', link: '/develop/plugin-dev/' },
                { text: '快速开始', link: '/develop/plugin-dev/getting-started' },
                { text: 'Manifest 配置参考', link: '/develop/plugin-dev/manifest' },
                { text: '上下文 API 参考', link: '/develop/plugin-dev/context-api' },
                { text: 'UI 扩展指南', link: '/develop/plugin-dev/ui-extension' },
                { text: '播放器与音频', link: '/develop/plugin-dev/player-audio' },
                { text: '文件存储与事件', link: '/develop/plugin-dev/filesystem-events' },
                { text: '发布与分发', link: '/develop/plugin-dev/publishing' },
              ]
            },
          ],
        },
      }
    },
    en: {
      label: 'English',
      lang: 'en-US',
      title: 'EchoMusic Docs',
      description: 'EchoMusic Usage Guide',
      link: '/en/',
      themeConfig: {
        editLink: {
          pattern: "https://github.com/yaoyaoprincess/EchoMusic-docs/edit/main/:path",
          text: "Edit this page on GitHub"
        },
        lastUpdated: {
          text: "Last updated",
          formatOptions: {
            dateStyle: "short",
            timeStyle: "short",
          },
        },
        nav: [
          { text: 'Home', link: '/en/' },
          { text: 'Features', link: '/en/features/' },
          {
            text: 'User Guide',
            items: [
              { text: 'Getting Started', link: '/en/guide/getting-started' },
              { text: 'Playback', link: '/en/guide/playback' },
              { text: 'Music Discovery', link: '/en/guide/music-discovery' },
              { text: 'Search', link: '/en/guide/search' },
              { text: 'Lyrics', link: '/en/guide/lyrics' },
              { text: 'Audio Settings', link: '/en/guide/audio' },
              { text: 'Personal FM', link: '/en/guide/personal-fm' },
              { text: 'Music Recognition', link: '/en/guide/music-recognition' },
              { text: 'Song Details', link: '/en/guide/song-detail' },
              { text: 'Preferences', link: '/en/guide/settings' },
              { text: 'FAQ', link: '/en/guide/faq' },
              { text: 'Plugin System', link: '/en/guide/plugins' },
            ]
          },
          {
            text: 'Development',
            items: [
              { text: 'Overview', link: '/en/develop/' },
              { text: 'Architecture', link: '/en/develop/architecture' },
              { text: 'Project Structure', link: '/en/develop/project-structure' },
              { text: 'Local Dev', link: '/en/develop/local-dev' },
              { text: 'Native Addons', link: '/en/develop/native-addons' },
              { text: 'Build', link: '/en/develop/build' },
              { text: 'Contributing', link: '/en/develop/contributing' },
              { text: 'API Reference', link: '/en/develop/api' },
              { text: 'Plugin Dev', link: '/en/develop/plugin-dev/' },
            ]
          },
          { text: 'Community', link: '/en/community/' },
          { text: 'Changelog', link: '/en/changelog/' },
          {
            text: 'GitHub',
            items: [
              { text: 'EchoMusic', link: 'https://github.com/hoowhoami/EchoMusic' },
              { text: 'EchoMusicPlugins', link: 'https://github.com/hoowhoami/EchoMusicPlugins' },
              { text: 'EchoMusic Docs', link: 'https://github.com/yaoyaoprincess/EchoMusic-docs' },
            ]
          },
        ],
        sidebar: {
          '/en/guide/': [
            {
              text: '📖 User Guide',
              collapsed: false,
              items: [
                { text: 'Getting Started', link: '/en/guide/getting-started' },
                { text: 'Playback', link: '/en/guide/playback' },
                { text: 'Music Discovery', link: '/en/guide/music-discovery' },
                { text: 'Search', link: '/en/guide/search' },
                { text: 'Lyrics', link: '/en/guide/lyrics' },
                { text: 'Audio Settings', link: '/en/guide/audio' },
                { text: 'Personal FM', link: '/en/guide/personal-fm' },
                { text: 'Music Recognition', link: '/en/guide/music-recognition' },
                { text: 'Song Details & Comments', link: '/en/guide/song-detail' },
                { text: 'Preferences', link: '/en/guide/settings' },
                { text: 'FAQ', link: '/en/guide/faq' },
                { text: 'Plugin System', link: '/en/guide/plugins' },
              ]
            },
          ],
          '/en/develop/': [
            {
              text: '🛠️ Development',
              collapsed: false,
              items: [
                { text: 'Overview', link: '/en/develop/' },
                { text: 'Architecture', link: '/en/develop/architecture' },
                { text: 'Project Structure', link: '/en/develop/project-structure' },
                { text: 'Local Dev Setup', link: '/en/develop/local-dev' },
                { text: 'Native Addons (Rust NAPI)', link: '/en/develop/native-addons' },
                { text: 'Build & Package', link: '/en/develop/build' },
                { text: 'Contributing', link: '/en/develop/contributing' },
                { text: 'API Reference', link: '/en/develop/api' },
                { text: 'Plugin Development', link: '/en/develop/plugin-dev/' },
              ]
            },
            {
              text: '🔌 Plugin Development',
              collapsed: false,
              items: [
                { text: 'Overview', link: '/en/develop/plugin-dev/' },
                { text: 'Getting Started', link: '/en/develop/plugin-dev/getting-started' },
                { text: 'Manifest Reference', link: '/en/develop/plugin-dev/manifest' },
                { text: 'Context API Reference', link: '/en/develop/plugin-dev/context-api' },
                { text: 'UI Extension Guide', link: '/en/develop/plugin-dev/ui-extension' },
                { text: 'Player & Audio', link: '/en/develop/plugin-dev/player-audio' },
                { text: 'Filesystem & Events', link: '/en/develop/plugin-dev/filesystem-events' },
                { text: 'Publishing', link: '/en/develop/plugin-dev/publishing' },
              ]
            },
          ],
        },
      }
    }
  },
  head: [
    ['link', { rel: 'icon', href: '/icon.ico' }]
  ],
  themeConfig: {
    search: {
      provider: 'local',
    },
    outline: [2, 4],
    socialLinks: [
      { icon: 'github', link: 'https://github.com/hoowhoami/EchoMusic' },
      { 
        icon: {
          svg: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/></svg>'
        },
        link: 'https://t.me/+H9vpkAJrDlViZjU1'
      }
    ],
  },
  markdown: {
    config(md) {
      md.use(tabsMarkdownPlugin);
      md.use(MermaidMarkdown);
      md.use(InlineLinkPreviewElementTransform);
    },
  },
  vite: {
    plugins: [MermaidPlugin()],
    optimizeDeps: {
      include: ['mermaid'],
      exclude: [
        '@nolebase/vitepress-plugin-inline-link-preview/client',
        '@nolebase/vitepress-plugin-enhanced-readabilities/client',
        '@nolebase/ui',
      ],
    },
    ssr: {
      noExternal: [
        'mermaid',
        '@nolebase/vitepress-plugin-inline-link-preview',
        '@nolebase/vitepress-plugin-enhanced-readabilities',
        '@nolebase/ui',
      ],
    },
  },
})
