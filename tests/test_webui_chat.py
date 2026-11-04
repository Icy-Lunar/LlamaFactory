from pathlib import Path

import gradio as gr

from llamafactory.extras.constants import EngineName
from llamafactory.hparams import ModelArguments
from llamafactory.webui.chat_locales import CHAT_ALERTS, CHAT_LOCALES, LANGUAGES
from llamafactory.webui.chatter import WebChatModel
from llamafactory.webui.engine import Engine
from llamafactory.webui.interface import _switch_workspace, create_ui


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_chat_workspace_is_present_and_has_no_backend_selector(monkeypatch):
    engine = Engine(demo_mode=True)
    monkeypatch.setattr("llamafactory.webui.interface.Engine", lambda **kwargs: engine)
    create_ui(demo_mode=False)

    assert engine.manager.has_elem("workspace.chat_workspace_btn")
    assert engine.manager.has_elem("chat.chat_model_path")
    assert engine.manager.has_elem("chat.chat_adapter_path")
    assert engine.manager.has_elem("chat.chatbot")
    assert not engine.manager.has_elem("chat.chat_template")
    assert not engine.manager.has_elem("chat.infer_backend")
    assert not engine.manager.has_elem("chat.extra_args")


def test_chat_workspace_switch_shows_only_chat_panel():
    updates = _switch_workspace("zh", "chat")
    assert [button.variant for button in updates[:3]] == ["secondary", "primary", "secondary"]
    assert [panel.visible for panel in updates[3:]] == [False, True, False]


def test_chat_locales_cover_every_supported_language():
    assert set(CHAT_ALERTS["model_missing"]) == set(LANGUAGES)
    for resource in CHAT_LOCALES.values():
        assert set(resource) == set(LANGUAGES)


def test_chat_rejects_missing_local_model_without_loading(monkeypatch, tmp_path):
    warnings = []
    monkeypatch.setattr(gr, "Warning", warnings.append)
    chatter = WebChatModel()
    messages = list(chatter.load_model("zh", str(tmp_path / "missing"), "", "none", "auto"))
    assert messages == [CHAT_ALERTS["model_missing"]["zh"]]
    assert warnings == messages
    assert not chatter.loaded


def test_chat_append_keeps_huggingface_message_format():
    chatbot, messages, query = WebChatModel.append([], [], "en", "hello", True)
    assert chatbot == [{"role": "user", "content": "hello"}]
    assert messages == [{"role": "user", "content": "hello"}]
    assert query == ""


def test_chat_model_always_uses_default_template(monkeypatch, tmp_path):
    captured_args = {}

    def fake_init(self, args):
        captured_args.update(args)
        self.engine = object()

    monkeypatch.setattr("llamafactory.webui.chatter.ChatModel.__init__", fake_init)
    chatter = WebChatModel()
    list(chatter.load_model("en", str(tmp_path), "", "none", "auto"))
    assert captured_args["template"] == "default"


def test_only_huggingface_inference_backend_remains_in_source():
    assert list(EngineName) == [EngineName.HF]
    fields = ModelArguments.__dataclass_fields__
    assert "infer_backend" not in fields
    assert "vllm_config" not in fields
    assert "sglang_config" not in fields
    for relative in (
        "src/llamafactory/chat/vllm_engine.py",
        "src/llamafactory/chat/sglang_engine.py",
        "requirements/vllm.txt",
        "requirements/sglang.txt",
        "scripts/vllm_infer.py",
        "examples/inference",
    ):
        assert not (PROJECT_ROOT / relative).exists()
