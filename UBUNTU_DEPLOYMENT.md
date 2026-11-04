# Ubuntu 部署说明

本发布包包含当前训练 WebUI、设备感知依赖安装器和运行检查脚本。验证集从训练数据中划分时使用百分比，界面默认值 `10` 会写入训练配置为 `val_size: 0.10`；验证间隔自动等于检查点保存间隔，每保存一次就验证一次。

## 1. 系统要求

- Ubuntu 22.04 或 24.04（x86_64）。
- Python 3.11 或更高版本，推荐 Python 3.12。
- 目标加速卡对应的驱动已经由运维人员安装并通过厂商工具验证。
- 首次安装需要访问 Python 与 PyTorch 软件源；发布包不包含模型、驱动或硬件专用 PyTorch wheel。

安装基础系统包：

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip build-essential
python3 --version
```

## 2. 解压并启动

```bash
unzip cyrene-llamafactory-ubuntu-20261026.zip
cd cyrene-llamafactory-ubuntu-20261026
bash start_webui.sh --backend auto
```

JupyterLab 可以在文件浏览器中直接解压 ZIP。若使用 `.tar.gz` 版本，则执行 `tar -xzf cyrene-llamafactory-ubuntu-20261026.tar.gz`。

交互启动时会先询问访问方式：选择 `1` 后 WebUI 与 TensorBoard 都只允许服务器本机访问（`127.0.0.1`），选择 `2` 后两者都允许 Jupyter 端口代理或局域网访问（`0.0.0.0`）。Notebook 单元等非交互环境应直接运行：

```bash
bash start_webui.sh --backend auto --host-mode network
```

安装器会创建 `.venv`、识别实际加速设备、安装匹配的 PyTorch 与项目依赖、检查反向传播和可用的 Liger Kernel，然后启动 WebUI。也可以将 `auto` 改为 `cuda`、`rocm`、`xpu`、`npu` 或 `cpu`。启动 WebUI 时安装器会替换自身进程，因此 `Ctrl+C` 能直接终止服务。

训练开始后，内置 TensorBoard 从端口 `6006` 起选择可用端口。JupyterHub 会自动生成 `/user/.../proxy/<端口>/` 看板链接；普通 Jupyter 代理可以在启动前设置，例如：

```bash
TENSORBOARD_PUBLIC_URL='/proxy/{port}/' \
SKIP_INSTALL=1 bash start_webui.sh --backend cuda --host-mode network
```

如果部署要求 Liger 检查必须通过，请增加 `--liger required`。仅准备环境而不启动服务时使用：

```bash
bash start_webui.sh --backend auto --liger required --no-start
```

CUDA 首次启动会编译 Liger/Triton 探测算子，默认最多等待 300 秒，并把缓存保存在 `.venv/.triton-cache`。若服务器首次编译确实更慢，可以显式延长而不修改代码：

```bash
LLAMAFACTORY_LIGER_PROBE_TIMEOUT=600 \
bash start_webui.sh --backend cuda --liger required --no-start
```

后续启动可跳过重复安装：

```bash
SKIP_INSTALL=1 WEBUI_PORT=7860 bash start_webui.sh --backend auto --host-mode network
```

## 3. 部署注意事项

- WebUI 读取服务器已有的本地模型目录，不会替用户下载模型。请提前挂载模型和数据目录，并授予运行账户只读或所需的最小权限。
- `0.0.0.0` 会监听所有网卡。生产环境应通过防火墙、VPN 或带身份认证的反向代理限制访问，不应将未鉴权端口直接暴露到公网。

AMD Ryzen AI Max+ 395 请不要使用通用 `--backend rocm` 的 ROCm 6.4 默认源。使用专用的一键入口：

```bash
bash start_aimax395.sh --host-mode network
```

它会选择 AMD 官方 ROCm 10.1 / PyTorch 2.14 `gfx1151` 软件包并验证设备架构；内核与统一内存的准备步骤见 [AI Max+ 395 部署指南](AIMAX395_DEPLOYMENT.md)。
- NVIDIA、AMD、Intel XPU 和昇腾环境使用不同的 PyTorch/驱动组合。安装器不会在加速设备检查失败后静默切换到 CPU。
- 可先运行 `bash start_webui.sh --backend <类型> --dry-run --no-start` 查看安装计划。
- 使用同目录下的 `.sha256` 文件校验发布包完整性：`sha256sum -c cyrene-llamafactory-ubuntu-20261026.zip.sha256`。

更完整的设备安装说明见 `PROJECT_INSTALLATION_AND_USAGE.md` 和 `docs/DEPENDENCY_INSTALLATION.md`。
