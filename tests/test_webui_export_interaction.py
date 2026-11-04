import gradio as gr
import pytest

from llamafactory.webui.components.export import create_export_tab, save_model
from llamafactory.webui.components.top import create_top
from llamafactory.webui.control import can_quantize_to, list_checkpoints
from llamafactory.webui.engine import Engine


def test_merge_action_uses_adapter_selected_in_merge_workspace() -> None:
    engine = Engine(demo_mode=True)
    with gr.Blocks() as demo:
        top = create_top()
        engine.manager.add_elems("top", top)
        merge = create_export_tab(engine)

    merge_action = next(event for event in demo.fns.values() if event.fn is save_model)

    assert merge_action.inputs[4] is merge["checkpoint_path"]
    assert merge_action.inputs[4] is not top["checkpoint_path"]
    assert "export_quantization_bit" not in merge
    assert "export_quantization_dataset" not in merge


def test_merge_remains_available_without_a_second_quantization_backend(tmp_path, monkeypatch):
    captured = []
    monkeypatch.setattr("llamafactory.webui.components.export.export_model", captured.append)
    monkeypatch.setattr("llamafactory.webui.components.export.torch_gc", lambda: None)
    monkeypatch.setattr("llamafactory.webui.components.export.load_config", lambda: {})
    list(save_model("en", "model", str(tmp_path), "lora", ["adapter"], "default", 5, "cpu", False, "merged"))
    assert len(captured) == 1
    assert captured[0]["export_quantization_bit"] is None
    assert captured[0]["adapter_name_or_path"]


def test_reopening_adapter_selectors_preserves_existing_selection() -> None:
    engine = Engine(demo_mode=True)
    with gr.Blocks() as demo:
        top = create_top()
        engine.manager.add_elems("top", top)
        merge = create_export_tab(engine)

    for selector in (top["checkpoint_path"], merge["checkpoint_path"]):
        focus_action = next(event for event in demo.fns.values() if (selector._id, "focus") in event.targets)
        refresh = focus_action.fn("", "lora")
        assert "value" not in refresh.constructor_args

    assert list_checkpoints("", "lora").constructor_args["value"] == []


@pytest.mark.parametrize(
    ("method", "bit", "finetuning_type", "expected_bit", "interactive"),
    [
        ("hqq", "2", "lora", "none", True),
        ("eetq", "4", "lora", "4", True),
        ("bnb", "8", "lora", "8", True),
        ("hqq", "4", "full", "none", False),
    ],
)
def test_restored_quantization_uses_only_bnb_compatible_bits(
    method, bit, finetuning_type, expected_bit, interactive
) -> None:
    update = can_quantize_to(method, bit, finetuning_type)

    assert update.value == expected_bit
    assert update.interactive is interactive
