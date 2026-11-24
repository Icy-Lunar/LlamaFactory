# Copyright 2025 the LlamaFactory team.
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

import csv
import json
import os
from itertools import islice
from typing import TYPE_CHECKING, Any

from ...extras.constants import DATA_CONFIG, FILEEXT2TYPE
from ...extras.packages import is_gradio_available
from ..preview_locales import PREVIEW_MESSAGES


if is_gradio_available():
    import gradio as gr


if TYPE_CHECKING:
    from gradio.components import Component


PAGE_SIZE = 2
PREVIEW_LIMIT = 100
MAX_PREVIEW_BYTES = 16 * 1024 * 1024


class PreviewError(ValueError):
    """A recoverable preview failure whose message is translated by the UI."""


def prev_page(page_index: int) -> int:
    return page_index - 1 if page_index > 0 else page_index


def next_page(page_index: int, total_num: int) -> int:
    return page_index + 1 if (page_index + 1) * PAGE_SIZE < total_num else page_index


def can_preview(dataset_dir: str, dataset: list) -> "gr.Button":
    r"""Keep the action available so invalid selections can receive useful feedback."""
    return gr.Button(interactive=True)


def _resolve_data_files(dataset_dir: str, dataset: list | None) -> list[str]:
    if not dataset:
        raise PreviewError("select_dataset")
    if not dataset_dir or dataset_dir == "ONLINE" or dataset_dir.startswith("REMOTE:"):
        raise PreviewError("local_only")
    try:
        with open(os.path.join(dataset_dir, DATA_CONFIG), encoding="utf-8-sig") as f:
            dataset_info = json.load(f)
    except (OSError, ValueError):
        raise PreviewError("invalid_catalog") from None

    selected = dataset[0] if isinstance(dataset, list) else dataset
    entry = dataset_info.get(selected) if isinstance(dataset_info, dict) else None
    if not isinstance(entry, dict):
        raise PreviewError("unknown_dataset")
    if (
        not isinstance(entry.get("file_name"), str)
        or not entry["file_name"]
        or any(key in entry for key in ("hf_hub_url", "ms_hub_url", "om_hub_url", "script_url", "cloud_file_name"))
    ):
        raise PreviewError("local_only")
    data_path = os.path.join(dataset_dir, entry["file_name"])
    if os.path.isfile(data_path):
        files = [data_path]
    elif os.path.isdir(data_path):
        files = [
            os.path.join(data_path, name)
            for name in sorted(os.listdir(data_path))
            if name != DATA_CONFIG and os.path.isfile(os.path.join(data_path, name))
        ]
    else:
        raise PreviewError("missing_file")

    supported = [path for path in files if os.path.splitext(path)[1].lower().lstrip(".") in FILEEXT2TYPE]
    if not supported:
        raise PreviewError("unsupported_format" if files else "empty_dataset")
    return supported


def _read_json_samples(file_path: str, limit: int) -> list[Any]:
    """Decode just the start of a JSON array, with a bound on bytes read."""
    decoder = json.JSONDecoder()
    samples = []
    with open(file_path, encoding="utf-8-sig") as f:
        buffer, consumed, eof = "", 0, False

        def refill() -> None:
            nonlocal buffer, consumed, eof
            chunk = f.read(min(65536, MAX_PREVIEW_BYTES - consumed))
            consumed += len(chunk)
            if not chunk:
                if consumed >= MAX_PREVIEW_BYTES:
                    raise PreviewError("sample_too_large")
                eof = True
            buffer += chunk

        def trim() -> None:
            nonlocal buffer
            buffer = buffer.lstrip()
            while not buffer and not eof:
                refill()
                buffer = buffer.lstrip()

        trim()
        array = buffer.startswith("[")
        if array:
            buffer = buffer[1:]
        while len(samples) < limit:
            trim()
            if array and buffer.startswith("]"):
                return samples
            if not buffer:
                raise PreviewError("invalid_data")
            while True:
                try:
                    value, end = decoder.raw_decode(buffer)
                    break
                except json.JSONDecodeError:
                    if eof:
                        raise PreviewError("invalid_data") from None
                    refill()
            samples.append(value)
            if not array:
                return samples
            buffer = buffer[end:]
            trim()
            if buffer.startswith("]"):
                return samples
            if not buffer.startswith(","):
                raise PreviewError("invalid_data")
            buffer = buffer[1:]
    return samples


def _load_data_file(file_path: str, limit: int = PREVIEW_LIMIT) -> list[Any]:
    """Read a bounded sample without materializing the complete dataset."""
    extension = os.path.splitext(file_path)[1].lower()
    if extension == ".json":
        return _read_json_samples(file_path, limit)
    if extension == ".parquet":
        import pyarrow.parquet as pq

        batch = next(pq.ParquetFile(file_path).iter_batches(batch_size=limit), None)
        return batch.to_pylist() if batch is not None else []
    if extension == ".arrow":
        import pyarrow as pa

        samples = []
        with pa.memory_map(file_path, "r") as source:
            try:
                reader = pa.ipc.open_file(source)
                batches = (reader.get_batch(index) for index in range(reader.num_record_batches))
            except pa.ArrowInvalid:
                source.seek(0)
                batches = pa.ipc.open_stream(source)
            for batch in batches:
                samples.extend(batch.slice(0, limit - len(samples)).to_pylist())
                if len(samples) >= limit:
                    break
        return samples
    with open(file_path, encoding="utf-8-sig", newline="") as f:

        def lines():
            consumed = 0
            while line := f.readline(MAX_PREVIEW_BYTES + 1):
                consumed += len(line)
                if consumed > MAX_PREVIEW_BYTES:
                    raise PreviewError("sample_too_large")
                yield line

        if extension == ".csv":
            return list(islice(csv.DictReader(lines()), limit))
        samples = []
        for line in lines():
            if not line.strip():
                continue
            samples.append(json.loads(line) if extension == ".jsonl" else {"text": line.rstrip("\r\n")})
            if len(samples) >= limit:
                break
        return samples


def preview_hint(dataset_dir: str, dataset: list | None, lang: str = "en") -> str:
    """Explain what the preview action will do, or what needs attention first."""
    messages = PREVIEW_MESSAGES.get(lang, PREVIEW_MESSAGES["en"])
    try:
        _resolve_data_files(dataset_dir, dataset)
        return messages["ready"].format(limit=PREVIEW_LIMIT)
    except PreviewError as err:
        return messages[str(err)]
    except (OSError, ValueError, TypeError):
        return messages["invalid_data"]


def get_preview(dataset_dir: str, dataset: list, page_index: int, lang: str = "en") -> tuple[int, list, "gr.Column"]:
    r"""Open a bounded local dataset preview, with actionable localized failures."""
    messages = PREVIEW_MESSAGES.get(lang, PREVIEW_MESSAGES["en"])
    try:
        files = _resolve_data_files(dataset_dir, dataset)
        data = []
        for file_path in files:
            data.extend(_load_data_file(file_path, PREVIEW_LIMIT - len(data)))
            if len(data) >= PREVIEW_LIMIT:
                break
        if not data:
            raise PreviewError("empty_dataset")
        page_index = max(0, min(int(page_index or 0), (len(data) - 1) // PAGE_SIZE))
    except PreviewError as err:
        raise gr.Error(messages[str(err)]) from None
    except (OSError, ValueError, TypeError, ImportError, csv.Error):
        raise gr.Error(messages["invalid_data"]) from None

    return len(data), data[PAGE_SIZE * page_index : PAGE_SIZE * (page_index + 1)], gr.Column(visible=True)


def create_preview_box(
    dataset_dir: "gr.Textbox", dataset: "gr.Dropdown", lang: "gr.Dropdown | None" = None
) -> dict[str, "Component"]:
    if lang is None:
        lang = gr.State("en")
    data_preview_btn = gr.Button(interactive=True, scale=1)
    with gr.Column(visible=False, elem_classes="modal-box") as preview_box:
        preview_status = gr.Markdown(PREVIEW_MESSAGES["en"]["select_dataset"], elem_classes="preview-status")
        with gr.Row():
            preview_count = gr.Number(value=0, interactive=False, precision=0)
            page_index = gr.Number(value=0, interactive=False, precision=0)

        with gr.Row():
            prev_btn = gr.Button()
            next_btn = gr.Button()
            close_btn = gr.Button()

        with gr.Row():
            preview_samples = gr.JSON()

    for component in (dataset, dataset_dir):
        component.change(
            lambda: (0, 0, [], gr.Column(visible=False)),
            outputs=[page_index, preview_count, preview_samples, preview_box],
            queue=False,
        ).then(preview_hint, [dataset_dir, dataset, lang], [preview_status], queue=False)
    lang.change(preview_hint, [dataset_dir, dataset, lang], [preview_status], queue=False)
    data_preview_btn.click(
        get_preview,
        [dataset_dir, dataset, page_index, lang],
        [preview_count, preview_samples, preview_box],
        queue=False,
    ).then(preview_hint, [dataset_dir, dataset, lang], [preview_status], queue=False)
    prev_btn.click(prev_page, [page_index], [page_index], queue=False).then(
        get_preview,
        [dataset_dir, dataset, page_index, lang],
        [preview_count, preview_samples, preview_box],
        queue=False,
    )
    next_btn.click(next_page, [page_index, preview_count], [page_index], queue=False).then(
        get_preview,
        [dataset_dir, dataset, page_index, lang],
        [preview_count, preview_samples, preview_box],
        queue=False,
    )
    close_btn.click(lambda: gr.Column(visible=False), outputs=[preview_box], queue=False)
    return dict(
        data_preview_btn=data_preview_btn,
        preview_status=preview_status,
        preview_count=preview_count,
        page_index=page_index,
        prev_btn=prev_btn,
        next_btn=next_btn,
        close_btn=close_btn,
        preview_samples=preview_samples,
    )
