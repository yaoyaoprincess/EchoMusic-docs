---
title: Heat & Stats
---

# 📊 Heat & Stats

EchoMusic ships with a plugin heat-statistics system that powers the "heat" ranking shown in the in-app marketplace and on the docs site. **Plugin developers don't need to register or integrate any SDK** — the statistics are collected automatically by the EchoMusic client at runtime.

## How It Works

1. When a user installs or updates a plugin in the marketplace (or an installation fails), the EchoMusic main process reports one event (`install` / `update` / `failure`) to the marketplace stats service. Successful events are reported exactly once without retries (keeping counts accurate);
2. Events are stored server-side (a Cloudflare Worker + D1 database), aggregated by `sourceId + pluginId`;
3. The marketplace UI and the docs-site heat ranking compute the heat score from the aggregated data in real time.

> 📋 Only event counts and timestamps are recorded — **no personal user data** is involved.

## Heat Score

The "heat" value shown in the app and on the docs site is computed by the server on every query:

```
score = (installCount + updateCount) × 3
      + today's (installCount + updateCount) × 5
      − failureCount × 2
```

| Field | Description |
|-------|-------------|
| `installCount` | Total installs |
| `updateCount` | Total updates |
| `failureCount` | Total failures (lowers the score) |
| `score` | The heat score shown as "heat" in the marketplace UI |
| `lastInstalledAt` / `lastUpdatedAt` | Last install / update time (UTC) |

## Query API

The stats service is public, requires no authentication, and allows CORS — you can query it from any web page or script:

**Request**

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

**Response** (example — values change over time)

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

Notes:

- A single query accepts at most **200** plugins — batch beyond that;
- `sourceId` is `github:owner/repo` (lowercase), the plugin source repository: the official source is `github:hoowhoami/echomusicplugins`, community sources use their own repository addresses;
- Querying a non-existent `(sourceId, pluginId)` pair does not error — it's simply absent from the response;
- Health check: `GET https://echomusic-plugin-marketplace.hoowhoami.dpdns.org/health` returns `{"ok":true}`.

## Examples

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

## FAQ

**Why is my plugin's heat 0?**
Stats aggregate by `(sourceId, pluginId)`; a brand-new plugin with no install events is simply absent from the response. Make sure the `sourceId` in your share link matches the plugin source repository — see [Publishing](./publishing).

**Does the docs-site heat ranking use the same data?**
Yes. The heat column on the [Plugin List](/en/guide/plugins/list) page reads the same API in real time, using the same scoring as the in-app ranking.

**Will the stats service go away?**
It is maintained by the EchoMusic team and deployed on Cloudflare Workers; any API changes will be reflected on this page.
