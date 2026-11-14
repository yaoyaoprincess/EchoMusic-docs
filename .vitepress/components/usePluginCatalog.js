import { computed, onMounted, ref } from 'vue'
import { useData } from 'vitepress'
import catalog from '../data/plugins.json'

const HEAT_CACHE_KEY = 'vitepress-plugin-heat-v1'
const HEAT_TTL = 10 * 60 * 1000
const HEAT_TIMEOUT_MS = 8000

// 插件市场仅展示官方源插件（社区源插件见"社区插件源"页面）
const officialPlugins = catalog.plugins.filter((p) => p.source === 'official')

/**
 * 插件目录共享逻辑：目录数据、搜索/分类/排序状态、热度数据加载
 * （sessionStorage 缓存 10 分钟 + 8s 超时 + 失败重试一次）。
 * 供 PluginMarketplace（卡片视图）使用；仅展示官方源插件。
 */
export function usePluginCatalog() {
  const { lang } = useData()
  const isZh = computed(() => !(lang.value || '').toLowerCase().startsWith('en'))

  const query = ref('')
  const category = ref('all')
  const sortKey = ref('heat') // 热度榜：默认按热度排序（数据到达前等价于目录序）
  const heatState = ref('loading')
  const heatMap = ref({})

  function heatKey(p) {
    return p.sourceId + '|' + p.id
  }
  function statsOf(p) {
    return heatState.value === 'ok' ? heatMap.value[heatKey(p)] : null
  }
  function heatScore(p) {
    const s = statsOf(p)
    return s ? s.score : -1
  }
  function heatInstalls(p) {
    const s = statsOf(p)
    return s ? s.installCount + s.updateCount : -1
  }
  function totalOf(p) {
    const s = statsOf(p)
    return s ? s.installCount + s.updateCount : null
  }
  function displayName(p) {
    return isZh.value ? p.zhName : p.enName
  }
  function displayDesc(p) {
    return isZh.value ? p.zhDesc : p.enDesc
  }
  function fmtCount(n) {
    if (n == null) return null
    if (n >= 10000) {
      // 与软件内插件市场一致的万缩写；en 用 k
      const wan = (n / 10000).toFixed(1).replace(/\.0$/, '')
      return isZh.value ? wan + '万' : (n / 1000).toFixed(1).replace(/\.0$/, '') + 'k'
    }
    return n.toLocaleString('en-US')
  }

  const filtered = computed(() => {
    const q = query.value.trim().toLowerCase()
    const list = officialPlugins.filter((p) => {
      if (category.value !== 'all' && p.category !== category.value) {
        return false
      }
      if (!q) return true
      const hay = [p.id, p.sourceId, p.zhName, p.enName, p.zhDesc, p.enDesc, p.author]
        .join(' ')
        .toLowerCase()
      return hay.includes(q)
    })
    if (sortKey.value === 'heat') return [...list].sort((a, b) => heatScore(b) - heatScore(a))
    if (sortKey.value === 'installs') return [...list].sort((a, b) => heatInstalls(b) - heatInstalls(a))
    if (sortKey.value === 'name') {
      return [...list].sort((a, b) =>
        displayName(a).localeCompare(displayName(b), isZh.value ? 'zh-Hans' : 'en')
      )
    }
    return list
  })

  const countText = computed(() => {
    const zh = '共 {n} 款插件 · 口径与软件内插件市场一致：安装总量 = 安装+更新次数，热度 = 应用内加权分'
    const en =
      'Showing {n} plugins · metrics match the in-app marketplace: Total = installs + updates, Heat = in-app weighted score'
    const tpl = isZh.value ? zh : en
    return tpl.replace('{n}', String(filtered.value.length))
  })

  function timeoutSignal() {
    try {
      return AbortSignal.timeout(HEAT_TIMEOUT_MS)
    } catch (e) {
      return undefined // 老浏览器不支持时退化为无超时
    }
  }

  async function fetchHeat() {
    const res = await fetch(catalog.statsApi, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        plugins: officialPlugins.map((p) => ({ sourceId: p.sourceId, pluginId: p.id }))
      }),
      signal: timeoutSignal()
    })
    if (!res.ok) throw new Error('HTTP ' + res.status)
    const json = await res.json()
    const map = {}
    for (const item of json.plugins || []) {
      map[item.sourceId + '|' + item.pluginId] = item.stats || null
    }
    return map
  }

  function applyHeat(map) {
    heatMap.value = map
    heatState.value = 'ok'
    try {
      sessionStorage.setItem(HEAT_CACHE_KEY, JSON.stringify({ ts: Date.now(), data: map }))
    } catch (e) {
      /* storage unavailable, skip caching */
    }
  }

  async function loadHeat() {
    try {
      const raw = sessionStorage.getItem(HEAT_CACHE_KEY)
      if (raw) {
        const cached = JSON.parse(raw)
        if (Date.now() - cached.ts < HEAT_TTL && cached.data) {
          applyHeat(cached.data)
          return
        }
      }
    } catch (e) {
      /* storage unavailable, fetch directly */
    }

    // 首次连接第三方统计域名时可能长时间挂起：8s 超时，失败后 1.5s 重试一次
    try {
      applyHeat(await fetchHeat())
      return
    } catch (e) {
      /* fall through to retry */
    }
    try {
      await new Promise((resolve) => setTimeout(resolve, 1500))
      applyHeat(await fetchHeat())
    } catch (e) {
      heatState.value = 'error'
    }
  }

  onMounted(loadHeat)

  return {
    catalog,
    isZh,
    query,
    category,
    sortKey,
    heatState,
    heatMap,
    filtered,
    countText,
    statsOf,
    heatScore,
    heatInstalls,
    totalOf,
    fmtCount,
    displayName,
    displayDesc
  }
}
