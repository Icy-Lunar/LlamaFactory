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
