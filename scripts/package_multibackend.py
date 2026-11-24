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

"""Create a clean multi-backend deployment directory and optional ZIP archive."""

import argparse
import hashlib
import json
import stat
import zipfile
from datetime import UTC, datetime
from pathlib import Path


try:
    from .package_ubuntu import ROOT, file_content, git_output, release_files
except ImportError:  # Direct script execution.
    from package_ubuntu import ROOT, file_content, git_output, release_files


DEFAULT_NAME = f"cyrene-llamafactory-multibackend-{datetime.now(UTC).date():%Y%m%d}"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_directory(destination: Path) -> tuple[int, str]:
    if destination.exists():
        raise FileExistsError(f"Destination already exists: {destination}")
    paths = release_files()
    destination.mkdir(parents=True)
    digest = hashlib.sha256()
    for relative in paths:
        source = ROOT / relative
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        content = file_content(source)
        target.write_bytes(content)
        if target.suffix == ".sh":
            target.chmod(target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        digest.update(relative.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(content)
    manifest = {
        "name": destination.name,
        "built_at_utc": datetime.now(UTC).isoformat(),
        "base_commit": git_output("rev-parse", "HEAD"),
        "contains_workspace_changes": bool(git_output("status", "--short")),
        "file_count": len(paths),
        "entrypoints": {
            "windows": "start_windows.bat",
            "linux": "start_linux.sh",
            "windows_double_click": "start_multibackend.cmd",
            "windows_wizard": "start_wizard.ps1",
            "linux_wizard": "start_wizard.sh",
            "windows_advanced": "start_multibackend.ps1",
            "linux_advanced": "start_multibackend.sh",
        },
        "backends": ["cuda", "xpu", "rocm"],
    }
    manifest_bytes = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    (destination / "RELEASE_MANIFEST.json").write_bytes(manifest_bytes)
    digest.update(manifest_bytes)
    return len(paths), digest.hexdigest()


def build_zip(source: Path, output: Path) -> str:
    with zipfile.ZipFile(output, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(source.rglob("*"), key=lambda item: item.relative_to(source).as_posix()):
            if not path.is_file():
                continue
            relative = path.relative_to(source)
            name = f"{source.name}/{relative.as_posix()}"
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            mode = 0o755 if path.suffix == ".sh" else 0o644
            info.external_attr = (stat.S_IFREG | mode) << 16
            archive.writestr(info, path.read_bytes())
    return sha256_file(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", default=DEFAULT_NAME)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    parser.add_argument("--archive", choices=("none", "zip"), default="zip")
    args = parser.parse_args()
    destination = args.output_dir.resolve() / args.name
    count, digest = build_directory(destination)
    checksum = destination.with_suffix(".sha256")
    checksum.write_text(f"{digest}  {destination.name}\n", encoding="utf-8", newline="\n")
    print(f"Created {destination} with {count} workspace files")
    print(f"CONTENT-SHA256 {digest}")
    if args.archive == "zip":
        archive = destination.with_suffix(".zip")
        archive_digest = build_zip(destination, archive)
        archive_checksum = archive.with_suffix(archive.suffix + ".sha256")
        archive_checksum.write_text(f"{archive_digest}  {archive.name}\n", encoding="utf-8", newline="\n")
        print(f"Created {archive}")
        print(f"ARCHIVE-SHA256 {archive_digest}")


if __name__ == "__main__":
    main()
