from llamafactory.webui.memory import SAFETY_MARGIN, ModelShape, _estimate_parameter_count, estimate_training_memory


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
    return ModelShape(
        parameter_count=_estimate_parameter_count(config, config),
        hidden_size=4096,
        num_hidden_layers=32,
        vocab_size=128000,
        num_attention_heads=32,
        num_key_value_heads=8,
        intermediate_size=14336,
        source="config",
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
