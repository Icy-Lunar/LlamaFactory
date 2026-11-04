# Cyrene Yield 零基础完整使用手册

> 适用范围：本项目的 CUDA、Intel XPU、AMD ROCm 统一部署版。
> 目标：即使从未使用过 Python、命令行或大模型训练，也能照着本文完成安装、第一次 LoRA 训练、TensorBoard 监控和适配器合并。

## 0. 先记住这四件事

1. 本项目不会替你下载模型。开始前必须准备一个完整的本地模型目录。
2. 第一次训练先选择 **SFT + LoRA**，不要直接选择 Full。
3. Windows 双击 `start_multibackend.cmd`；Ubuntu 执行 `bash start_wizard.sh`，然后按数字选择。
4. 启动终端必须保持打开。关闭终端会停止 WebUI，训练也可能随之停止。

如果只想尽快跑通，请依次阅读：

```text
第 1 节：认识名词
第 2 节：准备文件
第 3 节：启动
第 5 节：准备模型
第 6 节：准备数据
第 7 节：完成第一次训练
第 9 节：查看 TensorBoard
```

## 1. 用最简单的话理解这些名词

| 名词 | 零基础解释 |
| --- | --- |
| 基础模型 | 训练开始前已有的完整模型，例如一个本地 Qwen、Llama 或其他模型目录。 |
| 微调 | 在基础模型上继续训练，让它更适合你的数据和任务。 |
| LoRA | 只训练少量新增参数。速度快、占用小，最适合第一次使用。 |
| Full | 更新整个模型。通常需要更多显存、时间和磁盘。 |
| SFT | 监督微调。用“问题—答案”样本教模型回答，是最常用的第一种训练。 |
| batch size | GPU 一次处理多少条样本。越大越容易显存不足。 |
| 序列长度 | 每条样本最多保留多少 token。越长越耗显存。 |
| 梯度累积 | 多处理几次小批量后再更新模型。可以在低显存下模拟更大批次。 |
| epoch | 完整看一遍训练数据称为 1 个 epoch。 |
| checkpoint | 训练过程中的阶段性存档。可以用于恢复训练或选择最佳结果。 |
| 验证集 | 不用于更新模型，只用于观察模型是否开始过拟合的数据。 |
| TensorBoard | 在浏览器里显示损失、学习率和训练进度的监控看板。 |
| CUDA | NVIDIA GPU 使用的训练后端。 |
| XPU | Intel GPU 使用的训练后端。 |
| ROCm | AMD GPU/APU 使用的训练后端。 |
| WebUI | 浏览器中的图形操作界面。 |

## 2. 开始前需要准备什么

### 2.1 硬件与系统

需要以下三类设备之一：

- NVIDIA GPU：使用 CUDA。
- Intel Arc、Intel 数据中心 GPU 或受支持的 Intel 核显：使用 XPU。
- AMD Radeon、Instinct 或受支持的 Ryzen APU：使用 ROCm。

统一安装器支持 Windows 和 Linux。Linux 自动安装系统驱动的路径当前限定为受支持的 Ubuntu 版本。

### 2.2 磁盘空间

建议至少预留：

- 环境与依赖：20–40 GB。
- 基础模型：至少等于模型权重大小。
- 训练输出：LoRA 通常较小；Full 可能接近或超过基础模型大小。
- 检查点：保存次数越多，占用越大。

不要把模型、输出目录和临时环境都放在剩余空间很少的系统盘。

### 2.3 Python

推荐安装 64 位 Python 3.12。Windows 安装 Python 时建议勾选：

```text
Add Python to PATH
Install launcher for all users
```

检查 Python：

```powershell
py -3.12 --version
```

Ubuntu：

```bash
python3 --version
```

### 2.4 你必须已有模型

本项目只读取本地模型，不提供模型下载功能。请通过组织批准的来源准备模型，并确认许可证允许你的使用方式。

## 3. 解压和第一次启动

### 3.1 Windows：直接双击

1. 解压部署包。
2. 打开解压后的目录。
3. 双击：

```text
start_multibackend.cmd
```

4. Windows 弹出“是否允许此应用更改你的设备”时，选择“是”。
5. 在彩色终端中选择语言；之后每一页输入选项前面的数字并按 Enter。
6. 最后一页确认摘要后才会真正安装。安装期间保持终端窗口打开。

向导会依次询问：

```text
语言
→ 检测到多种显卡时选择训练后端
→ 保留、安装或跳过系统驱动
→ WebUI 仅本机访问或允许远程访问
→ 兼容优先、标准训练或全部能力严格检查
→ 安装并启动、只安装、或只检查
```

确认后脚本会自动完成：

```text
识别显卡厂商
→ 选择 CUDA / XPU / ROCm
→ 检查系统驱动
→ 创建独立虚拟环境
→ 安装匹配的 PyTorch 和项目依赖
→ 做真实 GPU 反向传播检查
→ 启动 WebUI
```

首次安装需要下载较大的依赖，耗时取决于网络速度。不要连续双击多次。

如果向导发现已经安装好的匹配环境，会把“检查并快速启动已有环境”放在第一项。选择它不会重新下载依赖。只有需要补齐或修复组件时，才选择“修复或补齐依赖”。AMD Max+ 395 的旧版专用环境会被自动复用，不需要在 `.venv-rocm-windows` 和 `.venv-aimax395-windows` 之间手工判断。

安装时屏幕只显示几个容易理解的阶段；完整 pip 输出和 traceback 自动写入 `logs`。遇到 Windows 应用控制、Liger、GPU 运行时、磁盘不足或端口占用时，向导会显示带背景色的原因和下一步。严格能力模式失败时，可以直接按数字切换到兼容 GPU 模式，不需要再复制 PowerShell 长命令。

### 3.2 Windows：一行命令

在项目目录空白处按住 Shift 并单击鼠标右键，选择“在终端中打开”，然后执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\start_wizard.ps1
```

这条命令与双击入口显示同一个向导。需要远程浏览器访问时，在“WebUI 访问方式”一页选择“局域网、远程服务器或 Jupyter”；只在当前电脑使用时选择“仅本机访问”。

如果是自动化部署且不希望回答问题，才使用高级入口：

```powershell
powershell -ExecutionPolicy Bypass -File .\start_multibackend.ps1 --host-mode local
```

### 3.3 Ubuntu：一行命令

进入解压目录，例如：

```bash
cd /workspace/trainer
```

启动：

```bash
bash start_wizard.sh
```

脚本需要安装系统驱动时会要求输入 `sudo` 密码。输入密码时终端不会显示星号，这是 Linux 的正常行为；输入完成后按 Enter。

向导使用操作系统自带的终端颜色，不要求预装额外 Python 包。完整日志保存在 `logs/setup-wizard-日期-时间.log`；遇到问题时直接提供该文件，不需要复制整屏命令。

### 3.4 驱动安装后的重启

系统驱动属于操作系统组件。安装完成后，脚本会停止并提示重启。

正确操作是：

```text
保存其他工作
→ 重启计算机
→ 回到同一个项目目录
→ 再次双击或执行同一条启动命令
```

不要在尚未重启时反复重新安装驱动。

### 3.5 Windows 全新机器的驱动文件

Windows 驱动与显卡型号绑定，部署包不会重新分发厂商驱动。需要自动安装时，将经过审核的官方安装器放入：

```text
drivers\nvidia-driver.exe
```

或者：

```text
drivers\amd-driver.exe
```

然后再次双击 `start_multibackend.cmd`。安装器会自动执行对应的静默安装命令。

如果驱动已经能正常工作，不需要把安装器放进此目录，也不会自动重装。

### 3.6 多种显卡同时存在

如果一台机器同时有 NVIDIA、Intel 或 AMD 中的两种以上设备，自动选择会停止，要求你明确指定。

Windows 示例：

```powershell
.\start_multibackend.ps1 --backend cuda --host-mode network
```

```powershell
.\start_multibackend.ps1 --backend xpu --host-mode network
```

```powershell
.\start_multibackend.ps1 --backend rocm --host-mode network
```

Ubuntu 示例：

```bash
bash start_multibackend.sh --backend cuda --host-mode network
```

## 4. 如何打开 WebUI

启动成功时，终端会显示类似：

```text
Starting WebUI at http://0.0.0.0:7860
```

`0.0.0.0` 是监听地址，不是浏览器中应该输入的地址。

### 4.1 WebUI 与浏览器在同一台电脑

打开：

```text
http://127.0.0.1:7860
```

### 4.2 WebUI 在远程服务器

先查服务器 IP。

Windows：

```powershell
ipconfig
```

Ubuntu：

```bash
hostname -I
```

假设服务器 IP 是 `192.168.1.50`，在自己的电脑浏览器中打开：

```text
http://192.168.1.50:7860
```

### 4.3 JupyterLab

可以使用 Jupyter 提供的端口代理。常见形式为：

```text
https://你的-Jupyter-地址/proxy/7860/
```

具体代理格式由 Jupyter 服务提供商决定。端口代理存在时，不需要把 7860 暴露到公网。

### 4.4 页面打不开时先检查

按顺序检查：

1. 启动终端是否仍在运行。
2. 终端最后是否显示安装失败。
3. 实际端口是否为 7860。
4. 远程启动是否使用了 `--host-mode network`。
5. 防火墙、云安全组或 Jupyter 端口代理是否允许该端口。

## 5. 准备本地模型目录

一个常见的完整模型目录如下：

```text
D:\models\my-model\
  config.json
  tokenizer.json
  tokenizer_config.json
  model.safetensors.index.json
  model-00001-of-00002.safetensors
  model-00002-of-00002.safetensors
```

Linux 示例：

```text
/workspace/models/my-model/
```

不同模型的文件名可能不同，但至少要有：

- `config.json`。
- 完整权重文件，通常是 `.safetensors` 或 `.bin`。
- 对应的分词器文件。
- 多模态模型还要有 processor 或 preprocessor 配置。

Windows 检查：

```powershell
Get-ChildItem D:\models\my-model
```

Ubuntu 检查：

```bash
ls -lh /workspace/models/my-model
```

以下目录不能当作完整基础模型：

- 只有 `adapter_model.safetensors` 的 LoRA 输出目录。
- 只有 `config.json`、没有权重的目录。
- 缺少某个分片权重的目录。
- 混入多个模型权重和历史备份的目录。

## 6. 准备第一份数据

### 6.1 最快方法：使用演示数据

第一次只为验证流程时，在 WebUI 中选择：

```text
数据目录：data
数据集：alpaca_zh_demo
```

演示数据只能用来确认系统可运行，不能代表你的业务训练效果。

### 6.2 创建自己的 SFT 数据

在项目的 `data` 目录中创建 `my_sft.json`：

```json
[
  {
    "instruction": "用一句话解释什么是训练检查点。",
    "input": "",
    "output": "训练检查点是训练过程中保存的模型与训练状态，可用于恢复或保留阶段性结果。"
  },
  {
    "instruction": "请把下面的句子改写得更礼貌。",
    "input": "把文件发给我。",
    "output": "方便的话，请把文件发送给我，谢谢。"
  }
]
```

JSON 有三个常见规则：

1. 字符串必须使用英文双引号 `"`。
2. 两条记录之间需要逗号。
3. 最后一条记录后面不要加逗号。

### 6.3 注册数据集

WebUI 通过 `data/dataset_info.json` 读取数据集名称。不要把整个文件替换掉，应在现有 JSON 对象内加入：

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

如果它前面还有其他数据集，需要在前一个数据集的右花括号后加逗号。

不熟悉 JSON 时，可以让 Python 帮你安全注册。把下面内容保存为 `register_my_dataset.py`，放在项目根目录：

```python
import json
from pathlib import Path

path = Path("data/dataset_info.json")
config = json.loads(path.read_text(encoding="utf-8"))
config["my_sft"] = {
    "file_name": "my_sft.json",
    "columns": {
        "prompt": "instruction",
        "query": "input",
        "response": "output",
    },
}
path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("Registered dataset: my_sft")
```

Windows 执行：

```powershell
py -3.12 .\register_my_dataset.py
```

Ubuntu 执行：

```bash
python3 register_my_dataset.py
```

完成后重启 WebUI，或重新选择数据目录以刷新列表。

### 6.4 先预览再训练

在 WebUI 第二步选择 `my_sft`，点击数据预览。确认：

- 问题、输入和答案没有错位。
- 中文没有乱码。
- 没有空答案。
- 多模态样本中的图片或视频路径在训练服务器上真实存在。

## 7. 第一次训练：逐页照着填写

第一次训练建议使用一个较小模型和少量样本。先证明流程能运行，再扩大规模。

### 7.1 第一步：模型与目标

建议选择：

| 项目 | 第一次建议 |
| --- | --- |
| 界面语言 | 简体中文 |
| 模型路径 | 你的完整本地模型目录 |
| 训练目标 | SFT / 监督微调 |
| 微调方法 | LoRA |
| 量化 | 先选不量化；显存不足且设备支持时再选 4-bit |
| 模板 | 使用系统识别或模型对应模板，不要随意选其他模型模板 |
| 加速方式 | 使用检测结果；Liger 不可用时允许回退标准训练 |

点击下一步前，确认界面已经识别模型，而不是只接受了一段不存在的路径。

### 7.2 第二步：数据

第一次建议：

```text
数据目录：data
训练数据集：alpaca_zh_demo 或 my_sft
```

点击“预览”，确认至少能看到正常样本，再进入下一步。

### 7.3 第三步：超参数

可以先使用界面自动生成的推荐值。想手工设置时，可从以下保守配置开始：

| 参数 | 第一次建议 | 为什么 |
| --- | ---: | --- |
| 序列长度 | 1024 | 比 4096 更容易跑通，显存占用更低。 |
| 单设备 batch size | 1 | 最安全的起点。 |
| 梯度累积 | 8 | 有效批次约为 8，同时不增加单次 batch。 |
| 学习率 | 0.0002 | 常见 LoRA SFT 起点，不是所有任务的最终最佳值。 |
| epoch | 1 | 先跑通一个完整周期。 |
| 最大样本数 | 100 | 第一次测试不要直接跑完整大数据集。 |
| LoRA rank | 8 | 占用较低的起点。 |
| LoRA alpha | 16 | 常见起点。 |
| LoRA dropout | 0.05 | 提供少量正则化。 |
| 日志步数 | 1 | 很快在 TensorBoard 中看到曲线。 |
| 保存步数 | 20 | 测试任务能较快产生检查点。 |
| 验证方式 | 按比例划分 |
| 验证比例 | 10% |
| 验证 batch size | 1 |

界面会自动让：

```text
eval_steps = save_steps
```

因此每保存一次 checkpoint，就会进行一次验证。用户不需要再填写另一套“验证触发步数”。

关键参数改变后，显存估计会立即刷新。对于普通 safetensors，程序会直接读取张量元数据得到参数量；对于量化权重则结合 `config.json` 计算。估算会读取序列长度、训练及验证 batch、微调方法、量化、精度、优化器、梯度检查点、ZeRO/offload 和多模态设置等信息。

### 7.4 如何看显存提示

界面会先显示估算明细：

- 已加载模型权重：基础模型以及 DPO/PPO 可能需要的辅助模型。
- 梯度与优化器状态：只按实际可训练参数计算，并考虑 ZeRO、offload 和优化器类型。
- 峰值激活值：会随序列长度、单卡 batch、梯度检查点、词表和多模态输入变化。
- 运行时与显存分配器：包含通信桶、内核运行空间和显存碎片预留。

最后显示两项重要数字：

```text
估计训练显存
建议可用显存 = 估计值 × 110%
```

判断方法：

- 可用显存高于建议值：通常可以尝试训练。
- 只高于估计值但低于建议值：存在风险，建议先降低参数。
- 低于估计值：不建议训练。
- 无法读取显存：不要把它当成“显存无限”。

如果仍要强行训练，WebUI 会弹出警告窗口，需要再次确认。

显存不足时按以下顺序调整：

```text
batch size 降到 1
→ 序列长度从 4096 降到 2048 或 1024
→ 使用 LoRA
→ 开启支持的 4-bit 量化
→ 开启梯度检查点
→ 降低多模态图片或视频像素
→ 换更小的模型
```

梯度累积影响有效批次，但通常不会像单设备 batch size 那样增加单次前后向峰值。

### 7.5 第四步：安全检查与输出目录

第一次建议使用新的输出名称，例如：

```text
first_lora_test
```

不要让两个训练任务共用同一个输出目录。

在最终页面确认：

- 模型路径正确。
- 数据集正确。
- 微调方法是 LoRA。
- 输出目录没有覆盖基础模型。
- 显存检查没有明显风险。
- 自动生成的配置允许手工修改时，修改后的值已经重新通过检查。

然后点击“开始训练”。

## 8. 如何判断训练真的开始了

正常现象包括：

- WebUI 日志持续出现 step、loss、learning rate 等信息。
- GPU 使用率上升。
- 输出目录出现日志和事件文件。
- 到达保存步数后出现 `checkpoint-*` 目录。
- 启用验证后，每次保存检查点附近会出现验证指标。

Windows 查看 NVIDIA GPU：

```powershell
nvidia-smi
```

AMD Max+ 395 可以使用任务管理器的 GPU 页面，同时以训练日志和 PyTorch 设备检查为准。共享内存 APU 显示的可用容量不等同于所有容量都能被单次训练稳定分配。

Ubuntu NVIDIA：

```bash
watch -n 1 nvidia-smi
```

训练输出通常位于：

```text
saves/<模型>/<微调方法>/<任务名>/
```

常见内容：

```text
training_args.yaml
llamaboard_config.yaml
webui_subprocess.log
tensorboard_server.log
trainer_log.jsonl
events.out.tfevents.*
checkpoint-20/
checkpoint-40/
adapter_config.json
adapter_model.safetensors
```

文件是否存在取决于训练目前进行到哪一步。

### 8.1 训练完成后快速测试

WebUI 顶部的“快速测试”用于检查模型能否正常回答，不会启动新的训练任务：

1. 打开“快速测试”。
2. “本地模型目录”选择原始基础模型；如果测试已经合并的完整模型，则直接选择合并后的目录。
3. 测试 LoRA 时，在“LoRA 适配器目录”中填写具体的 `checkpoint-*` 或最终适配器目录。
4. 对话模板由程序固定为 `default`，页面不会显示也不能更改。第一次建议保持不量化和自动精度。
5. 点击“加载模型”，出现加载成功提示后输入消息并发送。
6. 测试结束后点击“卸载模型”，释放模型占用的显存。

快速测试固定使用 Hugging Face Transformers，不提供其他推理后端，也不会从网络下载模型。模型目录或适配器目录必须已经存在于当前机器。

## 9. TensorBoard 监控看板

### 9.1 WebUI 训练时自动启动

从 WebUI 开始训练时，系统会自动：

1. 把 TensorBoard 日志目录指向当前训练输出目录。
2. 从 6006 开始寻找可用端口。
3. 启动 TensorBoard。
4. 在 WebUI 日志中显示看板链接。

本机访问通常是：

```text
http://127.0.0.1:6006
```

远程服务器假设 IP 为 `192.168.1.50`：

```text
http://192.168.1.50:6006
```

实际端口可能是 6007、6008 等，以 WebUI 显示为准。

Jupyter 端口代理常见形式：

```text
https://你的-Jupyter-地址/proxy/6006/
```

### 9.2 第一次应该看哪些曲线

| 曲线 | 怎么看 |
| --- | --- |
| `train/loss` | 训练损失。整体下降通常说明模型正在学习；允许短期波动。 |
| `eval/loss` | 验证损失。持续下降或稳定较好；训练损失下降但验证损失明显上升可能是过拟合。 |
| `learning_rate` | 当前学习率。通常会按调度器先升后降或逐步下降。 |
| `grad_norm` | 梯度大小。偶尔波动正常；持续极大、无穷或 NaN 需要停止排查。 |
| `epoch` | 当前训练进行了多少轮。 |

看到以下情况应停止并检查：

- loss 变成 `NaN` 或 `inf`。
- loss 长时间不变化。
- 验证损失持续快速升高。
- 日志停止更新且 GPU 使用率为零。
- 系统开始频繁使用磁盘交换空间。

### 9.3 为什么看板暂时没有曲线

训练必须至少写入一次日志，TensorBoard 才能画图。如果 `logging_steps` 是 10，就要等到第 10 步附近。

还要确认输出目录存在：

```text
events.out.tfevents.*
```

### 9.4 手动启动 TensorBoard

只有通过 CLI 直接训练时，才通常需要手动启动。

Windows CUDA 示例：

```powershell
.\.venv-cuda-windows\Scripts\python.exe -m tensorboard.main `
  --logdir "D:\training-output\first_lora_test" `
  --host 0.0.0.0 `
  --port 6006
```

Windows ROCm 示例：

```powershell
.\.venv-rocm-windows\Scripts\python.exe -m tensorboard.main `
  --logdir "D:\training-output\first_lora_test" `
  --host 0.0.0.0 `
  --port 6006
```

Ubuntu CUDA 示例：

```bash
.venv-cuda-linux/bin/python -m tensorboard.main \
  --logdir /workspace/training-output/first_lora_test \
  --host 0.0.0.0 \
  --port 6006
```

`--host 0.0.0.0` 允许远程访问。仅本机使用时改成 `127.0.0.1`。

### 9.5 停止手动 TensorBoard

在运行 TensorBoard 的终端按：

```text
Ctrl+C
```

如果它在后台运行，Windows 查询占用 6006 端口的进程：

```powershell
Get-NetTCPConnection -LocalPort 6006 -State Listen |
  Select-Object LocalAddress, LocalPort, OwningProcess
```

确认 PID 后停止，例如 PID 为 8368：

```powershell
Stop-Process -Id 8368
```

Ubuntu：

```bash
ps -eo pid,args | grep '[t]ensorboard.main'
```

确认 PID 后：

```bash
kill -TERM 8368
```

不要照抄示例 PID；必须使用自己机器查询到的数字。

## 10. 停止、恢复和检查 checkpoint

### 10.1 正常停止训练

优先点击 WebUI 中的“停止训练”。等待日志确认子进程结束。

不要把关闭浏览器页面当成停止训练。浏览器只是操作界面，后台进程可能仍在运行。

### 10.2 停止 WebUI

回到启动终端，按：

```text
Ctrl+C
```

等待命令行提示符重新出现。

### 10.3 恢复训练

恢复前检查 checkpoint 目录确实存在，例如：

```text
checkpoint-100/
  trainer_state.json
  optimizer.pt
  scheduler.pt
  adapter_model.safetensors
```

在 WebUI 中选择与原训练一致的：

- 基础模型。
- 微调方法。
- 模板。
- checkpoint。
- 数据与重要训练参数。

只有 LoRA 权重、没有优化器状态时，更接近“继续微调适配器”，不一定是完整恢复原训练进度。

## 11. 合并 LoRA 适配器

LoRA 训练结束后，得到的通常不是一个独立完整模型。需要部署完整模型时，可以合并适配器。

在 WebUI 的“适配器合并”区域：

1. 选择训练时使用的同一个完整基础模型目录。
2. 选择正确的模型模板。
3. 选择 LoRA 输出目录或具体 checkpoint。
4. 设置新的导出目录。
5. 默认可选择 CPU 合并；大模型仍需要足够系统内存。
6. 点击开始导出。

导出目录示例：

```text
D:\models\my-model-merged
```

不要把导出目录设置成基础模型目录，也不要覆盖训练 checkpoint。

QLoRA 适配器合并时应使用对应的未量化基础模型。Full 训练已经产生完整权重，通常不需要执行 LoRA 合并。

## 12. 用 YAML 和 CLI 训练

零基础用户建议先在 WebUI 生成一份配置，再复制修改。WebUI 会把最终配置保存到输出目录中的 `training_args.yaml`。

下面是便于阅读的 LoRA SFT 示例。所有路径、模板和数据集名称都必须换成自己的真实值：

```yaml
model_name_or_path: D:/models/my-model
stage: sft
do_train: true
finetuning_type: lora
lora_rank: 8
lora_alpha: 16
lora_dropout: 0.05

dataset_dir: data
dataset: my_sft
template: qwen
cutoff_len: 1024
max_samples: 100

per_device_train_batch_size: 1
gradient_accumulation_steps: 8
learning_rate: 0.0002
num_train_epochs: 1
lr_scheduler_type: cosine
warmup_ratio: 0.1

val_size: 0.1
per_device_eval_batch_size: 1
eval_strategy: steps
save_steps: 20
eval_steps: 20
logging_steps: 1

output_dir: D:/training-output/first_lora_test
logging_dir: D:/training-output/first_lora_test
report_to: tensorboard
overwrite_output_dir: false
```

`template: qwen` 只是示例。模板不匹配可能导致数据格式错误，优先复制 WebUI 自动生成的真实模板值。

Windows ROCm 执行：

```powershell
.\.venv-rocm-windows\Scripts\python.exe -X utf8 -m llamafactory.cli train D:\training-output\first_lora_test\training_args.yaml
```

Windows CUDA：

```powershell
.\.venv-cuda-windows\Scripts\python.exe -X utf8 -m llamafactory.cli train D:\training-output\first_lora_test\training_args.yaml
```

Ubuntu CUDA：

```bash
.venv-cuda-linux/bin/python -X utf8 -m llamafactory.cli train /workspace/training-output/first_lora_test/training_args.yaml
```

CLI 不会显示 WebUI 的显存警告弹窗。手工修改 YAML 后，应自行核对显存风险，并确保：

```yaml
eval_steps: 20
save_steps: 20
```

二者相同，才能保证每次保存时进行一次验证。

## 13. 多模态模型

系统检测到视觉或多模态配置后，才会显示相关参数。

零基础建议：

- 先冻结视觉塔。
- 先冻结视觉投影器，确认纯语言侧 LoRA 能跑通后再调整。
- 使用较低图片像素上限。
- 首次不要用长视频。
- 确认媒体路径是训练服务器上的路径，而不是自己笔记本上的路径。

提高图片分辨率、视频帧数或解冻视觉模块都会明显增加显存。

## 14. 常见问题：按现象查找

### 14.1 `127.0.0.1` 拒绝连接

检查启动终端是否还在运行。远程服务器应使用：

```text
--host-mode network
```

浏览器访问服务器真实 IP，不要在自己的电脑上把远程服务器理解成 `127.0.0.1`。

### 14.2 提示找不到 Python

Windows 安装 Python 3.12 x64 后重新打开 PowerShell：

```powershell
py -3.12 --version
```

Ubuntu：

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
```

### 14.3 安装很久没有结束

Torch、ROCm 和 CUDA 依赖可能很大。检查终端是否仍有下载进度、磁盘是否还有空间。不要同时运行第二个安装进程。

### 14.4 提示必须重启

系统驱动刚安装完成。重启后运行同一个启动入口，不需要改命令。

### 14.5 `torch.cuda.is_available()` 是 False

这不只发生在 NVIDIA。PyTorch 的 ROCm 后端也使用 `torch.cuda` 接口。

Windows ROCm 检查：

```powershell
$py = ".\.venv-rocm-windows\Scripts\python.exe"
& $py -c "import torch; print(torch.__version__); print(torch.version.hip); print(torch.cuda.is_available()); print(torch.cuda.device_count())"
```

正常 ROCm 应看到：

```text
torch.version.hip 有版本号
torch.cuda.is_available() 为 True
device_count 大于等于 1
```

### 14.6 ROCm SDK 自检找不到 `hipconfig`

先激活虚拟环境，使 `Scripts` 目录进入 PATH：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
& .\.venv-rocm-windows\Scripts\Activate.ps1
python -m rocm_sdk test
```

如果 `hipInfo.exe` 能识别 `gfx1151` 且 PyTorch 可用，这类 PATH 错误不等于 GPU 驱动失效。

### 14.6.1 Windows 报 `WinError 4551`

`应用程序控制策略已阻止此文件` 不是下载失败，也不是 ROCm 驱动失效。它表示 Windows Defender Application Control、Smart App Control 或单位的安全策略阻止了 Triton 临时编译的 `.pyd`，或 bitsandbytes 的原生 DLL。

新版一键包会把这两项当作可选能力处理：

- Liger 不可用时自动回退标准训练。
- bitsandbytes 不可用时仍允许不量化的 LoRA/Full 训练，但不要选择 4-bit 或 8-bit。
- torchaudio 或 torchvision 的原生扩展被拦截时，仅对应的音频或视觉预处理不可用；纯文本训练不受影响。
- ROCm、PyTorch、`gfx1151` 和基础反向传播仍必须通过检查，不能回退到 CPU 冒充成功。

如果企业环境必须使用 Liger 或 QLoRA，请让设备管理员根据组织安全规范审核并放行对应 ROCm、Triton、bitsandbytes 文件。不要为了运行训练而直接关闭整机安全策略。

### 14.7 AMD Max+ 395 显示 100 GB 以上可用显存

这是统一内存 APU 的常见表现。它表示 GPU 可以访问的共享容量，不保证单个训练任务能无碎片地全部分配。仍应保留安全余量，并从 batch size 1 开始。

### 14.8 显存不足或 OOM

依次降低：

```text
batch size
序列长度
图片/视频像素
LoRA rank
验证 batch size
```

然后开启梯度检查点，或换用受支持的 4-bit LoRA。不要把增加梯度累积当成释放当前一次前后向所需显存。

### 14.9 TensorBoard 打得开但没有曲线

检查：

1. 训练是否至少运行到一次 `logging_steps`。
2. TensorBoard 的 logdir 是否是本次任务输出目录。
3. 输出目录是否有 `events.out.tfevents.*`。
4. 查看 `tensorboard_server.log`。

### 14.10 每次保存时没有验证

打开实际保存的 `training_args.yaml`，确认：

```yaml
eval_strategy: steps
save_steps: 20
eval_steps: 20
```

还要确认验证方式不是关闭，并且验证数据不为空。

### 14.11 中文乱码

始终通过项目启动脚本运行。手动执行 Python 时加：

```text
-X utf8
```

### 14.12 旧界面仍在运行

先在旧启动终端按 `Ctrl+C`，确认进程退出，再重新运行统一入口。刷新网页不能让旧 Python 进程自动加载新代码。

## 15. 收集日志并请求帮助

报告问题时至少提供：

- 操作系统版本。
- GPU 型号。
- 选择的后端。
- 启动终端最后 100 行。
- 当前任务的 `webui_subprocess.log`。
- `training_args.yaml`，但先删除私有路径和敏感信息。
- OOM 时的模型目录权重总大小、序列长度、batch size、梯度累积和量化设置。

Windows 导出基础环境信息：

```powershell
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsBuildNumber
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion, DriverDate
```

查看任务日志最后 100 行：

```powershell
Get-Content D:\training-output\first_lora_test\webui_subprocess.log -Tail 100
```

Ubuntu：

```bash
uname -a
lspci | grep -Ei 'vga|3d|display'
tail -n 100 /workspace/training-output/first_lora_test/webui_subprocess.log
```

分享日志前删除访问令牌、用户名、内部服务器地址、私有数据内容和其他敏感信息。

## 16. 安全地重新安装某个后端环境

不要把 CUDA、XPU、ROCm 装进同一个虚拟环境。统一入口已经为它们分开目录。

环境损坏时，先停止 WebUI 和训练，再把旧环境改名保留，而不是立即永久删除。

Windows ROCm 示例：

```powershell
Rename-Item .venv-rocm-windows .venv-rocm-windows-backup
.\start_multibackend.ps1 --backend rocm --no-start --liger off
```

Ubuntu CUDA 示例：

```bash
mv .venv-cuda-linux .venv-cuda-linux-backup
bash start_multibackend.sh --backend cuda --no-start --liger off
```

新环境确认正常后，再决定是否清理备份。

## 17. 第一次训练完成检查表

完成以下所有项目，才算流程真正跑通：

- [ ] 统一启动器识别了正确的 CUDA、XPU 或 ROCm 后端。
- [ ] 环境检查没有回退到 CPU。
- [ ] WebUI 能从浏览器打开。
- [ ] 本地模型目录包含完整权重和 tokenizer。
- [ ] 数据预览正常。
- [ ] 使用 SFT + LoRA 完成至少一个小训练任务。
- [ ] TensorBoard 能看到训练损失。
- [ ] 启用验证后，保存检查点时出现验证指标。
- [ ] 输出目录包含 `training_args.yaml`、日志和 LoRA 权重。
- [ ] 如需完整模型，适配器已经成功合并到新的导出目录。

第一次跑通后，再逐步增加样本数、序列长度、batch size、训练周期和多模态复杂度。一次只改少量参数，才能从日志中判断是哪项变化带来了效果或问题。
