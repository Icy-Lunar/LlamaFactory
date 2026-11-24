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

"""Hugging Face-only model chat controller for the guided WebUI."""

from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any

from transformers.utils import is_torch_npu_available

from ..chat import ChatModel
from ..data import Role
from ..extras.misc import torch_gc
from ..extras.packages import is_gradio_available
from .chat_locales import CHAT_ALERTS
from .locales import ALERTS


if TYPE_CHECKING:
    from ..chat import BaseEngine


if is_gradio_available():
    import gradio as gr


def _escape_html(text: str) -> str:
    return text.replace("<", "&lt;").replace(">", "&gt;")


def _format_response(text: str, lang: str, escape_html: bool, thought_words: tuple[str, str]) -> str:
    if thought_words[0] not in text:
        return _escape_html(text) if escape_html else text

    text = text.replace(thought_words[0], "")
    result = text.split(thought_words[1], maxsplit=1)
    if len(result) == 1:
        summary = ALERTS["info_thinking"][lang]
        thought, answer = text, ""
    else:
        summary = ALERTS["info_thought"][lang]
        thought, answer = result

    if escape_html:
        thought, answer = _escape_html(thought), _escape_html(answer)

    return (
        f"<details open><summary class='thinking-summary'><span>{summary}</span></summary>\n\n"
        f"<div class='thinking-container'>\n{thought}\n</div>\n</details>{answer}"
    )


@contextmanager
def update_attr(obj: Any, name: str, value: Any):
    old_value = getattr(obj, name, None)
    setattr(obj, name, value)
    try:
        yield
    finally:
        setattr(obj, name, old_value)


class WebChatModel(ChatModel):
    def __init__(self, demo_mode: bool = False) -> None:
        self.demo_mode = demo_mode
        self.engine: BaseEngine | None = None

    @property
    def loaded(self) -> bool:
        return self.engine is not None

    def load_model(
        self,
        lang: str,
        model_path: str,
        adapter_path: str,
        quantization_bit: str,
        infer_dtype: str,
    ) -> Generator[str, None, None]:
        if self.loaded:
            message = CHAT_ALERTS["already_loaded"][lang]
            gr.Warning(message)
            yield message
            return

        local_model = Path(model_path).expanduser()
        if not model_path or not local_model.is_dir():
            message = CHAT_ALERTS["model_missing"][lang]
            gr.Warning(message)
            yield message
            return

        local_adapter = Path(adapter_path).expanduser() if adapter_path else None
        if local_adapter is not None and not local_adapter.is_dir():
            message = CHAT_ALERTS["adapter_missing"][lang]
            gr.Warning(message)
            yield message
            return

        if self.demo_mode:
            gr.Warning(ALERTS["err_demo"][lang])
            yield ALERTS["err_demo"][lang]
            return

        yield ALERTS["info_loading"][lang]
        args = {
            "model_name_or_path": str(local_model.resolve()),
            "adapter_name_or_path": str(local_adapter.resolve()) if local_adapter else None,
            "finetuning_type": "lora",
            "template": "default",
            "infer_dtype": infer_dtype,
            "trust_remote_code": True,
        }
        if quantization_bit != "none":
            args.update(
                quantization_bit=int(quantization_bit),
                quantization_method="bnb",
                double_quantization=not is_torch_npu_available(),
            )

        try:
            super().__init__(args)
        except Exception as error:
            self.engine = None
            torch_gc()
            message = CHAT_ALERTS["load_failed"][lang].format(error=error)
            gr.Warning(message)
            yield message
            return

        yield ALERTS["info_loaded"][lang]

    def unload_model(self, lang: str) -> Generator[str, None, None]:
        if self.demo_mode:
            gr.Warning(ALERTS["err_demo"][lang])
            yield ALERTS["err_demo"][lang]
            return

        yield ALERTS["info_unloading"][lang]
        self.close()
        self.engine = None
        torch_gc()
        yield ALERTS["info_unloaded"][lang]

    @staticmethod
    def append(
        chatbot: list[dict[str, str]],
        messages: list[dict[str, str]],
        lang: str,
        query: str,
        escape_html: bool,
    ) -> tuple[list[dict[str, str]], list[dict[str, str]], str]:
        if not query.strip():
            gr.Warning(CHAT_ALERTS["empty_query"][lang])
            return chatbot, messages, query
        return (
            chatbot + [{"role": "user", "content": _escape_html(query) if escape_html else query}],
            messages + [{"role": Role.USER.value, "content": query}],
            "",
        )

    def stream(
        self,
        chatbot: list[dict[str, str]],
        messages: list[dict[str, str]],
        lang: str,
        system: str,
        max_new_tokens: int,
        top_p: float,
        temperature: float,
        seed: float | int,
        escape_html: bool,
        enable_thinking: bool,
    ) -> Generator[tuple[list[dict[str, str]], list[dict[str, str]]], None, None]:
        if not self.loaded:
            gr.Warning(CHAT_ALERTS["not_loaded"][lang])
            yield chatbot, messages
            return

        with update_attr(self.engine.template, "enable_thinking", enable_thinking):
            chatbot.append({"role": "assistant", "content": ""})
            response = ""
            for new_text in self.stream_chat(
                messages,
                system=system or None,
                max_new_tokens=max_new_tokens,
                top_p=top_p,
                temperature=temperature,
                seed=None if int(seed) < 0 else int(seed),
                skip_special_tokens=True,
            ):
                response += new_text
                output_messages = messages + [{"role": Role.ASSISTANT.value, "content": response}]
                chatbot[-1] = {
                    "role": "assistant",
                    "content": _format_response(response, lang, escape_html, self.engine.template.thought_words),
                }
                yield chatbot, output_messages
