---
title: 备份与恢复
---

# 💾 备份与恢复

`ctx.backups` 提供两层能力：**命令式 API** 适合插件自己的同步流程；**存储提供方 API** 用于把 WebDAV、网盘等位置接入 EchoMusic 主程序的"备份与恢复"界面。

插件不需要了解或自行实现 EchoMusic 备份格式。归档生成、范围选择、格式校验、恢复回滚和应用重启均由宿主管理；插件只负责保存、列举、读取和可选的删除操作。

## 能力声明

使用任一备份 API 都应在 manifest 中声明 `backups`。如果 Provider 通过 `ctx.net.request()` 访问 WebDAV，还需声明 `unrestrictedNetwork`：

```json
{
  "capabilities": {
    "backups": true,
    "unrestrictedNetwork": true
  }
}
```

> ⚠️ 备份数据目前不加密，可能包含插件账号和插件私有数据。请使用 HTTPS、尽量采用服务端应用专用密码，并向用户说明远端存储位置和凭据保存方式。

## 命令式 API

由插件主动控制交互和传输，适合插件自有页面、定时同步或其他自动化流程。

### ctx.backups.create(options?)

创建内存备份。`settings` 和 `plugins` 默认均为 `true`，两项不能同时为 `false`：

```js
const result = await ctx.backups.create({ settings: true, plugins: true });

if (!result.ok) {
  if (!result.canceled) ctx.toast.warning(result.error || "创建备份失败");
  return;
}

console.log(result.fileName, result.summary);
// result.data 是 ArrayBuffer，可直接作为 ctx.net.request() 的请求体
```

创建前宿主会显示确认框，明确告知用户该插件将读取备份数据。

### ctx.backups.inspect(data)

检查下载或读取到的 `ArrayBuffer` / `ArrayBufferView`，返回备份摘要和短期有效的恢复 token：

```js
const inspected = await ctx.backups.inspect(downloadedData);
if (!inspected.ok) throw new Error(inspected.error);

console.log(inspected.summary);
```

token 与发起检查的插件绑定，默认十分钟内有效，成功恢复后不可再次使用。

### ctx.backups.restore(token, options?)

恢复先前检查过的备份：

```js
const restored = await ctx.backups.restore(inspected.token, {
  settings: inspected.summary.includes.settings,
  plugins: inspected.summary.includes.plugins,
});

if (!restored.ok && !restored.canceled) {
  throw new Error(restored.error || "恢复失败");
}
```

恢复前宿主会再次要求用户确认。成功后 EchoMusic **自动重启**；插件不应另外调用重启 API。

## 存储提供方 API

`ctx.backups.registerProvider(provider)` 注册一个主程序可见的存储位置。用户在设置页选择该位置后，宿主按以下流程工作：

```text
创建：宿主选择范围 → create → provider.save
恢复：provider.list → provider.load → inspect → 宿主选择范围 → restore
```

最小 Provider：

```js
const dispose = ctx.backups.registerProvider({
  id: "webdav",
  name: "WebDAV",
  description: "保存到我的 WebDAV 目录",

  async save({ fileName, data, summary, signal }) {
    // 保存 data；summary 可用于记录版本、创建时间和包含范围
  },

  async list({ signal }) {
    return [
      {
        id: "latest.echomusic-backup",
        name: "最新备份",
        createdAt: new Date().toISOString(),
        size: 1024,
      },
    ];
  },

  async load({ id, signal }) {
    // 返回 ArrayBuffer 或 ArrayBufferView
    return new ArrayBuffer(0);
  },

  async remove({ id, signal }) {
    // 可选。当前主程序不要求 Provider 必须支持删除
  },
});
```

注册返回注销函数，并自动纳入插件生命周期（禁用、卸载或运行时销毁时宿主自动移除）。Provider `id` 在当前插件内唯一，只能包含字母、数字、点、下划线和短横线，且必须以字母或数字开头。

Provider 仅能在**主窗口**插件运行时注册；独立插件浮窗可以继续调用命令式 API，但不能向设置页注册 Provider。

### Provider 字段

| 字段 | 必填 | 说明 |
|------|:--:|------|
| `id` | ✅ | 插件内唯一标识，最长 64 字符 |
| `name` | ✅ | 设置页展示名称，最长 80 字符 |
| `description` | ❌ | 存储位置说明，最长 240 字符 |
| `save(request)` | ✅ | 保存宿主生成的备份数据 |
| `list(request)` | ✅ | 返回可恢复的备份列表（最多展示 500 项） |
| `load(request)` | ✅ | 根据条目 id 返回备份二进制 |
| `remove(request)` | ❌ | 删除存储中的备份 |

所有请求都包含 `signal: AbortSignal`——用户切换存储位置、关闭流程或插件被停用时操作可能被取消；网络调用应把这个 signal 继续传给 `ctx.net.request()`。

`list()` 条目格式：`id`（传回 `load/remove` 的不透明标识，必填）、`name`（展示名，必填）、`createdAt`（ISO 8601，可选）、`size`（字节数，可选）、`description`（可选）。

## 官方示例

官方插件源中的 [`webdav-backup`](https://github.com/hoowhoami/EchoMusicPlugins) 插件就是基于这套 API 实现的 WebDAV Provider，可直接安装使用或参考其源码。

## 下一步

| 文档 | 内容 |
|------|------|
| [网络与下载 →](./network) | 用 ctx.net.request 上传/下载备份 |
| [文件存储与数据 →](./filesystem-storage) | 插件私有数据与 KV 存储 |
| [Context API →](./context-api) | ctx 完整 API 速查 |
