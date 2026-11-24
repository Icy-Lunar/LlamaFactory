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

import sys
from types import SimpleNamespace

from llamafactory.webui.runner import (
    _configure_accelerator_environment,
    _get_tensorboard_command,
    _get_tensorboard_public_url,
    _get_train_command,
)


def test_train_command_uses_active_python_interpreter():
    config_path = "training args.yaml"

    assert _get_train_command(config_path) == [
        sys.executable,
        "-m",
        "llamafactory.cli",
        "train",
        config_path,
    ]


def test_tensorboard_command_uses_training_output_directory():
    log_dir = "C:/training/output"

    assert _get_tensorboard_command(log_dir, "127.0.0.1", 6006) == [
        sys.executable,
        "-m",
        "tensorboard.main",
        "--logdir",
        log_dir,
        "--host",
        "127.0.0.1",
        "--port",
        "6006",
    ]


def test_tensorboard_public_url_supports_jupyter_proxy_and_explicit_override():
    assert (
        _get_tensorboard_public_url({"JUPYTERHUB_SERVICE_PREFIX": "/user/demo/"}, "0.0.0.0", 6006)
        == "/user/demo/proxy/6006/"
    )
    assert (
        _get_tensorboard_public_url(
            {"TENSORBOARD_PUBLIC_URL": "https://notebook.example/proxy/{port}/"}, "0.0.0.0", 6007
        )
        == "https://notebook.example/proxy/6007/"
    )


def test_tensorboard_public_url_uses_webui_request_host_for_network_mode():
    request = SimpleNamespace(
        headers={"host": "10.20.30.40:7860", "x-forwarded-proto": "https"},
    )
    assert _get_tensorboard_public_url({}, "0.0.0.0", 6006, request) == "https://10.20.30.40:6006"


def test_tensorboard_public_url_keeps_local_binding_local():
    assert _get_tensorboard_public_url({}, "127.0.0.1", 6006) == "http://127.0.0.1:6006"


def test_xpu_training_environment_relaxes_single_allocation_limit(monkeypatch):
    monkeypatch.setattr("llamafactory.webui.runner.is_torch_xpu_available", lambda: True)
    env = {}

    _configure_accelerator_environment(env)

    assert env["UR_L0_ENABLE_RELAXED_ALLOCATION_LIMITS"] == "1"


def test_xpu_training_environment_preserves_explicit_override(monkeypatch):
    monkeypatch.setattr("llamafactory.webui.runner.is_torch_xpu_available", lambda: True)
    env = {"UR_L0_ENABLE_RELAXED_ALLOCATION_LIMITS": "0"}

    _configure_accelerator_environment(env)

    assert env["UR_L0_ENABLE_RELAXED_ALLOCATION_LIMITS"] == "0"
