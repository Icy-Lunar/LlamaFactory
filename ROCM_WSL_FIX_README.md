# ROCm/WSL 训练稳定性修复说明

本文说明 Ryzen AI Max+ 395 等 AMD 设备在 WSL2 中出现“只启动 TensorBoard、不加载模型”或训练子进程以 `Exit code: -11` 退出时，本项目采用的修复、使用方式和日志定位流程。

## 1. 修复目标

故障日志显示训练进程可能在两个位置退出：

1. Python 导入阶段，即 `runtime_import`；
2. Transformers 将分片权重实体化并复制到 ROCm 设备的阶段，即 `weights`。

`-11` 是 Linux 子进程收到 `SIGSEGV` 后的返回值。它表示原生运行时发生段错误，不是普通 Python 异常，因此通常没有 `Traceback`。

本次修复遵循以下边界：

- 仅修改 **ROCm + WSL** 的保守运行策略；
- CUDA、Intel XPU、Windows 原生 ROCm 和 Linux 原生 ROCm 保持原有加载策略；
- 不回退到 CPU，也不把设备初始化失败伪装成可训练；
- TensorBoard 仍是可选监控进程，它启动失败不会阻止训练进程；
- 用户仍可使用 Liger，但定位原生崩溃时应先关闭 Liger，确认基础训练后再启用。

## 2. 零基础启动

### 2.1 在 Windows PowerShell 重启 WSL

驱动刚升级、ROCm 设备失联或出现原生段错误后，先运行：

```powershell
wsl --shutdown
wsl
```

### 2.2 在 WSL 中一键启动

```bash
cd /mnt/d/trainer

bash start_webui.sh \
  --backend rocm \
  --venv .venv-aimax395-wsl \
  --rocm-profile aimax395 \
  --host-mode network \
  --liger off
```

第一次排障使用 `--liger off`。基础训练成功后，可以改成 `--liger auto` 再测试。

启动 WebUI 后选择本地模型目录、数据集和训练参数，然后点击“开始训练”。无需手工设置 `HF_DEACTIVATE_ASYNC_LOAD`，WebUI 会在确认当前进程确实是 ROCm/WSL 后自动设置。

## 3. 路径建议

`/mnt/c`、`/mnt/d` 等目录通过 WSL 挂载 Windows 文件系统。项目允许继续使用这些路径，但 WebUI 会显示风险提示。

训练稳定性优先时，建议把项目、虚拟环境、模型和输出放在 WSL 的 Linux 文件系统：

```bash
mkdir -p "$HOME/trainer" "$HOME/models" "$HOME/outputs" "$HOME/.venvs"

rsync -a --exclude '.venv*' /mnt/d/trainer/ "$HOME/trainer/"
rsync -a --info=progress2 /mnt/d/Qwen35-9B/ "$HOME/models/Qwen35-9B/"

cd "$HOME/trainer"
bash start_webui.sh \
  --backend rocm \
  --venv "$HOME/.venvs/trainer-aimax395" \
  --rocm-profile aimax395 \
  --host-mode network \
  --liger off
```

不要直接复制旧虚拟环境。虚拟环境中的解释器路径和脚本入口可能仍指向原目录，应让启动器在新位置重新创建。

## 4. 代码修改详解

### 4.1 ROCm/WSL 环境识别

文件：`src/llamafactory/extras/diagnostics.py`

`is_rocm_wsl()` 同时检查：

- 当前 PyTorch 是否带有 HIP/ROCm 构建信息；
- Linux 内核名称是否包含 `microsoft`，或是否存在 `WSL_INTEROP`。

因此 CUDA on WSL 不会被误判为 ROCm/WSL。

### 4.2 串行加载模型权重

同一文件中的 `configure_rocm_wsl_environment()` 设置：

```text
HF_DEACTIVATE_ASYNC_LOAD=1
TOKENIZERS_PARALLELISM=false
OMP_NUM_THREADS=1
MKL_NUM_THREADS=1
```

关键项是 `HF_DEACTIVATE_ASYNC_LOAD=1`。Transformers 5 默认可以使用线程池并行实体化权重；在 ROCm/WSL 中，多线程同时进行主机到设备的权重复制可能以原生段错误结束。关闭异步加载会降低一部分模型加载速度，但不改变训练计算、模型精度或训练数据。

该保护同时在两处应用：

- `src/llamafactory/webui/runner.py`：在 WebUI 创建训练子进程前写入子进程环境；
- `src/llamafactory/train/tuner.py`：保护直接执行 CLI 训练的用户。

### 4.3 数据和 PyTorch 线程保护

`src/llamafactory/train/tuner.py` 在 ROCm/WSL 中继续强制：

```text
preprocessing_num_workers=1
dataloader_num_workers=0
dataloader_pin_memory=false
```

并执行一个最小张量计算和同步，用于在解析数据和加载大模型前确认设备真正可用。验证失败会立即报错，不会回退到 CPU。

### 4.4 独立原生故障日志

`faulthandler` 的周期线程栈和原生崩溃信息现在写入：

```text
<训练输出目录>/native_fault.log
```

正常训练输出仍写入：

```text
<训练输出目录>/webui_subprocess.log
```

这样可以避免 120 秒线程栈把权重加载进度切断，也能在 `SIGSEGV` 没有 Python 异常时保留最后的线程位置。每次新训练开始前，旧日志会重命名为带时间戳的 `.previous` 文件，不会被直接覆盖。

### 4.5 WebUI 错误解释

`src/llamafactory/webui/runner.py` 会把负返回码转换成操作系统信号名称。例如：

```text
Exit code: -11
SIGSEGV (11)
```

提示文字通过 `src/llamafactory/webui/runtime_locales.py` 获取，支持英语、简体中文、日语、韩语和俄语。业务逻辑没有直接写死中文。

### 4.6 `/mnt/*` 风险提示

当虚拟环境、模型或输出目录位于 `/mnt/<盘符>` 时，WebUI 会显示本地化提示，并在 `webui_subprocess.log` 中记录具体路径。提示不会强制终止训练，因为某些用户必须读取 Windows 盘中的大模型。

### 4.7 避免重复 Liger 探测

一键启动器在启动 WebUI 前已经执行过一次真实 Liger 前向/反向探测。探测结果现在通过进程环境传递给 WebUI，并且仅在训练精度与预检精度一致时复用。这样开始训练时不会再次等待 Triton 首次编译；如果用户随后更换 FP32、FP16 或 BF16 精度，系统仍会为新精度重新验证，避免错误复用。

### 4.8 本地数据集不再发送下载计数请求

训练子进程默认设置 `HF_UPDATE_DOWNLOAD_COUNTS=0`、`HF_HUB_DISABLE_TELEMETRY=1` 和 `DO_NOT_TRACK=1`，防止本地 JSON/JSONL 数据集初始化时等待无关的网络统计请求。该设置不会启用 Hugging Face 离线模式，因此用户明确配置的 Hub 数据集仍然可以访问；显式设置的管理员环境变量也不会被覆盖。

## 5. 日志怎么看

按以下顺序检查：

1. `runtime_state.json`：当前最近阶段；
2. `lifecycle.jsonl`：阶段和心跳的时间线；
3. `webui_subprocess.log`：Python、Transformers、数据集和训练输出；
4. `native_fault.log`：定时线程栈、段错误和其他原生故障；
5. `tensorboard_manual.log`：仅在手动启动 TensorBoard 时存在。

常见阶段：

| 阶段 | 含义 |
| --- | --- |
| `runtime_import` | 导入 Python 和训练依赖 |
| `device_check` | 执行 ROCm 最小张量测试 |
| `arguments` | 解析训练配置 |
| `tokenizer` | 加载分词器或多模态处理器 |
| `preprocessing` | 读取并预处理数据集 |
| `weights` | 读取并放置模型权重 |
| `model_ready` | 模型已完成加载 |
| `training` | 已进入训练循环 |
| `evaluation` | 正在验证 |
| `checkpoint` | 已保存检查点 |

`native_fault.log` 中出现 `Timeout (0:02:00)!` 只表示两分钟没有切换训练阶段，程序正在记录线程栈；它本身不会杀死进程。WebUI 的启动看门狗只会在早期导入、设备检查或参数解析停滞超过 600 秒后终止子进程。

如果线程栈停在 `get_liger_status` 的 `subprocess.run`，表示正在进行 Liger/Triton 内核探测；新版一键启动会复用预检结果。如果线程栈停在 `datasets.load.increase_load_count`、`getaddrinfo` 或 `connect_tcp`，表示旧版本正在发送数据集下载计数请求；新版默认关闭该非必要请求。

## 6. 再次发生 `-11` 时

先收集内核日志：

```bash
sudo dmesg -T \
  | grep -Ei 'segfault|amdgpu|kfd|dxg|oom|out of memory' \
  | tail -n 100
```

再执行最小 ROCm 测试：

```bash
.venv-aimax395-wsl/bin/python -X faulthandler - <<'PY'
import torch

print("torch:", torch.__version__)
print("hip:", torch.version.hip)
print("available:", torch.cuda.is_available())
print("device:", torch.cuda.get_device_name(0))
x = torch.ones(1024, device="cuda", requires_grad=True)
(x.square().sum()).backward()
torch.cuda.synchronize()
print("forward/backward: ok")
PY
```

提交故障时请附上：

- `training_args.yaml`，删除令牌和私密路径后再提供；
- `webui_subprocess.log`；
- `native_fault.log`；
- `lifecycle.jsonl`；
- 上述 `dmesg` 末尾输出；
- Windows AMD 驱动版本、WSL 内核版本和 PyTorch/ROCm 版本。

## 7. 验证范围

自动化测试覆盖：

- 仅 ROCm/WSL 设置串行权重加载环境变量；
- CUDA、XPU 和非 WSL 环境不改变相关变量；
- `/mnt/<盘符>` 路径检测；
- `-11` 到 `SIGSEGV` 的本地化解释；
- 原生故障写入独立文件；
- WebUI 训练子进程收到安全环境变量；
- 所有运行时语言包包含相同键集合。

自动化测试不能替代目标设备实测。最终仍需在 Ryzen AI Max+ 395 的 WSL2/ROCm 环境完成至少一次模型加载、一个训练步、一次验证和一次检查点保存。
