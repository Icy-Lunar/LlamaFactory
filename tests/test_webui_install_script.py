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

import pytest

from scripts import bootstrap_webui as installer


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_one_click_script_installs_required_dependency_sets_and_starts_webui():
    script = (PROJECT_ROOT / "start_webui.sh").read_text(encoding="utf-8")

    assert 'scripts/bootstrap_webui.py "$@"' in script
    assert "import bitsandbytes, gradio, liger_kernel" not in script


def test_aimax395_one_click_script_uses_isolated_official_rocm_profile():
    script = (PROJECT_ROOT / "start_aimax395.sh").read_text(encoding="utf-8")
    assert ".venv-aimax395" in script
    assert ".venv-aimax395-wsl" in script
    assert "HSA_ENABLE_DXG_DETECTION" in script
    assert "--backend rocm" in script
    assert "--rocm-profile aimax395" in script
    assert '"$@"' in script

    windows_script = (PROJECT_ROOT / "start_aimax395.ps1").read_text(encoding="utf-8")
    assert ".venv-aimax395-windows" in windows_script
    assert "--backend rocm" in windows_script
    assert "--rocm-profile aimax395" in windows_script
    assert "-3.12" in windows_script
    assert "Get-Command py" in windows_script


def test_multibackend_one_click_entrypoints_are_present_and_forward_arguments():
    powershell = (PROJECT_ROOT / "start_multibackend.ps1").read_text(encoding="utf-8")
    shell = (PROJECT_ROOT / "start_multibackend.sh").read_text(encoding="utf-8")
    cmd = (PROJECT_ROOT / "start_multibackend.cmd").read_text(encoding="utf-8")
    assert "bootstrap_multibackend.py" in powershell
    assert "@args" in powershell
    assert '"$@"' in shell
    assert "-Verb RunAs" in cmd
    assert "start_wizard.ps1" in cmd
    assert "start_wizard.ps1" in powershell
    assert "terminal_wizard.py" in shell


def test_release_launchers_prepare_python_and_forward_to_the_shared_installer():
    windows = (PROJECT_ROOT / "start_windows.bat").read_text(encoding="utf-8")
    windows_bootstrap = (PROJECT_ROOT / "scripts" / "launch_windows.ps1").read_text(encoding="utf-8")
    linux = (PROJECT_ROOT / "start_linux.sh").read_text(encoding="utf-8")

    assert "launch_windows.ps1" in windows
    assert "%*" in windows
    assert "Python.Python.3.12" in windows_bootstrap
    assert "start_multibackend.ps1" in windows_bootstrap
    assert "-Verb RunAs" in windows_bootstrap
    assert "apt-get" in linux
    assert "dnf" in linux
    assert "zypper" in linux
    assert "pacman" in linux
    assert "scripts/terminal_wizard.py" in linux
    assert 'scripts/bootstrap_multibackend.py "$@"' in linux


def test_interactive_wizard_entrypoints_are_present_and_forward_arguments():
    powershell = (PROJECT_ROOT / "start_wizard.ps1").read_text(encoding="utf-8")
    shell = (PROJECT_ROOT / "start_wizard.sh").read_text(encoding="utf-8")
    assert "terminal_wizard.py" in powershell
    assert "@WizardArguments" in powershell
    assert "-Verb RunAs" in powershell
    assert "terminal_wizard.py" in shell
    assert '"$@"' in shell


def test_core_metadata_includes_monitoring_and_quantization_dependencies():
    metadata = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    metrics = (PROJECT_ROOT / "requirements" / "metrics.txt").read_text(encoding="utf-8")

    assert '"tensorboard>=2.14.0,<=2.21.0"' in metadata
    assert '"bitsandbytes>=0.48.0,<=0.50.2"' in metadata
    assert "tensorboard>=2.14.0,<=2.21.0" in metrics


@pytest.mark.parametrize(
    ("mode", "expected"),
    (("local", "127.0.0.1"), ("network", "0.0.0.0")),
)
def test_explicit_webui_host_modes(mode, expected):
    assert installer.select_webui_host(mode, interactive=False) == expected


def test_interactive_webui_host_selection_and_safe_default():
    assert installer.select_webui_host("ask", interactive=True, input_fn=lambda _: "2") == "0.0.0.0"
    assert installer.select_webui_host("ask", interactive=True, input_fn=lambda _: "") == "127.0.0.1"
    assert installer.select_webui_host("ask", interactive=False) == "127.0.0.1"


def test_webui_host_environment_override_takes_priority(monkeypatch):
    monkeypatch.delenv("GRADIO_SERVER_NAME", raising=False)
    monkeypatch.delenv("WEBUI_HOST", raising=False)
    monkeypatch.setenv("WEBUI_HOST", "10.0.0.8")
    assert installer.resolve_webui_host("network", interactive=False) == "10.0.0.8"
    monkeypatch.setenv("GRADIO_SERVER_NAME", "127.0.0.2")
    assert installer.resolve_webui_host("network", interactive=False) == "127.0.0.2"


def test_network_mode_exposes_tensorboard_with_webui(monkeypatch):
    monkeypatch.delenv("TENSORBOARD_HOST", raising=False)
    installer.configure_service_hosts("0.0.0.0")
    assert installer.os.environ["GRADIO_SERVER_NAME"] == "0.0.0.0"
    assert installer.os.environ["TENSORBOARD_HOST"] == "0.0.0.0"


def test_explicit_tensorboard_host_is_preserved(monkeypatch):
    monkeypatch.setenv("TENSORBOARD_HOST", "127.0.0.2")
    installer.configure_service_hosts("0.0.0.0")
    assert installer.os.environ["TENSORBOARD_HOST"] == "127.0.0.2"


def test_webui_launch_replaces_bootstrap_process(monkeypatch, tmp_path):
    captured = {}
    python = tmp_path / "python"

    def fake_execv(executable, command):
        captured.update(executable=executable, command=command)

    monkeypatch.setattr(installer.os, "execv", fake_execv)
    installer.launch_webui(python)

    assert captured == {
        "executable": str(python),
        "command": [str(python), "-m", "llamafactory.cli", "webui"],
    }
