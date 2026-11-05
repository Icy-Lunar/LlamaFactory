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

import json
import subprocess
from types import SimpleNamespace

import pytest

from llamafactory.extras import liger
from llamafactory.webui.runner import _get_acceleration_args


@pytest.fixture(autouse=True)
def clear_probe_cache(monkeypatch):
    monkeypatch.delenv("LLAMAFACTORY_LIGER", raising=False)
    liger.get_liger_status.cache_clear()
    yield
    liger.get_liger_status.cache_clear()


def test_missing_liger_does_not_prevent_training(monkeypatch):
    def missing(name):
        raise liger.metadata.PackageNotFoundError(name)

    monkeypatch.setattr(liger.metadata, "version", missing)
    assert liger.get_liger_status().reason == "missing"
    assert _get_acceleration_args()["enable_liger_kernel"] is False


def test_probe_failure_disables_liger_and_is_cached(monkeypatch):
    calls = []
    monkeypatch.setattr(liger.metadata, "version", lambda _: "0.8.0")
    monkeypatch.setattr(
        liger.subprocess,
        "run",
        lambda *args, **kwargs: (
            calls.append(args)
            or SimpleNamespace(
                returncode=1,
                stdout="",
                stderr="No compatible Triton driver",
            )
        ),
    )
    first = liger.get_liger_status()
    assert first.reason == "runtime" and not first.enabled
    assert liger.get_liger_status() == first
    assert len(calls) == 1


def test_probe_timeout_is_a_fallback_not_a_training_crash(monkeypatch):
    monkeypatch.setattr(liger.metadata, "version", lambda _: "0.8.0")

    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], kwargs["timeout"], stderr="LIGER_STAGE=fused_linear_cross_entropy")

    monkeypatch.setattr(liger.subprocess, "run", timeout)
    status = liger.get_liger_status()
    assert not status.enabled
    assert "300s" in status.detail
    assert "fused_linear_cross_entropy" in status.detail


def test_probe_timeout_is_configurable_and_never_below_one_minute(monkeypatch):
    monkeypatch.setattr(liger.metadata, "version", lambda _: "0.8.0")
    calls = []
    monkeypatch.setattr(
        liger.subprocess,
        "run",
        lambda *args, **kwargs: (
            calls.append(kwargs)
            or SimpleNamespace(returncode=0, stdout='LIGER_PROBE=["apply_liger_kernel_to_llama"]', stderr="")
        ),
    )
    monkeypatch.setenv("LLAMAFACTORY_LIGER_PROBE_TIMEOUT", "120")
    assert liger.get_liger_status().enabled
    assert calls[0]["timeout"] == 120

    liger.get_liger_status.cache_clear()
    monkeypatch.setenv("LLAMAFACTORY_LIGER_PROBE_TIMEOUT", "5")
    assert liger.get_liger_status().enabled
    assert calls[1]["timeout"] == 60


def test_supported_model_and_dtype_are_checked_without_vendor_blacklist(monkeypatch, tmp_path):
    monkeypatch.setattr(liger.metadata, "version", lambda _: "0.8.0")
    commands = []
    monkeypatch.setattr(
        liger.subprocess,
        "run",
        lambda command, **kwargs: (
            commands.append(command)
            or SimpleNamespace(
                returncode=0,
                stdout='LIGER_PROBE=["apply_liger_kernel_to_qwen3"]',
                stderr="",
            )
        ),
    )
    (tmp_path / "config.json").write_text(json.dumps({"model_type": "qwen3"}), encoding="utf-8")
    assert liger.get_local_liger_status(str(tmp_path), "bf16").enabled
    assert commands[0][-1] == "bfloat16"
    assert not liger.get_model_liger_status("unknown", "bfloat16").enabled


def test_all_fallback_messages_are_localized():
    from llamafactory.webui.locales import LIGER_LOCALES

    for lang in ("en", "zh", "ru", "ko", "ja"):
        assert set(LIGER_LOCALES[lang]) == {
            "pending",
            "available",
            "standard",
            "disabled",
            "missing",
            "version",
            "runtime",
            "model",
        }


def test_disabled_liger_removes_memory_discount(monkeypatch, tmp_path):
    from llamafactory.webui.components import train
    from llamafactory.webui.memory import DeviceMemory

    (tmp_path / "model.safetensors").write_bytes(b"0" * 1024)
    (tmp_path / "config.json").write_text(
        json.dumps(
            {
                "hidden_size": 4096,
                "intermediate_size": 14336,
                "num_attention_heads": 32,
                "num_hidden_layers": 32,
                "num_key_value_heads": 8,
                "vocab_size": 128000,
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(train, "get_device_memory_snapshot", lambda: DeviceMemory(24, 24, 1))
    manager = SimpleNamespace(get_elem_by_id=lambda key: key)
    data = {"top.model_path": str(tmp_path), "top.booster": "liger_kernel"}
    monkeypatch.setattr(train, "get_local_liger_status", lambda *args, **kwargs: liger.LigerStatus(True, "available"))
    accelerated = train._assess_training_memory(data, manager)[2]
    monkeypatch.setattr(train, "get_local_liger_status", lambda *args, **kwargs: liger.LigerStatus(False, "runtime"))
    standard = train._assess_training_memory(data, manager)[2]
    assert standard > accelerated
