---
title: 网络与下载
---

# 🌐 网络与下载

`ctx.net` 提供三类网络能力：**主进程 HTTP 请求**（绕过渲染进程 CORS）、**TCP 客户端**（二进制设备协议）、**断点续传下载引擎**。各自对应独立的 manifest 能力声明。

```json
{
  "capabilities": {
    "unrestrictedNetwork": true,
    "tcp": true,
    "downloads": true
  }
}
```

> ⚠️ 这些能力是受信任插件的 API 开关，不构成强安全沙箱——只安装可信插件。

## HTTP 请求（ctx.net.request）

通过主进程发起请求，适合需要绕过 CORS、自定义 TLS 或读取二进制的场景。需要 `unrestrictedNetwork: true`。

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

| 选项 | 说明 |
|------|------|
| `method` / `url` / `headers` / `body` | 常规请求字段 |
| `responseType` | `'json'` / `'text'` / `'arrayBuffer'` |
| `timeoutMs` | 超时毫秒数 |
| `maxResponseBytes` | 响应体大小上限 |
| `maxRedirects` | 重定向次数上限 |
| `decompress` | 是否自动解压 |
| `tls` | `{rejectUnauthorized, servername}` |
| `signal` | `AbortSignal`，可取消请求 |

`ctx.net.fetch(input, init?)` 提供与浏览器一致的 **fetch 语义**（跟随渲染进程的网络环境，受 CORS 约束）；需要绕过这些限制时用 `request`。两者互为补充。

## TCP 客户端（ctx.net.tcp）

通过主进程的 Node.js Socket 连接 TCP 服务，适合 OpenRGB SDK 等二进制设备协议。需要 `tcp: true`，连接上限 **16**（跨窗口，宿主总计 128）。直连指定地址，不走应用 HTTP 代理，无 TLS、无监听服务。随 2.3.2-beta.4 引入，建议 `requires.echoMusicVersion: ">=2.3.2-beta.4"` 并保留运行时检测。

```js
const socket = await ctx.net.tcp.connect({
  host: "127.0.0.1",       // IPv6 不带方括号
  port: 6742,              // 1..65535
  connectTimeoutMs: 5000,  // 1..120000
  noDelay: true,
  keepAlive: true,
  keepAliveInitialDelayMs: 30000,
});
```

| 成员 | 说明 |
|------|------|
| `write(data)` | 写入 `ArrayBuffer`/`Uint8Array`（≤1 MiB/次），完成后仅表示已交给底层发送 |
| `read()` | 返回最多 64 KiB 的 `ArrayBuffer`；对端正常结束后返回 `null`。同一连接同时只能有一个待完成 read |
| `end({signal}?)` | 半关闭：排空写入后发送 FIN，仍可读对端响应 |
| `close()` | 立即中止整条连接，可重复调用 |

**字节流没有消息边界**——一次 `read()` 可能是半个包或多个包，插件需按协议长度自行拆包并限制最大包长。`connect({...signal})` 的 signal 管理整条连接生命周期；进行中取消任一操作会中止整条连接（已传字节无法撤回）。

```js
export async function activate(ctx) {
  if (!ctx.net.tcp) throw new Error("请升级 EchoMusic 以使用 TCP 插件");
  const socket = await ctx.net.tcp.connect({ host: "127.0.0.1", port: 9000 });
  const controller = new AbortController();
  ctx.dispose(() => controller.abort());
  void (async () => {
    try {
      await socket.write(new TextEncoder().encode("status\n"));
      for (;;) {
        const bytes = await socket.read({ signal: controller.signal });
        if (bytes === null) break;
        handlePacket(new Uint8Array(bytes)); // 交给协议解析器
      }
    } finally {
      await socket.close().catch(() => {});
    }
  })();
}
```

背压与生命周期：每条连接最多积压 4 MiB 或 64 个未完成写入；接收为按需读取（暂停 read 时由系统缓冲施加背压）；连接属于创建它的插件和窗口，插件停用/卸载/安全模式/窗口重载会中止相关连接。长连接协议（如 OpenRGB）保持一个读取循环，发送忙时只保留最新帧。

## 下载引擎（ctx.net.download）

断点续传下载，由宿主管理临时文件、进度与校验。需要 `downloads: true` 与 `localFiles: true`。

```js
const directory = await ctx.fs.getPrivateDirectory({ kind: "data" });
const task = await ctx.net.download({
  url: "https://your-server.example/video.mp4",
  target: { directoryId: directory.id, relativePath: "videos/bg.mp4" },
  // 可选：headers（鉴权）、name、sourceKey/idempotencyKey（去重标识）、
  //       expectedBytes/checksum（发布方提供的大小/哈希）、maxBytes、
  //       conflict: 'fail'|'rename'|'replace'（默认 fail）、resume（续传）、
  //       connectTimeoutMs/idleTimeoutMs
});
const unsubscribe = task.subscribe((snapshot) => {
  // snapshot: {state, receivedBytes, totalBytes, bytesPerSecond, remainingSeconds}
});
try {
  const result = await task.wait(); // 校验并提交成功才到 completed
  const lease = await ctx.fs.openMedia(result.file); // 用 MediaLease 播放
  // 用完记得 lease.release()
} finally {
  unsubscribe();
}
```

| 句柄成员 | 说明 |
|------|------|
| `getSnapshot()` | 当前任务快照 |
| `subscribe(fn)` | 订阅进度快照 |
| `pause()` / `resume()` / `retry()` | 暂停 / 续传 / 重试 |
| `cancel()` | 取消任务 |
| `wait()` | 等待任务完成，返回 `{file}` 文件引用 |

限制与行为：普通下载为 HTTP/HTTPS GET、沿用宿主代理、不自动携带宿主账号或 Cookie；URL 与请求头不落盘；跨来源重定向剥离鉴权头；最多 5 次重定向；上游须返回 identity 编码以保证续传偏移可靠。全局最多 3 个活动传输（每所有者 2 个）；默认连接超时 30s、空闲超时 60s。

## 文件授权

`download` 的保存目标、`openMedia` 的媒体引用都基于宿主登记的**授权引用**（`DirectoryRef` / `FileRef`），详见 [文件存储与数据 →](./filesystem-storage#授权文件与目录)。

## 下一步

| 文档 | 内容 |
|------|------|
| [文件存储与数据 →](./filesystem-storage) | 授权文件与目录、私有目录、媒体租约 |
| [备份与恢复 →](./backups) | 把备份文件上传到自己的存储 |
| [Graphics 绘图 →](./graphics) | 用下载的资源做渲染 |
| [Context API →](./context-api) | ctx 完整 API 速查 |
