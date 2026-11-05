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
from types import ModuleType, SimpleNamespace

import pytest

from llamafactory.hparams import ModelArguments


@pytest.mark.parametrize("finetuning_type", ["lora", "full"])
def test_kt_loading_has_no_removed_inference_selector(monkeypatch, tmp_path, finetuning_type):
    model_args = ModelArguments(model_name_or_path=str(tmp_path), use_kt=True)
    assert not hasattr(model_args, "infer_backend")
    model_args._kt_inference_config = {"kt_model_max_length": 2048}
    captured = {}
    handle = object()
    integration = ModuleType("transformers.integrations.kt")

    def configure_kt(config):
        captured.update(config)
        return handle

    integration.configure_kt = configure_kt
    monkeypatch.setitem(sys.modules, integration.__name__, integration)
    model_args.configure_kt_loading(SimpleNamespace(finetuning_type=finetuning_type, lora_rank=8), 4096)

    assert model_args._kt_config_handle is handle
    assert captured["kt_train_mode"] == finetuning_type
    assert captured["kt_full_weight_grad"] is (finetuning_type == "full")
    assert captured["kt_model_max_length"] == 4096
    assert captured["kt_lora_rank"] == 8


def test_kt_loading_without_optional_integration_fails_clearly(monkeypatch, tmp_path):
    monkeypatch.setitem(sys.modules, "transformers.integrations.kt", None)
    model_args = ModelArguments(model_name_or_path=str(tmp_path), use_kt=True)
    with pytest.raises(RuntimeError, match="does not provide `configure_kt"):
        model_args.configure_kt_loading(SimpleNamespace(finetuning_type="lora"), 4096)


def test_disabled_kt_does_not_import_integration_and_rejects_orphan_config(monkeypatch, tmp_path):
    monkeypatch.setitem(sys.modules, "transformers.integrations.kt", None)
    model_args = ModelArguments(model_name_or_path=str(tmp_path))
    model_args.configure_kt_loading(SimpleNamespace(finetuning_type="lora"), 4096)
    assert model_args._kt_config_handle is None
    model_args._kt_inference_config = {}
    with pytest.raises(ValueError, match="requires `use_kt: true`"):
        model_args.configure_kt_loading(SimpleNamespace(finetuning_type="lora"), 4096)
