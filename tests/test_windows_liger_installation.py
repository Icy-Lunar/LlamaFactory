import base64
import csv
import hashlib
import io
import json
import zipfile
from email.parser import BytesParser
from pathlib import Path
from types import SimpleNamespace

import pytest
from packaging.requirements import Requirement

from scripts import bootstrap_webui as bootstrap
from scripts import install_windows_liger as windows


@pytest.mark.parametrize(
    ("torch", "expected"),
    [
        ("2.9.1+rocm7.2.1", "triton-windows>=3.5,<3.6"),
        ("2.13.0+cu128", "triton-windows>=3.7,<3.8"),
        ("2.6.0+cu124", "triton-windows>=3.2,<3.3"),
        ("2.15.0+cu130", "triton-windows>=3.9,<3.10"),
    ],
)
def test_windows_version_matching(torch, expected):
    assert windows.windows_triton_requirement(torch) == expected


def test_unknown_torch_is_not_guessed():
    with pytest.raises(ValueError, match="No reviewed"):
        windows.windows_triton_requirement("3.0.0")


def test_xpu_provider_is_preserved_not_replaced_with_cuda():
    assert windows.select_provider("xpu", {"triton-xpu": "3.7.2"}, "2.13.0+xpu") == (
        "triton-xpu",
        "triton-xpu==3.7.2",
    )
    with pytest.raises(ValueError, match="bundled"):
        windows.select_provider("xpu", {}, "2.13.0+xpu")


@pytest.mark.parametrize(
    "versions",
    [
        {"triton": "3.7.0", "triton-xpu": "3.7.2"},
        {"triton-windows": "3.7.0", "triton-xpu": "3.7.2"},
    ],
)
def test_overlapping_module_providers_are_rejected(versions):
    with pytest.raises(ValueError, match="Overlapping"):
        windows.select_provider("xpu", versions, "2.13.0+xpu")


def test_existing_windows_triton_must_match_torch():
    with pytest.raises(ValueError, match="does not match"):
        windows.select_provider("cuda", {"triton-windows": "3.2.0.post21"}, "2.13.0")
    with pytest.raises(ValueError, match="Do not overwrite"):
        windows.select_provider("cuda", {"triton-xpu": "3.7.2"}, "2.13.0")


def test_existing_windows_triton_is_selected_without_linux_triton():
    provider, requirement = windows.select_provider(
        "cuda", {"triton-windows": "3.7.1.post27"}, "2.13.0+cu128"
    )
    assert provider == "triton-windows"
    assert Requirement(requirement).specifier.contains("3.7.1.post27")


def wheel_fixture(tmp_path, version=windows.LIGER_RELEASE):
    source = tmp_path / "upstream.whl"
    with zipfile.ZipFile(source, "w") as archive:
        prefix = f"liger_kernel-{version}.dist-info"
        archive.writestr(
            f"{prefix}/METADATA",
            f"Metadata-Version: 2.1\nName: liger-kernel\nVersion: {version}\n"
            "Requires-Dist: triton>=2.3.1\nRequires-Dist: torch>=2.1.2\n"
            'Requires-Dist: pytest; extra == "dev"\n\nOriginal description.\n',
        )
        archive.writestr(f"{prefix}/WHEEL", "Wheel-Version: 1.0\nRoot-Is-Purelib: true\nTag: py3-none-any\n")
        archive.writestr(f"{prefix}/RECORD", "old record")
        archive.writestr(f"{prefix}/licenses/LICENSE", "Upstream license")
        archive.writestr("liger_kernel/kernel.py", "# unchanged upstream code\n")
    return source


def test_adaptation_is_labelled_preserves_sources_and_has_valid_record(tmp_path):
    source = wheel_fixture(tmp_path)
    output = windows.adapt_wheel(source, tmp_path / "out", "triton-xpu", "3.7.2", "xpu")
    assert "+cyrene.xpu1" in output.name
    with zipfile.ZipFile(output) as archive:
        prefix = f"liger_kernel-{windows.LIGER_RELEASE}+cyrene.xpu1.dist-info"
        info = BytesParser().parsebytes(archive.read(f"{prefix}/METADATA"))
        assert info.get_all("Requires-Dist") == ["torch>=2.1.2", 'pytest; extra == "dev"', "triton-xpu==3.7.2"]
        assert archive.read("liger_kernel/kernel.py") == b"# unchanged upstream code\n"
        assert archive.read(f"{prefix}/licenses/LICENSE") == b"Upstream license"
        provenance = json.loads(archive.read(f"{prefix}/cyrene_backend.json"))
        assert provenance["sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()
        for name, digest, size in csv.reader(io.StringIO(archive.read(f"{prefix}/RECORD").decode())):
            if name.endswith("/RECORD"):
                continue
            content = archive.read(name)
            assert int(size) == len(content)
            assert (
                digest == "sha256=" + base64.urlsafe_b64encode(hashlib.sha256(content).digest()).rstrip(b"=").decode()
            )


def test_unreviewed_wheel_and_invalid_api_version_are_not_adapted(tmp_path):
    with pytest.raises(ValueError, match="Unreviewed"):
        windows.adapt_wheel(wheel_fixture(tmp_path, "0.9.0"), tmp_path / "out", "triton-xpu", "3.7.2", "xpu")
    with pytest.raises(ValueError, match="required API"):
        windows.adapt_wheel(wheel_fixture(tmp_path), tmp_path / "out", "triton-xpu", "2.0.0", "xpu")


def test_windows_provider_is_protected_by_constraints():
    result = bootstrap.hardware_constraints({"triton-windows": "3.7.0.post1", "torch": "2.13.0"})
    assert "triton-windows==3.7.0.post1" in result
    assert "triton===0" in result


def test_generic_liger_requirement_cannot_pull_linux_triton_on_windows():
    line = next(
        line
        for line in (Path(__file__).parents[1] / "requirements/liger-kernel.txt").read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    )
    requirement = Requirement(line)
    assert requirement.marker is not None
    assert not requirement.marker.evaluate({"platform_system": "Windows"})
    assert requirement.marker.evaluate({"platform_system": "Linux"})


def test_repeat_install_uses_provenance_and_actual_dependencies(monkeypatch):
    distribution = SimpleNamespace(
        version=f"{windows.LIGER_RELEASE}+cyrene.xpu1",
        requires=["torch>=2.1.2", "triton-xpu==3.7.2"],
        read_text=lambda _: json.dumps({"backend": "xpu", "provider": "triton-xpu", "provider_version": "3.7.2"}),
    )
    monkeypatch.setattr(windows.metadata, "distribution", lambda _: distribution)
    assert windows.installed_adapter_matches("xpu", "triton-xpu", "3.7.2")
    assert not windows.installed_adapter_matches("xpu", "triton-xpu", "3.8.0")
    distribution.requires.append("triton>=2.3.1")
    assert not windows.installed_adapter_matches("xpu", "triton-xpu", "3.7.2")


def test_newer_liger_is_not_silently_downgraded(monkeypatch):
    monkeypatch.setattr(windows.metadata, "distribution", lambda _: SimpleNamespace(version="0.10.0"))
    with pytest.raises(ValueError, match="instead of downgrading"):
        windows.installed_adapter_matches("xpu", "triton-xpu", "3.7.2")


@pytest.mark.parametrize("mode", ["auto", "required"])
def test_windows_failure_policy(monkeypatch, tmp_path, mode):
    monkeypatch.setenv("LLAMAFACTORY_LIGER", "auto")
    monkeypatch.setattr(bootstrap.platform, "system", lambda: "Windows")
    calls = []
    monkeypatch.setattr(bootstrap, "run", lambda command, **kwargs: calls.append(command) or False)
    if mode == "required":
        with pytest.raises(RuntimeError, match="Windows Liger"):
            bootstrap.install_liger(Path("python"), tmp_path / "constraints", mode, "xpu")
    else:
        bootstrap.install_liger(Path("python"), tmp_path / "constraints", mode, "xpu")
        assert bootstrap.os.environ["LLAMAFACTORY_LIGER"] == "off"
    assert "install_windows_liger.py" in calls[0][3]
