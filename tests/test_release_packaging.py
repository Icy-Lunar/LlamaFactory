import json
import stat
import zipfile
from pathlib import Path

from scripts import package_multibackend as packaging


def test_multibackend_release_directory_and_zip_include_primary_launchers(tmp_path, monkeypatch):
    source = tmp_path / "source"
    source.mkdir()
    (source / "start_windows.bat").write_text("@echo off\n", encoding="utf-8")
    (source / "start_linux.sh").write_bytes(b"#!/usr/bin/env bash\r\necho ready\r\n")
    (source / "module.py").write_text("VALUE = 1\n", encoding="utf-8")
    paths = [Path("module.py"), Path("start_linux.sh"), Path("start_windows.bat")]

    monkeypatch.setattr(packaging, "ROOT", source)
    monkeypatch.setattr(packaging, "release_files", lambda: paths)
    monkeypatch.setattr(packaging, "git_output", lambda *args: "" if args[0] == "status" else "abc123")

    destination = tmp_path / "release"
    count, digest = packaging.build_directory(destination)

    assert count == 3
    assert len(digest) == 64
    assert b"\r\n" not in (destination / "start_linux.sh").read_bytes()
    manifest = json.loads((destination / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["entrypoints"]["windows"] == "start_windows.bat"
    assert manifest["entrypoints"]["linux"] == "start_linux.sh"

    archive = tmp_path / "release.zip"
    archive_digest = packaging.build_zip(destination, archive)
    assert len(archive_digest) == 64
    with zipfile.ZipFile(archive) as bundle:
        assert "release/start_windows.bat" in bundle.namelist()
        linux_info = bundle.getinfo("release/start_linux.sh")
        assert stat.S_IMODE(linux_info.external_attr >> 16) == 0o755
