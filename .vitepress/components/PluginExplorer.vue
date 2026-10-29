<template>
  <div class="plugin-explorer">
    <div class="pe-toolbar">
      <input
        v-model="query"
        class="pe-search"
        type="search"
        :placeholder="t.searchPlaceholder"
      />
      <select v-model="sortKey" class="pe-sort" :aria-label="t.sortLabel">
        <option value="default">{{ t.sortDefault }}</option>
        <option value="heat">{{ t.sortHeat }}</option>
        <option value="installs">{{ t.sortInstalls }}</option>
        <option value="name">{{ t.sortName }}</option>
      </select>
    </div>

    <div class="pe-chips" role="group" :aria-label="t.filterLabel">
      <button
        class="pe-chip"
        :class="{ active: category === 'all' }"
        type="button"
        @click="category = 'all'"
      >{{ t.all }}</button>
      <button
        v-for="c in catalog.categories"
        :key="c.idx"
        class="pe-chip"
        :class="{ active: category === c.idx }"
        type="button"
        @click="category = c.idx"
      >{{ isZh ? c.zh : c.en }}</button>
      <button
        class="pe-chip"
        :class="{ active: category === 'community' }"
        type="button"
        @click="category = 'community'"
      >{{ t.community }}</button>
    </div>

    <p v-if="heatState === 'error'" class="pe-note">{{ t.heatError }}</p>

    <div class="pe-tablewrap">
      <table>
        <thead>
          <tr>
            <th>{{ t.colPlugin }}</th>
            <th class="pe-col-desc">{{ t.colDesc }}</th>
            <th>{{ t.colAuthor }}</th>
            <th class="pe-col-heat">{{ t.colHeat }}</th>
            <th>{{ t.colInstall }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in filtered" :key="p.source + ':' + p.id">
            <td>
              <a :href="p.link || '#'" target="_blank" rel="noreferrer">{{ displayName(p) }}</a>
              <span v-if="p.source === 'community'" class="pe-badge">{{ t.communityBadge }}</span>
            </td>
            <td class="pe-col-desc">{{ displayDesc(p) }}</td>
            <td>{{ p.author }}</td>
            <td class="pe-col-heat">
              <span v-if="heatState === 'loading'" class="pe-skeleton" aria-label="loading">···</span>
              <span v-else-if="statsOf(p)" :title="heatTitle(p)">🔥 {{ statsOf(p).score }}</span>
              <span v-else class="pe-heat-none">—</span>
            </td>
            <td>
              <a class="pe-install" :href="p.share" target="_blank" rel="noreferrer">{{ t.install }}</a>
            </td>
          </tr>
          <tr v-if="filtered.length === 0">
            <td colspan="5" class="pe-empty">{{ t.noResult }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <p class="pe-count">{{ countText }}</p>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useData } from 'vitepress'
import catalog from '../data/plugins.json'

const { lang } = useData()
const isZh = computed(() => !(lang.value || '').toLowerCase().startsWith('en'))

const TEXTS = {
  zh: {
    searchPlaceholder: '搜索插件 / 描述 / 作者…',
    sortLabel: '排序方式',
    sortDefault: '默认排序',
    sortHeat: '🔥 热度优先',
    sortInstalls: '安装数优先',
    sortName: '名称排序',
    filterLabel: '分类筛选',
    all: '全部',
    community: '社区源',
    communityBadge: '社区',
    heatError: '⚠️ 热度数据暂时无法获取，已按目录顺序显示',
    colPlugin: '插件',
    colDesc: '说明',
    colAuthor: '作者',
    colHeat: '热度',
    colInstall: '安装',
    install: '安装',
    noResult: '没有符合条件的插件',
    count: '共 {n} / {total} 款插件 · 热度 = 安装与更新的加权分，与应用内口径一致',
    heatTitle: (s) => `安装 ${s.installCount} · 更新 ${s.updateCount} · 失败 ${s.failureCount}`
  },
  en: {
    searchPlaceholder: 'Search plugins / descriptions / authors…',
    sortLabel: 'Sort by',
    sortDefault: 'Default order',
    sortHeat: '🔥 Heat first',
    sortInstalls: 'Installs first',
    sortName: 'Name',
    filterLabel: 'Filter by category',
    all: 'All',
    community: 'Community',
    communityBadge: 'Community',
    heatError: '⚠️ Heat data is unavailable right now — showing catalog order',
    colPlugin: 'Plugin',
    colDesc: 'Description',
    colAuthor: 'Author',
    colHeat: 'Heat',
    colInstall: 'Install',
    install: 'Install',
    noResult: 'No plugins match your filters',
    count: 'Showing {n} of {total} plugins · Heat = weighted score of installs & updates, same as the in-app ranking',
    heatTitle: (s) => `Installed ${s.installCount} · Updated ${s.updateCount} · Failed ${s.failureCount}`
  }
}
const t = computed(() => (isZh.value ? TEXTS.zh : TEXTS.en))

const query = ref('')
const category = ref('all')
const sortKey = ref('default')
const heatState = ref('loading')
const heatMap = ref({})

const HEAT_CACHE_KEY = 'vitepress-plugin-heat-v1'
const HEAT_TTL = 10 * 60 * 1000

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
function displayName(p) {
  return isZh.value ? p.zhName : p.enName
}
function displayDesc(p) {
  return isZh.value ? p.zhDesc : p.enDesc
}
function heatTitle(p) {
  const s = statsOf(p)
  return s ? t.value.heatTitle(s) : ''
}

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  const list = catalog.plugins.filter((p) => {
    if (category.value === 'community') {
      if (p.source !== 'community') return false
    } else if (category.value !== 'all' && p.category !== category.value) {
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

const countText = computed(() =>
  t.value.count
    .replace('{n}', String(filtered.value.length))
    .replace('{total}', String(catalog.plugins.length))
)

async function loadHeat() {
  try {
    const raw = sessionStorage.getItem(HEAT_CACHE_KEY)
    if (raw) {
      const cached = JSON.parse(raw)
      if (Date.now() - cached.ts < HEAT_TTL && cached.data) {
        heatMap.value = cached.data
        heatState.value = 'ok'
        return
      }
    }
  } catch (e) {
    /* storage unavailable, fetch directly */
  }

  try {
    const res = await fetch(catalog.statsApi, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        plugins: catalog.plugins.map((p) => ({ sourceId: p.sourceId, pluginId: p.id }))
      })
    })
    if (!res.ok) throw new Error('HTTP ' + res.status)
    const json = await res.json()
    const map = {}
    for (const item of json.plugins || []) {
      map[item.sourceId + '|' + item.pluginId] = item.stats || null
    }
    heatMap.value = map
    heatState.value = 'ok'
    try {
      sessionStorage.setItem(HEAT_CACHE_KEY, JSON.stringify({ ts: Date.now(), data: map }))
    } catch (e) {
      /* storage unavailable, skip caching */
    }
  } catch (e) {
    heatState.value = 'error'
  }
}

onMounted(loadHeat)
</script>

<style scoped>
.plugin-explorer {
  margin: 8px 0 4px;
}
.pe-toolbar {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 10px;
}
.pe-search {
  flex: 1 1 220px;
  min-width: 200px;
  max-width: 360px;
  padding: 7px 12px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-size: 13.5px;
}
.pe-search:focus {
  outline: none;
  border-color: var(--vp-c-brand-1);
}
.pe-sort {
  padding: 7px 10px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-size: 13.5px;
  cursor: pointer;
}
.pe-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 14px;
}
.pe-chip {
  padding: 4px 12px;
  font-size: 12.5px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 999px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-2);
  cursor: pointer;
  transition: color 0.2s, border-color 0.2s, background 0.2s;
}
.pe-chip:hover {
  border-color: var(--vp-c-brand-2);
  color: var(--vp-c-brand-1);
}
.pe-chip.active {
  background: var(--vp-c-brand-soft);
  border-color: var(--vp-c-brand-2);
  color: var(--vp-c-brand-1);
  font-weight: 500;
}
.pe-note {
  font-size: 13px;
  color: var(--vp-c-text-2);
  margin: 0 0 8px;
}
.pe-badge {
  display: inline-block;
  margin-left: 6px;
  padding: 0 7px;
  font-size: 11px;
  line-height: 18px;
  border-radius: 999px;
  background: var(--vp-c-brand-soft);
  color: var(--vp-c-brand-1);
  vertical-align: middle;
}
.pe-col-heat {
  white-space: nowrap;
}
.pe-skeleton {
  opacity: 0.4;
}
.pe-heat-none {
  color: var(--vp-c-text-3);
}
.pe-install {
  white-space: nowrap;
}
.pe-empty {
  text-align: center;
  color: var(--vp-c-text-2);
}
.pe-count {
  font-size: 12.5px;
  color: var(--vp-c-text-3);
  margin: 8px 0 0;
}
@media (max-width: 640px) {
  th.pe-col-desc,
  td.pe-col-desc {
    display: none;
  }
}
</style>
