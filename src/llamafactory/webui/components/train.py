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
from html import escape
from typing import TYPE_CHECKING, Any

from transformers.trainer_utils import SchedulerType

from ...extras.constants import TRAINING_STAGES
from ...extras.misc import get_device_count
from ...extras.packages import is_gradio_available
from ..common import DEFAULT_DATA_DIR
from ..control import change_stage, list_checkpoints, list_datasets, list_output_dirs
from ..locales import LOCALES, WIZARD_GUIDANCE_LOCALES, WIZARD_MEMORY_LOCALES, WIZARD_SUMMARY_LOCALES
from ..memory import estimate_training_memory, get_device_memory_snapshot, read_model_shape
from .data import create_preview_box
from .top import create_top


if is_gradio_available():
    import gradio as gr


if TYPE_CHECKING:
    from gradio.components import Component

    from ..engine import Engine


def _localized_value(key: str) -> str:
    return LOCALES[key]["en"]["value"]


def _show_wizard_step(step: int) -> tuple[Any, Any, Any, Any]:
    return tuple(gr.Column(visible=index == step) for index in range(1, 5))


def _guidance_text(lang: str | None) -> dict[str, Any]:
    return WIZARD_GUIDANCE_LOCALES.get(lang or "en", WIZARD_GUIDANCE_LOCALES["en"])


def _wizard_alert(message: str) -> str:
    if not message:
        return ""

    return f'<div class="oobe-alert" role="alert"><span aria-hidden="true">!</span>{escape(message)}</div>'


def _detect_hardware_profile() -> str:
    device_memory = get_device_memory_snapshot()
    if device_memory.device_count > 1:
        return "multi"
    if device_memory.total_gib is None:
        return "mid"
    if device_memory.total_gib >= 24:
        return "high"
    if device_memory.total_gib >= 12:
        return "mid"
    return "low"


def _recommend_training_setup(
    lang: str | None,
    goal: str,
    hardware: str,
    model_path: str,
    priority: str,
) -> tuple[Any, ...]:
    text = _guidance_text(lang)
    stage = {
        "instruction": "Supervised Fine-Tuning",
        "preference": "DPO",
        "pretrain": "Pre-Training",
    }.get(goal, "Supervised Fine-Tuning")

    capacity = {"low": 0, "mid": 1, "high": 2, "multi": 3}.get(hardware, 1)
    inspection_error = False
    try:
        model_shape = read_model_shape(model_path)
        weight_size_gib = model_shape.weight_size_bytes / (1024**3)
        pressure = 0 if weight_size_gib <= 8 else 1 if weight_size_gib <= 20 else 2 if weight_size_gib <= 60 else 3
    except (OSError, ValueError, json.JSONDecodeError):
        weight_size_gib = 0.0
        pressure = 3
        inspection_error = True

    batch_size = {"low": 1, "mid": 2, "high": 4, "multi": 8}.get(hardware, 2)
    cutoff_len = {"low": 1024, "mid": 2048, "high": 4096, "multi": 4096}.get(hardware, 2048)

    if pressure > capacity:
        batch_size = 1
        cutoff_len = min(cutoff_len, 1024)

    finetuning_type = "lora"
    if priority == "quality" and pressure == 0 and hardware in {"high", "multi"}:
        finetuning_type = "full"

    quantization_bit = "none"
    if finetuning_type != "full" and (
        hardware in {"low", "mid"} or pressure > capacity or pressure == 3 or priority == "memory"
    ):
        quantization_bit = "4"

    if priority == "memory":
        batch_size = max(1, batch_size // 2)
        cutoff_len = min(cutoff_len, 1024)
    elif priority == "speed" and pressure <= capacity:
        batch_size = min(16, batch_size * 2)
    elif priority == "quality" and pressure <= capacity:
        cutoff_len = min(8192, cutoff_len * 2)

    target_batch = 32 if hardware in {"high", "multi"} or priority == "speed" else 16
    gradient_accumulation_steps = max(1, (target_batch + batch_size - 1) // batch_size)
    compute_type = "fp16" if hardware == "low" else "bf16"
    learning_rate = (
        "2e-5"
        if finetuning_type == "full"
        else "1e-5"
        if goal == "preference"
        else "1e-4"
        if goal == "pretrain"
        else "5e-5"
    )
    num_train_epochs = {"instruction": "3.0", "preference": "2.0", "pretrain": "1.0"}.get(goal, "3.0")
    ds_stage = "2" if hardware == "multi" else "none"
    effective_batch = batch_size * gradient_accumulation_steps
    labels = text["result_labels"]
    values = (
        text["weight_size"].format(value=weight_size_gib),
        finetuning_type,
        text["none"] if quantization_bit == "none" else f"{quantization_bit}-bit",
        compute_type,
        text["tokens"].format(value=cutoff_len),
        text["effective_batch"].format(value=effective_batch),
    )
    if inspection_error:
        result_html = _wizard_alert(text["model_scan_error"])
    else:
        result_items = "".join(
            f"<div><span>{escape(label)}</span><strong>{escape(value)}</strong></div>"
            for label, value in zip(labels, values, strict=True)
        )
        result_html = (
            '<section class="oobe-profile-result">'
            f'<header><span aria-hidden="true">✓</span><div><strong>{escape(text["result_title"])}</strong>'
            f"<p>{escape(text['result_intro'])}</p></div></header>"
            f'<div class="oobe-profile-grid">{result_items}</div>'
            f'<p class="oobe-profile-reason">{escape(text[f"reason_{priority}"])}</p>'
            f"<footer>{escape(text['result_footer'])}</footer></section>"
        )
    param_mode = (
        "resources" if priority in {"memory", "speed"} else "learning" if priority == "quality" else "recommended"
    )

    return (
        stage,
        finetuning_type,
        quantization_bit,
        "bnb",
        compute_type,
        cutoff_len,
        batch_size,
        gradient_accumulation_steps,
        learning_rate,
        num_train_epochs,
        "cosine",
        ds_stage,
        False,
        "liger_kernel",
        result_html,
        not inspection_error,
        param_mode,
        *_show_param_branch(param_mode),
    )


def _validate_model_step(
    lang: str | None,
    profile_ready: bool,
    model_path: str | None,
) -> tuple[Any, ...]:
    text = _guidance_text(lang)
    error = ""
    if not profile_ready:
        error = text["error_profile"]
    elif not model_path or not model_path.strip():
        error = text["error_path"]
    return (_wizard_alert(error), *_show_wizard_step(1 if error else 2))


def _validate_data_step(lang: str | None, dataset: list[str] | None) -> tuple[Any, ...]:
    error = "" if dataset else _guidance_text(lang)["error_dataset"]
    return (_wizard_alert(error), *_show_wizard_step(2 if error else 3))


def _show_param_branch(mode: str) -> tuple[Any, Any]:
    return gr.Group(visible=mode == "resources"), gr.Group(visible=mode == "learning")


def _memory_text(lang: str | None) -> dict[str, Any]:
    return WIZARD_MEMORY_LOCALES.get(lang or "en", WIZARD_MEMORY_LOCALES["en"])


def _build_memory_report(
    lang: str | None,
    status: str,
    weight_size_gib: float,
    parameter_count: int,
    estimated_gib: float,
    recommended_gib: float,
    free_gib: float | None,
    total_gib: float | None,
    device_count: int,
    source: str,
) -> str:
    text = _memory_text(lang)
    labels = text["labels"]
    available = text["unknown"] if free_gib is None or total_gib is None else f"{free_gib:.2f} / {total_gib:.2f} GiB"
    values = (
        f"{weight_size_gib:.2f} GiB",
        f"{parameter_count / 1_000_000_000:.2f}B",
        f"{estimated_gib:.2f} GiB",
        f"{recommended_gib:.2f} GiB",
        available,
        str(device_count),
        text["local_source"] if source == "local_weights" else text["unavailable_source"],
    )
    rows = "".join(
        f"<div><span>{escape(label)}</span><strong>{escape(value)}</strong></div>"
        for label, value in zip(labels, values, strict=True)
    )
    return (
        f'<section class="oobe-memory-report is-{status}" role="status">'
        f'<header><span aria-hidden="true">{"✓" if status == "safe" else "!"}</span><div>'
        f"<strong>{escape(text['titles'][status])}</strong>"
        f"<p>{escape(text['descriptions'][status])}</p></div></header>"
        f'<div class="oobe-memory-grid">{rows}</div></section>'
    )


def _build_force_warning(
    lang: str | None,
    estimated_gib: float | None,
    recommended_gib: float | None,
    free_gib: float | None,
) -> str:
    text = _memory_text(lang)
    available = text["unknown"] if free_gib is None else f"{free_gib:.2f} GiB"
    metrics = (
        ""
        if estimated_gib is None or recommended_gib is None
        else (
            '<div class="oobe-risk-metrics">'
            f"<strong>{estimated_gib:.2f} GiB</strong><span>+10%</span>"
            f"<strong>{recommended_gib:.2f} GiB</strong><span>≤</span><strong>{escape(available)}</strong></div>"
        )
    )
    return (
        '<section class="oobe-risk-dialog" role="alertdialog" aria-modal="true">'
        f'<div class="oobe-risk-icon" aria-hidden="true">!</div><h2>{escape(text["risk_title"])}</h2>'
        f"<p>{escape(text['risk_body'])}</p>"
        f"{metrics}"
        f"<p>{escape(text['risk_action'])}</p></section>"
    )


def _assess_training_memory(
    data: dict[Any, Any], manager: Any
) -> tuple[str, str, float | None, float | None, float | None]:
    get = lambda elem_id, default=None: data.get(manager.get_elem_by_id(elem_id), default)
    lang = get("top.lang", "en")
    device_memory = get_device_memory_snapshot()
    configured_devices = max(1, int(get("train.device_count", 1) or 1))
    device_count = device_memory.device_count or configured_devices
    try:
        model_shape = read_model_shape(get("top.model_path", ""))
    except (OSError, ValueError, json.JSONDecodeError):
        text = _memory_text(lang)
        report = (
            '<section class="oobe-memory-report is-uncertain" role="status">'
            f'<header><span aria-hidden="true">!</span><div><strong>{escape(text["titles"]["uncertain"])}</strong>'
            f"<p>{escape(text['model_read_error'])}</p></div></header></section>"
        )
        return report, "uncertain", None, None, device_memory.free_gib

    try:
        extra_args = json.loads(get("train.extra_args", "{}") or "{}")
    except json.JSONDecodeError:
        extra_args = {}
    gradient_checkpointing = not bool(extra_args.get("disable_gradient_checkpointing", False))
    if "gradient_checkpointing" in extra_args:
        gradient_checkpointing = bool(extra_args["gradient_checkpointing"])

    estimate = estimate_training_memory(
        model_shape,
        finetuning_type=get("top.finetuning_type", "lora"),
        quantization_bit=get("top.quantization_bit", "none"),
        compute_type=get("train.compute_type", "bf16"),
        cutoff_len=int(get("train.cutoff_len", 2048)),
        batch_size=int(get("train.batch_size", 1)),
        lora_rank=int(get("train.lora_rank", 8)),
        stage=TRAINING_STAGES.get(get("train.training_stage"), "sft"),
        deepspeed_stage=get("train.ds_stage", "none"),
        offload=bool(get("train.ds_offload", False)),
        device_count=device_count,
        booster=get("top.booster", "liger_kernel"),
        gradient_checkpointing=gradient_checkpointing,
    )

    if device_memory.free_gib is None:
        status = "uncertain"
    elif device_memory.free_gib < estimate.estimated_gib:
        status = "insufficient"
    elif device_memory.free_gib < estimate.recommended_gib:
        status = "below"
    else:
        status = "safe"

    report = _build_memory_report(
        lang,
        status,
        estimate.weight_size_gib,
        estimate.parameter_count,
        estimate.estimated_gib,
        estimate.recommended_gib,
        device_memory.free_gib,
        device_memory.total_gib,
        device_count,
        model_shape.source,
    )
    return report, status, estimate.estimated_gib, estimate.recommended_gib, device_memory.free_gib


def _run_live_memory_estimate(data: dict[Any, Any], manager: Any) -> str:
    report, *_ = _assess_training_memory(data, manager)
    return report


def _run_memory_preflight(data: dict[Any, Any], manager: Any) -> tuple[Any, ...]:
    get = lambda elem_id, default=None: data.get(manager.get_elem_by_id(elem_id), default)
    lang = get("top.lang", "en")
    report, status, estimated_gib, recommended_gib, free_gib = _assess_training_memory(data, manager)
    warning = "" if status == "safe" else _build_force_warning(lang, estimated_gib, recommended_gib, free_gib)
    safe = status == "safe"
    return (
        report,
        gr.Button(visible=safe),
        gr.Group(visible=not safe),
        warning,
        gr.Checkbox(value=False),
        gr.Button(interactive=False),
    )


def _toggle_force_start(acknowledged: bool) -> Any:
    return gr.Button(interactive=acknowledged)


def _close_force_dialog() -> tuple[Any, Any, Any]:
    return gr.Group(visible=False), gr.Checkbox(value=False), gr.Button(interactive=False)


def _invalidate_memory_check() -> tuple[Any, ...]:
    return (
        "",
        gr.Button(visible=False),
        gr.Group(visible=False),
        gr.Checkbox(value=False),
        gr.Button(interactive=False),
    )


def _build_wizard_summary(
    lang: str,
    model_name: str | None,
    model_path: str | None,
    finetuning_type: str,
    quantization_bit: str,
    booster: str,
    training_stage: str,
    dataset: list[str] | None,
    learning_rate: str,
    num_train_epochs: str,
    cutoff_len: int,
    batch_size: int,
    gradient_accumulation_steps: int,
    compute_type: str,
    output_dir: str | None,
) -> str:
    text = WIZARD_SUMMARY_LOCALES.get(lang, WIZARD_SUMMARY_LOCALES["en"])
    dataset_text = escape(", ".join(dataset or []) or text["missing_dataset"])
    training_stage_text = escape(text["stages"].get(training_stage, training_stage))
    effective_batch = batch_size * gradient_accumulation_steps
    model_text = escape(model_name or text["missing_model"])
    path_text = escape(model_path or text["missing_path"])
    output_text = escape(output_dir or text["missing_output"])
    quantization_text = (
        text["no_quantization"]
        if quantization_bit == "none"
        else text["quantization"].format(bit=escape(quantization_bit))
    )
    labels = text["labels"]

    rows = (
        (labels[0], f"{model_text}<small>{path_text}</small>"),
        (labels[1], f"{escape(finetuning_type)} · {quantization_text} · {escape(booster)}"),
        (labels[2], f"{training_stage_text}<small>{dataset_text}</small>"),
        (
            labels[3],
            text["learning"].format(learning_rate=escape(learning_rate), epochs=escape(num_train_epochs)),
        ),
        (
            labels[4],
            text["batch"].format(
                batch_size=batch_size,
                accumulation=gradient_accumulation_steps,
                effective_batch=effective_batch,
            ),
        ),
        (
            labels[5],
            text["sequence"].format(cutoff_len=cutoff_len, compute_type=escape(compute_type)),
        ),
        (labels[6], output_text),
    )
    summary_rows = "".join(
        f'<div class="oobe-summary-row"><span>{escape(label)}</span><strong>{value}</strong></div>'
        for label, value in rows
    )
    return (
        '<section class="oobe-summary">'
        f'<div class="oobe-summary-title"><span>{text["title"]}</span><em>{text["subtitle"]}</em></div>'
        f"{summary_rows}</section>"
    )


def _validate_params_and_build_summary(
    lang: str | None,
    model_name: str | None,
    model_path: str | None,
    finetuning_type: str,
    quantization_bit: str,
    booster: str,
    training_stage: str,
    dataset: list[str] | None,
    learning_rate: str,
    num_train_epochs: str,
    cutoff_len: int,
    batch_size: int,
    gradient_accumulation_steps: int,
    compute_type: str,
    output_dir: str | None,
) -> tuple[Any, ...]:
    text = _guidance_text(lang)
    error = ""
    try:
        if float(learning_rate) <= 0:
            error = text["error_learning_rate"]
    except (TypeError, ValueError):
        error = text["error_learning_rate"]

    if not error:
        try:
            if float(num_train_epochs) <= 0:
                error = text["error_epochs"]
        except (TypeError, ValueError):
            error = text["error_epochs"]

    if not error and (batch_size < 1 or gradient_accumulation_steps < 1):
        error = text["error_batch"]

    if error:
        return (gr.HTML(), _wizard_alert(error), *_show_wizard_step(3))

    summary = _build_wizard_summary(
        lang or "en",
        model_name,
        model_path,
        finetuning_type,
        quantization_bit,
        booster,
        training_stage,
        dataset,
        learning_rate,
        num_train_epochs,
        cutoff_len,
        batch_size,
        gradient_accumulation_steps,
        compute_type,
        output_dir,
    )
    return (summary, "", *_show_wizard_step(4))


def create_train_tab(engine: "Engine") -> dict[str, "Component"]:
    elem_dict: dict[str, Component] = {}

    wizard_hero = gr.HTML(_localized_value("wizard_hero"))

    with gr.Column(visible=True, elem_classes="oobe-page") as model_step:
        wizard_header_1 = gr.HTML(_localized_value("wizard_header_1"))

        with gr.Group(elem_classes="oobe-card"):
            wizard_model_card = gr.Markdown(_localized_value("wizard_model_card"))
            top_elems = create_top()
            engine.manager.add_elems("top", top_elems)

        guidance = WIZARD_GUIDANCE_LOCALES["en"]
        with gr.Group(elem_classes="oobe-card oobe-questionnaire"):
            wizard_questionnaire = gr.Markdown(_localized_value("wizard_questionnaire"))
            with gr.Row():
                wizard_goal = gr.Radio(
                    choices=guidance["goal_choices"],
                    value="instruction",
                    label=guidance["goal_label"],
                    info=guidance["goal_info"],
                )
                wizard_priority = gr.Radio(
                    choices=guidance["priority_choices"],
                    value="balanced",
                    label=guidance["priority_label"],
                    info=guidance["priority_info"],
                )

            wizard_profile_result = gr.HTML()
            wizard_profile_ready = gr.State(False)
            wizard_hardware = gr.State(_detect_hardware_profile())

        with gr.Group(visible=False):
            current_time = gr.Textbox(visible=False, interactive=False)
            device_count = gr.Textbox(value=str(get_device_count() or 1), visible=False, interactive=False)
            ds_stage = gr.Dropdown(choices=["none", "2", "3"], value="none", visible=False)
            ds_offload = gr.Checkbox(visible=False)

        wizard_model_alert = gr.HTML()
        with gr.Row(elem_classes="oobe-nav"):
            wizard_model_next_btn = gr.Button(_localized_value("wizard_model_next_btn"), variant="primary")

    with gr.Column(visible=False, elem_classes="oobe-page") as data_step:
        wizard_header_2 = gr.HTML(_localized_value("wizard_header_2"))

        with gr.Group(elem_classes="oobe-card"):
            wizard_data_guide = gr.Markdown(_localized_value("wizard_data_guide"))
            stages = list(TRAINING_STAGES.keys())
            training_stage = gr.Dropdown(choices=stages, value=stages[0], visible=False)
            dataset_dir = gr.Textbox(value=DEFAULT_DATA_DIR, visible=False)
            with gr.Row():
                dataset = gr.Dropdown(multiselect=True, allow_custom_value=True, scale=5)
                preview_elems = create_preview_box(dataset_dir, dataset)

        wizard_data_alert = gr.HTML()
        with gr.Row(elem_classes="oobe-nav"):
            wizard_data_back_btn = gr.Button(_localized_value("wizard_data_back_btn"))
            wizard_data_next_btn = gr.Button(_localized_value("wizard_data_next_btn"), variant="primary")

    with gr.Column(visible=False, elem_classes="oobe-page") as params_step:
        wizard_header_3 = gr.HTML(_localized_value("wizard_header_3"))
        wizard_params_guide = gr.Markdown(_localized_value("wizard_params_guide"))
        wizard_param_mode = gr.Radio(
            choices=guidance["param_mode_choices"],
            value="recommended",
            label=guidance["param_mode_label"],
            info=guidance["param_mode_info"],
            elem_classes="oobe-branch-selector",
        )

        with gr.Group(visible=False, elem_classes="oobe-card oobe-branch-panel") as wizard_resource_params_group:
            wizard_resource_params_guide = gr.Markdown(_localized_value("wizard_resource_params_guide"))
            with gr.Row():
                compute_type = gr.Dropdown(choices=["bf16", "fp16", "fp32", "pure_bf16"], value="bf16")
                cutoff_len = gr.Slider(minimum=4, maximum=131072, value=2048, step=1)
                batch_size = gr.Slider(minimum=1, maximum=1024, value=2, step=1)
                gradient_accumulation_steps = gr.Slider(minimum=1, maximum=1024, value=8, step=1)

        with gr.Group(visible=False, elem_classes="oobe-card oobe-branch-panel") as wizard_learning_params_group:
            wizard_learning_params_guide = gr.Markdown(_localized_value("wizard_learning_params_guide"))
            with gr.Row():
                learning_rate = gr.Textbox(value="5e-5")
                num_train_epochs = gr.Textbox(value="3.0")

        with gr.Group(elem_classes="oobe-card oobe-live-memory"):
            wizard_live_memory_intro = gr.Markdown(_localized_value("wizard_live_memory_intro"))
            wizard_live_memory_report = gr.HTML()

        max_samples = gr.Textbox(value="100000", visible=False)
        lr_scheduler_type = gr.Dropdown(
            choices=[scheduler.value for scheduler in SchedulerType], value="cosine", visible=False
        )
        max_grad_norm = gr.Textbox(value="1.0", visible=False)
        train_seed = gr.Textbox(value="42", visible=False)

        # Compatibility values remain part of saved configurations, but are intentionally
        # absent from the guided interface. The wizard owns safe defaults for them.
        with gr.Group(visible=False):
            logging_steps = gr.Slider(minimum=1, maximum=1000, value=5, step=5)
            save_steps = gr.Slider(minimum=10, maximum=5000, value=100, step=10)
            warmup_steps = gr.Slider(minimum=0, maximum=5000, value=0, step=1)
            neftune_alpha = gr.Slider(minimum=0, maximum=10, value=0, step=0.1)
            extra_args = gr.Textbox(value='{"optim": "adamw_torch"}')
            packing = gr.Checkbox()
            neat_packing = gr.Checkbox()
            train_on_prompt = gr.Checkbox()
            mask_history = gr.Checkbox()
            resize_vocab = gr.Checkbox()
            use_llama_pro = gr.Checkbox()
            enable_thinking = gr.Checkbox(value=True)
            report_to = gr.Dropdown(value="none", choices=["none"])
            freeze_trainable_layers = gr.Slider(minimum=-128, maximum=128, value=2, step=1)
            freeze_trainable_modules = gr.Textbox(value="all")
            freeze_extra_modules = gr.Textbox()
            lora_rank = gr.Slider(minimum=1, maximum=1024, value=8, step=1)
            lora_alpha = gr.Slider(minimum=1, maximum=2048, value=16, step=1)
            lora_dropout = gr.Slider(minimum=0, maximum=1, value=0, step=0.01)
            loraplus_lr_ratio = gr.Slider(minimum=0, maximum=64, value=0, step=0.01)
            create_new_adapter = gr.Checkbox()
            use_rslora = gr.Checkbox()
            use_dora = gr.Checkbox()
            use_pissa = gr.Checkbox()
            lora_target = gr.Textbox()
            additional_target = gr.Textbox()
            pref_beta = gr.Slider(minimum=0, maximum=1, value=0.1, step=0.01)
            pref_ftx = gr.Slider(minimum=0, maximum=10, value=0, step=0.01)
            pref_loss = gr.Dropdown(value="sigmoid", choices=["sigmoid"])
            reward_model = gr.Dropdown(multiselect=True, allow_custom_value=True)
            ppo_score_norm = gr.Checkbox()
            ppo_whiten_rewards = gr.Checkbox()
            freeze_vision_tower = gr.Checkbox(value=True)
            freeze_multi_modal_projector = gr.Checkbox(value=True)
            freeze_language_model = gr.Checkbox(value=False)
            image_max_pixels = gr.Textbox(value="768*768")
            image_min_pixels = gr.Textbox(value="32*32")
            video_max_pixels = gr.Textbox(value="256*256")
            video_min_pixels = gr.Textbox(value="16*16")
            use_galore = gr.Checkbox()
            galore_rank = gr.Slider(minimum=1, maximum=1024, value=16, step=1)
            galore_update_interval = gr.Slider(minimum=1, maximum=2048, value=200, step=1)
            galore_scale = gr.Slider(minimum=0, maximum=100, value=2.0, step=0.1)
            galore_target = gr.Textbox(value="all")
            use_apollo = gr.Checkbox()
            apollo_rank = gr.Slider(minimum=1, maximum=1024, value=16, step=1)
            apollo_update_interval = gr.Slider(minimum=1, maximum=2048, value=200, step=1)
            apollo_scale = gr.Slider(minimum=0, maximum=100, value=32.0, step=0.1)
            apollo_target = gr.Textbox(value="all")
            use_badam = gr.Checkbox()
            badam_mode = gr.Dropdown(value="layer", choices=["layer"])
            badam_switch_mode = gr.Dropdown(value="ascending", choices=["ascending"])
            badam_switch_interval = gr.Slider(minimum=1, maximum=1024, value=50, step=1)
            badam_update_ratio = gr.Slider(minimum=0, maximum=1, value=0.05, step=0.01)
            use_swanlab = gr.Checkbox()
            swanlab_project = gr.Textbox(value="cyrene-yield")
            swanlab_run_name = gr.Textbox()
            swanlab_workspace = gr.Textbox()
            swanlab_api_key = gr.Textbox()
            swanlab_mode = gr.Dropdown(value="cloud", choices=["cloud"])
            swanlab_link = gr.Markdown(visible=False)

        wizard_params_alert = gr.HTML()
        with gr.Row(elem_classes="oobe-nav"):
            wizard_params_back_btn = gr.Button(_localized_value("wizard_params_back_btn"))
            wizard_params_next_btn = gr.Button(_localized_value("wizard_params_next_btn"), variant="primary")

    with gr.Column(visible=False, elem_classes="oobe-page") as review_step:
        wizard_header_4 = gr.HTML(_localized_value("wizard_header_4"))
        wizard_summary = gr.HTML()

        with gr.Group(elem_classes="oobe-card"):
            wizard_launch_card = gr.Markdown(_localized_value("wizard_launch_card"))
            output_dir = gr.Dropdown(allow_custom_value=True)
            wizard_memory_intro = gr.Markdown(_localized_value("wizard_memory_intro"))
            wizard_memory_report = gr.HTML()
            with gr.Row():
                wizard_preflight_btn = gr.Button(_localized_value("wizard_preflight_btn"), variant="primary")
                start_btn = gr.Button(variant="primary", visible=False)
                stop_btn = gr.Button(variant="stop", visible=False)

        memory_text = WIZARD_MEMORY_LOCALES["en"]
        with gr.Group(visible=False, elem_classes="oobe-risk-modal") as wizard_risk_modal:
            wizard_force_warning = gr.HTML()
            wizard_force_ack = gr.Checkbox(
                label=memory_text["force_ack_label"],
                info=memory_text["force_ack_info"],
            )
            with gr.Row():
                wizard_force_cancel_btn = gr.Button(memory_text["cancel_button"])
                wizard_force_start_btn = gr.Button(memory_text["force_button"], variant="stop", interactive=False)

        with gr.Row():
            with gr.Column(scale=3):
                with gr.Row():
                    resume_btn = gr.Checkbox(visible=False, interactive=False)
                    progress_bar = gr.Slider(visible=False, interactive=False)

                with gr.Row():
                    output_box = gr.Markdown()

            with gr.Column(scale=1):
                loss_viewer = gr.Plot(visible=False)

        with gr.Row(elem_classes="oobe-nav"):
            wizard_review_back_btn = gr.Button(_localized_value("wizard_review_back_btn"))

    input_elems = engine.manager.get_base_elems()
    input_elems.update(
        {
            training_stage,
            dataset_dir,
            dataset,
            learning_rate,
            num_train_epochs,
            max_grad_norm,
            train_seed,
            max_samples,
            compute_type,
            cutoff_len,
            batch_size,
            gradient_accumulation_steps,
            lr_scheduler_type,
            logging_steps,
            save_steps,
            warmup_steps,
            neftune_alpha,
            extra_args,
            packing,
            neat_packing,
            train_on_prompt,
            mask_history,
            resize_vocab,
            use_llama_pro,
            enable_thinking,
            report_to,
            freeze_trainable_layers,
            freeze_trainable_modules,
            freeze_extra_modules,
            lora_rank,
            lora_alpha,
            lora_dropout,
            loraplus_lr_ratio,
            create_new_adapter,
            use_rslora,
            use_dora,
            use_pissa,
            lora_target,
            additional_target,
            pref_beta,
            pref_ftx,
            pref_loss,
            reward_model,
            ppo_score_norm,
            ppo_whiten_rewards,
            freeze_vision_tower,
            freeze_multi_modal_projector,
            freeze_language_model,
            image_max_pixels,
            image_min_pixels,
            video_max_pixels,
            video_min_pixels,
            use_galore,
            galore_rank,
            galore_update_interval,
            galore_scale,
            galore_target,
            use_apollo,
            apollo_rank,
            apollo_update_interval,
            apollo_scale,
            apollo_target,
            use_badam,
            badam_mode,
            badam_switch_mode,
            badam_switch_interval,
            badam_update_ratio,
            use_swanlab,
            swanlab_project,
            swanlab_run_name,
            swanlab_workspace,
            swanlab_api_key,
            swanlab_mode,
            output_dir,
            ds_stage,
            ds_offload,
        }
    )
    memory_input_elems = {
        top_elems["lang"],
        top_elems["model_path"],
        top_elems["finetuning_type"],
        top_elems["quantization_bit"],
        top_elems["booster"],
        device_count,
        training_stage,
        compute_type,
        cutoff_len,
        batch_size,
        lora_rank,
        ds_stage,
        ds_offload,
        extra_args,
    }

    elem_dict.update(
        dict(
            wizard_hero=wizard_hero,
            wizard_header_1=wizard_header_1,
            wizard_questionnaire=wizard_questionnaire,
            wizard_goal=wizard_goal,
            wizard_priority=wizard_priority,
            wizard_model_card=wizard_model_card,
            wizard_model_next_btn=wizard_model_next_btn,
            wizard_header_2=wizard_header_2,
            wizard_data_guide=wizard_data_guide,
            wizard_data_back_btn=wizard_data_back_btn,
            wizard_data_next_btn=wizard_data_next_btn,
            wizard_header_3=wizard_header_3,
            wizard_params_guide=wizard_params_guide,
            wizard_param_mode=wizard_param_mode,
            wizard_resource_params_guide=wizard_resource_params_guide,
            wizard_learning_params_guide=wizard_learning_params_guide,
            wizard_live_memory_intro=wizard_live_memory_intro,
            wizard_live_memory_report=wizard_live_memory_report,
            wizard_params_back_btn=wizard_params_back_btn,
            wizard_params_next_btn=wizard_params_next_btn,
            wizard_header_4=wizard_header_4,
            wizard_launch_card=wizard_launch_card,
            wizard_memory_intro=wizard_memory_intro,
            wizard_preflight_btn=wizard_preflight_btn,
            wizard_force_ack=wizard_force_ack,
            wizard_force_cancel_btn=wizard_force_cancel_btn,
            wizard_force_start_btn=wizard_force_start_btn,
            wizard_review_back_btn=wizard_review_back_btn,
            training_stage=training_stage,
            dataset_dir=dataset_dir,
            dataset=dataset,
            **preview_elems,
            learning_rate=learning_rate,
            num_train_epochs=num_train_epochs,
            max_grad_norm=max_grad_norm,
            train_seed=train_seed,
            max_samples=max_samples,
            compute_type=compute_type,
            cutoff_len=cutoff_len,
            batch_size=batch_size,
            gradient_accumulation_steps=gradient_accumulation_steps,
            lr_scheduler_type=lr_scheduler_type,
            logging_steps=logging_steps,
            save_steps=save_steps,
            warmup_steps=warmup_steps,
            neftune_alpha=neftune_alpha,
            extra_args=extra_args,
            packing=packing,
            neat_packing=neat_packing,
            train_on_prompt=train_on_prompt,
            mask_history=mask_history,
            resize_vocab=resize_vocab,
            use_llama_pro=use_llama_pro,
            enable_thinking=enable_thinking,
            report_to=report_to,
            freeze_trainable_layers=freeze_trainable_layers,
            freeze_trainable_modules=freeze_trainable_modules,
            freeze_extra_modules=freeze_extra_modules,
            lora_rank=lora_rank,
            lora_alpha=lora_alpha,
            lora_dropout=lora_dropout,
            loraplus_lr_ratio=loraplus_lr_ratio,
            create_new_adapter=create_new_adapter,
            use_rslora=use_rslora,
            use_dora=use_dora,
            use_pissa=use_pissa,
            lora_target=lora_target,
            additional_target=additional_target,
            pref_beta=pref_beta,
            pref_ftx=pref_ftx,
            pref_loss=pref_loss,
            reward_model=reward_model,
            ppo_score_norm=ppo_score_norm,
            ppo_whiten_rewards=ppo_whiten_rewards,
            freeze_vision_tower=freeze_vision_tower,
            freeze_multi_modal_projector=freeze_multi_modal_projector,
            freeze_language_model=freeze_language_model,
            image_max_pixels=image_max_pixels,
            image_min_pixels=image_min_pixels,
            video_max_pixels=video_max_pixels,
            video_min_pixels=video_min_pixels,
            use_galore=use_galore,
            galore_rank=galore_rank,
            galore_update_interval=galore_update_interval,
            galore_scale=galore_scale,
            galore_target=galore_target,
            use_apollo=use_apollo,
            apollo_rank=apollo_rank,
            apollo_update_interval=apollo_update_interval,
            apollo_scale=apollo_scale,
            apollo_target=apollo_target,
            use_badam=use_badam,
            badam_mode=badam_mode,
            badam_switch_mode=badam_switch_mode,
            badam_switch_interval=badam_switch_interval,
            badam_update_ratio=badam_update_ratio,
            use_swanlab=use_swanlab,
            swanlab_project=swanlab_project,
            swanlab_run_name=swanlab_run_name,
            swanlab_workspace=swanlab_workspace,
            swanlab_api_key=swanlab_api_key,
            swanlab_mode=swanlab_mode,
            swanlab_link=swanlab_link,
            start_btn=start_btn,
            stop_btn=stop_btn,
            current_time=current_time,
            output_dir=output_dir,
            device_count=device_count,
            ds_stage=ds_stage,
            ds_offload=ds_offload,
            resume_btn=resume_btn,
            progress_bar=progress_bar,
            output_box=output_box,
            loss_viewer=loss_viewer,
        )
    )
    output_elems = [output_box, progress_bar, loss_viewer, swanlab_link, start_btn, stop_btn]

    wizard_steps = [model_step, data_step, params_step, review_step]
    branch_inputs = [wizard_param_mode]
    branch_outputs = [wizard_resource_params_group, wizard_learning_params_group]
    wizard_param_mode.change(
        _show_param_branch,
        inputs=branch_inputs,
        outputs=branch_outputs,
        queue=False,
    )
    recommendation_inputs = [
        top_elems["lang"],
        wizard_goal,
        wizard_hardware,
        top_elems["model_path"],
        wizard_priority,
    ]
    recommendation_outputs = [
        training_stage,
        top_elems["finetuning_type"],
        top_elems["quantization_bit"],
        top_elems["quantization_method"],
        compute_type,
        cutoff_len,
        batch_size,
        gradient_accumulation_steps,
        learning_rate,
        num_train_epochs,
        lr_scheduler_type,
        ds_stage,
        ds_offload,
        top_elems["booster"],
        wizard_profile_result,
        wizard_profile_ready,
        wizard_param_mode,
        *branch_outputs,
    ]
    for profile_control in (wizard_goal, top_elems["model_path"], wizard_priority):
        profile_control.change(
            _recommend_training_setup,
            inputs=recommendation_inputs,
            outputs=recommendation_outputs,
            queue=False,
        ).then(
            lambda data: _run_live_memory_estimate(data, engine.manager),
            inputs=memory_input_elems,
            outputs=[wizard_live_memory_report],
            concurrency_limit=None,
        )
    wizard_model_next_btn.click(
        _validate_model_step,
        inputs=[
            top_elems["lang"],
            wizard_profile_ready,
            top_elems["model_path"],
        ],
        outputs=[wizard_model_alert, *wizard_steps],
        queue=False,
    )
    wizard_data_back_btn.click(lambda: _show_wizard_step(1), outputs=wizard_steps, queue=False)
    wizard_data_next_btn.click(
        _validate_data_step,
        inputs=[top_elems["lang"], dataset],
        outputs=[wizard_data_alert, *wizard_steps],
        queue=False,
    ).then(
        lambda data: _run_live_memory_estimate(data, engine.manager),
        inputs=memory_input_elems,
        outputs=[wizard_live_memory_report],
        concurrency_limit=None,
    )
    wizard_params_back_btn.click(lambda: _show_wizard_step(2), outputs=wizard_steps, queue=False)
    wizard_review_back_btn.click(lambda: _show_wizard_step(3), outputs=wizard_steps, queue=False)
    summary_inputs = [
        top_elems["lang"],
        top_elems["model_name"],
        top_elems["model_path"],
        top_elems["finetuning_type"],
        top_elems["quantization_bit"],
        top_elems["booster"],
        training_stage,
        dataset,
        learning_rate,
        num_train_epochs,
        cutoff_len,
        batch_size,
        gradient_accumulation_steps,
        compute_type,
        output_dir,
    ]
    wizard_params_next_btn.click(
        _validate_params_and_build_summary,
        inputs=summary_inputs,
        outputs=[wizard_summary, wizard_params_alert, *wizard_steps],
        queue=False,
    )

    wizard_preflight_btn.click(
        lambda data: _run_memory_preflight(data, engine.manager),
        inputs=memory_input_elems,
        outputs=[
            wizard_memory_report,
            start_btn,
            wizard_risk_modal,
            wizard_force_warning,
            wizard_force_ack,
            wizard_force_start_btn,
        ],
        concurrency_limit=None,
    )
    wizard_force_ack.change(
        _toggle_force_start,
        inputs=[wizard_force_ack],
        outputs=[wizard_force_start_btn],
        queue=False,
    )
    wizard_force_cancel_btn.click(
        _close_force_dialog,
        outputs=[wizard_risk_modal, wizard_force_ack, wizard_force_start_btn],
        queue=False,
    )

    start_btn.click(engine.runner.run_train, input_elems, output_elems)
    wizard_force_start_btn.click(
        _close_force_dialog,
        outputs=[wizard_risk_modal, wizard_force_ack, wizard_force_start_btn],
        queue=False,
    ).then(engine.runner.run_train, input_elems, output_elems)
    stop_btn.click(engine.runner.set_abort)
    resume_btn.change(engine.runner.monitor, outputs=output_elems, concurrency_limit=None)

    lang = engine.manager.get_elem_by_id("top.lang")
    model_name: gr.Textbox = engine.manager.get_elem_by_id("top.model_name")
    finetuning_type: gr.Dropdown = engine.manager.get_elem_by_id("top.finetuning_type")
    lang.change(_build_wizard_summary, summary_inputs, [wizard_summary], queue=False)
    lang.change(
        _recommend_training_setup,
        inputs=recommendation_inputs,
        outputs=recommendation_outputs,
        queue=False,
    ).then(
        lambda data: _run_live_memory_estimate(data, engine.manager),
        inputs=memory_input_elems,
        outputs=[wizard_live_memory_report],
        concurrency_limit=None,
    )

    memory_sensitive_elems = (
        top_elems["model_path"],
        top_elems["finetuning_type"],
        top_elems["quantization_bit"],
        top_elems["booster"],
        training_stage,
        compute_type,
        cutoff_len,
        batch_size,
        lora_rank,
        ds_stage,
        ds_offload,
        extra_args,
        reward_model,
    )
    for memory_sensitive_elem in memory_sensitive_elems:
        memory_sensitive_elem.change(
            _invalidate_memory_check,
            outputs=[wizard_memory_report, start_btn, wizard_risk_modal, wizard_force_ack, wizard_force_start_btn],
            queue=False,
        )

    for live_memory_dropdown in (
        top_elems["finetuning_type"],
        top_elems["quantization_bit"],
        top_elems["booster"],
        compute_type,
    ):
        live_memory_dropdown.input(
            lambda data: _run_live_memory_estimate(data, engine.manager),
            inputs=memory_input_elems,
            outputs=[wizard_live_memory_report],
            concurrency_limit=None,
        )
    for live_memory_slider in (cutoff_len, batch_size):
        live_memory_slider.release(
            lambda data: _run_live_memory_estimate(data, engine.manager),
            inputs=memory_input_elems,
            outputs=[wizard_live_memory_report],
            concurrency_limit=None,
        )

    dataset.focus(list_datasets, [dataset_dir, training_stage], [dataset], queue=False)
    training_stage.change(change_stage, [training_stage], [dataset, packing], queue=False)
    reward_model.focus(list_checkpoints, [model_name, finetuning_type], [reward_model], queue=False)
    model_name.change(list_output_dirs, [model_name, finetuning_type, current_time], [output_dir], queue=False)
    finetuning_type.change(list_output_dirs, [model_name, finetuning_type, current_time], [output_dir], queue=False)
    output_dir.change(
        list_output_dirs, [model_name, finetuning_type, current_time], [output_dir], concurrency_limit=None
    )
    output_dir.input(
        engine.runner.check_output_dir,
        [lang, model_name, finetuning_type, output_dir],
        list(input_elems) + [output_box],
        concurrency_limit=None,
    )
    return elem_dict
