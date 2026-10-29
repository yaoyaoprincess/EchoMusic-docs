---
title: API 总览
outline: [2, 4]
---

# 🔧 API 总览

`ctx` 对象是插件的核心入口。本文档按模块列出所有插件可用的 API 速查表，每个 API 标注了所属的详情文档以便深入了解。

> ℹ️ 本文档以主程序源码（`src/renderer/plugins/runtime/context.ts` 的 `EchoPluginContext`）为准逐项核对。插件市场统计属于独立子系统，详见 [热度与统计 →](./marketplace-stats)。

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
| `ctx.ui.addPage({id, title, icon?, component, sidebar?})` | 注册侧边栏独立页面（`sidebar` 可传配置对象） | [UI 扩展](./ui-extension#注册独立页面) |
| `ctx.ui.sidebar.addItem({id, title, icon?, pageId, ...})` | 为已注册页面添加侧边栏项 | [UI 扩展](./ui-extension#侧边栏项) |
| `ctx.ui.sidebar.shortcuts.register({id, title, pageId?, onClick?})` | 注册侧边栏快捷卡片 | [UI 扩展](./ui-extension#侧边栏快捷卡片) |
| `ctx.ui.titlebar.register({id, title, icon?, defaultPlacement?, onClick})` | 注册标题栏按钮 | [UI 扩展](./ui-extension#标题栏按钮) |
| `ctx.ui.playerbar.register({id, title, icon?, badge?, trigger?, ...})` | 注册播放栏按钮 | [UI 扩展](./ui-extension#播放栏按钮) |
| `ctx.ui.lyricsPage.register({id, component, ...})` | 注册自定义歌词页/换肤（需 `lyricsPage` 能力） | [歌词页换肤](./lyrics-page) |
| `ctx.ui.settings.define({title, component})` | 注册插件设置面板 | [UI 扩展](./ui-extension#设置面板) |
| `ctx.ui.addSongContextMenuItem({id, label, onSelect})` | 歌曲右键菜单项 | [UI 扩展](./ui-extension#歌曲右键菜单) |
| `ctx.ui.cover.setFallback({id, resolveUrl})` | 封面无法加载时的回退图片 | [UI 扩展](./ui-extension#封面回退) |
| `ctx.ui.mount(target, component, opts?)` | 挂载 Vue 组件到 DOM | [UI 扩展](./ui-extension#组件挂载) |
| `ctx.ui.teleport(component, opts?)` | 把组件 Teleport 到 `document.body` | [UI 扩展](./ui-extension#组件传送) |
| `ctx.ui.components.*` | 宿主预置组件（自动暴露 `ui/`、`music/`、`player/` 全部组件） | [UI 扩展](./ui-extension#预置组件) |
| `ctx.css.inject(css, {id?})` | 动态注入 CSS，返回清理函数（重复调用同 `id` 会先移除旧的） | [UI 扩展](./ui-extension#css-注入) |
| `ctx.dom.observe(selector, callback, opts?)` | 监听 DOM 节点出现（`opts`: `{root?, once?}`，回调可返回清理函数） | [UI 扩展](./ui-extension#dom-监听) |
| `ctx.dom.query(selector)` / `queryAll(selector)` | 在插件作用域内查询元素 | [UI 扩展](./ui-extension#dom-监听) |
| `ctx.commands.register(id, handler, {title?})` / `execute(id, ...args)` | 注册/执行插件命令 | — |

---

## 🎵 播放 & 音频

### 播放控制

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.player.play(trackId?, options?)` | 播放指定歌曲或恢复播放 | [播放器](./player-audio#播放控制) |
| `ctx.player.pause()` | 暂停 | [播放器](./player-audio#播放控制) |
| `ctx.player.toggle()` | 播放/暂停切换 | [播放器](./player-audio#播放控制) |
| `ctx.player.next()` / `prev()` | 队列内下一首 / 上一首 | [播放器](./player-audio#播放控制) |
| `ctx.player.stop()` | 停止 | [播放器](./player-audio#播放控制) |
| `ctx.player.playTrack(trackId, options?)` | 按 ID 播放指定歌曲 | [播放器](./player-audio#播放控制) |
| `ctx.player.playSong(song, options?)` | 播放歌曲对象（入队并播放） | [播放器](./player-audio#播放控制) |
| `ctx.player.playNext(song, options?)` / `playLast(song, options?)` | 把歌曲插播到当前播放之后 / 末尾 | [播放器](./player-audio#播放控制) |
| `ctx.player.replaceQueueAndPlay(songs, options?)` | 替换队列并播放 | [播放器](./player-audio#播放控制) |
| `ctx.player.seek(time)` | 跳转（秒） | [播放器](./player-audio#播放控制) |
| `ctx.player.setVolume(v)` | 设置音量（0-100） | [播放器](./player-audio#播放控制) |
| `ctx.player.setPlaybackRate(r)` | 倍速（0.5-3.0） | [播放器](./player-audio#播放控制) |
| `ctx.player.setPlayMode(m)` | 播放模式 | [播放器](./player-audio#播放控制) |
| `ctx.player.setAudioQuality(q)` | 音频品质 | [播放器](./player-audio#播放控制) |
| `ctx.player.setAudioEffect(e)` | 设置音效 | [播放器](./player-audio#播放控制) |
| `ctx.player.dislikePersonalFm()` | 私人 FM 不喜欢 | [播放器](./player-audio#播放控制) |
| `ctx.player.toggleLyricView(open?)` | 切换歌词视图 | [播放器](./player-audio#播放控制) |

### 播放状态（computed，只读响应式）

| 属性 | 类型 | 说明 |
|------|:--:|------|
| `currentTrack` | `computed` | 当前歌曲对象 |
| `currentTrackId` | `computed` | 当前歌曲 ID |
| `currentTime` / `duration` | `computed` | 播放进度 / 总时长（秒） |
| `isPlaying` / `isLoading` | `computed` | 是否播放中 / 加载中 |
| `playbackState` | `computed` | 播放状态显示值 |
| `playbackRate` | `computed` | 播放速率 |
| `volume` | `computed` | 音量（0-100） |
| `playMode` | `computed` | 播放模式 |
| `audioQuality` | `computed` | `{effective, resolved, override}` 音质信息 |
| `audioEffect` | `computed` | `{current, resolved}` 音效信息 |

### 播放队列

> 队列支持**多队列**模型：`queues` 为全部队列列表，`activeQueue` 为当前生效队列；多数操作可传 `queueId?` 指定队列，缺省操作 active 队列。

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.playlist.getActiveQueue()` | 获取当前生效队列 | [播放器](./player-audio#播放队列管理) |
| `ctx.playlist.getQueue(queueId)` | 获取指定队列 | [播放器](./player-audio#播放队列管理) |
| `ctx.playlist.getQueueSongs(queueId?)` | 获取队列歌曲列表 | [播放器](./player-audio#播放队列管理) |
| `ctx.playlist.queues` / `activeQueue` | 全部队列 / 当前队列（computed） | [播放器](./player-audio#播放队列管理) |
| `ctx.playlist.setActiveQueue(queueId)` | 切换生效队列 | [播放器](./player-audio#播放队列管理) |
| `ctx.playlist.replace(songs, options?)` | 替换队列内容 | [播放器](./player-audio#播放队列管理) |
| `ctx.playlist.replaceAndPlay(songs, options?)` | 替换队列并播放 | [播放器](./player-audio#播放队列管理) |
| `ctx.playlist.append(songs, options?)` | 追加歌曲到队列 | [播放器](./player-audio#播放队列管理) |
| `ctx.playlist.playNext(song, options?)` / `playLast(song, options?)` | 插播到当前之后 / 末尾 | [播放器](./player-audio#播放队列管理) |
| `ctx.playlist.enqueuePlayNext(songId)` / `enqueuePlayNextSequential(songId)` | 按 ID 插播（覆盖式 / 顺序排队） | [播放器](./player-audio#播放队列管理) |
| `ctx.playlist.remove(songId, queueId?)` | 移除歌曲 | [播放器](./player-audio#播放队列管理) |
| `ctx.playlist.reorder(fromIndex, toIndex, queueId?)` | 重排 | [播放器](./player-audio#播放队列管理) |
| `ctx.playlist.clear(queueId?)` | 清空队列 | [播放器](./player-audio#播放队列管理) |

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

> ℹ️ FFmpeg 引擎高级控制（EQ/空间音效/IR/设备/渐变等）属于内部 API，不在插件范围内。详见 [内部 API 参考 →](../internal-api/audio-engine)。

## 🌐 本地 HTTP 服务

> 需要 capability：`webServer: true`

| API | 说明 |
|-----|------|
| `ctx.webServer.listen(handler, opts?)` | 启动 HTTP 服务，默认监听 `127.0.0.1`，返回端口号 |
| `ctx.webServer.status()` | 获取当前服务状态 |
| `ctx.webServer.close()` | 关闭服务 |
| `ctx.webServer.onRequest(handler)` | 注册请求处理器 |

> 适合 Wallpaper Engine、OBS、本地脚本等桌面软件读取 EchoMusic 当前状态和歌词页面。插件禁用/卸载/安全模式/退出时自动释放端口。

---

## 🖥️ 桌面歌词 & Mini 播放器

> 桌面歌词与 Mini 播放器为独立窗口，与主窗口不共享 JS 内存。需在 manifest `runtime` 中声明对应字段。

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.desktopLyric.*` | 桌面歌词完整 API（快照订阅、显示/隐藏、锁定、设置更新） | [系统](./windows-system#桌面歌词) |
| `ctx.miniPlayer.*` | Mini 播放器完整 API（快照订阅、置顶、音量、进度） | [系统](./windows-system#mini-播放器) |
| `ctx.lyricEffects.register({ scope: "desktop", ... })` | 注册桌面歌词视觉效果（需 `lyricEffects: true`） | [播放器](./player-audio#歌词视觉效果) |

---

## 💾 数据 & 文件

### KV 存储

`ctx.storage` 提供按插件隔离的持久化 KV 存储。

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.storage.get(key)` | 读取键值 | [数据](./filesystem-storage#kv-存储) |
| `ctx.storage.set(key, value)` | 写入键值 | [数据](./filesystem-storage#kv-存储) |
| `ctx.storage.delete(key)` | 删除键值 | [数据](./filesystem-storage#kv-存储) |

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
| `ctx.appearance.getSnapshot()` | 外观快照：`{isDark, accentColor, fontFamily?, colors?, floatingSurfaceFrosted?}` | [数据](./filesystem-storage#外观订阅) |
| `ctx.appearance.onSnapshot(fn)` | 订阅外观变化 | [数据](./filesystem-storage#外观订阅) |
| `ctx.fonts.getAll()` | 系统字体名称列表 | — |
| `ctx.fonts.getOptions({includeSystem?, systemLabel?, followLabel?})` | 字体选项（可用于 Select 组件） | — |
| `ctx.fonts.buildFamily(name)` | 构建 CSS font-family 字符串 | — |

### SQLite 数据库

> 需要 capability：`sqlite: true`

插件私有 SQLite 数据库，按插件 id 隔离，由宿主托管。

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.sqlite.open({name?, readOnly?, busyTimeoutMs?, migrations?})` | 打开/创建数据库，默认库名 `main` | [数据](./filesystem-storage#sqlite-数据库) |
| `ctx.sqlite.listDatabases()` | 列出所有数据库 | [数据](./filesystem-storage#sqlite-数据库) |
| `ctx.sqlite.deleteDatabase(name?)` | 删除指定数据库 | [数据](./filesystem-storage#sqlite-数据库) |
| `db.exec(sql)` | 执行 SQL | [数据](./filesystem-storage#sqlite-数据库) |
| `db.run(sql, params?)` | 执行 INSERT/UPDATE/DELETE | [数据](./filesystem-storage#sqlite-数据库) |
| `db.get(sql, params?)` | 查询单行 | [数据](./filesystem-storage#sqlite-数据库) |
| `db.all(sql, params?)` | 查询多行 | [数据](./filesystem-storage#sqlite-数据库) |
| `db.transaction(sqls)` | 事务执行（**SQL 语句数组**） | [数据](./filesystem-storage#sqlite-数据库) |
| `db.close()` | 关闭连接 | [数据](./filesystem-storage#sqlite-数据库) |

> 支持 BLOB 参数，写入 `{ type: "hex", data }` 或 `{ type: "base64", data }`，查询返回 hex 字符串。

---

## 🪟 窗口 & 系统

### 窗口控制

> `windowId` 首参指定目标窗口（如插件声明的浮窗 ID）。

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.windows.show(windowId, options?)` | 显示窗口 | [系统](./windows-system#窗口控制) |
| `ctx.windows.hide(windowId)` | 隐藏窗口 | [系统](./windows-system#窗口控制) |
| `ctx.windows.close(windowId)` | 关闭窗口 | [系统](./windows-system#窗口控制) |
| `ctx.windows.move(windowId, bounds)` | 移动窗口 | [系统](./windows-system#窗口控制) |
| `ctx.windows.getBounds(windowId)` | 获取窗口位置和尺寸 | [系统](./windows-system#窗口控制) |
| `ctx.windows.setIgnoreMouseEvents(windowId, ignore)` | 鼠标穿透 | [系统](./windows-system#窗口控制) |

### Now Playing

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.nowPlaying.getSnapshot()` | 当前状态快照（嵌套结构：`snapshot.playback.title/artist` 等） | [系统](./windows-system#now-playing-浮窗) |
| `ctx.nowPlaying.onSnapshot(fn)` | 订阅状态变化 | [系统](./windows-system#now-playing-浮窗) |
| `ctx.nowPlaying.onCommand(fn)` | 监听命令 | [系统](./windows-system#now-playing-浮窗) |
| `ctx.nowPlaying.syncSnapshot(payload)` | 同步快照（含播放/歌词信息，替换旧版 syncPlayback/syncLyric） | [系统](./windows-system#now-playing-浮窗) |

### 进程管理

> 需要 capability：`process: true`

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.process.launch(opts)` | 启动插件目录内程序（`executable` 指定程序，首次运行需用户授权确认） | [系统](./windows-system#进程管理) |
| `ctx.process.terminate(pid)` | 终止已启动的进程（`pid` 必填） | [系统](./windows-system#进程管理) |

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
  mode: "out-in",          // 或 "in-out"
  appear: true,
  durationMs: 450,
  enterOpacity: 0,
  leaveOpacity: 0,
  enterTranslateY: 6,
  enterTranslateX: 0,
  leaveTranslateX: 0,
  enterScale: 1,
  leaveScale: 1,
  enterFilter: "none",
  leaveFilter: "none",
  name: "my-transition",   // 可选：自定义 transition 类名前缀
  css: "",                 // 可选：附加 CSS
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
  enabled: true,
  opacity: 1,
  midPosition: 0.5,
  midOpacity: 0.6,
  background: "",
  dark: {},                // 可选：暗色模式下的独立配置
});
ctx.theme.accentGradient.clear();
```

---

## 📜 滚动画布

`ctx.scroll` 提供页面滚动容器的高级控制，适合滚动增强类插件。

| API | 说明 |
|-----|------|
| `queryContainers({role?, visible?})` | 获取滚动容器（可按角色/可见性过滤） |
| `getCurrentContainer()` | 获取当前焦点容器 |
| `getState(el?)` | 获取滚动状态 |
| `scrollToTop(el?)` / `scrollToBottom(el?)` | 滚动到顶部 / 底部 |
| `scrollTo(el, target, options?)` | 精确滚动到指定元素或位置 |
| `selector` | 宿主滚动容器的 CSS 选择器 |
| `observeContainers(handler(el, state))` | 监听滚动容器变化 |

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
| `ctx.kugou.audioEffect` | 音效相关接口 |
| `ctx.kugou.blacklist` | 歌曲黑名单管理 |
| `ctx.kugou.channel` | 频道相关接口 |
| `ctx.kugou.importPlaylist` | 外部歌单导入 |
| `ctx.kugou.listenTogether` | 一起听相关接口 |
| `ctx.kugou.listeningPreferences` | 听歌偏好 |
| `ctx.kugou.purchased` | 已购音乐 |
| `ctx.kugou.recognize` | 听歌识曲相关接口 |

> ⚠️ 插件仅传业务参数（`hash`、`id` 等），不传敏感凭证（token、dfid、mid）。主进程自动注入当前登录态。

## 🔐 酷狗安全验证

> 需要 capability：`kugouVerification: true`

| API | 说明 |
|-----|------|
| `ctx.kugouVerification.request(challenge)` | 处理酷狗安全验证挑战，返回 `{ ok: true, eventId }` 或 `{ ok: false, error, canceled? }` |

---

## ⚡ 原生 API

### Electron 对象

```js
ctx.electron.platform  // "win32" | "darwin" | "linux"
```

可直接访问宿主 Electron API（如 `ctx.electron.miniPlayer?.show()`），但大部分场景应使用 `ctx` 封装的 API。

> ⚠️ **插件管理类方法在 `ctx.electron.plugins` 上，不在 `ctx.plugins`**——`EchoPluginContext` 顶层没有 `plugins` 成员，这是最常见的踩坑点。详见 [发布与分发 →](./publishing#插件管理-api)。

---

## 🧩 插件管理

> 这些方法位于 **`ctx.electron.plugins`**（管理面 API，非 `ctx.plugins`）。

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.electron.plugins.list()` | 列出所有插件 | [发布](./publishing#插件管理-api) |
| `ctx.electron.plugins.installLocal(paths, opts?)` | 本地安装 | [发布](./publishing#本地安装) |
| `ctx.electron.plugins.uninstall(pluginId, {removeData?})` | 卸载插件 | [发布](./publishing#卸载) |
| `ctx.electron.plugins.setEnabled(id, enabled)` | 启用/禁用 | [发布](./publishing#安全模式与故障管理) |
| `ctx.electron.plugins.setSafeMode(enabled)` | 全局安全模式 | [发布](./publishing#安全模式与故障管理) |
| `ctx.electron.plugins.reportFailure(failure)` | 上报故障 | [发布](./publishing#故障上报) |
| `ctx.electron.plugins.clearFailure(pluginId?)` | 清除故障记录 | [发布](./publishing#故障上报) |
| `ctx.electron.plugins.marketplace.listSources()` | 列出插件源 | [发布](./publishing#源管理) |
| `ctx.electron.plugins.marketplace.addSource(input)` | 添加插件源 | [发布](./publishing#源管理) |
| `ctx.electron.plugins.marketplace.patchSource(id, patch)` | 修改源配置 | [发布](./publishing#源管理) |
| `ctx.electron.plugins.marketplace.removeSource(id)` | 移除插件源 | [发布](./publishing#源管理) |
| `ctx.electron.plugins.marketplace.list(opts?)` | 浏览在线插件 | [发布](./publishing#浏览与安装) |
| `ctx.electron.plugins.marketplace.install(srcId, pId, opts?)` | 在线安装 | [发布](./publishing#浏览与安装) |

---

## 🌐 网络与下载

> 需要 capability：`unrestrictedNetwork`（request）/ `tcp`（TCP）/ `downloads`（下载）。详见 [网络与下载 →](./network)。

| API | 说明 |
|-----|------|
| `ctx.net.request(options)` | 主进程发起 HTTP 请求（绕过 CORS，支持自定义 TLS/超时/重定向） |
| `ctx.net.fetch(input, init?)` | 浏览器 fetch 语义 |
| `ctx.net.tcp.connect({host, port, ...})` | 建立 TCP 连接（读写、保活，连接上限 16） |
| `ctx.net.download(options)` | 断点续传下载（进度订阅、暂停/恢复、sha256 校验） |
| `ctx.net.downloads.{list,get,attach,remove}` | 下载任务管理 |

## 🖼️ Graphics 绘图

> 无需额外能力声明。详见 [Graphics 绘图 →](./graphics)。

| API | 说明 |
|-----|------|
| `ctx.graphics.getCapabilities({refresh?})` | 查询 WebGPU/HDR 能力 |
| `ctx.graphics.createCanvas({dynamicRange, ...})` | 创建 HDR/SDR 绘图画布（自动回退） |
| `ctx.graphics.onCapabilitiesChanged(cb)` | 订阅能力变化 |

## 🛰️ 服务请求拦截

> 需要 capability：`serverIntercept`。详见 [服务请求拦截 →](./server-intercept)。

| API | 说明 |
|-----|------|
| `ctx.server.intercept(interceptor, {priority?, match?, name?})` | 拦截主程序发往 API server 的请求（可读取、修改、Mock、转发） |

## 📋 任务面板

| API | 说明 |
|-----|------|
| `ctx.tasks.register({id, name, status, ...})` | 注册会话式任务（进度、取消、操作按钮），返回句柄 `{update, finish, dismiss, ...}` |

## 💾 备份与恢复

> 需要 capability：`backups`。详见 [备份与恢复 →](./backups)。

| API | 说明 |
|-----|------|
| `ctx.backups.create(scope?, settingsData?)` | 创建应用备份 |
| `ctx.backups.inspect(data)` | 校验备份并获取恢复令牌 |
| `ctx.backups.restore(token, scope?)` | 从备份恢复（成功后自动重启） |
| `ctx.backups.registerProvider({id, name, ...})` | 注册自定义备份提供者 |

## 🧭 其他

| API | 说明 |
|-----|------|
| `ctx.id` / `ctx.manifest` | 当前插件 ID 与 manifest（只读） |
| `ctx.descriptor` | 插件描述符：`installSource`、`directory`、`compatibility` 等 |
| `ctx.dispose(fn)` | 注册清理函数（插件禁用时调用） |
| `ctx.toast.info(msg)` / `success(msg)` / `warning(msg)` / `danger(msg)` / `show(opts)` | 提示消息 |
| `ctx.events` | 播放事件订阅：`onTrackChange / onPlaybackChange / onPlaybackStateChange / onPlay({immediate?}) / onPause / onEnded / onSeek / onError / onTimeUpdate / on(event, ...)` |
| `ctx.shortcuts.register(accelerator, handler)` | 应用内快捷键 |
| `ctx.shortcuts.registerGlobal(accelerator, handler)` | 系统全局快捷键（冲突时抛错） |
| `ctx.commands.register(id, handler, {title?})` / `execute(id, ...args)` | 注册 / 执行插件命令 |
| `ctx.host.showOnTop(target?, {focus?})` | 把 `'main'` 或 `'mini-player'` 窗口带到最前 |

---

## 下一步

| 文档 | 内容 |
|------|------|
| [UI 扩展指南 →](./ui-extension) | 界面定制的深入实践 |
| [播放器与音频引擎 →](./player-audio) | 播放控制、播放队列、频谱、歌词系统 |
| [文件存储与数据 →](./filesystem-storage) | 文件系统、KV 存储、授权文件、外观订阅 |
| [音频频谱 →](./audio-spectrum) | 实时 FFT 频谱数据 |
| [窗口与系统 →](./windows-system) | 浮窗、Now Playing、任务栏、进程、图标 |
| [网络与下载 →](./network) | 主进程请求、TCP、下载引擎 |
| [Graphics 绘图 →](./graphics) | HDR/WebGPU 绘图画布 |
| [服务请求拦截 →](./server-intercept) | 拦截 API server 请求 |
| [任务面板 →](./tasks) | 会话式任务注册与更新 |
| [备份与恢复 →](./backups) | 应用备份与自定义备份提供者 |
| [歌词页换肤 →](./lyrics-page) | 自定义歌词页与皮肤 |
| [热度与统计 →](./marketplace-stats) | 插件热度口径与查询接口 |
| [发布与分发 →](./publishing) | 插件源、市场、故障管理 |
