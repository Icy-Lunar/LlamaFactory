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

import os
from collections.abc import Generator
from typing import TYPE_CHECKING

from ...extras.constants import PEFT_METHODS
from ...extras.misc import torch_gc
from ...extras.packages import is_gradio_available
from ...train.tuner import export_model
from ..common import get_save_dir, load_config
from ..control import list_checkpoints
from ..locales import ALERTS, LOCALES


if is_gradio_available():
    import gradio as gr


if TYPE_CHECKING:
    from gradio.components import Component

    from ..engine import Engine


GPTQ_BITS = ["8", "4", "3", "2"]


def can_quantize(checkpoint_path: str | list[str]) -> "gr.Dropdown":
    if isinstance(checkpoint_path, list) and len(checkpoint_path) != 0:
        return gr.Dropdown(value="none", interactive=False)
    else:
        return gr.Dropdown(interactive=True)


def save_model(
    lang: str,
    model_name: str,
    model_path: str,
    finetuning_type: str,
    checkpoint_path: str | list[str],
    template: str,
    export_size: int,
    export_quantization_bit: str,
    export_quantization_dataset: str,
    export_device: str,
    export_legacy_format: bool,
    export_dir: str,
) -> Generator[str, None, None]:
    user_config = load_config()
    error = ""
    if not model_path or not os.path.isdir(os.path.abspath(os.path.expanduser(model_path))):
        error = ALERTS["err_no_path"][lang]
    elif not model_name:
        error = ALERTS["err_no_model"][lang]
    elif not export_dir:
        error = ALERTS["err_no_export_dir"][lang]
    elif export_quantization_bit in GPTQ_BITS and not export_quantization_dataset:
        error = ALERTS["err_no_dataset"][lang]
    elif export_quantization_bit not in GPTQ_BITS and not checkpoint_path:
        error = ALERTS["err_no_adapter"][lang]
    elif export_quantization_bit in GPTQ_BITS and checkpoint_path and isinstance(checkpoint_path, list):
        error = ALERTS["err_gptq_lora"][lang]

    if error:
        gr.Warning(error)
        yield error
        return

    args = dict(
        model_name_or_path=model_path,
        cache_dir=user_config.get("cache_dir", None),
        finetuning_type=finetuning_type,
        template=template,
        export_dir=export_dir,
        export_hub_model_id=None,
        export_size=export_size,
        export_quantization_bit=int(export_quantization_bit) if export_quantization_bit in GPTQ_BITS else None,
        export_quantization_dataset=export_quantization_dataset,
        export_device=export_device,
        export_legacy_format=export_legacy_format,
        trust_remote_code=True,
    )

    if checkpoint_path:
        if finetuning_type in PEFT_METHODS:  # list
            args["adapter_name_or_path"] = ",".join(
                [get_save_dir(model_name, finetuning_type, adapter) for adapter in checkpoint_path]
            )
        else:  # str
            args["model_name_or_path"] = get_save_dir(model_name, finetuning_type, checkpoint_path)

    yield ALERTS["info_exporting"][lang]
    export_model(args)
    torch_gc()
    yield ALERTS["info_exported"][lang]


def create_export_tab(engine: "Engine") -> dict[str, "Component"]:
    with gr.Column(elem_classes="merge-page"):
        merge_hero = gr.HTML(LOCALES["merge_hero"]["en"]["value"])

        with gr.Group(elem_classes="merge-card merge-source-card"):
            merge_source_guide = gr.Markdown(LOCALES["merge_source_guide"]["en"]["value"])
            checkpoint_path = gr.Dropdown(multiselect=True, allow_custom_value=True)
            merge_finetuning_type = gr.State("lora")

        with gr.Accordion(
            LOCALES["merge_optional_settings"]["en"]["label"], open=False, elem_classes="merge-card"
        ) as merge_optional_settings:
            merge_settings_guide = gr.Markdown(LOCALES["merge_settings_guide"]["en"]["value"])
            with gr.Row():
                export_size = gr.Slider(minimum=1, maximum=100, value=5, step=1)
                export_quantization_bit = gr.Dropdown(choices=["none"] + GPTQ_BITS, value="none")
                export_device = gr.Radio(choices=["cpu", "auto"], value="cpu")

            with gr.Row():
                export_quantization_dataset = gr.Textbox(value="data/c4_demo.jsonl", scale=2)
                export_legacy_format = gr.Checkbox(scale=1)

        with gr.Group(elem_classes="merge-card"):
            merge_destination_guide = gr.Markdown(LOCALES["merge_destination_guide"]["en"]["value"])
            export_dir = gr.Textbox()

        export_btn = gr.Button(
            LOCALES["merge_export_btn"]["en"]["value"], variant="primary", elem_classes="merge-action"
        )
        info_box = gr.Textbox(show_label=False, interactive=False, elem_classes="merge-status")

    checkpoint_path.change(can_quantize, [checkpoint_path], [export_quantization_bit], queue=False)
    checkpoint_path.focus(
        list_checkpoints,
        [engine.manager.get_elem_by_id("top.model_name"), merge_finetuning_type],
        [checkpoint_path],
        queue=False,
    )

    export_btn.click(
        save_model,
        [
            engine.manager.get_elem_by_id("top.lang"),
            engine.manager.get_elem_by_id("top.model_name"),
            engine.manager.get_elem_by_id("top.model_path"),
            merge_finetuning_type,
            engine.manager.get_elem_by_id("top.checkpoint_path"),
            engine.manager.get_elem_by_id("top.template"),
            export_size,
            export_quantization_bit,
            export_quantization_dataset,
            export_device,
            export_legacy_format,
            export_dir,
        ],
        [info_box],
    )

    return dict(
        export_size=export_size,
        export_quantization_bit=export_quantization_bit,
        export_quantization_dataset=export_quantization_dataset,
        export_device=export_device,
        export_legacy_format=export_legacy_format,
        export_dir=export_dir,
        checkpoint_path=checkpoint_path,
        merge_export_btn=export_btn,
        merge_status=info_box,
        merge_hero=merge_hero,
        merge_source_guide=merge_source_guide,
        merge_settings_guide=merge_settings_guide,
        merge_optional_settings=merge_optional_settings,
        merge_destination_guide=merge_destination_guide,
    )
