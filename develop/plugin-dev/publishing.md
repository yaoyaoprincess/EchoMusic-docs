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

### 步骤三：用户在 EchoMusic 中添加插件源

1. 打开 EchoMusic → 设置 → 插件管理
2. 点击"添加插件源"
3. 输入插件源仓库的 URL：`https://github.com/your-name/my-echo-plugins`
4. EchoMusic 会自动拉取 `echo-plugins.json` 并展示可用插件

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

# vite.config.js
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
- 如需浮窗与主窗口通信，需要使用 `postMessage` 或 Electron IPC（通过宿主提供的桥接）
- 详细文档见 [EchoMusicPlugins 浮窗文档](https://github.com/hoowhoami/EchoMusicPlugins/blob/main/docs/windows.md)

---

## 发布检查清单

发布插件前，建议逐项确认：

- [ ] `manifest.json` 格式正确、JSON 语法有效
- [ ] `id` 唯一，无冲突
- [ ] `version` 符合 semver 规范
- [ ] `capabilities` 遵循最小权限原则
- [ ] 入口文件无 bare import（不直接 `import from 'vue'`）
- [ ] `extends.echoMusicVersion` 版本范围合理
- [ ] 在 EchoMusic 中实测通过
- [ ] `echo-plugins.json` 中不包含 version/description/author（属于 manifest.json）

---

## 下一步

- [插件开发概览 →](./) — 返回总览
- [上下文 API 参考 →](./context-api) — 完整 ctx API 参考
- [EchoMusicPlugins 仓库 →](https://github.com/hoowhoami/EchoMusicPlugins) — 官方插件示例
