# Cyrene Yield Training：从这里开始

本发行版支持 NVIDIA CUDA、Intel XPU 和 AMD ROCm。启动器会识别显卡、为所选后端创建独立虚拟环境、安装匹配的 PyTorch 与训练依赖、执行能力检查，然后启动 WebUI。

## Windows

在解压目录中双击 `start_windows.bat`，或在命令提示符中执行：

```bat
start_windows.bat
```

若未安装兼容的 Python，启动器会尝试通过 Windows `winget` 安装 Python 3.12。系统驱动安装可能触发管理员权限确认；驱动安装完成后，重启 Windows 并再次运行同一文件。

## Linux

在解压目录执行：

```bash
bash start_linux.sh
```

若缺少 Python 或 `venv`，脚本会尝试通过 `apt`、`dnf`、`zypper` 或 `pacman` 安装基础环境。Linux 自动安装 GPU 系统驱动的完整支持范围是 Ubuntu；其他发行版应先安装厂商驱动。

## Ryzen AI Max+ 395 的 WSL2 启动

Windows 11 上的 Radeon 8060S 使用专用入口。显卡驱动安装在 Windows 主机，不要在 WSL 内安装 `amdgpu-dkms`，WSL 中没有 `/dev/kfd` 也是正常现象：

```bash
bash start_aimax395.sh --host-mode network --liger auto
```

脚本会检查 WSL 的 `/dev/dxg` 与 Windows AMD 显卡，创建独立的 `.venv-aimax395-wsl`，安装 ROCm 10.1、PyTorch 2.14 和 `gfx1151` 设备包，然后用真实的 GPU 反向传播验证环境。若更新过 Windows 显卡驱动，应先在 Windows PowerShell 执行 `wsl --shutdown`，再重新进入 Ubuntu。

## 无交互参数

单显卡平台通常可以自动识别。也可以明确指定：

```bat
start_windows.bat --backend cuda --host-mode local --liger auto
```

```bash
bash start_linux.sh --backend rocm --host-mode network --liger auto
```

`local` 仅允许本机访问；远程服务器或 JupyterLab 使用 `network`。不要把未配置认证和防火墙的端口直接暴露到公网。

完整零基础说明见 `BEGINNER_GUIDE_ZH.md`，部署矩阵见 `MULTIBACKEND_DEPLOYMENT.md`。
