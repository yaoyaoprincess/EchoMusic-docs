---
title: API 总览
outline: [2, 4]
---

# 🔧 API 总览

`ctx` 对象是插件的核心入口。本文档按模块列出所有插件可用的 API 速查表，每个 API 标注了所属的详情文档以便深入了解。

> ℹ️ 本文档以 [EchoMusicPlugins 仓库](https://github.com/hoowhoami/EchoMusicPlugins) 官方文档为准。内部 API（mpv 引擎、桌面歌词、Mini 播放器等）不在插件范围内，详见 [内部 API 参考 →](../internal-api/)。

---

## 🏗️ 宿主运行时

| API | 类型 | 说明 |
|-----|------|------|
| `ctx.vue` | Vue 3 运行时 | `defineComponent` / `h` / `ref` / `computed` / `watch` / `onMounted` / `onUnmounted` / `defineAsyncComponent` / `reactive` / `resolveComponent` |
| `ctx.app` | App 实例 | 主应用 Vue App 实例 |
| `ctx.router` | Router 实例 | Vue Router 实例 |
| `ctx.pinia` | Pinia 实例 | Pinia 状态管理实例 |

> ⚠️ 不能 `import { ref } from 'vue'`，必须通过 `ctx.vue.ref()` 访问。

---

## 📦 状态管理（Stores）

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.stores.player` | 播放状态：当前歌曲、进度、音量、播放模式 | [播放器](./player-audio) |
| `ctx.stores.playlist` | 播放队列状态 | [播放器](./player-audio) |
| `ctx.stores.lyric` | 歌词状态：当前行、翻译、偏移 | [播放器](./player-audio#歌词系统) |
| `ctx.stores.settings` | 用户全局设置 | — |
| `ctx.stores.theme` | 主题色、深浅模式 | [文件存储](./filesystem-storage#外观订阅) |

---

## 🎨 UI 扩展

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.ui.addPage({id, title, icon?, component, sidebar?})` | 注册侧边栏独立页面 | [UI 扩展](./ui-extension#注册独立页面) |
| `ctx.ui.sidebar.addItem({id, title, icon?, pageId, section?, order?})` | 为已注册页面添加侧边栏项 | [UI 扩展](./ui-extension#侧边栏项) |
| `ctx.ui.settings.define({title, component})` | 注册插件设置面板 | [UI 扩展](./ui-extension#设置面板) |
| `ctx.ui.addSongContextMenuItem({id, label, onSelect})` | 歌曲右键菜单项 | [UI 扩展](./ui-extension#歌曲右键菜单) |
| `ctx.ui.cover.setFallback({id, resolveUrl})` | 封面无法加载时的回退图片 | [UI 扩展](./ui-extension#封面回退) |
| `ctx.ui.mount(target, component, opts?)` | 挂载 Vue 组件到 DOM | [UI 扩展](./ui-extension#组件挂载) |
| `ctx.ui.teleport(component, opts?)` | Teleport 组件到 body | [UI 扩展](./ui-extension#组件传送) |
| `ctx.ui.components.Button` / `Switch` / `Input` / `Select` / `Slider` | 预置 UI 控件（`defineAsyncComponent` 加载） | [UI 扩展](./ui-extension#预置组件) |
| `ctx.css.inject(css, {id?})` | 动态注入 CSS | [UI 扩展](./ui-extension#css-注入) |
| `ctx.css.remove(id)` | 移除注入的 CSS | [UI 扩展](./ui-extension#css-注入) |
| `ctx.dom.observe(selector, callback)` | 监听 DOM 节点出现 | [UI 扩展](./ui-extension#dom-监听) |

---

## 🎵 播放 & 音频

### 播放控制

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.player.play()` | 开始/恢复播放 | [播放器](./player-audio#播放控制) |
| `ctx.player.pause()` | 暂停 | [播放器](./player-audio#播放控制) |
| `ctx.player.toggle()` | 播放/暂停切换 | [播放器](./player-audio#播放控制) |
| `ctx.player.prev()` | 上一首 | [播放器](./player-audio#播放控制) |
| `ctx.player.next()` | 下一首 | [播放器](./player-audio#播放控制) |
| `ctx.player.stop()` | 停止 | [播放器](./player-audio#播放控制) |
| `ctx.player.seek(time)` | 跳转（秒） | [播放器](./player-audio#播放控制) |
| `ctx.player.setVolume(v)` | 设置音量（0-100） | [播放器](./player-audio#播放控制) |
| `ctx.player.setPlaybackRate(r)` | 倍速（0.5-3.0） | [播放器](./player-audio#播放控制) |
| `ctx.player.setPlayMode(m)` | 播放模式 | [播放器](./player-audio#播放控制) |
| `ctx.player.setAudioQuality(q)` | 音频品质 | [播放器](./player-audio#播放控制) |
| `ctx.player.setAudioEffect(e)` | 设置音效 | [播放器](./player-audio#播放控制) |
| `ctx.player.playTrack(track)` | 播放指定歌曲 | [播放器](./player-audio#播放控制) |
| `ctx.player.playNext()` | 播放下一首（跳过队列） | [播放器](./player-audio#播放控制) |
| `ctx.player.playLast()` | 播放上一首 | [播放器](./player-audio#播放控制) |
| `ctx.player.replaceQueueAndPlay(items)` | 替换队列并播放 | [播放器](./player-audio#播放控制) |
| `ctx.player.dislikePersonalFm()` | 私人 FM 不喜欢 | [播放器](./player-audio#播放控制) |
| `ctx.player.toggleLyricView(open?)` | 切换歌词视图 | [播放器](./player-audio#播放控制) |

### 播放状态（computed，只读响应式）

| 属性 | 类型 | 说明 |
|------|:--:|------|
| `currentTrack` | `computed` | 当前歌曲对象 |
| `currentTrackId` | `computed` | 当前歌曲 ID |
| `currentTime` | `computed` | 播放进度（秒） |
| `duration` | `computed` | 总时长（秒） |
| `isPlaying` | `computed` | 是否播放中 |
| `playbackRate` | `computed` | 播放速率 |
| `volume` | `computed` | 音量（0-100） |
| `playMode` | `computed` | 播放模式 |

### 播放队列

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.playlist.getQueue()` | 获取当前队列 | [播放器](./player-audio#播放队列管理) |
| `ctx.playlist.replaceQueue(items)` | 替换整个队列 | [播放器](./player-audio#播放队列管理) |
| `ctx.playlist.addTrack(track)` | 添加歌曲 | [播放器](./player-audio#播放队列管理) |
| `ctx.playlist.removeTrack(id)` | 移除歌曲 | [播放器](./player-audio#播放队列管理) |
| `ctx.playlist.clear()` | 清空队列 | [播放器](./player-audio#播放队列管理) |
| `ctx.playlist.reorder(from, to)` | 重排 | [播放器](./player-audio#播放队列管理) |
| `ctx.playlist.playNext(track)` | 插播（下一首播放） | [播放器](./player-audio#播放队列管理) |

### 音频频谱

> 需要 capability：`audioSpectrum: true`

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.audio.spectrum.getStatus()` | 获取捕获状态 | [频谱](./audio-spectrum#getstatus) |
| `ctx.audio.spectrum.getSnapshot()` | 单帧频谱快照 | [频谱](./audio-spectrum#getsnapshot) |
| `ctx.audio.spectrum.subscribe(opts, cb)` | 实时订阅频谱 | [频谱](./audio-spectrum#subscribe) |

### 自定义音源 & 歌词

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.player.audioSource.register(opts)` | 注册音源解析器（需 `audioSource: true`） | [播放器](./player-audio#自定义音源) |
| `ctx.lyrics.registerResolver(opts)` | 注册歌词解析器（需 `lyrics: true`） | [播放器](./player-audio#注册歌词解析器) |
| `ctx.lyrics.getSnapshot()` | 歌词状态快照 | [播放器](./player-audio#获取订阅歌词快照) |
| `ctx.lyrics.onSnapshot(fn)` | 订阅歌词变化 | [播放器](./player-audio#获取订阅歌词快照) |
| `ctx.lyrics.command(cmd)` | 发送歌词命令 | [播放器](./player-audio#获取订阅歌词快照) |
| `ctx.lyricEffects.register(opts)` | 注册歌词动效（需 `lyricEffects: true`） | [播放器](./player-audio#歌词视觉效果) |

> ℹ️ mpv 引擎高级控制（EQ/空间音效/IR/设备/渐变等）属于内部 API，不在插件范围内。详见 [内部 API 参考 →](../internal-api/audio-engine)。

---

## 💾 数据 & 文件

### KV 存储

`ctx.storage` 提供按插件隔离的持久化 KV 存储。

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.storage.get(key)` | 读取键值 | [数据](./filesystem-storage#kv-存储) |
| `ctx.storage.set(key, value)` | 写入键值 | [数据](./filesystem-storage#kv-存储) |

> 插件卸载时 KV 数据自动清除；升级（覆盖安装）时保留。

### 文件系统

> 需要 capability：`localFiles: true`（大部分操作）

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.fs.listFiles(directory, opts?)` | 扫描目录 | [数据](./filesystem-storage#文件系统) |
| `ctx.fs.listImageFiles(directory, opts?)` | 扫描图片文件 | [数据](./filesystem-storage#文件系统) |
| `ctx.fs.readTextFile(path, opts?)` | 读取文本文件 | [数据](./filesystem-storage#文件系统) |
| `ctx.fs.readFileBytes(path, opts?)` | 读取二进制文件 | [数据](./filesystem-storage#文件系统) |
| `ctx.fs.writeFile(path, data, opts?)` | 写入文件（仅插件目录内） | [数据](./filesystem-storage#文件系统) |
| `ctx.fs.deleteFile(path)` | 删除文件（仅插件目录内） | [数据](./filesystem-storage#文件系统) |
| `ctx.fs.getFileUrl(path)` | 获取文件播放 URL | [数据](./filesystem-storage#文件系统) |

### 外观 & 字体

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.appearance.getSnapshot()` | 外观快照（主题色/深色模式/字体） | [数据](./filesystem-storage#外观订阅) |
| `ctx.appearance.onSnapshot(fn)` | 订阅外观变化 | [数据](./filesystem-storage#外观订阅) |
| `ctx.fonts.getAll()` | 系统字体名称列表 | — |
| `ctx.fonts.getOptions({includeFollow?})` | 字体选项（可用于 Select 组件） | — |
| `ctx.fonts.buildFamily(name)` | 构建 CSS font-family 字符串 | — |

---

## 🪟 窗口 & 系统

### 插件浮窗

> 浮窗需在 manifest `contributes.windows` 中声明。

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.windows.show()` | 显示浮窗 | [系统](./windows-system#浮窗管理) |
| `ctx.windows.hide()` | 隐藏浮窗 | [系统](./windows-system#浮窗管理) |
| `ctx.windows.close()` | 关闭浮窗 | [系统](./windows-system#浮窗管理) |
| `ctx.windows.move(x, y)` | 移动浮窗 | [系统](./windows-system#浮窗管理) |
| `ctx.windows.getBounds()` | 获取浮窗位置和尺寸 | [系统](./windows-system#浮窗管理) |
| `ctx.windows.setIgnoreMouseEvents(bool)` | 鼠标穿透 | [系统](./windows-system#浮窗管理) |

### Now Playing

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.nowPlaying.getSnapshot()` | 当前状态快照 | [系统](./windows-system#now-playing-浮窗) |
| `ctx.nowPlaying.onSnapshot(fn)` | 订阅状态变化 | [系统](./windows-system#now-playing-浮窗) |
| `ctx.nowPlaying.onCommand(fn)` | 监听命令 | [系统](./windows-system#now-playing-浮窗) |
| `ctx.nowPlaying.syncPlayback(state)` | 同步播放状态 | [系统](./windows-system#now-playing-浮窗) |
| `ctx.nowPlaying.syncLyric(state)` | 同步歌词状态 | [系统](./windows-system#now-playing-浮窗) |

### 进程管理

> 需要 capability：`process: true`

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.process.launch(opts)` | 启动插件目录内程序 | [系统](./windows-system#进程管理) |
| `ctx.process.terminate(pid?)` | 终止已启动的进程 | [系统](./windows-system#进程管理) |

### 应用图标

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.appIcons.refresh()` | 刷新所有图标缓存 | [系统](./windows-system#应用图标) |
| `ctx.appIcons.setRuntimeWindowIcon(path)` | 设置运行时窗口图标 | [系统](./windows-system#应用图标) |
| `ctx.appIcons.restoreDefaultWindowIcon()` | 恢复默认窗口图标 | [系统](./windows-system#应用图标) |
| `ctx.appIcons.restoreDefaultDesktopIcon()` | 恢复默认桌面图标 | [系统](./windows-system#应用图标) |
| `ctx.appIcons.restoreDefaultTaskbarIcon()` | 恢复默认任务栏图标 | [系统](./windows-system#应用图标) |

### 图标库

| API | 说明 |
|-----|------|
| `ctx.icons` | Iconify 图标对象，如 `ctx.icons.iconPictureInPicture`，可直接传入 `Icon` 组件 |

```js
const Icon = ctx.vue.resolveComponent("Icon");
h(Icon, { icon: ctx.icons.iconPictureInPicture, width: 16, height: 16 });
```

### 系统对话框

| API | 说明 |
|-----|------|
| `ctx.dialog.selectDirectory(opts?)` | 打开目录选择对话框，返回 `{canceled, paths}` |
| `ctx.dialog.selectFiles(opts?)` | 打开文件选择对话框，支持 `multiple`、`filters` |

### 字体

| API | 说明 |
|-----|------|
| `ctx.fonts.getAll()` | 系统可用字体名称列表 |
| `ctx.fonts.getOptions({includeFollow?})` | 字体下拉选项 |
| `ctx.fonts.buildFamily(name)` | 构建 CSS `font-family` 值 |

---

## 🎨 主题 & 样式

### 表面样式

```js
ctx.theme.surface.set({
  enabled: true,
  mainOpacity: 82,         // 0-100
  sidebarOpacity: 82,
  cardOpacity: 86,
  playerOpacity: 92,
  backdropFilter: "blur(10px)",
  playerBackdropFilter: "blur(20px) saturate(180%)",
});
ctx.theme.surface.clear(); // 恢复默认
```

### 页面过渡动画

```js
ctx.theme.pageTransition.set({
  enabled: true,
  mode: "out-in",
  appear: true,
  durationMs: 450,
  enterOpacity: 0,
  leaveOpacity: 0,
  enterTranslateY: 6,
});
ctx.theme.pageTransition.clear();
```

### 主题色渐变

```js
ctx.theme.accentGradient.set({
  color: "#ff5c8a",
  angle: 180,
  height: "46%",
  peakOpacity: 0.28,
});
ctx.theme.accentGradient.clear();
```

---

## 📜 滚动画布

`ctx.scroll` 提供页面滚动容器的高级控制，适合滚动增强类插件。

| API | 说明 |
|-----|------|
| `queryContainers()` | 获取所有滚动容器 |
| `getCurrentContainer()` | 获取当前焦点容器 |
| `getState(el?)` | 获取滚动状态 |
| `scrollToTop(el?)` | 滚动到顶部 |
| `scrollToBottom(el?)` | 滚动到底部 |
| `observeContainers(handler)` | 监听滚动容器变化 |

---

## 🌐 酷狗 API

> 需要 capability：`kugouApi: true`

`ctx.kugou` 提供对 EchoMusic 内置酷狗音乐接口的访问。API 采用延迟加载，按需调用。

| 命名空间 | 示例 |
|----------|------|
| `ctx.kugou.music` | `ctx.kugou.music.getSongUrl(hash)` |
| `ctx.kugou.user` | `ctx.kugou.user.getUserDetail()` |
| `ctx.kugou.playlist` | `ctx.kugou.playlist.getUserPlaylists()` |
| `ctx.kugou.video` | `ctx.kugou.video.getVideoDetail(id)` |
| `ctx.kugou.search` | `ctx.kugou.search.search(keyword)` |
| `ctx.kugou.artist` | `ctx.kugou.artist.getArtistDetail(id)` |
| `ctx.kugou.album` | `ctx.kugou.album.getAlbumDetail(id)` |
| `ctx.kugou.comment` | `ctx.kugou.comment.getMusicComments(mixSongId)` |

> ⚠️ 插件仅传业务参数（`hash`、`id` 等），不传敏感凭证（token、dfid、mid）。主进程自动注入当前登录态。

---

## ⚡ 原生 API

### Electron 对象

```js
ctx.electron.platform  // "win32" | "darwin" | "linux"
```

可直接访问宿主 Electron API（如 `ctx.electron.miniPlayer?.show()`），但大部分场景应使用 `ctx` 封装的 API。

---

## 📋 插件管理

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.id` | 当前插件 ID（只读） | — |
| `ctx.manifest` | 当前插件 manifest.json（只读） | [Manifest](./manifest) |
| `ctx.dispose(fn)` | 注册清理函数（插件禁用时调用） | [概览](./) |
| `ctx.toast.info(msg)` / `success(msg)` / `warning(msg)` / `danger(msg)` | 提示消息 | — |
| `ctx.plugins.list()` | 列出所有插件 | [发布](./publishing#插件管理-api) |
| `ctx.plugins.installLocal(paths, opts?)` | 本地安装 | [发布](./publishing#本地安装) |
| `ctx.plugins.uninstall(pluginId)` | 卸载插件 | [发布](./publishing#卸载) |
| `ctx.plugins.setEnabled(id, enabled)` | 启用/禁用 | [发布](./publishing#安全模式与故障管理) |
| `ctx.plugins.setSafeMode(enabled)` | 全局安全模式 | [发布](./publishing#安全模式与故障管理) |
| `ctx.plugins.reportFailure(failure)` | 上报故障 | [发布](./publishing#故障上报) |
| `ctx.plugins.clearFailure(pluginId?)` | 清除故障记录 | [发布](./publishing#故障上报) |
| `ctx.plugins.marketplace.listSources()` | 列出插件源 | [发布](./publishing#源管理) |
| `ctx.plugins.marketplace.addSource(input)` | 添加插件源 | [发布](./publishing#源管理) |
| `ctx.plugins.marketplace.patchSource(id, patch)` | 修改源配置 | [发布](./publishing#源管理) |
| `ctx.plugins.marketplace.removeSource(id)` | 移除插件源 | [发布](./publishing#源管理) |
| `ctx.plugins.marketplace.list(opts?)` | 浏览在线插件 | [发布](./publishing#浏览与安装) |
| `ctx.plugins.marketplace.install(srcId, pId, opts?)` | 在线安装 | [发布](./publishing#浏览与安装) |

---

## 下一步

| 文档 | 内容 |
|------|------|
| [UI 扩展指南 →](./ui-extension) | 界面定制的深入实践 |
| [播放器与音频引擎 →](./player-audio) | 播放控制、播放队列、频谱、歌词系统 |
| [文件存储与数据 →](./filesystem-storage) | 文件系统、KV 存储、外观订阅 |
| [音频频谱 →](./audio-spectrum) | 实时 FFT 频谱数据 |
| [窗口与系统 →](./windows-system) | 浮窗、Now Playing、进程、图标 |
| [发布与分发 →](./publishing) | 插件源、市场、故障管理 |
| [内部 API 参考 →](../internal-api/) | 不暴露给插件的内部 API（mpv 引擎等） |
