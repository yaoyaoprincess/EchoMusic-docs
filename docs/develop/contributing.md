---
title: 贡献指南
---

# 🤝 贡献指南

感谢你对 EchoMusic 的关注！欢迎参与项目贡献。在提交代码之前，请阅读以下规范。

## 行为准则

- 保持友善和尊重，包容不同观点和经验水平
- 建设性地提出批评和建议
- 关注对社区最有利的事情

## 如何贡献

### 报告 Bug

如果你发现了 Bug，请使用 [Bug 报告模板](https://github.com/hoowhoami/EchoMusic/issues/new?template=bug_report.md) 提交 Issue，并包含：

1. **标题**：简洁描述问题
2. **环境信息**：操作系统版本、EchoMusic 版本
3. **复现步骤**：详细描述如何触发该 Bug
4. **预期行为**：描述你原本期望的结果
5. **实际行为**：描述实际发生的情况
6. **截图或日志**：如果适用

### 功能建议

请使用 [功能请求模板](https://github.com/hoowhoami/EchoMusic/issues/new?template=feature_request.md) 提交：

1. 先搜索 [Issues](https://github.com/hoowhoami/EchoMusic/issues)，确认没有重复
2. 详细描述功能需求和适用场景
3. 说明为什么这个功能对项目有价值

### Issue 自动化

- 新建 Issue 后，`issue-ai-labeler` 工作流会用 AI 判定内容是否符合模板规范，不符合模板要求（缺少问题描述/复现步骤/环境信息等）的 Issue 会被自动标记 `invalid`
- 每日定时运行的 `issue-closer` 工作流会关闭被标记 `invalid` 的 Issue，关闭前会留言提醒；补充信息后可重新开启

### 提交代码

#### Fork 与本地开发

````bash
# Fork 仓库
# https://github.com/hoowhoami/EchoMusic/fork

# 克隆你的 Fork（含 server 子模块）
git clone https://github.com/YOUR_USERNAME/EchoMusic.git
cd EchoMusic
git submodule update --init --recursive

# 创建功能分支
git checkout -b feature/my-feature

# 开发...

# 提交
git add .
git commit -m "feat: your feature description"

# 推送
git push origin feature/my-feature
````

#### Commit 规范

对提交消息格式没有严格要求，但建议保持清晰明了：

- `feat: xxx` — 新功能
- `fix: xxx` — Bug 修复
- `docs: xxx` — 文档更新
- `refactor: xxx` — 代码重构
- `style: xxx` — 代码格式
- `chore: xxx` — 构建/工具变更

#### Pull Request 流程

1. 确保改动在本地可以正常运行（`pnpm dev` 启动、核心功能可用）
2. 运行与改动相关的测试（见下文"测试"）
3. PR 标题清晰描述改动内容
4. PR 描述中说明改动的目的和范围
5. 等待代码审查

## 测试

项目测试位于 `tests/` 目录，使用 Node.js 内置的 `node:test` 框架编写（无第三方测试框架），共 275 个测试文件（220 个 `*.test.mjs` + 55 个 `*.test.ts`）。

`package.json` 中没有根级 `test` 脚本，测试按文件直接运行：

````bash
# 运行单个 JavaScript 测试
node --test tests/api-request-merge-security.test.mjs

# 运行单个 TypeScript 测试（需要 Node 的类型剥离支持：
# Node 22.12+ 使用 --experimental-strip-types，更高版本默认支持）
node --test --experimental-strip-types tests/abort-error.test.ts
````

提交 PR 前建议至少运行与改动模块对应的测试文件；部分端到端冒烟测试（`*.electron-smoke.mjs`）需要完整的 Electron 环境。

## 代码规范

### 代码风格工具

项目已配置以下工具以保证代码风格一致：

| 工具 | 配置文件 | 说明 |
|------|----------|------|
| ESLint | `eslint.config.js`（`.eslintrc.json` 为旧版并存配置） | JavaScript/TypeScript/Vue 代码检查 |
| Prettier | `.prettierrc` / `.prettierignore` | 代码格式化 |
| VS Code 推荐扩展 | `.vscode/extensions.json` | 统一编辑器插件（见下文） |

仓库没有 `.editorconfig`；编辑器行为统一通过 `.vscode/extensions.json` 推荐扩展保证。

常用命令：

````bash
pnpm lint    # ESLint 检查并自动修复（.vue/.js/.ts/.jsx/.tsx）
pnpm format  # Prettier 格式化 src 与配置文件
````

### 前端 (Vue 3 + TypeScript)

- 使用 Composition API（`<script setup>`）
- 遵循 Vue 3 官方风格指南
- TypeScript 严格模式
- 组件命名使用 PascalCase
- 文件命名遵循仓库现有约定

### 后端 (Node.js)

- 使用 TypeScript
- 异步操作使用 async/await
- 错误处理使用 try/catch

### Rust 原生模块

- 遵循 Rust 官方编码规范
- 使用 `cargo fmt` 格式化代码
- 使用 `cargo clippy` 进行 lint 检查

## 开发工具推荐

### VS Code

项目提供 `.vscode/extensions.json`，打开项目时 VS Code 会提示安装推荐扩展，包括：

- Vue Language Features (Volar)
- ESLint
- Prettier
- Tailwind CSS IntelliSense
- Iconify

## 开发注意事项

- **跨平台兼容**：确保改动在 macOS、Windows、Linux 三平台上都正常工作
- **原生模块**：修改 Rust 代码后，确保在所有目标平台上编译通过（Linux 不构建 `echo-platform-adaptor`）
- **依赖管理**：使用 pnpm，不要混用 npm/yarn；`server/` 是 pnpm workspace 成员，根目录 `pnpm install` 即可
- **向后兼容**：尽量不要引入破坏性更改

## 审核流程

1. 提交 PR 后，等待项目维护者审核
2. 根据审核意见修改代码
3. PR 通过审核后合并

## 文档贡献

文档贡献同样重要：

- 修正文档中的错误或过时信息
- 补充缺失的文档内容
- 改进文档的可读性和结构
- 添加使用示例和最佳实践

## 联系方式

- [GitHub Issues](https://github.com/hoowhoami/EchoMusic/issues)
- QQ 1 群：1036693403
- QQ 2 群：491694809
- [Telegram](https://telegram.me/+H9vpkAJrDlViZjU1)
