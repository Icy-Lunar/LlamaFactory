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

from tests import model_fixtures


@pytest.fixture(autouse=True)
def clear_fixture_cache():
    model_fixtures.local_model_path.cache_clear()
    yield
    model_fixtures.local_model_path.cache_clear()


def test_existing_fixture_directory_never_downloads(monkeypatch, tmp_path):
    monkeypatch.setattr(model_fixtures, "snapshot_download", lambda *a, **kw: pytest.fail("Unexpected download"))
    assert model_fixtures.local_model_path(str(tmp_path)) == str(tmp_path.resolve())


@pytest.mark.parametrize("weights", [False, True])
def test_fixture_download_is_explicit_and_bounded(monkeypatch, tmp_path, weights):
    calls = []
    monkeypatch.setattr(model_fixtures, "snapshot_download", lambda *a, **kw: calls.append((a, kw)) or str(tmp_path))
    model = "llamafactory/tiny-random-Llama-3" if weights else "Qwen/Qwen2-VL-2B-Instruct"
    result = model_fixtures.local_model_path(model, weights=weights)
    assert Path(result).is_dir()
    assert len(calls) == 1
    assert calls[0][0] == (model,)
    patterns = calls[0][1]["allow_patterns"]
    assert ("*.safetensors" in patterns) is weights
    assert ("*.bin" in patterns) is weights
    assert "*.json" in patterns


def test_large_weight_download_is_rejected(monkeypatch):
    monkeypatch.setattr(model_fixtures, "snapshot_download", lambda *a, **kw: pytest.fail("Unexpected download"))
    with pytest.raises(ValueError, match="Only tiny test repositories"):
        model_fixtures.local_model_path("Qwen/Qwen2-VL-2B-Instruct")


def test_fixture_arguments_do_not_mutate_original_config(tmp_path):
    original = {"model_name_or_path": str(tmp_path), "template": "llama3", "finetuning_type": "full"}
    prepared = model_fixtures.local_model_args(original)
    assert prepared is not original
    assert prepared == {**original, "model_name_or_path": str(tmp_path.resolve())}
