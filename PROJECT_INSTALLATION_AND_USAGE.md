# Cyrene Yield Training / LlamaFactory 完整安装与操作指南

更新日期：2026-10-06。本文以本仓库当前实现为准，整合设备依赖安装、环境检查、WebUI 操作、显存估算、训练监控和适配器合并。

本文中的 Windows 项目路径 `E:\trainer\LlamaFactory-main` 和模型路径 `E:\model` 是本机示例；其他机器请替换为实际路径。Linux 示例中的 `/path/to/project` 等也是占位路径。

## 1. 本项目做了哪些调整

本项目基于 LLaMAFactory，主要提供本地模型训练和 LoRA 适配器合并。WebUI 使用分步引导，按用户选择显示相关设置，支持中文、英语、俄语、韩语和日语。界面文案通过本地化资源显示。

| 方面 | 当前行为 |
| --- | --- |
| 模型来源 | 从本地目录读取，不提供模型下载流程，也不要求用户手填模型大小 |
| 训练流程 | 选择模型与目标 → 选择数据 → 按需调整 → 检查并训练 |
| 参数配置 | 自动建议参数，用户仍可修改；按训练任务和微调方法显示相关选项 |
| 微调方法 | 支持 LoRA、Full、Freeze、OFT；并非只能使用 LoRA |
| 量化 | 默认不量化，可选择 4-bit / 8-bit；必须符合微调方法和设备后端的限制 |
| 显存估算 | 读取模型配置与权重文件大小，随关键超参数变化更新估计，训练前再次检查 |
| 风险提示 | 建议显存为估计值的 110%；不足或无法可靠确认时提示风险，强行继续需要确认 |
| 多模态 | 保留视觉塔、视觉投影层、语言模型冻结和图像/视频像素限制等设置 |
| 监控 | WebUI 默认使用 TensorBoard，开始训练时启动对应输出目录的监控服务 |
| 功能范围 | 不提供独立推理/评测入口；训练过程内的验证配置仍然保留 |
| 适配器合并 | 保留 LoRA 合并，本地导出，不提供上传模型或导出时再次量化的流程 |
| 依赖安装 | 自动检测设备，安装对应 PyTorch 后端，同时保留项目公共依赖与 metrics 依赖 |
| Liger Kernel | 兼容时启用，不兼容时禁用；不再无条件强制安装和启用 |

注意：保留 `modelscope`、`hf-transfer`、`fastapi` 等底层依赖，不代表重新开放模型下载或独立 API 服务等业务入口。

## 2. 快速开始

### 2.1 Windows：安装并启动

先安装 64 位 Python。项目要求 Python 3.11 或更高，建议使用 Python 3.12；AMD Windows 默认安装方案要求 Python 3.12。

在 PowerShell 中运行：

```powershell
Set-Location E:\trainer\LlamaFactory-main
.\start_webui.ps1
```

脚本默认使用项目下的 `.venv`，没有则创建。它会检测设备、安装依赖、验证运行环境，然后启动 WebUI。无需事先激活虚拟环境。

如果 PowerShell 因本机执行策略阻止脚本，并且你已检查并信任仓库中的脚本，可仅对本次子进程运行放行：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\start_webui.ps1
```

默认访问地址为 [http://127.0.0.1:7860](http://127.0.0.1:7860)。以终端实际输出的监听地址为准；旧预览使用过的 `8788` 不一定仍在监听。

### 2.2 Linux：安装并启动

```bash
cd /path/to/project
bash start_webui.sh
```

需要 Python 3.11+、可用的 `venv` 模块，以及设备对应的系统驱动。Windows 和 Linux/WSL 不能共用同一个虚拟环境目录。

### 2.3 已安装后再次启动

Windows：

```powershell
.\start_webui.ps1 --skip-install
```

Linux：

```bash
bash start_webui.sh --skip-install
```

`--skip-install` 只跳过安装，仍会执行依赖和设备运行检查。如果更新了项目依赖，请重新运行不带该参数的启动脚本。

终端需要保持运行。关闭 WebUI 前先停止并确认训练任务已退出；不要在训练中直接结束整个终端进程。

## 3. 安装前需要准备什么

- Python 与足够的磁盘空间：模型、虚拟环境、下载缓存、训练检查点都会占用空间。
- 可用网络：首次安装需要访问 PyPI、PyTorch 或设备厂商的软件源。模型文件请自行预先准备。
- 正确的显卡/NPU 驱动。脚本不会自动安装内核驱动、刷写固件或重启系统。
- 本地完整模型目录与训练数据。只有模型配置文件而没有权重，不能开始训练。
- 使用 Triton/JIT 编译的功能时，需要对应平台的编译工具链。

Intel Windows 环境若提示缺少 `cl.exe`，可在 Visual Studio Build Tools 中安装“使用 C++ 的桌面开发”、MSVC 编译工具及 Windows SDK。项目会尝试发现已安装的 MSVC 环境，但不会代替用户安装编译器。Linux 编译依赖需要按发行版和加速库要求准备。

“Intel CPU”不等于“支持 XPU 加速的 Intel GPU”。设备识别依据显卡/NPU，而不是 CPU 品牌；识别到设备也不等于该型号受所选软件版本支持。

## 4. 自动安装的执行流程

入口文件是 [start_webui.ps1](start_webui.ps1) 和 [start_webui.sh](start_webui.sh)，共用 [scripts/bootstrap_webui.py](scripts/bootstrap_webui.py)。

1. 读取安装参数，检查 Python 和虚拟环境所属操作系统。
2. 检测设备与已有 PyTorch 运行环境，选择后端。
3. 如有需要，创建虚拟环境并安装设备对应的 PyTorch。
4. 生成临时硬件版本约束，保护已有可用的 Torch、Triton 及设备运行库。
5. 安装本项目与 metrics 依赖。
6. 根据后端与依赖解析结果尝试安装 Liger；不兼容时按策略禁用。
7. 执行 `pip check`、设备反向传播和相关依赖检查。
8. 检查通过后启动 WebUI，或按参数只完成安装/检查。

公共依赖安装包含以下两项；自动脚本还会附加硬件版本约束：

```bash
python -m pip install -e .
python -m pip install -r requirements/metrics.txt
```

不要将这两条命令理解为“在空环境中即可自动选对显卡后端”。手动安装时需要先准备正确的 PyTorch。优先使用本项目启动脚本，避免重新解析依赖时替换掉已经可用的 XPU/ROCm/NPU 运行库。

### 4.1 设备分支与默认安装方案

下表是当前脚本对新环境采用的方案，不是对所有型号的兼容承诺，也不代表厂商永久不变的最新版本。

| 设备 | 参数 | 新环境默认方案 | 注意事项 |
| --- | --- | --- | --- |
| NVIDIA | `--backend cuda` | PyTorch 官方 `cu128` 源中的 torch / torchvision / torchaudio | 驱动和 GPU 型号必须支持所选构建 |
| Intel GPU | `--backend xpu` | 官方 XPU 源；torch 2.13.0、torchvision 0.28.0、torchaudio 2.11.0 | 不要根据 Torch 版本自行推断 torchaudio 必须同版本 |
| AMD / Linux | `--backend rocm` | PyTorch 官方 `rocm6.4` 源 | 需要受支持的 GPU、系统及驱动组合 |
| AMD / Windows | `--backend rocm` | AMD ROCm 7.2.1 Windows wheel 方案；torch 2.9.1、vision 0.24.1、audio 2.9.1 | 要求 Python 3.12、Windows x64；仅适用于厂商支持的设备 |
| 华为昇腾 / Linux | `--backend npu` | 读取 `requirements/npu.txt`，安装 Torch 与 torch-npu 配套版本 | 驱动、固件、CANN Toolkit/算子包需匹配 |
| CPU | `--backend cpu` | PyTorch 官方 CPU 源 | 不启用 Liger；大型模型训练可能非常慢，仍受内存限制 |

自动模式会优先保留已有可用且与检测结果一致的加速后端；否则按 CUDA → NPU → XPU → ROCm 选择，没有检测到加速设备则选择 CPU。多设备机器建议显式指定 `--backend`。

如果已有环境与目标后端不一致，脚本会停止，要求使用新的虚拟环境；不会直接把现有环境改造成另一种后端。识别出加速器但 PyTorch 无法使用时，也不会静默降级到 CPU。

### 4.2 指定设备与隔离环境

Windows 示例，按实际设备选其中一个：

```powershell
.\start_webui.ps1 --backend xpu --venv .venv-xpu
.\start_webui.ps1 --backend cuda --venv .venv-cuda
.\start_webui.ps1 --backend cpu --venv .venv-cpu
```

Linux 示例：

```bash
bash start_webui.sh --backend rocm --venv .venv-rocm
```

这些是替代方案，不要求全部执行。以后启动或检查时应使用同一组 `--backend` 与 `--venv` 参数。

`--venv` 指定环境目录，不负责选择创建环境所用的 Python 版本。需要明确使用 Python 3.12 时，可以直接通过该解释器运行安装器：

```powershell
py -3.12 scripts/bootstrap_webui.py --backend rocm --venv .venv-rocm
```

```bash
python3.12 scripts/bootstrap_webui.py --backend rocm --venv .venv-rocm
```

### 4.3 常用安装参数

| 参数 | 含义 |
| --- | --- |
| `--backend auto/cuda/xpu/rocm/npu/cpu` | 自动识别或指定后端，默认 `auto` |
| `--venv PATH` | 指定虚拟环境，默认项目 `.venv` |
| `--dry-run` | 只查看安装计划，不创建环境、不安装包、不启动服务 |
| `--no-start` | 安装并验证，不启动 WebUI |
| `--check-only` | 只检查已有环境，不安装、不启动 |
| `--skip-install` | 跳过安装，检查通过后启动 |
| `--host-mode ask/local/network` | 启动时询问访问方式、仅绑定本机，或绑定 `0.0.0.0` 供 Jupyter/LAN 访问；默认 `ask` |
| `--liger auto` | 尝试安装并检测 Liger，失败时回退普通训练；默认策略 |
| `--liger off` | 不安装/启用 Liger |
| `--liger required` | 要求 Liger 检查通过，否则停止；不适合尚未确认兼容性的环境 |
| `--cuda-index NAME` | 覆盖 CUDA 软件源后缀，默认 `cu128` |
| `--rocm-index NAME` | 覆盖 Linux ROCm 软件源后缀，默认 `rocm6.4` |
| `--rocm-profile aimax395` | 使用 AMD 官方 ROCm 10.1 / PyTorch 2.14 `gfx1151` 配置；Linux 运行 `start_aimax395.sh`，Windows 运行 `start_aimax395.ps1` |
| `--torch-index-url URL` | 显式指定经过确认的兼容 PyTorch 源；不替代 NPU 专用安装分支 |
| `--cann-installer PATH` | 本地官方 CANN `.run` 安装包，可重复提供，按顺序执行 |
| `--cann-env PATH` | CANN 的 `set_env.sh` 路径 |

修改软件源参数不会主动替换一个已经可用的硬件环境；需要测试其他方案时请使用新的 `--venv`。`--check-only` 不能与 `--cann-installer` 同用。

常用操作：

```powershell
.\start_webui.ps1 --dry-run
.\start_webui.ps1 --no-start
.\start_webui.ps1 --check-only
.\start_webui.ps1 --skip-install --liger off
```

Linux 使用相同参数，将入口替换为 `bash start_webui.sh` 即可。

### 4.4 华为昇腾与 CANN

昇腾分支需要受支持的 Linux 主机。先按官方文档安装匹配的驱动和固件，确认 `npu-smi info` 可以正常执行。

已经安装 CANN 时：

```bash
bash start_webui.sh --backend npu \
  --cann-env /usr/local/Ascend/ascend-toolkit/set_env.sh
```

需要由脚本执行已下载的官方 Toolkit/算子安装包时：

```bash
bash start_webui.sh --backend npu \
  --cann-installer /path/to/official-toolkit.run \
  --cann-installer /path/to/official-ops.run \
  --cann-env /path/to/ascend-toolkit/set_env.sh \
  --no-start
```

上述路径必须替换为真实文件。脚本依次执行 `bash <安装包> --install`，再加载 CANN 环境；不会自动下载安装包、申请提权或修改用户 shell 配置。当前账号应具备所选安装目录需要的权限。

当前 `requirements/npu.txt` 配套版本为 Torch 2.10.0、torch-npu 2.10.0.post2、torchvision 0.25.0、torchaudio 2.10.0。具体 CANN、驱动与芯片组合仍需按官方兼容矩阵选择。

安装了 bitsandbytes 不代表 NPU 量化已经可用。若该构建未提供当前 NPU 后端，检查程序会提示量化不受支持；不要为了装入旧预览包而绕过本项目的版本约束。

## 5. 保留了哪些依赖

依赖版本的最终依据是 [pyproject.toml](pyproject.toml) 和 [requirements](requirements) 中的文件，而不是本文中的安装快照。

| 分组 | 必装内容与用途 |
| --- | --- |
| 训练核心 | torch、torchvision、torchaudio、transformers、datasets、accelerate、peft、trl、torchdata |
| WebUI 与监控 | gradio、matplotlib、tensorboard、tyro |
| 量化与计算 | bitsandbytes、einops、numpy、pandas、scipy |
| 模型与分词 | sentencepiece、tiktoken、modelscope、hf-transfer、safetensors |
| 多媒体与配置 | av、fire、omegaconf、packaging、protobuf、pyyaml、pydantic |
| 保留的底层服务依赖 | uvicorn、fastapi、sse-starlette |
| metrics 文件 | nltk、jieba、rouge-chinese、tensorboard |

其中 bitsandbytes 和 TensorBoard 是公共必装依赖，不会因为选择某个平台而被安装器省略。当前范围分别是 `bitsandbytes>=0.48.0,<=0.50.2` 和 `tensorboard>=2.14.0,<=2.21.0`。

Liger 是可选加速依赖，要求 `liger-kernel>=0.8.0`。DeepSpeed、其他特殊加速功能的依赖不等于公共必装依赖；启用这些功能前，需要按对应 requirements 文件与设备兼容要求另行准备。不要无差别安装 requirements 目录下所有文件，不同后端的依赖可能互相冲突。

### 5.1 环境检查到底检查什么

[scripts/check_training_environment.py](scripts/check_training_environment.py) 会检查：

- 公共依赖和 metrics 包是否能导入，以及 `pip check` 是否通过。
- 所选设备是否实际可用，而非仅安装了一个带相应名称的软件包。
- 小规模张量运算和反向传播是否成功。
- bitsandbytes 声明支持当前设备时，执行小规模 4-bit 线性层前向/反向测试。
- Liger 的可用性及失败原因。

如果 bitsandbytes 不支持当前后端，会明确报告，不将“安装成功”描述成“量化可用”。若它声明支持却在实际测试时出错，环境检查会失败并停止启动。

小规模检查通过不保证某个 8B 或多模态模型能够装入内存，也不替代完整训练验证。

## 6. Liger Kernel 的兼容性策略

Liger 不再是所有平台无条件启用的选项。当前逻辑会检查：

1. 是否安装符合版本要求的 Liger。
2. Torch、Triton 与当前设备后端能否一起工作。
3. 小规模 Liger 运算是否能完成前向/反向传播。
4. 模型类型是否存在对应的 Liger 补丁支持。

不兼容时，WebUI 和 CLI 会回退到普通训练路径并给出原因；显存估算也不会继续假设存在 Liger 带来的节省。检查结果在进程内有缓存，变更依赖后应重启 WebUI。

CUDA 探测会按照设备能力使用 BF16 或 FP16，而不是固定使用与实际训练无关的 FP32；多卡机器会在编译和运行算子前显式设置当前 CUDA 设备。首次 Triton JIT 编译可能耗时超过一分钟，默认探测超时为 300 秒，超时诊断会显示停留的编译阶段。安装器还会将 `TRITON_CACHE_DIR` 默认指向虚拟环境内的 `.triton-cache`，让安装检查、WebUI 和训练复用同一份编译缓存。

Intel XPU 不会仅因品牌而被一概禁用。早期安装器会因 Liger 对通用 `triton` 的依赖与 XPU Triton 提供包名称不同而跳过 Liger；2026-10-06 的 Windows 适配已处理这个依赖声明问题，同时保留硬件运行检查。不是简单删除 `triton===0` 约束。

不要用不受约束的 `pip install --upgrade liger-kernel` 强行覆盖已有 Triton。若手工排查确实需要该命令，至少需要给版本表达式加引号，并先确认厂商后端兼容性；常规使用直接交给启动脚本处理。

可显式禁用：

```powershell
.\start_webui.ps1 --skip-install --liger off
```

禁用 Liger 不会同时关闭 TensorBoard 或 bitsandbytes。FlashAttention 是另一个独立功能，不能因 Liger 检查通过就认为它也可用。

### 6.1 Windows 加速依赖匹配（二次改进）

Windows 的安装由 [scripts/install_windows_liger.py](scripts/install_windows_liger.py) 自动处理：

| 平台 | 当前匹配策略 |
| --- | --- |
| Intel XPU | 保留官方 PyTorch XPU 安装所带的 `triton-xpu` / `pytorch-triton-xpu`；不安装 CUDA 版 Triton |
| NVIDIA CUDA | 根据实际 Torch 版本选择对应小版本范围的 `triton-windows`，同时检查 GPU 架构限制 |
| AMD ROCm | 根据实际 Torch 版本选择 `triton-windows`，实际 Triton target 必须是 `hip`；仍需受支持的 ROCm/GPU 组合 |
| CPU / Windows NPU | 不尝试用 GPU Triton 伪装支持；CPU 使用普通训练，NPU 安装仍要求支持的 Linux 系统 |

例如 Torch 2.9 对应 Triton Windows 3.5 系列，Torch 2.12/2.13 对应 3.7 系列。未知版本不会盲目安装最新 Triton，已有不匹配的提供包也不会被静默覆盖。版本关系来自 [Triton Windows 维护仓库](https://github.com/triton-lang/triton-windows)。Intel 则沿用其 [XPU 后端](https://github.com/intel/intel-xpu-backend-for-triton/blob/main/.github/WINDOWS.md)，不使用 NVIDIA/AMD 的版本选择分支。

Liger 的通用 wheel 将依赖写成 `triton`，pip 不认识 `triton-windows` 等其他发行包提供了同名 Python 模块。为避免 Windows 安装时误拉 Linux Triton，`pyproject.toml` 和 `requirements/liger-kernel.txt` 的通用入口会在 Windows 跳过 Liger，由一键启动脚本调用硬件感知安装器。安装器优先复用当前虚拟环境中与 Torch 匹配的 `triton-windows`；仅在缺失时安装匹配版本。XPU 则保留 PyTorch 配套的 XPU Triton，不能与 `triton-windows` 混装。

安装器下载 PyPI 官方 Liger 0.8.5 wheel，生成带 `+cyrene.xpu1`、`+cyrene.cuda1` 或 `+cyrene.rocm1` 标记的本地适配版本：只把通用 Triton 依赖替换为实际检测到的提供包及精确版本，保留原始算子代码和许可证，并重新生成 wheel 文件校验记录。来源 wheel 的 SHA256、设备和提供包版本记录在安装包的 `cyrene_backend.json` 中。这是本项目的本地打包适配，不是上游另行发布的官方 Windows Liger 版本。

安装仍执行正常依赖解析、`pip check` 和运行探针；不使用虚假的占位 `triton` 包，不用 `--no-deps` 跳过安装时的检查（仅下载原始 wheel 时使用该参数）。重复安装时会验证已有本地版本的依赖与来源记录，匹配就复用。当前只适配已检查的 Liger 0.8.5，不会自动将已有更高版本降级；后续 Liger 发布需审查后更新配置。

更新代码后，在实际项目目录执行一次安装，而不是带 `--skip-install`：

```powershell
.\start_webui.ps1 --backend xpu --venv .venv-xpu --no-start
```

默认环境叫 `.venv` 时请去掉 `--venv .venv-xpu`。验证输出应显示对应 `triton_providers`、Liger 版本和 `enabled: true`；若仍为 false，应根据实际原因排查驱动、编译器、算子或精度，而不是强制启用。之后可使用 `--skip-install` 启动。

如果之前在当前终端设置过 `$env:LLAMAFACTORY_LIGER = "off"`，需要先移除或改为 `"auto"`，否则显式禁用仍然优先生效。

其他依赖不因本次修复被移除：bnb 和 TensorBoard 继续必装，Torch/vision/audio 保留现有可用版本。FlashAttention 的上游 Windows 编译支持仍有限，不作为 Windows 一键必装项；不能把 Liger 的成功等同于所有可选加速库都可用。[bitsandbytes 平台支持](https://huggingface.co/docs/bitsandbytes/installation) · [FlashAttention 安装说明](https://github.com/Dao-AILab/flash-attention#installation-and-features)

## 7. 准备本地模型和数据

### 7.1 模型目录

模型目录需要包含模型架构配置、完整权重、分词器文件；多模态模型还需要对应处理器配置。以下为分片模型的示意结构，实际文件名随模型而异：

```text
model/
  config.json
  tokenizer_config.json
  tokenizer.json 或其他模型对应的分词器文件
  model.safetensors.index.json
  model-00001-of-00002.safetensors
  model-00002-of-00002.safetensors
  多模态模型所需的 processor / preprocessor 配置
```

单文件权重模型不要求具有分片索引。不要遗漏分片，也不要将 LoRA 输出目录当作完整基础模型目录。量化选项表示训练加载时采用的方案，不是自动修复缺失权重或把任意预量化格式转换为 bnb。

模型大小由本地权重文件与 `config.json` 分析得出。尽量保持目录整洁，不要混入无关模型权重和历史备份。

### 7.2 最小 SFT 数据集

首次验证基础流程可使用仓库注册的 `alpaca_zh_demo`。自行准备数据时，例如创建 `data/my_sft.json`：

```json
[
  {
    "instruction": "Explain the purpose of a training checkpoint.",
    "input": "",
    "output": "A checkpoint saves training state so training can be resumed."
  }
]
```

然后在 `data/dataset_info.json` 的现有 JSON 对象内追加注册项，保留其他数据集：

```json
"my_sft": {
  "file_name": "my_sft.json",
  "columns": {
    "prompt": "instruction",
    "query": "input",
    "response": "output"
  }
}
```

第二段只是待追加的对象成员，不是完整 JSON 文件；请注意相邻成员之间的逗号。WebUI 选择的是注册名 `my_sft`，不是文件名。

DPO、KTO、奖励模型和 PPO 等任务有不同的数据要求，不能直接认为任意 SFT 数据都适用。多模态数据还必须包含正确的媒体字段、对话格式，以及训练主机实际可读取的图像/视频路径；可参考项目已有的 `mllm_demo` 注册方式。

## 8. WebUI 四步操作

### 第一步：选择模型与训练目标

1. 选择界面语言，输入本地模型目录，例如 `E:\model`。
2. 选择训练任务。基础指令微调通常选择监督微调（SFT）；继续预训练选择 PT。
3. 选择微调方法。LoRA 训练参数较少；Full 更新全部参数，通常需要显著更多显存。
4. 选择量化。默认不量化；需要 QLoRA 时选择支持的 4-bit 配置。
5. 核对对话模板、可选检查点和加速状态。模板必须与基础模型匹配。

量化训练在当前配置路径中用于 LoRA/OFT 等参数高效微调；Full/Freeze 不应搭配这里的 bnb 量化选项。量化还取决于模型和设备的实际支持情况，不能仅凭下拉框存在就认定可运行。

若希望恢复训练或继续适配器训练，先确认检查点与基础模型、微调方法一致；“读取适配器继续训练”和“完整恢复优化器状态”不是同一个概念。

### 第二步：选择数据

1. 指定数据目录，默认 `data`。
2. 从注册列表中选择训练数据集。
3. 使用数据预览核对字段、内容和媒体路径。

预览主要帮助检查样本格式，不会为整个数据集的所有记录提供完整正确性保证。若选择多个数据集，应确保它们都符合所选任务的数据要求。

### 第三步：按需调整超参数

先使用建议配置，再调整与自己目标有关的参数。推荐值不是锁定值。

| 参数 | 如何理解与调整 |
| --- | --- |
| 序列长度 | 控制单条训练样本的 token 长度；越长通常越耗显存，超长内容可能被截断 |
| 单卡 batch size | 一次前向/反向处理的样本数；显存不足时优先从 1 开始 |
| 梯度累积 | 累积多次小批量后更新；可提高有效批次，但不等于增加单次前向的 batch size |
| 学习率 | 控制更新幅度；应结合微调方法、数据规模和损失曲线调整 |
| 训练周期 | 完整遍历数据的次数；过多可能过拟合 |
| 计算精度 | 根据设备支持选择；不能假定所有 GPU 都适合 bf16 |
| 最大样本数 | 首次跑通时可减少样本，避免直接启动长时间任务 |
| 日志步数 | 决定多久写入训练指标；较小值便于初次观察 |
| 保存步数 | 决定检查点频率；过密会增加磁盘和保存开销 |
| warmup、调度器、梯度裁剪、随机种子 | 用于优化训练稳定性、学习率变化和可重复性 |

通常有效全局批次可理解为：`单设备 batch size × 梯度累积步数 × 数据并行设备数`。这不是峰值显存的计算公式。

界面会按选择展示相关分支：

- LoRA：rank、alpha、dropout，以及适用的扩展选项。
- SFT/PT：适用的数据打包、词表调整等设置。
- DPO/KTO：对应偏好训练的损失和权重设置。
- PPO：奖励模型、PPO 周期、缓冲和 KL 等设置。
- 多模态：是否冻结视觉塔、视觉投影层和语言模型，以及图像/视频像素限制。

多模态模型不仅需要正确的媒体数据，还需要可用的处理器。解冻视觉模块、提高图像分辨率或增加视频内容都可能大幅提高显存占用。

训练内部验证可按任务选择关闭、按百分比从训练集划分或使用独立验证集；默认保留 10%。启用后生成 `eval_strategy: steps`，并自动令 `eval_steps` 等于 `save_steps`，确保每保存一次检查点就验证一次，同时不要求用户重复配置两个间隔。PPO 不展示同样的验证分支。这不等于恢复独立推理或独立评测页面。

### 第四步：检查并开始训练

1. 核对模型、任务、量化、学习参数和最终输出目录。
2. 查看显存估计、建议值和当前可用显存。
3. 如有风险，先降低配置或更换模型；只有理解风险后才确认强行继续。
4. 点击开始训练，查看启动日志、完整错误堆栈和 TensorBoard 链接。

修改关键参数后，需要以新的显存检查结果为准，之前的风险确认不能当作新配置的保证。

训练开始时自动保存最终配置。WebUI 会根据当前表单生成配置，不是任意 YAML 的原样执行器；不要手改历史 YAML 后期待下一次 WebUI 点击开始时自动采用这些改动。需要完整手工控制时，复制并修改保存的配置，通过 CLI 执行。

## 9. 显存估算与 OOM

显存估算不再让用户手填“模型为几 B”，而是读取本地模型配置、权重体积并结合训练设置计算。

主要考虑因素包括微调方法、量化、计算精度、序列长度、单设备 batch size、LoRA 参数、梯度检查点、训练任务、多设备/DeepSpeed 设置、多模态像素及冻结设置，以及实际可用的 Liger 状态。

```text
建议可用显存 = 估计训练显存 × 1.10
```

关键超参数变化时会更新估计，训练前还会再检查。低于估计值或建议余量时不建议直接开始；无法确定设备可用容量时也应谨慎。

10% 是额外建议余量，不是误差上界。估算不能完全覆盖模型临时张量、设备碎片、驱动分配限制、其他进程占用、共享内存机制和实际多模态输入差异。

遇到 OOM 可依次考虑：

1. 单设备 batch size 降到 1，缩短序列长度。
2. 使用 LoRA 和设备实际支持的量化；注意 4-bit 不代表训练所有张量都只有 4-bit。
3. 开启适用的梯度检查点；需要维持有效批次时提高梯度累积。
4. 减少图像/视频像素或冻结更多视觉模块。
5. 减少训练内部验证 batch size，关闭不必要的占用显存的其他程序。
6. 如果仍失败，改用更小模型或更大容量的设备。

Intel 核显可能出现“总空闲容量足够，但单次大块分配失败”。启动器为 XPU 默认设置 `UR_L0_ENABLE_RELAXED_ALLOCATION_LIMITS=1`，但它不会创造额外内存，也不能保证消除 OOM。`empty_cache()` 不能释放仍被活跃张量占用的内存。

## 10. TensorBoard、输出目录与日志

### 10.1 WebUI 自动监控

WebUI 默认使用 TensorBoard。开始训练时会：

1. 确定实际训练输出目录。
2. 将 TensorBoard 的 `logging_dir` 与该输出目录保持一致。
3. 启动该目录对应的 TensorBoard 服务并提供访问链接。
4. 尝试在运行 WebUI 的机器上打开浏览器，然后启动训练。

默认 TensorBoard 地址为 `http://127.0.0.1:6006`。如果端口被占用，会在后续端口中尝试可用端口；以 WebUI 实际显示的链接为准。无桌面的服务器不一定弹出浏览器窗口，这不代表监控没有启动。

TensorBoard 启动失败时会停止本次训练启动并记录错误。训练结束后保留监控服务以便查看曲线；下一次训练会切换到新任务对应目录，已有事件文件不会因此删除。

第一次到达日志记录步数之前，TensorBoard 可能还没有曲线。监控不能在训练尚未完成任何日志记录时凭空显示损失值。

### 10.2 输出文件在哪里

使用简单输出名称，例如 `train_2026-10-04-example`，通常会保存到：

```text
saves/<model_name>/<finetuning_type>/<output_name>/
  training_args.yaml
  llamaboard_config.yaml
  webui_subprocess.log
  tensorboard_server.log
  running_log.txt
  trainer_log.jsonl
  events.out.tfevents.*
  checkpoint-*/
  训练完成后的模型或适配器文件
```

文件是否已生成取决于任务进行到哪个阶段。`training_args.yaml` 是实际训练参数，`webui_subprocess.log` 主要用于查看子进程标准输出、标准错误和完整堆栈。

如果填写绝对输出路径，则以界面显示的最终路径为准。Windows 输出路径建议使用 `E:\training_output\run_name` 这样的本机格式。不要让不同任务共用同一个输出目录。

LoRA 产物通常包含 `adapter_config.json` 和适配器权重；Full 的产物是模型权重，不应按 LoRA 适配器处理。停止任务不保证立即保存一个新的完整检查点，应检查已有文件。

### 10.3 端口与环境变量

| 环境变量 | 用途 / 默认值 |
| --- | --- |
| `PYTHON_BIN` | 指定启动器使用的 Python 解释器 |
| `VENV_DIR` | 默认虚拟环境路径；命令行 `--venv` 可覆盖 |
| `TRAINING_BACKEND` | 默认后端，未设置时为 `auto` |
| `SKIP_INSTALL=1` | 默认跳过依赖安装 |
| `WEBUI_HOST_MODE` | `ask`、`local` 或 `network`；未设置时为 `ask` |
| `WEBUI_HOST` | 显式绑定地址；设置后优先于部署模式选择 |
| `WEBUI_PORT` | 默认 `7860` |
| `GRADIO_SERVER_NAME` / `GRADIO_SERVER_PORT` | 若已设置，会优先于启动器的 WEBUI 默认设置 |
| `TENSORBOARD_HOST` | 未设置时继承 WebUI 的本地/网络部署模式；可单独覆盖监听地址 |
| `TENSORBOARD_PORT` | 默认首选 `6006` |
| `TENSORBOARD_PUBLIC_URL` | 可选的浏览器访问地址，支持 `{port}` 占位符，例如 `https://host/proxy/{port}/` |
| `LLAMAFACTORY_LIGER=off` | 禁用 Liger |
| `LLAMAFACTORY_LIGER_PROBE_TIMEOUT` | Liger 运行探测超时秒数；默认 `300`，最小 `60` |
| `TRITON_CACHE_DIR` | Triton JIT 缓存目录；默认位于虚拟环境的 `.triton-cache` |

例如恢复使用 8788 端口：

```powershell
$env:WEBUI_PORT = "8788"
.\start_webui.ps1 --skip-install
```

```bash
WEBUI_PORT=8788 bash start_webui.sh --skip-install
```

交互终端启动时会先询问访问方式：选择本地模式后 WebUI 和训练时启动的 TensorBoard 都绑定 `127.0.0.1`，选择网络/Jupyter 模式后两者都绑定 `0.0.0.0`。Notebook 单元或其他非交互环境为安全起见默认本地模式，应显式添加 `--host-mode network`。JupyterHub 环境会根据 `JUPYTERHUB_SERVICE_PREFIX` 生成看板代理链接；其他代理可设置 `TENSORBOARD_PUBLIC_URL`。远程服务器上的 `127.0.0.1` 指服务器自身，不是你的客户端电脑。可通过 Jupyter 端口代理或 SSH 转发访问；不要为了方便而无保护地暴露训练服务到公网。启动器在运行 WebUI 前会替换自身进程，因此 `Ctrl+C` 会直接发送给 WebUI。

## 11. 合并 LoRA 适配器

当前 WebUI 合并流程针对 LoRA，不是所有微调方法的通用模型转换器。

1. 在模型设置中指定对应的完整基础模型目录和模板。
2. 打开适配器合并区域，使用该区域的检查点选择器选择已训练的 LoRA 适配器。
3. 选择独立的导出目录，不要覆盖基础模型或训练检查点。
4. 按内存条件选择导出设备。默认 CPU；大模型合并仍然可能消耗大量系统内存。
5. 根据需要设置分片大小和保存格式，然后开始导出。

QLoRA 训练得到的适配器在合并时应使用对应的未量化基础模型。不要直接将一个不兼容的预量化模型当作可合并底座。

Full 训练已经生成模型权重，通常不需要 LoRA 合并。当前界面不执行 Hub 上传，也不在合并时重新量化。

## 12. 命令行操作

CLI 保留训练、导出合并、WebUI 和环境信息等入口。常用命令是 `train`、`export`、`webui`、`env`、`version`、`help`；也可使用安装后生成的 `llamafactory-cli`。

为避免调用到其他 Python 环境，以下使用项目虚拟环境中的解释器。自定义了 `--venv` 时请同步替换路径。

Windows：

```powershell
.\.venv\Scripts\python.exe -X utf8 -m llamafactory.cli help
.\.venv\Scripts\python.exe -X utf8 -m llamafactory.cli env
.\.venv\Scripts\python.exe -X utf8 -m llamafactory.cli train "E:\training_output\run_name\training_args.yaml"
```

Linux：

```bash
.venv/bin/python -X utf8 -m llamafactory.cli help
.venv/bin/python -X utf8 -m llamafactory.cli env
.venv/bin/python -X utf8 -m llamafactory.cli train /path/to/training_args.yaml
```

训练配置路径需要替换为真实存在的文件。建议先用 WebUI 生成一份有效配置，复制后再调整输出目录、超参数等，以保留原任务记录。CLI 不会显示 WebUI 的显存风险确认窗口。

导出使用 `export <export_config.yaml>`，需要准备符合导出参数要求的独立配置；不能直接把训练 YAML 当作通用导出配置。

### 12.1 CLI 下的 TensorBoard

CLI 训练不会自动启动 TensorBoard 服务。配置中应包含合适的监控设置，例如：

```yaml
report_to: tensorboard
output_dir: saves/manual_run
logging_dir: saves/manual_run
logging_steps: 1
```

然后在另一个终端手动启动监控：

```powershell
.\.venv\Scripts\python.exe -m tensorboard.main --logdir "saves/manual_run" --host 127.0.0.1 --port 6006
```

```bash
.venv/bin/python -m tensorboard.main --logdir saves/manual_run --host 127.0.0.1 --port 6006
```

直接调用 CLI 也不会执行整个安装器的环境准备流程。NPU 需先加载 CANN 环境；XPU 如需使用前述分配限制设置，应在启动进程前设置对应环境变量。

## 13. 常见问题

| 现象 | 排查方法 |
| --- | --- |
| 回环地址拒绝连接 | 查看启动终端是否仍在运行，确认实际端口是 7860 还是 8788，以及安装检查是否已失败退出 |
| 一直停留在安装阶段 | 查看终端最后一条 pip 操作；首次 Torch 下载可能很大，不要并行对同一个环境重复安装 |
| 提示已有环境后端不一致 | 保留原环境，用新的 `--venv` 安装目标后端；不要手工混装 CPU/CUDA/XPU 包 |
| Liger 解析失败或被禁用 | 默认策略下可使用普通训练；查看失败原因，不要强行覆盖厂商 Triton |
| bnb 已安装但不能量化 | 运行 `--check-only`，区分包导入成功与当前设备量化内核真正可用 |
| 缺少 jieba、nltk 或 rouge_chinese | 不带 `--skip-install` 重新执行安装器，确认 metrics 安装成功 |
| 缺少编译器或 JIT 编译失败 | 检查 MSVC / Linux 编译工具链及设备库要求；安装 Python 包不等于安装了 C/C++ 编译器 |
| 中文日志乱码或编码异常 | 使用启动脚本，或指定 `python -X utf8`；脚本会设置 `PYTHONUTF8=1` |
| 显示显存够用却 OOM | 估算不是保证；检查单次分配、序列长度、batch size、多模态输入和设备共享内存限制 |
| TensorBoard 没有曲线 | 确认 logdir 与实际输出目录一致、已有事件文件且达到日志步数，再看服务日志 |
| 点击开始没有进入训练 | 检查模型/数据必填项、显存风险确认、TensorBoard 启动情况，以及子进程日志 |
| 安装后界面仍显示旧行为 | 停止旧 WebUI 后重新启动；已有 Python 进程不会自动重载全部依赖和兼容性缓存 |

只检查当前默认环境：

```powershell
.\start_webui.ps1 --check-only
.\.venv\Scripts\python.exe -m pip check
```

排障时请保留完整堆栈，尤其是 `webui_subprocess.log` 中第一处实际失败的位置，不要只截取最后一行通用错误。分享日志前先删除令牌、私有数据和其他敏感信息。

## 14. 安装产物与代码合并

依赖主要安装到所选虚拟环境，不写入项目的 Python 源码目录。可编辑安装会让虚拟环境引用当前源码，因此修改源码后应按需要重启服务。

- `.venv/` 与 `.venv-*/` 已配置忽略；自定义为其他名字的环境需要自行确认忽略规则。
- 临时硬件约束文件在安装结束后清理；pip 下载缓存可能保留在系统缓存目录。
- 模型、训练输出、TensorBoard 事件、下载的 wheel 和日志不应当作功能源码提交。
- 当前工作区的 `logs/` 可能包含人工留下的日志或大文件；提交前必须检查，不能假定都已被忽略。
- 需要合并的是安装脚本、依赖声明、兼容性代码、测试和文档，不需要上传整个虚拟环境。

提交前可检查：

```bash
git status --short
git diff --check
```

避免未经检查直接将所有未跟踪文件加入提交。该安装流程不会自动提交或推送 Git 仓库。

## 15. 已验证范围与限制

截至 2026-10-04，前一次安装验证已在本机 Windows / Intel Arc 130T XPU 上完成：

| 项目 | 当时结果 |
| --- | --- |
| Python | 3.12.14 |
| Torch | 2.13.0+xpu，保留已有运行环境 |
| XPU Triton | triton-xpu 3.7.2 |
| bitsandbytes | 0.50.2，小规模 4-bit 前向/反向检查通过 |
| TensorBoard | 2.21.0，可导入 |
| metrics | nltk、jieba、rouge-chinese 已安装 |
| 依赖一致性 | `pip check` 通过 |
| Liger | 当前组合不兼容，跳过安装并禁用 |
| 自动化回归 | 相关安装器、兼容性与 WebUI 测试共 83 项通过 |

这是当时环境的验证记录，不是本次文档编写时重新安装或重新训练的结果。CUDA、ROCm、NPU 分支尚未在对应实机上完成同等验证；安装方案和单元测试通过不应表述为所有厂商设备均已训练成功。

2026-10-06 补充验证：在本工作区 `.venv` 中安装 `liger-kernel 0.8.4+cyrene.xpu1`，保留 Torch 2.13.0+xpu 和 triton-xpu 3.7.2；`pip check`、bnb 4-bit 检查通过，Liger FP32/BF16 RMSNorm 与融合线性交叉熵前向/反向通过。另用随机初始化的微型 Llama 模型完成 BF16 + Liger + LoRA 的损失、反向传播和优化器更新检查，无模型下载、无用户数据读取。安装与 WebUI 回归测试 128 项通过，加上该实机测试共 129 项。此记录更新了上表中旧的 Liger 禁用结论，但不代表完整 8B 模型训练或 NVIDIA/AMD 实机已验证。

开发者可选执行上述小模型测试（默认不会随普通测试启动 GPU 训练）：

```powershell
$env:RUN_WINDOWS_LIGER_SMOKE = "1"
.\.venv\Scripts\python.exe -X utf8 -m pytest tests/test_windows_liger_runtime.py -q
```

## 16. 维护入口与参考资料

本地维护入口：

- [安装器](scripts/bootstrap_webui.py)：设备选择、安装顺序和硬件约束。
- [环境检查](scripts/check_training_environment.py)：导入、设备和量化运行检查。
- [公共依赖](pyproject.toml)、[metrics 依赖](requirements/metrics.txt)、[NPU 依赖](requirements/npu.txt)、[Liger 依赖](requirements/liger-kernel.txt)。
- [Liger 兼容性检查](src/llamafactory/extras/liger.py)、[设备环境准备](src/llamafactory/extras/accelerator.py)。
- [训练与监控调度](src/llamafactory/webui/runner.py)。
- [专项依赖说明](docs/DEPENDENCY_INSTALLATION.md)、[已有 WebUI 说明](docs/CYRENE_YIELD_WEBUI.md)。旧文档如有“固定启用 Liger”等历史描述，应以当前代码及本文的兼容性策略为准。

官方参考资料：

- [LLaMAFactory 安装文档](https://llamafactory.readthedocs.io/en/latest/getting_started/installation.html)
- [LLaMAFactory 昇腾安装文档](https://llamafactory.readthedocs.io/en/latest/multibackend/npu/npu_installation.html)
- [PyTorch 安装选择器](https://pytorch.org/get-started/locally/)
- [bitsandbytes 安装与平台支持](https://huggingface.co/docs/bitsandbytes/installation)
- [Liger Kernel 官方安装说明](https://github.com/linkedin/Liger-Kernel#installation)
- [AMD Windows ROCm 7.2.1 软件包目录](https://repo.radeon.com/rocm/windows/rocm-rel-7.2.1/)

升级硬件依赖时，应同时核对厂商支持范围、项目版本约束和运行检查结果，不要单独把某一个包升级到最新版后就视为整套环境已经兼容。
