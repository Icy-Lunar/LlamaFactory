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

"""Install Liger with a real Windows Triton provider, without alias/dummy packages.

Upstream universal wheels require the distribution named ``triton`` even when
the same Python module is supplied by triton-xpu or triton-windows. Build an
explicitly labelled local wheel with that dependency replaced, leaving kernel
sources unchanged. Normal pip resolution and runtime checks remain mandatory.
"""

import argparse
import base64
import csv
import hashlib
import importlib.metadata as metadata
import io
import json
import os
import subprocess
import sys
import tempfile
import zipfile
from email import policy
from email.parser import BytesParser
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
from packaging.version import Version


ROOT = Path(__file__).resolve().parents[1]
PROVIDERS = ("triton", "triton-windows", "triton-xpu", "pytorch-triton-xpu", "pytorch-triton-rocm", "triton-ascend")
# https://github.com/triton-lang/triton-windows (PyTorch compatibility table)
WINDOWS_TRITON = {
    (2, 4): "3.1",
    (2, 5): "3.1",
    (2, 6): "3.2",
    (2, 7): "3.3",
    (2, 8): "3.4",
    (2, 9): "3.5",
    (2, 10): "3.6",
    (2, 11): "3.6",
    (2, 12): "3.7",
    (2, 13): "3.7",
    (2, 14): "3.8",
    (2, 15): "3.9",
}
# Only the reviewed upstream release is repackaged; future metadata needs review.
LIGER_RELEASE = "0.8.5"


def windows_triton_requirement(torch_version: str) -> str:
    release = Version(torch_version).release[:2]
    if release not in WINDOWS_TRITON:
        raise ValueError(f"No reviewed Windows Triton profile for torch {torch_version}; retain standard training.")
    minor = WINDOWS_TRITON[release]
    major, number = map(int, minor.split("."))
    return f"triton-windows>={minor},<{major}.{number + 1}"


def select_provider(backend: str, versions: dict[str, str], torch_version: str) -> tuple[str, str]:
    """Select the installed backend provider before considering a new install.

    Distribution names are used here because every provider exports the same
    ``triton`` Python package. Importing that shared namespace cannot identify
    which wheel owns it.
    """
    present = [name for name in PROVIDERS if name in versions]
    if len(present) > 1:
        raise ValueError(f"Overlapping Triton distributions: {', '.join(present)}. Use a clean environment.")
    if backend == "xpu":
        if present not in (["triton-xpu"], ["pytorch-triton-xpu"]):
            raise ValueError("XPU requires the Triton provider bundled with the official PyTorch XPU build.")
        name = present[0]
        return name, f"{name}=={versions[name]}"
    if backend not in {"cuda", "rocm"}:
        raise ValueError(f"No Windows Liger profile for {backend}")
    if present and present != ["triton-windows"]:
        raise ValueError(f"Do not overwrite {present[0]} with triton-windows; use a clean environment.")
    requirement = windows_triton_requirement(torch_version)
    if present and not Requirement(requirement).specifier.contains(versions[present[0]]):
        raise ValueError(f"Installed triton-windows does not match {requirement}; use a matching environment.")
    return "triton-windows", requirement


def adapt_wheel(source: Path, destination: Path, provider: str, provider_version: str, backend: str) -> Path:
    """Rewrite only dependency metadata; retain licenses, sources, and a provenance record."""
    if provider not in {"triton-xpu", "pytorch-triton-xpu", "triton-windows"}:
        raise ValueError("Unreviewed Triton provider")
    with zipfile.ZipFile(source) as archive:
        files = {name: archive.read(name) for name in archive.namelist() if not name.endswith("/")}
    entries = [name for name in files if name.endswith(".dist-info/METADATA")]
    if len(entries) != 1:
        raise ValueError("Expected one wheel metadata entry")
    old_info = entries[0].rsplit("/", 1)[0]
    info = BytesParser(policy=policy.compat32).parsebytes(files[entries[0]])
    if canonicalize_name(info["Name"]) != "liger-kernel" or info["Version"] != LIGER_RELEASE:
        raise ValueError("Unreviewed upstream Liger wheel")
    requirements = info.get_all("Requires-Dist", [])
    triton_requirements = [
        Requirement(item) for item in requirements if canonicalize_name(Requirement(item).name) == "triton"
    ]
    if len(triton_requirements) != 1 or triton_requirements[0].marker is not None:
        raise ValueError("Upstream Triton metadata changed; review before adapting")
    if not triton_requirements[0].specifier.contains(provider_version):
        raise ValueError("The Triton provider does not meet Liger's required API version")
    local_version = f"{LIGER_RELEASE}+cyrene.{backend}1"
    info.replace_header("Version", local_version)
    del info["Requires-Dist"]
    for item in requirements:
        if canonicalize_name(Requirement(item).name) != "triton":
            info["Requires-Dist"] = item
    info["Requires-Dist"] = f"{provider}=={provider_version}"
    new_info = f"liger_kernel-{local_version}.dist-info"
    output_files = {}
    for name, content in files.items():
        if name in {f"{old_info}/RECORD", f"{old_info}/RECORD.jws", f"{old_info}/RECORD.p7s"}:
            continue
        output_files[name.replace(old_info + "/", new_info + "/", 1)] = content
    output_files[f"{new_info}/METADATA"] = info.as_bytes()
    output_files[f"{new_info}/cyrene_backend.json"] = json.dumps(
        {
            "upstream_version": LIGER_RELEASE,
            "source_wheel": source.name,
            "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "provider": provider,
            "provider_version": provider_version,
            "backend": backend,
            "change": "Replace generic Triton dependency only; kernel source unchanged.",
        },
        indent=2,
    ).encode()
    record = io.StringIO(newline="")
    writer = csv.writer(record, lineterminator="\n")
    for name, content in output_files.items():
        digest = base64.urlsafe_b64encode(hashlib.sha256(content).digest()).rstrip(b"=").decode()
        writer.writerow([name, "sha256=" + digest, len(content)])
    writer.writerow([f"{new_info}/RECORD", "", ""])
    output_files[f"{new_info}/RECORD"] = record.getvalue().encode()
    destination.mkdir(parents=True, exist_ok=True)
    output = destination / f"liger_kernel-{local_version}-py3-none-any.whl"
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in output_files.items():
            archive.writestr(name, content)
    return output


def pip(*arguments: str) -> None:
    command = [sys.executable, "-m", "pip", *arguments]
    print("+ " + subprocess.list2cmdline(command), flush=True)
    subprocess.run(command, check=True)


def installed_adapter_matches(backend: str, provider: str, provider_version: str) -> bool:
    try:
        distribution = metadata.distribution("liger-kernel")
    except metadata.PackageNotFoundError:
        return False
    if Version(Version(distribution.version).base_version) > Version(LIGER_RELEASE):
        raise ValueError("A newer Liger is already installed; review its Windows profile instead of downgrading it.")
    expected = f"{LIGER_RELEASE}+cyrene.{backend}1"
    if distribution.version != expected:
        return False
    provenance = json.loads(distribution.read_text("cyrene_backend.json") or "{}")
    dependencies = [Requirement(item) for item in distribution.requires or []]
    return (
        provenance.get("backend") == backend
        and provenance.get("provider") == provider
        and provenance.get("provider_version") == provider_version
        and any(
            canonicalize_name(item.name) == provider and str(item.specifier) == f"=={provider_version}"
            for item in dependencies
        )
        and all(canonicalize_name(item.name) != "triton" for item in dependencies)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", choices=("xpu", "cuda", "rocm"), required=True)
    parser.add_argument("--constraints", type=Path, required=True)
    args = parser.parse_args()
    if os.name != "nt":
        raise ValueError("This adapter is only for Windows")
    import torch

    if args.backend == "xpu":
        from llamafactory.extras.accelerator import configure_xpu_environment

        configure_xpu_environment(os.environ)
    versions = {canonicalize_name(dist.metadata["Name"]): dist.version for dist in metadata.distributions()}
    provider, requirement = select_provider(args.backend, versions, torch.__version__)
    if args.backend == "cuda":
        major, _ = torch.cuda.get_device_capability()
        triton_minor = WINDOWS_TRITON[Version(torch.__version__).release[:2]]
        if major < 7 or (major == 7 and Version(triton_minor) > Version("3.2")):
            raise ValueError("This NVIDIA GPU needs an older Triton/Torch profile; no automatic Torch downgrade.")
    if provider in versions:
        print(f"Detected installed Windows Triton provider: {provider} {versions[provider]}.")
    else:
        print(f"No compatible Windows Triton provider is installed; installing {requirement}.")
        pip("install", "--only-binary=:all:", "-c", str(args.constraints), requirement)
    import triton

    target = triton.runtime.driver.active.get_current_target()
    expected = {"xpu": "xpu", "cuda": "cuda", "rocm": "hip"}[args.backend]
    if target.backend != expected:
        raise ValueError(f"Triton target {target.backend} does not match {expected}")
    provider_version = metadata.version(provider)
    print(f"Windows backend: {provider} {provider_version}; Liger {LIGER_RELEASE} (local dependency adapter).")
    if installed_adapter_matches(args.backend, provider, provider_version):
        print("Matching local Liger adapter is already installed; retain it and proceed to runtime verification.")
        return
    with tempfile.TemporaryDirectory(prefix="llamafactory-liger-") as folder:
        temporary = Path(folder)
        # Download only: do not install upstream's generic Triton requirement.
        pip(
            "download",
            "--no-deps",
            "--only-binary=:all:",
            "--index-url",
            "https://pypi.org/simple",
            "--dest",
            str(temporary),
            f"liger-kernel=={LIGER_RELEASE}",
        )
        sources = list(temporary.glob("liger_kernel-*.whl"))
        if len(sources) != 1:
            raise ValueError("Expected exactly one official Liger wheel")
        adapted = adapt_wheel(sources[0], temporary / "adapted", provider, provider_version, args.backend)
        # Retain full pip resolution and constrain newly selected providers too.
        constraints = temporary / "hardware.txt"
        constraints.write_text(
            args.constraints.read_text(encoding="utf-8") + f"\n{provider}=={provider_version}\ntriton===0\n",
            encoding="utf-8",
        )
        pip("install", "--dry-run", "-c", str(constraints), str(adapted))
        pip("install", "-c", str(constraints), str(adapted))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"Windows Liger installation unavailable: {error}", file=sys.stderr)
        if "4551" in str(error) or "application control" in str(error).casefold():
            print(
                "Windows application control blocked the ROCm/Triton compiler or its generated native module. "
                "Use standard training, or ask the endpoint administrator to approve the blocked file; "
                "the installer will not bypass host security policy.",
                file=sys.stderr,
            )
        sys.exit(1)
