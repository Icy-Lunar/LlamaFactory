"""Dependency-free, localized terminal wizard for multi-backend setup."""

from __future__ import annotations

import argparse
import ctypes
import os
import platform
import shutil
import subprocess
import sys
import time
import unicodedata
from collections import deque
from dataclasses import dataclass, replace
from datetime import datetime


try:
    from .bootstrap_multibackend import (
        ROOT,
        driver_is_ready,
        environment_python,
        hardware_inventory,
        resolve_windows_installer,
        select_environment_directory,
        select_rocm_profile,
    )
    from .session_logging import live_output
    from .terminal_locales import LANGUAGE_CHOICES, translate
except ImportError:
    from bootstrap_multibackend import (  # type: ignore[no-redef]
        ROOT,
        driver_is_ready,
        environment_python,
        hardware_inventory,
        resolve_windows_installer,
        select_environment_directory,
        select_rocm_profile,
    )
    from session_logging import live_output  # type: ignore[no-redef]
    from terminal_locales import LANGUAGE_CHOICES, translate  # type: ignore[no-redef]


RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
WHITE = "\033[97m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BG_NAVY = "\033[48;5;17m"
BG_BLUE = "\033[48;5;24m"
BG_GRAY = "\033[48;5;236m"
BG_GREEN = "\033[48;5;22m"
BG_RED = "\033[48;5;52m"


@dataclass(frozen=True)
class WizardConfig:
    language: str
    backend: str
    rocm_profile: str
    driver_mode: str
    driver_installer: str | None
    host_mode: str
    liger: str
    action: str


@dataclass(frozen=True)
class ExecutionResult:
    code: int
    output: str
    log_path: str


@dataclass(frozen=True)
class FailureDiagnosis:
    title_key: str
    detail_key: str
    next_key: str
    can_retry_without_liger: bool = False


def enable_virtual_terminal() -> bool:
    if not sys.stdout.isatty():
        return False
    if os.name != "nt":
        return os.environ.get("TERM", "") != "dumb"
    try:
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        return bool(kernel32.SetConsoleMode(handle, mode.value | 0x0004))
    except (AttributeError, OSError):
        return False


class Screen:
    def __init__(self, *, color: bool = True, clear: bool = True):
        self.color = color and enable_virtual_terminal()
        self.clear_enabled = clear and sys.stdout.isatty()

    def styled(self, value: str, *styles: str) -> str:
        if not self.color:
            return value
        return "".join(styles) + value + RESET

    def clear(self) -> None:
        if self.clear_enabled:
            print("\033[2J\033[H", end="", flush=True)

    def width(self) -> int:
        return max(56, min(100, shutil.get_terminal_size((80, 24)).columns))

    @staticmethod
    def padded(value: str, width: int) -> str:
        display_width = sum(2 if unicodedata.east_asian_width(character) in {"F", "W"} else 1 for character in value)
        return value + " " * max(0, width - display_width)

    def block(self, title: str, lines: list[str], *, tone: str = "normal") -> None:
        width = self.width()
        background = {"good": BG_GREEN, "bad": BG_RED, "accent": BG_BLUE}.get(tone, BG_GRAY)
        print(self.styled(self.padded(f" {title} ", width), BOLD, WHITE, background))
        for line in lines:
            print(self.styled(self.padded(f"  {line}", width), WHITE, background))
        print()

    def banner(self, language: str) -> None:
        width = self.width()
        print(self.styled(self.padded(" ", width), BG_NAVY))
        print(self.styled(self.padded(f"  {translate(language, 'title')}", width), BOLD, CYAN, BG_NAVY))
        print(self.styled(self.padded(f"  {translate(language, 'subtitle')}", width), WHITE, BG_NAVY))
        print(self.styled(self.padded(" ", width), BG_NAVY))
        print()

    def log_line(self, line: str) -> None:
        lowered = line.casefold()
        if any(marker in lowered for marker in ("error", "failed", "traceback")):
            print(self.styled(line, RED))
        elif any(marker in lowered for marker in ("warning", "retrying", "unavailable")):
            print(self.styled(line, YELLOW))
        elif any(marker in lowered for marker in ("success", "completed", "available")):
            print(self.styled(line, GREEN))
        else:
            print(self.styled(line, DIM))


class ProgressView:
    """Turn verbose installer output into a small set of user-facing phases."""

    PHASES = (
        (("selected backend:", "detected:"), "phase_hardware"),
        (("creating virtual environment", " -m venv "), "phase_environment"),
        (("collecting ", "downloading "), "phase_download"),
        (("installing collected packages", "successfully installed"), "phase_dependencies"),
        (("rocm_sdk init", "device runtime is not ready"), "phase_runtime"),
        (("pip check", "check_training_environment.py"), "phase_verify"),
        (("windows backend:", "liger "), "phase_acceleration"),
    )

    def __init__(self, screen: Screen, language: str):
        self.screen = screen
        self.language = language
        self.seen: set[str] = set()
        self.current_phase = "phase_environment"

    def show_phase(self, key: str) -> None:
        self.current_phase = key
        if key not in self.seen:
            self.seen.add(key)
            self.screen.block(
                translate(self.language, key), [translate(self.language, key + "_detail")], tone="accent"
            )

    def consume(self, line: str) -> None:
        stripped = line.strip()
        lowered = stripped.casefold()
        for markers, key in self.PHASES:
            if any(marker in lowered for marker in markers):
                self.show_phase(key)
                break
        if "starting webui at" in lowered or "running on local url" in lowered:
            self.show_phase("phase_ready")
            self.screen.log_line(stripped)
            return
        if not stripped:
            return
        if "phase_ready" in self.seen or stripped.startswith("[stage]") or lowered.startswith("traceback"):
            self.screen.log_line(stripped)
            return
        if any(marker in lowered for marker in ("error", "failed", "warning", "unavailable", "winerror")):
            self.screen.log_line(stripped)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language", choices=tuple(code for code, _ in LANGUAGE_CHOICES))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-color", action="store_true")
    parser.add_argument("--no-clear", action="store_true")
    return parser.parse_args(argv)


def ask_choice(
    screen: Screen,
    language: str,
    title: str,
    options: list[tuple[str, str]],
    *,
    default: int = 1,
) -> str:
    while True:
        screen.block(title, [f"{index}. {label}" for index, (_, label) in enumerate(options, 1)], tone="accent")
        try:
            raw = input(screen.styled(f"[{default}] > ", BOLD, CYAN)).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            raise SystemExit(130) from None
        if not raw:
            raw = str(default)
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1][0]
        print(screen.styled(translate(language, "invalid"), YELLOW))


def choose_language(screen: Screen, requested: str | None) -> str:
    if requested:
        return requested
    return ask_choice(screen, "en", translate("en", "language"), list(LANGUAGE_CHOICES))


def accelerator_lines(inventory: dict[str, list[str]]) -> list[str]:
    lines = []
    for backend in ("cuda", "xpu", "rocm"):
        for name in inventory[backend]:
            lines.append(f"{backend.upper()}: {name}")
    return lines


def collect_configuration(screen: Screen, language: str) -> WizardConfig:
    inventory = hardware_inventory()
    detected = [backend for backend in ("cuda", "xpu", "rocm") if inventory[backend]]
    screen.block(
        translate(language, "system"),
        [
            f"{translate(language, 'os')}: {platform.system()} {platform.release()}",
            f"{translate(language, 'python')}: {sys.executable}",
            *(accelerator_lines(inventory) or [f"{translate(language, 'detected')}: {translate(language, 'none')}"]),
        ],
    )
    if not detected:
        screen.block(translate(language, "system"), [translate(language, "no_backend")], tone="bad")
        raise SystemExit(1)

    if len(detected) == 1:
        backend = detected[0]
        print(screen.styled(translate(language, "backend_auto"), GREEN))
    else:
        print(screen.styled(translate(language, "multiple"), YELLOW))
        backend = ask_choice(
            screen,
            language,
            translate(language, "backend"),
            [(item, f"{item.upper()} — {', '.join(inventory[item])}") for item in detected],
        )

    rocm_profile = select_rocm_profile("auto", inventory["rocm"])
    system_name = platform.system().lower()
    environment = select_environment_directory(backend, system_name, rocm_profile)
    existing_environment = environment_python(environment, system_name).is_file()
    screen.block(
        translate(language, "environment"),
        [
            str(environment),
            translate(language, "environment_found" if existing_environment else "environment_new"),
        ],
        tone="good" if existing_environment else "normal",
    )
    ready = driver_is_ready(backend)
    status = translate(language, "driver_ready" if ready else "driver_missing")
    print(screen.styled(status, GREEN if ready else YELLOW))
    driver_options = []
    if ready:
        driver_options.append(("auto", translate(language, "driver_keep")))
    if backend != "xpu":
        driver_options.append(("install", translate(language, "driver_install")))
    driver_options.append(("skip", translate(language, "driver_skip")))
    driver_mode = ask_choice(screen, language, translate(language, "driver"), driver_options)

    driver_installer = None
    if platform.system() == "Windows" and backend in {"cuda", "rocm"} and driver_mode == "install":
        discovered = resolve_windows_installer(backend, None)
        if discovered:
            driver_installer = str(discovered)
        else:
            try:
                value = input(screen.styled(translate(language, "installer") + "\n> ", CYAN)).strip()
            except (EOFError, KeyboardInterrupt):
                raise SystemExit(130) from None
            driver_installer = value or None

    host_mode = ask_choice(
        screen,
        language,
        translate(language, "access"),
        [
            ("local", translate(language, "access_local")),
            ("network", translate(language, "access_network")),
        ],
    )
    liger = ask_choice(
        screen,
        language,
        translate(language, "liger"),
        [
            ("auto", translate(language, "liger_auto")),
            ("off", translate(language, "liger_off")),
            ("required", translate(language, "liger_required")),
        ],
    )
    if existing_environment:
        actions = [
            ("quick", translate(language, "action_quick")),
            ("repair", translate(language, "action_repair")),
            ("check", translate(language, "action_check")),
        ]
    else:
        actions = [
            ("start", translate(language, "action_start")),
            ("prepare", translate(language, "action_prepare")),
        ]
    action = ask_choice(
        screen,
        language,
        translate(language, "action"),
        actions,
    )
    return WizardConfig(
        language=language,
        backend=backend,
        rocm_profile=rocm_profile,
        driver_mode=driver_mode,
        driver_installer=driver_installer,
        host_mode=host_mode,
        liger=liger,
        action=action,
    )


def label_for(config: WizardConfig, group: str, value: str) -> str:
    keys = {
        ("driver", "auto"): "driver_keep",
        ("driver", "install"): "driver_install",
        ("driver", "skip"): "driver_skip",
        ("access", "local"): "access_local",
        ("access", "network"): "access_network",
        ("liger", "auto"): "liger_auto",
        ("liger", "off"): "liger_off",
        ("liger", "required"): "liger_required",
        ("action", "quick"): "action_quick",
        ("action", "repair"): "action_repair",
        ("action", "start"): "action_start",
        ("action", "prepare"): "action_prepare",
        ("action", "check"): "action_check",
    }
    return translate(config.language, keys.get((group, value), value))


def build_command(config: WizardConfig, *, python: str | None = None, dry_run: bool = False) -> list[str]:
    command = [
        python or sys.executable,
        "-X",
        "utf8",
        str(ROOT / "scripts/bootstrap_multibackend.py"),
        "--backend",
        config.backend,
        "--driver-mode",
        config.driver_mode,
        "--rocm-profile",
        config.rocm_profile,
        "--host-mode",
        config.host_mode,
        "--liger",
        config.liger,
    ]
    if config.driver_installer:
        command.extend(["--driver-installer", config.driver_installer])
    if config.action == "prepare":
        command.append("--no-start")
    elif config.action == "check":
        command.append("--check-only")
    elif config.action == "quick":
        command.append("--skip-install")
    if config.liger == "required":
        command.append("--require-all-capabilities")
    if dry_run:
        command.append("--dry-run")
    return command


def review(screen: Screen, config: WizardConfig, inventory: dict[str, list[str]] | None = None) -> bool:
    devices = (inventory or hardware_inventory())[config.backend]
    environment = select_environment_directory(config.backend, platform.system().lower(), config.rocm_profile)
    screen.block(
        translate(config.language, "summary"),
        [
            f"{translate(config.language, 'summary_backend')}: {config.backend.upper()}",
            f"{translate(config.language, 'summary_device')}: {', '.join(devices)}",
            f"{translate(config.language, 'summary_environment')}: {environment}",
            f"{translate(config.language, 'summary_driver')}: {label_for(config, 'driver', config.driver_mode)}",
            f"{translate(config.language, 'summary_access')}: {label_for(config, 'access', config.host_mode)}",
            f"{translate(config.language, 'summary_liger')}: {label_for(config, 'liger', config.liger)}",
            f"{translate(config.language, 'summary_action')}: {label_for(config, 'action', config.action)}",
        ],
        tone="accent",
    )
    answer = ask_choice(
        screen,
        config.language,
        translate(config.language, "confirm"),
        [("yes", translate(config.language, "yes")), ("no", translate(config.language, "no"))],
    )
    return answer == "yes"


def execute(screen: Screen, config: WizardConfig, command: list[str]) -> ExecutionResult:
    log_dir = ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"setup-wizard-{datetime.now():%Y%m%d-%H%M%S}.log"
    screen.block(
        translate(config.language, "running"),
        [f"{translate(config.language, 'log')}: {log_path}"],
        tone="accent",
    )
    output_lines = deque(maxlen=2000)
    started = time.monotonic()
    progress = ProgressView(screen, config.language)
    with log_path.open("w", encoding="utf-8", newline="\n") as log:
        log.write(subprocess.list2cmdline(command) + "\n\n")
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            env={**os.environ, "PYTHONUNBUFFERED": "1", "PYTHONUTF8": "1"},
        )
        try:
            assert process.stdout is not None
            for line in live_output(process):
                heartbeat = not line
                if not line:
                    line = (
                        translate(
                            config.language,
                            "heartbeat",
                            pid=process.pid,
                            elapsed=int(time.monotonic() - started),
                            phase=translate(config.language, progress.current_phase),
                        )
                        + "\n"
                    )
                    screen.log_line(line.rstrip())
                output_lines.append(line)
                log.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {line}")
                log.flush()
                if not heartbeat:
                    progress.consume(line)
            return ExecutionResult(process.wait(), "".join(output_lines), str(log_path))
        except KeyboardInterrupt:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
            raise


def diagnose_failure(output: str, config: WizardConfig) -> FailureDiagnosis:
    lowered = output.casefold()
    if "winerror 4551" in lowered or "application control policy" in lowered:
        return FailureDiagnosis(
            "failure_app_control",
            "failure_app_control_detail",
            "failure_app_control_next",
            can_retry_without_liger=config.liger == "required",
        )
    if "windows liger provider installation failed" in lowered or "liger is required but unavailable" in lowered:
        return FailureDiagnosis(
            "failure_liger",
            "failure_liger_detail",
            "failure_liger_next",
            can_retry_without_liger=config.liger == "required",
        )
    if "required training capabilities unavailable" in lowered:
        return FailureDiagnosis(
            "failure_capabilities",
            "failure_capabilities_detail",
            "failure_capabilities_next",
            can_retry_without_liger=config.liger == "required",
        )
    if "pytorch cannot use rocm" in lowered or "requested device cuda is unavailable" in lowered:
        return FailureDiagnosis("failure_runtime", "failure_runtime_detail", "failure_runtime_next")
    if "no space left" in lowered or "not enough space" in lowered:
        return FailureDiagnosis("failure_disk", "failure_disk_detail", "failure_disk_next")
    if "address already in use" in lowered or "only one usage of each socket" in lowered:
        return FailureDiagnosis("failure_port", "failure_port_detail", "failure_port_next")
    return FailureDiagnosis("failure_unknown", "failure_unknown_detail", "failure_unknown_next")


def show_failure(screen: Screen, config: WizardConfig, result: ExecutionResult) -> FailureDiagnosis:
    diagnosis = diagnose_failure(result.output, config)
    screen.block(
        translate(config.language, diagnosis.title_key),
        [
            translate(config.language, diagnosis.detail_key),
            translate(config.language, diagnosis.next_key),
            f"{translate(config.language, 'log')}: {result.log_path}",
        ],
        tone="bad",
    )
    return diagnosis


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    screen = Screen(color=not args.no_color, clear=not args.no_clear)
    language = choose_language(screen, args.language)
    screen.clear()
    screen.banner(language)
    try:
        config = collect_configuration(screen, language)
        if not review(screen, config):
            screen.block(translate(language, "summary"), [translate(language, "cancelled")])
            return 0
        command = build_command(config, dry_run=args.dry_run)
        if args.dry_run:
            screen.block(
                translate(language, "running"),
                [translate(language, "dry_run"), subprocess.list2cmdline(command)],
                tone="accent",
            )
            return 0
        result = execute(screen, config, command)
        if result.code == 0:
            screen.block(translate(language, "summary"), [translate(language, "success")], tone="good")
        elif result.code == 10:
            screen.block(translate(language, "summary"), [translate(language, "reboot")], tone="accent")
        else:
            diagnosis = show_failure(screen, config, result)
            if diagnosis.can_retry_without_liger:
                fallback = ask_choice(
                    screen,
                    language,
                    translate(language, "fallback_question"),
                    [("yes", translate(language, "fallback_yes")), ("no", translate(language, "fallback_no"))],
                )
                if fallback == "yes":
                    fallback_action = config.action if config.action in {"prepare", "check"} else "quick"
                    fallback_config = replace(config, liger="off", action=fallback_action)
                    fallback_result = execute(screen, fallback_config, build_command(fallback_config))
                    if fallback_result.code == 0:
                        screen.block(
                            translate(language, "summary"),
                            [translate(language, "fallback_success")],
                            tone="good",
                        )
                    else:
                        show_failure(screen, fallback_config, fallback_result)
                    return fallback_result.code
        return result.code
    except KeyboardInterrupt:
        print()
        screen.block(translate(language, "summary"), [translate(language, "cancelled")])
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
