<template>
  <div class="download-container">
    <!-- 单个按钮 -->
    <div v-if="version !== 'both'" class="single-button-wrapper">
      <DownloadCore
        :type="type"
        :release-data="version === 'latest' ? latestReleaseData : prereleaseReleaseData"
        :best-mirror-url="bestMirrorUrl"
        :os-display-name="osDisplayName"
        :arch-display-name="archDisplayName"
        :label="version === 'latest' ? '正式版' : '预发布版'"
        :show-version="showVersion"
      />
    </div>

    <!-- 双按钮并排 -->
    <div v-else class="double-buttons">
      <div class="button-item">
        <DownloadCore
          :type="type"
          :release-data="latestReleaseData"
          :best-mirror-url="bestMirrorUrl"
          :os-display-name="osDisplayName"
          :arch-display-name="archDisplayName"
          label="正式版"
          :show-version="showVersion"
        />
      </div>
      <div class="button-item">
        <DownloadCore
          :type="type"
          :release-data="prereleaseReleaseData"
          :best-mirror-url="bestMirrorUrl"
          :os-display-name="osDisplayName"
          :arch-display-name="archDisplayName"
          label="预发布版"
          :show-version="showVersion"
        />
      </div>
    </div>

    <!-- 系统信息 -->
    <div class="system-info">
      <p class="download-info">
        检测到您的系统：{{ osDisplayName }} ({{ archDisplayName }})
      </p>
      <p class="download-note">
        如果下载没有自动开始，请检查网络或
        <a :href="releasesUrl" target="_blank">前往 GitHub Releases</a> 手动下载。
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import DownloadCore from './DownloadCore.vue';

// ================= 组件参数 =================
const props = defineProps({
  type: {
    type: String,
    default: 'icon',
    validator: (val) => ['link', 'icon', 'card'].includes(val)
  },
  version: {
    type: String,
    default: 'latest',
    validator: (val) => ['latest', 'prerelease', 'both'].includes(val)
  },
  customMirrors: {
    type: Array,
    default: () => []
  },
  showVersion: {
    type: Boolean,
    default: true
  },
  cacheTTL: {
    type: Number,
    default: 10 * 60 * 1000  // 10分钟
  }
});

// ================= GitHub 配置 =================
const owner = 'hoowhoami';
const repo = 'EchoMusic';
const releasesUrl = `https://github.com/${owner}/${repo}/releases`;

// ================= 镜像列表 =================
// 镜像为第三方 GHProxy 实例，可能随时失效（2026-10 实测已移除 mirror.ghproxy.com、gh.api.99988866.xyz、gh.bugdey.us.kg 三个失效源）
const defaultMirrors = [
  { name: 'GHProxy.net', url: 'https://ghproxy.net/' }
];
// 站点内置的扩展镜像列表，与 defaultMirrors 一起参与测速
const customMirrorsList = [
  { name: 'GHProxy1', url: 'https://gh.felicity.ac.cn/' },
  { name: 'GHProxy2', url: 'https://github.dpik.top/' },
  { name: 'GHProxy3', url: 'https://gh.acmsz.top/' },
  { name: 'GHProxy4', url: 'https://fastgit.cc/' },
  { name: 'GHProxy5', url: 'https://github.cnmclash.de5.net/' }
];

// 合并镜像列表：默认镜像 + 内置扩展镜像 + 外部传入的自定义镜像
const allMirrors = [...defaultMirrors, ...customMirrorsList, ...props.customMirrors];

// ================= 缓存 Key =================
const CACHE_KEY = 'vitepress_download_cache';

// ================= 响应式数据 =================
const userOS = ref('unknown');
const userArch = ref('unknown');
const osDisplayName = ref('');
const archDisplayName = ref('');
const latestReleaseData = ref(null);
const prereleaseReleaseData = ref(null);
const bestMirrorUrl = ref('');

// ================= 系统检测 =================
function detectOS() {
  const platform = navigator.platform;
  if (/^Mac/i.test(platform)) return 'mac';
  if (/^Win/i.test(platform)) return 'windows';
  if (/^Linux/i.test(platform)) return 'linux';
  return 'unknown';
}

function detectArch() {
  const ua = navigator.userAgent.toLowerCase();
  if (ua.includes('arm64') || ua.includes('aarch64')) return 'arm64';
  if (ua.includes('arm') && !ua.includes('arm64')) return 'arm';
  if (ua.includes('x86_64') || ua.includes('x64') || ua.includes('wow64') || ua.includes('win64')) return 'x64';
  if (ua.includes('i686') || ua.includes('i386') || (ua.includes('windows') && !ua.includes('x64') && !ua.includes('arm'))) return 'x86';
  return 'x64';
}

function getOSDisplayName(os) {
  if (os === 'windows') return 'Windows';
  if (os === 'mac') return 'macOS';
  if (os === 'linux') return 'Linux';
  return '未知系统';
}

function getArchDisplayName(arch) {
  if (arch === 'x64') return 'x86_64 (64位)';
  if (arch === 'x86') return 'x86 (32位)';
  if (arch === 'arm64') return 'ARM64';
  if (arch === 'arm') return 'ARM (32位)';
  return '未知架构';
}

// ================= 智能匹配附件 =================
function matchAsset(assets, os, arch) {
  const patterns = [];
  if (os === 'windows') {
    if (arch === 'arm64') {
      patterns.push(/[-_.]arm64\.exe$/i, /[-_.]aarch64\.exe$/i);
    } else if (arch === 'x86') {
      patterns.push(/[-_.]x64\.exe$/i, /[-_.]amd64\.exe$/i);
    } else {
      patterns.push(/[-_.]x64\.exe$/i, /[-_.]amd64\.exe$/i);
    }
    patterns.push(/\.exe$/i, /\.msi$/i);
  } 
  else if (os === 'mac') {
    if (arch === 'arm64') {
      patterns.push(/[-_.]arm64\.(dmg|pkg)$/i, /[-_.]aarch64\.(dmg|pkg)$/i);
    } else {
      patterns.push(/[-_.]x64\.(dmg|pkg)$/i, /[-_.]amd64\.(dmg|pkg)$/i);
    }
    patterns.push(/\.dmg$/i, /\.pkg$/i);
  }
  else if (os === 'linux') {
    if (arch === 'arm64') {
      patterns.push(/[-_.]arm64\.(AppImage|deb|rpm|tar\.gz)$/i, /[-_.]aarch64\.(AppImage|deb|rpm|tar\.gz)$/i);
    } else if (arch === 'arm') {
      patterns.push(/[-_.]armhf\.(deb|AppImage)/i, /[-_.]armv7l\.(deb|AppImage)/i);
    } else {
      patterns.push(/[-_.]x86_64\.(AppImage|deb|rpm|tar\.gz)$/i, /[-_.]amd64\.(AppImage|deb|rpm|tar\.gz)$/i);
    }
    patterns.push(/\.(AppImage|deb|rpm|tar\.gz)$/i);
  }

  for (const pattern of patterns) {
    const asset = assets.find(a => pattern.test(a.name));
    if (asset) return asset;
  }
  return null;
}

// ================= 获取 Releases 数据 =================
async function fetchAllReleases(os, arch, osDisplay, archDisplay) {
  try {
    const url = `https://api.github.com/repos/${owner}/${repo}/releases?_=${Date.now()}&per_page=100`;
    const response = await fetch(url);
    if (!response.ok) throw new Error(`API 请求失败 (${response.status})`);
    const releases = await response.json();

    const latestNormal = releases.find(r => !r.prerelease && !r.draft);
    const latestPrerelease = releases.find(r => r.prerelease && !r.draft);

    const latest = latestNormal
      ? (() => {
          const asset = matchAsset(latestNormal.assets, os, arch);
          return {
            tag_name: latestNormal.tag_name,
            download_url: asset ? asset.browser_download_url : null,
            error: asset ? null : `未找到适用于 ${osDisplay} (${archDisplay}) 的安装包`
          };
        })()
      : { tag_name: null, download_url: null, error: '没有找到任何正式版本' };

    const prerelease = latestPrerelease
      ? (() => {
          const asset = matchAsset(latestPrerelease.assets, os, arch);
          return {
            tag_name: latestPrerelease.tag_name,
            download_url: asset ? asset.browser_download_url : null,
            error: asset ? null : `未找到适用于 ${osDisplay} (${archDisplay}) 的安装包`
          };
        })()
      : { tag_name: null, download_url: null, error: '没有找到任何预发布版本' };

    return { latest, prerelease };
  } catch (err) {
    console.error('获取 Releases 失败:', err);
    const errorMsg = err.message || '获取版本信息失败';
    return {
      latest: { tag_name: null, download_url: null, error: errorMsg },
      prerelease: { tag_name: null, download_url: null, error: errorMsg }
    };
  }
}

// ================= 测速选择最优镜像 =================
// 替换原来的 selectBestMirror 函数
async function selectBestMirror(mirrorList) {
  if (!mirrorList || mirrorList.length === 0) return '';
  
  // 用于测速的固定小文件（本仓库 README.md，各镜像代理该地址以测试连通性与速度）
  const testFilePath = 'https://raw.githubusercontent.com/hoowhoami/EchoMusic/main/README.md';
  
  const timeout = 10000; // 10秒超时
  const results = [];
  
  for (const mirror of mirrorList) {
    const testUrl = `${mirror.url}${testFilePath}`;
    const start = performance.now();
    let success = false;
    let speed = 0;
    let fileSize = 0;
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);
      
      // 发起真实 GET 请求，获取部分数据即可计算速度
      const response = await fetch(testUrl, {
        method: 'GET',
        signal: controller.signal,
        // 不设置 mode: 'no-cors'，以便读取 Content-Length
      });
      clearTimeout(timeoutId);
      
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      // 获取文件大小（Content-Length header）
      const contentLength = response.headers.get('content-length');
      if (contentLength) {
        fileSize = parseInt(contentLength, 10);
      } else {
        // 如果没有 Content-Length，则下载前 N 字节估算
        // 这里简化：认为下载成功即可，速度按时间倒数排序
        success = true;
        const latency = performance.now() - start;
        results.push({ mirror, latency, speed: 0, success: true });
        continue;
      }
      
      // 下载第一块数据（例如前 256KB）来测速
      const reader = response.body.getReader();
      let received = 0;
      const targetSize = Math.min(256 * 1024, fileSize); // 最多下载 256KB
      const startDownload = performance.now();
      
      while (received < targetSize) {
        const { done, value } = await reader.read();
        if (done) break;
        received += value.length;
      }
      reader.cancel(); // 取消继续下载
      
      const downloadTime = (performance.now() - startDownload) / 1000; // 秒
      const speedMbps = (received / 1024 / 1024) / downloadTime; // MB/s
      
      success = true;
      results.push({
        mirror,
        latency: performance.now() - start,
        speed: speedMbps,
        success: true
      });
      
      console.log(`[测速] ${mirror.name} 速度: ${speedMbps.toFixed(2)} MB/s, 延迟: ${(performance.now() - start).toFixed(0)}ms`);
      
    } catch (err) {
      console.warn(`[测速] ${mirror.name} 失败:`, err);
      results.push({ mirror, latency: Infinity, speed: 0, success: false });
    }
  }
  
  // 优先按速度排序（速度越高越好），速度相同时按延迟排序
  const successful = results.filter(r => r.success);
  if (successful.length === 0) return '';
  
  successful.sort((a, b) => {
    if (a.speed > 0 && b.speed > 0) return b.speed - a.speed; // 速度降序
    if (a.speed > 0) return -1;
    if (b.speed > 0) return 1;
    return a.latency - b.latency; // 都没有速度数据时按延迟
  });
  
  const best = successful[0];
  console.log(`[最优镜像] ${best.mirror.name} (速度 ${best.speed.toFixed(2)} MB/s, 延迟 ${best.latency.toFixed(0)}ms)`);
  return best.mirror.url;
}
// ================= 缓存读写 =================
function getCachedData(os, arch) {
  // 1. 内存缓存
  if (window.__downloadButtonCache) {
    const mem = window.__downloadButtonCache;
    const now = Date.now();
    if (now - mem.timestamp <= props.cacheTTL && mem.os === os && mem.arch === arch) {
      console.log('[DownloadButton] 命中内存缓存');
      return mem;
    }
  }
  // 2. localStorage
  const stored = localStorage.getItem(CACHE_KEY);
  if (stored) {
    try {
      const cache = JSON.parse(stored);
      const now = Date.now();
      if (now - cache.timestamp <= props.cacheTTL && cache.os === os && cache.arch === arch) {
        console.log('[DownloadButton] 命中 localStorage 缓存');
        window.__downloadButtonCache = cache;
        return cache;
      } else {
        console.log('[DownloadButton] localStorage 缓存已过期或系统不匹配');
      }
    } catch (e) {
      console.warn('[DownloadButton] 解析缓存失败', e);
    }
  }
  return null;
}

function setCachedData(latest, prerelease, mirrorUrl, os, arch) {
  const cacheObj = {
    latestReleaseData: latest,
    prereleaseReleaseData: prerelease,
    bestMirrorUrl: mirrorUrl,
    os,
    arch,
    timestamp: Date.now()
  };
  window.__downloadButtonCache = cacheObj;
  localStorage.setItem(CACHE_KEY, JSON.stringify(cacheObj));
  console.log('[DownloadButton] 已写入缓存');
}

// ================= 主加载逻辑 =================
async function loadData() {
  const os = detectOS();
  const arch = detectArch();
  const osName = getOSDisplayName(os);
  const archName = getArchDisplayName(arch);

  userOS.value = os;
  userArch.value = arch;
  osDisplayName.value = osName;
  archDisplayName.value = archName;

  const cached = getCachedData(os, arch);
  if (cached) {
    latestReleaseData.value = cached.latestReleaseData;
    prereleaseReleaseData.value = cached.prereleaseReleaseData;
    bestMirrorUrl.value = cached.bestMirrorUrl;
    return;
  }

  console.log('[DownloadButton] 无有效缓存，发起网络请求');
  const [releasesData, mirrorUrl] = await Promise.all([
    fetchAllReleases(os, arch, osName, archName),
    selectBestMirror(allMirrors)
  ]);

  latestReleaseData.value = releasesData.latest;
  prereleaseReleaseData.value = releasesData.prerelease;
  bestMirrorUrl.value = mirrorUrl;

  setCachedData(releasesData.latest, releasesData.prerelease, mirrorUrl, os, arch);
}

onMounted(() => {
  loadData();
});
</script>

<style scoped>
.download-container {
  text-align: center;
  margin: 2rem 0;
}
.double-buttons {
  display: flex;
  justify-content: center;
  gap: 2rem;
  flex-wrap: wrap;
}
.button-item {
  flex: 0 1 auto;
}
.system-info {
  margin-top: 1.5rem;
}
.download-info, .download-note {
  font-size: 0.9rem;
  color: #4e6e8e;
  margin: 0.5rem 0;
}
.download-note a {
  color: #3eaf7c;
  text-decoration: none;
}
.download-note a:hover {
  text-decoration: underline;
}
</style>