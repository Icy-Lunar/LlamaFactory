# Copyright 2026 the LlamaFactory team.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy at http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""Standard-library-only logging available before project dependencies are installed."""

import importlib.util
import os
import queue
import subprocess
import threading
import time
from pathlib import Path


spec = importlib.util.spec_from_file_location(
    "startup_diagnostics", Path(__file__).resolve().parents[1] / "src/llamafactory/extras/diagnostics.py"
)
diagnostics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diagnostics)
enable_console_log = diagnostics.enable_console_log
redact = diagnostics.redact


def live_output(process, interval=15):
    """Yield output or a heartbeat, even when a subprocess is completely silent."""
    messages = queue.Queue(maxsize=1024)

    def read():
        try:
            for line in process.stdout:
                messages.put(line)
        finally:
            messages.put(None)

    threading.Thread(target=read, daemon=True).start()
    while True:
        try:
            item = messages.get(timeout=interval)
        except queue.Empty:
            yield ""
            continue
        if item is None:
            return
        yield redact(item)


def run_logged(command, cwd):
    started = time.monotonic()
    process = subprocess.Popen(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
        env={**os.environ, "LLAMAFACTORY_LOG_CAPTURED": "1", "PYTHONUNBUFFERED": "1", "PYTHONUTF8": "1"},
    )
    try:
        for line in live_output(process):
            print(
                line.rstrip()
                if line
                else f"[heartbeat] PID={process.pid} elapsed={int(time.monotonic() - started)}s; waiting for output",
                flush=True,
            )
        return subprocess.CompletedProcess(command, process.wait())
    except KeyboardInterrupt:
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
        raise
