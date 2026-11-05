"""Install dependencies for the detected accelerator, verify them, and start WebUI."""

import argparse
import json
import os
import platform
import subprocess
import sys
import tempfile
import time
from pathlib import Path


try:
    from .session_logging import enable_console_log, run_logged
except ImportError:
    from session_logging import enable_console_log, run_logged


ROOT = Path(__file__).resolve().parents[1]
PYTORCH_INDEX = "https://download.pytorch.org/whl/"
AMD_WINDOWS = "https://repo.radeon.com/rocm/windows/rocm-rel-7.2.1/"
AMD_ROCM_NEXT_INDEX = "https://stable.repo.amd.com/rocm/whl-next/"
NPU_GUIDE = "https://llamafactory.readthedocs.io/en/latest/multibackend/npu/npu_installation.html"
RYZEN_AI_GUIDE = "https://rocm.docs.amd.com/en/latest/reference/system-optimization/rdna3-5.html"
BACKENDS = ("auto", "cuda", "xpu", "rocm", "npu", "cpu")
HOST_MODES = ("ask", "local", "network")
ROCM_PROFILES = ("generic", "aimax395")
RYZEN_AI_MAX_PACKAGES = (
    "torch[device-gfx1151]==2.14.0+rocm10.1.0",
    "torchvision[device-gfx1151]==0.29.0a0+rocm10.1.0",
    "torchaudio==2.11.0.3+rocm10.1.0",
)
RYZEN_AI_MAX_LINUX_SDK = "rocm[libraries,device-gfx1151]==10.1.0"
RYZEN_AI_MAX_WINDOWS_SDK = "rocm[libraries,devel,device-gfx1151]==10.1.0"


def capture(command: list[str], timeout: int = 30) -> str:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""


def is_wsl() -> bool:
    """Return whether the current Linux process is hosted by WSL."""
    if platform.system() != "Linux":
        return False
    for path in (Path("/proc/sys/kernel/osrelease"), Path("/proc/version")):
        try:
            if "microsoft" in path.read_text(encoding="utf-8", errors="replace").lower():
                return True
        except OSError:
            continue
    return False


def windows_display_devices() -> str:
    """Read host display adapters from Windows, including when called through WSL interop."""
    return capture(
        [
            "powershell.exe",
            "-NoProfile",
            "-Command",
            "Get-CimInstance Win32_VideoController | "
            "ForEach-Object { '{0}|{1}|{2}' -f $_.Name,$_.PNPDeviceID,$_.DriverVersion }",
        ]
    )


def detect_backends() -> set[str]:
    """Inspect accelerator devices, never the CPU vendor."""
    found = set()
    if capture(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"]):
        found.add("cuda")
    if capture(["npu-smi", "info"]):
        found.add("npu")
    if platform.system() == "Windows":
        devices = capture(
            [
                "powershell.exe",
                "-NoProfile",
                "-Command",
                "Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty PNPDeviceID",
            ]
        )
        for vendor, backend in (("VEN_10DE", "cuda"), ("VEN_8086", "xpu"), ("VEN_1002", "rocm")):
            if vendor in devices.upper():
                found.add(backend)
    elif platform.system() == "Linux":
        for device in Path("/sys/class/drm").glob("card[0-9]*/device/vendor"):
            try:
                vendor = device.read_text().strip().lower()
            except OSError:
                continue
            backend = {"0x10de": "cuda", "0x8086": "xpu", "0x1002": "rocm"}.get(vendor)
            if backend:
                found.add(backend)
        if capture(["rocm-smi", "--showproductname"]) or capture(["amd-smi", "list"]):
            found.add("rocm")
        if capture(["xpu-smi", "discovery"]):
            found.add("xpu")
        if is_wsl() and Path("/dev/dxg").exists():
            devices = windows_display_devices().upper()
            for vendor, backend in (("VEN_10DE", "cuda"), ("VEN_8086", "xpu"), ("VEN_1002", "rocm")):
                if vendor in devices:
                    found.add(backend)
    return found


def choose_backend(requested: str, detected: set[str], existing: str | None = None) -> str:
    if requested != "auto":
        return requested
    if existing and existing != "cpu" and (not detected or existing in detected):
        return existing
    return next((name for name in ("cuda", "npu", "xpu", "rocm") if name in detected), "cpu")


def venv_python(directory: Path) -> Path:
    return directory / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def inspect_runtime(python: Path, timeout: int = 30) -> dict:
    if not python.is_file():
        return {}
    source = """
import importlib.metadata as m
import json
import torch
backend = 'cpu'
build_backend = 'rocm' if torch.version.hip else ('cuda' if torch.version.cuda else None)
for name in ('xpu', 'npu', 'cuda'):
    module = getattr(torch, name, None)
    if module is not None and module.is_available():
        backend = 'rocm' if name == 'cuda' and torch.version.hip else name
        break
versions = {d.metadata['Name'].lower().replace('_', '-'): d.version for d in m.distributions()}
print('RUNTIME=' + json.dumps({'backend': backend, 'build_backend': build_backend, 'versions': versions}))
"""
    output = capture([str(python), "-X", "utf8", "-c", source], timeout=timeout)
    for line in reversed(output.splitlines()):
        if line.startswith("RUNTIME="):
            return json.loads(line.removeprefix("RUNTIME="))
    return {}


def prepend_executable_directory(python: Path) -> None:
    """Expose console shims and native runtime helpers from the selected environment."""
    scripts_directory = str(python.parent.resolve())
    current = os.environ.get("PATH", "")
    entries = current.split(os.pathsep) if current else []
    if scripts_directory.casefold() not in {entry.casefold() for entry in entries}:
        os.environ["PATH"] = scripts_directory + (os.pathsep + current if current else "")


def initialize_windows_rocm_sdk(python: Path, *, dry_run: bool = False) -> bool:
    """Expand the pip ROCm SDK before the first Torch device probe on Windows."""
    prepend_executable_directory(python)
    executable = python.parent / "rocm-sdk.exe"
    command = [str(executable), "init"] if executable.is_file() or dry_run else [str(python), "-m", "rocm_sdk", "init"]
    return run(
        command,
        dry_run=dry_run,
        check=False,
    )


def python_module_exists(python: Path, module: str) -> bool:
    source = f"import importlib.util; print('1' if importlib.util.find_spec({module!r}) else '0')"
    return capture([str(python), "-X", "utf8", "-c", source], timeout=30).strip() == "1"


def wait_for_runtime(
    python: Path,
    backend: str,
    *,
    attempts: int = 3,
    timeout: int = 180,
    delay: float = 2.0,
) -> dict:
    """Allow slow first-load device runtimes to initialize without being misclassified as CPU-only."""
    runtime = {}
    for attempt in range(1, attempts + 1):
        runtime = inspect_runtime(python, timeout=timeout)
        if runtime.get("backend") == backend:
            return runtime
        if attempt < attempts:
            print(f"Device runtime is not ready yet; retrying probe ({attempt}/{attempts})...", flush=True)
            time.sleep(delay)
    return runtime


def _kernel_numbers(release: str) -> tuple[int, ...]:
    numbers = []
    for part in release.replace("-", ".").split("."):
        digits = "".join(character for character in part if character.isdigit())
        if not digits:
            break
        numbers.append(int(digits))
    return tuple(numbers)


def supports_gfx1151_kernel(release: str) -> bool:
    """Check the minimum upstream or Ubuntu kernel containing the required gfx1151 KFD fixes."""
    numbers = _kernel_numbers(release)
    padded = (*numbers, 0, 0, 0, 0)
    major, minor, patch, build = padded[:4]
    if (major, minor, patch) >= (7, 0, 0):
        return True
    if (major, minor, patch) == (6, 17, 0) and build >= 19:
        return True
    if (major, minor, patch) == (6, 14, 0) and build >= 1018:
        return True
    return (major, minor, patch) >= (6, 18, 4)


def validate_ryzen_ai_max_host(*, dry_run: bool = False) -> None:
    """Fail before package installation when the host cannot expose gfx1151 compute safely."""
    if platform.machine().lower() not in {"x86_64", "amd64"}:
        raise ValueError("The Ryzen AI Max+ 395 training profile requires an x86-64 operating system.")
    if platform.system() == "Windows":
        if platform.release() != "11":
            raise ValueError("The Ryzen AI Max+ 395 ROCm profile requires Windows 11.")
        if dry_run:
            print("Ryzen AI Max+ 395 prerequisite: install a current AMD Software driver for Windows 11.")
        return
    if platform.system() != "Linux":
        raise ValueError("The Ryzen AI Max+ 395 training profile requires Windows 11 or Linux. " + RYZEN_AI_GUIDE)
    if is_wsl():
        if dry_run:
            print(
                "Ryzen AI Max+ 395 WSL prerequisite: expose /dev/dxg and install a compatible AMD driver "
                "on the Windows host; /dev/kfd is not used."
            )
            return
        if not Path("/dev/dxg").exists():
            raise RuntimeError(
                "Missing /dev/dxg. Update WSL and the Windows AMD graphics driver, run `wsl --shutdown`, "
                "then start the distribution again. Do not install an amdgpu DKMS driver inside WSL."
            )
        if "VEN_1002" not in windows_display_devices().upper():
            raise RuntimeError("WSL exposes /dev/dxg, but no AMD display adapter was reported by the Windows host.")
        return
    if not supports_gfx1151_kernel(platform.release()):
        raise RuntimeError(
            f"Kernel {platform.release()} lacks the required gfx1151 KFD fixes. "
            "Use Ubuntu 24.04 OEM 6.14.0-1018+, HWE 6.17.0-19+, Ubuntu 26.04, "
            "or another distribution with kernel 6.18.4+. " + RYZEN_AI_GUIDE
        )
    if dry_run:
        print("Ryzen AI Max+ 395 prerequisite: expose /dev/kfd and /dev/dri/renderD* to this environment.")
        return
    if not Path("/dev/kfd").exists():
        raise RuntimeError(
            "Missing /dev/kfd. Install or enable the AMD kernel driver; containers must receive --device=/dev/kfd."
        )
    if not any(Path("/dev/dri").glob("renderD*")):
        raise RuntimeError(
            "No DRM render device is available. Containers must receive --device=/dev/dri and the render/video groups."
        )


def torch_install_args(backend: str, system: str, python_version: tuple[int, int], args) -> list[str]:
    if backend == "npu":
        if system != "Linux":
            raise ValueError("Ascend installation requires a supported Linux host. " + NPU_GUIDE)
        packages = [
            line.strip()
            for line in (ROOT / "requirements/npu.txt").read_text().splitlines()
            if line.startswith(("torch==", "torchvision==", "torchaudio=="))
        ]
        return [*packages, "--index-url", PYTORCH_INDEX + "cpu"]
    if system not in {"Linux", "Windows"}:
        raise ValueError("This installer currently supports Windows and Linux.")
    if args.torch_index_url:
        return ["torch", "torchvision", "torchaudio", "--index-url", args.torch_index_url]
    if backend == "rocm" and args.rocm_profile == "aimax395":
        if system not in {"Linux", "Windows"}:
            raise ValueError("The Ryzen AI Max+ 395 training profile requires Windows 11 or Linux.")
        if not (3, 11) <= python_version <= (3, 14):
            raise ValueError("The Ryzen AI Max+ 395 ROCm 10.1 profile requires Python 3.11 through 3.14.")
        packages = [*RYZEN_AI_MAX_PACKAGES]
        if system == "Windows":
            packages.append(RYZEN_AI_MAX_WINDOWS_SDK)
        else:
            packages.append(RYZEN_AI_MAX_LINUX_SDK)
        return [*packages, "--index-url", AMD_ROCM_NEXT_INDEX]
    if backend == "rocm" and system == "Windows":
        if python_version != (3, 12):
            raise ValueError(
                "The AMD Windows 7.2.1 profile requires Python 3.12. Use a Python 3.12 virtual environment."
            )
        wheels = [
            "rocm_sdk_core-7.2.1-py3-none-win_amd64.whl",
            "rocm_sdk_devel-7.2.1-py3-none-win_amd64.whl",
            "rocm_sdk_libraries_custom-7.2.1-py3-none-win_amd64.whl",
            "torch-2.9.1%2Brocm7.2.1-cp312-cp312-win_amd64.whl",
            "torchvision-0.24.1%2Brocm7.2.1-cp312-cp312-win_amd64.whl",
            "torchaudio-2.9.1%2Brocm7.2.1-cp312-cp312-win_amd64.whl",
        ]
        return [AMD_WINDOWS + wheel for wheel in wheels]
    index = {"cuda": args.cuda_index, "rocm": args.rocm_index, "xpu": "xpu", "cpu": "cpu"}[backend]
    packages = ["torch", "torchvision", "torchaudio"]
    if backend == "xpu":
        packages = ["torch==2.13.0", "torchvision==0.28.0", "torchaudio==2.11.0"]
    return [*packages, "--index-url", PYTORCH_INDEX + index]


def run(command: list[str], *, dry_run: bool = False, check: bool = True) -> bool:
    print("+ " + subprocess.list2cmdline(command), flush=True)
    if dry_run:
        return True
    result = run_logged(command, ROOT) if os.getenv("LLAMAFACTORY_SESSION_LOG") else subprocess.run(command, cwd=ROOT)
    if check and result.returncode:
        raise RuntimeError(f"Command failed (exit {result.returncode}); see the output above.")
    return result.returncode == 0


def select_webui_host(mode: str, *, interactive: bool | None = None, input_fn=None) -> str:
    """Resolve local-only or network-visible WebUI binding without weakening non-interactive defaults."""
    if mode == "local":
        return "127.0.0.1"
    if mode == "network":
        return "0.0.0.0"
    if interactive is None:
        interactive = sys.stdin.isatty()
    if not interactive:
        print(
            "Non-interactive launch defaults to local-only access. Use --host-mode network for Jupyter or LAN access."
        )
        return "127.0.0.1"

    read_choice = input if input_fn is None else input_fn
    print("Select WebUI access mode:")
    print("  1) Local only (127.0.0.1)")
    print("  2) Network / Jupyter (0.0.0.0)")
    while True:
        try:
            choice = read_choice("Choice [1]: ").strip().lower()
        except EOFError:
            choice = "1"
        if choice in {"", "1", "local"}:
            return "127.0.0.1"
        if choice in {"2", "network", "jupyter"}:
            return "0.0.0.0"
        print("Enter 1 for local-only access or 2 for network/Jupyter access.")


def resolve_webui_host(host_mode: str, *, interactive: bool | None = None, input_fn=None) -> str:
    """Honor explicit environment overrides before selecting a deployment mode."""
    explicit_host = os.getenv("GRADIO_SERVER_NAME", "").strip() or os.getenv("WEBUI_HOST", "").strip()
    return explicit_host or select_webui_host(host_mode, interactive=interactive, input_fn=input_fn)


def configure_service_hosts(webui_host: str) -> None:
    """Apply the selected exposure mode to WebUI and TensorBoard unless explicitly overridden."""
    os.environ["GRADIO_SERVER_NAME"] = webui_host
    tensorboard_host = os.getenv("TENSORBOARD_HOST", "").strip()
    os.environ["TENSORBOARD_HOST"] = tensorboard_host or webui_host


def configure_kernel_cache(directory: Path, *, create: bool = True) -> Path:
    """Keep Triton JIT products across the installer probe and subsequent WebUI training processes."""
    cache = Path(os.getenv("TRITON_CACHE_DIR", str(directory / ".triton-cache"))).resolve()
    if create:
        cache.mkdir(parents=True, exist_ok=True)
    os.environ["TRITON_CACHE_DIR"] = str(cache)
    return cache


def launch_webui(python: Path) -> None:
    """Replace the bootstrap process so Ctrl+C reaches the WebUI directly."""
    command = [str(python), "-m", "llamafactory.cli", "webui"]
    print("+ " + subprocess.list2cmdline(command), flush=True)
    os.execv(str(python), command)


def configure_cann(args) -> None:
    """Install user-supplied official packages and load their environment without editing shell profiles."""
    if platform.system() != "Linux":
        raise ValueError("CANN requires a supported Linux host. " + NPU_GUIDE)
    if not capture(["npu-smi", "info"]):
        raise RuntimeError("Ascend driver/firmware is unavailable (npu-smi failed). " + NPU_GUIDE)
    for installer in args.cann_installer:
        package = Path(installer).resolve(strict=True)
        run(["bash", str(package), "--install"])
    candidates = (
        [Path(args.cann_env)]
        if args.cann_env
        else [
            Path("/usr/local/Ascend/ascend-toolkit/set_env.sh"),
            Path.home() / "Ascend/ascend-toolkit/set_env.sh",
        ]
    )
    script = next((path for path in candidates if path.is_file()), None)
    if script is None:
        raise RuntimeError(
            "CANN environment script not found. Supply --cann-installer and/or --cann-env. " + NPU_GUIDE
        )
    result = subprocess.run(
        ["bash", "-c", 'source "$1" >&2 && env -0', "cann-env", str(script)],
        capture_output=True,
        check=True,
    )
    for entry in result.stdout.decode("utf-8", errors="replace").split("\0"):
        if "=" in entry:
            name, value = entry.split("=", 1)
            os.environ[name] = value


def hardware_constraints(versions: dict[str, str]) -> str:
    providers = ("triton-xpu", "pytorch-triton-xpu", "pytorch-triton-rocm", "triton-ascend", "triton-windows")
    names = {"torch", "torchvision", "torchaudio", "torch-npu", "triton", *providers}
    lines = [
        f"{name}=={value}"
        for name, value in sorted(versions.items())
        if name in names or name.startswith(("intel-", "rocm-", "nvidia-"))
    ]
    # Triton providers share an import namespace; never overwrite XPU/Ascend Triton with CUDA Triton.
    if any(name in versions for name in providers) and "triton" not in versions:
        lines.append("triton===0")
    return "\n".join(lines) + "\n"


def install_liger(python: Path, constraints: Path, mode: str, backend: str) -> None:
    if mode == "off" or backend == "cpu" or os.getenv("LLAMAFACTORY_LIGER") == "off":
        os.environ["LLAMAFACTORY_LIGER"] = "off"
        return
    if platform.system() == "Windows" and backend in {"cuda", "xpu", "rocm"}:
        command = [
            str(python),
            "-X",
            "utf8",
            str(ROOT / "scripts/install_windows_liger.py"),
            "--backend",
            backend,
            "--constraints",
            str(constraints),
        ]
        if not run(command, check=False):
            if mode == "required":
                raise RuntimeError("Windows Liger provider installation failed; see diagnostics above.")
            print("Windows Liger is unavailable; continuing with standard training.")
            os.environ["LLAMAFACTORY_LIGER"] = "off"
        return
    command = [
        str(python),
        "-m",
        "pip",
        "install",
        "-c",
        str(constraints),
        "-r",
        str(ROOT / "requirements/liger-kernel.txt"),
    ]
    if not run([*command, "--dry-run"], check=False) or not run(command, check=False):
        if mode == "required":
            raise RuntimeError("Liger cannot be installed with the selected hardware dependencies.")
        print("Liger installation is incompatible or unavailable; continuing with standard training.")
        os.environ["LLAMAFACTORY_LIGER"] = "off"


def verify_environment(
    python: Path,
    backend: str,
    liger: str,
    expected_arch: str | None = None,
    *,
    require_all_capabilities: bool = False,
) -> None:
    run([str(python), "-m", "pip", "check"])
    command = [
        str(python),
        "-X",
        "utf8",
        str(ROOT / "scripts/check_training_environment.py"),
        "--backend",
        backend,
        "--liger",
        liger,
    ]
    if expected_arch:
        command.extend(["--expected-arch", expected_arch])
    if require_all_capabilities:
        command.append("--require-all-capabilities")
    run(command)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", choices=BACKENDS, default=os.getenv("TRAINING_BACKEND", "auto"))
    parser.add_argument("--venv", type=Path, default=Path(os.getenv("VENV_DIR", str(ROOT / ".venv"))))
    parser.add_argument("--dry-run", action="store_true", help="Print the plan without changing an environment.")
    parser.add_argument("--check-only", action="store_true", help="Verify without installing or starting.")
    parser.add_argument("--skip-install", action="store_true", default=os.getenv("SKIP_INSTALL") == "1")
    parser.add_argument("--no-start", action="store_true")
    parser.add_argument(
        "--host-mode",
        choices=HOST_MODES,
        default=os.getenv("WEBUI_HOST_MODE", "ask"),
        help="Choose interactively, bind locally, or bind to all interfaces for Jupyter/LAN access.",
    )
    parser.add_argument("--liger", choices=("auto", "off", "required"), default="auto")
    parser.add_argument(
        "--require-all-capabilities",
        action="store_true",
        help="Require media extensions, bitsandbytes, and Liger runtime probes to pass.",
    )
    parser.add_argument(
        "--torch-index-url", help="Override the backend index with an explicitly chosen compatible build."
    )
    parser.add_argument("--cuda-index", default="cu128")
    parser.add_argument("--rocm-index", default="rocm6.4")
    parser.add_argument(
        "--rocm-profile",
        choices=ROCM_PROFILES,
        default=os.getenv("ROCM_PROFILE", "generic"),
        help="Use the generic PyTorch index or the official Ryzen AI Max+ 395 gfx1151 package set.",
    )
    parser.add_argument(
        "--cann-installer",
        action="append",
        default=[],
        help="Local official Toolkit/ops .run package; repeat in installation order.",
    )
    parser.add_argument("--cann-env", help="Path to CANN set_env.sh.")
    return parser.parse_args(argv)


def main(argv=None) -> None:
    args = parse_args(argv)
    if args.require_all_capabilities:
        args.liger = "required"
    if args.check_only and args.cann_installer:
        raise ValueError("--check-only cannot be combined with --cann-installer.")
    if sys.version_info < (3, 11):  # noqa: UP036 - the bootstrap also runs before the project is installed.
        raise ValueError("Python 3.11 or newer is required; Python 3.12 is recommended.")
    os.environ["PYTHONUTF8"] = "1"
    webui_host = None
    if not args.no_start and not args.check_only:
        webui_host = resolve_webui_host(args.host_mode, interactive=False if args.dry_run else None)
    os.environ["LLAMAFACTORY_LIGER"] = args.liger
    os.environ["PYTHONUNBUFFERED"] = "1"
    wsl_rocm = is_wsl() and args.rocm_profile == "aimax395" and args.backend in {"auto", "rocm"}
    if wsl_rocm:
        os.environ.setdefault("HSA_ENABLE_DXG_DETECTION", "1")
        os.environ.setdefault("NCCL_PROTO", "LL128,Simple")
    directory = args.venv.resolve()
    python = venv_python(directory)
    kernel_cache = configure_kernel_cache(
        directory,
        create=not args.dry_run and (python.exists() or not args.check_only),
    )
    foreign_python = directory / ("bin/python" if os.name == "nt" else "Scripts/python.exe")
    if not python.exists() and foreign_python.exists():
        raise ValueError("Virtual environment belongs to another OS. Choose --venv .venv-linux or .venv-windows.")
    windows_rocm_sdk = (
        platform.system() == "Windows"
        and args.rocm_profile == "aimax395"
        and args.backend
        in {
            "auto",
            "rocm",
        }
    )
    slow_rocm_runtime = windows_rocm_sdk or wsl_rocm
    if python.exists():
        prepend_executable_directory(python)
        if windows_rocm_sdk and python_module_exists(python, "rocm_sdk"):
            initialize_windows_rocm_sdk(python)
    # CANN environment is needed even to import an already installed torch_npu.
    if args.backend == "npu" and not args.dry_run:
        configure_cann(args)
    runtime = inspect_runtime(python, timeout=300 if slow_rocm_runtime else 30)
    detected = detect_backends()
    backend = choose_backend(args.backend, detected, runtime.get("backend"))
    print(f"Detected: {', '.join(sorted(detected)) or 'CPU only'}; selected: {backend}; environment: {directory}")
    print(
        f"Triton cache: {kernel_cache}; Liger probe timeout: {os.getenv('LLAMAFACTORY_LIGER_PROBE_TIMEOUT', '300')}s"
    )
    if len(detected) > 1:
        print("Multiple accelerators detected. Use --backend to override this selection.")
    if args.rocm_profile == "aimax395":
        if backend != "rocm":
            raise ValueError("--rocm-profile aimax395 requires --backend rocm or a detected ROCm device.")
        validate_ryzen_ai_max_host(dry_run=args.dry_run)
        print("ROCm profile: Ryzen AI Max+ 395 (gfx1151), ROCm 10.1, PyTorch 2.14.")
    if backend == "npu":
        if args.dry_run:
            print("Prerequisite: Ascend Linux HDK, CANN Toolkit and ops. " + NPU_GUIDE)
        elif args.backend != "npu":
            configure_cann(args)
            runtime = inspect_runtime(python)
    installed_backend = runtime.get("build_backend") or runtime.get("backend")
    if installed_backend not in {None, backend}:
        raise ValueError(
            f"Existing environment uses {installed_backend}. Choose a new --venv directory for {backend}."
        )
    if backend == "xpu":
        os.environ.setdefault("UR_L0_ENABLE_RELAXED_ALLOCATION_LIMITS", "1")
    install = not args.skip_install and not args.check_only
    torch_args = torch_install_args(backend, platform.system(), sys.version_info[:2], args) if not runtime else []
    if args.dry_run:
        if not python.exists():
            run([sys.executable, "-m", "venv", str(directory)], dry_run=True)
        if install:
            if torch_args:
                run([str(python), "-m", "pip", "install", *torch_args], dry_run=True)
                if backend == "npu":
                    run([str(python), "-m", "pip", "install", "-r", "requirements/npu.txt"], dry_run=True)
                if windows_rocm_sdk:
                    initialize_windows_rocm_sdk(python, dry_run=True)
            else:
                print("Preserve installed hardware runtime; constrain subsequent dependency resolution.")
            run([str(python), "-m", "pip", "install", "-e", ".", "-c", "<hardware-constraints>"], dry_run=True)
            run(
                [
                    str(python),
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    "requirements/metrics.txt",
                    "-c",
                    "<hardware-constraints>",
                ],
                dry_run=True,
            )
            print(f"Liger: {args.liger}; resolve against hardware constraints and check kernels before enabling.")
            if platform.system() == "Windows":
                print(
                    "Windows: preserve XPU Triton, or match triton-windows to Torch for CUDA/ROCm; "
                    "adapt reviewed Liger wheel dependency metadata, then verify real kernels."
                )
        print("Verify pip dependencies, device backward, bitsandbytes, TensorBoard and optional Liger.")
        if not args.no_start and not args.check_only:
            print(f"WebUI bind address: {webui_host}")
            run([str(python), "-m", "llamafactory.cli", "webui"], dry_run=True)
        return
    if install:
        if not python.exists():
            run([sys.executable, "-m", "venv", str(directory)])
        prepend_executable_directory(python)
        pip = [str(python), "-m", "pip"]
        run([*pip, "install", "--upgrade", "pip", "setuptools", "wheel"])
        if torch_args:
            run([*pip, "install", *torch_args])
            if backend == "npu":
                run([*pip, "install", "-r", "requirements/npu.txt"])
        if windows_rocm_sdk and not initialize_windows_rocm_sdk(python):
            raise RuntimeError("The Windows ROCm SDK could not initialize after installation.")
        runtime = wait_for_runtime(
            python,
            backend,
            attempts=3,
            timeout=300 if slow_rocm_runtime else 90,
        )
        if runtime.get("backend") != backend:
            if windows_rocm_sdk:
                hip_info = python.parent / "hipInfo.exe"
                if hip_info.is_file():
                    run([str(hip_info)], check=False)
            if wsl_rocm:
                devices = windows_display_devices().strip() or "Windows display adapter details unavailable"
                raise RuntimeError(
                    "PyTorch cannot initialize ROCm through WSL /dev/dxg after repeated probes. "
                    "Use a ROCm 10.1-compatible Windows AMD driver, run `wsl --shutdown`, and retry. "
                    "Do not install a Linux amdgpu DKMS driver inside WSL. Host adapters: " + devices
                )
            raise RuntimeError(
                f"PyTorch cannot use {backend} after repeated device probes. "
                "Check the device and driver diagnostics above; no CPU fallback was applied."
            )
        with tempfile.TemporaryDirectory(prefix="llamafactory-install-") as temporary:
            constraints = Path(temporary) / "hardware.txt"
            constraints.write_text(hardware_constraints(runtime["versions"]), encoding="utf-8")
            run([*pip, "install", "-e", ".", "-c", str(constraints)])
            run([*pip, "install", "-r", "requirements/metrics.txt", "-c", str(constraints)])
            if backend == "npu" and args.liger != "off":
                if not run(
                    [*pip, "install", "-r", "requirements/triton_ascend.txt", "-c", str(constraints)], check=False
                ):
                    if args.liger == "required":
                        raise RuntimeError("The required Ascend Triton backend could not be installed.")
                    print("Ascend Triton is unavailable; Liger will stay disabled.")
                    os.environ["LLAMAFACTORY_LIGER"] = "off"
                else:
                    updated = inspect_runtime(python)
                    constraints.write_text(hardware_constraints(updated["versions"]), encoding="utf-8")
            install_liger(python, constraints, args.liger, backend)
    if not python.exists():
        raise ValueError("Environment does not exist. Run without --skip-install/--check-only first.")
    expected_arch = "gfx1151" if args.rocm_profile == "aimax395" else None
    verify_environment(
        python,
        backend,
        args.liger,
        expected_arch,
        require_all_capabilities=args.require_all_capabilities,
    )
    if not args.no_start and not args.check_only:
        configure_service_hosts(webui_host or "127.0.0.1")
        os.environ["GRADIO_SERVER_PORT"] = (
            os.getenv("GRADIO_SERVER_PORT", "").strip() or os.getenv("WEBUI_PORT", "").strip() or "7860"
        )
        print(f"Starting WebUI at http://{os.environ['GRADIO_SERVER_NAME']}:{os.environ['GRADIO_SERVER_PORT']}")
        print(f"TensorBoard will bind to {os.environ['TENSORBOARD_HOST']} when training starts.")
        if os.environ["GRADIO_SERVER_NAME"] == "0.0.0.0":
            print("Open the server IP and port, or use your Jupyter port proxy. Press Ctrl+C to stop the WebUI.")
        launch_webui(python)


if __name__ == "__main__":
    enable_console_log()
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"Installation stopped: {error}", file=sys.stderr)
        sys.exit(1)
