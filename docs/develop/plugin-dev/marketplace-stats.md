---
title: 热度与统计
---

# 📊 热度与统计

EchoMusic 内置一套插件热度统计系统，用于在插件市场与文档站展示"热度"排名。**插件开发者无需注册或接入任何 SDK**——统计由 EchoMusic 客户端在运行时自动完成。

## 统计链路

1. 用户在插件市场安装、更新插件，或安装失败时，EchoMusic 主进程向插件市场统计服务上报一条事件（`install` / `update` / `failure`），成功事件只上报一次、不做重试（保证计数不重复）；
2. 事件写入服务端（Cloudflare Worker + D1 数据库），按 `sourceId + pluginId` 聚合；
3. 插件市场 UI 与文档站"热度榜"基于聚合结果实时计算热度分并排序。

> 📋 统计只记录事件计数与时间戳，**不涉及任何用户个人数据**。

## 热度口径

应用内与文档站展示的"热度"值由服务端在每次查询时按下式实时计算：

```
score = (installCount + updateCount) × 3
      + 当日 (installCount + updateCount) × 5
      − failureCount × 2
```

| 字段 | 说明 |
|------|------|
| `installCount` | 累计安装次数 |
| `updateCount` | 累计更新次数 |
| `failureCount` | 累计失败次数（会降低热度） |
| `score` | 热度分，即市场 UI 展示的"热度" |
| `lastInstalledAt` / `lastUpdatedAt` | 最近一次安装 / 更新时间（UTC） |

## 查询接口

统计服务公开、无需鉴权、支持 CORS，可直接在网页或脚本中查询：

**请求**

```
POST https://echomusic-plugin-marketplace.hoowhoami.dpdns.org/v1/plugins/stats
Content-Type: application/json

{
  "plugins": [
    { "sourceId": "github:hoowhoami/echomusicplugins", "pluginId": "water-lyrics" },
    { "sourceId": "github:hoowhoami/echomusicplugins", "pluginId": "apple-music-lyrics" }
  ]
}
```

**响应**（示例，数值随时间变化）

```json
{
  "ok": true,
  "plugins": [
    {
      "sourceId": "github:hoowhoami/echomusicplugins",
      "pluginId": "water-lyrics",
      "stats": {
        "installCount": 945,
        "updateCount": 193,
        "failureCount": 534,
        "score": 2456,
        "lastInstalledAt": "2026-10-28T17:16:52.257Z",
        "lastUpdatedAt": "2026-10-28T18:19:09.673Z"
      }
    }
  ]
}
```

注意事项：

- 单次查询最多 **200** 个插件，超出请分批请求；
- `sourceId` 格式为 `github:owner/repo`（小写），即插件源仓库地址：官方源为 `github:hoowhoami/echomusicplugins`，社区源为各自仓库地址；
- 查询不存在的 `(sourceId, pluginId)` 不会报错，只是返回结果中不含该条目；
- 服务状态检查：`GET https://echomusic-plugin-marketplace.hoowhoami.dpdns.org/health` 返回 `{"ok":true}`。

## 查询示例

**cURL**

```bash
curl -s -X POST \
  https://echomusic-plugin-marketplace.hoowhoami.dpdns.org/v1/plugins/stats \
  -H "Content-Type: application/json" \
  -d '{"plugins":[{"sourceId":"github:hoowhoami/echomusicplugins","pluginId":"water-lyrics"}]}'
```

**JavaScript**

```js
const res = await fetch(
  "https://echomusic-plugin-marketplace.hoowhoami.dpdns.org/v1/plugins/stats",
  {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      plugins: [
        { sourceId: "github:hoowhoami/echomusicplugins", pluginId: "water-lyrics" }
      ]
    })
  }
);
const { plugins } = await res.json();
console.log(plugins[0].stats.score);
```

## 常见问题

**为什么我的插件热度是 0？**
统计按 `(sourceId, pluginId)` 聚合，新插件尚无安装事件时查询结果中不含该条目。请确认分享链接中的 `sourceId` 与插件源仓库一致，详见[发布与分发](./publishing)。

**文档站的热度榜用的是同一套数据吗？**
是。[插件列表](/guide/plugins/list)页面的热度列实时读取同一接口，与应用内排序口径一致。

**统计服务会下线吗？**
该服务由 EchoMusic 官方维护，部署在 Cloudflare Workers 上；接口如有变更会在本页同步更新。
