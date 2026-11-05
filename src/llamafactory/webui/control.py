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

import json
import os
from html import escape
from typing import Any

from transformers.trainer_utils import get_last_checkpoint

from ..extras.constants import (
    CHECKPOINT_NAMES,
    PEFT_METHODS,
    RUNNING_LOG,
    STAGES_USE_PAIR_DATA,
    SWANLAB_CONFIG,
    TRAINER_LOG,
    TRAINING_STAGES,
)
from ..extras.diagnostics import tail
from ..extras.packages import is_gradio_available, is_matplotlib_available
from ..extras.ploting import gen_loss_plot
from .common import DEFAULT_CONFIG_DIR, DEFAULT_DATA_DIR, get_save_dir, get_template, load_dataset_info
from .locales import ALERTS


if is_gradio_available():
    import gradio as gr


def can_quantize(finetuning_type: str) -> "gr.Dropdown":
    r"""Judge if the quantization is available in this finetuning type.

    Inputs: top.finetuning_type
    Outputs: top.quantization_bit
    """
    if finetuning_type not in PEFT_METHODS:
        return gr.Dropdown(value="none", interactive=False)
    else:
        return gr.Dropdown(interactive=True)


def can_quantize_to(
    quantization_method: str, quantization_bit: str = "none", finetuning_type: str = "lora"
) -> "gr.Dropdown":
    r"""Get the available quantization bits.

    Inputs: top.quantization_method, top.quantization_bit, top.finetuning_type
    Outputs: top.quantization_bit
    """
    # The guided product has one quantization backend, including restored configurations.
    available_bits = ["none", "8", "4"]

    interactive = finetuning_type in PEFT_METHODS
    selected_bit = quantization_bit if interactive and quantization_bit in available_bits else "none"
    return gr.Dropdown(value=selected_bit, interactive=interactive)


def change_stage(training_stage: str = list(TRAINING_STAGES.keys())[0]) -> tuple[list[str], bool]:
    r"""Modify states after changing the training stage.

    Inputs: train.training_stage
    Outputs: train.dataset, train.packing
    """
    return [], TRAINING_STAGES[training_stage] == "pt"


def get_local_model_info(model_path: str) -> tuple[str, str]:
    r"""Infer the display name and conversation template from a local model directory."""
    if not model_path or not os.path.isdir(os.path.abspath(os.path.expanduser(model_path))):
        return "", "default"

    model_name = os.path.basename(os.path.normpath(model_path))
    return model_name, get_template(model_name)


def check_template(lang: str, template: str) -> None:
    r"""Check if an instruct model is used.

    Please use queue=True to show the warning message.

    Inputs: top.lang, top.template
    """
    if template == "default":
        gr.Warning(ALERTS["warn_no_instruct"][lang])


def get_trainer_info(lang: str, output_path: os.PathLike) -> tuple[str, "gr.Slider", dict[str, Any]]:
    r"""Get training information for the progress monitor."""
    running_log = ""
    running_progress = gr.Slider(visible=False)
    running_info = {}

    running_log_path = os.path.join(output_path, "webui_subprocess.log")
    if not os.path.isfile(running_log_path):
        running_log_path = os.path.join(output_path, RUNNING_LOG)
    if os.path.isfile(running_log_path):
        running_log = f"<pre>{escape(tail(running_log_path))}</pre>"

    trainer_log_path = os.path.join(output_path, TRAINER_LOG)
    if os.path.isfile(trainer_log_path):
        trainer_log: list[dict[str, Any]] = []
        for line in tail(trainer_log_path, 256000).splitlines():
            try:
                item = json.loads(line)
                if isinstance(item, dict) and all(
                    key in item
                    for key in ("percentage", "current_steps", "total_steps", "elapsed_time", "remaining_time")
                ):
                    trainer_log.append(item)
            except (ValueError, TypeError):
                continue  # Writer may be midway through appending the last JSON record.

        if len(trainer_log) != 0:
            latest_log = trainer_log[-1]
            percentage = min(100, max(0, latest_log["percentage"]))
            label = "Running {:d}/{:d}: {} < {}".format(
                latest_log["current_steps"],
                latest_log["total_steps"],
                latest_log["elapsed_time"],
                latest_log["remaining_time"],
            )
            running_progress = gr.Slider(label=label, value=percentage, visible=True)

            if is_matplotlib_available():
                running_info["loss_viewer"] = gr.Plot(gen_loss_plot(trainer_log))

    swanlab_config_path = os.path.join(output_path, SWANLAB_CONFIG)
    if os.path.isfile(swanlab_config_path):
        with open(swanlab_config_path, encoding="utf-8") as f:
            swanlab_public_config = json.load(f)
            swanlab_link = swanlab_public_config["cloud"]["experiment_url"]
            if swanlab_link is not None:
                running_info["swanlab_link"] = gr.Markdown(
                    ALERTS["info_swanlab_link"][lang] + swanlab_link, visible=True
                )

    return running_log, running_progress, running_info


def list_checkpoints(model_name: str, finetuning_type: str, reset_selection: bool = True) -> "gr.Dropdown":
    r"""List all available checkpoints.

    Inputs: top.model_name, top.finetuning_type
    Outputs: top.checkpoint_path
    """
    checkpoints = []
    if model_name:
        save_dir = get_save_dir(model_name, finetuning_type)
        if save_dir and os.path.isdir(save_dir):
            for checkpoint in os.listdir(save_dir):
                if os.path.isdir(os.path.join(save_dir, checkpoint)) and any(
                    os.path.isfile(os.path.join(save_dir, checkpoint, name)) for name in CHECKPOINT_NAMES
                ):
                    checkpoints.append(checkpoint)

    if not reset_selection:
        return gr.Dropdown(choices=checkpoints, multiselect=finetuning_type in PEFT_METHODS)
    elif finetuning_type in PEFT_METHODS:
        return gr.Dropdown(value=[], choices=checkpoints, multiselect=True)
    else:
        return gr.Dropdown(value=None, choices=checkpoints, multiselect=False)


def list_config_paths(current_time: str) -> "gr.Dropdown":
    r"""List all the saved configuration files.

    Inputs: train.current_time
    Outputs: train.config_path
    """
    config_files = [f"{current_time}.yaml"]
    if os.path.isdir(DEFAULT_CONFIG_DIR):
        for file_name in os.listdir(DEFAULT_CONFIG_DIR):
            if file_name.endswith(".yaml") and file_name not in config_files:
                config_files.append(file_name)

    return gr.Dropdown(choices=config_files)


def list_datasets(dataset_dir: str = None, training_stage: str = list(TRAINING_STAGES.keys())[0]) -> "gr.Dropdown":
    r"""List all available datasets in the dataset dir for the training stage.

    Inputs: *.dataset_dir, *.training_stage
    Outputs: *.dataset
    """
    dataset_info = load_dataset_info(dataset_dir if dataset_dir is not None else DEFAULT_DATA_DIR)
    ranking = TRAINING_STAGES[training_stage] in STAGES_USE_PAIR_DATA
    datasets = [k for k, v in dataset_info.items() if v.get("ranking", False) == ranking]
    return gr.Dropdown(choices=datasets)


def list_output_dirs(model_name: str | None, finetuning_type: str, current_time: str) -> "gr.Dropdown":
    r"""List all the directories that can resume from.

    Inputs: top.model_name, top.finetuning_type, train.current_time
    Outputs: train.output_dir
    """
    output_dirs = [f"train_{current_time}"]
    if model_name:
        save_dir = get_save_dir(model_name, finetuning_type)
        if save_dir and os.path.isdir(save_dir):
            for folder in os.listdir(save_dir):
                output_dir = os.path.join(save_dir, folder)
                if os.path.isdir(output_dir) and get_last_checkpoint(output_dir) is not None:
                    output_dirs.append(folder)

    return gr.Dropdown(choices=output_dirs)
