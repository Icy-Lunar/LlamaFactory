"""Environment setup shared by XPU training and accelerator probes."""

import os
import shutil
import warnings


def configure_xpu_environment(env: dict[str, str]) -> None:
    # Intel Arc drivers otherwise reject a single allocation larger than 4 GiB on Windows.
    env.setdefault("UR_L0_ENABLE_RELAXED_ALLOCATION_LIMITS", "1")
    path_key = next((key for key in env if key.lower() == "path"), "PATH")
    if os.name == "nt" and shutil.which("cl", path=env.get(path_key)) is None:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                from setuptools._distutils._msvccompiler import _get_vc_env

                msvc_env = _get_vc_env("x64")
        except (ImportError, OSError, RuntimeError):
            return
        for name in ("path", "include", "lib", "libpath"):
            if value := msvc_env.get(name):
                target_key = next((key for key in env if key.lower() == name), name.upper())
                env[target_key] = value
