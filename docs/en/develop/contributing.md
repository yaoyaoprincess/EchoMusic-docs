---
title: Contributing Guide
---

# 🤝 Contributing Guide

Thank you for your interest in EchoMusic! Welcome to project contributions. Please read the following guidelines before submitting code.

## Code of Conduct

- Stay friendly and respectful; embrace people of different backgrounds and experience levels
- Offer constructive criticism and suggestions
- Focus on what is best for the community

## How to Contribute

### Reporting Bugs

If you find a bug, please submit an Issue using the [Bug report template](https://github.com/hoowhoami/EchoMusic/issues/new?template=bug_report.md) and include:

1. **Title**: a concise description of the problem
2. **Environment**: OS version and EchoMusic version
3. **Reproduction steps**: how to trigger the bug in detail
4. **Expected behavior**: what you expected to happen
5. **Actual behavior**: what actually happened
6. **Screenshots or logs**: if applicable

### Feature Suggestions

Please use the [feature request template](https://github.com/hoowhoami/EchoMusic/issues/new?template=feature_request.md):

1. Search the [Issues](https://github.com/hoowhoami/EchoMusic/issues) first to avoid duplicates
2. Describe the feature and its use cases in detail
3. Explain why this feature is valuable to the project

### Issue Automation

- After a new Issue is opened, the `issue-ai-labeler` workflow uses AI to check whether it follows the template rules; Issues missing the required sections (problem description / reproduction steps / environment info, etc.) are automatically labeled `invalid`
- The `issue-closer` workflow runs daily and closes Issues labeled `invalid`, leaving a reminder comment first; once the information is completed, the Issue can be reopened

### Submitting Code

#### Fork and Local Development

````bash
# Fork the repository
# https://github.com/hoowhoami/EchoMusic/fork

# Clone your fork (including the server submodule)
git clone https://github.com/YOUR_USERNAME/EchoMusic.git
cd EchoMusic
git submodule update --init --recursive

# Create a feature branch
git checkout -b feature/my-feature

# Develop...

# Commit
git add .
git commit -m "feat: your feature description"

# Push
git push origin feature/my-feature
````

#### Commit Convention

There is no strict requirement on commit message formats, but please keep them clear:

- `feat: xxx` — new feature
- `fix: xxx` — bug fix
- `docs: xxx` — documentation update
- `refactor: xxx` — code refactoring
- `style: xxx` — code formatting
- `chore: xxx` — build/tooling changes

#### Pull Request Process

1. Make sure your changes run locally (`pnpm dev` starts and the core features work)
2. Run the tests related to your changes (see "Testing" below)
3. Use a clear PR title that describes the change
4. Explain the purpose and scope of the change in the PR description
5. Wait for code review

## Testing

Project tests live in the `tests/` directory and are written with Node.js's built-in `node:test` framework (no third-party test framework) — 275 test files in total (220 `*.test.mjs` + 55 `*.test.ts`).

There is no root-level `test` script in `package.json`; tests are run per file:

````bash
# Run a single JavaScript test
node --test tests/api-request-merge-security.test.mjs

# Run a single TypeScript test (requires Node's type-stripping support:
# Node 22.12+ with --experimental-strip-types; enabled by default in newer versions)
node --test --experimental-strip-types tests/abort-error.test.ts
````

Before submitting a PR, at least run the test files corresponding to the modules you changed; some end-to-end smoke tests (`*.electron-smoke.mjs`) require a full Electron environment.

## Code Standards

### Code Style Tools

The project is configured with the following tools to keep the code style consistent:

| Tool | Config File | Description |
|------|----------|------|
| ESLint | `eslint.config.js` (`.eslintrc.json` is a legacy config kept alongside) | JavaScript/TypeScript/Vue linting |
| Prettier | `.prettierrc` / `.prettierignore` | Code formatting |
| VS Code recommended extensions | `.vscode/extensions.json` | Consistent editor plugins (see below) |

The repository has no `.editorconfig`; consistent editor behavior is ensured through the extensions recommended in `.vscode/extensions.json`.

Common commands:

````bash
pnpm lint    # ESLint check with auto-fix (.vue/.js/.ts/.jsx/.tsx)
pnpm format  # Prettier formatting for src and config files
````

### Frontend (Vue 3 + TypeScript)

- Use the Composition API (`<script setup>`)
- Follow the official Vue 3 style guide
- TypeScript strict mode
- Name components in PascalCase
- File naming follows the repository's existing conventions

### Backend (Node.js)

- Use TypeScript
- Use async/await for asynchronous operations
- Handle errors with try/catch

### Rust Native Modules

- Follow the official Rust coding standards
- Format code with `cargo fmt`
- Lint with `cargo clippy`

## Recommended Development Tools

### VS Code

The project provides `.vscode/extensions.json`; VS Code will prompt to install the recommended extensions when you open the project, including:

- Vue Language Features (Volar)
- ESLint
- Prettier
- Tailwind CSS IntelliSense
- Iconify

## Development Notes

- **Cross-platform compatibility**: make sure your changes work on macOS, Windows, and Linux
- **Native modules**: after modifying Rust code, make sure it compiles on all target platforms (Linux does not build `echo-platform-adaptor`)
- **Dependency management**: use pnpm, do not mix npm/yarn; `server/` is a pnpm workspace member, so a root-level `pnpm install` is enough
- **Backward compatibility**: avoid introducing breaking changes when possible

## Review Process

1. After submitting a PR, wait for the maintainers to review
2. Revise the code according to the review feedback
3. The PR is merged once approved

## Documentation Contributions

Documentation contributions are equally welcome:

- Fix errors or outdated information in the docs
- Add missing documentation content
- Improve readability and structure
- Add usage examples and best practices

## Contact

- [GitHub Issues](https://github.com/hoowhoami/EchoMusic/issues)
- QQ group 1: 1036693403
- QQ group 2: 491694809
- [Telegram](https://telegram.me/+H9vpkAJrDlViZjU1)
