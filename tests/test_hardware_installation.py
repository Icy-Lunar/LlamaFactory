from pathlib import Path

import pytest

from scripts import bootstrap_webui as installer
from scripts import check_training_environment as environment_check


@pytest.mark.parametrize(
    ("requested", "detected", "existing", "expected"),
    [
        ("auto", {"xpu"}, None, "xpu"),
        ("auto", {"xpu", "cuda"}, None, "cuda"),
        ("auto", {"xpu", "cuda"}, "xpu", "xpu"),
        ("auto", {"rocm"}, None, "rocm"),
        ("auto", {"npu"}, None, "npu"),
        ("auto", set(), None, "cpu"),
        ("cpu", {"cuda"}, None, "cpu"),
    ],
)
def test_backend_selection(requested, detected, existing, expected):
    assert installer.choose_backend(requested, detected, existing) == expected


def test_windows_detection_uses_display_device_vendor_not_cpu(monkeypatch):
    monkeypatch.setattr(installer.platform, "system", lambda: "Windows")
    monkeypatch.setattr(
        installer, "capture", lambda command: "PCI\\VEN_10DE&DEV_2684" if command[0] == "powershell.exe" else ""
    )
    assert installer.detect_backends() == {"cuda"}


def test_wsl_detection_uses_windows_host_gpu_and_dxg(monkeypatch):
    monkeypatch.setattr(installer.platform, "system", lambda: "Linux")
    monkeypatch.setattr(installer, "is_wsl", lambda: True)
    monkeypatch.setattr(
        installer.Path,
        "exists",
        lambda path: str(path).replace("\\", "/") == "/dev/dxg",
    )
    monkeypatch.setattr(installer.Path, "glob", lambda *args, **kwargs: [])
    monkeypatch.setattr(
        installer,
        "capture",
        lambda command, timeout=30: (
            "AMD Radeon(TM) 8060S|PCI\\VEN_1002&DEV_150E|32.0.31036.15" if command[0] == "powershell.exe" else ""
        ),
    )
    assert installer.detect_backends() == {"rocm"}


@pytest.mark.parametrize(
    ("backend", "index"), [("cuda", "cu128"), ("rocm", "rocm6.4"), ("xpu", "xpu"), ("cpu", "cpu")]
)
def test_torch_backend_install_sources(backend, index):
    args = installer.parse_args([])
    command = installer.torch_install_args(backend, "Linux", (3, 12), args)
    assert command[-2:] == ["--index-url", installer.PYTORCH_INDEX + index]
    assert any(package.startswith("torchvision") for package in command)
    assert any(package.startswith("torchaudio") for package in command)


def test_ascend_installs_cpu_torch_before_device_plugin():
    args = installer.parse_args([])
    command = installer.torch_install_args("npu", "Linux", (3, 12), args)
    assert "torch==2.10.0" in command
    assert command[-1].endswith("/cpu")
    with pytest.raises(ValueError, match="Linux"):
        installer.torch_install_args("npu", "Windows", (3, 12), args)


def test_windows_amd_profile_contains_sdk_and_matching_wheels():
    args = installer.parse_args([])
    command = installer.torch_install_args("rocm", "Windows", (3, 12), args)
    assert len(command) == 6
    assert all(url.startswith(installer.AMD_WINDOWS) for url in command)
    with pytest.raises(ValueError, match="3.12"):
        installer.torch_install_args("rocm", "Windows", (3, 13), args)


def test_ryzen_ai_max_profile_uses_official_gfx1151_packages():
    args = installer.parse_args(["--rocm-profile", "aimax395"])
    for system in ("Linux", "Windows"):
        command = installer.torch_install_args("rocm", system, (3, 12), args)
        expected = list(installer.RYZEN_AI_MAX_PACKAGES)
        if system == "Windows":
            expected.append(installer.RYZEN_AI_MAX_WINDOWS_SDK)
        else:
            expected.append(installer.RYZEN_AI_MAX_LINUX_SDK)
        assert command[:-2] == expected
        assert command[-2:] == ["--index-url", installer.AMD_ROCM_NEXT_INDEX]
        assert "device-gfx1151" in command[0]
    with pytest.raises(ValueError, match="Python 3.11 through 3.14"):
        installer.torch_install_args("rocm", "Linux", (3, 10), args)


def test_ryzen_ai_max_windows_host_requires_windows_11(monkeypatch):
    monkeypatch.setattr(installer.platform, "system", lambda: "Windows")
    monkeypatch.setattr(installer.platform, "machine", lambda: "AMD64")
    monkeypatch.setattr(installer.platform, "release", lambda: "11")
    installer.validate_ryzen_ai_max_host(dry_run=True)
    monkeypatch.setattr(installer.platform, "release", lambda: "10")
    with pytest.raises(ValueError, match="Windows 11"):
        installer.validate_ryzen_ai_max_host(dry_run=True)


def test_ryzen_ai_max_wsl_uses_dxg_instead_of_kfd(monkeypatch):
    monkeypatch.setattr(installer.platform, "system", lambda: "Linux")
    monkeypatch.setattr(installer.platform, "machine", lambda: "x86_64")
    monkeypatch.setattr(installer, "is_wsl", lambda: True)
    monkeypatch.setattr(
        installer.Path,
        "exists",
        lambda path: str(path).replace("\\", "/") == "/dev/dxg",
    )
    monkeypatch.setattr(installer, "windows_display_devices", lambda: "AMD|PCI\\VEN_1002&DEV_150E|driver")
    installer.validate_ryzen_ai_max_host()


@pytest.mark.parametrize(
    ("release", "supported"),
    [
        ("6.14.0-1018-oem", True),
        ("6.14.0-1017-oem", False),
        ("6.17.0-19-generic", True),
        ("6.17.0-18-generic", False),
        ("6.18.4", True),
        ("6.18.3", False),
        ("7.0.0-generic", True),
    ],
)
def test_gfx1151_kernel_requirements(release, supported):
    assert installer.supports_gfx1151_kernel(release) is supported


def test_environment_verification_checks_requested_gpu_architecture(monkeypatch):
    commands = []
    monkeypatch.setattr(installer, "run", lambda command, **kwargs: commands.append(command) or True)
    installer.verify_environment(Path("python"), "rocm", "auto", "gfx1151")
    assert commands[-1][-2:] == ["--expected-arch", "gfx1151"]


def test_strict_environment_verification_requires_all_capabilities(monkeypatch):
    commands = []
    monkeypatch.setattr(installer, "run", lambda command, **kwargs: commands.append(command) or True)
    installer.verify_environment(Path("python"), "rocm", "required", "gfx1151", require_all_capabilities=True)
    assert "--require-all-capabilities" in commands[-1]


def test_hardware_constraints_preserve_xpu_and_block_competing_triton():
    constraints = installer.hardware_constraints(
        {"torch": "2.13.0+xpu", "triton-xpu": "3.7.2", "tensorboard": "2.21.0"}
    )
    assert "torch==2.13.0+xpu" in constraints
    assert "triton-xpu==3.7.2" in constraints
    assert "triton===0" in constraints
    assert "tensorboard" not in constraints


def test_install_plan_keeps_project_and_metrics_and_does_not_mutate(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(installer, "detect_backends", lambda: {"xpu"})
    monkeypatch.setattr(installer, "inspect_runtime", lambda _, **kwargs: {})
    monkeypatch.setattr(installer.platform, "system", lambda: "Windows")
    monkeypatch.setattr(
        installer.subprocess, "run", lambda *args, **kwargs: pytest.fail("Dry run must not execute commands")
    )
    destination = tmp_path / "new-env"
    installer.main(["--dry-run", "--venv", str(destination), "--no-start"])
    output = capsys.readouterr().out
    assert "pip install -e ." in output
    assert "requirements/metrics.txt" in output
    assert "/whl/xpu" in output
    assert not destination.exists()


def test_aimax395_dry_run_prints_complete_official_install_plan(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("TRITON_CACHE_DIR", raising=False)
    monkeypatch.setattr(installer, "detect_backends", lambda: {"rocm"})
    monkeypatch.setattr(installer, "inspect_runtime", lambda _, **kwargs: {})
    monkeypatch.setattr(installer.platform, "system", lambda: "Linux")
    monkeypatch.setattr(installer.platform, "machine", lambda: "x86_64")
    monkeypatch.setattr(installer.platform, "release", lambda: "6.18.4")
    destination = tmp_path / "aimax-env"

    installer.main(
        [
            "--dry-run",
            "--backend",
            "rocm",
            "--rocm-profile",
            "aimax395",
            "--venv",
            str(destination),
            "--no-start",
        ]
    )

    output = capsys.readouterr().out
    assert installer.AMD_ROCM_NEXT_INDEX in output
    assert "torch[device-gfx1151]==2.14.0+rocm10.1.0" in output
    assert "ROCm profile: Ryzen AI Max+ 395" in output
    assert not destination.exists()


def test_triton_cache_is_persistent_and_dry_run_can_avoid_creation(tmp_path, monkeypatch):
    monkeypatch.delenv("TRITON_CACHE_DIR", raising=False)
    destination = tmp_path / "env"
    cache = installer.configure_kernel_cache(destination, create=False)
    assert cache == (destination / ".triton-cache").resolve()
    assert not cache.exists()

    installer.configure_kernel_cache(destination)
    assert cache.is_dir()
    assert installer.os.environ["TRITON_CACHE_DIR"] == str(cache)


def test_existing_runtime_of_different_backend_is_not_replaced(tmp_path, monkeypatch):
    monkeypatch.setattr(installer, "detect_backends", lambda: {"cuda"})
    monkeypatch.setattr(installer, "inspect_runtime", lambda _, **kwargs: {"backend": "xpu"})
    with pytest.raises(ValueError, match="new --venv"):
        installer.main(["--backend", "cuda", "--venv", str(tmp_path), "--dry-run"])


def test_optional_liger_resolution_failure_preserves_training(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(installer.platform, "system", lambda: "Linux")
    monkeypatch.setenv("LLAMAFACTORY_LIGER", "auto")
    monkeypatch.setattr(installer, "run", lambda command, **kwargs: calls.append(command) or False)
    installer.install_liger(Path("python"), tmp_path / "constraints.txt", "auto", "xpu")
    assert len(calls) == 1
    assert "--dry-run" in calls[0]
    assert installer.os.environ["LLAMAFACTORY_LIGER"] == "off"


def test_windows_rocm_sdk_initialization_prefers_environment_executable(tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", installer.os.environ.get("PATH", ""))
    python = tmp_path / "Scripts" / "python.exe"
    sdk = python.parent / "rocm-sdk.exe"
    sdk.parent.mkdir(parents=True)
    sdk.touch()
    commands = []
    monkeypatch.setattr(installer, "run", lambda command, **kwargs: commands.append((command, kwargs)) or True)

    assert installer.initialize_windows_rocm_sdk(python)
    assert commands == [([str(sdk), "init"], {"dry_run": False, "check": False})]
    first_path = installer.os.environ["PATH"].split(installer.os.pathsep)[0]
    assert str(python.parent.resolve()).casefold() == first_path.casefold()


def test_slow_device_runtime_probe_retries_without_falling_back(monkeypatch):
    responses = [{}, {"backend": "cpu"}, {"backend": "rocm"}]
    calls = []

    def inspect(_python, timeout=30):
        calls.append(timeout)
        return responses.pop(0)

    monkeypatch.setattr(installer, "inspect_runtime", inspect)
    monkeypatch.setattr(installer.time, "sleep", lambda _delay: None)

    runtime = installer.wait_for_runtime(Path("python"), "rocm", attempts=3, timeout=300)
    assert runtime == {"backend": "rocm"}
    assert calls == [300, 300, 300]


def test_rocm_architecture_is_read_from_torch_without_external_tools():
    class Properties:
        gcnArchName = "gfx1151:sramecc-:xnack-"

    class Cuda:
        @staticmethod
        def get_device_properties(index):
            assert index == 0
            return Properties()

    class Torch:
        cuda = Cuda()

    assert environment_check.detect_device_architecture(Torch()) == "gfx1151:sramecc-:xnack-"


def test_bitsandbytes_native_load_failure_is_an_optional_degradation(monkeypatch, capsys):
    monkeypatch.setattr(environment_check, "package_version", lambda _: "0.50.2")

    def blocked_import(_):
        raise OSError("application control policy blocked this file")

    monkeypatch.setattr(environment_check.importlib, "import_module", blocked_import)
    version, status = environment_check.check_bitsandbytes(object(), "cuda")

    assert version == "0.50.2"
    assert status.startswith("unavailable:")
    assert "ordinary non-quantized training remains usable" in capsys.readouterr().out


def test_optional_media_extension_load_failure_does_not_block_other_training(monkeypatch, capsys):
    monkeypatch.setattr(environment_check, "package_version", lambda _: "2.14.0")

    def blocked_import(_):
        raise OSError("application control policy blocked libtorchaudio.pyd")

    monkeypatch.setattr(environment_check.importlib, "import_module", blocked_import)
    version, status = environment_check.check_optional_import("torchaudio", "audio preprocessing")

    assert version == "2.14.0"
    assert status.startswith("unavailable:")
    assert "unrelated training modes remain usable" in capsys.readouterr().out
