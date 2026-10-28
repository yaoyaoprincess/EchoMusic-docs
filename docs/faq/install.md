---
title: 安装与启动
---

# 🚀 安装与启动

### 如何下载 EchoMusic {#download}

EchoMusic 提供两种下载渠道：

1. **GitHub Releases**（推荐）：访问 https://github.com/hoowhoami/EchoMusic/releases ，提供各系统全量安装包
2. **QQ 群文件**：在群文件的「正式版」「测试版」文件夹中获取，仅提供 Windows 安装包，其余系统请到 GitHub 发布页下载

安装包与系统对应关系：

| 系统 | 安装包 |
| ---- | ------ |
| Windows | Windows-Setup-x64 |
| macOS（Intel 芯片） | mac-x64 |
| macOS（Apple Silicon） | macOS-arm64 |

### Windows 提示「Windows 已保护你的电脑」 {#windows-smartscreen}

这是 SmartScreen 的安全提示，点击「更多信息」→「仍要运行」即可继续安装。

### Windows 安装后没有主程序，只有卸载程序 {#wrong-arch}

安装包与系统架构不匹配，导致主程序未能正确安装。若不确定自己电脑的架构，优先使用 **x64 安装包**。

### macOS 提示「无法验证开发者」 {#macos-gatekeeper}

这是 macOS Gatekeeper 的安全机制，不影响正常使用，任选一种方法解决：

```bash
xattr -cr /Applications/EchoMusic.app
```

也可以在系统设置中放行：**系统设置 → 隐私与安全性 → 点击「仍要打开」**。

### Linux AppImage 无法运行 {#appimage}

确保已赋予可执行权限后再运行：

```bash
chmod +x EchoMusic-*.AppImage
./EchoMusic-*.AppImage
```

### 启动后闪退 {#crash-on-start}

1. 检查系统版本是否满足最低要求
2. 尝试以管理员/root 权限运行
3. 检查是否有安全软件拦截

### 启动提示「播放引擎初始化失败」或「设备注册失败」 {#engine-init-fail}

多与网络环境或安全策略有关，可依次尝试：

1. 关闭代理/加速服务后重试，或在「设置 → 网络 → 全局网络代理」中选择「直接连接」
2. 检查是否被安全软件、Windows Defender 或应用程序控制策略拦截，将 EchoMusic 加入白名单
3. 更换网络环境（如手机热点）后重试
4. 若提示为「播放引擎初始化失败」，可先更新到最新版本
5. 仍无法进入时，点击弹窗中的「仍然进入」，在设置中导出日志，向群主/开发者反馈

### 如何用命令行启动排查问题 {#console-log}

在程序根目录打开终端，执行以下命令启动，将终端输出的日志截图发到群里求助：

```bash
.\EchoMusic.exe --console
```
