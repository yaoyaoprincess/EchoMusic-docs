---
title: 发布与分发
outline: [2, 4]
---

# 🚢 发布与分发

将插件分享给其他 EchoMusic 用户有两种方式：直接分享插件目录，或发布到在线插件源。

## 直接分发

最简单的方式：将插件文件夹打包为 ZIP，分享给用户。用户解压到 EchoMusic 的插件目录即可。

```
my-plugin.zip
  └── my-plugin/
      ├── manifest.json
      ├── index.js
      ├── style.css      ← 可选
      └── icon.svg       ← 可选
```

> 缺点：用户无法自动获取更新。

---

## 在线插件源

在线插件源让用户能在 EchoMusic 的插件管理页中**浏览、一键安装和自动更新**插件。

### 工作原理

```
  ┌─────────────┐      fetch echo-plugins.json      ┌──────────────┐
  │  EchoMusic   │ ─────────────────────────────────▶ │  GitHub 仓库   │
  │  插件管理页   │                                     │  (插件源)      │
  │              │ ◀───────────────────────────────── │              │
  │  显示插件列表  │      返回插件索引数据               └──────────────┘
  └──────┬───────┘
         │ 用户点击"安装"
         ▼
  ┌─────────────┐      clone / download               ┌──────────────┐
  │  本地插件目录  │ ◀────────────────────────────────── │  插件仓库      │
  └─────────────┘                                      └──────────────┘
```

### 步骤一：创建插件源仓库

在 GitHub 创建一个仓库（例如 `my-echo-plugins`），在仓库根目录创建 `echo-plugins.json`：

```json
{
  "name": "我的插件源",
  "homepage": "https://github.com/your-name/my-echo-plugins",
  "plugins": [
    {
      "id": "lyric-enhancer",
      "path": "lyric-enhancer",
      "repo": "https://github.com/your-name/lyric-enhancer",
      "homepage": "https://github.com/your-name/lyric-enhancer#readme",
      "tags": ["lyrics", "ui"]
    },
    {
      "id": "mini-spectrum",
      "path": "mini-spectrum",
      "repo": "https://github.com/your-name/mini-spectrum",
      "homepage": "https://github.com/your-name/mini-spectrum",
      "tags": ["visualizer", "audio"]
    }
  ]
}
```

### echo-plugins.json 字段说明

#### 根级字段

| 字段 | 类型 | 必选 | 说明 |
|------|------|:--:|------|
| `name` | `string` | ✅ | 插件源名称 |
| `homepage` | `string` | ❌ | 插件源主页 URL |
| `plugins` | `array` | ✅ | 包含的插件列表 |

#### plugins[] 条目

| 字段 | 类型 | 必选 | 说明 |
|------|------|:--:|------|
| `id` | `string` | ✅ | 插件 ID，必须与 manifest.json 中的 `id` 一致 |
| `path` | `string` | ✅ | 插件在仓库中的目录路径（空字符串表示仓库根目录） |
| `repo` | `string` | ❌ | 插件源码仓库地址，留空则使用插件源仓库 |
| `homepage` | `string` | ❌ | 插件详情页或文档链接 |
| `tags` | `string[]` | ❌ | 分类标签，用于在线列表的筛选和搜索 |

> ⚠️ **不要在 `echo-plugins.json` 中维护 `version`、`description`、`author` 等字段。** 这些信息属于各插件的 `manifest.json`，EchoMusic 会自动从插件仓库中读取。

### 步骤二：将插件放入仓库

如果插件在独立仓库中（推荐）：

```
your-name/lyric-enhancer/        ← 独立的插件仓库
  ├── manifest.json
  ├── index.js
  ├── style.css
  └── icon.svg
```

然后在插件源的 `echo-plugins.json` 中指向这个仓库：

```json
{
  "id": "lyric-enhancer",
  "path": "",                    ← 空字符串，因为仓库根目录就是插件
  "repo": "https://github.com/your-name/lyric-enhancer"
}
```

如果多个插件放在同一个仓库中：

```
your-name/my-echo-plugins/       ← 插件源仓库
  ├── echo-plugins.json
  ├── lyric-enhancer/            ← 插件 1
  │   ├── manifest.json
  │   └── index.js
  └── mini-spectrum/             ← 插件 2
      ├── manifest.json
      └── index.js
```

对应的 `echo-plugins.json`：

```json
{
  "plugins": [
    {
      "id": "lyric-enhancer",
      "path": "lyric-enhancer",   ← 指向子目录
      "repo": ""                  ← 留空，使用此仓库
    },
    {
      "id": "mini-spectrum",
      "path": "mini-spectrum",
      "repo": ""
    }
  ]
}
```

---

## 插件市场编程式 API

除了 UI 上的"添加插件源"，插件还可以通过 `ctx.plugins.marketplace` 以编程方式管理插件源和安装插件。这对"插件管理器插件"等工具类插件非常有用。

### 源管理

| API | 说明 |
|-----|------|
| `ctx.plugins.marketplace.listSources()` | 列出所有已添加的插件源 |
| `ctx.plugins.marketplace.addSource(input, options?)` | 添加一个插件源（input: `{ url, name? }`） |
| `ctx.plugins.marketplace.patchSource(sourceId, patch)` | 修改插件源的配置 |
| `ctx.plugins.marketplace.removeSource(sourceId)` | 移除一个插件源 |

```js
// 添加插件源
await ctx.plugins.marketplace.addSource({
  url: "https://github.com/hoowhoami/EchoMusicPlugins",
  name: "EchoMusic 官方插件",
});

// 列出当前的插件源
const sources = await ctx.plugins.marketplace.listSources();
console.log(sources);

// 修改插件源名称
await ctx.plugins.marketplace.patchSource("source-id", {
  name: "更新后的名称",
});
```

### 浏览与安装

| API | 说明 |
|-----|------|
| `ctx.plugins.marketplace.list(options?)` | 浏览所有已添加源中的可用插件 |
| `ctx.plugins.marketplace.install(sourceId, pluginId, options?)` | 从指定源安装插件 |

```js
// 获取所有可用插件
const result = await ctx.plugins.marketplace.list();
// result.plugins 是 { sourceId, pluginId, manifest, ... } 列表

// 在线安装插件
const installResult = await ctx.plugins.marketplace.install(
  "source-id",
  "my-plugin",
  { force: true }   // force: true 会覆盖本地已有版本
);
```

---

## 插件管理 API

### 本地安装

| API | 说明 |
|-----|------|
| `ctx.plugins.installLocal(paths, options?)` | 从本地路径（文件/文件夹）安装插件 |

```js
// 安装从文件管理器拖入的插件
const paths = ctx.plugins.getDroppedFilePaths(event.dataTransfer.files);
const result = await ctx.plugins.installLocal(paths);
```

### 卸载

| API | 说明 |
|-----|------|
| `ctx.plugins.uninstall(pluginId)` | 卸载指定插件，删除插件目录并清除 KV 数据 |

---

## 安全模式与故障管理

### 安全模式

当插件出现未捕获异常时，EchoMusic 会触发安全保护机制。

| API | 说明 |
|-----|------|
| `ctx.plugins.setSafeMode(enabled)` | 全局开关安全模式（true 时禁用所有插件） |
| `ctx.plugins.setEnabled(pluginId, enabled)` | 启用/禁用指定插件 |

### 故障上报

插件可以主动上报运行故障，帮助 EchoMusic 判断是否需要建议用户禁用该插件。

| API | 说明 |
|-----|------|
| `ctx.plugins.reportFailure(failure)` | 上报故障记录 |
| `ctx.plugins.clearFailure(pluginId?)` | 清除故障记录（不传参数清除所有） |
| `ctx.plugins.markStartup(pluginIds)` | 标记启动期间活动的插件 |
| `ctx.plugins.setActiveSession(pluginIds)` | 标记当前会话的活动插件 |
| `ctx.plugins.clearStartup()` | 清除启动标记 |

```js
// 上报故障
ctx.plugins.reportFailure({
  pluginId: ctx.manifest.id,
  error: "插件初始化时网络请求失败",
  safeMode: false,   // 是否建议进入安全模式
});

// 清除此插件的历史故障记录
ctx.plugins.clearFailure(ctx.manifest.id);
```

> 如果某个启用了的插件在一个**启动会话**中多次崩溃，EchoMusic 会自动建议用户禁用该插件。

---

## 版本管理

### manifest.json 中的 version

插件版本在 `manifest.json` 中定义，遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)：

```json
{
  "version": "1.2.0"
}
```

### 更新检测

EchoMusic 会比较本地已安装插件的 `version` 与在线插件源的 `manifest.json` 中的 `version`：

| 情况 | EchoMusic 行为 |
|------|----------------|
| 在线版本 > 本地版本 | 显示"有更新"，提示用户升级 |
| 在线版本 = 本地版本 | 显示"已是最新" |
| 本地版本未在插件源中 | 不会自动提示更新 |

### 版本号升级建议

```json
// Bug 修复：升级 PATCH
"version": "1.0.0" → "1.0.1"

// 新功能（向后兼容）：升级 MINOR，重置 PATCH
"version": "1.0.5" → "1.1.0"

// 破坏性变更：升级 MAJOR，重置 MINOR 和 PATCH
"version": "1.5.2" → "2.0.0"
```

---

## 使用 TypeScript / Vue SFC

插件入口运行在浏览器 ESM 环境，如果你需要使用 TypeScript 或 `.vue` 单文件组件，需要先打包为纯 JavaScript ESM。

### 推荐工具链

#### 方案一：Vite（推荐）

```bash
# 初始化
npm init -y
npm install -D vite
```

```js
// vite.config.js
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  build: {
    lib: {
      entry: 'src/index.ts',        // 入口
      formats: ['es'],              // ESM 格式
      fileName: () => 'index.js',   // 输出文件名
    },
    rollupOptions: {
      external: [],                 // 不排除任何依赖（因为宿主不提供）
    },
    outDir: 'dist',
  },
});
```

构建后，将 `manifest.json` 中的 `main` 指向 `dist/index.js`：

```json
{
  "main": "dist/index.js"
}
```

#### 方案二：esbuild

```bash
npm install -D esbuild
```

```json
// package.json
{
  "scripts": {
    "build": "esbuild src/index.ts --bundle --format=esm --outfile=dist/index.js"
  }
}
```

---

## 浮窗开发补充

关于 `contributes.windows` 浮窗配置（已在 [Manifest 配置参考](./manifest#contributeswindows) 中详述），以下是额外提示：

- 浮窗由 **Electron 主进程** 创建，与插件 JS 运行在不同的进程中
- 浮窗内的 HTML 可以使用 `<script>` 标签，但无法直接访问 `ctx`
- 如需浮窗与主窗口通信，需要通过宿主提供的 `window.electronAPI` 桥接
- 浮窗内的 `ctx` 通过 window API 同步注入，浮窗也有自己的 `activate(ctx)` 调用
- 详细文档见 [窗口与系统 →](./windows-system) 和 [EchoMusicPlugins 浮窗文档](https://github.com/hoowhoami/EchoMusicPlugins/blob/main/docs/windows.md)

---

## 发布检查清单

发布插件前，建议逐项确认：

- [ ] `manifest.json` 格式正确、JSON 语法有效
- [ ] `id` 唯一，无冲突
- [ ] `version` 符合 semver 规范
- [ ] `capabilities` 遵循最小权限原则
- [ ] `permissions.http` 声明了网络访问范围（如适用）
- [ ] 入口文件无 bare import（不直接 `import from 'vue'`）
- [ ] `requires.echoMusicVersion` 版本范围合理
- [ ] 在 EchoMusic 中实测通过
- [ ] `echo-plugins.json` 中不包含 version/description/author（属于 manifest.json）

---

## 下一步

- [API 总览 →](./context-api) — 完整 ctx API 参考
- [窗口与系统 →](./windows-system) — 浮窗、桌面歌词、Mini 播放器管理
- [插件开发概览 →](./) — 返回总览
- [EchoMusicPlugins 仓库 →](https://github.com/hoowhoami/EchoMusicPlugins) — 官方插件示例
