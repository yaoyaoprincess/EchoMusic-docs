---
title: Network & Downloads
---

# 🌐 Network & Downloads

`ctx.net` provides three networking capabilities: **main-process HTTP requests** (bypassing renderer CORS), a **TCP client** (binary device protocols), and a **resumable download engine**. Each has its own manifest capability:

```json
{
  "capabilities": {
    "unrestrictedNetwork": true,
    "tcp": true,
    "downloads": true
  }
}
```

> ⚠️ These capabilities are trusted-plugin API switches, not a strong security sandbox — only install trusted plugins.

## HTTP Requests (ctx.net.request)

Requests via the main process, ideal for bypassing CORS, custom TLS, or reading binaries. Requires `unrestrictedNetwork: true`.

```js
const res = await ctx.net.request({
  method: "GET",
  url: "https://api.example.com/data",
  headers: { Authorization: "Bearer xxx" },
  responseType: "json",        // 'json' | 'text' | 'arrayBuffer'
  timeoutMs: 15000,
  maxResponseBytes: 10 * 1024 * 1024,
});
console.log(res.data);
```

| Option | Description |
|------|------|
| `method` / `url` / `headers` / `body` | Standard request fields |
| `responseType` | `'json'` / `'text'` / `'arrayBuffer'` |
| `timeoutMs` | Timeout in milliseconds |
| `maxResponseBytes` | Response size cap |
| `maxRedirects` | Redirect limit |
| `decompress` | Automatic decompression |
| `tls` | `{rejectUnauthorized, servername}` |
| `signal` | `AbortSignal` to cancel |

`ctx.net.fetch(input, init?)` provides **fetch semantics** matching the browser (uses the renderer's network environment, subject to CORS); use `request` when you need to bypass those limits. They complement each other.

## TCP Client (ctx.net.tcp)

Connect to TCP services through the main process's Node.js Socket — great for the OpenRGB SDK and other binary device protocols. Requires `tcp: true`; up to **16** connections per plugin (128 host-wide). Direct connections only — no app HTTP proxy, no TLS, no listening. Introduced in 2.3.2-beta.4; prefer `requires.echoMusicVersion: ">=2.3.2-beta.4"` and keep runtime detection.

```js
const socket = await ctx.net.tcp.connect({
  host: "127.0.0.1",       // IPv6 without brackets
  port: 6742,              // 1..65535
  connectTimeoutMs: 5000,  // 1..120000
  noDelay: true,
  keepAlive: true,
  keepAliveInitialDelayMs: 30000,
});
```

| Member | Description |
|------|------|
| `write(data)` | Write `ArrayBuffer`/`Uint8Array` (≤1 MiB per call); completion means handed to the OS, not processed by the peer |
| `read()` | Returns up to 64 KiB `ArrayBuffer`; `null` after a normal remote EOF. Only one pending read per connection |
| `end({signal}?)` | Half-close: drain pending writes then send FIN; you can still read the response |
| `close()` | Abort the connection immediately; safe to call repeatedly |

**The byte stream has no message boundaries** — one `read()` may be half a packet or several packets; frame by protocol length yourself and cap the maximum packet size. The `connect({...signal})` signal governs the whole connection; cancelling any in-flight operation aborts the connection (already-transferred bytes cannot be recalled).

```js
export async function activate(ctx) {
  if (!ctx.net.tcp) throw new Error("Upgrade EchoMusic to use the TCP plugin API");
  const socket = await ctx.net.tcp.connect({ host: "127.0.0.1", port: 9000 });
  const controller = new AbortController();
  ctx.dispose(() => controller.abort());
  void (async () => {
    try {
      await socket.write(new TextEncoder().encode("status\n"));
      for (;;) {
        const bytes = await socket.read({ signal: controller.signal });
        if (bytes === null) break;
        handlePacket(new Uint8Array(bytes)); // feed your protocol parser
      }
    } finally {
      await socket.close().catch(() => {});
    }
  })();
}
```

Backpressure & lifecycle: up to 4 MiB or 64 pending writes per connection; reads are pull-based (pausing reads applies OS-level backpressure); connections belong to the owning plugin and window — plugin disable/uninstall/safe mode/window reload aborts them. For long-lived protocols (like OpenRGB) keep one read loop and keep only the newest frame when the sender is busy.

## Download Engine (ctx.net.download)

Resumable downloads with host-managed temp files, progress, and verification. Requires `downloads: true` and `localFiles: true`.

```js
const directory = await ctx.fs.getPrivateDirectory({ kind: "data" });
const task = await ctx.net.download({
  url: "https://your-server.example/video.mp4",
  target: { directoryId: directory.id, relativePath: "videos/bg.mp4" },
  // Optional: headers (auth), name, sourceKey/idempotencyKey (dedup),
  //   expectedBytes/checksum (publisher-provided), maxBytes,
  //   conflict: 'fail'|'rename'|'replace' (default fail), resume,
  //   connectTimeoutMs/idleTimeoutMs
});
const unsubscribe = task.subscribe((snapshot) => {
  // snapshot: {state, receivedBytes, totalBytes, bytesPerSecond, remainingSeconds}
});
try {
  const result = await task.wait(); // reaches completed only after verification & commit
  const lease = await ctx.fs.openMedia(result.file); // play via MediaLease
  // remember lease.release() when done
} finally {
  unsubscribe();
}
```

| Handle member | Description |
|------|------|
| `getSnapshot()` | Current task snapshot |
| `subscribe(fn)` | Subscribe to progress snapshots |
| `pause()` / `resume()` / `retry()` | Pause / resume / retry |
| `cancel()` | Cancel the task |
| `wait()` | Wait for completion, returns `{file}` reference |

Limits & behavior: plain downloads are HTTP/HTTPS GET, follow the host proxy, never attach host credentials or cookies; URL and headers are not persisted; cross-origin redirects strip auth headers; at most 5 redirects; upstream must return identity encoding for reliable resume offsets. Up to 3 active transfers globally (2 per owner); default connect timeout 30s, idle timeout 60s.

## File Grants

The `download` target and `openMedia` media references are based on host-registered **granted references** (`DirectoryRef` / `FileRef`) — see [Filesystem & Storage →](./filesystem-storage#granted-files-directories).

## Next Steps

| Document | Content |
|------|------|
| [Filesystem & Storage →](./filesystem-storage) | Granted files & directories, private dirs, media leases |
| [Backups →](./backups) | Upload backups to your own storage |
| [Graphics →](./graphics) | Render with downloaded resources |
| [Context API →](./context-api) | Full ctx API quick reference |
