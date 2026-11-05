"""Select CUDA, XPU, or ROCm, prepare the system driver, and launch the matching isolated environment."""

import argparse
import ctypes
import os
import platform
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path


try:
    from .session_logging import enable_console_log, run_logged
except ImportError:
    from session_logging import enable_console_log, run_logged


ROOT = Path(__file__).resolve().parents[1]
BACKENDS = ("auto", "cuda", "xpu", "rocm")
DRIVER_MODES = ("auto", "install", "skip")
HOST_MODES = ("ask", "local", "network")
ROCM_PROFILES = ("auto", "generic", "aimax395")
ROCM_RUNFILE_URL = "https://stable.repo.amd.com/rocm/core/linux-installers/rocm-installer-10.1.0-5.run"


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
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def is_wsl() -> bool:
    if platform.system() != "Linux":
        return False
    for path in (Path("/proc/sys/kernel/osrelease"), Path("/proc/version")):
        try:
            if "microsoft" in path.read_text(encoding="utf-8", errors="replace").lower():
                return True
        except OSError:
            continue
    return False


def windows_gpu_inventory() -> dict[str, list[str]]:
    inventory = {"cuda": [], "xpu": [], "rocm": []}
    source = "Get-CimInstance Win32_VideoController | ForEach-Object { '{0}|{1}' -f $_.Name,$_.PNPDeviceID }"
    for row in capture(["powershell.exe", "-NoProfile", "-Command", source]).splitlines():
        upper = row.upper()
        for vendor, backend in (("VEN_10DE", "cuda"), ("VEN_8086", "xpu"), ("VEN_1002", "rocm")):
            if vendor in upper:
                inventory[backend].append(row.split("|", 1)[0].strip())
    return inventory


def hardware_inventory(system: str | None = None) -> dict[str, list[str]]:
    """Return accelerator names keyed by framework backend without requiring a working compute runtime."""
    system = system or platform.system()
    inventory = {"cuda": [], "xpu": [], "rocm": []}
    if system == "Windows":
        return windows_gpu_inventory()

    if system == "Linux":
        if is_wsl() and Path("/dev/dxg").exists():
            inventory = windows_gpu_inventory()
        vendor_map = {"0x10de": "cuda", "0x8086": "xpu", "0x1002": "rocm"}
        for vendor_file in Path("/sys/class/drm").glob("card[0-9]*/device/vendor"):
            try:
                backend = vendor_map.get(vendor_file.read_text(encoding="utf-8").strip().lower())
                device_name = (vendor_file.parent / "uevent").read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if backend:
                name = device_name.strip() or str(vendor_file.parent)
                if name not in inventory[backend]:
                    inventory[backend].append(name)
        return inventory

    raise ValueError("The unified installer supports Windows and Linux hosts.")


def select_backend(requested: str, inventory: dict[str, list[str]]) -> str:
    if requested != "auto":
        if not inventory.get(requested):
            raise RuntimeError(
                f"No {requested} accelerator was detected. Use an explicit backend only on matching hardware."
            )
        return requested
    detected = [backend for backend in ("cuda", "xpu", "rocm") if inventory.get(backend)]
    if not detected:
        raise RuntimeError("No supported NVIDIA, Intel, or AMD accelerator was detected.")
    if len(detected) > 1:
        names = ", ".join(detected)
        raise RuntimeError(f"Multiple accelerator families were detected ({names}); select one with --backend.")
    return detected[0]


def select_rocm_profile(requested: str, names: list[str]) -> str:
    if requested != "auto":
        return requested
    normalized = " ".join(names).upper()
    if any(marker in normalized for marker in ("RYZEN AI MAX", "RADEON(TM) 8060S", "RADEON 8060S", "GFX1151")):
        return "aimax395"
    return "generic"


def environment_python(directory: Path, system: str) -> Path:
    return directory / ("Scripts/python.exe" if system == "windows" else "bin/python")


def select_environment_directory(backend: str, system: str, rocm_profile: str, *, wsl: bool = False) -> Path:
    """Reuse an existing compatible environment before choosing the canonical new location."""
    system = system.lower()
    default = ROOT / f".venv-{backend}-{system}"
    if backend != "rocm" or rocm_profile != "aimax395":
        return default

    if system == "windows":
        environment_name = ".venv-aimax395-windows"
    elif wsl:
        environment_name = ".venv-aimax395-wsl"
    else:
        environment_name = ".venv-aimax395"
    dedicated = ROOT / environment_name
    for candidate in (dedicated, default):
        if environment_python(candidate, system).is_file():
            return candidate
    return dedicated


def driver_is_ready(backend: str, system: str | None = None) -> bool:
    system = system or platform.system()
    if backend == "cuda":
        return bool(capture(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"]))
    if backend == "xpu":
        if capture(["xpu-smi", "discovery"]):
            return True
        return system == "Windows" or any(Path("/dev/dri").glob("renderD*"))
    if system == "Windows":
        source = (
            "Get-CimInstance Win32_VideoController | "
            "Where-Object {$_.PNPDeviceID -match 'VEN_1002' -and $_.DriverVersion} | "
            "Select-Object -First 1 -ExpandProperty DriverVersion"
        )
        return bool(capture(["powershell.exe", "-NoProfile", "-Command", source]))
    if is_wsl():
        return Path("/dev/dxg").exists() and bool(windows_gpu_inventory().get(backend))
    return Path("/dev/kfd").exists() and any(Path("/dev/dri").glob("renderD*"))


def is_windows_admin() -> bool:
    return bool(ctypes.windll.shell32.IsUserAnAdmin()) if platform.system() == "Windows" else False


def resolve_windows_installer(backend: str, value: str | None) -> Path | None:
    if value:
        candidate = Path(value).expanduser().resolve()
        if not candidate.is_file():
            raise FileNotFoundError(f"Driver installer does not exist: {candidate}")
        return candidate
    patterns = ("*nvidia*.exe", "*cuda*.exe") if backend == "cuda" else ("*amd*.exe", "*radeon*.exe")
    driver_dir = ROOT / "drivers"
    candidates = [path for pattern in patterns for path in driver_dir.glob(pattern)] if driver_dir.is_dir() else []
    return sorted(candidates)[0] if candidates else None


def download_driver(url: str, backend: str, *, dry_run: bool = False) -> Path:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https":
        raise ValueError("Driver downloads require an HTTPS URL from the hardware vendor.")
    suffix = Path(parsed.path).suffix or (".exe" if platform.system() == "Windows" else ".run")
    destination = ROOT / ".driver-cache" / f"{backend}-driver{suffix}"
    print(f"Download official driver: {url} -> {destination}")
    if not dry_run:
        destination.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, destination)  # noqa: S310 - HTTPS is required above.
    return destination


def run(command: list[str], *, dry_run: bool = False, success_codes: set[int] | None = None) -> int:
    print("+ " + subprocess.list2cmdline(command), flush=True)
    if dry_run:
        return 0
    result = run_logged(command, ROOT) if os.getenv("LLAMAFACTORY_SESSION_LOG") else subprocess.run(command, cwd=ROOT)
    accepted = success_codes or {0}
    if result.returncode not in accepted:
        raise RuntimeError(f"Command failed with exit code {result.returncode}; see the output above.")
    return result.returncode


def install_windows_driver(backend: str, installer: Path, *, dry_run: bool = False) -> None:
    if not dry_run and not is_windows_admin():
        raise PermissionError("System driver installation requires an elevated PowerShell window.")
    log_dir = ROOT / "logs" / "driver-install"
    if not dry_run:
        log_dir.mkdir(parents=True, exist_ok=True)
    if backend == "cuda":
        command = [
            str(installer),
            "-s",
            "-n",
            "Display.Driver",
            f"-log:{log_dir}",
            "-loglevel:6",
        ]
        run(command, dry_run=dry_run, success_codes={0, 1})
    elif backend == "rocm":
        run([str(installer), "-INSTALL", "-OUTPUT", "screen"], dry_run=dry_run, success_codes={0, 1, 3010})
    else:
        raise ValueError("Automatic Windows system-driver execution is limited to CUDA and ROCm.")


def sudo_prefix() -> list[str]:
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        return []
    run(["sudo", "-v"])
    return ["sudo"]


def install_ubuntu_driver(backend: str, rocm_profile: str, *, dry_run: bool = False) -> None:
    if not Path("/etc/os-release").is_file() or "ubuntu" not in Path("/etc/os-release").read_text().lower():
        raise RuntimeError("Automatic Linux driver installation is restricted to supported Ubuntu releases.")
    if is_wsl():
        raise RuntimeError(
            "WSL GPU drivers must be installed on the Windows host. Do not install Linux CUDA or amdgpu DKMS "
            "drivers inside WSL; update the Windows driver and run `wsl --shutdown` instead."
        )
    prefix = [] if dry_run else sudo_prefix()
    if backend == "cuda":
        run([*prefix, "apt-get", "update"], dry_run=dry_run)
        run(
            [
                *prefix,
                "apt-get",
                "install",
                "-y",
                f"linux-headers-{platform.release()}",
                "ubuntu-drivers-common",
            ],
            dry_run=dry_run,
        )
        run([*prefix, "ubuntu-drivers", "install", "--gpgpu"], dry_run=dry_run)
        return
    if backend == "rocm":
        if rocm_profile == "aimax395":
            raise RuntimeError(
                "Ryzen AI Max APUs use Ubuntu's inbox amdgpu driver. Install a supported Ubuntu kernel instead of "
                "running the discrete-GPU amdgpu installer."
            )
        run([*prefix, "apt-get", "update"], dry_run=dry_run)
        run([*prefix, "apt-get", "install", "-y", "wget", "python3", "perl"], dry_run=dry_run)
        installer = download_driver(ROCM_RUNFILE_URL, backend, dry_run=dry_run)
        run([*prefix, "bash", str(installer), "deps=install", "amdgpu"], dry_run=dry_run)
        return
    raise ValueError("XPU system drivers are validated but not changed automatically by this installer.")


def prepare_system_driver(
    backend: str,
    mode: str,
    rocm_profile: str,
    installer_value: str | None,
    driver_url: str | None,
    *,
    dry_run: bool = False,
) -> bool:
    ready = driver_is_ready(backend)
    if mode == "skip" or mode == "auto" and ready:
        print(f"System driver for {backend}: {'ready' if ready else 'verification skipped'}.", flush=True)
        return False
    if backend == "xpu":
        if not ready:
            raise RuntimeError(
                "Install a supported Intel graphics/compute driver, reboot, and run this command again."
            )
        return False
    if platform.system() == "Windows":
        installer = download_driver(driver_url, backend, dry_run=dry_run) if driver_url else None
        installer = installer or resolve_windows_installer(backend, installer_value)
        if installer is None:
            raise RuntimeError(
                f"Place an official {backend} Windows driver installer in the drivers directory, or pass "
                "--driver-installer/--driver-url."
            )
        install_windows_driver(backend, installer, dry_run=dry_run)
    elif platform.system() == "Linux":
        install_ubuntu_driver(backend, rocm_profile, dry_run=dry_run)
    else:
        raise RuntimeError("Automatic system-driver installation supports Windows and Ubuntu only.")
    return not dry_run


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", choices=BACKENDS, default="auto")
    parser.add_argument("--driver-mode", choices=DRIVER_MODES, default="auto")
    parser.add_argument("--driver-installer")
    parser.add_argument("--driver-url")
    parser.add_argument("--rocm-profile", choices=ROCM_PROFILES, default="auto")
    parser.add_argument("--host-mode", choices=HOST_MODES, default="ask")
    parser.add_argument("--liger", choices=("auto", "off", "required"), default="auto")
    parser.add_argument("--require-all-capabilities", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-start", action="store_true")
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--skip-install", action="store_true")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    inventory = hardware_inventory()
    backend = select_backend(args.backend, inventory)
    rocm_profile = select_rocm_profile(args.rocm_profile, inventory["rocm"])
    devices = ", ".join(inventory[backend])
    print(f"Selected backend: {backend}; detected devices: {devices}", flush=True)
    if backend == "rocm":
        print(f"Selected ROCm profile: {rocm_profile}", flush=True)
    installed_driver = prepare_system_driver(
        backend,
        args.driver_mode,
        rocm_profile,
        args.driver_installer,
        args.driver_url,
        dry_run=args.dry_run,
    )
    if installed_driver:
        print("System driver installation completed. Reboot the host, then run the same command again.")
        return 10

    system_name = platform.system().lower()
    venv = select_environment_directory(backend, system_name, rocm_profile, wsl=is_wsl())
    print(f"Selected environment: {venv}", flush=True)
    command = [
        sys.executable,
        "-X",
        "utf8",
        str(ROOT / "scripts/bootstrap_webui.py"),
        "--backend",
        backend,
        "--venv",
        str(venv),
        "--host-mode",
        args.host_mode,
        "--liger",
        args.liger,
    ]
    if backend == "rocm":
        command.extend(["--rocm-profile", rocm_profile])
    for enabled, option in (
        (args.dry_run, "--dry-run"),
        (args.no_start, "--no-start"),
        (args.check_only, "--check-only"),
        (args.skip_install, "--skip-install"),
        (args.require_all_capabilities, "--require-all-capabilities"),
    ):
        if enabled:
            command.append(option)
    result = run_logged(command, ROOT) if os.getenv("LLAMAFACTORY_SESSION_LOG") else subprocess.run(command, cwd=ROOT)
    return result.returncode


if __name__ == "__main__":
    enable_console_log()
    try:
        raise SystemExit(main())
    except (FileNotFoundError, OSError, PermissionError, RuntimeError, ValueError) as error:
        print(f"Unified installation stopped: {error}", file=sys.stderr)
        raise SystemExit(1) from None
