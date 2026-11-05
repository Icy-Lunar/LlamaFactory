# Copyright 2026 the LlamaFactory team.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy at http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""Dependency-free stage records and bounded log readers for startup diagnostics."""

import faulthandler
import json
import logging
import os
import platform
import re
import sys
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path


def is_rocm_wsl() -> bool:
    # Inspect build metadata, never call a GPU API from the Gradio request thread.
    torch = sys.modules.get("torch")
    return bool(getattr(getattr(torch, "version", None), "hip", None)) and (
        "microsoft" in platform.release().lower() or bool(os.getenv("WSL_INTEROP"))
    )


def redact(text: str) -> str:
    text = re.sub(r"(?i)(bearer\s+)\S+", r"\1[REDACTED]", text)
    return re.sub(
        r"(?i)((?:[\w-]*(?:token|password|secret|api[_-]?key))[\"']?\s*[:=]\s*[\"']?)[^\s,\"'}]+",
        r"\1[REDACTED]",
        text,
    )


def tail(path, limit: int = 24000) -> str:
    try:
        with open(path, "rb") as stream:
            stream.seek(0, os.SEEK_END)
            stream.seek(max(0, stream.tell() - limit))
            return redact(stream.read(limit).decode("utf-8", errors="replace"))
    except OSError:
        return ""


def stage(name: str, **details) -> None:
    """Flush a stage before a potentially blocking operation; no config/secret dumps."""
    if os.getenv("LOCAL_RANK", "0") != "0":
        return
    record = {"time": time.time(), "stage": name, "pid": os.getpid(), **details}
    print("[stage] " + json.dumps(record, ensure_ascii=True), file=sys.stderr, flush=True)
    directory = os.getenv("LLAMABOARD_WORKDIR")
    if directory:
        try:
            path = Path(directory)
            path.mkdir(parents=True, exist_ok=True)
            with (path / "lifecycle.jsonl").open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(record) + "\n")
            temporary = path / f".runtime-state-{os.getpid()}.tmp"
            temporary.write_text(json.dumps(record), encoding="utf-8")
            temporary.replace(path / "runtime_state.json")
        except OSError as error:
            print(f"[diagnostics] Cannot persist stage: {error}", file=sys.stderr, flush=True)


def enable_diagnostics() -> None:
    if os.getenv("LLAMABOARD_ENABLED") != "1":
        return
    faulthandler.enable()
    # Native stalls can hold the GIL: faulthandler's watchdog does not require it.
    faulthandler.dump_traceback_later(120, repeat=True)
    stage("runtime_import", python=platform.python_version(), platform=platform.system())


def training_started() -> None:
    if os.getenv("LLAMABOARD_ENABLED") == "1":
        faulthandler.cancel_dump_traceback_later()
    stage("training")


def enable_console_log() -> str:
    """Tee Python stdout/stderr without replacing terminal ownership or Ctrl+C."""
    if getattr(sys.stderr, "session_log", None):
        return sys.stderr.session_log
    if os.getenv("LLAMAFACTORY_LOG_CAPTURED") == "1" and os.getenv("LLAMAFACTORY_SESSION_LOG"):
        # The launcher already captures this pipe. Only one process may rotate a file.
        return os.environ["LLAMAFACTORY_SESSION_LOG"]
    path = Path(
        os.getenv("LLAMAFACTORY_SESSION_LOG", "")
        or (Path("logs") / f"session-{time.strftime('%Y%m%d-%H%M%S')}-{os.getpid()}.log")
    ).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    os.environ["LLAMAFACTORY_SESSION_LOG"] = str(path)
    handler = RotatingFileHandler(path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))

    class Tee:
        session_log = str(path)

        def __init__(self, stream):
            self.stream = stream

        def write(self, value):
            self.stream.write(value)
            self.stream.flush()
            if value.strip():
                handler.handle(logging.LogRecord("session", logging.INFO, "", 0, redact(value.rstrip()), (), None))
            return len(value)

        def flush(self):
            self.stream.flush()
            handler.flush()

        def __getattr__(self, name):
            return getattr(self.stream, name)

    sys.stdout, sys.stderr = Tee(sys.stdout), Tee(sys.stderr)
    print(f"[diagnostics] Session log: {path}", flush=True)
    return str(path)
