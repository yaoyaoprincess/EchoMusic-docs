---
title: Contributing Guide
---

# 🤝 Contributing Guide

Thank you for your interest in EchoMusic! Welcome to project contributions. Please read the following guidelines before submitting code.

## Code of Conduct

- Be kind and respectful, embrace different perspectives and experience levels
- Provide constructive criticism and suggestions
- Focus on what's best for the community

## How to Contribute

### Reporting Bugs

If you find a bug, please submit an issue using the [Bug Report template](https://github.com/hoowhoami/EchoMusic/issues/new?template=bug_report.md), including:

1. **Title**: Concise problem description
2. **Environment**: OS version, EchoMusic version
3. **Steps to Reproduce**: Detailed steps to trigger the bug
4. **Expected Behavior**: What you expected to happen
5. **Actual Behavior**: What actually happened
6. **Screenshots or Logs**: If applicable

### Feature Suggestions

Please use the [Feature Request template](https://github.com/hoowhoami/EchoMusic/issues/new?template=feature_request.md):

1. Search [Issues](https://github.com/hoowhoami/EchoMusic/issues) first to avoid duplicates
2. Describe the feature in detail with use cases
3. Explain why this feature is valuable to the project

### Issue Automation

- New issues are auto-labeled by the `issue-ai-labeler` workflow
- Long-inactive issues are auto-closed by `issue-closer` after being marked `stale`

### Submitting Code

#### Fork & Local Development

````bash
# Fork the repository
# https://github.com/hoowhoami/EchoMusic/fork

# Clone your fork
git clone https://github.com/YOUR_USERNAME/EchoMusic.git
cd EchoMusic

# Create a feature branch
git checkout -b feature/my-feature

# Develop...

# Commit
git add .
git commit -m "feat: your feature description"

# Push
git push origin feature/my-feature
````

#### Commit Conventions

No strict format required, but clear messages are recommended:

- `feat: xxx` — New feature
- `fix: xxx` — Bug fix
- `docs: xxx` — Documentation update
- `refactor: xxx` — Code refactoring
- `style: xxx` — Formatting
- `chore: xxx` — Build/tooling changes

#### Pull Request Process

1. Ensure code passes local testing
2. Ensure `pnpm dev` starts without errors
3. PR title clearly describes the changes
4. PR description explains the purpose and scope of changes
5. Wait for code review

## Code Standards

### Tooling

The project is configured with the following tools for consistent code style:

| Tool | Config File | Description |
|------|----------|------|
| ESLint | `.eslintrc.json` | JavaScript/TypeScript linting |
| Prettier | `.prettierrc` | Code formatting |
| EditorConfig | `.vscode/extensions.json` | Recommended VS Code extensions |

Install the corresponding editor plugins and enable format-on-save for the best experience.

### Frontend (Vue 3 + TypeScript)

- Use Composition API (`<script setup>`)
- Follow Vue 3 official style guide
- TypeScript strict mode
- PascalCase for component names
- kebab-case for file names

### Backend (Node.js)

- Use TypeScript
- async/await for asynchronous operations
- try/catch for error handling

### Rust Native Modules

- Follow Rust official coding conventions
- Format code with `cargo fmt`
- Lint with `cargo clippy`

## Recommended Dev Tools

### VS Code

Open the project and VS Code will prompt to install recommended extensions from `.vscode/extensions.json`, including:

- Vue Language Features (Volar)
- TypeScript
- Rust Analyzer
- ESLint
- Prettier
- Tailwind CSS IntelliSense

### Claude Code

The project includes `.claude/settings.json` for optimized AI-assisted development with Claude Code.

## Development Notes

- **Cross-platform**: Ensure changes work on macOS, Windows, and Linux
- **Native modules**: After modifying Rust code, verify compilation on all platforms
- **Dependencies**: Use pnpm — do not mix npm/yarn
- **Backward compatibility**: Avoid breaking changes when possible

## Review Process

1. Submit PR and wait for maintainer review
2. Revise based on review feedback
3. PR is merged after approval

## Documentation Contributions

Documentation contributions are equally important:

- Fix errors or outdated information
- Fill in missing documentation
- Improve readability and structure
- Add usage examples and best practices

## Contact

- [GitHub Issues](https://github.com/hoowhoami/EchoMusic/issues)
- QQ Group: 1036693403
- [Telegram](https://t.me/+H9vpkAJrDlViZjU1)
