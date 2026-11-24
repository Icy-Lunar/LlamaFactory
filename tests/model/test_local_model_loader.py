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

from types import SimpleNamespace

import pytest

from llamafactory.model.loader import _get_init_kwargs
from llamafactory.v1.config.model_args import ModelArguments as V1ModelArguments


def test_model_loader_forces_local_files_only(tmp_path) -> None:
    model_args = SimpleNamespace(model_name_or_path=str(tmp_path), trust_remote_code=False)

    init_kwargs = _get_init_kwargs(model_args)

    assert init_kwargs == {"trust_remote_code": False, "local_files_only": True}
    assert model_args.model_name_or_path == str(tmp_path.resolve())


def test_model_loader_rejects_remote_identifier() -> None:
    model_args = SimpleNamespace(model_name_or_path="organization/remote-model", trust_remote_code=False)

    with pytest.raises(ValueError, match="local model directory"):
        _get_init_kwargs(model_args)


def test_v1_model_arguments_require_local_directory(tmp_path) -> None:
    model_args = V1ModelArguments(model=str(tmp_path))
    assert model_args.model == str(tmp_path.resolve())

    with pytest.raises(ValueError, match="local model directory"):
        V1ModelArguments(model="organization/remote-model")
