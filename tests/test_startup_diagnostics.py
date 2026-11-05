# Copyright 2026 the LlamaFactory team.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy at http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import json
import os
import subprocess
import sys
from types import SimpleNamespace

import pytest

from llamafactory.extras import diagnostics, liger
from llamafactory.webui import control, runner
from llamafactory.webui.common import load_args
from llamafactory.webui.runtime_locales import RUNTIME_LOCALES
from scripts.session_logging import live_output


def manager():
    return SimpleNamespace(get_elem_by_id=lambda key: key, has_elem=lambda key: True)


@pytest.mark.parametrize("content", [None, "", "null", "[]", "invalid: ["])
def test_existing_output_without_valid_webui_config_is_safe(tmp_path, content):
    if content is not None:
        (tmp_path / runner.LLAMABOARD_CONFIG).write_text(content, encoding="utf-8")
    result = runner.Runner(manager()).check_output_dir("en", "Custom", "lora", str(tmp_path))
    assert "train.output_box" in result
    assert load_args(str(tmp_path / runner.LLAMABOARD_CONFIG)) is None


def test_preview_never_runs_liger_subprocess(monkeypatch, tmp_path):
    monkeypatch.delenv("LLAMAFACTORY_LIGER", raising=False)
    monkeypatch.setattr(liger.metadata, "version", lambda _: "0.8.5")
    monkeypatch.setattr(liger, "get_liger_status", lambda *a: pytest.fail("GPU probe in UI"))
    (tmp_path / "config.json").write_text('{"model_type":"llama"}', encoding="utf-8")
    status = liger.get_local_liger_status(str(tmp_path), probe=False)
    assert status.enabled and status.reason == "pending"
    assert runner._get_acceleration_args(str(tmp_path))["enable_liger_kernel"]


def test_rocm_wsl_detection_does_not_query_gpu(monkeypatch):
    import torch

    monkeypatch.setattr(torch.version, "hip", "7.2")
    monkeypatch.setattr(diagnostics.platform, "release", lambda: "6.6-microsoft-standard-WSL2")
    assert diagnostics.is_rocm_wsl()
    monkeypatch.setattr(torch.version, "hip", None)
    assert not diagnostics.is_rocm_wsl()  # CUDA on WSL is unchanged.


def test_stage_is_flushed_and_persisted(monkeypatch, tmp_path):
    monkeypatch.setenv("LLAMABOARD_WORKDIR", str(tmp_path))
    monkeypatch.setenv("LOCAL_RANK", "0")
    diagnostics.stage("weights")
    assert json.loads((tmp_path / "runtime_state.json").read_text())["stage"] == "weights"
    assert json.loads((tmp_path / "lifecycle.jsonl").read_text())["pid"] > 0


def test_log_tail_is_bounded_and_escaped(tmp_path, monkeypatch):
    (tmp_path / "webui_subprocess.log").write_text(
        "x" * 50000 + "\n<script>alert(1)</script>\ntoken=private", encoding="utf-8"
    )
    (tmp_path / control.TRAINER_LOG).write_text('{"unfinished":', encoding="utf-8")
    text, _, _ = control.get_trainer_info("en", str(tmp_path))
    assert len(text) < 25000 and "<script>" not in text and "&lt;script&gt;" in text
    assert "private" not in text and "[REDACTED]" in text


def test_terminal_heartbeat_when_child_is_silent():
    with subprocess.Popen(
        [sys.executable, "-u", "-c", "import time; time.sleep(.15); print('ready')"], stdout=subprocess.PIPE, text=True
    ) as child:
        output = list(live_output(child, interval=0.02))
    assert "" in output and "ready\n" in output


def test_runtime_localizations_are_complete():
    assert all(set(value) == set(RUNTIME_LOCALES["en"]) for value in RUNTIME_LOCALES.values())


def prepared_runner(monkeypatch, tmp_path, code=0):
    job = runner.Runner(manager())
    monkeypatch.setattr(job, "_initialize", lambda *a, **kw: "")
    monkeypatch.setattr(
        job, "_parse_train_args", lambda data: {"output_dir": str(tmp_path), "report_to": "tensorboard"}
    )
    monkeypatch.setattr(job, "_build_config_dict", lambda data: {})
    monkeypatch.setattr(runner, "save_cmd", lambda args: str(tmp_path / "train.yaml"))
    monkeypatch.setattr(runner, "_configure_accelerator_environment", lambda env: None)
    monkeypatch.setattr(runner.gr, "Info", lambda *a: None)
    monkeypatch.setattr(runner.gr, "Warning", lambda *a: None)

    class Child:
        pid = 123456
        returncode = None

        def __init__(self, command, **kwargs):
            assert kwargs["env"]["PYTHONUNBUFFERED"] == "1"
            kwargs["stdout"].write("early import output\n")

        def poll(self):
            return self.returncode

        def communicate(self, timeout):
            self.returncode = code
            return None, None

    monkeypatch.setattr(runner, "Popen", Child)

    def failed_dashboard(*a):
        assert job.trainer is not None  # Start training before optional dashboard.
        raise TimeoutError("dashboard unavailable")

    monkeypatch.setattr(job, "_start_tensorboard", failed_dashboard)
    data = {
        "top.lang": "en",
        "top.model_name": "Custom",
        "top.finetuning_type": "lora",
        "train.output_dir": str(tmp_path),
    }
    return job, data


@pytest.mark.parametrize("exit_code", [0, 1, -1, -15])
def test_child_exit_and_dashboard_failure_restore_controls(monkeypatch, tmp_path, exit_code):
    job, data = prepared_runner(monkeypatch, tmp_path, exit_code)
    updates = list(job._launch(data))
    assert not job.running and job.trainer is None
    assert updates[-1]["train.start_btn"].visible
    assert not updates[-1]["train.stop_btn"].visible
    assert "dashboard unavailable" in (tmp_path / "webui_subprocess.log").read_text()
    assert json.loads((tmp_path / "lifecycle.jsonl").read_text().splitlines()[-1])["return_code"] == exit_code


def test_cancel_before_child_start_and_duplicate_click(monkeypatch, tmp_path):
    job, data = prepared_runner(monkeypatch, tmp_path)
    first = job._launch(data)
    next(first)
    assert job.running
    assert "train.output_box" in next(job._launch(data))
    job.set_abort()
    list(first)
    assert not job.running and job.trainer is None


def test_configuration_exception_releases_launch_lock(monkeypatch, tmp_path):
    job, data = prepared_runner(monkeypatch, tmp_path)

    def fail(data):
        raise ValueError("invalid configuration")

    monkeypatch.setattr(job, "_parse_train_args", fail)
    updates = list(job._launch(data))
    assert any("invalid configuration" in str(update.get("train.output_box", "")) for update in updates)
    assert not job.running and not job._launch_lock.locked()


def test_required_liger_never_silently_falls_back(monkeypatch):
    import torch

    from llamafactory.model.model_utils import liger_kernel

    monkeypatch.setenv("LLAMAFACTORY_LIGER", "required")
    monkeypatch.setattr(
        liger_kernel, "get_model_liger_status", lambda *a: liger.LigerStatus(False, "runtime", "timeout")
    )
    args = SimpleNamespace(enable_liger_kernel=True, compute_dtype=torch.bfloat16)
    with pytest.raises(RuntimeError, match="Required Liger"):
        liger_kernel.apply_liger_kernel(SimpleNamespace(model_type="llama"), args, True, False)


def test_startup_watchdog_stops_import_stall(monkeypatch, tmp_path):
    job, data = prepared_runner(monkeypatch, tmp_path, -15)
    job.running_data = data
    job.started_at = runner.time.time() - 700
    job.trainer = SimpleNamespace(pid=123456, returncode=-15, communicate=lambda **kw: (None, None))
    killed = []
    monkeypatch.setattr(runner, "abort_process", killed.append)
    list(job.monitor())
    assert killed == [123456]
    assert "600" in job.launch_failure


def test_long_preprocessing_is_not_killed_as_import_stall(monkeypatch, tmp_path):
    job, data = prepared_runner(monkeypatch, tmp_path, 0)
    job.running_data = data
    job.started_at = runner.time.time() - 700
    job.trainer = SimpleNamespace(pid=123456, returncode=0, communicate=lambda **kw: (None, None))
    (tmp_path / "runtime_state.json").write_text(json.dumps({"stage": "preprocessing", "time": job.started_at}))
    monkeypatch.setattr(runner, "abort_process", lambda *a: pytest.fail("Long data processing must not be killed"))
    list(job.monitor())
    assert not job.launch_failure


def test_launch_real_child_writes_before_tensorboard(monkeypatch, tmp_path):
    """Exercise Popen/logging end to end, without requiring an accelerator or model."""
    real_popen = subprocess.Popen
    job, data = prepared_runner(monkeypatch, tmp_path)
    monkeypatch.setattr(runner, "Popen", real_popen)
    monkeypatch.setattr(
        runner, "_get_train_command", lambda path: [sys.executable, "-c", "print('model process reached', flush=True)"]
    )

    def dashboard(*args):
        assert job.trainer is not None
        job.trainer.wait(timeout=15)
        assert "model process reached" in (tmp_path / "webui_subprocess.log").read_text()
        raise TimeoutError("dashboard intentionally unavailable")

    monkeypatch.setattr(job, "_start_tensorboard", dashboard)
    updates = list(job._launch(data))
    assert updates[-1]["train.start_btn"].visible
    assert json.loads((tmp_path / "lifecycle.jsonl").read_text().splitlines()[-1])["return_code"] == 0


def test_rejected_launch_does_not_stop_existing_job(monkeypatch, tmp_path):
    job, data = prepared_runner(monkeypatch, tmp_path)
    existing = SimpleNamespace(pid=123456, poll=lambda: None)
    job.trainer = existing
    job.running = True
    monkeypatch.setattr(job, "_initialize", lambda *a, **kw: "already running")
    monkeypatch.setattr(runner, "abort_process", lambda *a: pytest.fail("Must not stop another job"))
    list(job._launch(data))
    assert job.running and job.trainer is existing
    assert not job._launch_lock.locked()


def test_child_console_capture_has_single_log_writer(tmp_path):
    log_path = tmp_path / "session.log"
    env = {**os.environ, "LLAMAFACTORY_SESSION_LOG": str(log_path)}
    env.pop("LLAMAFACTORY_LOG_CAPTURED", None)
    child = "from scripts.session_logging import enable_console_log; enable_console_log(); print('unique-child-line')"
    code = (
        "import sys; from scripts.session_logging import enable_console_log, run_logged; "
        f"enable_console_log(); run_logged([sys.executable, '-c', {child!r}], '.')"
    )
    result = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stderr
    assert log_path.read_text(encoding="utf-8").count("unique-child-line") == 1


def test_browser_reconnect_during_startup_does_not_finalize_job(monkeypatch, tmp_path):
    job, data = prepared_runner(monkeypatch, tmp_path)
    launch = job._launch(data)
    next(launch)
    observer = job.resume_monitor()
    assert "train.output_box" in next(observer)
    assert job.running and job._launch_lock.locked()
    list(launch)
    list(observer)
    assert not job.running and not job._launch_lock.locked()
    events = [json.loads(line) for line in (tmp_path / "lifecycle.jsonl").read_text().splitlines()]
    assert sum(event.get("event") == "exit" for event in events) == 1


@pytest.mark.parametrize("config_format", ["yaml", "json"])
def test_real_cli_loads_local_weights_and_trains_one_cpu_step(tmp_path, config_format):
    """Offline smoke test of real config/data/weight/adapter/trainer transitions, not ROCm certification."""
    from tokenizers import Tokenizer
    from tokenizers.models import WordLevel
    from tokenizers.pre_tokenizers import Whitespace
    from transformers import LlamaConfig, LlamaForCausalLM, PreTrainedTokenizerFast

    model_dir = tmp_path / "tiny-model"
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    vocabulary = {word: i for i, word in enumerate(["<unk>", "<s>", "</s>", "<pad>", "Hello", "world", "Answer"])}
    tokenizer = Tokenizer(WordLevel(vocabulary, unk_token="<unk>"))
    tokenizer.pre_tokenizer = Whitespace()
    PreTrainedTokenizerFast(
        tokenizer_object=tokenizer, unk_token="<unk>", bos_token="<s>", eos_token="</s>", pad_token="<pad>"
    ).save_pretrained(model_dir)
    model = LlamaForCausalLM(
        LlamaConfig(
            vocab_size=len(vocabulary),
            hidden_size=16,
            intermediate_size=32,
            num_hidden_layers=1,
            num_attention_heads=2,
            num_key_value_heads=2,
            max_position_embeddings=128,
            bos_token_id=1,
            eos_token_id=2,
            pad_token_id=3,
        )
    )
    model.save_pretrained(model_dir)
    (tmp_path / "dataset_info.json").write_text(json.dumps({"tiny": {"file_name": "tiny.json"}}))
    (tmp_path / "tiny.json").write_text(json.dumps([{"instruction": "Hello", "input": "", "output": "world"}] * 4))
    config = {
        "model_name_or_path": str(model_dir),
        "dataset_dir": str(tmp_path),
        "dataset": "tiny",
        "output_dir": str(output_dir),
        "stage": "sft",
        "do_train": True,
        "do_eval": True,
        "template": "default",
        "finetuning_type": "lora",
        "lora_rank": 2,
        "lora_target": "q_proj,v_proj",
        "cutoff_len": 64,
        "preprocessing_num_workers": 1,
        "dataloader_num_workers": 0,
        "use_cpu": True,
        "bf16": False,
        "fp16": False,
        "enable_liger_kernel": False,
        "flash_attn": "disabled",
        "max_steps": 1,
        "per_device_train_batch_size": 1,
        "per_device_eval_batch_size": 1,
        "logging_steps": 1,
        "save_steps": 1,
        "eval_strategy": "steps",
        "eval_steps": 1,
        "val_size": 0.5,
        "report_to": [],
        "disable_tqdm": True,
        "plot_loss": False,
    }
    config_path = tmp_path / f"training.{config_format}"
    config_path.write_text(json.dumps(config))
    env = {
        **os.environ,
        "LLAMABOARD_ENABLED": "1",
        "LLAMABOARD_WORKDIR": str(output_dir),
        "CUDA_VISIBLE_DEVICES": "",
        "USE_V1": "0",
        "FORCE_TORCHRUN": "0",
        "USE_RAY": "0",
        "HF_HUB_OFFLINE": "1",
        "TOKENIZERS_PARALLELISM": "false",
        "PYTHONUNBUFFERED": "1",
    }
    result = subprocess.run(
        [sys.executable, "-m", "llamafactory.cli", "train", str(config_path)],
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=90,
    )
    assert result.returncode == 0, (result.stdout + result.stderr)[-12000:]
    stages = {json.loads(line).get("stage") for line in (output_dir / "lifecycle.jsonl").read_text().splitlines()}
    assert {
        "runtime_import",
        "arguments",
        "tokenizer",
        "preprocessing",
        "weights",
        "adapters",
        "training",
        "evaluation",
        "checkpoint",
    } <= stages
    assert (output_dir / "checkpoint-1" / "adapter_model.safetensors").is_file()
