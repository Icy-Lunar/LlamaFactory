# Copyright 2026 the LlamaFactory team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import bootstrap_multibackend as unified


def test_windows_inventory_maps_physical_gpu_vendors(monkeypatch):
    output = "\n".join(
        [
            "NVIDIA RTX 5090|PCI\\VEN_10DE&DEV_2B85",
            "Intel Arc Graphics|PCI\\VEN_8086&DEV_E20B",
            "AMD Radeon(TM) 8060S Graphics|PCI\\VEN_1002&DEV_1586",
        ]
    )
    monkeypatch.setattr(unified, "capture", lambda command, timeout=30: output)
    assert unified.hardware_inventory("Windows") == {
        "cuda": ["NVIDIA RTX 5090"],
        "xpu": ["Intel Arc Graphics"],
        "rocm": ["AMD Radeon(TM) 8060S Graphics"],
    }


def test_wsl_inventory_uses_windows_host_gpu(monkeypatch):
    monkeypatch.setattr(unified, "is_wsl", lambda: True)
    monkeypatch.setattr(
        unified.Path,
        "exists",
        lambda path: str(path).replace("\\", "/") == "/dev/dxg",
    )
    monkeypatch.setattr(unified.Path, "glob", lambda *args, **kwargs: [])
    monkeypatch.setattr(
        unified,
        "capture",
        lambda command, timeout=30: "AMD Radeon(TM) 8060S Graphics|PCI\\VEN_1002&DEV_150E",
    )
    assert unified.hardware_inventory("Linux")["rocm"] == ["AMD Radeon(TM) 8060S Graphics"]


def test_auto_backend_requires_choice_when_multiple_families_exist():
    inventory = {"cuda": ["NVIDIA"], "xpu": [], "rocm": ["AMD"]}
    with pytest.raises(RuntimeError, match="Multiple accelerator"):
        unified.select_backend("auto", inventory)
    assert unified.select_backend("rocm", inventory) == "rocm"


def test_gfx1151_windows_device_selects_current_rocm_profile():
    assert unified.select_rocm_profile("auto", ["AMD Radeon(TM) 8060S Graphics"]) == "aimax395"
    assert unified.select_rocm_profile("auto", ["AMD Radeon RX 7900 XTX"]) == "generic"


def test_aimax_environment_reuses_dedicated_or_legacy_install(tmp_path, monkeypatch):
    monkeypatch.setattr(unified, "ROOT", tmp_path)
    dedicated = tmp_path / ".venv-aimax395-windows"
    legacy = tmp_path / ".venv-rocm-windows"

    assert unified.select_environment_directory("rocm", "windows", "aimax395") == dedicated
    (legacy / "Scripts").mkdir(parents=True)
    (legacy / "Scripts/python.exe").touch()
    assert unified.select_environment_directory("rocm", "windows", "aimax395") == legacy
    (dedicated / "Scripts").mkdir(parents=True)
    (dedicated / "Scripts/python.exe").touch()
    assert unified.select_environment_directory("rocm", "windows", "aimax395") == dedicated


def test_aimax_wsl_uses_an_isolated_environment(tmp_path, monkeypatch):
    monkeypatch.setattr(unified, "ROOT", tmp_path)
    assert unified.select_environment_directory("rocm", "linux", "aimax395", wsl=True) == (
        tmp_path / ".venv-aimax395-wsl"
    )


def test_windows_driver_execution_uses_vendor_silent_arguments(monkeypatch, tmp_path):
    installer = tmp_path / "vendor.exe"
    installer.write_bytes(b"placeholder")
    calls = []
    monkeypatch.setattr(unified, "is_windows_admin", lambda: True)
    monkeypatch.setattr(unified, "run", lambda command, **kwargs: calls.append((command, kwargs)) or 0)

    unified.install_windows_driver("cuda", installer)
    assert calls[-1][0][1:4] == ["-s", "-n", "Display.Driver"]
    assert calls[-1][1]["success_codes"] == {0, 1}

    unified.install_windows_driver("rocm", installer)
    assert calls[-1][0][1:] == ["-INSTALL", "-OUTPUT", "screen"]
    assert 3010 in calls[-1][1]["success_codes"]


def test_main_uses_backend_specific_environment_and_rocm_profile(monkeypatch):
    inventory = {"cuda": [], "xpu": [], "rocm": ["AMD Radeon(TM) 8060S Graphics"]}
    monkeypatch.setattr(unified, "hardware_inventory", lambda: inventory)
    monkeypatch.setattr(unified, "prepare_system_driver", lambda *args, **kwargs: False)
    calls = []
    monkeypatch.setattr(
        unified.subprocess,
        "run",
        lambda command, **kwargs: calls.append(command) or SimpleNamespace(returncode=0),
    )
    monkeypatch.setattr(unified.platform, "system", lambda: "Windows")

    assert unified.main(["--backend", "rocm", "--no-start", "--liger", "off"]) == 0
    command = calls[-1]
    assert str(Path(".venv-aimax395-windows")) in " ".join(command)
    assert command[command.index("--rocm-profile") + 1] == "aimax395"


def test_driver_install_completion_requires_restart(monkeypatch):
    inventory = {"cuda": ["NVIDIA"], "xpu": [], "rocm": []}
    monkeypatch.setattr(unified, "hardware_inventory", lambda: inventory)
    monkeypatch.setattr(unified, "prepare_system_driver", lambda *args, **kwargs: True)
    assert unified.main(["--backend", "cuda", "--no-start"]) == 10
