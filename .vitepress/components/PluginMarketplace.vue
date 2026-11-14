<template>
  <div class="plugin-market">
    <div class="pm-toolbar">
      <input
        v-model="query"
        class="pm-search"
        type="search"
        :placeholder="t.searchPlaceholder"
      />
      <select v-model="sortKey" class="pm-sort" :aria-label="t.sortLabel">
        <option value="heat">{{ t.sortHeat }}</option>
        <option value="installs">{{ t.sortInstalls }}</option>
        <option value="name">{{ t.sortName }}</option>
        <option value="default">{{ t.sortDefault }}</option>
      </select>
      <select v-model="verBase" class="pm-sort" :aria-label="t.verLabel">
        <option value="all">{{ t.verAll }}</option>
        <option v-for="g in versionGroups" :key="g.base" :value="g.base">
          {{ g.base }}{{ t.seriesSuffix }}
        </option>
      </select>
      <select
        v-if="activeGroup"
        v-model="appVer"
        class="pm-sort"
        :aria-label="t.verBoundLabel"
      >
        <option v-for="b in activeGroup.bounds" :key="b" :value="b">≥ {{ b }}</option>
      </select>
    </div>

    <div class="pm-chips" role="group" :aria-label="t.filterLabel">
      <button
        class="pm-chip"
        :class="{ active: category === 'all' }"
        type="button"
        @click="category = 'all'"
      >{{ t.all }}</button>
      <button
        v-for="c in catalog.categories"
        :key="c.idx"
        class="pm-chip"
        :class="{ active: category === c.idx }"
        type="button"
        @click="category = c.idx"
      >{{ isZh ? c.zh : c.en }}</button>
    </div>

    <p v-if="heatState === 'error'" class="pm-note">{{ t.heatError }}</p>
    <p v-else-if="heatState === 'loading'" class="pm-note">{{ t.heatLoading }}</p>

    <div class="pm-grid">
      <article v-for="p in filtered" :key="p.source + ':' + p.id" class="pm-card">
        <div class="pm-head">
          <div class="pm-icon">
            <img
              v-if="iconSrc(p)"
              :src="iconSrc(p)"
              alt=""
              @error="onIconError(p)"
            />
            <span v-else class="pm-icon-fallback">{{ initial(p) }}</span>
          </div>
          <div class="pm-title-wrap">
            <h3 class="pm-name">{{ displayName(p) }}</h3>
            <div class="pm-author">{{ p.author || '—' }}</div>
          </div>
          <span v-if="p.version && p.version !== 'unknown'" class="pm-version">v{{ p.version }}</span>
        </div>

        <p class="pm-desc">{{ displayDesc(p) || '—' }}</p>

        <div v-if="p.tags && p.tags.length" class="pm-tags">
          <span v-for="tg in p.tags.slice(0, 6)" :key="tg" class="pm-tag">{{ tg }}</span>
        </div>

        <div class="pm-meta">
          <span class="pm-meta-id">ID: {{ p.id }}</span>
          <span>来源: {{ isZh ? p.sourceZh : p.sourceEn }}</span>
          <span class="pm-meta-ver" :title="p.echoMusicVersion || undefined">
            {{ t.compatLabel }}{{ p.echoMusicVersion ? displayVer(p.echoMusicVersion) : t.compatAny }}
          </span>
        </div>

        <div class="pm-stats">
          <template v-if="heatState === 'loading'">
            <span class="pm-stat-box">···</span>
            <span class="pm-stat-box">···</span>
            <span class="pm-stat-box">···</span>
          </template>
          <template v-else-if="statsOf(p)">
            <span class="pm-stat-box" :title="dlTitle(p)">
              <ArrowDownToLine class="pm-ic pm-ic-dl" :size="13" />
              {{ fmtCount(totalOf(p)) }}
            </span>
            <span class="pm-stat-box" :title="updTitle(p)">
              <RefreshCw class="pm-ic pm-ic-up" :size="13" />
              {{ fmtCount(statsOf(p).updateCount) }}
            </span>
            <span class="pm-stat-box" :title="heatTitle(p)">
              <Heart class="pm-ic pm-ic-heat" :size="13" />
              {{ fmtCount(statsOf(p).score) }}
            </span>
          </template>
          <template v-else>
            <span class="pm-stat-box pm-stat-none">—</span>
            <span class="pm-stat-box pm-stat-none">—</span>
            <span class="pm-stat-box pm-stat-none">—</span>
          </template>
        </div>

        <div class="pm-actions">
          <button class="pm-btn" type="button" @click="copyShare(p)">
            <Share2 class="pm-bic" :size="13" />
            {{ copied[p.id] ? t.copied : t.share }}
          </button>
          <a class="pm-btn" :href="p.link || '#'" target="_blank" rel="noreferrer">
            <FolderGit2 class="pm-bic" :size="13" />
            {{ t.repo }}
          </a>
          <a class="pm-btn pm-btn-primary" :href="p.share" target="_blank" rel="noreferrer">
            <Download class="pm-bic" :size="13" />
            {{ t.install }}
          </a>
        </div>
      </article>

      <div v-if="filtered.length === 0" class="pm-empty">{{ t.noResult }}</div>
    </div>

    <p class="pm-count">{{ countText }}</p>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ArrowDownToLine, Download, FolderGit2, Heart, RefreshCw, Share2 } from 'lucide-vue-next'
import { usePluginCatalog } from './usePluginCatalog'

const { catalog, isZh, query, category, sortKey, verBase, appVer, versionGroups, activeGroup, displayVer, heatState, filtered, countText, statsOf, fmtCount, totalOf, displayName, displayDesc } =
  usePluginCatalog()

const TEXTS = {
  zh: {
    searchPlaceholder: '搜索插件 / 描述 / 作者…',
    sortLabel: '排序方式',
    sortDefault: '默认排序',
    sortHeat: '热度优先',
    sortInstalls: '安装总量优先',
    sortName: '名称排序',
    filterLabel: '分类筛选',
    all: '全部',
    verLabel: '适用的大版本',
    verBoundLabel: '该系列的具体版本',
    verAll: '适用全部版本',
    seriesSuffix: ' 系列',
    compatLabel: '适用: ',
    compatAny: '任意版本',
    heatError: '⚠️ 热度数据暂时无法获取，已按目录顺序显示',
    heatLoading: '⏳ 热度数据加载中…',
    share: '分享',
    copied: '已复制 ✓',
    repo: '仓库',
    install: '安装',
    noResult: '没有符合条件的插件',
    dlTitle: (s) => `安装和更新总量 ${s.installCount + s.updateCount}（安装 ${s.installCount} · 更新 ${s.updateCount}）`,
    updTitle: (s) => `累计更新 ${s.updateCount} 次`,
    heatTitle: (s) => `应用内热度 ${s.score}（安装 ${s.installCount} · 更新 ${s.updateCount} · 失败 ${s.failureCount}）`
  },
  en: {
    searchPlaceholder: 'Search plugins / descriptions / authors…',
    sortLabel: 'Sort by',
    sortDefault: 'Default order',
    sortHeat: 'Heat first',
    sortInstalls: 'Total first',
    sortName: 'Name',
    filterLabel: 'Filter by category',
    all: 'All',
    verLabel: 'App version series',
    verBoundLabel: 'Version requirement in this series',
    verAll: 'All versions',
    seriesSuffix: ' series',
    compatLabel: 'Requires: ',
    compatAny: 'any version',
    heatError: '⚠️ Heat data is unavailable right now — showing catalog order',
    heatLoading: '⏳ Loading heat data…',
    share: 'Share',
    copied: 'Copied ✓',
    repo: 'Repository',
    install: 'Install',
    noResult: 'No plugins match your filters',
    dlTitle: (s) => `Total installs+updates ${s.installCount + s.updateCount} (installed ${s.installCount} · updated ${s.updateCount})`,
    updTitle: (s) => `Updated ${s.updateCount} times`,
    heatTitle: (s) => `In-app heat ${s.score} (installed ${s.installCount} · updated ${s.updateCount} · failed ${s.failureCount})`
  }
}
const t = computed(() => (isZh.value ? TEXTS.zh : TEXTS.en))

const copied = ref({})
const iconStage = ref({}) // p.id → 图标候选源序号；超出候选数则显示首字母占位

// raw.githubusercontent 国内访问不稳定：本地镜像 → jsDelivr 镜像 → raw 原始 逐级回退
function jsdelivrUrl(raw) {
  return raw.replace(
    /^https:\/\/raw\.githubusercontent\.com\/([^/]+)\/([^/]+)\//,
    'https://cdn.jsdelivr.net/gh/$1@$2/'
  )
}
function iconCandidates(p) {
  const list = []
  // 同步脚本下载到 docs/public/plugin-icons/ 的本地镜像；?v= 版本号破缓存
  if (p.iconExt) {
    const v = p.version && p.version !== 'unknown' ? '?v=' + encodeURIComponent(p.version) : ''
    list.push('/plugin-icons/' + p.id + p.iconExt + v)
  }
  if (p.icon) {
    list.push(jsdelivrUrl(p.icon))
    list.push(p.icon)
  }
  return list
}
function iconSrc(p) {
  const list = iconCandidates(p)
  const stage = iconStage.value[p.id] ?? 0
  return stage < list.length ? list[stage] : null
}
function onIconError(p) {
  const max = iconCandidates(p).length
  const cur = iconStage.value[p.id] ?? 0
  if (cur < max) iconStage.value = { ...iconStage.value, [p.id]: cur + 1 }
}
function initial(p) {
  const name = displayName(p) || p.id || '?'
  return name.trim().charAt(0).toUpperCase()
}
function heatTitle(p) {
  const s = statsOf(p)
  return s ? t.value.heatTitle(s) : ''
}
function dlTitle(p) {
  const s = statsOf(p)
  return s ? t.value.dlTitle(s) : ''
}
function updTitle(p) {
  const s = statsOf(p)
  return s ? t.value.updTitle(s) : ''
}
async function copyShare(p) {
  try {
    await navigator.clipboard.writeText(p.share)
    copied.value = { ...copied.value, [p.id]: true }
    setTimeout(() => {
      copied.value = { ...copied.value, [p.id]: false }
    }, 1500)
  } catch (e) {
    // 剪贴板不可用时直接打开分享页
    window.open(p.share, '_blank', 'noopener')
  }
}
</script>

<style scoped>
.plugin-market {
  margin: 8px 0 4px;
}
.pm-toolbar {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 10px;
}
.pm-search {
  flex: 1 1 240px;
  max-width: 380px;
  padding: 8px 14px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 10px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-size: 14px;
}
.pm-search:focus {
  outline: none;
  border-color: var(--vp-c-brand-1);
}
.pm-sort {
  padding: 8px 12px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 10px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-size: 14px;
  cursor: pointer;
}
.pm-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 18px;
}
.pm-chip {
  padding: 5px 14px;
  font-size: 13px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 999px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-2);
  cursor: pointer;
  transition: color 0.2s, border-color 0.2s, background 0.2s;
}
.pm-chip:hover {
  border-color: var(--vp-c-brand-2);
  color: var(--vp-c-brand-1);
}
.pm-chip.active {
  background: var(--vp-c-brand-soft);
  border-color: var(--vp-c-brand-2);
  color: var(--vp-c-brand-1);
  font-weight: 500;
}
.pm-note {
  font-size: 13px;
  color: var(--vp-c-text-2);
  margin: 0 0 12px;
}
.pm-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}
.pm-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 14px;
  padding: 16px;
  background: var(--vp-c-bg);
  transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
}
.pm-card:hover {
  transform: translateY(-3px);
  border-color: var(--vp-c-brand-2);
  box-shadow: 0 10px 30px var(--vp-c-brand-soft);
}
.pm-head {
  display: flex;
  align-items: center;
  gap: 12px;
}
.pm-icon {
  width: 46px;
  height: 46px;
  border-radius: 12px;
  overflow: hidden;
  flex: none;
  background: linear-gradient(135deg, var(--vp-c-brand-soft), var(--vp-c-bg-soft));
  display: flex;
  align-items: center;
  justify-content: center;
}
html.dark .pm-icon {
  /* 暗色模式下给图标垫浅色底，避免深色主题的图标融入背景 */
  background: #eef1f5;
}
.pm-icon img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.pm-icon-fallback {
  font-size: 20px;
  font-weight: 600;
  color: var(--vp-c-brand-1);
}
.pm-title-wrap {
  flex: 1;
  min-width: 0;
}
.pm-name {
  margin: 0;
  font-size: 15.5px;
  font-weight: 600;
  color: var(--vp-c-text-1);
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.pm-author {
  font-size: 12.5px;
  color: var(--vp-c-text-2);
  margin-top: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.pm-version {
  font-size: 11.5px;
  color: var(--vp-c-text-3);
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  padding: 1px 7px;
  white-space: nowrap;
  align-self: flex-start;
}
.pm-desc {
  margin: 0;
  font-size: 13px;
  line-height: 1.65;
  color: var(--vp-c-text-2);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  /* 1 行简介也预留 2 行高度，保证同行卡片的标签/元信息起点一致 */
  min-height: calc(2 * 1.65em);
}
.pm-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.pm-tag {
  font-size: 11.5px;
  padding: 2px 9px;
  border-radius: 999px;
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-2);
  border: 1px solid var(--vp-c-divider);
}
.pm-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 14px;
  font-size: 12px;
  color: var(--vp-c-text-3);
  /* 吸底：简介/标签行数不一致时，把元信息+三数据+按钮钉在卡片底部，同排卡片横向对齐 */
  margin-top: auto;
}
.pm-meta-ver {
  /* 适用版本固定独占一行 */
  flex-basis: 100%;
}
.pm-stats {
  display: flex;
  gap: 8px;
}
.pm-stat-box {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  padding: 7px 4px;
  border-radius: 9px;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  font-size: 12.5px;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
  color: var(--vp-c-text-1);
}
.pm-ic {
  flex: none;
}
.pm-ic-dl,
.pm-ic-up {
  color: var(--vp-c-brand-1);
}
.pm-ic-heat {
  color: #ec6a7c;
}
.pm-stat-none {
  color: var(--vp-c-text-3);
}
.pm-actions {
  display: flex;
  gap: 8px;
}
.pm-btn {
  flex: 1;
  min-width: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  padding: 7px 4px;
  font-size: 13px;
  font-weight: 500;
  border-radius: 9px;
  border: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-1);
  text-decoration: none;
  cursor: pointer;
  font-family: inherit;
  transition: color 0.2s, border-color 0.2s, background 0.2s;
}
.pm-btn:hover {
  border-color: var(--vp-c-brand-2);
  color: var(--vp-c-brand-1);
}
.pm-btn:hover .pm-bic {
  color: var(--vp-c-brand-1);
}
.pm-bic {
  flex: none;
}
.pm-btn-primary {
  background: var(--vp-c-brand-3);
  border-color: var(--vp-c-brand-3);
  color: #fff;
}
.pm-btn-primary:hover {
  background: var(--vp-c-brand-2);
  color: #fff;
}
.pm-btn-primary:hover .pm-bic {
  color: #fff;
}
.pm-empty {
  grid-column: 1 / -1;
  text-align: center;
  color: var(--vp-c-text-2);
  padding: 40px 0;
  border: 1px dashed var(--vp-c-divider);
  border-radius: 14px;
}
.pm-count {
  font-size: 12.5px;
  color: var(--vp-c-text-3);
  margin: 16px 0 0;
}
</style>
