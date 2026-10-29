---
title: Server Intercept
---

# 🛰️ Server Intercept

`ctx.server.intercept()` lets a plugin act like a packet-capture proxy for every API call the app sends to the Kugou server:

```
app business code → plugin interceptor chain (priority-ordered) → Kugou server
```

Interceptors can **observe, modify, block (mock), and forward** requests, and post-process responses.

## Declaring the Capability

This capability can read the login token, user ID, and device identifier from the Authorization header, plus all listening data — and can tamper with requests and responses. Its sensitivity is on par with `unrestrictedNetwork`. It must be declared explicitly in `manifest.json`:

```json
{
  "capabilities": {
    "serverIntercept": true
  }
}
```

To forward requests to a third-party/self-hosted service, also declare `unrestrictedNetwork: true` (forward via `ctx.net.request`, no CORS limits). It's recommended to require a host version that ships this capability in `requires.echoMusicVersion`.

## Quick Start

```js
module.exports.activate = (ctx) => {
  ctx.server.intercept(
    async (req, next) => {
      // 1. Observe the request
      console.log(req.method, req.url, req.params);

      // 2. Modify request parameters (signatures are recomputed by the host — they stay valid)
      if (req.url === '/search/complex') {
        req.params.keyword = String(req.params.keyword ?? '').trim();
      }

      // 3. Pass to the next interceptor / the real server
      const res = await next();

      // 4. Post-process the response
      return res;
    },
    { name: 'my-interceptor' },
  );
};
```

`intercept(handler, options?)` returns an unregister function; the host also unregisters automatically when the plugin is disabled. One plugin may register multiple interceptors.

## Request & Response Objects

The `request` received by `handler(request, next)`:

| Field | Type | Description |
|---|---|---|
| `method` | `string` | `'GET'` / `'POST'` |
| `url` | `string` | Service route, e.g. `'/song/url'` |
| `params` | `object` | Query parameters (a live object, mutable in place) |
| `data` | `any` | POST body, may be absent |
| `headers` | `object` | Request headers, **already including the injected Authorization** |
| `origin` | `object` | Always `{ type: 'host' }`. Requests the plugin itself makes via `ctx.kugou` do not enter the chain |

`next()` resolves to the response object:

| Field | Type | Description |
|---|---|---|
| `status` | `number` | HTTP status code |
| `body` | `any` | Server response body |
| `headers` | `object` | Response headers, may be absent |
| `cookie` | `string[]` | Set-Cookie values, may be absent |
| `mocked` | `boolean` | Whether the response was short-circuited by an interceptor (never hit the network) |
| `handledBy` | `string` | ID of the plugin that short-circuited the request |

## Three Core Decisions

### 1. priority — position in the chain

Interceptors form an **onion chain**: a higher `priority` sits more outward (runs earlier on the request, receives the result later); equal priorities keep registration order, frozen at the start of each request.

| priority | Purpose (convention, not enforced) |
|---|---|
| `100` | Observation: traffic logs, timing (the outermost layer sees the fully-processed final result) |
| `0` (default) | Data transformation: fill parameters, sanitize responses |
| `-100` | Mock / forward: the innermost takeover — its result can still be observed and post-processed by outer layers |

### 2. match — whether it applies to this request

`options.match` supports three forms; when not matched the handler is **not called** (zero-cost transparent skip):

```js
// String: route prefix match
ctx.server.intercept(handler, { match: '/song/' });

// RegExp: tested against the url
ctx.server.intercept(handler, { match: /^\/(song|privilege)\// });

// Function: inspect the full request yourself
ctx.server.intercept(handler, {
  match: (req) => req.method === 'GET' && req.url.startsWith('/privilege/'),
});
```

`match` is evaluated layer by layer on the chain: if an outer interceptor rewrites `url`, inner layers re-evaluate against the rewritten value.

### 3. next — whether to continue

| Form | Behavior |
|---|---|
| `return next()` | Pass to the next interceptor (post-process its result afterwards) |
| `return next({ params: {...}, headers: {...} })` | Patch the request then pass on (shallow merge; headers merge deeply) |
| Not calling `next`, `return { status, body }` | **Short-circuit takeover**: no later interceptor or real server is reached; the response is marked `mocked: true` |
| Not calling `next` and throwing / returning an invalid value | The host passes the original request through (**fail-open**) and records the plugin error |

`next()` is idempotent: calling it repeatedly returns the same result without a second network request.

> ⚠️ **Do not `throw` to "block" a request** — exceptions are passed through by fail-open. To block, return an error-shaped mock response (e.g. `{ status: 403, body: {...} }`).

## Typical Scenarios

### Mock / block a request

```js
ctx.server.intercept(
  () => ({ status: 200, body: { status: 1, data: { count: 0 } } }),
  { match: '/some/counter', priority: -100, name: 'counter-mock' },
);
```

Mock responses still go through the app's normal post-processing (login-expiry detection, error wrapping), so return a business-plausible body.

### Forward to your own service (Map Remote)

```js
ctx.server.intercept(
  async (req) => {
    const external = await ctx.net.request({
      method: 'POST',
      url: `https://my-server.example.com/kugou${req.url}`,
      body: { params: req.params, data: req.data },
    });
    return { status: external.status, body: external.data };
  },
  { match: /^\/song\//, priority: -100 },
);
```

### Modify responses / detect inner mocks

```js
ctx.server.intercept(
  async (req, next) => {
    const res = await next();
    if (res.mocked) {
      console.log(`Response was taken over by ${res.handledBy}`);
    }
    if (req.url === '/song/url' && res.body?.data) {
      res.body.data = patchSongUrl(res.body.data);
    }
    return res;
  },
  { priority: 100, name: 'response-patcher' },
);
```

When multiple interceptors want to take over the same request, the innermost wins first and outer layers keep the final override.

### Runtime toggle

```js
let enabled = true;
ctx.server.intercept(
  (req, next) => (enabled ? doIntercept(req, next) : next()),
  { match: '/song/', name: 'optional-patch' },
);
```

## Boundaries & Notes

1. The interception point is the **logical API layer** (route + params + data + headers), before request signing — parameter changes never break signatures;
2. You cannot see or change server-internal signatures, default device parameters, or the final outbound domain (for transparent gateway swaps use the app's network proxy settings);
3. Audio streams, direct cover image connections, WebSockets, and requests made via `ctx.net.*` are **not intercepted**;
4. Requests the plugin makes via `ctx.kugou.*` do not enter the chain, so interceptors can freely call `ctx.kugou` without recursion;
5. Interceptor errors always fail-open; the error appears in the plugin's failure record in the plugin manager;
6. The main window, Mini Player, and Desktop Lyric are separate runtimes — an interceptor only affects requests made by the window it runs in (business traffic is concentrated in the main window).
