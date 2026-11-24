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

"""Build a source deployment archive for Ubuntu from the current workspace."""

import argparse
import gzip
import hashlib
import io
import json
import stat
import subprocess
import tarfile
import zipfile
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_NAME = f"cyrene-llamafactory-ubuntu-{datetime.now(UTC).date():%Y%m%d}"
EXCLUDED_PARTS = {
    ".ai",
    ".claude",
    ".driver-cache",
    ".git",
    ".github",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    ".tmp-rocm-inspect",
    "__pycache__",
    "dist",
    "llamaboard_cache",
    "logs",
    "output",
    "outputs",
    "saves",
    "site",
    "tests",
    "tests_v1",
}


def git_output(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True, encoding="utf-8")
    return result.stdout.strip()


def release_files() -> list[Path]:
    output = subprocess.run(
        ["git", "ls-files", "-co", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout
    paths = []
    for raw_path in output.split(b"\0"):
        if not raw_path:
            continue
        relative = Path(raw_path.decode("utf-8"))
        posix = PurePosixPath(relative.as_posix())
        if any(part in EXCLUDED_PARTS for part in posix.parts):
            continue
        if relative.name.startswith(".env"):
            continue
        source = ROOT / relative
        if source.is_file():
            paths.append(relative)
    return sorted(set(paths), key=lambda path: path.as_posix())


def add_bytes(archive: tarfile.TarFile, name: str, content: bytes, mode: int = 0o644) -> None:
    info = tarfile.TarInfo(name)
    info.size = len(content)
    info.mode = mode
    info.mtime = 0
    archive.addfile(info, io.BytesIO(content))


def file_content(source: Path) -> bytes:
    content = source.read_bytes()
    return content.replace(b"\r\n", b"\n") if source.suffix == ".sh" else content


def release_manifest(root_name: str, paths: list[Path], entrypoint: str) -> bytes:
    manifest = {
        "name": root_name,
        "built_at_utc": datetime.now(UTC).isoformat(),
        "base_commit": git_output("rev-parse", "HEAD"),
        "contains_workspace_changes": bool(git_output("status", "--short")),
        "file_count": len(paths),
        "entrypoint": entrypoint,
        "python": ">=3.11",
    }
    return (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def add_zip_bytes(archive: zipfile.ZipFile, name: str, content: bytes, mode: int = 0o644) -> None:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.create_system = 3
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = (stat.S_IFREG | mode) << 16
    archive.writestr(info, content)


def build_archive(
    output: Path, root_name: str, archive_format: str = "tar.gz", entrypoint: str = "start_webui.sh"
) -> tuple[int, str]:
    paths = release_files()
    manifest = release_manifest(root_name, paths, entrypoint)

    output.parent.mkdir(parents=True, exist_ok=True)
    if archive_format == "zip":
        with zipfile.ZipFile(output, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for relative in paths:
                source = ROOT / relative
                mode = 0o755 if source.suffix == ".sh" else 0o644
                add_zip_bytes(archive, f"{root_name}/{relative.as_posix()}", file_content(source), mode)
            add_zip_bytes(archive, f"{root_name}/RELEASE_MANIFEST.json", manifest)
    else:
        with output.open("wb") as raw_archive:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw_archive, mtime=0) as compressed:
                with tarfile.open(fileobj=compressed, mode="w") as archive:
                    for relative in paths:
                        source = ROOT / relative
                        mode = 0o755 if source.suffix == ".sh" else 0o644
                        add_bytes(archive, f"{root_name}/{relative.as_posix()}", file_content(source), mode)
                    add_bytes(archive, f"{root_name}/RELEASE_MANIFEST.json", manifest)

    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    checksum = output.with_suffix(output.suffix + ".sha256")
    checksum.write_text(f"{digest}  {output.name}\n", encoding="utf-8", newline="\n")
    return len(paths), digest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", default=DEFAULT_NAME, help="Top-level directory and archive base name.")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    parser.add_argument("--format", choices=("tar.gz", "zip"), default="tar.gz")
    parser.add_argument("--entrypoint", default="start_webui.sh")
    args = parser.parse_args()
    output = args.output_dir.resolve() / f"{args.name}.{args.format}"
    count, digest = build_archive(output, args.name, args.format, args.entrypoint)
    print(f"Created {output} with {count} workspace files")
    print(f"SHA256 {digest}")


if __name__ == "__main__":
    main()
