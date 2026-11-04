from scripts.terminal_locales import TEXT, translate
from scripts.terminal_wizard import WizardConfig, build_command, diagnose_failure, label_for


def configuration(**overrides):
    values = {
        "language": "zh",
        "backend": "rocm",
        "rocm_profile": "aimax395",
        "driver_mode": "auto",
        "driver_installer": None,
        "host_mode": "network",
        "liger": "auto",
        "action": "start",
    }
    values.update(overrides)
    return WizardConfig(**values)


def test_all_terminal_locales_have_the_same_resource_keys():
    reference = set(TEXT["en"])
    assert reference
    assert all(set(resources) == reference for resources in TEXT.values())


def test_unknown_language_falls_back_to_english():
    assert translate("unknown", "success") == TEXT["en"]["success"]


def test_wizard_builds_complete_rocm_command():
    command = build_command(configuration(), python="python-test", dry_run=True)
    assert command[0] == "python-test"
    assert command[command.index("--backend") + 1] == "rocm"
    assert command[command.index("--rocm-profile") + 1] == "aimax395"
    assert command[command.index("--host-mode") + 1] == "network"
    assert "--dry-run" in command
    assert "--no-start" not in command


def test_strict_wizard_mode_requires_every_optional_capability():
    command = build_command(configuration(liger="required"))
    assert "--require-all-capabilities" in command


def test_wizard_maps_prepare_and_check_actions_to_existing_bootstrap_options():
    assert "--no-start" in build_command(configuration(action="prepare"))
    assert "--check-only" in build_command(configuration(action="check"))
    assert "--skip-install" in build_command(configuration(action="quick"))


def test_wizard_forwards_reviewed_windows_driver_installer():
    command = build_command(configuration(driver_mode="install", driver_installer=r"D:\Drivers\amd.exe"))
    assert command[command.index("--driver-installer") + 1] == r"D:\Drivers\amd.exe"


def test_summary_labels_are_localized_instead_of_exposing_internal_values():
    config = configuration()
    assert label_for(config, "access", "network") == TEXT["zh"]["access_network"]
    assert label_for(config, "action", "start") == TEXT["zh"]["action_start"]


def test_windows_application_control_failure_has_guided_liger_fallback():
    config = configuration(liger="required")
    diagnosis = diagnose_failure(
        "Windows Liger installation unavailable: [WinError 4551] application control policy blocked this file",
        config,
    )
    assert diagnosis.title_key == "failure_app_control"
    assert diagnosis.can_retry_without_liger is True


def test_runtime_failure_does_not_offer_fake_liger_fallback():
    diagnosis = diagnose_failure("PyTorch cannot use rocm after repeated device probes", configuration())
    assert diagnosis.title_key == "failure_runtime"
    assert diagnosis.can_retry_without_liger is False
