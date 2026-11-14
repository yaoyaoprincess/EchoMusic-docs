import { computed, onMounted, ref, watch } from 'vue'
import { useData } from 'vitepress'
import catalog from '../data/plugins.json'

const HEAT_CACHE_KEY = 'vitepress-plugin-heat-v1'
const HEAT_TTL = 10 * 60 * 1000
const HEAT_TIMEOUT_MS = 8000

// 插件市场仅展示官方源插件（社区源插件见"社区插件源"页面）
const officialPlugins = catalog.plugins.filter((p) => p.source === 'official')

// ── 适用版本（manifest requires.echoMusicVersion，semver 范围）──────────
function parseSemver(s) {
  const m = /^v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?/.exec(String(s).trim())
  if (!m) return { core: [0, 0, 0], pre: null }
  return { core: [+m[1], +m[2], +m[3]], pre: m[4] ? m[4].split('.') : null }
}
function cmpVer(a, b) {
  // semver 比较（含预发布段：数值段升序、数字段 < 字母段、有预发布 < 无预发布）
  const pa = parseSemver(a)
  const pb = parseSemver(b)
  for (let i = 0; i < 3; i++) {
    if (pa.core[i] !== pb.core[i]) return pa.core[i] < pb.core[i] ? -1 : 1
  }
  if (!pa.pre && !pb.pre) return 0
  if (!pa.pre) return 1
  if (!pb.pre) return -1
  const len = Math.max(pa.pre.length, pb.pre.length)
  for (let i = 0; i < len; i++) {
    const x = pa.pre[i]
    const y = pb.pre[i]
    if (x === undefined) return -1
    if (y === undefined) return 1
    const nx = /^\d+$/.test(x)
    const ny = /^\d+$/.test(y)
    if (nx && ny) {
      if (+x !== +y) return +x < +y ? -1 : 1
    } else if (nx !== ny) {
      return nx ? -1 : 1
    } else if (x !== y) {
      return x < y ? -1 : 1
    }
  }
  return 0
}
function parseRange(range) {
  // 解析 ">=2.2.6-beta.9 <3" 这类空格分隔的范围，取下界（含）与上界（不含）
  const tokens = String(range).split(/\s+/).filter(Boolean)
  let min = null
  let max = null
  for (const t of tokens) {
    if (t.startsWith('<')) {
      if (!max) max = t.replace(/^[<>=]+/, '').trim()
    } else if (!min) {
      min = t.replace(/^[<>=]+/, '').trim()
    }
  }
  return { min, max }
}
function displayVer(range) {
  const { min, max } = parseRange(range)
  if (!min) return ''
  return max ? min + ' ~ ' + max : '≥ ' + min
}

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
  const verBase = ref('all') // 第一级：大版本系列（如 2.3.2）；all = 不筛选
  const appVer = ref('all') // 第二级：具体版本下界；随系列联动，all = 不筛选
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

  // 大版本分组：目录中出现的所有版本下界按 x.y.z 分组，从新到旧；
  // 组内下界也从高到低（正式版 > beta，beta 按序号降序）。选项全部来自
  // 插件声明，不合成假选项，上游更新后自动变化
  const versionGroups = computed(() => {
    const byBase = new Map()
    for (const p of officialPlugins) {
      if (!p.echoMusicVersion) continue
      const { min } = parseRange(p.echoMusicVersion)
      if (!min) continue
      const base = parseSemver(min).core.join('.')
      if (!byBase.has(base)) byBase.set(base, [])
      const bounds = byBase.get(base)
      if (!bounds.some((v) => cmpVer(v, min) === 0)) bounds.push(min)
    }
    return [...byBase.entries()]
      .map(([base, bounds]) => ({ base, bounds: bounds.sort((a, b) => cmpVer(b, a)) }))
      .sort((a, b) => cmpVer(b.base, a.base))
  })

  // 当前选中的系列（未选/全部时为 null，第二级下拉隐藏）
  const activeGroup = computed(
    () => versionGroups.value.find((g) => g.base === verBase.value) || null
  )

  // 切换系列时默认按该系列最高一档（正式版）过滤，第二级可再切换到具体 beta
  watch(verBase, (v) => {
    const g = versionGroups.value.find((x) => x.base === v)
    appVer.value = g ? g.bounds[0] : 'all'
  })

  // 选中应用版本 c 时插件是否适用：min ≤ c 且（无上界或 c < 上界）
  function compatibleWithApp(p) {
    if (appVer.value === 'all') return true
    if (!p.echoMusicVersion) return true // 未声明要求的插件视为任意版本可用
    const { min, max } = parseRange(p.echoMusicVersion)
    const c = appVer.value
    if (min && cmpVer(min, c) > 0) return false
    if (max && cmpVer(c, max) >= 0) return false
    return true
  }

  const filtered = computed(() => {
    const q = query.value.trim().toLowerCase()
    const list = officialPlugins.filter((p) => {
      if (category.value !== 'all' && p.category !== category.value) {
        return false
      }
      if (!compatibleWithApp(p)) {
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
    verBase,
    appVer,
    versionGroups,
    activeGroup,
    compatibleWithApp,
    displayVer,
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
