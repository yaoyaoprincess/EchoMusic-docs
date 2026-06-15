---
title: API 总览
outline: [2, 4]
---

# 🔧 API 总览

`ctx` 对象是插件的核心入口。本文档按模块列出全部 ~120 个 API 的速查表，每个 API 标注了所属的详情文档以便深入了解。

---

## 🏗️ 宿主运行时

| API | 类型 | 说明 | 详见 |
|-----|------|------|:--:|
| `ctx.vue` | Vue 3 运行时 | `defineComponent` / `h` / `ref` / `computed` / `watch` / `onMounted` / `onUnmounted` / `defineAsyncComponent` | — |
| `ctx.app` | App 实例 | 主应用 Vue App 实例 | — |
| `ctx.router` | Router 实例 | Vue Router 实例 | — |
| `ctx.pinia` | Pinia 实例 | Pinia 状态管理实例 | — |

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
| `ctx.ui.addPage({id, title, icon?, component, order?})` | 注册侧边栏独立页面 | [UI 扩展](./ui-extension#注册独立页面) |
| `ctx.ui.settings.define({title, component})` | 注册插件设置面板 | [UI 扩展](./ui-extension#设置面板) |
| `ctx.ui.addSongContextMenuItem({id, label, onSelect})` | 歌曲右键菜单项 | [UI 扩展](./ui-extension#歌曲右键菜单) |
| `ctx.ui.addPlayerButton({id, icon, label?, onClick, order?})` | 播放器控制栏按钮 | [UI 扩展](./ui-extension#播放器按钮) |
| `ctx.ui.mount(el, component)` | 挂载 Vue 组件到 DOM | [UI 扩展](./ui-extension#组件挂载) |
| `ctx.ui.teleport(selector, component)` | Teleport 组件 | [UI 扩展](./ui-extension#组件传送) |
| `ctx.ui.components.Button` | 预置按钮组件 | [UI 扩展](./ui-extension#设置面板) |
| `ctx.ui.components.Switch` | 预置开关组件 | [UI 扩展](./ui-extension#设置面板) |
| `ctx.ui.components.Input` | 预置输入框组件 | [UI 扩展](./ui-extension#设置面板) |
| `ctx.css.inject(css)` | 动态注入 CSS（卸载时自动移除） | [UI 扩展](./ui-extension#css-注入) |
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
| `ctx.player.setSpeed(s)` | 倍速（0.5-3.0） | [播放器](./player-audio#播放控制) |
| `ctx.player.setPlayMode(m)` | 播放模式 | [播放器](./player-audio#播放控制) |
| `ctx.player.setAudioQuality(q)` | 音频品质 | [播放器](./player-audio#播放控制) |
| `ctx.player.setAudioEffect(e)` | 设置音效 | [播放器](./player-audio#播放控制) |
| `ctx.player.isPlaying` | Ref\<boolean\>（响应式） | [播放器](./player-audio#播放状态) |
| `ctx.player.currentTime` | Ref\<number\>（响应式） | [播放器](./player-audio#播放状态) |
| `ctx.player.duration` | Ref\<number\>（响应式） | [播放器](./player-audio#播放状态) |
| `ctx.player.currentTrack` | Ref（响应式） | [播放器](./player-audio#播放状态) |
| `ctx.player.playMode` | Ref（响应式） | [播放器](./player-audio#播放状态) |
| `ctx.player.volume` | Ref（响应式） | [播放器](./player-audio#播放状态) |

### 播放队列

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.player.playlist.getQueue()` | 获取当前队列 | [播放器](./player-audio#播放队列管理) |
| `ctx.player.playlist.append(items)` | 追加歌曲 | [播放器](./player-audio#播放队列管理) |
| `ctx.player.playlist.remove(songId)` | 移除歌曲 | [播放器](./player-audio#播放队列管理) |
| `ctx.player.playlist.clear()` | 清空队列 | [播放器](./player-audio#播放队列管理) |
| `ctx.player.playlist.replace(items)` | 替换整个队列 | [播放器](./player-audio#播放队列管理) |
| `ctx.player.playlist.reorder(from, to)` | 重排 | [播放器](./player-audio#播放队列管理) |
| `ctx.player.playlist.setCurrentTrack(songId)` | 切歌 | [播放器](./player-audio#播放队列管理) |

### mpv 引擎高级控制

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.audio.setEqualizer(gains)` | 18段 EQ（-12~+12 dB） | [播放器](./player-audio#均衡器) |
| `ctx.audio.setSpatialAudio({preset, dryWet})` | 空间音效 | [播放器](./player-audio#空间音效) |
| `ctx.audio.setImpulseResponse(path\|{path,dryWet})` | IR 卷积 | [播放器](./player-audio#脉冲响应) |
| `ctx.audio.setAudioDevice(name)` | 切换输出设备 | [播放器](./player-audio#音频设备控制) |
| `ctx.audio.getAudioDevices()` | 获取设备列表 | [播放器](./player-audio#音频设备控制) |
| `ctx.audio.setExclusive(bool)` | 独占模式 | [播放器](./player-audio#音频设备控制) |
| `ctx.audio.getAudioFilter()` | 当前音效滤波器 | [播放器](./player-audio#音频设备控制) |
| `ctx.audio.fade(from, to, ms)` | 音量渐变 | [播放器](./player-audio#音量渐变) |
| `ctx.audio.cancelFade()` | 取消渐变 | [播放器](./player-audio#音量渐变) |
| `ctx.audio.pauseWithFade(v, ms)` | 渐弱暂停 | [播放器](./player-audio#音量渐变) |
| `ctx.audio.playWithFade(v, ms)` | 渐强恢复 | [播放器](./player-audio#音量渐变) |
| `ctx.audio.setNormalizationGain(dB)` | 响度归一化 | [播放器](./player-audio#响度归一化) |
| `ctx.audio.loadFile(url, track?)` | 加载文件/MKV | [播放器](./player-audio#文件和循环) |
| `ctx.audio.getTrackList()` | MKV 轨道列表 | [播放器](./player-audio#文件和循环) |
| `ctx.audio.setLoopFile(bool)` | 单曲循环 | [播放器](./player-audio#文件和循环) |
| `ctx.audio.setMediaTitle(title)` | 设置媒体标题 | [播放器](./player-audio#文件和循环) |
| `ctx.audio.available()` | 引擎是否可用 | [播放器](./player-audio#引擎控制) |
| `ctx.audio.restart()` | 重启引擎 | [播放器](./player-audio#引擎控制) |
| `ctx.audio.getState()` | 内部状态 | [播放器](./player-audio#引擎控制) |

### 音频事件

| API | 回调参数 | 详见 |
|-----|----------|:--:|
| `ctx.audio.onTimeUpdate(fn)` | `(time)` | [播放器](./player-audio#核心事件) |
| `ctx.audio.onDurationChange(fn)` | `(duration)` | [播放器](./player-audio#核心事件) |
| `ctx.audio.onStateChange(fn)` | `({playing?, paused?})` | [播放器](./player-audio#核心事件) |
| `ctx.audio.onPlaybackEnd(fn)` | `(reason)` | [播放器](./player-audio#核心事件) |
| `ctx.audio.onError(fn)` | `(msg)` | [播放器](./player-audio#核心事件) |
| `ctx.audio.onAudioDeviceListChanged(fn)` | `(devices[])` | [播放器](./player-audio#设备事件) |
| `ctx.audio.onImpulseResponseDisabled(fn)` | `({path?, reason?})` | [播放器](./player-audio#设备事件) |

### 音频频谱

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.audio.spectrum.getStatus()` | 获取捕获状态 | [频谱](./audio-spectrum#getstatus) |
| `ctx.audio.spectrum.getSnapshot()` | 单帧频谱快照 | [频谱](./audio-spectrum#getsnapshot) |
| `ctx.audio.spectrum.subscribe(opts, cb, meta?)` | 实时订阅频谱 | [频谱](./audio-spectrum#subscribe) |

### 自定义音源 & 歌词

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.player.audioSource.register(opts)` | 注册音源解析器 | [播放器](./player-audio#自定义音源) |
| `ctx.lyrics.registerResolver(opts)` | 注册歌词解析器 | [播放器](./player-audio#注册歌词解析器) |
| `ctx.lyrics.getSnapshot()` | 歌词状态快照 | [播放器](./player-audio#获取订阅歌词快照) |
| `ctx.lyrics.onSnapshot(fn)` | 订阅歌词变化 | [播放器](./player-audio#获取订阅歌词快照) |
| `ctx.lyricEffects.register(opts)` | 注册歌词动效 | [播放器](./player-audio#歌词视觉效果) |

---

## 💾 数据 & 文件

### KV 存储

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.storage.kvGet(key)` | 读取键值 | [数据](./filesystem-storage#kv-存储) |
| `ctx.storage.kvSet(key, value)` | 写入键值 | [数据](./filesystem-storage#kv-存储) |
| `ctx.storage.kvDelete(key)` | 删除键值 | [数据](./filesystem-storage#kv-存储) |

### 播放队列持久化

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.storage.playbackGetSnapshot()` | 播放状态快照 | [数据](./filesystem-storage#播放队列持久化) |
| `ctx.storage.playbackGetQueue()` | 完整队列 | [数据](./filesystem-storage#播放队列持久化) |
| `ctx.storage.playbackReplaceQueue(items)` | 替换队列 | [数据](./filesystem-storage#播放队列持久化) |
| `ctx.storage.playbackAppendQueueItems(items)` | 追加歌曲 | [数据](./filesystem-storage#播放队列持久化) |
| `ctx.storage.playbackRemoveQueueItem(id)` | 移除歌曲 | [数据](./filesystem-storage#播放队列持久化) |
| `ctx.storage.playbackReorderQueueItems(from,to)` | 重排 | [数据](./filesystem-storage#播放队列持久化) |
| `ctx.storage.playbackSetCurrentTrack(id)` | 设置当前曲目 | [数据](./filesystem-storage#播放队列持久化) |
| `ctx.storage.playbackUpdateMeta(meta)` | 更新队列元数据 | [数据](./filesystem-storage#播放队列持久化) |

### 文件系统

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.fs.listFiles(opts)` | 扫描目录 | [数据](./filesystem-storage#文件系统) |
| `ctx.fs.listImageFiles(opts)` | 扫描图片 | [数据](./filesystem-storage#文件系统) |
| `ctx.fs.readTextFile(opts)` | 读取文本文件 | [数据](./filesystem-storage#文件系统) |
| `ctx.fs.readFileBytes(opts)` | 读取二进制 | [数据](./filesystem-storage#文件系统) |
| `ctx.fs.writeFile(opts)` | 写入文件 | [数据](./filesystem-storage#文件系统) |
| `ctx.fs.deleteFile(path)` | 删除文件 | [数据](./filesystem-storage#文件系统) |
| `ctx.fs.getFileUrl(path)` | 获取播放 URL | [数据](./filesystem-storage#文件系统) |

### HTTP & 事件

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.api.request(config)` | HTTP 请求 | [数据](./filesystem-storage#http-请求) |
| `ctx.events.onTrackChange(fn)` | 歌曲切换 | [数据](./filesystem-storage#事件监听) |
| `ctx.events.onPlayStateChange(fn)` | 播放/暂停 | [数据](./filesystem-storage#事件监听) |
| `ctx.events.onVolumeChange(fn)` | 音量变化 | [数据](./filesystem-storage#事件监听) |
| `ctx.appearance.getSnapshot()` | 外观快照 | [数据](./filesystem-storage#外观订阅) |
| `ctx.appearance.onSnapshot(fn)` | 订阅外观变化 | [数据](./filesystem-storage#外观订阅) |

---

## 🪟 窗口 & 系统

### 浮窗

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.window.show(pluginId, windowId, opts?)` | 显示浮窗 | [系统](./windows-system#浮窗管理) |
| `ctx.window.hide(pluginId, windowId)` | 隐藏浮窗 | [系统](./windows-system#浮窗管理) |
| `ctx.window.getContext()` | 浮窗上下文 | [系统](./windows-system#浮窗管理) |

### 桌面歌词

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.desktopLyric.getSnapshot()` | 状态快照 | [系统](./windows-system#桌面歌词) |
| `ctx.desktopLyric.show()` / `hide()` / `toggleLock()` | 显示/隐藏/锁定 | [系统](./windows-system#桌面歌词) |
| `ctx.desktopLyric.updateSettings(s)` | 更新设置 | [系统](./windows-system#桌面歌词) |
| `ctx.desktopLyric.onSnapshot(fn)` | 订阅状态 | [系统](./windows-system#桌面歌词) |
| `ctx.desktopLyric.command(cmd)` | 发送命令 | [系统](./windows-system#桌面歌词) |
| `ctx.desktopLyric.setIgnoreMouseEvents(bool)` | 鼠标穿透 | [系统](./windows-system#桌面歌词) |

### Mini 播放器

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.miniPlayer.getSnapshot()` | 状态快照 | [系统](./windows-system#mini-播放器) |
| `ctx.miniPlayer.show()` / `hide()` / `toggle()` | 显示/隐藏/切换 | [系统](./windows-system#mini-播放器) |
| `ctx.miniPlayer.setExpanded(bool)` | 展开/收缩 | [系统](./windows-system#mini-播放器) |
| `ctx.miniPlayer.setAlwaysOnTop(bool)` | 置顶 | [系统](./windows-system#mini-播放器) |
| `ctx.miniPlayer.getBounds()` / `move(x, y)` | 位置/尺寸 | [系统](./windows-system#mini-播放器) |
| `ctx.miniPlayer.onSnapshot(fn)` | 订阅状态 | [系统](./windows-system#mini-播放器) |
| `ctx.miniPlayer.onCommand(fn)` | 命令监听 | [系统](./windows-system#mini-播放器) |

### Now Playing

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.nowPlaying.getSnapshot()` | 状态快照 | [系统](./windows-system#now-playing-浮窗) |
| `ctx.nowPlaying.onSnapshot(fn)` | 订阅状态 | [系统](./windows-system#now-playing-浮窗) |
| `ctx.nowPlaying.command(cmd)` / `onCommand(fn)` | 命令 | [系统](./windows-system#now-playing-浮窗) |

### 其他系统 API

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.shortcuts.register({enabled, shortcutMap})` | 注册快捷键 | [系统](./windows-system#快捷键) |
| `ctx.shortcuts.refresh()` | 刷新快捷键 | [系统](./windows-system#快捷键) |
| `ctx.shortcuts.onTrigger(fn)` | 监听触发 | [系统](./windows-system#快捷键) |
| `ctx.tray.syncPlayback(state)` | 同步托盘状态 | [系统](./windows-system#系统托盘) |
| `ctx.tray.onSetPlayMode(fn)` | 托盘模式切换 | [系统](./windows-system#系统托盘) |
| `ctx.windowControl(action)` | 最大化/最小化/关闭/全屏 | [系统](./windows-system#窗口控制) |
| `ctx.power.onSuspend(fn)` | 系统休眠 | [系统](./windows-system#电源事件) |
| `ctx.power.onResume(fn)` | 系统唤醒 | [系统](./windows-system#电源事件) |
| `ctx.process.launch(opts)` | 启动程序 | [系统](./windows-system#进程管理) |
| `ctx.process.terminate()` | 终止进程 | [系统](./windows-system#进程管理) |
| `ctx.icons.refresh()` | 刷新图标 | [系统](./windows-system#应用图标) |
| `ctx.icons.setRuntimeWindowIcon(path)` | 设置窗口图标 | [系统](./windows-system#应用图标) |
| `ctx.icons.restoreDefaultWindowIcon()` | 恢复窗口图标 | [系统](./windows-system#应用图标) |
| `ctx.icons.restoreDefaultDesktopIcon()` | 恢复桌面图标 | [系统](./windows-system#应用图标) |
| `ctx.icons.restoreDefaultTaskbarIcon()` | 恢复任务栏图标 | [系统](./windows-system#应用图标) |
| `ctx.appInfo.get()` | 应用信息 | [系统](./windows-system#应用信息) |
| `ctx.appInfo.getChangelog()` | 更新日志 | [系统](./windows-system#应用信息) |
| `ctx.updater.download()` / `install(silent?)` | 更新 | [系统](./windows-system#更新器) |
| `ctx.updater.onDownloadStatus(fn)` | 下载进度 | [系统](./windows-system#更新器) |
| `ctx.apiServer.start()` / `status()` | 本地 API 服务 | [系统](./windows-system#api-服务器) |
| `ctx.fonts.getAll()` | 系统字体列表 | [系统](./windows-system#字体) |
| `ctx.audioEffects.importImpulseResponse()` | 导入 IR 文件 | [系统](./windows-system#音频特效管理) |
| `ctx.audioEffects.deleteImpulseResponse(path)` | 删除 IR | [系统](./windows-system#音频特效管理) |
| `ctx.logger.info/error/warn/debug(...)` | 结构化日志 | [系统](./windows-system#日志) |
| `ctx.logging.get()` / `update(s)` | 日志设置 | [系统](./windows-system#日志) |

---

## 📋 插件管理

| API | 说明 | 详见 |
|-----|------|:--:|
| `ctx.manifest` | 只读，当前插件 manifest.json | [Manifest](./manifest) |
| `ctx.dispose(fn)` | 注册清理函数 | [概览](./) |
| `ctx.toast.success(msg)` | 绿色成功提示 | [概览](./) |
| `ctx.toast.info(msg)` | 蓝色信息提示 | [概览](./) |
| `ctx.toast.error(msg)` | 红色错误提示 | [概览](./) |
| `ctx.dialog.open(opts)` | 打开系统对话框 | — |
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
| [播放器与音频引擎 →](./player-audio) | 播放控制、EQ、空间音效、歌词系统 |
| [文件存储与数据 →](./filesystem-storage) | FS、KV、播放队列持久化、事件 |
| [音频频谱 →](./audio-spectrum) | 实时 FFT 频谱数据 |
| [窗口与系统 →](./windows-system) | 浮窗、桌面歌词、Mini、快捷键 |
| [发布与分发 →](./publishing) | 插件源、市场、故障管理 |
