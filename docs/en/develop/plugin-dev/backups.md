---
title: Backups
---

# 💾 Backups

`ctx.backups` provides two layers of capability: an **imperative API** for your plugin's own sync flows, and a **storage provider API** for plugging WebDAV, cloud drives, and other locations into EchoMusic's "Backup & Restore" UI.

Plugins don't need to know or implement the EchoMusic backup format. Archive generation, scope selection, format validation, restore rollback, and app restarts are all managed by the host; the plugin only handles save, list, load, and optional delete.

## Declaring the Capability

Declare `backups` in the manifest to use any backup API. If your provider accesses WebDAV via `ctx.net.request()`, also declare `unrestrictedNetwork`:

```json
{
  "capabilities": {
    "backups": true,
    "unrestrictedNetwork": true
  }
}
```

> ⚠️ Backup data is currently unencrypted and may include plugin accounts and private plugin data. Use HTTPS, prefer server-side app-specific passwords, and explain the remote storage location and credential handling to users.

## Imperative API

The plugin controls the interaction and transport — good for custom pages, scheduled syncs, and other automated flows.

### ctx.backups.create(options?)

Create an in-memory backup. `settings` and `plugins` default to `true`; both cannot be `false`:

```js
const result = await ctx.backups.create({ settings: true, plugins: true });

if (!result.ok) {
  if (!result.canceled) ctx.toast.warning(result.error || "Backup failed");
  return;
}

console.log(result.fileName, result.summary);
// result.data is an ArrayBuffer, usable directly as a ctx.net.request() body
```

Before creating, the host shows a confirmation dialog telling the user that this plugin will read backup data.

### ctx.backups.inspect(data)

Inspect a downloaded or read `ArrayBuffer` / `ArrayBufferView`, returning the backup summary and a short-lived restore token:

```js
const inspected = await ctx.backups.inspect(downloadedData);
if (!inspected.ok) throw new Error(inspected.error);

console.log(inspected.summary);
```

The token is bound to the inspecting plugin, valid for ten minutes by default, and unusable after a successful restore.

### ctx.backups.restore(token, options?)

Restore a previously inspected backup:

```js
const restored = await ctx.backups.restore(inspected.token, {
  settings: inspected.summary.includes.settings,
  plugins: inspected.summary.includes.plugins,
});

if (!restored.ok && !restored.canceled) {
  throw new Error(restored.error || "Restore failed");
}
```

The host asks the user to confirm again before restoring. On success EchoMusic **restarts automatically** — don't call any restart API yourself.

## Storage Provider API

`ctx.backups.registerProvider(provider)` registers a storage location visible to the app. Once the user selects it in settings, the host works like this:

```text
Create: host picks scope → create → provider.save
Restore: provider.list → provider.load → inspect → host picks scope → restore
```

A minimal provider:

```js
const dispose = ctx.backups.registerProvider({
  id: "webdav",
  name: "WebDAV",
  description: "Save to my WebDAV directory",

  async save({ fileName, data, summary, signal }) {
    // Save data; summary records version, creation time, and included scope
  },

  async list({ signal }) {
    return [
      {
        id: "latest.echomusic-backup",
        name: "Latest backup",
        createdAt: new Date().toISOString(),
        size: 1024,
      },
    ];
  },

  async load({ id, signal }) {
    // Return an ArrayBuffer or ArrayBufferView
    return new ArrayBuffer(0);
  },

  async remove({ id, signal }) {
    // Optional. The host currently doesn't require delete support
  },
});
```

Registration returns an unregister function and is automatically tied to the plugin lifecycle (removed on disable, uninstall, or runtime teardown). The provider `id` is unique within the plugin and may only contain letters, digits, dots, underscores, and hyphens, starting with a letter or digit.

Providers can only be registered from the **main window** plugin runtime; standalone floating windows can still call the imperative API but cannot register providers.

### Provider Fields

| Field | Required | Description |
|------|:--:|------|
| `id` | ✅ | Unique within the plugin, max 64 chars |
| `name` | ✅ | Name shown in settings, max 80 chars |
| `description` | ❌ | Storage description, max 240 chars |
| `save(request)` | ✅ | Save host-generated backup data |
| `list(request)` | ✅ | Return restorable backups (up to 500 shown) |
| `load(request)` | ✅ | Return the backup binary for an entry ID |
| `remove(request)` | ❌ | Delete a backup from storage |

Every request includes `signal: AbortSignal` — operations may be cancelled when the user switches locations, closes the flow, or the plugin is disabled; forward the signal to `ctx.net.request()`.

`list()` entry format: `id` (opaque ID passed back to `load/remove`, required), `name` (required), `createdAt` (ISO 8601, optional), `size` (bytes, optional), `description` (optional).

## Official Example

The [`webdav-backup`](https://github.com/hoowhoami/EchoMusicPlugins) plugin in the official source is a WebDAV provider built on this API — install it directly or read its source code.

## Next Steps

| Document | Content |
|------|------|
| [Network & Downloads →](./network) | Upload/download backups with ctx.net.request |
| [Filesystem & Storage →](./filesystem-storage) | Plugin-private data and KV storage |
| [Context API →](./context-api) | Full ctx API quick reference |
