import json

import pytest

from llamafactory.webui.memory import (
    SAFETY_MARGIN,
    ModelShape,
    _estimate_parameter_count,
    estimate_training_memory,
    get_local_weight_size,
    read_model_shape,
)


def _qwen_shape() -> ModelShape:
    config = {
        "hidden_size": 4096,
        "intermediate_size": 14336,
        "num_attention_heads": 32,
        "num_hidden_layers": 32,
        "num_key_value_heads": 8,
        "tie_word_embeddings": False,
        "vocab_size": 128000,
    }
    parameter_count = _estimate_parameter_count(config, config)
    return ModelShape(
        parameter_count=parameter_count,
        hidden_size=4096,
        num_hidden_layers=32,
        vocab_size=128000,
        num_attention_heads=32,
        num_key_value_heads=8,
        intermediate_size=14336,
        source="config",
        weight_size_bytes=parameter_count * 2,
    )


def _estimate(shape: ModelShape, **overrides):
    kwargs = {
        "finetuning_type": "lora",
        "quantization_bit": "4",
        "compute_type": "bf16",
        "cutoff_len": 2048,
        "batch_size": 2,
        "lora_rank": 8,
        "stage": "sft",
        "deepspeed_stage": "none",
        "offload": False,
        "device_count": 1,
        "booster": "liger_kernel",
    }
    kwargs.update(overrides)
    return estimate_training_memory(shape, **kwargs)


def test_estimate_uses_model_architecture() -> None:
    shape = _qwen_shape()
    assert 7_000_000_000 < shape.parameter_count < 9_000_000_000


def test_estimate_applies_ten_percent_margin() -> None:
    estimate = _estimate(_qwen_shape())
    assert estimate.recommended_gib == round(estimate.estimated_gib * SAFETY_MARGIN, 2)


def test_manual_batch_change_updates_peak_estimate() -> None:
    shape = _qwen_shape()
    default = _estimate(shape, batch_size=2)
    edited = _estimate(shape, batch_size=8)
    assert edited.estimated_gib > default.estimated_gib


def test_zero_three_reduces_full_finetuning_memory_per_device() -> None:
    shape = _qwen_shape()
    single_device = _estimate(
        shape,
        finetuning_type="full",
        quantization_bit="none",
        deepspeed_stage="none",
        device_count=1,
    )
    zero_three = _estimate(
        shape,
        finetuning_type="full",
        quantization_bit="none",
        deepspeed_stage="3",
        device_count=4,
    )
    assert zero_three.estimated_gib < single_device.estimated_gib


def test_read_model_shape_sums_unique_indexed_weight_shards(tmp_path) -> None:
    config = {
        "hidden_size": 16,
        "intermediate_size": 32,
        "num_attention_heads": 4,
        "num_hidden_layers": 2,
        "num_key_value_heads": 2,
        "torch_dtype": "float16",
        "vocab_size": 64,
    }
    (tmp_path / "config.json").write_text(json.dumps(config), encoding="utf-8")
    (tmp_path / "model-00001-of-00002.safetensors").write_bytes(b"a" * 11)
    (tmp_path / "model-00002-of-00002.safetensors").write_bytes(b"b" * 13)
    weight_map = {
        "layer.0.weight": "model-00001-of-00002.safetensors",
        "layer.1.weight": "model-00001-of-00002.safetensors",
        "layer.2.weight": "model-00002-of-00002.safetensors",
    }
    (tmp_path / "model.safetensors.index.json").write_text(json.dumps({"weight_map": weight_map}), encoding="utf-8")

    shape = read_model_shape(str(tmp_path))

    assert shape.source == "local_weights"
    assert shape.weight_size_bytes == 24
    assert shape.weight_file_count == 2
    assert shape.parameter_count == 12
    assert get_local_weight_size(str(tmp_path)) == (24, 2)


def test_read_model_shape_rejects_non_local_model_identifier() -> None:
    with pytest.raises(ValueError, match="local directory"):
        read_model_shape("organization/remote-model")


def test_weight_scan_prefers_safetensors_and_ignores_duplicate_bin_format(tmp_path) -> None:
    (tmp_path / "config.json").write_text("{}", encoding="utf-8")
    (tmp_path / "model.safetensors").write_bytes(b"a" * 17)
    (tmp_path / "pytorch_model.bin").write_bytes(b"b" * 31)
    (tmp_path / "optimizer.pt").write_bytes(b"c" * 53)

    assert get_local_weight_size(str(tmp_path)) == (17, 1)
