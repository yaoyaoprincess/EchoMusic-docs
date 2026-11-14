import { h } from 'vue'
import type { Theme } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import { enhanceAppWithTabs } from 'vitepress-plugin-tabs/client'
import { NolebaseInlineLinkPreviewPlugin } from '@nolebase/vitepress-plugin-inline-link-preview/client'
import {
  NolebaseEnhancedReadabilitiesMenu,
  NolebaseEnhancedReadabilitiesScreenMenu,
} from '@nolebase/vitepress-plugin-enhanced-readabilities/client'
import DownloadButton from '../components/DownloadButton.vue'
import PluginMarketplace from '../components/PluginMarketplace.vue'

import '@nolebase/vitepress-plugin-inline-link-preview/client/style.css'
import '@nolebase/vitepress-plugin-enhanced-readabilities/client/style.css'
import './style.css'

export default {
  extends: DefaultTheme,
  Layout: () => {
    return h(DefaultTheme.Layout, null, {
      'nav-bar-content-after': () => h(NolebaseEnhancedReadabilitiesMenu),
      'nav-screen-content-after': () => h(NolebaseEnhancedReadabilitiesScreenMenu),
    })
  },
  enhanceApp({ app }) {
    enhanceAppWithTabs(app)
    app.use(NolebaseInlineLinkPreviewPlugin)
    app.component('DownloadButton', DownloadButton)
    app.component('PluginMarketplace', PluginMarketplace)
    if (typeof window !== 'undefined') {
      // 临时调试：捕获插件组件的渲染错误（定位后移除）
      app.config.errorHandler = (err, _inst, info) => {
        const w = window as unknown as { __vueErrs?: string[] }
        w.__vueErrs = w.__vueErrs || []
        w.__vueErrs.push(String((err as Error)?.stack || err) + ' || ' + info)
      }
    }
  }
} satisfies Theme
