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
