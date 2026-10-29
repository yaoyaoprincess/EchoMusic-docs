---
title: Tasks
---

# 📋 Tasks

Plugins can plug long-running work into the EchoMusic task center via `ctx.tasks`. One `register()` call represents one independent run and returns a task handle bound to that run generation.

## Quick Start

```js
export function activate(ctx) {
  const task = ctx.tasks.register({
    id: `${ctx.id}:sync-library`,
    name: "Sync media library",
    status: "running",
    retention: "transient",
    progress: { done: 0, total: 100, percent: 0, label: "Preparing" },
  });

  void runSync(task);
}

async function runSync(task) {
  try {
    for (let done = 0; done < 100; done += 1) {
      if (task.signal.aborted) return;
      await syncOneItem(done, { signal: task.signal });
      task.update({
        progress: { done: done + 1, total: 100, percent: done + 1, label: `${done + 1} / 100` },
      });
    }
    task.finish("completed", { progress: { label: "Sync complete" } });
  } catch (error) {
    if (task.signal.aborted) return;
    task.finish("error", { error: error instanceof Error ? error.message : String(error) });
  }
}
```

## Lifecycle

Task statuses: `pending` (waiting for user action, never auto-cleaned) → `running` → `completed` / `error` / `aborted` (terminal).

- `register()` creates a new run and returns a handle;
- `update()` only updates the current run — it cannot change the status;
- `start(patch?)` moves `pending` to `running`, keeping the same handle and signal;
- `finish()` is the only way from `pending`/`running` into a terminal state;
- Retrying or re-running requires calling `register()` again for a new handle; re-registering with the same ID immediately invalidates the old handle;
- Once a handle is stale, `start()/update()/finish()/cancel()/dismiss()` return `false`;
- When a task is replaced, closed, auto-cleaned, or the plugin is disabled, `task.signal` aborts;
- `finish("aborted")` aborts immediately and shows the aborted state per the retention policy.

> ⚠️ Don't store just the task ID in async callbacks or maintain your own `runId` — capture the handle returned by `register()`.

## Retention (required)

### transient — ordinary background work

- `completed`: auto-cleaned after 5 seconds;
- `aborted`: auto-cleaned after 3 seconds;
- `error`: kept until manually dismissed.

### action-required — tasks needing follow-up

- `completed` / `error`: manual dismissal;
- `aborted`: auto-cleaned after 3 seconds.

### Custom policy

```js
retention: {
  completed: { mode: "auto", delayMs: 8000 },
  error: { mode: "manual" },
  aborted: { mode: "auto", delayMs: 2000 },
}
```

`delayMs` must be a finite number between `0` and `2147483647`.

## Task Handle

| Member | Description |
|------|------|
| `active` | Whether this handle still owns the task entry (terminal states stay active during retention; check `signal.aborted` for business continuation) |
| `signal` | Standard `AbortSignal` — pass it to business functions and check before every irreversible side effect |
| `start(patch?)` | Start a `pending` task; returns `false` for duplicate starts, terminal states, or stale handles |
| `update(patch)` | Update name, icon, priority, progress, error text, `items`, or `actions` (does not change status) |
| `finish(status, patch?)` | End the current run; `status` must be `completed` / `error` / `aborted` |
| `cancel()` | Only aborts the current run's signal — it does not remove the entry; call `finish("aborted")` or `dismiss()` after stopping |
| `dismiss()` | Remove the task immediately and abort its signal |

`progress.percent` may be omitted: with a valid `done` and a positive `total`, the percentage is computed automatically; running tasks with unknown totals show an indeterminate bar.

## Actions

```js
const task = ctx.tasks.register({
  id: `${ctx.id}:download-model`,
  name: "Download model",
  status: "running",
  retention: "action-required",
  actions: [
    {
      id: "cancel",
      label: "Cancel",
      variant: "ghost",
      onClick() {
        if (task.cancel()) {
          task.finish("aborted", { progress: { label: "Cancelled" } });
        }
      },
    },
  ],
});
```

Action fields: `id` (unique within the task), `label`, `variant` (`ghost` / `primary` / `danger`, visual only), `closePanel` (whether to close the panel), `disabled`, `onClick` (sync or async). Action failures never change the task status automatically.

## IDs & Plugin Deactivation

- `echo:` is a host-reserved prefix — plugins cannot register it;
- Task IDs are globally unique in the task center; prefer `${ctx.id}:purpose` naming;
- Plugins cannot override or touch other plugins' tasks;
- When a plugin starts deactivating, its task session is invalidated and all tasks removed — late async callbacks cannot recreate or update old tasks;
- This is a breaking new task API with no legacy per-ID `ctx.tasks.update(id, patch)` / `dismiss(id)` compatibility layer.
