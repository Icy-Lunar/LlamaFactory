"""Check optional Liger kernels without making them a prerequisite for training."""

import importlib.metadata as metadata
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from packaging.version import Version

from .diagnostics import stage


# Keep this list aligned with the model patches used by model_utils/liger_kernel.py.
MODEL_PATCHES = {
    name: f"apply_liger_kernel_to_{name}"
    for name in (
        "gemma",
        "gemma2",
        "gemma3",
        "gemma3_text",
        "glm4",
        "glm4v",
        "granite",
        "llama",
        "llava",
        "mistral",
        "mixtral",
        "mllama",
        "olmo2",
        "paligemma",
        "phi3",
        "qwen2",
        "qwen2_vl",
        "qwen2_5_vl",
        "qwen3",
        "qwen3_moe",
        "qwen3_next",
        "qwen3_5",
        "qwen3_5_moe",
        "gpt_oss",
    )
}
MODEL_PATCHES["glm"] = MODEL_PATCHES["glm4"]
DEFAULT_PROBE_TIMEOUT = 300


@dataclass(frozen=True)
class LigerStatus:
    enabled: bool
    reason: str
    detail: str = ""
    patches: tuple[str, ...] = ()


def _probe() -> None:
    """Exercise forward/backward in an isolated process, including the memory-saving loss."""
    print("LIGER_STAGE=imports", file=sys.stderr, flush=True)
    import liger_kernel.transformers as kernels
    import torch
    import triton

    from .accelerator import configure_xpu_environment
    from .misc import get_current_device

    device = get_current_device()
    if device.type == "xpu":
        configure_xpu_environment(os.environ)
    elif device.type == "cuda":
        # Some Triton kernels compile or launch against the active device rather than the tensor device.
        device_index = device.index if device.index is not None else torch.cuda.current_device()
        torch.cuda.set_device(device_index)
        device = torch.device("cuda", device_index)
    if device.type not in {"cuda", "xpu", "npu"}:
        raise RuntimeError(f"Unsupported Liger device: {device.type}")
    minimum = "2.5.0" if torch.version.hip else "2.6.0" if device.type == "xpu" else "2.1.2"
    if Version(torch.__version__) < Version(minimum):
        raise RuntimeError(f"Liger on {device.type} requires torch>={minimum}")
    if device.type == "cuda":
        minimum_triton = "3.0.0" if torch.version.hip else "2.3.1"
        if Version(triton.__version__) < Version(minimum_triton):
            raise RuntimeError(f"Liger requires triton>={minimum_triton}")
    # Driver selection rejects a missing/mismatched Triton backend before allocating tensors.
    target = triton.runtime.driver.active.get_current_target()
    expected = {"cuda": {"hip"} if torch.version.hip else {"cuda"}, "xpu": {"xpu"}, "npu": {"npu", "ascend"}}
    if target.backend not in expected[device.type]:
        raise RuntimeError(f"Triton backend {target.backend} does not match {device.type}")
    print(f"LIGER_STAGE=rms_norm backend={target.backend}", file=sys.stderr, flush=True)
    dtype = getattr(torch, sys.argv[2] if len(sys.argv) > 2 else "float32")
    x = torch.randn(2, 128, device=device, dtype=dtype, requires_grad=True)
    norm = kernels.LigerRMSNorm(128).to(device=device, dtype=dtype)
    result = norm(x)
    result.float().sum().backward()
    if not torch.isfinite(result).all() or not torch.isfinite(x.grad).all():
        raise RuntimeError("Liger RMSNorm produced non-finite values")
    print("LIGER_STAGE=fused_linear_cross_entropy", file=sys.stderr, flush=True)
    weight = torch.randn(256, 128, device=device, dtype=dtype, requires_grad=True)
    inputs = x.detach().requires_grad_(True)
    labels = torch.tensor([0, 1], device=device)
    loss = kernels.LigerFusedLinearCrossEntropyLoss()(weight, inputs, labels)
    loss.backward()
    if not torch.isfinite(loss) or not torch.isfinite(inputs.grad).all():
        raise RuntimeError("Liger fused loss produced non-finite values")
    accelerator = getattr(torch, device.type, None)
    if accelerator is not None and hasattr(accelerator, "synchronize"):
        accelerator.synchronize()
    patches = [name for name in MODEL_PATCHES.values() if callable(getattr(kernels, name, None))]
    print("LIGER_PROBE=" + json.dumps(patches))


def _probe_timeout() -> int:
    try:
        return max(60, int(os.getenv("LLAMAFACTORY_LIGER_PROBE_TIMEOUT", DEFAULT_PROBE_TIMEOUT)))
    except ValueError:
        return DEFAULT_PROBE_TIMEOUT


def _timeout_detail(error: subprocess.TimeoutExpired, timeout: int) -> str:
    output = error.stderr or error.stdout or ""
    if isinstance(output, bytes):
        output = output.decode("utf-8", errors="replace")
    last_output = str(output).strip()[-2000:]
    message = f"Liger CUDA/Triton probe timed out after {timeout}s; first-run kernel compilation may still be active."
    return f"{message} Last probe output: {last_output}" if last_output else message


@lru_cache(maxsize=3)
def get_liger_status(dtype: str = "float32") -> LigerStatus:
    """Cache a bounded runtime check; restart after changing drivers or packages."""
    if os.getenv("LLAMAFACTORY_LIGER", "auto").lower() == "off":
        return LigerStatus(False, "disabled")
    try:
        if Version(metadata.version("liger-kernel")) < Version("0.8.0"):
            return LigerStatus(False, "version", "liger-kernel>=0.8.0 is required")
    except metadata.PackageNotFoundError:
        return LigerStatus(False, "missing", "liger-kernel is not installed")
    timeout = _probe_timeout()
    stage("liger_probe", timeout=timeout, dtype=dtype)
    try:
        result = subprocess.run(
            [sys.executable, "-X", "utf8", "-m", "llamafactory.extras.liger", "--probe", dtype],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env={**os.environ, "PYTHONUTF8": "1"},
        )
        for line in reversed(result.stdout.splitlines()):
            if result.returncode == 0 and line.startswith("LIGER_PROBE="):
                return LigerStatus(True, "available", patches=tuple(json.loads(line.removeprefix("LIGER_PROBE="))))
        detail = (result.stderr or result.stdout).strip()[-2000:]
        return LigerStatus(False, "runtime", detail or f"Probe exited with code {result.returncode}")
    except subprocess.TimeoutExpired as error:
        return LigerStatus(False, "runtime", _timeout_detail(error, timeout))
    except (OSError, ValueError) as error:
        return LigerStatus(False, "runtime", str(error))


def get_model_liger_status(model_type: str, dtype: str = "float32") -> LigerStatus:
    status = get_liger_status(dtype)
    if not status.enabled:
        return status
    if MODEL_PATCHES.get(model_type) not in status.patches:
        return LigerStatus(False, "model", f"No installed Liger patch for model_type={model_type}")
    return status


def get_local_liger_status(model_path: str | None, compute_type: str = "fp32", *, probe: bool = True) -> LigerStatus:
    if not probe:
        # Preview/save/start must never compile GPU kernels in the WebUI request.
        if os.getenv("LLAMAFACTORY_LIGER", "auto").lower() == "off":
            return LigerStatus(False, "disabled")
        try:
            if Version(metadata.version("liger-kernel")) < Version("0.8.0"):
                return LigerStatus(False, "version")
            config = json.loads((Path(model_path or "") / "config.json").read_text(encoding="utf-8"))
            supported = config.get("model_type") in MODEL_PATCHES
            return LigerStatus(supported, "pending" if supported else "model")
        except metadata.PackageNotFoundError:
            return LigerStatus(False, "missing")
        except (OSError, ValueError, AttributeError):
            return LigerStatus(False, "model")
    dtype = {"bf16": "bfloat16", "pure_bf16": "bfloat16", "fp16": "float16"}.get(compute_type, "float32")
    status = get_liger_status(dtype)
    if not status.enabled:
        return status
    try:
        config = json.loads((Path(model_path or "") / "config.json").read_text(encoding="utf-8"))
        return get_model_liger_status(config.get("model_type", ""), dtype)
    except (OSError, ValueError, AttributeError):
        return LigerStatus(False, "model", "Cannot read a supported local model configuration")


if __name__ == "__main__":
    if "--probe" in sys.argv:
        _probe()
    else:
        status = get_liger_status()
        print(json.dumps({"enabled": status.enabled, "reason": status.reason, "detail": status.detail}))
