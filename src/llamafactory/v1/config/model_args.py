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
from dataclasses import dataclass, field

from ..utils.types import AttentionFunction
from .arg_utils import ModelClass, PluginConfig, get_plugin_config


@dataclass
class ModelArguments:
    model: str = field(
        default="",
        metadata={"help": "Path to an existing local directory containing the base model weights."},
    )
    custom_chat_template: str | None = field(
        default=None,
        metadata={"help": "Custom Jinja2 chat template string. Overrides the model's built-in template."},
    )
    trust_remote_code: bool = field(
        default=False,
        metadata={"help": "Trust remote code from Hugging Face."},
    )
    flash_attn: AttentionFunction = field(
        default=AttentionFunction.SDPA,
        metadata={
            "help": "Attention implementation to use: eager, sdpa, or flash_attention_2. SDPA is the default implementation for models."
        },
    )
    model_class: ModelClass = field(
        default=ModelClass.LLM,
        metadata={"help": "Model class from Hugging Face."},
    )
    init_config: PluginConfig | None = field(
        default=None,
        metadata={"help": "Initialization configuration for the model."},
    )
    peft_config: PluginConfig | None = field(
        default=None,
        metadata={"help": "PEFT configuration for the model."},
    )
    kernel_config: PluginConfig | None = field(
        default=None,
        metadata={"help": "Kernel configuration for the model."},
    )
    quant_config: PluginConfig | None = field(
        default=None,
        metadata={"help": "Quantization configuration for the model."},
    )

    def __post_init__(self) -> None:
        model_path = os.path.abspath(os.path.expanduser(self.model)) if self.model else ""
        if not model_path or not os.path.isdir(model_path):
            raise ValueError("`model` must be an existing local model directory.")

        self.model = model_path
        supported_flash_attn = [item.value for item in AttentionFunction]
        if self.flash_attn not in supported_flash_attn:
            raise ValueError(
                f"Unsupported `flash_attn`: {self.flash_attn}. Supported values are: {supported_flash_attn}."
            )

        self.init_config = get_plugin_config(self.init_config)
        self.peft_config = get_plugin_config(self.peft_config)
        self.kernel_config = get_plugin_config(self.kernel_config)
        self.quant_config = get_plugin_config(self.quant_config)
