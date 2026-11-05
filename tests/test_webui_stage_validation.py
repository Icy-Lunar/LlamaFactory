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

import json

import pytest

from llamafactory.extras.constants import TRAINING_STAGES
from llamafactory.webui.components import train as train_components
from llamafactory.webui.engine import Engine
from llamafactory.webui.interface import create_ui
from llamafactory.webui.locales import LOCALES
from llamafactory.webui.memory import DeviceMemory
from llamafactory.webui.runner import _get_acceleration_args
from llamafactory.webui.stage_locales import GOAL_STAGES, STAGE_GOAL_CHOICES, STAGE_GUIDES, STAGE_LOCALES


@pytest.fixture(scope="module")
def form():
    engine = Engine(demo_mode=True)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr("llamafactory.webui.interface.Engine", lambda **kwargs: engine)
        demo = create_ui(demo_mode=True)
    data = {component: getattr(component, "value", None) for component in engine.manager.get_elem_list()}
    data[engine.manager.get_elem_by_id("top.model_name")] = "Custom"
    data[engine.manager.get_elem_by_id("train.dataset")] = ["train-data"]
    data[engine.manager.get_elem_by_id("train.output_dir")] = "test-output"
    return engine, demo, data


def _with(form, **values):
    engine, _, default_data = form
    data = default_data.copy()
    for name, value in values.items():
        data[engine.manager.get_elem_by_id(name.replace("__", "."))] = value
    return data


def test_all_supported_stages_are_reachable_and_localized():
    assert set(GOAL_STAGES.values()) == set(TRAINING_STAGES)
    for lang in ("en", "zh", "ru", "ko", "ja"):
        assert {goal for _, goal in STAGE_GOAL_CHOICES[lang]} == set(GOAL_STAGES)
        assert set(STAGE_GUIDES[lang]) == set(TRAINING_STAGES.values())
        for component, translations in STAGE_LOCALES.items():
            assert LOCALES[component][lang]
            assert translations[lang]


@pytest.mark.parametrize("stage", TRAINING_STAGES)
def test_stage_panel_visibility_is_relevant(stage):
    guide, text, sft, preference, dpo, kto, ppo, validation = train_components._show_stage_parameters(stage, "zh")
    key = TRAINING_STAGES[stage]
    assert guide == STAGE_GUIDES["zh"][key]
    assert text.visible is (key in {"sft", "pt"})
    assert sft.visible is (key == "sft")
    assert preference.visible is (key in {"dpo", "kto"})
    assert dpo.visible is (key == "dpo")
    assert kto.visible is (key == "kto")
    assert ppo.visible is (key == "ppo")
    assert validation.visible is (key != "ppo")


def test_stage_event_and_recommendation_outputs_are_wired(form):
    engine, demo, _ = form
    stage = engine.manager.get_elem_by_id("train.training_stage")
    stage_event = next(event for event in demo.fns.values() if event.fn is train_components._show_stage_parameters)
    assert (stage._id, "change") in stage_event.targets
    assert len(stage_event.outputs) == 8
    recommendation = next(
        event for event in demo.fns.values() if event.fn is train_components._recommend_training_setup
    )
    values = recommendation.fn("en", "instruction", "mid", "", "balanced", "lora", "none")
    assert len(values) == len(recommendation.outputs)
    for goal, stage_name in GOAL_STAGES.items():
        assert recommendation.fn("en", goal, "mid", "", "balanced", "lora", "none")[0] == stage_name


def test_new_controls_are_in_launch_inputs_and_saved_config(form):
    engine, demo, data = form
    launch = next(event for event in demo.fns.values() if event.fn == engine.runner.run_train)
    names = {
        "validation_mode",
        "val_size",
        "eval_dataset",
        "eval_batch_size",
        "dpo_label_smoothing",
        "simpo_gamma",
        "kto_chosen_weight",
        "kto_rejected_weight",
        "ppo_epochs",
        "ppo_buffer_size",
        "ppo_target",
    }
    saved = engine.runner._build_config_dict(data)
    for name in names:
        control = engine.manager.get_elem_by_id(f"train.{name}")
        assert control in launch.inputs
        assert f"train.{name}" in saved


def test_tensorboard_is_the_default_training_logger(form):
    engine, demo, data = form
    args = engine.runner._parse_train_args(data)
    launch = next(event for event in demo.fns.values() if event.fn == engine.runner.run_train)

    assert data[engine.manager.get_elem_by_id("train.report_to")] == "tensorboard"
    assert args["report_to"] == "tensorboard"
    assert args["logging_dir"] == args["output_dir"]
    assert engine.manager.get_elem_by_id("train.tensorboard_link") in launch.outputs


@pytest.mark.parametrize("rocm_wsl", [True, False])
def test_wsl_worker_safety_does_not_change_other_backends(form, monkeypatch, rocm_wsl):
    monkeypatch.setattr("llamafactory.webui.runner.is_rocm_wsl", lambda: rocm_wsl)
    engine, _, _ = form
    data = _with(
        form,
        train__extra_args=json.dumps(
            {"preprocessing_num_workers": 8, "dataloader_num_workers": 4, "dataloader_pin_memory": True}
        ),
    )
    args = engine.runner._parse_train_args(data)
    assert args["preprocessing_num_workers"] == (1 if rocm_wsl else 8)
    assert args["dataloader_num_workers"] == (0 if rocm_wsl else 4)
    assert args["dataloader_pin_memory"] is (not rocm_wsl)


@pytest.mark.parametrize("mode", ["none", "split", "separate"])
def test_validation_branch_and_generated_args(form, mode):
    engine, _, _ = form
    split, datasets, schedule = train_components._show_validation_parameters(mode)
    assert split.visible is (mode == "split")
    assert datasets.visible is (mode == "separate")
    assert schedule.visible is (mode != "none")
    data = _with(
        form,
        train__validation_mode=mode,
        train__val_size=15,
        train__eval_dataset=["held-out"],
        train__eval_batch_size=3,
        train__save_steps=40,
        train__extra_args=json.dumps(
            {"val_size": 0.5, "eval_dataset": "stale", "eval_strategy": "steps", "eval_steps": 25}
        ),
    )
    args = engine.runner._parse_train_args(data)
    if mode == "none":
        assert "eval_dataset" not in args and "val_size" not in args and "do_eval" not in args
    else:
        assert args["do_eval"] is True
        assert args["eval_strategy"] == "steps"
        assert args["save_strategy"] == "steps"
        assert args["eval_steps"] == args["save_steps"] == 40
        assert args["per_device_eval_batch_size"] == 3
        if mode == "split":
            assert args["val_size"] == 0.15 and "eval_dataset" not in args
        else:
            assert args["eval_dataset"] == "held-out" and "val_size" not in args


@pytest.mark.parametrize("stage", TRAINING_STAGES)
def test_hidden_stage_values_cannot_leak_into_training_args(form, stage):
    engine, _, _ = form
    data = _with(
        form,
        train__training_stage=stage,
        train__train_on_prompt=True,
        train__mask_history=True,
        train__neat_packing=True,
        train__packing=True,
        train__pref_loss="simpo",
        train__simpo_gamma=2.0,
        train__pref_beta=0.2,
        train__pref_ftx=0.3,
        train__kto_chosen_weight=1.7,
        train__kto_rejected_weight=0.7,
        train__reward_model=["local-reward"],
        train__ppo_epochs=7,
        train__validation_mode="split",
        train__val_size=10,
        train__extra_args=json.dumps({"stage": "ppo", "dpo_label_smoothing": 0.3}),
    )
    args = engine.runner._parse_train_args(data)
    key = TRAINING_STAGES[stage]
    assert args["stage"] == key
    if key != "sft":
        assert not {"train_on_prompt", "mask_history", "neat_packing", "neftune_noise_alpha"}.intersection(args)
    if key not in {"sft", "pt"}:
        assert args["packing"] is False
    if key not in {"dpo", "kto"}:
        assert "pref_beta" not in args
    if key == "dpo":
        assert args["pref_loss"] == "simpo" and args["simpo_gamma"] == 2.0
        assert "dpo_label_smoothing" not in args
        assert args["pref_ftx"] == 0.3
    else:
        assert not {"pref_loss", "pref_ftx", "simpo_gamma", "dpo_label_smoothing"}.intersection(args)
    if key == "kto":
        assert args["kto_chosen_weight"] == 1.7 and args["kto_rejected_weight"] == 0.7
    else:
        assert not {"kto_chosen_weight", "kto_rejected_weight"}.intersection(args)
    if key == "ppo":
        assert args["ppo_epochs"] == 7 and args["reward_model"]
        assert not {"val_size", "eval_dataset", "do_eval", "eval_steps", "eval_strategy"}.intersection(args)
    else:
        assert "ppo_epochs" not in args and "reward_model" not in args


def test_dpo_loss_specific_fields(form):
    engine, _, _ = form
    for loss in ("sigmoid", "hinge", "ipo", "kto_pair", "orpo", "simpo"):
        smoothing, margin = train_components._show_dpo_loss_parameters(loss)
        assert smoothing.visible is (loss == "sigmoid")
        assert margin.visible is (loss == "simpo")
        args = engine.runner._parse_train_args(_with(form, train__training_stage="DPO", train__pref_loss=loss))
        assert args["pref_loss"] == loss


def test_restored_legacy_backend_values_cannot_override_fixed_choices(form):
    engine, _, _ = form
    args = engine.runner._parse_train_args(
        _with(
            form,
            top__quantization_bit="4",
            top__quantization_method="hqq",
            top__booster="unsloth",
            train__report_to="none",
            train__extra_args=json.dumps(
                {"enable_liger_kernel": False, "use_unsloth": True, "quantization_method": "eetq"}
            ),
        )
    )
    assert args["enable_liger_kernel"] is _get_acceleration_args()["enable_liger_kernel"]
    assert args["use_unsloth"] is False
    assert args["quantization_method"] == "bnb"
    assert args["quantization_bit"] == 4
    assert args["report_to"] == "tensorboard"


def test_reward_selector_focus_preserves_selection_and_method_change_resets_it(form):
    engine, demo, _ = form
    reward = engine.manager.get_elem_by_id("train.reward_model")
    method = engine.manager.get_elem_by_id("top.finetuning_type")
    focus_event = next(event for event in demo.fns.values() if (reward._id, "focus") in event.targets)
    assert "value" not in focus_event.fn("Custom", "lora").constructor_args
    reset_event = next(
        event for event in demo.fns.values() if (method._id, "change") in event.targets and reward in event.outputs
    )
    reset = reset_event.fn("Custom", "full")
    assert reset.multiselect is False and reset.value is None
    args = engine.runner._parse_train_args(
        _with(form, train__training_stage="PPO", top__finetuning_type="full", train__reward_model="local-reward")
    )
    assert args["reward_model_type"] == "full" and args["reward_model"].endswith("local-reward")


def test_validation_missing_data_is_actionable_and_ppo_ignores_it(form, tmp_path):
    engine, _, _ = form
    data = _with(
        form,
        top__lang="zh",
        top__model_path=str(tmp_path),
        top__model_name="Custom",
        train__validation_mode="separate",
        train__eval_dataset=[],
    )
    assert engine.runner._initialize(data, from_preview=True) == train_components._validation_error(
        "zh", "Supervised Fine-Tuning", "separate", 10, []
    )
    assert train_components._validation_error("zh", "PPO", "separate", 10, []) == ""


def test_validation_batch_updates_live_memory_and_invalidates_preflight(form, tmp_path, monkeypatch):
    engine, demo, _ = form
    (tmp_path / "config.json").write_text(
        json.dumps(
            {
                "hidden_size": 4096,
                "intermediate_size": 14336,
                "num_attention_heads": 32,
                "num_hidden_layers": 32,
                "num_key_value_heads": 8,
                "vocab_size": 128000,
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "model.safetensors").write_bytes(b"weights")
    monkeypatch.setattr(train_components, "get_device_memory_snapshot", lambda: DeviceMemory(80.0, 80.0, 1))
    data = _with(form, top__model_path=str(tmp_path), train__validation_mode="split", train__eval_batch_size=1)
    first = train_components._assess_training_memory(data, engine.manager)
    data[engine.manager.get_elem_by_id("train.eval_batch_size")] = 16
    larger = train_components._assess_training_memory(data, engine.manager)
    assert larger[2] > first[2]
    eval_batch = engine.manager.get_elem_by_id("train.eval_batch_size")
    assert any((eval_batch._id, "release") in event.targets for event in demo.fns.values())
    assert any(
        (eval_batch._id, "change") in event.targets and event.fn is train_components._invalidate_memory_check
        for event in demo.fns.values()
    )
