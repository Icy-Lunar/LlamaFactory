import inspect

import gradio as gr
import pytest

from llamafactory.extras.constants import METHODS
from llamafactory.webui.components.top import create_top
from llamafactory.webui.engine import Engine
from llamafactory.webui.help import field_help
from llamafactory.webui.help_locales import FIELD_HELP, FINETUNING_LABELS
from llamafactory.webui.interface import create_ui
from llamafactory.webui.locales import LOCALES, get_finetuning_label


@pytest.mark.parametrize("lang", ["en", "zh", "ru", "ko", "ja"])
def test_method_labels_are_localized_without_changing_config_values(lang):
    choices = LOCALES["finetuning_type"][lang]["choices"]
    assert [value for _, value in choices] == METHODS
    for label, value in choices:
        assert label != value
        assert get_finetuning_label(value, lang) == label
    assert set(FINETUNING_LABELS[lang]) == set(METHODS)


def test_quantization_and_acceleration_have_only_fixed_supported_backends():
    with gr.Blocks():
        controls = create_top()
    assert controls["quantization_method"].choices == [("bitsandbytes (bnb)", "bnb")]
    assert [value for _, value in controls["booster"].choices] == ["liger_kernel", "none"]
    assert not controls["quantization_method"].interactive
    assert not controls["booster"].interactive
    assert controls["quantization_bit"].value == "none"


def test_help_markup_is_accessible_and_escapes_resource_text():
    html = field_help('A "field"', "<script>unsafe</script>", "en", "top.test")
    assert 'role="button" tabindex="0"' in html
    assert 'role="tooltip"' in html
    assert 'id="help-top-test"' in html
    assert "&lt;script&gt;" in html
    assert "<script>" not in html


def test_all_registered_form_fields_have_translated_help(monkeypatch):
    engine = Engine(demo_mode=True)
    monkeypatch.setattr("llamafactory.webui.interface.Engine", lambda **kwargs: engine)
    create_ui(demo_mode=False)
    for lang in FINETUNING_LABELS:
        updates = engine.change_lang(lang)
        for name, component in engine.manager.get_elem_iter():
            if (
                "info" not in inspect.signature(type(component)).parameters
                or component.visible is False
                or component.show_label is False
            ):
                continue
            # Hidden legacy controls can still be registered for old configuration files.
            if name not in LOCALES or "label" not in LOCALES[name][lang]:
                continue
            assert LOCALES[name][lang].get("info"), (name, lang)
            assert 'class="field-help"' in updates[component].info, (name, lang)
            assert "value" not in updates[component].constructor_args, (name, lang)
    for translations in FIELD_HELP.values():
        assert set(translations) == set(FINETUNING_LABELS)


def test_resume_preserves_help_for_restored_model_path(monkeypatch):
    monkeypatch.setattr(
        "llamafactory.webui.engine.load_config",
        lambda: {"lang": "zh", "last_model_path": "C:/models/example", "last_model": "example"},
    )
    engine = Engine()
    monkeypatch.setattr("llamafactory.webui.interface.Engine", lambda **kwargs: engine)
    create_ui(demo_mode=True)
    updates = next(engine.resume())
    restored = updates[engine.manager.get_elem_by_id("top.model_path")]
    assert restored.value == "C:/models/example"
    assert 'class="field-help"' in restored.info
