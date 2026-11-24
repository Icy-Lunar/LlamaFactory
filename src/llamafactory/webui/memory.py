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

"""Estimate per-device training memory from local model weights and training settings."""

import json
import os
import re
from dataclasses import dataclass
from functools import lru_cache
from math import prod
from pathlib import Path
from typing import Any

from transformers.utils import CONFIG_NAME

from ..extras.memory_calibration import ESTIMATE_METADATA_NAME, get_calibration
from ..extras.misc import get_current_memory, get_device_count, get_torch_device


GIB = 1024**3
SAFETY_MARGIN = 1.10
DEFAULT_ATTENTION_TILE = 256
DEFAULT_CROSS_ENTROPY_CHUNK = 8192
DEFAULT_COMMUNICATION_BUFFER_BYTES = 25 * 1024**2
OFFLOAD_RESIDENCY = {"cpu": 0.08, "nvme": 0.02}
WEIGHT_INDEX_NAMES = ("model.safetensors.index.json", "pytorch_model.bin.index.json")
WEIGHT_SUFFIX_GROUPS = ((".safetensors",), (".bin",), (".pt", ".pth"))
IGNORED_WEIGHT_PREFIXES = ("optimizer", "scheduler", "trainer", "training_args", "rng_state", "scaler")


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
    weight_size_bytes: int = 0
    weight_file_count: int = 0
    weight_bytes_per_parameter: float = 2.0
    config_error: str | None = None
    is_multimodal: bool = False
    vision_hidden_size: int = 0
    vision_num_hidden_layers: int = 0
    vision_intermediate_size: int = 0
    vision_patch_size: int = 14
    vision_spatial_merge_size: int = 1
    num_local_experts: int = 1
    num_experts_per_tok: int = 1
    shared_expert_intermediate_size: int = 0
    text_parameter_count: int = 0
    vision_parameter_count: int = 0
    projector_parameter_count: int = 0
    parameter_source: str = "file_size"
    quantization_group_size: int = 64
    quantization_type: str = ""


@dataclass(frozen=True)
class MemoryEstimate:
    estimated_gib: float
    recommended_gib: float
    parameter_count: int
    persistent_gib: float
    activation_gib: float
    workspace_gib: float
    per_device: bool
    weight_size_gib: float
    model_gib: float
    trainable_state_gib: float
    trainable_parameter_count: int
    peak_kind: str
    uncalibrated_gib: float = 0.0
    calibration_factor: float = 1.0
    calibration_samples: int = 0
    calibration_key: str = ""


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


def resolve_local_model_dir(model_path: str) -> Path:
    if not model_path or not model_path.strip():
        raise ValueError("A local model directory is required.")

    model_dir = Path(model_path).expanduser().resolve()
    if not model_dir.is_dir():
        raise ValueError("The model path must be an existing local directory.")

    return model_dir


def _load_config_dict(model_dir: Path) -> dict[str, Any]:
    config_path = model_dir / CONFIG_NAME
    if not config_path.is_file():
        raise ValueError(f"Missing {CONFIG_NAME} in the local model directory.")

    with open(config_path, encoding="utf-8") as config_file:
        config = json.load(config_file)

    if not isinstance(config, dict):
        raise ValueError("Model configuration must be a JSON object.")

    return config


def _read_weight_index(model_dir: Path, index_path: Path) -> list[Path]:
    with open(index_path, encoding="utf-8") as index_file:
        index = json.load(index_file)

    weight_map = index.get("weight_map") if isinstance(index, dict) else None
    if not isinstance(weight_map, dict) or not weight_map:
        raise ValueError(f"Invalid weight index: {index_path.name}.")

    weight_files = []
    for relative_name in sorted(set(weight_map.values())):
        if not isinstance(relative_name, str):
            raise ValueError(f"Invalid weight file entry in {index_path.name}.")

        weight_path = (model_dir / relative_name).resolve()
        try:
            weight_path.relative_to(model_dir)
        except ValueError as err:
            raise ValueError(f"Weight index points outside the model directory: {relative_name}.") from err

        if not weight_path.is_file():
            raise ValueError(f"Weight shard listed by the index was not found: {relative_name}.")

        weight_files.append(weight_path)

    return weight_files


def _scan_weight_files(model_dir: Path) -> list[Path]:
    for index_name in WEIGHT_INDEX_NAMES:
        index_path = model_dir / index_name
        if index_path.is_file():
            return _read_weight_index(model_dir, index_path)

    candidates: dict[tuple[str, ...], list[Path]] = {suffixes: [] for suffixes in WEIGHT_SUFFIX_GROUPS}
    for weight_path in model_dir.rglob("*"):
        relative_parent_parts = weight_path.relative_to(model_dir).parts[:-1]
        if not weight_path.is_file() or any(part.startswith("checkpoint-") for part in relative_parent_parts):
            continue

        file_name = weight_path.name.lower()
        if file_name.startswith(IGNORED_WEIGHT_PREFIXES):
            continue

        for suffixes in WEIGHT_SUFFIX_GROUPS:
            if weight_path.suffix.lower() in suffixes:
                candidates[suffixes].append(weight_path)
                break

    for suffixes in WEIGHT_SUFFIX_GROUPS:
        if candidates[suffixes]:
            return sorted(candidates[suffixes])

    raise ValueError("No supported model weight files were found in the local model directory.")


def _read_safetensors_metadata(weight_files: list[Path]) -> tuple[int, int] | None:
    """Read tensor counts from safetensors headers without allocating model weights."""
    if not weight_files or any(weight_file.suffix.lower() != ".safetensors" for weight_file in weight_files):
        return None

    parameter_count = 0
    tensor_bytes = 0
    try:
        for weight_file in weight_files:
            file_size = weight_file.stat().st_size
            with open(weight_file, "rb") as safetensors_file:
                header_length_bytes = safetensors_file.read(8)
                if len(header_length_bytes) != 8:
                    return None

                header_length = int.from_bytes(header_length_bytes, byteorder="little", signed=False)
                if header_length <= 0 or header_length > min(file_size - 8, 256 * 1024 * 1024):
                    return None

                header = json.loads(safetensors_file.read(header_length).decode("utf-8"))
                data_size = file_size - 8 - header_length

            if not isinstance(header, dict):
                return None

            for tensor_name, tensor_info in header.items():
                if tensor_name == "__metadata__":
                    continue
                if not isinstance(tensor_info, dict):
                    return None

                shape = tensor_info.get("shape")
                offsets = tensor_info.get("data_offsets")
                if (
                    not isinstance(shape, list)
                    or not all(isinstance(dimension, int) and dimension >= 0 for dimension in shape)
                    or not isinstance(offsets, list)
                    or len(offsets) != 2
                    or not all(isinstance(offset, int) and offset >= 0 for offset in offsets)
                    or offsets[1] < offsets[0]
                    or offsets[1] > data_size
                ):
                    return None

                parameter_count += prod(shape)
                tensor_bytes += offsets[1] - offsets[0]
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None

    if parameter_count <= 0 or tensor_bytes <= 0:
        return None
    return parameter_count, tensor_bytes


def get_local_weight_size(model_path: str) -> tuple[int, int]:
    shape = read_model_shape(model_path)
    return shape.weight_size_bytes, shape.weight_file_count


def _weight_bytes_per_parameter(config: dict[str, Any], text_config: dict[str, Any]) -> float:
    quantization_config = config.get("quantization_config")
    if isinstance(quantization_config, dict):
        bits = quantization_config.get("bits")
        try:
            parsed_bits = float(bits)
        except (TypeError, ValueError):
            parsed_bits = 0.0

        if parsed_bits > 0:
            return max(0.5, parsed_bits / 8)

    dtype = str(text_config.get("torch_dtype", config.get("torch_dtype", "float16"))).lower()
    if any(name in dtype for name in ("float64", "double")):
        return 8.0
    if any(name in dtype for name in ("float32", "fp32")):
        return 4.0
    if any(name in dtype for name in ("float8", "fp8", "int8", "uint8")):
        return 1.0
    if any(name in dtype for name in ("int4", "nf4", "fp4")):
        return 0.5

    return 2.0


def _estimate_text_parameter_count(text_config: dict[str, Any]) -> int:
    for key in ("num_parameters", "n_params", "parameter_count", "model_size"):
        direct_count = _parse_parameter_count(text_config.get(key))
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

    tied_embeddings = bool(text_config.get("tie_word_embeddings", False))
    embedding_params = vocab_size * hidden_size * (1 if tied_embeddings else 2)
    return int(num_layers * (attention_params + mlp_params) + embedding_params)


def _estimate_vision_parameter_count(vision_config: dict[str, Any]) -> int:
    if not vision_config:
        return 0

    vision_hidden = _positive_int(vision_config.get("hidden_size"), 1024)
    vision_layers = _positive_int(vision_config.get("num_hidden_layers"), 24)
    vision_intermediate = _positive_int(vision_config.get("intermediate_size"), 4 * vision_hidden)
    return int(vision_layers * (4 * vision_hidden * vision_hidden + 2 * vision_hidden * vision_intermediate))


def _estimate_parameter_count(config: dict[str, Any], text_config: dict[str, Any]) -> int:
    for key in ("num_parameters", "n_params", "parameter_count", "model_size"):
        direct_count = _parse_parameter_count(config.get(key)) or _parse_parameter_count(text_config.get(key))
        if direct_count is not None:
            return direct_count

    parameter_count = _estimate_text_parameter_count(text_config)

    vision_config = config.get("vision_config")
    if isinstance(vision_config, dict):
        parameter_count += _estimate_vision_parameter_count(vision_config)

    return int(parameter_count)


def _is_multimodal_config(config: dict[str, Any]) -> bool:
    if isinstance(config.get("vision_config"), dict):
        return True

    architectures = config.get("architectures", [])
    if isinstance(architectures, str):
        architectures = [architectures]
    elif not isinstance(architectures, (list, tuple)):
        architectures = []

    model_identity = " ".join(
        [
            str(config.get("model_type", "")),
            *(str(architecture) for architecture in architectures),
        ]
    ).lower()
    return any(
        marker in model_identity
        for marker in ("vision", "visual", "llava", "mllama", "paligemma", "idefics", "internvl", "minicpmv", "_vl")
    )


def _model_directory_mtime(model_dir: Path) -> int:
    """Build a cheap invalidation key without walking every weight shard."""
    candidates = [model_dir, model_dir / CONFIG_NAME, *(model_dir / name for name in WEIGHT_INDEX_NAMES)]
    mtimes = []
    for candidate in candidates:
        try:
            mtimes.append(candidate.stat().st_mtime_ns)
        except OSError:
            continue
    return hash(tuple(mtimes))


@lru_cache(maxsize=16)
def _read_model_shape_cached(model_dir_text: str, directory_mtime: int) -> ModelShape:
    del directory_mtime  # It is intentionally part of the cache key.
    model_dir = Path(model_dir_text)
    config = _load_config_dict(model_dir)
    weight_files = _scan_weight_files(model_dir)
    weight_size_bytes = sum(weight_file.stat().st_size for weight_file in weight_files)
    if weight_size_bytes <= 0:
        raise ValueError("The local model weight files are empty.")

    text_config = dict(config.get("text_config")) if isinstance(config.get("text_config"), dict) else config
    if text_config is not config:
        text_config.setdefault("tie_word_embeddings", config.get("tie_word_embeddings", False))
    hidden_size = _positive_int(text_config.get("hidden_size", text_config.get("n_embd")), 4096)
    num_layers = _positive_int(text_config.get("num_hidden_layers", text_config.get("n_layer")), 32)
    vocab_size = _positive_int(text_config.get("vocab_size"), 32000)
    num_heads = _positive_int(text_config.get("num_attention_heads", text_config.get("n_head")), 32)
    num_kv_heads = _positive_int(text_config.get("num_key_value_heads"), num_heads)
    intermediate_size = _positive_int(
        text_config.get("intermediate_size", text_config.get("n_inner")), 4 * hidden_size
    )
    vision_config = config.get("vision_config") if isinstance(config.get("vision_config"), dict) else {}
    is_multimodal = _is_multimodal_config(config)
    configured_bytes_per_parameter = _weight_bytes_per_parameter(config, text_config)
    tensor_metadata = _read_safetensors_metadata(weight_files)
    architecture_parameter_count = _estimate_parameter_count(config, text_config)
    quantization_config = config.get("quantization_config")
    has_quantized_storage = isinstance(quantization_config, dict) and any(
        quantization_config.get(key) not in (None, False, "")
        for key in ("quant_method", "bits", "load_in_4bit", "load_in_8bit")
    )
    if tensor_metadata is not None and not has_quantized_storage:
        parameter_count, tensor_bytes = tensor_metadata
        bytes_per_parameter = tensor_bytes / parameter_count
        parameter_source = "safetensors_metadata"
    elif has_quantized_storage:
        parameter_count = architecture_parameter_count
        bytes_per_parameter = weight_size_bytes / max(1, parameter_count)
        parameter_source = "config_architecture"
    else:
        parameter_count = max(1, round(weight_size_bytes / configured_bytes_per_parameter))
        bytes_per_parameter = configured_bytes_per_parameter
        parameter_source = "weight_size"

    text_parameter_estimate = _estimate_text_parameter_count(text_config)
    if is_multimodal:
        resolved_vision_config = vision_config or {
            "hidden_size": 1024,
            "num_hidden_layers": 24,
            "intermediate_size": 4096,
        }
        vision_parameter_estimate = _estimate_vision_parameter_count(resolved_vision_config)
        vision_hidden_size = _positive_int(resolved_vision_config.get("hidden_size"), 1024)
        projector_parameter_estimate = vision_hidden_size * hidden_size + hidden_size * hidden_size
    else:
        vision_parameter_estimate = 0
        projector_parameter_estimate = 0

    component_total = max(
        1,
        text_parameter_estimate + vision_parameter_estimate + projector_parameter_estimate,
    )
    component_scale = parameter_count / component_total
    text_parameter_count = int(text_parameter_estimate * component_scale)
    vision_parameter_count = int(vision_parameter_estimate * component_scale)
    projector_parameter_count = max(0, parameter_count - text_parameter_count - vision_parameter_count)
    return ModelShape(
        parameter_count=parameter_count,
        hidden_size=hidden_size,
        num_hidden_layers=num_layers,
        vocab_size=vocab_size,
        num_attention_heads=num_heads,
        num_key_value_heads=num_kv_heads,
        intermediate_size=intermediate_size,
        source="local_weights",
        weight_size_bytes=weight_size_bytes,
        weight_file_count=len(weight_files),
        weight_bytes_per_parameter=bytes_per_parameter,
        is_multimodal=is_multimodal,
        vision_hidden_size=_positive_int(vision_config.get("hidden_size"), 1024) if is_multimodal else 0,
        vision_num_hidden_layers=(_positive_int(vision_config.get("num_hidden_layers"), 24) if is_multimodal else 0),
        vision_intermediate_size=(
            _positive_int(vision_config.get("intermediate_size"), 4 * 1024) if is_multimodal else 0
        ),
        vision_patch_size=_positive_int(vision_config.get("patch_size"), 14) if is_multimodal else 14,
        vision_spatial_merge_size=(_positive_int(vision_config.get("spatial_merge_size"), 1) if is_multimodal else 1),
        num_local_experts=_positive_int(
            text_config.get("num_local_experts", text_config.get("num_experts", text_config.get("n_routed_experts"))),
            1,
        ),
        num_experts_per_tok=_positive_int(
            text_config.get("num_experts_per_tok", text_config.get("num_experts_per_token")),
            1,
        ),
        shared_expert_intermediate_size=_positive_int(
            text_config.get("shared_expert_intermediate_size"),
            0,
        ),
        text_parameter_count=text_parameter_count,
        vision_parameter_count=vision_parameter_count,
        projector_parameter_count=projector_parameter_count,
        parameter_source=parameter_source,
        quantization_group_size=(
            _positive_int(quantization_config.get("group_size", quantization_config.get("block_size")), 64)
            if isinstance(quantization_config, dict)
            else 64
        ),
        quantization_type=(
            str(
                quantization_config.get(
                    "bnb_4bit_quant_type",
                    quantization_config.get("quant_method", ""),
                )
            ).lower()
            if isinstance(quantization_config, dict)
            else ""
        ),
    )


def read_model_shape(model_path: str) -> ModelShape:
    model_dir = resolve_local_model_dir(model_path)
    return _read_model_shape_cached(str(model_dir), _model_directory_mtime(model_dir))


def _normalize_lora_targets(lora_target: str | list[str] | tuple[str, ...] | None) -> set[str]:
    if isinstance(lora_target, str):
        targets = re.split(r"[,\s]+", lora_target.strip())
    elif isinstance(lora_target, (list, tuple)):
        targets = [str(target) for target in lora_target]
    else:
        targets = ["all"]
    normalized = {target.rsplit(".", 1)[-1].lower() for target in targets if target}
    return normalized or {"all"}


def _estimate_lora_parameters(
    shape: ModelShape,
    rank: int,
    lora_target: str | list[str] | tuple[str, ...] | None = "all",
) -> int:
    head_dim = max(1, shape.hidden_size // shape.num_attention_heads)
    kv_size = shape.num_key_value_heads * head_dim
    targets = _normalize_lora_targets(lora_target)
    all_modules = "all" in targets or "all-linear" in targets
    module_dimensions = {
        "q_proj": (shape.hidden_size, shape.hidden_size),
        "k_proj": (shape.hidden_size, kv_size),
        "v_proj": (shape.hidden_size, kv_size),
        "o_proj": (shape.hidden_size, shape.hidden_size),
        "gate_proj": (shape.hidden_size, shape.intermediate_size),
        "up_proj": (shape.hidden_size, shape.intermediate_size),
        "down_proj": (shape.intermediate_size, shape.hidden_size),
    }
    selected = (
        module_dimensions
        if all_modules
        else {name: dimensions for name, dimensions in module_dimensions.items() if name in targets}
    )
    # Unknown custom names are conservatively treated as hidden-to-hidden projections.
    unknown_count = 0 if all_modules else len(targets - set(module_dimensions))
    per_layer = sum(rank * (input_size + output_size) for input_size, output_size in selected.values())
    per_layer += unknown_count * rank * 2 * shape.hidden_size

    expert_targets = {"gate_proj", "up_proj", "down_proj"}.intersection(selected)
    if expert_targets and shape.num_local_experts > 1:
        expert_parameters = sum(rank * sum(module_dimensions[name]) for name in expert_targets)
        per_layer += expert_parameters * (shape.num_local_experts - 1)
    if shape.shared_expert_intermediate_size and (all_modules or expert_targets):
        shared_dimensions = shape.hidden_size + shape.shared_expert_intermediate_size
        per_layer += len(expert_targets or {"gate_proj", "up_proj", "down_proj"}) * rank * shared_dimensions
    return shape.num_hidden_layers * per_layer


def _optimizer_state_bytes(
    optimizer: str,
    *,
    use_galore: bool = False,
    use_apollo: bool = False,
    use_adam_mini: bool = False,
    use_muon: bool = False,
    projection_rank: int = 16,
    hidden_size: int = 4096,
) -> float:
    normalized = (optimizer or "adamw_torch").lower()
    projection_ratio = min(1.0, max(0.01, projection_rank / max(1, hidden_size)))
    if use_galore or "galore" in normalized:
        return 4.0 + 8.0 * projection_ratio
    if use_apollo or "apollo" in normalized:
        return 2.0 + 6.0 * projection_ratio
    if "8bit" in normalized:
        return 2.5
    if "adafactor" in normalized:
        return 4.0
    if use_adam_mini or "adam_mini" in normalized or "adam-mini" in normalized:
        return 4.5
    if use_muon or "muon" in normalized:
        return 4.0
    if any(name in normalized for name in ("sgd", "rmsprop")):
        return 4.0
    return 8.0


def _attention_workspace_elements(
    shape: ModelShape,
    *,
    batch: int,
    stage_multiplier: float,
    sequence: int,
    attention_backend: str,
) -> float:
    normalized = (attention_backend or "sdpa").lower().replace("-", "_")
    prefix = batch * stage_multiplier * max(1, shape.num_attention_heads) * sequence
    if normalized in {"eager", "disabled"}:
        return prefix * sequence
    if normalized in {"fa2", "fa3", "flash", "flash_attn", "flash_attention_2", "flash_attention_3"}:
        return prefix * min(sequence, 64)
    return prefix * min(sequence, DEFAULT_ATTENTION_TILE)


def _logits_materialization_factor(
    shape: ModelShape,
    *,
    fused_loss: bool,
    cross_entropy_mode: str,
    cross_entropy_chunk_size: int,
) -> float:
    mode = (cross_entropy_mode or "auto").lower()
    if fused_loss or mode in {"fused", "liger"}:
        return 0.12
    if mode in {"chunked", "chunk"}:
        return min(1.0, max(0.08, cross_entropy_chunk_size / max(1, shape.vocab_size)))
    return 1.0


def _estimate_text_activation_bytes(
    shape: ModelShape,
    *,
    batch_size: int,
    cutoff_len: int,
    dtype_bytes: int,
    stage: str,
    gradient_checkpointing: bool,
    fused_loss: bool,
    attention_backend: str,
    cross_entropy_mode: str,
    cross_entropy_chunk_size: int,
    training: bool,
) -> float:
    batch = max(1, batch_size)
    sequence = max(1, cutoff_len)
    stage_multiplier = 2.0 if stage in {"dpo", "kto", "ppo"} else 1.0
    tokens = batch * sequence * stage_multiplier
    head_dim = max(1, shape.hidden_size // max(1, shape.num_attention_heads))
    kv_size = max(1, shape.num_key_value_heads) * head_dim
    active_intermediate = shape.intermediate_size * max(1, shape.num_experts_per_tok)

    # Only one transformer's temporary tensors are live at a time. Attention workspaces differ
    # substantially: eager materializes the full score matrix, while SDPA and FlashAttention tile it.
    transient_elements = tokens * (4 * shape.hidden_size + 3 * active_intermediate + 2 * kv_size)
    attention_workspace_elements = _attention_workspace_elements(
        shape,
        batch=batch,
        stage_multiplier=stage_multiplier,
        sequence=sequence,
        attention_backend=attention_backend,
    )
    transient_bytes = (transient_elements + attention_workspace_elements) * dtype_bytes

    if training and gradient_checkpointing:
        saved_bytes = tokens * shape.hidden_size * shape.num_hidden_layers * dtype_bytes * 2.0
    elif training:
        saved_elements = (
            tokens * (6 * shape.hidden_size + 3 * active_intermediate + 2 * kv_size) * shape.num_hidden_layers
        )
        saved_bytes = saved_elements * dtype_bytes
    else:
        saved_bytes = 0.0

    # Standard causal-LM loss materializes full logits, usually in fp32. Liger's fused linear
    # cross entropy works in chunks and therefore keeps only a fraction of that peak live.
    logits_factor = _logits_materialization_factor(
        shape,
        fused_loss=fused_loss,
        cross_entropy_mode=cross_entropy_mode,
        cross_entropy_chunk_size=cross_entropy_chunk_size,
    )
    logits_bytes = tokens * shape.vocab_size * 4 * logits_factor
    return saved_bytes + transient_bytes + logits_bytes


def _estimate_vision_activation_bytes(
    shape: ModelShape,
    *,
    batch_size: int,
    dtype_bytes: int,
    stage: str,
    gradient_checkpointing: bool,
    freeze_vision_tower: bool,
    freeze_multi_modal_projector: bool,
    image_max_pixels: int,
    video_max_pixels: int,
    video_num_frames: int,
) -> float:
    patch_area = max(1, shape.vision_patch_size**2 * shape.vision_spatial_merge_size**2)
    image_tokens = max(1, image_max_pixels) / patch_area
    video_tokens = max(1, video_num_frames) * max(1, video_max_pixels) / patch_area
    stage_multiplier = 2.0 if stage in {"dpo", "kto", "ppo"} else 1.0
    tokens = max(1, batch_size) * stage_multiplier * (image_tokens + video_tokens)
    hidden = shape.vision_hidden_size or 1024
    intermediate = shape.vision_intermediate_size or 4 * hidden
    layers = shape.vision_num_hidden_layers or 24
    transient_bytes = tokens * (6 * hidden + 2 * intermediate) * dtype_bytes

    if freeze_vision_tower:
        saved_bytes = 0.0
    elif gradient_checkpointing:
        saved_bytes = tokens * hidden * layers * dtype_bytes * 2.0
    else:
        saved_bytes = tokens * (6 * hidden + 2 * intermediate) * layers * dtype_bytes

    projector_bytes = 0.0
    if not freeze_multi_modal_projector:
        projector_bytes = tokens * shape.hidden_size * dtype_bytes * 3.0
    return transient_bytes + saved_bytes + projector_bytes


def _four_bit_bytes_per_parameter(shape: ModelShape, double_quantization: bool) -> float:
    # Packed nibbles plus per-group scale/zero metadata. Double quantization compresses scales.
    metadata_bytes = 2.5 if double_quantization else 4.0
    return 0.5 + metadata_bytes / max(1, shape.quantization_group_size)


def _calibration_bucket(
    shape: ModelShape,
    *,
    finetuning_type: str,
    quantization_bit: str,
    compute_type: str,
    cutoff_len: int,
    batch_size: int,
    attention_backend: str,
    deepspeed_stage: str,
    fsdp_strategy: str,
    stage: str,
    offload: bool,
    offload_target: str,
    booster: str,
    lora_target: str | list[str] | tuple[str, ...] | None,
    optimizer: str,
    is_multimodal: bool,
) -> str:
    parameter_bucket = max(1, round(shape.parameter_count / 1_000_000_000))
    sequence_bucket = 1 << max(0, max(1, cutoff_len).bit_length() - 1)
    fields = (
        f"p{parameter_bucket}b",
        finetuning_type,
        f"q{quantization_bit}",
        compute_type,
        f"s{sequence_bucket}",
        f"b{max(1, batch_size)}",
        (attention_backend or "sdpa").lower(),
        f"z{deepspeed_stage}",
        (fsdp_strategy or "none").lower(),
        stage,
        f"offload-{offload_target.lower()}" if offload else "no-offload",
        booster,
        "lora-" + ",".join(sorted(_normalize_lora_targets(lora_target))),
        optimizer.lower(),
        "multimodal" if is_multimodal else "text",
    )
    return ":".join(fields)


def _communication_buffer_bytes() -> int:
    configured = os.getenv("NCCL_BUFFSIZE", "").strip()
    try:
        value = int(configured)
    except ValueError:
        value = DEFAULT_COMMUNICATION_BUFFER_BYTES
    return max(1, value)


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
    is_multimodal: bool = False,
    freeze_vision_tower: bool = True,
    freeze_multi_modal_projector: bool = True,
    freeze_language_model: bool = False,
    image_max_pixels: int = 768 * 768,
    video_max_pixels: int = 256 * 256,
    eval_batch_size: int = 0,
    validation_enabled: bool = False,
    freeze_trainable_layers: int = 2,
    optimizer: str = "adamw_torch",
    use_badam: bool = False,
    badam_mode: str = "layer",
    badam_update_ratio: float = 0.05,
    lora_target: str | list[str] | tuple[str, ...] | None = "all",
    attention_backend: str = "sdpa",
    cross_entropy_mode: str = "auto",
    cross_entropy_chunk_size: int = DEFAULT_CROSS_ENTROPY_CHUNK,
    double_quantization: bool = True,
    offload_target: str = "cpu",
    fsdp_strategy: str = "none",
    fsdp_shard_size: int = 0,
    use_galore: bool = False,
    use_apollo: bool = False,
    use_adam_mini: bool = False,
    use_muon: bool = False,
    projection_rank: int = 16,
    video_num_frames: int = 128,
    use_vllm: bool = False,
    vllm_gpu_util: float = 0.0,
    vllm_colocate: bool = True,
    total_device_gib: float = 0.0,
    apply_calibration: bool = True,
) -> MemoryEstimate:
    devices = max(1, device_count)
    dtype_bytes = 4 if compute_type == "fp32" else 2
    quantization_enabled = finetuning_type in {"lora", "oft"} and quantization_bit in {"4", "8"}
    if quantization_enabled and quantization_bit == "4":
        loaded_bytes_per_parameter = _four_bit_bytes_per_parameter(shape, double_quantization)
    elif quantization_enabled:
        loaded_bytes_per_parameter = 1.125
    else:
        loaded_bytes_per_parameter = dtype_bytes

    base_model_bytes = shape.parameter_count * loaded_bytes_per_parameter
    zero_stage = int(deepspeed_stage) if deepspeed_stage in {"2", "3"} else 0

    text_parameters = shape.text_parameter_count or shape.parameter_count
    vision_parameters = shape.vision_parameter_count
    projector_parameters = shape.projector_parameter_count
    if finetuning_type == "full":
        if is_multimodal or shape.is_multimodal:
            trainable_parameters = (
                (0 if freeze_language_model else text_parameters)
                + (0 if freeze_vision_tower else vision_parameters)
                + (0 if freeze_multi_modal_projector else projector_parameters)
            )
        else:
            trainable_parameters = shape.parameter_count
    elif finetuning_type == "freeze":
        layer_fraction = min(1.0, max(1, abs(freeze_trainable_layers)) / max(1, shape.num_hidden_layers))
        trainable_parameters = max(1, int(text_parameters * layer_fraction))
        if is_multimodal or shape.is_multimodal:
            trainable_parameters += 0 if freeze_vision_tower else vision_parameters
            trainable_parameters += 0 if freeze_multi_modal_projector else projector_parameters
    elif finetuning_type == "oft":
        trainable_parameters = max(1, int(shape.parameter_count * 0.004))
    else:
        base_lora_parameters = _estimate_lora_parameters(shape, max(1, lora_rank), lora_target)
        trainable_parameters = 0 if freeze_language_model else base_lora_parameters
        if is_multimodal or shape.is_multimodal:
            text_denominator = max(1, text_parameters)
            if not freeze_vision_tower:
                trainable_parameters += int(base_lora_parameters * vision_parameters / text_denominator)
            if not freeze_multi_modal_projector:
                trainable_parameters += max(
                    1,
                    int(base_lora_parameters * projector_parameters / text_denominator),
                )
        trainable_parameters = max(1, trainable_parameters)

    state_parameter_count = trainable_parameters
    if use_badam and finetuning_type in {"full", "freeze"}:
        active_ratio = (
            1 / max(1, shape.num_hidden_layers) if badam_mode == "layer" else min(1.0, max(0.01, badam_update_ratio))
        )
        state_parameter_count = max(1, int(trainable_parameters * active_ratio))

    adapter_parameters = trainable_parameters if finetuning_type in {"lora", "oft"} else 0
    adapter_parameter_bytes = adapter_parameters * 4
    gradient_bytes = state_parameter_count * (4 if finetuning_type in {"lora", "oft"} else dtype_bytes)
    optimizer_bytes = state_parameter_count * _optimizer_state_bytes(
        optimizer,
        use_galore=use_galore,
        use_apollo=use_apollo,
        use_adam_mini=use_adam_mini,
        use_muon=use_muon,
        projection_rank=projection_rank,
        hidden_size=shape.hidden_size,
    )
    master_weight_bytes = (
        state_parameter_count * 4
        if dtype_bytes < 4 and compute_type != "pure_bf16" and finetuning_type in {"full", "freeze"}
        else 0
    )

    normalized_fsdp = (fsdp_strategy or "none").lower().replace("-", "_")
    if zero_stage == 3:
        model_device_bytes = base_model_bytes / devices
        adapter_device_bytes = adapter_parameter_bytes  # small parameters commonly remain persistent
        gradient_device_bytes = gradient_bytes / devices
        optimizer_device_bytes = optimizer_bytes / devices
        master_device_bytes = master_weight_bytes / devices
    elif zero_stage == 2:
        model_device_bytes = base_model_bytes
        adapter_device_bytes = adapter_parameter_bytes
        gradient_device_bytes = gradient_bytes / devices
        optimizer_device_bytes = optimizer_bytes / devices
        master_device_bytes = master_weight_bytes / devices
    elif normalized_fsdp in {"full_shard", "fsdp2", "full"}:
        shard_devices = max(1, fsdp_shard_size or devices)
        model_device_bytes = base_model_bytes / shard_devices
        adapter_device_bytes = adapter_parameter_bytes
        gradient_device_bytes = gradient_bytes / shard_devices
        optimizer_device_bytes = optimizer_bytes / shard_devices
        master_device_bytes = master_weight_bytes / shard_devices
    elif normalized_fsdp in {"shard_grad_op", "grad_op"}:
        model_device_bytes = base_model_bytes
        adapter_device_bytes = adapter_parameter_bytes
        gradient_device_bytes = gradient_bytes / devices
        optimizer_device_bytes = optimizer_bytes / devices
        master_device_bytes = master_weight_bytes / devices
    elif normalized_fsdp in {"hybrid_shard", "hybrid"}:
        shard_devices = max(1, fsdp_shard_size or round(devices**0.5))
        model_device_bytes = base_model_bytes / shard_devices
        adapter_device_bytes = adapter_parameter_bytes
        gradient_device_bytes = gradient_bytes / shard_devices
        optimizer_device_bytes = optimizer_bytes / shard_devices
        master_device_bytes = master_weight_bytes / shard_devices
    else:
        model_device_bytes = base_model_bytes
        adapter_device_bytes = adapter_parameter_bytes
        gradient_device_bytes = gradient_bytes
        optimizer_device_bytes = optimizer_bytes
        master_device_bytes = master_weight_bytes

    if offload:
        residency = OFFLOAD_RESIDENCY.get((offload_target or "cpu").lower(), OFFLOAD_RESIDENCY["cpu"])
        if zero_stage == 2:
            optimizer_device_bytes *= residency
            master_device_bytes *= residency
        elif zero_stage == 3 or normalized_fsdp in {"full_shard", "fsdp2", "full", "hybrid_shard", "hybrid"}:
            model_device_bytes *= residency
            optimizer_device_bytes *= residency
            master_device_bytes *= residency

    auxiliary_model_factor = 0.0
    if stage in {"dpo", "kto"} and finetuning_type == "full":
        auxiliary_model_factor = 1.0
    elif stage == "ppo":
        auxiliary_model_factor = 2.0
    auxiliary_model_bytes = auxiliary_model_factor * base_model_bytes
    if stage == "ppo" and use_vllm and vllm_colocate and total_device_gib > 0:
        auxiliary_model_bytes += max(0.0, min(1.0, vllm_gpu_util)) * total_device_gib * GIB

    model_gib = (model_device_bytes + auxiliary_model_bytes) / GIB
    trainable_state_gib = (
        adapter_device_bytes + gradient_device_bytes + optimizer_device_bytes + master_device_bytes
    ) / GIB
    persistent_gib = model_gib + trainable_state_gib

    fused_loss = booster == "liger_kernel" and stage in {"pt", "sft"}
    training_activation_bytes = _estimate_text_activation_bytes(
        shape,
        batch_size=batch_size,
        cutoff_len=cutoff_len,
        dtype_bytes=dtype_bytes,
        stage=stage,
        gradient_checkpointing=gradient_checkpointing,
        fused_loss=fused_loss,
        attention_backend=attention_backend,
        cross_entropy_mode=cross_entropy_mode,
        cross_entropy_chunk_size=cross_entropy_chunk_size,
        training=True,
    )
    if is_multimodal or shape.is_multimodal:
        training_activation_bytes += _estimate_vision_activation_bytes(
            shape,
            batch_size=batch_size,
            dtype_bytes=dtype_bytes,
            stage=stage,
            gradient_checkpointing=gradient_checkpointing,
            freeze_vision_tower=freeze_vision_tower,
            freeze_multi_modal_projector=freeze_multi_modal_projector,
            image_max_pixels=image_max_pixels,
            video_max_pixels=video_max_pixels,
            video_num_frames=video_num_frames,
        )

    evaluation_activation_bytes = 0.0
    if validation_enabled and stage != "ppo" and eval_batch_size > 0:
        evaluation_activation_bytes = _estimate_text_activation_bytes(
            shape,
            batch_size=eval_batch_size,
            cutoff_len=cutoff_len,
            dtype_bytes=dtype_bytes,
            stage=stage,
            gradient_checkpointing=False,
            fused_loss=fused_loss,
            attention_backend=attention_backend,
            cross_entropy_mode=cross_entropy_mode,
            cross_entropy_chunk_size=cross_entropy_chunk_size,
            training=False,
        )
        if is_multimodal or shape.is_multimodal:
            evaluation_activation_bytes += _estimate_vision_activation_bytes(
                shape,
                batch_size=eval_batch_size,
                dtype_bytes=dtype_bytes,
                stage=stage,
                gradient_checkpointing=False,
                freeze_vision_tower=True,
                freeze_multi_modal_projector=True,
                image_max_pixels=image_max_pixels,
                video_max_pixels=video_max_pixels,
                video_num_frames=video_num_frames,
            )

    peak_kind = "validation" if evaluation_activation_bytes > training_activation_bytes else "training"
    activation_bytes = max(training_activation_bytes, evaluation_activation_bytes)
    activation_gib = activation_bytes / GIB

    largest_layer_parameters = max(1, text_parameters // max(1, shape.num_hidden_layers))
    communication_bytes = 0.0
    communication_buffer = _communication_buffer_bytes()
    if zero_stage == 2:
        communication_bytes = min(gradient_device_bytes, 2 * communication_buffer)
    elif zero_stage == 3:
        communication_bytes = largest_layer_parameters * dtype_bytes * 1.5
    elif devices > 1:
        communication_bytes = min(gradient_bytes, 2 * communication_buffer)

    runtime_bytes = (1.0 + (0.35 if quantization_enabled else 0.0)) * GIB
    subtotal_bytes = persistent_gib * GIB + activation_bytes + communication_bytes + runtime_bytes
    fragmentation_ratio = 0.12 if quantization_enabled else 0.08
    fragmentation_bytes = subtotal_bytes * fragmentation_ratio
    workspace_gib = (communication_bytes + runtime_bytes + fragmentation_bytes) / GIB
    uncalibrated_gib = max(1.0, persistent_gib + activation_gib + workspace_gib)
    calibration_key = _calibration_bucket(
        shape,
        finetuning_type=finetuning_type,
        quantization_bit=quantization_bit,
        compute_type=compute_type,
        cutoff_len=cutoff_len,
        batch_size=batch_size,
        attention_backend=attention_backend,
        deepspeed_stage=deepspeed_stage,
        fsdp_strategy=fsdp_strategy,
        stage=stage,
        offload=offload,
        offload_target=offload_target,
        booster=booster,
        lora_target=lora_target,
        optimizer=("adam-mini" if use_adam_mini else "muon" if use_muon else optimizer),
        is_multimodal=is_multimodal or shape.is_multimodal,
    )
    calibration_factor, calibration_samples = get_calibration(calibration_key) if apply_calibration else (1.0, 0)
    estimated_gib = max(persistent_gib + activation_gib, uncalibrated_gib * calibration_factor)
    workspace_gib = max(0.0, estimated_gib - persistent_gib - activation_gib)

    return MemoryEstimate(
        estimated_gib=round(estimated_gib, 2),
        recommended_gib=round(estimated_gib * SAFETY_MARGIN, 2),
        parameter_count=shape.parameter_count,
        persistent_gib=round(persistent_gib, 2),
        activation_gib=round(activation_gib, 2),
        workspace_gib=round(workspace_gib, 2),
        per_device=True,
        weight_size_gib=round(shape.weight_size_bytes / GIB, 2),
        model_gib=round(model_gib, 2),
        trainable_state_gib=round(trainable_state_gib, 2),
        trainable_parameter_count=trainable_parameters,
        peak_kind=peak_kind,
        uncalibrated_gib=round(uncalibrated_gib, 2),
        calibration_factor=round(calibration_factor, 4),
        calibration_samples=calibration_samples,
        calibration_key=calibration_key,
    )


def _deepspeed_memory_settings(value: Any) -> tuple[str, bool, str]:
    if not value:
        return "none", False, "cpu"
    path = Path(str(value))
    try:
        with open(path, encoding="utf-8") as stream:
            config = json.load(stream)
        zero = config.get("zero_optimization", {})
        stage = str(zero.get("stage", "none"))
        optimizer_device = zero.get("offload_optimizer", {}).get("device")
        parameter_device = zero.get("offload_param", {}).get("device")
        target = str(parameter_device or optimizer_device or "cpu")
        return stage, bool(optimizer_device or parameter_device), target
    except (AttributeError, OSError, TypeError, ValueError, json.JSONDecodeError):
        name = path.name.lower()
        stage = "3" if "z3" in name else "2" if "z2" in name else "none"
        return stage, "offload" in name, "nvme" if "nvme" in name else "cpu"


def estimate_training_memory_from_args(args: dict[str, Any]) -> MemoryEstimate:
    """Estimate a parsed YAML/CLI configuration for calibration metadata."""
    shape = read_model_shape(str(args.get("model_name_or_path", "")))
    deepspeed_stage, offload, offload_target = _deepspeed_memory_settings(args.get("deepspeed"))
    compute_type = (
        "pure_bf16"
        if args.get("pure_bf16")
        else "bf16"
        if args.get("bf16")
        else "fp16"
        if args.get("fp16")
        else "fp32"
    )
    fsdp = args.get("fsdp", "none")
    if isinstance(fsdp, (list, tuple)):
        fsdp = next((str(item) for item in fsdp if "shard" in str(item).lower()), "none")
    device_memory = get_device_memory_snapshot()
    return estimate_training_memory(
        shape,
        finetuning_type=str(args.get("finetuning_type", "lora")),
        quantization_bit=str(args.get("quantization_bit", "none")),
        compute_type=compute_type,
        cutoff_len=int(args.get("cutoff_len", 2048)),
        batch_size=int(args.get("per_device_train_batch_size", 1)),
        lora_rank=int(args.get("lora_rank", 8)),
        stage=str(args.get("stage", "sft")),
        deepspeed_stage=deepspeed_stage,
        offload=offload,
        device_count=max(1, device_memory.device_count),
        booster="liger_kernel" if args.get("enable_liger_kernel") else "none",
        gradient_checkpointing=bool(args.get("gradient_checkpointing", True)),
        is_multimodal=shape.is_multimodal,
        freeze_vision_tower=bool(args.get("freeze_vision_tower", True)),
        freeze_multi_modal_projector=bool(args.get("freeze_multi_modal_projector", True)),
        freeze_language_model=bool(args.get("freeze_language_model", False)),
        image_max_pixels=int(args.get("image_max_pixels", 768 * 768)),
        video_max_pixels=int(args.get("video_max_pixels", 256 * 256)),
        eval_batch_size=int(args.get("per_device_eval_batch_size", 0)),
        validation_enabled=bool(args.get("do_eval", False)),
        freeze_trainable_layers=int(args.get("freeze_trainable_layers", 2)),
        optimizer=str(args.get("optim", "adamw_torch")),
        use_badam=bool(args.get("use_badam", False)),
        badam_mode=str(args.get("badam_mode", "layer")),
        badam_update_ratio=float(args.get("badam_update_ratio", 0.05)),
        lora_target=args.get("lora_target", "all"),
        attention_backend=str(args.get("flash_attn", "sdpa")),
        cross_entropy_mode="chunked" if args.get("chunked_cross_entropy") else "auto",
        cross_entropy_chunk_size=int(args.get("cross_entropy_chunk_size", DEFAULT_CROSS_ENTROPY_CHUNK)),
        double_quantization=bool(args.get("double_quantization", True)),
        offload_target=offload_target,
        fsdp_strategy=str(fsdp),
        fsdp_shard_size=int(args.get("fsdp_shard_size", 0)),
        use_galore=bool(args.get("use_galore", False)),
        use_apollo=bool(args.get("use_apollo", False)),
        use_adam_mini=bool(args.get("use_adam_mini", False)),
        use_muon=bool(args.get("use_muon", False)),
        projection_rank=int(args.get("galore_rank", args.get("apollo_rank", 16))),
        video_num_frames=int(args.get("video_maxlen", 128)),
        use_vllm=bool(args.get("use_vllm", False)),
        vllm_gpu_util=float(args.get("vllm_gpu_util", args.get("vllm_gpu_memory_utilization", 0.0))),
        vllm_colocate=bool(args.get("vllm_colocate", True)),
        total_device_gib=float(device_memory.total_gib or 0.0),
    )


def write_memory_estimate_metadata(args: dict[str, Any]) -> Path:
    estimate = estimate_training_memory_from_args(args)
    output_path = Path(str(args["output_dir"])) / ESTIMATE_METADATA_NAME
    payload = {
        "version": 1,
        "calibration_key": estimate.calibration_key,
        "calibration_factor": estimate.calibration_factor,
        "calibration_samples": estimate.calibration_samples,
        "base_estimated_gib": estimate.uncalibrated_gib,
        "estimated_gib": estimate.estimated_gib,
        "recommended_gib": estimate.recommended_gib,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")
    return output_path


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
