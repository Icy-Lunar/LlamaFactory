import json

import gradio as gr

from llamafactory.webui.components import train as train_components
from llamafactory.webui.components.top import create_top
from llamafactory.webui.components.train import _build_wizard_summary
from llamafactory.webui.interface import create_ui
from llamafactory.webui.locales import (
    LOCALES,
    WIZARD_GUIDANCE_LOCALES,
    WIZARD_MEMORY_LOCALES,
    WIZARD_SUMMARY_LOCALES,
)
from llamafactory.webui.memory import DeviceMemory


class _FakeManager:
    def get_elem_by_id(self, elem_id: str) -> str:
        return elem_id


def test_guided_flow_exposes_only_three_parameter_branches() -> None:
    expected_values = ["recommended", "resources", "learning"]
    for guidance in WIZARD_GUIDANCE_LOCALES.values():
        assert [value for _, value in guidance["param_mode_choices"]] == expected_values
        assert len(guidance["result_labels"]) == 6


def test_training_stage_is_localized_in_summary() -> None:
    summary = _build_wizard_summary(
        "zh",
        "local-model",
        "C:/models/local-model",
        "lora",
        "4",
        "liger_kernel",
        "Supervised Fine-Tuning",
        ["demo"],
        "5e-5",
        "3.0",
        2048,
        1,
        16,
        "bf16",
        "train-output",
    )

    assert WIZARD_SUMMARY_LOCALES["zh"]["stages"]["Supervised Fine-Tuning"] in summary
    assert "Supervised Fine-Tuning" not in summary


def test_current_product_and_merge_copy_have_no_obsolete_hub_guidance() -> None:
    for lang in WIZARD_GUIDANCE_LOCALES:
        assert "Cyrene Yield" in LOCALES["title"][lang]["value"]
        assert "Hub" not in LOCALES["merge_destination_guide"][lang]["value"]


def test_live_memory_guidance_is_available_for_every_language() -> None:
    assert WIZARD_MEMORY_LOCALES.keys() == WIZARD_GUIDANCE_LOCALES.keys()
    for lang, text in WIZARD_MEMORY_LOCALES.items():
        assert text["live_intro"]
        assert len(text["labels"]) == 13
        assert set(text["peak_kinds"]) == {"training", "validation"}
        assert set(text["sources"]) == {"safetensors_metadata", "config_architecture", "weight_size"}
        assert LOCALES["wizard_live_memory_intro"][lang]["value"] == text["live_intro"]


def test_specialized_parameter_guidance_is_available_for_every_language() -> None:
    keys = (
        "common_params_label",
        "common_params_guide",
        "lora_params_guide",
        "multimodal_params_guide",
    )
    for lang, guidance in WIZARD_GUIDANCE_LOCALES.items():
        for key in keys:
            assert guidance[key]

        assert LOCALES["wizard_common_params"][lang]["label"] == guidance["common_params_label"]
        assert LOCALES["wizard_common_params_guide"][lang]["value"] == guidance["common_params_guide"]
        assert LOCALES["wizard_lora_params_guide"][lang]["value"] == guidance["lora_params_guide"]
        assert LOCALES["wizard_multimodal_params_guide"][lang]["value"] == guidance["multimodal_params_guide"]


def test_first_step_exposes_method_and_optional_quantization() -> None:
    with gr.Blocks():
        top = create_top()

    assert top["finetuning_type"].visible is True
    assert "full" in [value for _, value in top["finetuning_type"].choices]
    assert top["quantization_bit"].visible is True
    assert top["quantization_bit"].value == "none"


def test_platform_profile_can_choose_a_safe_default_compute_type(monkeypatch) -> None:
    monkeypatch.setenv("LLAMAFACTORY_DEFAULT_COMPUTE_TYPE", "fp16")
    assert train_components._default_compute_type("high") == "fp16"
    monkeypatch.setenv("LLAMAFACTORY_DEFAULT_COMPUTE_TYPE", "unsupported")
    assert train_components._default_compute_type("high") == "bf16"


def test_live_memory_assessment_uses_current_batch_size(tmp_path, monkeypatch) -> None:
    config = {
        "hidden_size": 4096,
        "intermediate_size": 14336,
        "num_attention_heads": 32,
        "num_hidden_layers": 32,
        "num_key_value_heads": 8,
        "vocab_size": 128000,
    }
    (tmp_path / "config.json").write_text(json.dumps(config), encoding="utf-8")
    (tmp_path / "model.safetensors").write_bytes(b"weights")
    monkeypatch.setattr(
        train_components,
        "get_device_memory_snapshot",
        lambda: DeviceMemory(free_gib=80.0, total_gib=80.0, device_count=1),
    )
    data = {
        "top.lang": "en",
        "top.model_path": str(tmp_path),
        "top.finetuning_type": "lora",
        "top.quantization_bit": "4",
        "top.booster": "liger_kernel",
        "train.device_count": "1",
        "train.compute_type": "bf16",
        "train.cutoff_len": 2048,
        "train.batch_size": 1,
        "train.lora_rank": 8,
        "train.training_stage": "Supervised Fine-Tuning",
        "train.ds_stage": "none",
        "train.ds_offload": False,
        "train.extra_args": "{}",
    }

    initial = train_components._assess_training_memory(data, _FakeManager())
    data["train.batch_size"] = 8
    updated = train_components._assess_training_memory(data, _FakeManager())

    assert updated[2] > initial[2]
    assert train_components._run_live_memory_estimate(data, _FakeManager()) == updated[0]


def test_all_webui_slider_defaults_are_within_bounds() -> None:
    demo = create_ui()
    invalid_sliders = [
        (component._id, component.value, component.minimum, component.maximum)
        for component in demo.blocks.values()
        if isinstance(component, gr.Slider)
        and component.value is not None
        and not component.minimum <= component.value <= component.maximum
    ]

    assert invalid_sliders == []


def test_force_cancel_returns_to_parameter_step_and_resets_acknowledgement() -> None:
    modal, acknowledgement, force_start, *pages = train_components._return_to_parameters()

    assert modal.visible is False
    assert acknowledgement.value is False
    assert force_start.interactive is False
    assert [page.visible for page in pages] == [False, False, True, False]


def test_language_switch_does_not_output_training_parameters(monkeypatch) -> None:
    from llamafactory.webui.engine import Engine

    engine = Engine(demo_mode=True)
    monkeypatch.setattr("llamafactory.webui.interface.Engine", lambda **kwargs: engine)
    demo = create_ui(demo_mode=True)
    language = engine.manager.get_elem_by_id("top.lang")
    training_controls = {
        engine.manager.get_elem_by_id(f"train.{name}")._id
        for name in ("cutoff_len", "batch_size", "learning_rate", "num_train_epochs", "lr_scheduler_type")
    }

    for event in demo.fns.values():
        if (language._id, "change") not in event.targets or event.fn == engine.change_lang:
            continue

        assert not training_controls.intersection(component._id for component in event.outputs)
