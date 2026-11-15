import { defineComponent, h, nextTick, watch } from 'vue'
import { useRoute } from 'vitepress'
import type { Theme } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import { enhanceAppWithTabs } from 'vitepress-plugin-tabs/client'
import { NolebaseInlineLinkPreviewPlugin } from '@nolebase/vitepress-plugin-inline-link-preview/client'
import {
  NolebaseEnhancedReadabilitiesMenu,
  NolebaseEnhancedReadabilitiesPlugin,
  NolebaseEnhancedReadabilitiesScreenMenu,
} from '@nolebase/vitepress-plugin-enhanced-readabilities/client'
import DownloadButton from '../components/DownloadButton.vue'
import PluginMarketplace from '../components/PluginMarketplace.vue'

import '@nolebase/vitepress-plugin-inline-link-preview/client/style.css'
import '@nolebase/vitepress-plugin-enhanced-readabilities/client/style.css'
import './style.css'

export default {
  extends: DefaultTheme,
  // 页面切换入场动画：SPA 路由变化时给内容区挂 page-enter 类（淡入上浮），
  // 导航栏与侧边栏保持静止；监听 relativePath 使同页锚点跳转不会重复触发，
  // 首次加载不播放，避免 SSR 内容先显示再闪动
  Layout: defineComponent({
    name: 'EchoMusicLayout',
    setup() {
      const route = useRoute()
      watch(() => route.data.relativePath, async () => {
        await nextTick()
        const el = document.querySelector('.VPContent')
        if (!el) return
        el.classList.remove('page-enter')
        void el.offsetWidth // 强制 reflow，连续跳转时动画也能重新触发
        el.classList.add('page-enter')
      })
      return () =>
        h(DefaultTheme.Layout, null, {
          'nav-bar-content-after': () => h(NolebaseEnhancedReadabilitiesMenu),
          'nav-screen-content-after': () => h(NolebaseEnhancedReadabilitiesScreenMenu),
        })
    },
  }),
  enhanceApp({ app }) {
    enhanceAppWithTabs(app)
    // 关闭阅读增强插件的布局切换动画：该插件默认在每次路由变化时给 body 加
    // VPNolebaseEnhancedReadabilitiesLayoutSwitchAnimated 类，令导航栏/侧边栏/内容区
    // 的 width、padding、max-width 带 0.5s 过渡，表现为切换页面时整页布局"滑动"一下
    app.use(NolebaseEnhancedReadabilitiesPlugin, {
      layoutSwitch: {
        disableAnimation: true,
        // 内容/页面宽度滑块组件在挂载约 1s 后也会触发一次同样的布局动画，一并关闭
        contentLayoutMaxWidth: { disableAnimation: true },
        pageLayoutMaxWidth: { disableAnimation: true },
      },
    })
    app.use(NolebaseInlineLinkPreviewPlugin)
    app.component('DownloadButton', DownloadButton)
    app.component('PluginMarketplace', PluginMarketplace)
  }
} satisfies Theme
