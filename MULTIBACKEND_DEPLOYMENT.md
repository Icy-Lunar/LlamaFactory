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

## Startup diagnostics / 启动诊断（2026-11-05）

The WebUI no longer runs Liger GPU compilation in form, preview, or memory callbacks.
It checks local metadata and verifies real kernels in the training child process.
`--liger required` remains strict: a failed runtime/model check stops training.
Until verified, the memory estimate uses standard kernels without a Liger discount.
Existing output folders without a valid `llamaboard_config.yaml` are safe to select;
they no longer cause `NoneType.items` errors.

WebUI 填表、预览和显存估算不再执行 Liger GPU 编译，只读取本地元数据；真实内核检测
放入训练子进程。`--liger required` 仍为严格模式，设备或模型不兼容时停止，不静默降级。
验证前显存按标准内核保守估算。已有输出目录即使没有有效的 WebUI 配置，也不再发生
`NoneType.items` 错误。此修复不更改 CUDA/XPU 的依赖选择。

ROCm on WSL uses one preprocessing worker, zero DataLoader workers, no pinned
memory, and one Torch CPU thread to avoid forking inherited HIP/OpenMP state.
CUDA, XPU, and native ROCm do not receive these WSL-only settings.
See [PyTorch multiprocessing guidance](https://docs.pytorch.org/docs/2.15/notes/multiprocessing.html).
This is preventive hardening; without a remote stack trace it is not proof of the reported hang's cause.

ROCm/WSL 采用单进程数据预处理、零 DataLoader 子进程、关闭 pinned memory 和单 Torch CPU
线程，避免 fork 继承 HIP/OpenMP 状态。CUDA、XPU 和原生 Linux ROCm 不受这些设置影响。
这是预防性加固；尚无远程堆栈证实该机制就是本次卡住的原因。

| File / 文件 | Contents / 内容 |
| --- | --- |
| `logs/session-*.log` | Installer/WebUI Python output and exceptions; 10 MiB rotation, 5 backups / 安装与 WebUI 输出、异常，单文件 10 MiB，保留 5 个轮转备份 |
| `logs/setup-wizard-*.log` | Timestamped terminal-wizard child output / 终端向导的完整子进程输出与时间戳 |
| `<output>/webui_subprocess.log` | Unbuffered child stdout/stderr, imports, Liger, weight loading and startup stack dumps / 子进程未缓冲输出、导入、Liger、权重加载、启动堆栈 |
| `<output>/lifecycle.jsonl` | Stage changes, PID, 15-second monitor heartbeats and exit codes / 阶段、PID、每 15 秒监测心跳和退出码 |
| `<output>/runtime_state.json` | Current stage and its start timestamp / 当前阶段与起始时间 |
| `<output>/tensorboard_server.log` | Dashboard startup diagnostics / 看板启动日志 |

The UI refreshes every approximately two seconds and reads bounded log tails.
Startup emits stack traces every 120 seconds until the training loop begins.
Import/device/argument stages have a 600-second watchdog; dataset preprocessing,
weight loading, training and evaluation are not killed merely for taking longer.
Distributed initialization defaults to 1800 seconds, not years.
TensorBoard startup failure is logged but does not block the training process.
Both YAML and UTF-8 JSON training configurations are supported. JSON startup is
covered by the same real CPU smoke test because the Cyrene training Plugin emits JSON.
The training child is created **before** TensorBoard; a ready dashboard is not proof
that weights loaded. The normal SFT order is tokenizer → dataset/preprocessing →
model configuration/weights → adapters → training. The live stage identifies which
operation is actually in progress, including work performed before loading weights.

界面约每两秒刷新一次，只读取日志尾部，避免大日志拖慢页面。训练循环开始前每 120 秒
输出堆栈。导入、设备检查、配置解析超过 600 秒会停止任务并显示诊断；数据预处理、
权重加载、正常训练及验证不会仅因耗时较长而被终止。分布式初始化默认超时为 1800 秒。
TensorBoard 启动失败会记录，但不阻止训练启动。
同时支持 YAML 与 UTF-8 JSON 训练配置；Cyrene 训练插件生成 JSON，因此两种格式均覆盖
真实小模型 CPU 训练测试，避免把路径对象错误地当成已打开文件读取。
现在先创建训练子进程，再启动 TensorBoard；看板能打开不代表权重已加载。
SFT 正常顺序是分词器 → 数据集与预处理 → 模型配置与权重 → 适配器 → 训练。
实时阶段会显示当前实际执行的操作，包括加载权重前的数据处理。

Heartbeat means "process alive", not "training is advancing". Old per-run logs are
archived with `.previous` suffixes. Raw training/wizard logs are retained rather than
truncated: monitor disk usage and archive them after a run. They may include paths or
dataset excerpts printed by third-party code; review before sharing. UI/session logs
mask common token/password patterns, but this is not a guarantee of complete sanitization.

心跳仅代表进程存活，不代表训练正在推进。旧任务日志以 `.previous` 后缀保留。
训练原始日志和向导日志不截断，请关注磁盘空间，训练后自行归档。第三方输出可能包含
本地路径或数据样例，分享前请检查；界面和会话日志会遮盖常见令牌、密码格式，但不保证
所有敏感信息均已被识别。真实 ROCm/WSL GPU 验收需要在远程机器重新启动训练后完成。
