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
from dataclasses import replace
from math import prod
from types import SimpleNamespace

import pytest

from llamafactory.extras.memory_calibration import get_calibration, record_calibration
from llamafactory.train.callbacks import MemoryCalibrationCallback
from llamafactory.webui import memory as memory_module
from llamafactory.webui.memory import (
    SAFETY_MARGIN,
    DeviceMemory,
    ModelShape,
    _estimate_parameter_count,
    estimate_training_memory,
    get_local_weight_size,
    read_model_shape,
    write_memory_estimate_metadata,
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
        "apply_calibration": False,
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


def test_user_quantization_choice_changes_memory_estimate() -> None:
    shape = _qwen_shape()
    unquantized = _estimate(shape, quantization_bit="none")
    four_bit = _estimate(shape, quantization_bit="4")

    assert four_bit.estimated_gib < unquantized.estimated_gib


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


def test_read_model_shape_detects_multimodal_config(tmp_path) -> None:
    config = {
        "model_type": "qwen2_5_vl",
        "text_config": {
            "hidden_size": 16,
            "intermediate_size": 32,
            "num_attention_heads": 4,
            "num_hidden_layers": 2,
            "num_key_value_heads": 2,
            "vocab_size": 64,
        },
        "vision_config": {
            "hidden_size": 24,
            "num_hidden_layers": 3,
        },
        "torch_dtype": "float16",
    }
    (tmp_path / "config.json").write_text(json.dumps(config), encoding="utf-8")
    (tmp_path / "model.safetensors").write_bytes(b"a" * 32)

    shape = read_model_shape(str(tmp_path))

    assert shape.is_multimodal is True
    assert shape.vision_hidden_size == 24
    assert shape.vision_num_hidden_layers == 3


def test_multimodal_freeze_and_pixel_settings_change_memory_estimate() -> None:
    shape = replace(
        _qwen_shape(),
        is_multimodal=True,
        vision_hidden_size=1024,
        vision_num_hidden_layers=24,
    )
    frozen = _estimate(
        shape,
        freeze_vision_tower=True,
        image_max_pixels=224 * 224,
        video_max_pixels=128 * 128,
    )
    trainable_vision = _estimate(
        shape,
        freeze_vision_tower=False,
        image_max_pixels=224 * 224,
        video_max_pixels=128 * 128,
    )
    larger_inputs = _estimate(
        shape,
        freeze_vision_tower=False,
        image_max_pixels=1024 * 1024,
        video_max_pixels=512 * 512,
    )

    assert trainable_vision.estimated_gib > frozen.estimated_gib
    assert larger_inputs.estimated_gib > trainable_vision.estimated_gib


def test_weight_scan_prefers_safetensors_and_ignores_duplicate_bin_format(tmp_path) -> None:
    (tmp_path / "config.json").write_text("{}", encoding="utf-8")
    (tmp_path / "model.safetensors").write_bytes(b"a" * 17)
    (tmp_path / "pytorch_model.bin").write_bytes(b"b" * 31)
    (tmp_path / "optimizer.pt").write_bytes(b"c" * 53)

    assert get_local_weight_size(str(tmp_path)) == (17, 1)


def test_read_model_shape_uses_exact_safetensors_tensor_metadata(tmp_path) -> None:
    config = {
        "hidden_size": 8,
        "intermediate_size": 16,
        "num_attention_heads": 2,
        "num_hidden_layers": 1,
        "num_key_value_heads": 1,
        "torch_dtype": "float16",
        "vocab_size": 16,
    }
    tensors = {
        "model.embed_tokens.weight": {"dtype": "F16", "shape": [16, 8], "data_offsets": [0, 256]},
        "model.layers.0.mlp.weight": {"dtype": "F16", "shape": [8, 8], "data_offsets": [256, 384]},
    }
    encoded_header = json.dumps(tensors, separators=(",", ":")).encode("utf-8")
    encoded_header += b" " * (-len(encoded_header) % 8)
    (tmp_path / "config.json").write_text(json.dumps(config), encoding="utf-8")
    (tmp_path / "model.safetensors").write_bytes(
        len(encoded_header).to_bytes(8, byteorder="little") + encoded_header + bytes(384)
    )

    shape = read_model_shape(str(tmp_path))

    assert shape.parameter_count == sum(prod(tensor["shape"]) for tensor in tensors.values())
    assert shape.weight_bytes_per_parameter == 2.0
    assert shape.parameter_source == "safetensors_metadata"


def test_gradient_checkpointing_reduces_activation_peak() -> None:
    shape = _qwen_shape()
    checkpointed = _estimate(shape, gradient_checkpointing=True)
    uncheckpointed = _estimate(shape, gradient_checkpointing=False)

    assert uncheckpointed.activation_gib > checkpointed.activation_gib
    assert uncheckpointed.estimated_gib > checkpointed.estimated_gib


def test_validation_forward_peak_is_estimated_separately() -> None:
    shape = _qwen_shape()
    training_only = _estimate(shape, batch_size=1, validation_enabled=False)
    with_validation = _estimate(
        shape,
        batch_size=1,
        validation_enabled=True,
        eval_batch_size=16,
    )

    assert training_only.peak_kind == "training"
    assert with_validation.peak_kind == "validation"
    assert with_validation.activation_gib > training_only.activation_gib


def test_memory_breakdown_reconstructs_estimated_peak() -> None:
    estimate = _estimate(_qwen_shape())

    reconstructed = (
        estimate.model_gib + estimate.trainable_state_gib + estimate.activation_gib + estimate.workspace_gib
    )
    assert estimate.persistent_gib == pytest.approx(estimate.model_gib + estimate.trainable_state_gib, abs=0.02)
    assert estimate.estimated_gib == pytest.approx(reconstructed, abs=0.03)


def test_optimizer_and_offload_are_reflected_in_training_states() -> None:
    shape = _qwen_shape()
    adamw = _estimate(shape, finetuning_type="full", quantization_bit="none", optimizer="adamw_torch")
    eight_bit = _estimate(shape, finetuning_type="full", quantization_bit="none", optimizer="paged_adamw_8bit")
    zero_offload = _estimate(
        shape,
        finetuning_type="full",
        quantization_bit="none",
        optimizer="adamw_torch",
        deepspeed_stage="2",
        device_count=4,
        offload=True,
    )
    badam = _estimate(
        shape,
        finetuning_type="full",
        quantization_bit="none",
        optimizer="adamw_torch",
        use_badam=True,
        badam_mode="layer",
    )

    assert eight_bit.trainable_state_gib < adamw.trainable_state_gib
    assert zero_offload.trainable_state_gib < adamw.trainable_state_gib
    assert badam.trainable_state_gib < adamw.trainable_state_gib


def test_freeze_layer_count_changes_trainable_state_memory() -> None:
    shape = _qwen_shape()
    two_layers = _estimate(shape, finetuning_type="freeze", quantization_bit="none", freeze_trainable_layers=2)
    eight_layers = _estimate(shape, finetuning_type="freeze", quantization_bit="none", freeze_trainable_layers=8)

    assert eight_layers.trainable_parameter_count > two_layers.trainable_parameter_count
    assert eight_layers.trainable_state_gib > two_layers.trainable_state_gib


def test_moe_counts_all_expert_adapters_but_only_active_expert_activations() -> None:
    dense = _qwen_shape()
    moe_two_active = replace(dense, num_local_experts=8, num_experts_per_tok=2)
    moe_all_active = replace(moe_two_active, num_experts_per_tok=8)

    dense_estimate = _estimate(dense)
    sparse_estimate = _estimate(moe_two_active)
    dense_moe_estimate = _estimate(moe_all_active)

    assert sparse_estimate.trainable_parameter_count > dense_estimate.trainable_parameter_count
    assert dense_moe_estimate.activation_gib > sparse_estimate.activation_gib


def test_lora_target_only_counts_selected_projections() -> None:
    shape = _qwen_shape()
    all_linear = _estimate(shape, lora_target="all")
    qv_only = _estimate(shape, lora_target="q_proj,v_proj")

    assert qv_only.trainable_parameter_count < all_linear.trainable_parameter_count
    assert qv_only.trainable_state_gib < all_linear.trainable_state_gib


def test_attention_backend_changes_long_context_workspace() -> None:
    shape = _qwen_shape()
    eager = _estimate(shape, cutoff_len=8192, attention_backend="eager")
    sdpa = _estimate(shape, cutoff_len=8192, attention_backend="sdpa")
    flash = _estimate(shape, cutoff_len=8192, attention_backend="flash_attention_2")

    assert eager.activation_gib > sdpa.activation_gib > flash.activation_gib


def test_pure_bf16_does_not_allocate_fp32_master_weights() -> None:
    shape = _qwen_shape()
    mixed = _estimate(shape, finetuning_type="full", quantization_bit="none", compute_type="bf16")
    pure = _estimate(shape, finetuning_type="full", quantization_bit="none", compute_type="pure_bf16")

    assert pure.trainable_state_gib < mixed.trainable_state_gib


def test_video_frame_count_changes_multimodal_activation() -> None:
    shape = replace(_qwen_shape(), is_multimodal=True, vision_hidden_size=1024, vision_num_hidden_layers=24)
    short_clip = _estimate(shape, video_num_frames=4)
    long_clip = _estimate(shape, video_num_frames=32)

    assert long_clip.activation_gib > short_clip.activation_gib


def test_memory_calibration_uses_bounded_ema(tmp_path) -> None:
    path = tmp_path / "calibration.json"
    first = record_calibration("bucket", actual_gib=12, base_estimated_gib=10, path=path)
    second = record_calibration("bucket", actual_gib=16, base_estimated_gib=10, path=path)
    factor, samples = get_calibration("bucket", path=path)

    assert first is not None and first["ema_ratio"] == pytest.approx(1.2)
    assert second is not None and second["ema_ratio"] == pytest.approx(1.3)
    assert factor == pytest.approx(1.3)
    assert samples == 2


def test_model_shape_scan_is_cached_until_directory_changes(tmp_path, monkeypatch) -> None:
    (tmp_path / "config.json").write_text("{}", encoding="utf-8")
    (tmp_path / "model.bin").write_bytes(b"weights")
    memory_module._read_model_shape_cached.cache_clear()
    original_scan = memory_module._scan_weight_files
    calls = 0

    def counted_scan(model_dir):
        nonlocal calls
        calls += 1
        return original_scan(model_dir)

    monkeypatch.setattr(memory_module, "_scan_weight_files", counted_scan)
    read_model_shape(str(tmp_path))
    read_model_shape(str(tmp_path))

    assert calls == 1


def test_training_callback_records_actual_peak(tmp_path, monkeypatch) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    calibration_path = tmp_path / "calibration.json"
    monkeypatch.setenv("LLAMAFACTORY_MEMORY_CALIBRATION_FILE", str(calibration_path))
    (output_dir / "memory_estimate.json").write_text(
        json.dumps({"calibration_key": "test", "base_estimated_gib": 4.0, "estimated_gib": 5.0}),
        encoding="utf-8",
    )

    class FakeMemoryApi:
        reset = False

        def reset_peak_memory_stats(self):
            self.reset = True

        def max_memory_allocated(self):
            return 6 * 1024**3

    api = FakeMemoryApi()
    callback = MemoryCalibrationCallback()
    monkeypatch.setattr(callback, "_select_memory_api", lambda: api)
    args = SimpleNamespace(should_save=True, output_dir=str(output_dir))
    callback.on_train_begin(args, SimpleNamespace(), SimpleNamespace())
    callback.on_train_end(args, SimpleNamespace(), SimpleNamespace())

    observation = json.loads((output_dir / "memory_actual.json").read_text(encoding="utf-8"))
    assert api.reset is True
    assert observation["actual_peak_gib"] == pytest.approx(6.0)
    assert get_calibration("test", calibration_path) == pytest.approx((1.5, 1))


def test_extended_optimizer_and_fsdp_models_change_state_memory() -> None:
    shape = _qwen_shape()
    adam = _estimate(shape, finetuning_type="full", quantization_bit="none", optimizer="adamw_torch")
    galore = _estimate(
        shape,
        finetuning_type="full",
        quantization_bit="none",
        optimizer="adamw_torch",
        use_galore=True,
        projection_rank=16,
    )
    full_shard = _estimate(
        shape,
        finetuning_type="full",
        quantization_bit="none",
        device_count=4,
        fsdp_strategy="full_shard",
    )
    shard_grad = _estimate(
        shape,
        finetuning_type="full",
        quantization_bit="none",
        device_count=4,
        fsdp_strategy="shard_grad_op",
    )

    assert galore.trainable_state_gib < adam.trainable_state_gib
    assert full_shard.model_gib < shard_grad.model_gib


def test_vllm_colocation_and_chunked_cross_entropy_are_modeled() -> None:
    shape = _qwen_shape()
    standard = _estimate(shape, booster="none", cross_entropy_mode="standard")
    chunked = _estimate(shape, booster="none", cross_entropy_mode="chunked", cross_entropy_chunk_size=4096)
    ppo = _estimate(shape, stage="ppo", use_vllm=False)
    ppo_colocated = _estimate(
        shape,
        stage="ppo",
        use_vllm=True,
        vllm_colocate=True,
        vllm_gpu_util=0.4,
        total_device_gib=80,
    )

    assert chunked.activation_gib < standard.activation_gib
    assert ppo_colocated.model_gib > ppo.model_gib


def test_four_bit_group_size_and_offload_target_affect_estimate() -> None:
    small_groups = _estimate(replace(_qwen_shape(), quantization_group_size=32))
    large_groups = _estimate(replace(_qwen_shape(), quantization_group_size=128))
    cpu_offload = _estimate(
        _qwen_shape(),
        finetuning_type="full",
        quantization_bit="none",
        deepspeed_stage="3",
        device_count=4,
        offload=True,
        offload_target="cpu",
    )
    nvme_offload = _estimate(
        _qwen_shape(),
        finetuning_type="full",
        quantization_bit="none",
        deepspeed_stage="3",
        device_count=4,
        offload=True,
        offload_target="nvme",
    )

    assert small_groups.model_gib > large_groups.model_gib
    assert nvme_offload.model_gib < cpu_offload.model_gib


def test_runner_metadata_is_generated_from_final_training_args(tmp_path, monkeypatch) -> None:
    model_dir = tmp_path / "model"
    output_dir = tmp_path / "output"
    model_dir.mkdir()
    (model_dir / "config.json").write_text(
        json.dumps(
            {
                "hidden_size": 16,
                "intermediate_size": 32,
                "num_attention_heads": 2,
                "num_hidden_layers": 1,
                "num_key_value_heads": 2,
                "vocab_size": 64,
            }
        ),
        encoding="utf-8",
    )
    (model_dir / "model.bin").write_bytes(b"weights" * 32)
    monkeypatch.setattr(
        memory_module,
        "get_device_memory_snapshot",
        lambda: DeviceMemory(free_gib=12.0, total_gib=16.0, device_count=1),
    )

    path = write_memory_estimate_metadata(
        {
            "model_name_or_path": str(model_dir),
            "output_dir": str(output_dir),
            "finetuning_type": "lora",
            "lora_target": "q_proj,v_proj",
            "lora_rank": 4,
            "quantization_bit": 4,
            "cutoff_len": 1024,
            "per_device_train_batch_size": 1,
            "stage": "sft",
            "bf16": True,
            "flash_attn": "sdpa",
        }
    )
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["base_estimated_gib"] > 0
    assert "lora-q_proj,v_proj" in payload["calibration_key"]
