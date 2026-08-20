# Copyright 2025 the LlamaFactory team.
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
import os
import re
from dataclasses import dataclass
from typing import Any

from transformers.utils import CONFIG_NAME, cached_file

from ..extras.misc import get_current_memory, get_device_count, get_torch_device


GIB = 1024**3
SAFETY_MARGIN = 1.10


@dataclass(frozen=True)
class ModelShape:
    parameter_count: int
    hidden_size: int
    num_hidden_layers: int
    vocab_size: int
    num_attention_heads: int
    num_key_value_heads: int
    intermediate_size: int
    source: str
    config_error: str | None = None


@dataclass(frozen=True)
class MemoryEstimate:
    estimated_gib: float
    recommended_gib: float
    parameter_count: int
    persistent_gib: float
    activation_gib: float
    workspace_gib: float
    per_device: bool


@dataclass(frozen=True)
class DeviceMemory:
    free_gib: float | None
    total_gib: float | None
    device_count: int


def _positive_int(value: Any, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default

    return parsed if parsed > 0 else default


def _parse_parameter_count(value: Any) -> int | None:
    if isinstance(value, (int, float)) and value > 1_000_000:
        return int(value)

    if isinstance(value, str):
        normalized = value.strip().lower().replace(",", "")
        match = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)\s*([bmk]?)", normalized)
        if match:
            multiplier = {"": 1, "k": 1_000, "m": 1_000_000, "b": 1_000_000_000}[match.group(2)]
            parsed = int(float(match.group(1)) * multiplier)
            return parsed if parsed > 1_000_000 else None

    return None


def _fallback_parameter_count(profile: str) -> int:
    return {
        "small": 3_000_000_000,
        "medium": 8_000_000_000,
        "large": 24_000_000_000,
        "xlarge": 70_000_000_000,
    }.get(profile, 8_000_000_000)


def _fallback_shape(profile: str, config_error: str | None = None) -> ModelShape:
    shapes = {
        "small": (3_000_000_000, 3072, 28, 32000, 24, 8, 8192),
        "medium": (8_000_000_000, 4096, 32, 128000, 32, 8, 14336),
        "large": (24_000_000_000, 5120, 60, 128000, 40, 8, 13824),
        "xlarge": (70_000_000_000, 8192, 80, 128000, 64, 8, 28672),
    }
    params, hidden, layers, vocab, heads, kv_heads, intermediate = shapes.get(profile, shapes["medium"])
    return ModelShape(
        parameter_count=params,
        hidden_size=hidden,
        num_hidden_layers=layers,
        vocab_size=vocab,
        num_attention_heads=heads,
        num_key_value_heads=kv_heads,
        intermediate_size=intermediate,
        source="profile",
        config_error=config_error,
    )


def _load_config_dict(model_path: str) -> dict[str, Any]:
    if os.path.isfile(model_path):
        config_path = model_path
    elif os.path.isdir(model_path):
        config_path = os.path.join(model_path, CONFIG_NAME)
    else:
        config_path = cached_file(model_path, CONFIG_NAME)

    with open(config_path, encoding="utf-8") as config_file:
        config = json.load(config_file)

    if not isinstance(config, dict):
        raise ValueError("Model configuration must be a JSON object.")

    return config


def _estimate_parameter_count(config: dict[str, Any], text_config: dict[str, Any]) -> int:
    for key in ("num_parameters", "n_params", "parameter_count", "model_size"):
        direct_count = _parse_parameter_count(config.get(key)) or _parse_parameter_count(text_config.get(key))
        if direct_count is not None:
            return direct_count

    hidden_size = _positive_int(text_config.get("hidden_size", text_config.get("n_embd")), 4096)
    num_layers = _positive_int(text_config.get("num_hidden_layers", text_config.get("n_layer")), 32)
    vocab_size = _positive_int(text_config.get("vocab_size"), 32000)
    num_heads = _positive_int(text_config.get("num_attention_heads", text_config.get("n_head")), 32)
    num_kv_heads = _positive_int(text_config.get("num_key_value_heads"), num_heads)
    head_dim = _positive_int(text_config.get("head_dim"), max(1, hidden_size // num_heads))
    intermediate_size = _positive_int(
        text_config.get("intermediate_size", text_config.get("n_inner")), 4 * hidden_size
    )
    kv_size = num_kv_heads * head_dim
    attention_params = 2 * hidden_size * hidden_size + 2 * hidden_size * kv_size
    expert_count = _positive_int(
        text_config.get("num_local_experts", text_config.get("num_experts", text_config.get("n_routed_experts"))),
        1,
    )
    mlp_params = 3 * hidden_size * intermediate_size * expert_count
    shared_expert_size = _positive_int(text_config.get("shared_expert_intermediate_size"), 0)
    if shared_expert_size:
        mlp_params += 3 * hidden_size * shared_expert_size

    tied_embeddings = bool(text_config.get("tie_word_embeddings", config.get("tie_word_embeddings", False)))
    embedding_params = vocab_size * hidden_size * (1 if tied_embeddings else 2)
    parameter_count = num_layers * (attention_params + mlp_params) + embedding_params

    vision_config = config.get("vision_config")
    if isinstance(vision_config, dict):
        vision_hidden = _positive_int(vision_config.get("hidden_size"), 1024)
        vision_layers = _positive_int(vision_config.get("num_hidden_layers"), 24)
        vision_intermediate = _positive_int(vision_config.get("intermediate_size"), 4 * vision_hidden)
        parameter_count += vision_layers * (
            4 * vision_hidden * vision_hidden + 2 * vision_hidden * vision_intermediate
        )

    return int(parameter_count)


def read_model_shape(model_path: str, fallback_profile: str) -> ModelShape:
    try:
        config = _load_config_dict(model_path)
        text_config = config.get("text_config") if isinstance(config.get("text_config"), dict) else config
        hidden_size = _positive_int(text_config.get("hidden_size", text_config.get("n_embd")), 4096)
        num_layers = _positive_int(text_config.get("num_hidden_layers", text_config.get("n_layer")), 32)
        vocab_size = _positive_int(text_config.get("vocab_size"), 32000)
        num_heads = _positive_int(text_config.get("num_attention_heads", text_config.get("n_head")), 32)
        num_kv_heads = _positive_int(text_config.get("num_key_value_heads"), num_heads)
        intermediate_size = _positive_int(
            text_config.get("intermediate_size", text_config.get("n_inner")), 4 * hidden_size
        )
        return ModelShape(
            parameter_count=_estimate_parameter_count(config, text_config),
            hidden_size=hidden_size,
            num_hidden_layers=num_layers,
            vocab_size=vocab_size,
            num_attention_heads=num_heads,
            num_key_value_heads=num_kv_heads,
            intermediate_size=intermediate_size,
            source="config",
        )
    except Exception as err:
        return _fallback_shape(fallback_profile, config_error=str(err))


def _estimate_lora_parameters(shape: ModelShape, rank: int) -> int:
    head_dim = max(1, shape.hidden_size // shape.num_attention_heads)
    kv_size = shape.num_key_value_heads * head_dim
    attention = rank * (6 * shape.hidden_size + 2 * kv_size)  # q/o use 2h each; k/v use h + kv_size each
    mlp = 3 * rank * (shape.hidden_size + shape.intermediate_size)
    return shape.num_hidden_layers * (attention + mlp)


def estimate_training_memory(
    shape: ModelShape,
    *,
    finetuning_type: str,
    quantization_bit: str,
    compute_type: str,
    cutoff_len: int,
    batch_size: int,
    lora_rank: int,
    stage: str,
    deepspeed_stage: str,
    offload: bool,
    device_count: int,
    booster: str,
    gradient_checkpointing: bool = True,
) -> MemoryEstimate:
    devices = max(1, device_count)
    dtype_bytes = 4 if compute_type == "fp32" else 2
    weight_bytes = 0.65 if quantization_bit == "4" else 1.1 if quantization_bit == "8" else dtype_bytes
    base_weight_gib = shape.parameter_count * weight_bytes / GIB
    zero_stage = int(deepspeed_stage) if deepspeed_stage in {"2", "3"} else 0

    if finetuning_type == "full":
        weight_memory = shape.parameter_count * dtype_bytes / GIB
        gradient_memory = shape.parameter_count * dtype_bytes / GIB
        optimizer_memory = shape.parameter_count * 8 / GIB
        master_weight_memory = shape.parameter_count * (4 if dtype_bytes < 4 else 0) / GIB
        if zero_stage == 3:
            persistent_gib = (weight_memory + gradient_memory + optimizer_memory + master_weight_memory) / devices
        elif zero_stage == 2:
            persistent_gib = weight_memory + (gradient_memory + optimizer_memory + master_weight_memory) / devices
        else:
            persistent_gib = weight_memory + gradient_memory + optimizer_memory + master_weight_memory

        if offload and zero_stage:
            offloadable = optimizer_memory + master_weight_memory
            if zero_stage == 3:
                offloadable += weight_memory
            persistent_gib -= 0.9 * offloadable / devices
    else:
        base_on_device = base_weight_gib / devices if zero_stage == 3 else base_weight_gib
        if finetuning_type == "freeze":
            trainable_parameters = int(shape.parameter_count * 0.05)
        elif finetuning_type == "oft":
            trainable_parameters = int(shape.parameter_count * 0.004)
        else:
            trainable_parameters = _estimate_lora_parameters(shape, max(1, lora_rank))

        trainable_states_gib = trainable_parameters * 16 / GIB
        if zero_stage >= 2:
            trainable_states_gib /= devices
        if offload and zero_stage:
            trainable_states_gib *= 0.35
        persistent_gib = base_on_device + trainable_states_gib

    if stage in {"dpo", "kto"} and finetuning_type == "full":
        persistent_gib += base_weight_gib / devices if zero_stage == 3 else base_weight_gib
    elif stage == "ppo":
        persistent_gib += 1.5 * (base_weight_gib / devices if zero_stage == 3 else base_weight_gib)

    activation_factor = 6.0 if gradient_checkpointing else 18.0
    if booster == "liger_kernel":
        activation_factor *= 0.82
    if finetuning_type == "full":
        activation_factor *= 1.12
    if stage in {"dpo", "kto"}:
        activation_factor *= 1.35
    elif stage == "ppo":
        activation_factor *= 1.8

    activation_gib = (
        max(1, batch_size)
        * max(1, cutoff_len)
        * shape.hidden_size
        * shape.num_hidden_layers
        * dtype_bytes
        * activation_factor
        / GIB
    )
    logits_factor = 0.15 if booster == "liger_kernel" else 0.55
    activation_gib += max(1, batch_size) * max(1, cutoff_len) * shape.vocab_size * dtype_bytes * logits_factor / GIB
    workspace_gib = 1.25 + 0.08 * persistent_gib
    estimated_gib = max(1.0, persistent_gib + activation_gib + workspace_gib)

    return MemoryEstimate(
        estimated_gib=round(estimated_gib, 2),
        recommended_gib=round(estimated_gib * SAFETY_MARGIN, 2),
        parameter_count=shape.parameter_count,
        persistent_gib=round(persistent_gib, 2),
        activation_gib=round(activation_gib, 2),
        workspace_gib=round(workspace_gib, 2),
        per_device=True,
    )


def get_device_memory_snapshot() -> DeviceMemory:
    device_count = get_device_count()
    if device_count < 1:
        free, total = get_current_memory()
        if total <= 0:
            return DeviceMemory(free_gib=None, total_gib=None, device_count=0)
        return DeviceMemory(free_gib=free / GIB, total_gib=total / GIB, device_count=1)

    free_values: list[int] = []
    total_values: list[int] = []
    device_api = get_torch_device()
    for device_index in range(device_count):
        try:
            free, total = device_api.mem_get_info(device_index)
        except (AttributeError, TypeError, ValueError, RuntimeError):
            if device_index > 0:
                continue
            free, total = get_current_memory()

        if total > 0:
            free_values.append(free)
            total_values.append(total)

    if not total_values:
        return DeviceMemory(free_gib=None, total_gib=None, device_count=device_count)

    return DeviceMemory(
        free_gib=min(free_values) / GIB,
        total_gib=min(total_values) / GIB,
        device_count=device_count,
    )
