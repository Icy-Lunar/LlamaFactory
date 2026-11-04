# 按设备安装训练依赖

安装器保留 `pyproject.toml` 中的公共训练依赖和 `requirements/metrics.txt`。bitsandbytes、TensorBoard 均为必装项；Liger Kernel 是唯一在本次调整中改为按兼容性安装、启用的加速依赖，原有 `requirements/liger-kernel.txt` 仍保留。

## 一键安装与启动

Windows PowerShell：

```powershell
./start_webui.ps1
```

Linux / Git Bash：

```bash
bash start_webui.sh
```

也可直接使用 Python 3.11 及以上（建议 3.12）：

```bash
python scripts/bootstrap_webui.py
```

安装器检测实际 GPU/NPU，而非 CPU 厂商。多设备机器优先复用已有可用后端；新环境按 CUDA、NPU、XPU、ROCm 顺序选择，并输出选择结果。未识别到加速器才选择 CPU；检测到加速器但验证失败会报错，不会静默转成 CPU。

## 支持的安装分支

| 后端 | 新环境安装方案 | 系统前提 |
| --- | --- | --- |
| Intel XPU | 官方 XPU 源：torch 2.13.0、torchvision 0.28.0、torchaudio 2.11.0；由 wheel 安装 SYCL/Triton 依赖 | 受支持的 Intel GPU、驱动；Windows 编译算子需要 MSVC Build Tools |
| NVIDIA CUDA | 官方 cu128 源中的配套 torch / torchvision / torchaudio | 兼容的 NVIDIA GPU 和驱动；可用 `--cuda-index` 改选官方构建 |
| AMD ROCm / Linux | 通用设备使用 PyTorch ROCm 索引；Ryzen AI Max+ 395 专用入口使用 AMD 官方 ROCm 10.1 / PyTorch 2.14 `gfx1151` 设备包 | 裸机 Linux 需要规定的 KFD 内核修复；WSL2 使用 `/dev/dxg`，驱动必须安装在 Windows 主机 |
| AMD ROCm / Windows | 通用旧配置保留 ROCm 7.2.1；Ryzen AI Max+ 395 专用入口使用 AMD 官方 ROCm 10.1 / PyTorch 2.14、`gfx1151` 设备库与开发组件 | Windows 11 x64、兼容 AMD 驱动；专用入口使用独立虚拟环境并强制验证反向传播 |
| 昇腾 NPU | 先安装 CPU 版 PyTorch 三件套，再安装项目 `requirements/npu.txt`；Liger 按需检查 `requirements/triton_ascend.txt` | Linux、HDK 驱动/固件、配套 CANN Toolkit 和算子包 |
| CPU | 官方 CPU 源中的配套 PyTorch | Windows / Linux |

这些是安装配置，不代表本项目已经在全部设备上完成实机测试。已有环境优先保留其硬件包版本，通过临时 constraints 防止后续 pip 安装替换 PyTorch 或覆盖另一种 Triton。发现不同后端的已有环境会停止，并提示用 `--venv` 指定独立环境。

## 常用参数

```bash
# 只显示检测结果和安装计划，不安装、不启动
bash start_webui.sh --dry-run

# 指定设备和独立虚拟环境
bash start_webui.sh --backend cuda --venv .venv-cuda
bash start_webui.sh --backend xpu --venv .venv-xpu
bash start_webui.sh --backend rocm --venv .venv-rocm

# 仅安装和校验；或仅校验现有环境
bash start_webui.sh --no-start
bash start_webui.sh --check-only

# 复用已安装环境，校验后启动
bash start_webui.sh --skip-install

# 不询问，直接选择本机访问或 Jupyter/LAN 访问
bash start_webui.sh --skip-install --host-mode local
bash start_webui.sh --skip-install --host-mode network

# 关闭 Liger；或要求必须通过 Liger 检查，否则停止
bash start_webui.sh --liger off
bash start_webui.sh --liger required

# Ryzen AI Max+ 395 / Radeon 8060S（gfx1151）
bash start_aimax395.sh --host-mode network
```

在 WSL2 中同样使用 `start_aimax395.sh`。启动器会自动选择 `.venv-aimax395-wsl`，不要求 `/dev/kfd`，并安装 `rocm[libraries,device-gfx1151]`。不要在 WSL 内安装 Linux `amdgpu-dkms`；Windows 驱动更新后先在 Windows PowerShell 运行 `wsl --shutdown`。系统路径中的旧版 `rocminfo` 不能代替新虚拟环境的 PyTorch 反向传播校验。

PowerShell 使用同样的参数，例如 `./start_webui.ps1 --dry-run`。

保留 `PYTHON_BIN`、`VENV_DIR`、`SKIP_INSTALL`、`WEBUI_HOST`、`WEBUI_PORT` 环境变量；另支持 `TRAINING_BACKEND` 与 `WEBUI_HOST_MODE`。未显式指定地址时，交互启动会询问本机访问（`127.0.0.1`）或 Jupyter/LAN 访问（`0.0.0.0`）；TensorBoard 默认继承同一监听模式。JupyterHub 会自动生成端口代理链接，其他部署可用 `TENSORBOARD_HOST` 和 `TENSORBOARD_PUBLIC_URL` 覆盖监听与浏览器地址。非交互启动默认本机访问，可用 `--host-mode network` 覆盖。Windows 和 WSL 不共用同一个虚拟环境，可分别指定 `.venv-windows`、`.venv-linux`。平台虚拟环境目录已加入 Git 忽略规则。

## 昇腾 CANN

驱动/固件与 CANN 需匹配实际硬件及系统，普通 pip 无法安装这些系统组件。已有 CANN 时，安装器加载其 `set_env.sh`。也可提供已下载的官方 Toolkit、ops 安装包，按给定顺序执行安装：

```bash
bash start_webui.sh --backend npu \
  --cann-installer /path/to/Ascend-cann-toolkit.run \
  --cann-installer /path/to/Ascend-cann-ops.run \
  --cann-env /usr/local/Ascend/ascend-toolkit/set_env.sh
```

按 CANN 安装包要求使用具有相应目录权限的账户；脚本不会自动提权、覆盖驱动或重启系统。默认项目 NPU 版本由 `requirements/npu.txt` 决定，应与 LlamaFactory 官方 NPU 文档核对。CANN 不匹配会在设备校验时报告错误。

bitsandbytes 安装成功不等于昇腾 QLoRA 可用。官方 LlamaFactory README 的 NPU 量化方案涉及专用后端构建及关闭双重量化。校验器分别报告“包已安装”和“当前设备的 4-bit 前向/反向可用”；若安装的 bnb 不包含该设备后端，会明确提示，不宣称量化已经验证通过。请勿为迁就旧版 NPU bnb 而绕过本项目版本要求。

## Liger 与校验

默认 `--liger auto`。安装器先预演 Liger 依赖解析；如果需要替换当前硬件后端或无法取得兼容包，就跳过该可选加速依赖。CUDA Triton 与 XPU/ROCm/Ascend 的 Triton 提供者不能随意混装。

2026-11-04 Windows 更新：通用依赖入口在 Windows 上不再安装 Liger，避免上游元数据把 Linux 发行包 `triton` 拉入 Windows 环境；Windows 始终交给硬件感知安装器处理。安装器先检查当前虚拟环境：已有且与 Torch 版本匹配的 `triton-windows` 会直接复用，不重新安装；Intel XPU 保留官方 Torch 配套的 `triton-xpu`/`pytorch-triton-xpu`；只有 NVIDIA/AMD 环境缺少提供者时，才按 Torch 小版本安装相应范围的 `triton-windows`。发现多个共享 `triton` 命名空间的提供者时会停止并报告冲突，不会猜测或覆盖。

安装器从 PyPI 下载已审查的 Liger 0.8.5，生成带 `+cyrene.<backend>1` 标记的本地 wheel，仅将通用 `triton` 依赖替换为实际检测到的 Windows 提供包及精确版本，保留算子代码、许可证和来源校验记录，然后执行正常依赖解析及真实运行检查。不使用虚假占位包，不覆盖其他 Triton 提供者，不自动降级 Torch。重复安装会复用匹配的本地适配版本。

具体平台限制、升级命令及本地 wheel 的说明见 [完整指南第 6 节](../PROJECT_INSTALLATION_AND_USAGE.md)。本机 XPU 已验证 Liger FP32/BF16 前向/反向通过；CUDA/ROCm 的安装匹配有单元测试，但尚无相应实机验证。bnb 与 TensorBoard 必装策略不变，FlashAttention 不作为 Windows 一键必装项。

运行时在隔离子进程内检查 Liger >=0.8.0、实际 Triton 驱动，以及小规模 RMSNorm、融合线性交叉熵的前向/反向。CUDA 会使用设备支持的 BF16 或 FP16 探测，并在探测前显式切换到张量所在设备，避免多卡环境中 Triton 编译或启动到错误设备。首次 Triton JIT 编译可能明显超过一分钟，因此默认超时调整为 300 秒，且阶段信息会保留在错误详情中。结果按精度缓存；设备、依赖、算子或模型适配检查失败时，WebUI 和 CLI 自动使用标准训练。WebUI 的五种语言均显示对应原因，显存估算不会继续套用 Liger 节省系数。非 PT/SFT 任务保守地不计入融合损失的显存节省。

安装器将编译产物持久化在虚拟环境的 `.triton-cache` 中，安装检查和后续 WebUI/训练共用缓存，避免每次启动都从头编译。可用 `TRITON_CACHE_DIR` 修改缓存目录，用 `LLAMAFACTORY_LIGER_PROBE_TIMEOUT` 修改探测超时（单位为秒，最小 60，默认 300）。

安装结束还会执行 `pip check`，导入监控和指标包，验证设备反向传播，以及支持的 bitsandbytes 4-bit 反向传播。首次运行可能编译少量算子；这些检查不会下载模型或启动真实训练任务。基础算子检查不能替代目标模型的完整训练验证。

## 官方参考

- [LlamaFactory 安装文档](https://llamafactory.readthedocs.io/en/latest/getting_started/installation.html)
- [LlamaFactory NPU 安装文档](https://llamafactory.readthedocs.io/en/latest/multibackend/npu/npu_installation.html)
- [LlamaFactory 官方 README](https://github.com/hiyouga/LlamaFactory/blob/main/README.md)
- [Liger Kernel 官方安装与后端要求](https://github.com/linkedin/Liger-Kernel#installation)
- [Liger 0.8.0 后端依赖选择源码](https://github.com/linkedin/Liger-Kernel/blob/v0.8.0/setup.py)
- [Triton Windows 支持与 Torch 版本匹配](https://github.com/triton-lang/triton-windows)
- [Intel Triton Windows 支持](https://github.com/intel/intel-xpu-backend-for-triton/blob/main/.github/WINDOWS.md)
- [bitsandbytes 安装与设备支持](https://huggingface.co/docs/bitsandbytes/installation)
- [AMD Windows ROCm 7.2.1 官方 wheel](https://repo.radeon.com/rocm/windows/rocm-rel-7.2.1/)
- [AMD Windows 支持矩阵](https://rocm.docs.amd.com/projects/radeon-ryzen/en/latest/docs/compatibility/compatibilityrad/windows/windows_compatibility.html)
