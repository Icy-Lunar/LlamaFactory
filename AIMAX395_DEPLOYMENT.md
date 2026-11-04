# AMD Ryzen AI Max+ 395 一键部署

本配置面向 Linux 上的 AMD Ryzen AI Max+ 395 / Radeon 8060S（`gfx1151`）。专用入口不会使用通用 ROCm 6.4 源，而是安装 AMD 官方 ROCm 10.1、PyTorch 2.14 和 `gfx1151` 设备包，并使用独立的 `.venv-aimax395` 环境。

Windows 11 机器请改用 [Windows 专用部署指南](AIMAX395_WINDOWS_DEPLOYMENT.md) 和 `start_aimax395.ps1`，不要运行本页的 Bash 入口。

## 1. 主机前提

- 推荐 Ubuntu 24.04 或 26.04、x86-64、Python 3.12。
- Ubuntu 24.04 至少使用 OEM `6.14.0-1018` 或 HWE `6.17.0-19` 内核；其他发行版至少需要包含对应 KFD 修复的 `6.18.4` 内核。
- 裸机必须存在 `/dev/kfd` 和 `/dev/dri/renderD*`。容器或 Jupyter 环境必须由宿主机映射这两个设备。
- 不要设置 `HSA_OVERRIDE_GFX_VERSION`；官方软件包原生包含 `gfx1151`。

检查：

```bash
uname -r
ls -l /dev/kfd /dev/dri/renderD*
python3 --version
```

若 Ubuntu 24.04 的内核过旧，可先在宿主机安装 OEM 内核并重启：

```bash
sudo apt update
sudo apt install -y linux-oem-24.04 python3-venv python3-pip unzip libnuma-dev
sudo reboot
```

内核、驱动和设备映射属于宿主机设置，项目安装脚本只检查，不会未经确认修改内核或重启机器。

## 2. 解压后一次启动

```bash
unzip cyrene-llamafactory-aimax395-ubuntu-20261026.zip
cd cyrene-llamafactory-aimax395-ubuntu-20261026
bash start_aimax395.sh --host-mode network
```

脚本会依次创建虚拟环境、安装 AMD 官方 `gfx1151` PyTorch/ROCm 依赖、安装项目与指标依赖、验证真实 GPU 反向传播、检查 bitsandbytes 和 Liger，然后在 `0.0.0.0:7860` 启动 WebUI。TensorBoard 同样对 Jupyter 端口代理开放。

只安装和验证、不启动 WebUI：

```bash
bash start_aimax395.sh --no-start
```

之后跳过安装直接启动：

```bash
SKIP_INSTALL=1 bash start_aimax395.sh --host-mode network
```

检查输出中的 `device_arch` 必须以 `gfx1151` 开头。专用入口默认 FP16；用户仍可在 WebUI 中自行选择其他精度。Liger 使用兼容性探测，成功才启用，失败会回退标准训练；若部署要求 Liger 必须可用，可增加 `--liger required`。

## 3. 共享显存

AI Max+ 395 使用统一内存。默认 GTT 上限通常约为系统内存的 50%，这可能小于机器的实际可用容量。AMD 建议保持 BIOS 专用显存较小，并通过 TTM/GTT 调整 GPU 可映射的共享内存：

```bash
sudo apt install -y pipx
pipx install amd-debug-tools
amd-ttm
amd-ttm --set 100
```

上例适用于 128 GB 机器，并预留约 28 GB 给操作系统和数据加载；其他内存容量应相应降低。修改后需要重启。WebUI 的显存预估读取 PyTorch 实际报告的可用内存，不把全部系统内存直接当成可训练显存。

## 4. 常见问题

| 现象 | 处理 |
| --- | --- |
| `Kernel ... lacks the required gfx1151 KFD fixes` | 升级到文首要求的内核并重启 |
| `Missing /dev/kfd` | 检查 amdgpu 驱动；容器需映射 `/dev/kfd` |
| `No DRM render device` | 映射 `/dev/dri`，并确保运行账户可访问 `render` / `video` 组 |
| 安装后报告的架构不是 `gfx1151` | 不要继续训练，检查机器型号、设备映射和 PyTorch 软件包来源 |
| 可用显存只有总内存的一半 | 按第 3 节检查和调整 TTM/GTT 上限 |
| 首次 Liger 检查较慢 | 专用入口默认等待 600 秒并复用 `.triton-cache`，后续启动会更快 |

官方参考：

- [ROCm 10.1 PyTorch 安装选择器](https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/frameworks/pytorch/install.html)
- [AMD RDNA3.5 内核与统一内存设置](https://rocm.docs.amd.com/en/latest/reference/system-optimization/rdna3-5.html)
- [bitsandbytes AMD ROCm 安装与 `gfx1151` 支持](https://huggingface.co/docs/bitsandbytes/main/en/installation)
