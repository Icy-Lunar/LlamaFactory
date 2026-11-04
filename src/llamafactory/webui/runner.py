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

"""Convert WebUI forms into jobs and manage subprocesses, logs, progress, and cancellation."""

import json
import os
import socket
import sys
import time
import traceback
import webbrowser
from collections.abc import Generator
from copy import deepcopy
from subprocess import Popen, TimeoutExpired
from typing import TYPE_CHECKING, Any
from urllib.parse import urlsplit

from transformers.utils import is_torch_cuda_available, is_torch_npu_available, is_torch_xpu_available

from ..extras.accelerator import configure_xpu_environment
from ..extras.constants import LLAMABOARD_CONFIG, MULTIMODAL_SUPPORTED_MODELS, PEFT_METHODS, TRAINING_STAGES
from ..extras.liger import get_local_liger_status
from ..extras.misc import is_accelerator_available, torch_gc
from ..extras.packages import is_gradio_available
from .common import (
    DEFAULT_CACHE_DIR,
    DEFAULT_CONFIG_DIR,
    abort_process,
    calculate_pixels,
    gen_cmd,
    get_save_dir,
    load_args,
    load_config,
    save_args,
    save_cmd,
)
from .control import get_trainer_info
from .locales import ALERTS, LIGER_LOCALES, LOCALES
from .stage_locales import STAGE_VALIDATION_ERRORS


if is_gradio_available():
    import gradio as gr


if TYPE_CHECKING:
    from gradio.components import Component

    from .manager import Manager


def _parse_seed(value: Any, default: int = 42) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _get_acceleration_args(model_path: str | None = None, compute_type: str = "fp32") -> dict[str, bool | str]:
    r"""Return hardware-compatible training acceleration settings."""
    return {
        "enable_liger_kernel": get_local_liger_status(model_path, compute_type).enabled,
        "flash_attn": "auto" if is_torch_cuda_available() or is_torch_npu_available() else "disabled",
    }


def _get_train_command(config_path: str) -> list[str]:
    r"""Build a training command that does not depend on the executable search path."""
    return [sys.executable, "-m", "llamafactory.cli", "train", config_path]


def _get_tensorboard_command(log_dir: str, host: str, port: int) -> list[str]:
    r"""Build the TensorBoard command for one training output directory."""
    return [
        sys.executable,
        "-m",
        "tensorboard.main",
        "--logdir",
        log_dir,
        "--host",
        host,
        "--port",
        str(port),
    ]


def _is_port_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.25):
            return True
    except OSError:
        return False


def _find_available_port(host: str, preferred_port: int) -> int:
    for port in range(preferred_port, preferred_port + 20):
        with socket.socket() as listener:
            try:
                listener.bind((host, port))
            except OSError:
                continue
            return port

    raise OSError(f"No available TensorBoard port from {preferred_port} to {preferred_port + 19}.")


def _get_tensorboard_public_url(env: dict[str, str], host: str, port: int, request: Any = None) -> str:
    """Build a browser-reachable URL for direct, proxied, and JupyterHub deployments."""
    configured_url = env.get("TENSORBOARD_PUBLIC_URL", "").strip()
    if configured_url:
        return configured_url.replace("{host}", host).replace("{port}", str(port))

    jupyter_prefix = env.get("JUPYTERHUB_SERVICE_PREFIX", "").strip()
    if jupyter_prefix:
        return f"{jupyter_prefix.rstrip('/')}/proxy/{port}/"

    if host not in {"0.0.0.0", "::"}:
        return f"http://{host}:{port}"

    headers = {}
    if request is not None:
        try:
            headers = {str(name).lower(): str(value) for name, value in dict(request.headers).items()}
        except (AttributeError, TypeError, ValueError):
            headers = {}
    forwarded_host = headers.get("x-forwarded-host", "").split(",", 1)[0].strip()
    request_host = forwarded_host or headers.get("host", "").strip()
    hostname = urlsplit(f"//{request_host}").hostname if request_host else None
    if hostname:
        public_host = f"[{hostname}]" if ":" in hostname else hostname
        scheme = headers.get("x-forwarded-proto", "").split(",", 1)[0].strip() or "http"
        return f"{scheme}://{public_host}:{port}"

    return f"http://127.0.0.1:{port}"


def _configure_accelerator_environment(env: dict[str, str]) -> None:
    r"""Apply backend-specific process settings before the training runtime is imported."""
    if is_torch_xpu_available():
        configure_xpu_environment(env)


class Runner:
    r"""A class to manage the running status of the trainers."""

    def __init__(self, manager: "Manager", demo_mode: bool = False) -> None:
        r"""Init a runner."""
        self.manager = manager
        self.demo_mode = demo_mode
        """ Resume """
        self.trainer: Popen | None = None
        self.tensorboard: Popen | None = None
        self.tensorboard_url: str | None = None
        self.running_data: dict[Component, Any] = None
        """ State """
        self.aborted = False
        self.running = False

    def set_abort(self) -> None:
        self.aborted = True
        if self.trainer is not None:
            abort_process(self.trainer.pid)

    def _stop_tensorboard(self) -> None:
        if self.tensorboard is not None and self.tensorboard.poll() is None:
            abort_process(self.tensorboard.pid)

        self.tensorboard = None
        self.tensorboard_url = None

    def _start_tensorboard(self, output_dir: str, env: dict[str, str], request: Any = None) -> tuple[str, str]:
        r"""Start a TensorBoard server dedicated to the current training directory."""
        self._stop_tensorboard()
        log_dir = os.path.abspath(output_dir)
        host = env.get("TENSORBOARD_HOST", "").strip() or env.get("GRADIO_SERVER_NAME", "").strip() or "127.0.0.1"
        preferred_port = int(env.get("TENSORBOARD_PORT", "6006"))
        port = _find_available_port(host, preferred_port)
        server_log_path = os.path.join(log_dir, "tensorboard_server.log")

        with open(server_log_path, "a", encoding="utf-8") as server_log:
            self.tensorboard = Popen(
                _get_tensorboard_command(log_dir, host, port),
                env=env,
                stdout=server_log,
                stderr=server_log,
                text=True,
            )

        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if self.tensorboard.poll() is not None:
                with open(server_log_path, encoding="utf-8", errors="replace") as server_log:
                    raise RuntimeError(server_log.read()[-20000:])
            probe_host = "127.0.0.1" if host == "0.0.0.0" else "::1" if host == "::" else host
            if _is_port_open(probe_host, port):
                break
            time.sleep(0.1)
        else:
            self._stop_tensorboard()
            raise TimeoutError(f"TensorBoard did not become ready on {host}:{port}.")

        self.tensorboard_url = _get_tensorboard_public_url(env, host, port, request)
        if host not in {"0.0.0.0", "::"} and self.tensorboard_url.startswith(("http://", "https://")):
            try:
                webbrowser.open_new_tab(self.tensorboard_url)
            except webbrowser.Error:
                pass
        return self.tensorboard_url, log_dir

    def _initialize(self, data: dict["Component", Any], from_preview: bool) -> str:
        r"""Validate the configuration."""
        get = lambda elem_id: data[self.manager.get_elem_by_id(elem_id)]
        lang, model_name, model_path = get("top.lang"), get("top.model_name"), get("top.model_path")
        dataset = get("train.dataset")

        if self.running:
            return ALERTS["err_conflict"][lang]

        if not model_path or not os.path.isdir(os.path.abspath(os.path.expanduser(model_path))):
            return ALERTS["err_no_path"][lang]

        if not model_name:
            return ALERTS["err_no_model"][lang]

        if not dataset:
            return ALERTS["err_no_dataset"][lang]

        if not from_preview and self.demo_mode:
            return ALERTS["err_demo"][lang]

        if not get("train.output_dir"):
            return ALERTS["err_no_output_dir"][lang]

        try:
            json.loads(get("train.extra_args"))
        except json.JSONDecodeError:
            return ALERTS["err_json_schema"][lang]

        stage = TRAINING_STAGES[get("train.training_stage")]
        if stage == "ppo" and not get("train.reward_model"):
            return ALERTS["err_no_reward_model"][lang]

        optional = lambda elem_id, default=None: data.get(self.manager.get_elem_by_id(elem_id), default)
        validation_mode = optional("train.validation_mode", "none")
        if stage != "ppo" and validation_mode != "none":
            errors = STAGE_VALIDATION_ERRORS.get(lang, STAGE_VALIDATION_ERRORS["en"])
            if validation_mode == "separate" and not optional("train.eval_dataset"):
                return errors["dataset"]
            if validation_mode == "split" and not 0 < float(optional("train.val_size", 0)) < 100:
                return errors["split"]

        if not from_preview:
            status = get_local_liger_status(get("top.model_path"), optional("train.compute_type", "fp32"))
            if not status.enabled:
                gr.Info(LIGER_LOCALES.get(lang, LIGER_LOCALES["en"])[status.reason])
            if is_torch_xpu_available():
                gr.Info(ALERTS["info_xpu_compat"][lang])
            elif not is_accelerator_available():
                gr.Warning(ALERTS["warn_no_cuda"][lang])

        return ""

    def _finalize(self, lang: str, finish_info: str) -> None:
        r"""Clean the cached memory and resets the runner."""
        finish_info = ALERTS["info_aborted"][lang] if self.aborted else finish_info
        gr.Info(finish_info)
        self.trainer = None
        self.aborted = False
        self.running = False
        self.running_data = None
        torch_gc()

    def _parse_train_args(self, data: dict["Component", Any]) -> dict[str, Any]:
        r"""Build and validate the training arguments."""
        get = lambda elem_id: data[self.manager.get_elem_by_id(elem_id)]
        optional = lambda elem_id, default=None: data.get(self.manager.get_elem_by_id(elem_id), default)
        model_name, finetuning_type = get("top.model_name"), get("top.finetuning_type")
        selected_stage = TRAINING_STAGES[get("train.training_stage")]
        user_config = load_config()

        acceleration_args = _get_acceleration_args(get("top.model_path"), get("train.compute_type"))
        args = dict(
            stage=selected_stage,
            do_train=True,
            model_name_or_path=get("top.model_path"),
            cache_dir=user_config.get("cache_dir", None),
            preprocessing_num_workers=16,
            finetuning_type=finetuning_type,
            template=get("top.template"),
            rope_scaling=get("top.rope_scaling") if get("top.rope_scaling") != "none" else None,
            use_unsloth=False,
            dataset_dir=get("train.dataset_dir"),
            dataset=",".join(get("train.dataset")),
            cutoff_len=get("train.cutoff_len"),
            learning_rate=float(get("train.learning_rate")),
            num_train_epochs=float(get("train.num_train_epochs")),
            max_samples=int(get("train.max_samples")),
            seed=_parse_seed(get("train.train_seed")),
            per_device_train_batch_size=get("train.batch_size"),
            gradient_accumulation_steps=get("train.gradient_accumulation_steps"),
            lr_scheduler_type=get("train.lr_scheduler_type"),
            max_grad_norm=float(get("train.max_grad_norm")),
            logging_steps=get("train.logging_steps"),
            save_steps=get("train.save_steps"),
            warmup_steps=get("train.warmup_steps"),
            neftune_noise_alpha=get("train.neftune_alpha") or None,
            packing=get("train.packing") or get("train.neat_packing"),
            neat_packing=get("train.neat_packing"),
            train_on_prompt=get("train.train_on_prompt"),
            mask_history=get("train.mask_history"),
            resize_vocab=get("train.resize_vocab"),
            use_llama_pro=get("train.use_llama_pro"),
            enable_thinking=get("train.enable_thinking"),
            report_to="tensorboard",
            use_galore=get("train.use_galore"),
            use_apollo=get("train.use_apollo"),
            use_badam=get("train.use_badam"),
            use_swanlab=get("train.use_swanlab"),
            output_dir=get_save_dir(model_name, finetuning_type, get("train.output_dir")),
            fp16=(get("train.compute_type") == "fp16"),
            bf16=(get("train.compute_type") == "bf16"),
            pure_bf16=(get("train.compute_type") == "pure_bf16"),
            plot_loss=True,
            trust_remote_code=True,
            ddp_timeout=180000000,
            include_num_input_tokens_seen=True,
        )
        args.update(acceleration_args)
        args.update(json.loads(get("train.extra_args")))
        # The guided choices are authoritative, including when loading an older saved form.
        args.update(stage=selected_stage, use_unsloth=False, **acceleration_args)
        for key in ("quantization_bit", "quantization_method", "double_quantization"):
            args.pop(key, None)

        # checkpoints
        if get("top.checkpoint_path"):
            if finetuning_type in PEFT_METHODS:  # list
                args["adapter_name_or_path"] = ",".join(
                    [get_save_dir(model_name, finetuning_type, adapter) for adapter in get("top.checkpoint_path")]
                )
            else:  # str
                args["model_name_or_path"] = get_save_dir(model_name, finetuning_type, get("top.checkpoint_path"))

        # quantization
        if get("top.quantization_bit") in {"4", "8"} and finetuning_type in PEFT_METHODS:
            args["quantization_bit"] = int(get("top.quantization_bit"))
            args["quantization_method"] = "bnb"
            args["double_quantization"] = not is_torch_npu_available()

        # freeze config
        if args["finetuning_type"] == "freeze":
            args["freeze_trainable_layers"] = get("train.freeze_trainable_layers")
            args["freeze_trainable_modules"] = get("train.freeze_trainable_modules")
            args["freeze_extra_modules"] = get("train.freeze_extra_modules") or None

        # lora config
        if args["finetuning_type"] == "lora":
            args["lora_rank"] = get("train.lora_rank")
            args["lora_alpha"] = get("train.lora_alpha")
            args["lora_dropout"] = get("train.lora_dropout")
            args["loraplus_lr_ratio"] = get("train.loraplus_lr_ratio") or None
            args["create_new_adapter"] = get("train.create_new_adapter")
            args["use_rslora"] = get("train.use_rslora")
            args["use_dora"] = get("train.use_dora")
            args["pissa_init"] = get("train.use_pissa")
            args["pissa_convert"] = get("train.use_pissa")
            args["lora_target"] = get("train.lora_target") or "all"
            args["additional_target"] = get("train.additional_target") or None

            if args["use_llama_pro"]:
                args["freeze_trainable_layers"] = get("train.freeze_trainable_layers")

        # rlhf config
        if args["stage"] == "ppo":
            rewards = get("train.reward_model")
            rewards = rewards if isinstance(rewards, list) else [rewards]
            if finetuning_type in PEFT_METHODS:
                args["reward_model"] = ",".join(
                    [get_save_dir(model_name, finetuning_type, adapter) for adapter in rewards]
                )
            else:
                args["reward_model"] = get_save_dir(model_name, finetuning_type, rewards[0])

            args["reward_model_type"] = "lora" if finetuning_type == "lora" else "full"
            args["ppo_score_norm"] = get("train.ppo_score_norm")
            args["ppo_whiten_rewards"] = get("train.ppo_whiten_rewards")
            args["ppo_epochs"] = optional("train.ppo_epochs", 4)
            args["ppo_buffer_size"] = optional("train.ppo_buffer_size", 1)
            args["ppo_target"] = optional("train.ppo_target", 6.0)
            args["top_k"] = 0
            args["top_p"] = 0.9
        elif args["stage"] in ["dpo", "kto"]:
            args["pref_beta"] = get("train.pref_beta")
            if args["stage"] == "dpo":
                args["pref_ftx"] = get("train.pref_ftx")
                args["pref_loss"] = get("train.pref_loss")
                if args["pref_loss"] == "sigmoid":
                    args["dpo_label_smoothing"] = optional("train.dpo_label_smoothing", 0)
                if args["pref_loss"] == "simpo":
                    args["simpo_gamma"] = optional("train.simpo_gamma", 0.5)
            else:
                args["kto_chosen_weight"] = optional("train.kto_chosen_weight", 1.0)
                args["kto_rejected_weight"] = optional("train.kto_rejected_weight", 1.0)

        # Never submit hidden settings belonging to a different training stage.
        stage_fields = {
            "sft": {"train_on_prompt", "mask_history", "neat_packing", "neftune_noise_alpha"},
            "dpo": {"pref_ftx", "pref_loss", "dpo_label_smoothing", "simpo_gamma", "pref_bco_weight"},
            "kto": {"kto_chosen_weight", "kto_rejected_weight"},
            "ppo": {
                "reward_model",
                "reward_model_type",
                "ppo_score_norm",
                "ppo_whiten_rewards",
                "ppo_epochs",
                "ppo_buffer_size",
                "ppo_target",
                "top_k",
                "top_p",
            },
        }
        for stage, fields in stage_fields.items():
            if selected_stage != stage:
                for key in fields:
                    args.pop(key, None)
        if selected_stage not in {"dpo", "kto"}:
            args.pop("pref_beta", None)
        if selected_stage not in {"sft", "pt"}:
            args["packing"] = False
            args.pop("resize_vocab", None)
        elif selected_stage == "pt":
            args["packing"] = get("train.packing")
        if selected_stage == "dpo" and args["pref_loss"] != "sigmoid":
            args.pop("dpo_label_smoothing", None)
        if selected_stage == "dpo" and args["pref_loss"] != "simpo":
            args.pop("simpo_gamma", None)

        # Validation is part of training, not a standalone evaluation workflow.
        for key in (
            "val_size",
            "eval_dataset",
            "eval_strategy",
            "evaluation_strategy",
            "eval_steps",
            "per_device_eval_batch_size",
            "do_eval",
            "predict_with_generate",
            "do_predict",
        ):
            args.pop(key, None)
        validation_mode = optional("train.validation_mode", "none")
        if selected_stage != "ppo" and validation_mode in {"split", "separate"}:
            if validation_mode == "split":
                args["val_size"] = float(optional("train.val_size", 10)) / 100
            else:
                args["eval_dataset"] = ",".join(optional("train.eval_dataset", []) or [])
            args.update(
                do_eval=True,
                eval_strategy="steps",
                eval_steps=args["save_steps"],
                save_strategy="steps",
                per_device_eval_batch_size=optional("train.eval_batch_size", 1),
            )

        # multimodal config
        if get("train.model_is_multimodal") or model_name in MULTIMODAL_SUPPORTED_MODELS:
            args["freeze_vision_tower"] = get("train.freeze_vision_tower")
            args["freeze_multi_modal_projector"] = get("train.freeze_multi_modal_projector")
            args["freeze_language_model"] = get("train.freeze_language_model")
            args["image_max_pixels"] = calculate_pixels(get("train.image_max_pixels"))
            args["image_min_pixels"] = calculate_pixels(get("train.image_min_pixels"))
            args["video_max_pixels"] = calculate_pixels(get("train.video_max_pixels"))
            args["video_min_pixels"] = calculate_pixels(get("train.video_min_pixels"))

        # galore config
        if args["use_galore"]:
            args["galore_rank"] = get("train.galore_rank")
            args["galore_update_interval"] = get("train.galore_update_interval")
            args["galore_scale"] = get("train.galore_scale")
            args["galore_target"] = get("train.galore_target")

        # apollo config
        if args["use_apollo"]:
            args["apollo_rank"] = get("train.apollo_rank")
            args["apollo_update_interval"] = get("train.apollo_update_interval")
            args["apollo_scale"] = get("train.apollo_scale")
            args["apollo_target"] = get("train.apollo_target")

        # badam config
        if args["use_badam"]:
            args["badam_mode"] = get("train.badam_mode")
            args["badam_switch_mode"] = get("train.badam_switch_mode")
            args["badam_switch_interval"] = get("train.badam_switch_interval")
            args["badam_update_ratio"] = get("train.badam_update_ratio")

        # swanlab config
        if get("train.use_swanlab"):
            args["swanlab_project"] = get("train.swanlab_project")
            args["swanlab_run_name"] = get("train.swanlab_run_name")
            args["swanlab_workspace"] = get("train.swanlab_workspace")
            args["swanlab_api_key"] = get("train.swanlab_api_key")
            args["swanlab_mode"] = get("train.swanlab_mode")

        # ds config
        if get("train.ds_stage") != "none":
            ds_stage = get("train.ds_stage")
            ds_offload = "offload_" if get("train.ds_offload") else ""
            args["deepspeed"] = os.path.join(DEFAULT_CACHE_DIR, f"ds_z{ds_stage}_{ds_offload}config.json")

        if args["report_to"] == "tensorboard":
            args["logging_dir"] = args["output_dir"]

        return args

    def _preview(self, data: dict["Component", Any]) -> Generator[dict["Component", str], None, None]:
        r"""Preview the training commands."""
        output_box = self.manager.get_elem_by_id("train.output_box")
        error = self._initialize(data, from_preview=True)
        if error:
            gr.Warning(error)
            yield {output_box: error}
        else:
            yield {output_box: gen_cmd(self._parse_train_args(data))}

    def _launch(
        self, data: dict["Component", Any], request: Any = None
    ) -> Generator[dict["Component", Any], None, None]:
        r"""Start the training process."""
        output_box = self.manager.get_elem_by_id("train.output_box")
        error = self._initialize(data, from_preview=False)
        if error:
            gr.Warning(error)
            yield {output_box: error}
        else:
            self.running_data = data
            args = self._parse_train_args(data)
            lang = data[self.manager.get_elem_by_id("top.lang")]

            os.makedirs(args["output_dir"], exist_ok=True)
            save_args(os.path.join(args["output_dir"], LLAMABOARD_CONFIG), self._build_config_dict(data))

            env = deepcopy(os.environ)
            env["LLAMABOARD_ENABLED"] = "1"
            env["LLAMABOARD_WORKDIR"] = args["output_dir"]
            _configure_accelerator_environment(env)
            if args.get("deepspeed", None) is not None:
                env["FORCE_TORCHRUN"] = "1"

            # NOTE: DO NOT USE shell=True to avoid security risk
            webui_log_path = os.path.join(args["output_dir"], "webui_subprocess.log")
            config_path = save_cmd(args)
            tensorboard_url = None
            tensorboard_log_dir = None
            try:
                if args.get("report_to") == "tensorboard":
                    tensorboard_url, tensorboard_log_dir = self._start_tensorboard(args["output_dir"], env, request)

                with open(webui_log_path, "a", encoding="utf-8") as webui_log:
                    self.trainer = Popen(
                        _get_train_command(config_path),
                        env=env,
                        stdout=webui_log,
                        stderr=webui_log,
                        text=True,
                    )
            except (OSError, RuntimeError, TimeoutError):
                error_stack = traceback.format_exc()
                self._stop_tensorboard()
                with open(webui_log_path, "a", encoding="utf-8") as webui_log:
                    webui_log.write(error_stack)

                failure_message = ALERTS["err_launch"][lang].format(log_path=webui_log_path)
                failure_details = f"{failure_message}\n\n```text\n{error_stack}\n```"
                self._finalize(lang, failure_message)
                gr.Warning(failure_message)
                yield {output_box: failure_details}
                return

            if tensorboard_url is not None and tensorboard_log_dir is not None:
                tensorboard_link = self.manager.get_elem_by_id("train.tensorboard_link")
                tensorboard_message = ALERTS["info_tensorboard_started"][lang].format(url=tensorboard_url)
                gr.Info(tensorboard_message)
                yield {
                    tensorboard_link: gr.Markdown(
                        value=ALERTS["info_tensorboard_link"][lang].format(
                            url=tensorboard_url, log_dir=tensorboard_log_dir
                        ),
                        visible=True,
                    )
                }

            yield from self.monitor()

    def _build_config_dict(self, data: dict["Component", Any]) -> dict[str, Any]:
        r"""Build a dictionary containing the current training configuration."""
        config_dict = {}
        skip_ids = ["top.lang", "top.model_path", "train.output_dir", "train.model_is_multimodal"]
        for elem, value in data.items():
            elem_id = self.manager.get_id_by_elem(elem)
            if elem_id not in skip_ids:
                config_dict[elem_id] = value

        return config_dict

    def preview_train(self, data):
        yield from self._preview(data)

    def run_train(self, data, request: gr.Request):
        yield from self._launch(data, request)

    def monitor(self):
        r"""Monitorgit the training progress and logs."""
        self.aborted = False
        self.running = True

        get = lambda elem_id: self.running_data[self.manager.get_elem_by_id(elem_id)]
        lang, model_name, finetuning_type = get("top.lang"), get("top.model_name"), get("top.finetuning_type")
        output_dir = get("train.output_dir")
        output_path = get_save_dir(model_name, finetuning_type, output_dir)

        output_box = self.manager.get_elem_by_id("train.output_box")
        progress_bar = self.manager.get_elem_by_id("train.progress_bar")
        loss_viewer = self.manager.get_elem_by_id("train.loss_viewer")
        swanlab_link = self.manager.get_elem_by_id("train.swanlab_link")
        start_btn = self.manager.get_elem_by_id("train.start_btn")
        stop_btn = self.manager.get_elem_by_id("train.stop_btn")

        running_log = ""
        return_code = -1
        while return_code == -1:
            if self.aborted:
                yield {
                    output_box: ALERTS["info_aborting"][lang],
                    progress_bar: gr.Slider(visible=False),
                }
            else:
                running_log, running_progress, running_info = get_trainer_info(lang, output_path)
                return_dict = {
                    output_box: running_log,
                    progress_bar: running_progress,
                    start_btn: gr.Button(visible=False),
                    stop_btn: gr.Button(visible=True),
                }
                if "loss_viewer" in running_info:
                    return_dict[loss_viewer] = running_info["loss_viewer"]

                if "swanlab_link" in running_info:
                    return_dict[swanlab_link] = running_info["swanlab_link"]

                yield return_dict

            try:
                stderr = self.trainer.communicate(timeout=2)[1]
                return_code = self.trainer.returncode
            except TimeoutExpired:
                continue

        if return_code == 0 or self.aborted:
            finish_info = ALERTS["info_finished"][lang]
            finish_log = ALERTS["info_finished"][lang] + "\n\n" + running_log
        else:
            if stderr is None:
                webui_log_path = os.path.join(output_path, "webui_subprocess.log")
                if os.path.exists(webui_log_path):
                    with open(webui_log_path, "rb") as f:
                        f.seek(0, os.SEEK_END)
                        f.seek(max(f.tell() - 20000, 0))
                        stderr = f.read().decode("utf-8", errors="replace")
                else:
                    stderr = "No subprocess log file found."

            print(stderr)
            finish_info = ALERTS["err_failed"][lang]
            finish_log = ALERTS["err_failed"][lang] + f" Exit code: {return_code}\n\n```\n{stderr}\n```\n"

        self._finalize(lang, finish_info)
        return_dict = {
            output_box: finish_log,
            progress_bar: gr.Slider(visible=False),
            start_btn: gr.Button(visible=True),
            stop_btn: gr.Button(visible=False),
        }
        yield return_dict

    def save_args(self, data):
        r"""Save the training configuration to config path."""
        output_box = self.manager.get_elem_by_id("train.output_box")
        error = self._initialize(data, from_preview=True)
        if error:
            gr.Warning(error)
            return {output_box: error}

        lang = data[self.manager.get_elem_by_id("top.lang")]
        config_path = data[self.manager.get_elem_by_id("train.config_path")]
        os.makedirs(DEFAULT_CONFIG_DIR, exist_ok=True)
        save_path = os.path.join(DEFAULT_CONFIG_DIR, config_path)

        save_args(save_path, self._build_config_dict(data))
        return {output_box: ALERTS["info_config_saved"][lang] + save_path}

    def load_args(self, lang: str, config_path: str):
        r"""Load the training configuration from config path."""
        output_box = self.manager.get_elem_by_id("train.output_box")
        config_dict = load_args(os.path.join(DEFAULT_CONFIG_DIR, config_path))
        if config_dict is None:
            gr.Warning(ALERTS["err_config_not_found"][lang])
            return {output_box: ALERTS["err_config_not_found"][lang]}

        output_dict: dict[Component, Any] = {output_box: ALERTS["info_config_loaded"][lang]}
        for elem_id, value in config_dict.items():
            if self.manager.has_elem(elem_id):
                output_dict[self.manager.get_elem_by_id(elem_id)] = value

        return output_dict

    def check_output_dir(self, lang: str, model_name: str, finetuning_type: str, output_dir: str):
        r"""Restore the training status if output_dir exists."""
        output_box = self.manager.get_elem_by_id("train.output_box")
        output_dict: dict[Component, Any] = {output_box: LOCALES["output_box"][lang]["value"]}
        if model_name and output_dir and os.path.isdir(get_save_dir(model_name, finetuning_type, output_dir)):
            gr.Warning(ALERTS["warn_output_dir_exists"][lang])
            output_dict[output_box] = ALERTS["warn_output_dir_exists"][lang]

            output_dir = get_save_dir(model_name, finetuning_type, output_dir)
            config_dict = load_args(os.path.join(output_dir, LLAMABOARD_CONFIG))  # load llamaboard config
            for elem_id, value in config_dict.items():
                if self.manager.has_elem(elem_id):
                    output_dict[self.manager.get_elem_by_id(elem_id)] = value

        return output_dict
