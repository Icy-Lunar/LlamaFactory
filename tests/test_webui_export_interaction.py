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
        ("hqq", "2", "lora", "2", True),
        ("eetq", "4", "lora", "none", True),
        ("bnb", "8", "lora", "8", True),
        ("hqq", "4", "full", "none", False),
    ],
)
def test_changing_quantization_method_preserves_only_compatible_choices(
    method, bit, finetuning_type, expected_bit, interactive
) -> None:
    update = can_quantize_to(method, bit, finetuning_type)

    assert update.value == expected_bit
    assert update.interactive is interactive
