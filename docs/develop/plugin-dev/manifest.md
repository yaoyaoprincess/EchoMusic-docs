---
title: Manifest 配置参考
outline: [2, 4]
---

# 📋 Manifest 配置参考

`manifest.json` 是插件的心脏——它定义了插件的身份、能力、运行时环境和版本要求。本文档逐字段说明所有配置项。

## 完整示例

```json
{
  "id": "my-awesome-plugin",
  "name": "My Awesome Plugin",
  "version": "1.0.0",
  "description": "一个功能强大的 EchoMusic 插件",
  "author": "EchoMusic User",
  "icon": "icon.svg",
  "main": "index.js",
  "style": "style.css",
  "tags": ["tool"],
  "runtime": {
    "miniPlayer": false,
    "desktopLyric": true
  },
  "capabilities": {
    "audioSpectrum": true,
    "lyrics": true,
    "localFiles": true
  },
  "requires": {
    "echoMusicVersion": ">=2.3.2 <3"
  },
  "contributes": {
    "windows": [
      {
        "id": "my-float",
        "title": "我的浮窗",
        "main": "float.js",
        "defaultWidth": 360,
        "defaultHeight": 200
      }
    ]
  }
}
```

---

## 基础字段

### id

| 属性 | 值 |
|------|-----|
| 类型 | `string` |
| 必选 | ✅ |
| 格式 | kebab-case（推荐） |

插件唯一标识符。这个 ID 在整个 EchoMusic 中必须是唯一的。

```json
"id": "my-awesome-plugin"
```

- 建议使用 `kebab-case` 格式：小写字母 + 连字符
- 避免与其他插件冲突的通用名称
- 卸载时 EchoMusic 用此 ID 定位插件目录和 KV 数据

---

### name

| 属性 | 值 |
|------|-----|
| 类型 | `string` |
| 必选 | ✅ |

插件在管理页面显示的**人类可读**名称。

```json
"name": "My Awesome Plugin"
```

- 支持中文、Emoji 等任意字符
- 长度建议在 30 个字符以内
- 可以与其他插件的 name 重复（但 id 不能重复）

---

### version

| 属性 | 值 |
|------|-----|
| 类型 | `string` |
| 必选 | ✅ |
| 格式 | [Semantic Versioning](https://semver.org/lang/zh-CN/) |

```json
"version": "1.2.3"
```

- 遵循 MAJOR.MINOR.PATCH 格式
- 在线插件源会根据版本号判断是否有更新
- 版本升级时的惯例：
  - PATCH（1.0.0 → 1.0.1）：Bug 修复，向后兼容
  - MINOR（1.0.0 → 1.1.0）：新增功能，向后兼容
  - MAJOR（1.0.0 → 2.0.0）：破坏性变更

---

### description

| 属性 | 值 |
|------|-----|
| 类型 | `string` |
| 必选 | ❌ |

插件简短描述，显示在插件管理页面。

```json
"description": "一个功能强大的 EchoMusic 插件"
```

- 建议控制在 100 字以内
- 简明扼要地说明插件的核心功能

---

### author

| 属性 | 值 |
|------|-----|
| 类型 | `string` |
| 必选 | ❌ |

插件作者名称，显示在插件管理页面。

```json
"author": "EchoMusic User"
```

---

### tags

| 属性 | 值 |
|------|-----|
| 类型 | `string[]` |
| 必选 | ❌ |

插件标签数组，可用于分类或筛选（`echo-plugins.json` 中的 `tags` 字段用于插件源目录归类）。

```json
"tags": ["lyrics", "tool"]
```

---

### downloadUrl

| 属性 | 值 |
|------|-----|
| 类型 | `string` |
| 必选 | ❌ |

插件包的直接下载地址（可选）。未提供时，在线插件源按插件源仓库路径下载。

```json
"downloadUrl": "https://example.com/releases/my-plugin-1.2.3.zip"
```

---

### icon

| 属性 | 值 |
|------|-----|
| 类型 | `string` |
| 必选 | ❌ |

插件图标。支持三种形式：

```json
// 1. 相对路径（插件目录内）
"icon": "icon.svg"

// 2. HTTPS URL
"icon": "https://example.com/icon.png"

// 3. data: URI（内联 Base64）
"icon": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0..."
```

- 推荐使用 **SVG**（矢量、体积小）
- PNG 也可，建议 128×128 以上
- 如果未提供，EchoMusic 会显示默认图标

---

### main

| 属性 | 值 |
|------|-----|
| 类型 | `string` |
| 必选 | ❌ |
| 默认值 | `"index.js"` |

插件入口 JavaScript 文件。路径相对于插件目录。

```json
"main": "index.js"
```

- 支持 `.js` 和 `.mjs` 扩展名
- 入口文件运行在浏览器 ESM 环境，**不能使用** `require()` 或 Node.js 内置模块

---

### style

| 属性 | 值 |
|------|-----|
| 类型 | `string` |
| 必选 | ❌ |

插件样式文件。路径相对于插件目录，仅支持 `.css`。

```json
"style": "style.css"
```

- 该 CSS 文件会被注入到**插件所在的所有窗口**
- 如果 `runtime.miniPlayer: true`，CSS 也会注入 Mini 播放器窗口

---

## runtime（运行时）

控制插件在哪些窗口中被加载。

```json
"runtime": {
  "miniPlayer": false,
  "desktopLyric": true
}
```

| 字段 | 类型 | 默认值 | 说明 |
|------|------|:---:|------|
| `miniPlayer` | `boolean` | `false` | 是否在 Mini 播放器窗口中加载 |
| `desktopLyric` | `boolean` | `false` | 是否在桌面歌词窗口中加载。改变桌面歌词布局、动效或尺寸时，需同时使用 `ctx.lyricEffects.register({ scope: "desktop" })` 和 `ctx.desktopLyric`。 |

### 使用场景

| 场景 | miniPlayer | desktopLyric |
|------|:--:|:--:|
| 添加主窗口设置面板 | ❌ | ❌ |
| 在 Mini 播放器显示自定义 UI | ✅ | ❌ |
| 在桌面歌词上叠加动效 | ❌ | ✅ |
| 跨窗口通信（高级） | ✅ | ✅ |

> ⚠️ 主窗口、Mini 播放器、桌面歌词是**三个独立的渲染进程**，JS 内存不共享。如果插件需要在 Mini 播放器中也显示，必须同时开启 `miniPlayer`。

---

## capabilities（能力声明）

插件对敏感 API 的访问采用**显式声明**。只声明插件实际需要的 capability。

```json
"capabilities": {
  "audioSource": false,
  "audioSpectrum": true,
  "backups": false,
  "downloads": false,
  "kugouApi": false,
  "kugouVerification": false,
  "localFiles": true,
  "lyricEffects": false,
  "lyrics": true,
  "lyricsPage": false,
  "process": false,
  "serverIntercept": false,
  "sqlite": false,
  "tcp": false,
  "theme": false,
  "unrestrictedNetwork": false,
  "webServer": false
}
```

### 各能力详解

#### audioSource

| 属性 | 值 |
|------|-----|
| 授予 | `ctx.player.audioSource.register()` |

接管特定平台或特定歌曲的**音源解析**。开发自定义音源插件（如接入第三方音乐平台 API）时需要开启。

```js
// 需要使用 audioSource 能力
ctx.player.audioSource.register({
  id: "my-platform-resolver",
  position: "after-catalog", // 兜底级别，旧插件默认 before-catalog
  async resolve({ track, quality }) {
    const response = await fetch(`https://api.example.com/song/${track.id}`);
    const data = await response.json();
    return data.streamUrl; // 返回 URL 字符串，或 Partial<ResolvedAudioSource> 对象
  },
});
```

#### audioSpectrum

| 属性 | 值 |
|------|-----|
| 授予 | `ctx.audio.spectrum` |

读取或订阅**实时音频频谱数据**。适用于可视化频谱、均衡器、VU 表等插件。详见 [音频频谱 →](./audio-spectrum)。

```js
// 需要使用 audioSpectrum 能力
ctx.audio.spectrum.subscribe({ fps: 30, binCount: 48 }, (frame) => {
  // frame.bins 为频谱数据数组，frame.waveform 为可选波形数据
  drawVisualizer(frame.bins);
});
```

#### backups

| 属性 | 值 |
|------|-----|
| 授予 | `ctx.backups` |

创建与恢复**应用备份**，或把插件自己的存储后端注册为备份提供者。详见[备份与恢复 →](./backups)。

#### downloads

| 属性 | 值 |
|------|-----|
| 授予 | `ctx.net.download` / `ctx.net.downloads` |

使用宿主**下载引擎**进行断点续传下载（进度订阅、暂停/恢复、sha256 校验）。详见[网络与下载 →](./network)。

#### lyricsPage

| 属性 | 值 |
|------|-----|
| 授予 | `ctx.ui.lyricsPage` |

注册**自定义歌词页与换肤方案**（`register/usePage/useSkin/openSkins`）。详见[歌词页换肤 →](./lyrics-page)。

#### theme

| 属性 | 值 |
|------|-----|
| 授予 | `ctx.theme.register` |

注册**完整应用主题**（亮/暗色 variants、颜色 token、背景与装饰）。详见[主题相关章节](./filesystem-storage#主题相关)。

#### tcp

| 属性 | 值 |
|------|-----|
| 授予 | `ctx.net.tcp.connect` |

建立**原始 TCP 连接**（读写、超时与保活配置，连接上限 16）。详见[网络与下载 →](./network#tcp-客户端)。

#### unrestrictedNetwork

| 属性 | 值 |
|------|-----|
| 授予 | `ctx.net.request` |

通过**主进程发起网络请求**（绕过渲染进程 CORS 限制，支持自定义 TLS/超时/重定向策略）。详见[网络与下载 →](./network)。

#### serverIntercept

| 属性 | 值 |
|------|-----|
| 授予 | `ctx.server.intercept` |

**拦截主程序发往 API server 的请求**（读取、修改、Mock 或转发）。详见[服务请求拦截 →](./server-intercept)。

#### kugouApi

| 属性 | 值 |
|------|-----|
| 授予 | `ctx.kugou` |

调用**酷狗音乐 API** 进行搜索、获取歌曲详情、获取播放链接等。

#### kugouVerification

| 属性 | 值 |
|------|-----|
| 授予 | `ctx.kugouVerification.request(challenge)` |

处理酷狗安全验证挑战。当酷狗需要滑块/验证码等验证时，插件可替代宿主接管验证流程。

```js
// 需要使用 kugouVerification 能力
const result = await ctx.kugouVerification.request({ challenge: "..." });
// result: { ok: true, eventId: "..." } 或 { ok: false, error: "...", canceled: true }
```

#### localFiles

| 属性 | 值 |
|------|-----|
| 授予 | `ctx.fs` |

扫描、读取文件系统中的音频文件，或在插件目录内写入数据。详见 [文件存储与数据 →](./filesystem-storage)。

#### lyricEffects

| 属性 | 值 |
|------|-----|
| 授予 | `ctx.lyricEffects.register()` |

注册**歌词视觉动效**（页面歌词和桌面歌词），通过 CSS 注入或 overlay 装饰层实现。桌面歌词需使用 `scope: "desktop"`。详见 [播放器与音频引擎 →](./player-audio#歌词视觉效果)。

#### lyrics

| 属性 | 值 |
|------|-----|
| 授予 | `ctx.lyrics.registerResolver()` |

为歌曲提供**自定义歌词解析器**。适用于接入第三方歌词源。详见 [播放器与音频引擎 →](./player-audio#注册歌词解析器)。

#### process

| 属性 | 值 |
|------|-----|
| 授予 | `ctx.process.launch()` |

启动**插件目录内的本机程序**。适用于需要调用外部工具的场景。详见 [窗口与系统 →](./windows-system#进程管理)。

> ⚠️ 此能力允许执行任意本地程序，只对可信插件开启。

#### webServer

| 属性 | 值 |
|------|-----|
| 授予 | `ctx.webServer` |

创建**本地 HTTP 服务**，供本机其他软件（Wallpaper Engine、OBS、本地脚本等）访问 EchoMusic 状态、歌词页面或可视化页面。服务默认监听 `127.0.0.1`，插件禁用/卸载/安全模式/退出时自动释放端口。

```js
// 需要 webServer 能力
ctx.webServer.listen(async (req) => {
  return { status: 200, body: JSON.stringify({ playing: ctx.player.currentTrack }) }
}).then(port => console.log('Server on port', port))
```

#### sqlite

| 属性 | 值 |
|------|-----|
| 授予 | `ctx.sqlite` |

使用**插件私有 SQLite 数据库**，由宿主创建在 EchoMusic 用户数据目录下，按插件 id 隔离。数据库名默认 `main`，支持建表、CRUD、事务和 BLOB。详见 [文件存储与数据 →](./filesystem-storage#sqlite-数据库)。

```js
// 需要 sqlite 能力
const db = await ctx.sqlite.open({ name: "library" });
await db.run("CREATE TABLE IF NOT EXISTS songs (id TEXT PRIMARY KEY, title TEXT)");
await db.run("INSERT OR REPLACE INTO songs (id, title) VALUES (?, ?)", ["1", "My Song"]);
const row = await db.get("SELECT * FROM songs WHERE id = ?", ["1"]);
```

---

## requires（版本要求）

```json
"requires": {
  "echoMusicVersion": ">=2.2.6-beta.9 <3"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `echoMusicVersion` | `string` | semver 范围，描述兼容的 EchoMusic 版本 |

### 版本范围语法

| 写法 | 含义 |
|------|------|
| `>=2.2.6` | 2.2.6 及以上版本 |
| `>=2.2.6 <3` | 2.2.6 至 3.0.0（不含） |
| `>=2.2.6-beta.9` | 2.2.6-beta.9 及以上（含 beta 版本） |
| `2.2.6` | 等价于 `>=2.2.6` |
| `^2.2.0` | 兼容 2.x.x（2.2.0 到 3.0.0 之前） |

### 版本校验行为

| 情况 | 结果 |
|------|------|
| 版本范围格式错误 | manifest 被标记为**无效**，插件不会出现在列表中 |
| 版本范围有效但不满足 | 插件出现在列表中，状态显示**"版本不兼容"**，阻止启用 |
| 版本范围满足 | 正常可以使用 |

---

## contributes（贡献点）

声明插件贡献给主应用的静态资源，目前支持浮窗。

### contributes.windows

```json
"contributes": {
  "windows": [
    {
      "id": "my-float",
      "title": "我的浮窗",
      "main": "float.js",
      "style": "float.css",
      "defaultWidth": 360,
      "defaultHeight": 200,
      "minWidth": 240,
      "minHeight": 120,
      "position": "top-center",
      "transparent": true,
      "alwaysOnTop": true,
      "skipTaskbar": true,
      "resizable": false,
      "movable": true,
      "rememberBounds": true,
      "allowOutsideWorkArea": false,
      "acceptFirstMouse": false
    }
  ]
}
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|:---:|------|
| `id` | `string` | — | 窗口唯一标识（必填，插件内不可重复） |
| `title` | `string` | `"{插件名} - {窗口id}"` | 窗口标题 |
| `main` | `string` | — | **浮窗入口 JS 文件**（必填，相对于插件目录）。浮窗没有独立的 HTML，入口脚本运行在宿主提供的浮窗环境中 |
| `style` | `string` | — | 浮窗样式文件（相对于插件目录，仅 `.css`） |
| `type` | `string` | `"floating"` | 窗口类型，当前仅支持 `"floating"` |
| `defaultWidth` | `number` | `420` | 默认宽度（px） |
| `defaultHeight` | `number` | `72` | 默认高度（px），任务栏歌词类横条窗口常用 |
| `minWidth` / `minHeight` | `number` | 随默认值 | 最小尺寸 |
| `maxWidth` / `maxHeight` | `number` | 随默认值 | 最大尺寸 |
| `position` | `string` | `"top-center"` | 初始位置：`"top-center"` 或 `"center"` |
| `transparent` | `boolean` | `true` | 启用透明背景 |
| `alwaysOnTop` | `boolean` | `true` | 窗口置顶 |
| `skipTaskbar` | `boolean` | `true` | 不在任务栏显示 |
| `resizable` | `boolean` | `false` | 允许拖拽缩放 |
| `movable` | `boolean` | `true` | 允许拖拽移动 |
| `rememberBounds` | `boolean` | `true` | 记住窗口位置和大小 |
| `allowOutsideWorkArea` | `boolean` | `false` | 允许超出显示器工作区 |
| `acceptFirstMouse` | `boolean` | `false` | 点击穿透首次点击（直接作为窗口激活） |

> ⚠️ 浮窗入口是 **JS 文件**（`main`），不是 HTML——旧版文档中的 `url`、`label`、`width`、`height` 字段已废弃。浮窗内运行在**独立的插件窗口上下文**中，可用 API 与主窗口不同，详见 [窗口与系统 →](./windows-system#浮窗专用上下文) 和 [EchoMusicPlugins 浮窗文档](https://github.com/hoowhoami/EchoMusicPlugins/blob/main/docs/floating-windows.md)。

---

## manifest 校验规则

EchoMusic 在加载插件时会校验 manifest：

1. ✅ **JSON 格式** — 必须是合法的 JSON
2. ✅ **必选字段** — `id`、`name`、`version` 必须存在且非空
3. ✅ **版本格式** — `version` 必须符合 semver 格式
4. ✅ **requires.echoMusicVersion** — semver 范围语法必须合法
5. ✅ **capabilities** — 声明了不存在的 capability 不会报错，但也不会生效

校验失败 → manifest 无效 → 插件不出现在管理列表中。

---

## 下一步

- [API 总览 →](./context-api) — 了解 `ctx` 对象的所有可用 API
- [UI 扩展指南 →](./ui-extension) — 学习如何添加界面元素
- [快速开始 →](./getting-started) — 从零创建你的第一个插件
