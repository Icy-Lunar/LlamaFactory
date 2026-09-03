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

from typing import TYPE_CHECKING

from ...data import TEMPLATES
from ...extras.constants import METHODS
from ...extras.packages import is_gradio_available
from ..common import save_config
from ..control import can_quantize, can_quantize_to, check_template, get_local_model_info, list_checkpoints
from ..locales import LOCALES


if is_gradio_available():
    import gradio as gr


if TYPE_CHECKING:
    from gradio.components import Component


def create_top() -> dict[str, "Component"]:
    with gr.Row(elem_classes="compact-language-row"):
        lang = gr.Dropdown(choices=["en", "ru", "zh", "ko", "ja"], value="zh", scale=1)

    with gr.Row():
        model_name = gr.Textbox(visible=False, interactive=False)
        model_path = gr.Textbox(scale=1)

    with gr.Accordion(LOCALES["manual_settings"]["en"]["label"], open=False) as manual_settings:
        with gr.Row():
            finetuning_type = gr.Dropdown(choices=METHODS, value="lora", scale=1)
            checkpoint_path = gr.Dropdown(multiselect=True, allow_custom_value=True, scale=6)

        with gr.Row():
            quantization_bit = gr.Dropdown(choices=["none", "8", "4"], value="none", allow_custom_value=True)
            quantization_method = gr.Dropdown(choices=["bnb", "hqq", "eetq"], value="bnb")
            template = gr.Dropdown(choices=list(TEMPLATES.keys()), value="default")
            rope_scaling = gr.Dropdown(choices=["none", "linear", "dynamic", "yarn", "llama3"], value="none")
            booster = gr.Dropdown(choices=["liger_kernel", "flashattn2", "unsloth"], value="liger_kernel")

    model_path.input(get_local_model_info, [model_path], [model_name, template], queue=False).then(
        save_config, inputs=[lang, model_name, model_path], queue=False
    ).then(list_checkpoints, [model_name, finetuning_type], [checkpoint_path], queue=False).then(
        check_template, [lang, template]
    )
    finetuning_type.change(can_quantize, [finetuning_type], [quantization_bit], queue=False).then(
        list_checkpoints, [model_name, finetuning_type], [checkpoint_path], queue=False
    )
    checkpoint_path.focus(list_checkpoints, [model_name, finetuning_type], [checkpoint_path], queue=False)
    quantization_method.change(can_quantize_to, [quantization_method], [quantization_bit], queue=False)
    return dict(
        lang=lang,
        manual_settings=manual_settings,
        model_name=model_name,
        model_path=model_path,
        finetuning_type=finetuning_type,
        checkpoint_path=checkpoint_path,
        quantization_bit=quantization_bit,
        quantization_method=quantization_method,
        template=template,
        rope_scaling=rope_scaling,
        booster=booster,
    )
