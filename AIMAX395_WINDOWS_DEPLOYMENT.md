# AMD Ryzen AI Max+ 395 Windows 一键部署

本配置面向 Windows 11 上的 AMD Ryzen AI Max+ 395 / Radeon 8060S（`gfx1151`）。不需要预先手工安装 Linux 版 ROCm，也不需要把 ROCm 安装到全局 Python。主机需要先安装兼容的 AMD Windows 显卡驱动；专用脚本会在隔离的 `.venv-aimax395-windows` 中安装 AMD 官方 ROCm 10.1、PyTorch 2.14、ML 库、`gfx1151` 设备库和用于 Triton/Liger 的开发组件。

## 1. 主机前提

- Windows 11 x86-64。
- 推荐 Python 3.12 x64，并确保 `py -3.12` 可用。
- 安装当前与 ROCm 10.1 兼容的 AMD Software 驱动。
- 安装 Microsoft Visual C++ 2015–2022 Redistributable x64。
- 保留足够磁盘空间；PyTorch、ROCm 设备库和开发组件体积较大。

当前 Windows 安装不使用 `HSA_OVERRIDE_GFX_VERSION`，也不复用 CUDA/XPU 虚拟环境。

## 2. 解压后一次启动

在 PowerShell 中执行：

```powershell
Expand-Archive .\cyrene-llamafactory-aimax395-windows-20261026.zip -DestinationPath .
Set-Location .\cyrene-llamafactory-aimax395-windows-20261026

powershell -ExecutionPolicy Bypass -File .\start_aimax395.ps1 --host-mode network
```

脚本会创建独立环境并安装固定组合：

```text
ROCm 10.1.0
PyTorch 2.14.0
torchvision 0.29.0a0
gfx1151 device libraries
ROCm development components for Triton/Liger
```

安装结束必须同时通过以下检查，才会启动 WebUI：

- `torch.cuda.is_available()` 对 AMD GPU 返回 `True`。
- `torch.version.hip` 存在，证明不是误装 CUDA/CPU PyTorch。
- 设备架构以 `gfx1151` 开头。
- 小张量前向和反向传播成功。
- bitsandbytes 4-bit 后端会执行真实前向/反向探测；不可用时明确禁用量化能力，但不阻断普通 LoRA/Full 训练。
- Liger/Triton 成功则启用；失败时默认回退标准训练。

只安装和验证：

```powershell
.\start_aimax395.ps1 --no-start
```

后续跳过安装直接启动：

```powershell
$env:SKIP_INSTALL = "1"
.\start_aimax395.ps1 --host-mode network
```

## 3. 支持边界

旧版 ROCm 7.2.1 Windows 文档明确限制了 ML 训练，因此专用入口不会使用项目原有的通用 Windows ROCm 7.2.1 分支。当前入口使用 ROCm 10.1 / PyTorch 2.14，并用真实反向传播检查作为启动门槛。由于开发机没有 Ryzen AI Max+ 395，不能把自动化测试描述成 Windows 395 实机训练验证；首次安装输出才是该机器的最终兼容性证据。

Liger 是可选加速项。在 Windows ROCm 上如果 Triton 编译器、驱动或算子不兼容，WebUI 会继续使用标准训练。初次部署不要传 `--liger required`；先确认普通 LoRA/Full 训练可运行。

如果日志出现 `WinError 4551`，说明 Windows 应用控制策略阻止了 Triton 临时编译文件、bitsandbytes 原生 DLL，或 torchvision/torchaudio 扩展。此时基础 ROCm 文本训练仍可继续，但应保持不量化并让 Liger 自动回退；被阻止的视觉或音频扩展所对应的多模态预处理不可用。需要这些能力时，应由设备管理员审核并按组织策略放行文件；安装器不会自动关闭或绕过系统安全策略。

官方参考：

- [ROCm 10.1 PyTorch 安装说明](https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/frameworks/pytorch/install.html)
- [ROCm 10.1 Windows/Python 安装方式](https://rocm.docs.amd.com/en/latest/install/rocm.html)
- [Windows HIP SDK 支持设备](https://rocm.docs.amd.com/projects/install-on-windows/en/latest/reference/system-requirements.html)
