---
title: 任务面板
---

# 📋 任务面板

插件可以通过 `ctx.tasks` 把长时间运行的工作接入 EchoMusic 任务中心。一次 `register()` 代表一次独立运行，并返回绑定该运行世代的 task handle。

## 快速开始

```js
export function activate(ctx) {
  const task = ctx.tasks.register({
    id: `${ctx.id}:sync-library`,
    name: "同步媒体库",
    status: "running",
    retention: "transient",
    progress: { done: 0, total: 100, percent: 0, label: "准备中" },
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
    task.finish("completed", { progress: { label: "同步完成" } });
  } catch (error) {
    if (task.signal.aborted) return;
    task.finish("error", { error: error instanceof Error ? error.message : String(error) });
  }
}
```

## 生命周期

任务状态：`pending`（等待用户操作，不自动清理）→ `running` → `completed` / `error` / `aborted`（终态）。

- `register()` 创建一轮新任务并返回 handle；
- `update()` 只更新当前运行，不允许改变状态；
- `start(patch?)` 将 `pending` 变为 `running`，保留同一个 handle 和 signal；
- `finish()` 是从 `pending` 或 `running` 进入终态的唯一方式；
- 重试或重新运行必须再次调用 `register()`，获得新的 handle；同一插件用相同 ID 重新注册时，旧 handle 立即失效；
- handle 失效后，`start()/update()/finish()/cancel()/dismiss()` 返回 `false`；
- 任务被替换、关闭、自动清理或插件停用时，`task.signal` 触发 abort；
- `finish("aborted")` 会立即触发 abort，并按保留策略展示中止状态。

> ⚠️ 不要在异步回调中只保存任务 ID 或自行维护 `runId`——直接捕获本次 `register()` 返回的 handle。

## 保留策略（retention，必填）

### transient —— 普通后台工作

- `completed`：展示 5 秒后自动清理；
- `aborted`：展示 3 秒后自动清理；
- `error`：保留到用户手动关闭。

### action-required —— 完成后仍需操作的任务

- `completed` / `error`：手动关闭；
- `aborted`：展示 3 秒后自动清理。

### 自定义策略

```js
retention: {
  completed: { mode: "auto", delayMs: 8000 },
  error: { mode: "manual" },
  aborted: { mode: "auto", delayMs: 2000 },
}
```

`delayMs` 必须是 `0` 到 `2147483647` 之间的有限数字。

## Task Handle

| 成员 | 说明 |
|------|------|
| `active` | 该 handle 是否仍拥有当前任务条目（终态在保留期间仍为 active；判断业务是否继续应同时检查 `signal.aborted`） |
| `signal` | 标准 `AbortSignal`，应传给支持 signal 的业务函数，并在每个不可撤销副作用前检查 |
| `start(patch?)` | 将 `pending` 任务开始执行；重复开始、终态或失效的 handle 返回 `false` |
| `update(patch)` | 更新名称、图标、优先级、进度、错误文本、`items` 明细或 `actions`（不改变状态） |
| `finish(status, patch?)` | 结束当前运行，`status` 只能是 `completed` / `error` / `aborted` |
| `cancel()` | 只触发当前运行的 AbortSignal，不删除条目；调用方应在业务停止后 `finish("aborted")` 或 `dismiss()` |
| `dismiss()` | 立即移除当前任务并触发 AbortSignal |

`progress.percent` 可省略：提供有效的 `done` 和大于零的 `total` 时自动计算百分比；数量未知的运行中任务显示不确定进度条。

## 操作按钮（actions）

```js
const task = ctx.tasks.register({
  id: `${ctx.id}:download-model`,
  name: "下载模型",
  status: "running",
  retention: "action-required",
  actions: [
    {
      id: "cancel",
      label: "取消",
      variant: "ghost",
      onClick() {
        if (task.cancel()) {
          task.finish("aborted", { progress: { label: "已取消" } });
        }
      },
    },
  ],
});
```

Action 字段：`id`（任务内唯一）、`label`（按钮文字）、`variant`（`ghost` / `primary` / `danger`，仅控制视觉层级）、`closePanel`（触发后是否关闭面板）、`disabled`（禁用按钮）、`onClick`（同步或异步回调）。Action 失败不会自动改变任务状态。

## ID 与插件停用

- `echo:` 是主程序保留前缀，插件不能注册；
- 任务 ID 在任务中心全局唯一，推荐 `${ctx.id}:用途` 命名；
- 插件不能覆盖或操作其他插件的任务；
- 插件开始停用时任务会话先失效、所有任务被移除，迟到的异步回调无法重新创建或更新旧任务；
- 这是破坏性的新任务 API，不提供旧版按 ID 的 `ctx.tasks.update(id, patch)` / `dismiss(id)` 兼容层。
