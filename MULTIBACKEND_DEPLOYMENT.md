# CUDA、XPU、ROCm 统一部署

发行包的首选入口已经统一为：

- Windows：双击或执行 `start_windows.bat`
- Linux：执行 `bash start_linux.sh`

这两个入口会先准备兼容的 Python 与 `venv`，随后进入同一套硬件识别和依赖安装流程。原有 `start_multibackend.*` 和 `start_wizard.*` 保留为高级入口。

第一次接触 Python 或模型训练，请先阅读[零基础完整使用手册](BEGINNER_GUIDE_ZH.md)。该手册从解压、启动、本地模型与数据准备开始，完整说明 WebUI、显存检查、checkpoint、TensorBoard 和 LoRA 合并。

本目录提供同一份训练项目，启动时根据显卡厂商选择 CUDA、Intel XPU 或 AMD ROCm，并为每种后端创建互不污染的虚拟环境：

```text
.venv-cuda-windows / .venv-cuda-linux
.venv-xpu-windows  / .venv-xpu-linux
.venv-rocm-windows / .venv-rocm-linux
```

## 彩色交互向导（推荐）

Windows 11 可以直接双击：

```text
start_multibackend.cmd
```

该入口会申请管理员权限并打开彩色终端向导。用户只需要按数字选择语言、训练后端、驱动处理方式、WebUI 访问范围和加速策略，不需要记住安装参数。向导会先展示完整摘要，确认后才执行安装。

向导会优先复用已经通过检查的后端环境。再次运行时默认显示“快速启动”，不会重复下载和安装；需要补齐依赖时再选择“修复或补齐依赖”。Ryzen AI Max+ 395 会识别并复用旧版专用 `.venv-aimax395-windows` / `.venv-aimax395`，避免与统一入口重复创建第二套 ROCm 环境。

Windows 一行命令：

```powershell
powershell -ExecutionPolicy Bypass -File .\start_wizard.ps1
```

Ubuntu 一行命令：

```bash
bash start_wizard.sh
```

`start_multibackend.ps1` 或 `start_multibackend.sh` 在不带参数时也会进入同一个交互向导；带高级参数时仍保留无交互自动化能力。

向导不依赖 Rich、Textual 等第三方终端库，未安装项目依赖时也能启动；支持简体中文、英语、俄语、韩语和日语。每次运行的完整安装输出会保存到 `logs/setup-wizard-日期-时间.log`，便于把错误日志交给运维人员。

终端只显示硬件、环境、下载、安装、运行时、能力验证和启动阶段。Python traceback、pip 包清单等技术细节只写入完整日志。显卡运行时、磁盘、端口、Liger/Triton 和 Windows 应用控制错误会显示成带背景色的原因与下一步页面。

加速策略有三种：

- 兼容优先：尝试 Liger；不可用时保留标准 GPU 训练。
- 标准训练：不安装或启用 Liger。
- 全部能力严格可用：同时要求 Liger、bitsandbytes、torchvision 和 torchaudio 的真实运行检查通过，否则停止。严格模式遇到可选能力失败时，向导会询问是否切换到兼容模式。

Windows AMD ROCm 安装完成后，向导还会自动展开 pip ROCm SDK、补全虚拟环境工具路径，并允许首次设备加载最长 300 秒、最多三次探测，避免将“首次加载较慢”误判成 GPU 不可用。

## 无交互自动化入口（高级）

服务器批量部署或已经熟悉命令行的用户仍可直接传参：

如果同一台机器同时存在多种显卡，需要明确选择：

```powershell
.\start_multibackend.ps1 --backend cuda --host-mode network
.\start_multibackend.ps1 --backend xpu --host-mode network
.\start_multibackend.ps1 --backend rocm --host-mode network
```

## 系统驱动

默认 `--driver-mode auto`：驱动已可用时不会重装；缺失时才进入驱动安装阶段。驱动安装完成后程序停止并要求重启，重启后再次执行同一入口，才会安装 Python 依赖并启动 WebUI。

Ubuntu：

- NVIDIA 使用 Ubuntu 的硬件驱动选择器安装计算驱动；PyTorch wheel 自带所需 CUDA 用户态运行库，不额外安装完整 CUDA Toolkit。
- AMD 独立显卡使用 AMD ROCm 10.1 官方 runfile 安装 `amdgpu` 内核驱动。
- Ryzen AI Max APU 使用 Ubuntu 支持版本自带的 `amdgpu` 驱动，统一入口不会用独立显卡安装器覆盖它。
- XPU 会检查 Intel 驱动，但不会自动替换系统图形栈。

Windows：厂商驱动与具体硬件型号绑定，项目不重新分发驱动二进制。将已审核的官方安装器放入 `drivers` 目录后双击一键入口，程序会自动执行静默安装：

```text
drivers/nvidia-driver.exe
drivers/amd-driver.exe
```

也可以直接指定本地文件或厂商 HTTPS 地址：

```powershell
.\start_multibackend.ps1 --backend cuda --driver-mode install --driver-installer C:\Installers\nvidia.exe
.\start_multibackend.ps1 --backend rocm --driver-mode install --driver-url https://vendor.example/approved-driver.exe
```

`--driver-mode install` 强制重新执行驱动安装；`--driver-mode skip` 跳过驱动处理，仅适合已经由运维统一配置驱动的主机。

## 依赖选择

| 后端 | Python 运行时来源 | 说明 |
| --- | --- | --- |
| CUDA | PyTorch `cu128` 索引 | 安装后验证 NVIDIA 设备和真实反向传播 |
| XPU | PyTorch 官方 XPU 索引 | 固定匹配的 Torch、vision、audio 组合，保留 XPU Triton |
| ROCm / Linux | PyTorch ROCm 索引 | 与 CUDA 环境完全分离 |
| ROCm / Windows Max+ 395 | AMD ROCm 10.1 `gfx1151` 包 | 自动安装 ML 库、设备库和开发组件 |

Liger 默认采用 `auto`：兼容性检查成功才启用，否则回退标准训练。首次排查可以使用：

```powershell
.\start_multibackend.ps1 --no-start --liger off
```

所有后端都必须通过 `pip check`、设备识别和小张量反向传播后才会启动 WebUI，不会静默回退到 CPU。
