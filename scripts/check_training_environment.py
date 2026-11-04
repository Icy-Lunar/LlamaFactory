"""Validate packages and actual device execution in the selected environment."""

import argparse
import contextlib
import importlib
import importlib.metadata as metadata
import io
import json
import os


def package_version(name: str) -> str | None:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return None


def detect_device_architecture(torch) -> str | None:
    """Read the active AMD architecture from Torch without requiring hipInfo on PATH."""
    properties = torch.cuda.get_device_properties(0)
    for attribute in ("gcnArchName", "gcn_arch_name", "arch_name"):
        value = getattr(properties, attribute, None)
        if value:
            return str(value)
    get_arch_list = getattr(torch.cuda, "get_arch_list", None)
    if callable(get_arch_list):
        architectures = [str(value) for value in get_arch_list() if str(value).startswith("gfx")]
        if architectures:
            return architectures[0]
    return None


def check_optional_import(name: str, capability: str) -> tuple[str | None, str]:
    """Report an optional native extension without turning it into a core runtime gate."""
    version = package_version(name)
    if version is None:
        return None, "unavailable: package is not installed"
    diagnostics = io.StringIO()
    try:
        with contextlib.redirect_stdout(diagnostics), contextlib.redirect_stderr(diagnostics):
            importlib.import_module(name)
    except Exception as error:
        detail = str(error).strip() or type(error).__name__
        captured = diagnostics.getvalue().strip().splitlines()
        if captured:
            detail = f"{detail}; {captured[-1]}"
        print(f"WARNING: {capability} is unavailable, but unrelated training modes remain usable. {detail}")
        return version, f"unavailable: {detail}"
    return version, "available"


def check_bitsandbytes(torch, device_type: str) -> tuple[str | None, str]:
    """Probe optional 4-bit execution without preventing ordinary LoRA/full training."""
    version = package_version("bitsandbytes")
    if version is None:
        return None, "unavailable: package is not installed"

    diagnostics = io.StringIO()
    try:
        with contextlib.redirect_stdout(diagnostics), contextlib.redirect_stderr(diagnostics):
            bnb = importlib.import_module("bitsandbytes")
            supported_devices = getattr(bnb, "supported_torch_devices", set())
            if device_type not in supported_devices:
                return version, "unsupported by this bitsandbytes build"
            layer = bnb.nn.Linear4bit(
                64,
                32,
                quant_type="nf4",
                compress_statistics=device_type != "npu",
            ).to(device_type)
            data = torch.randn(2, 64, device=device_type, requires_grad=True)
            layer(data).float().sum().backward()
            if data.grad is None or not torch.isfinite(data.grad).all():
                raise RuntimeError("4-bit backward check returned an invalid gradient")
    except Exception as error:  # Native loaders may raise OSError/RuntimeError under Windows application control.
        detail = str(error).strip() or type(error).__name__
        captured = diagnostics.getvalue().strip().splitlines()
        if captured:
            detail = f"{detail}; {captured[-1]}"
        print(
            "WARNING: bitsandbytes 4-bit execution is unavailable; ordinary non-quantized training remains usable. "
            f"{detail}"
        )
        return version, f"unavailable: {detail}"
    return version, "available"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", required=True)
    parser.add_argument("--liger", choices=("auto", "off", "required"), default="auto")
    parser.add_argument("--expected-arch")
    parser.add_argument("--require-all-capabilities", action="store_true")
    args = parser.parse_args()
    import torch

    from llamafactory.extras.accelerator import configure_xpu_environment

    if args.backend == "xpu":
        configure_xpu_environment(os.environ)
    if args.liger == "off":
        os.environ["LLAMAFACTORY_LIGER"] = "off"
    import gradio
    import jieba
    import nltk
    import rouge_chinese
    import tensorboard
    from llamafactory.extras.liger import get_liger_status

    device_type = "cuda" if args.backend == "rocm" else args.backend
    if device_type != "cpu" and not getattr(torch, device_type).is_available():
        raise RuntimeError(f"Requested device {device_type} is unavailable")
    if args.backend == "cuda" and torch.version.hip or args.backend == "rocm" and not torch.version.hip:
        raise RuntimeError("Installed PyTorch backend does not match the selected accelerator")
    device = torch.device(device_type)
    device_arch = None
    if device_type == "cuda":
        device_arch = detect_device_architecture(torch) if args.backend == "rocm" else None
        if args.expected_arch and not str(device_arch or "").startswith(args.expected_arch):
            raise RuntimeError(
                f"Expected device architecture {args.expected_arch}, but PyTorch reported {device_arch or 'unknown'}"
            )
    sample = torch.randn(4, 16, device=device, requires_grad=True)
    sample.square().mean().backward()
    if not torch.isfinite(sample.grad).all():
        raise RuntimeError("Device backward check failed")
    torchvision_version, torchvision_status = check_optional_import("torchvision", "vision preprocessing")
    torchaudio_version, torchaudio_status = check_optional_import("torchaudio", "audio preprocessing")
    bnb_version, quantization = check_bitsandbytes(torch, device_type)
    if quantization != "available":
        print(
            f"WARNING: do not select 4-bit/8-bit quantization on {device_type} until the report says it is available."
        )
    liger_dtype = "float32"
    if args.backend == "cuda":
        liger_dtype = "bfloat16" if torch.cuda.is_bf16_supported() else "float16"
    elif args.backend == "rocm":
        liger_dtype = "float16"
    status = get_liger_status(liger_dtype)
    if args.liger == "required" and not status.enabled:
        raise RuntimeError(f"Liger is required but unavailable: {status.reason}: {status.detail}")
    if args.require_all_capabilities:
        unavailable = []
        if torchvision_status != "available":
            unavailable.append("vision preprocessing")
        if torchaudio_status != "available":
            unavailable.append("audio preprocessing")
        if quantization != "available":
            unavailable.append("bitsandbytes quantization")
        if not status.enabled:
            unavailable.append("Liger acceleration")
        if unavailable:
            raise RuntimeError("Required training capabilities unavailable: " + ", ".join(unavailable))
    print(
        json.dumps(
            {
                "device": str(device),
                "device_arch": device_arch,
                "torch": torch.__version__,
                "torchvision": torchvision_version,
                "torchaudio": torchaudio_version,
                "media_extensions": {
                    "vision": torchvision_status,
                    "audio": torchaudio_status,
                },
                "bitsandbytes": bnb_version,
                "quantization": quantization,
                "tensorboard": tensorboard.__version__,
                "gradio": gradio.__version__,
                "metrics": [nltk.__name__, jieba.__name__, rouge_chinese.__name__],
                "triton_providers": {
                    dist.metadata["Name"]: dist.version
                    for dist in metadata.distributions()
                    if dist.metadata["Name"].lower().replace("_", "-")
                    in {
                        "triton",
                        "triton-windows",
                        "triton-xpu",
                        "pytorch-triton-xpu",
                        "pytorch-triton-rocm",
                        "triton-ascend",
                    }
                },
                "liger": {
                    "enabled": status.enabled,
                    "reason": status.reason,
                    "detail": status.detail,
                    "probe_dtype": liger_dtype,
                    "version": next(
                        (
                            dist.version
                            for dist in metadata.distributions()
                            if dist.metadata["Name"].lower().replace("_", "-") == "liger-kernel"
                        ),
                        None,
                    ),
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
