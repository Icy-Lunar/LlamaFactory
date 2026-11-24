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

import json

import gradio as gr
import pytest

from llamafactory.webui.components.data import (
    PREVIEW_LIMIT,
    PreviewError,
    _load_data_file,
    can_preview,
    create_preview_box,
    get_preview,
    next_page,
    prev_page,
    preview_hint,
)
from llamafactory.webui.preview_locales import PREVIEW_LOCALES, PREVIEW_MESSAGES


def _catalog(tmp_path, entry=None):
    (tmp_path / "dataset_info.json").write_text(
        json.dumps({"sample": entry or {"file_name": "records.json"}}), encoding="utf-8"
    )


def test_preview_is_clickable_without_selection_and_explains_what_to_do(tmp_path):
    assert can_preview(str(tmp_path), None).interactive is True
    with pytest.raises(gr.Error, match=PREVIEW_MESSAGES["en"]["select_dataset"]):
        get_preview(str(tmp_path), None, 0)


@pytest.mark.parametrize("lang", ["en", "zh", "ru", "ko", "ja"])
def test_preview_failures_and_guidance_are_localized(tmp_path, lang):
    assert preview_hint(str(tmp_path), [], lang) == PREVIEW_MESSAGES[lang]["select_dataset"]
    with pytest.raises(gr.Error) as exc:
        get_preview("ONLINE", ["sample"], 0, lang)
    assert exc.value.message == PREVIEW_MESSAGES[lang]["local_only"]
    assert PREVIEW_LOCALES["preview_status"][lang]["value"]
    assert PREVIEW_LOCALES["preview_count"][lang]["label"]


@pytest.mark.parametrize(
    ("entry", "filename", "contents", "expected"),
    [
        ({"file_name": "missing.json"}, None, None, "missing_file"),
        ({"hf_hub_url": "remote/dataset"}, None, None, "local_only"),
        ({"file_name": "records.bad"}, "records.bad", "x", "unsupported_format"),
        ({"file_name": "records.json"}, "records.json", "[]", "empty_dataset"),
        ({"file_name": "records.json"}, "records.json", "not json", "invalid_data"),
    ],
)
def test_invalid_local_datasets_fail_with_actionable_message(tmp_path, entry, filename, contents, expected):
    _catalog(tmp_path, entry)
    if filename:
        (tmp_path / filename).write_text(contents, encoding="utf-8")
    with pytest.raises(gr.Error) as exc:
        get_preview(str(tmp_path), ["sample"], 0)
    assert exc.value.message == PREVIEW_MESSAGES["en"][expected]


def test_stale_and_invalid_catalog_are_reported(tmp_path):
    with pytest.raises(gr.Error) as exc:
        get_preview(str(tmp_path), ["sample"], 0)
    assert exc.value.message == PREVIEW_MESSAGES["en"]["invalid_catalog"]
    _catalog(tmp_path)
    with pytest.raises(gr.Error) as exc:
        get_preview(str(tmp_path), ["removed"], 0)
    assert exc.value.message == PREVIEW_MESSAGES["en"]["unknown_dataset"]


def test_missing_file_error_recovers_without_reload_or_reselecting(tmp_path):
    _catalog(tmp_path)
    with gr.Blocks() as demo:
        directory = gr.Textbox(str(tmp_path))
        dataset = gr.Dropdown(choices=["sample"], value=["sample"], multiselect=True)
        preview = create_preview_box(directory, dataset)
    callback = next(
        event for event in demo.fns.values() if (preview["data_preview_btn"]._id, "click") in event.targets
    )
    with pytest.raises(gr.Error):
        callback.fn(str(tmp_path), ["sample"], 0)
    (tmp_path / "records.json").write_text('[{"text":"recovered"}]', encoding="utf-8")
    assert callback.fn(str(tmp_path), ["sample"], 0)[1] == [{"text": "recovered"}]
    assert preview["data_preview_btn"].interactive is True


def test_json_preview_pages_and_clamps_to_last_page(tmp_path):
    _catalog(tmp_path)
    records = [{"instruction": str(index)} for index in range(5)]
    (tmp_path / "records.json").write_text(json.dumps(records), encoding="utf-8")
    count, samples, modal = get_preview(str(tmp_path), ["sample"], 0)
    assert count == 5
    assert samples == records[:2]
    assert modal.visible is True
    assert get_preview(str(tmp_path), ["sample"], 1)[1] == records[2:4]
    assert get_preview(str(tmp_path), ["sample"], 999)[1] == records[4:]
    assert prev_page(0) == 0
    assert next_page(2, 5) == 2


@pytest.mark.parametrize("suffix", ["json", "jsonl"])
def test_preview_does_not_read_whole_large_dataset(tmp_path, suffix):
    path = tmp_path / f"records.{suffix}"
    records = [{"instruction": str(index)} for index in range(PREVIEW_LIMIT + 1)]
    # A malformed tail proves preview does not parse the full file after the first 100 samples.
    prefix = (
        json.dumps(records)[:-1] + ",INVALID"
        if suffix == "json"
        else "\n".join(map(json.dumps, records)) + "\nINVALID"
    )
    path.write_text(prefix, encoding="utf-8")
    assert _load_data_file(str(path)) == records[:PREVIEW_LIMIT]


def test_preview_reading_budget_is_enforced(tmp_path, monkeypatch):
    monkeypatch.setattr("llamafactory.webui.components.data.MAX_PREVIEW_BYTES", 64)
    for suffix in ("json", "jsonl", "csv"):
        path = tmp_path / f"large.{suffix}"
        path.write_text('[{"text":"' + "x" * 256, encoding="utf-8")
        with pytest.raises(PreviewError, match="sample_too_large"):
            _load_data_file(str(path))


def test_directory_preview_is_sorted_and_ignores_subdirectories_and_unsupported_files(tmp_path):
    _catalog(tmp_path, {"file_name": "records"})
    records_dir = tmp_path / "records"
    records_dir.mkdir()
    (records_dir / "nested").mkdir()
    (records_dir / "b.jsonl").write_text('\n{"text":"second"}\n', encoding="utf-8")
    (records_dir / "a.jsonl").write_text('{"text":"first"}\n', encoding="utf-8-sig")
    (records_dir / "notes.md").write_text("Documentation", encoding="utf-8")
    assert get_preview(str(tmp_path), ["sample"], 0)[1] == [{"text": "first"}, {"text": "second"}]


def test_csv_and_text_preview_produce_records(tmp_path):
    csv_path = tmp_path / "records.csv"
    csv_path.write_text('instruction,output\n"line1\nline2",answer\n', encoding="utf-8", newline="\n")
    assert _load_data_file(str(csv_path)) == [{"instruction": "line1\nline2", "output": "answer"}]
    txt_path = tmp_path / "records.txt"
    txt_path.write_text("first\nsecond\n", encoding="utf-8")
    assert _load_data_file(str(txt_path)) == [{"text": "first"}, {"text": "second"}]


@pytest.mark.parametrize("file_format", ["parquet", "arrow", "arrow_stream"])
def test_binary_columnar_formats_are_read_as_bounded_records(tmp_path, file_format):
    import pyarrow as pa
    import pyarrow.parquet as pq

    table = pa.table({"instruction": [str(index) for index in range(PREVIEW_LIMIT + 20)]})
    path = tmp_path / ("records.parquet" if file_format == "parquet" else "records.arrow")
    if file_format == "parquet":
        pq.write_table(table, path)
    else:
        writer = pa.ipc.new_file if file_format == "arrow" else pa.ipc.new_stream
        with pa.OSFile(str(path), "wb") as sink, writer(sink, table.schema) as output:
            output.write_table(table)
    assert _load_data_file(str(path)) == table.slice(0, PREVIEW_LIMIT).to_pylist()


def test_actual_ui_callbacks_reset_on_directory_and_dataset_changes_and_use_language(tmp_path):
    _catalog(tmp_path)
    (tmp_path / "records.json").write_text('[{"instruction":"hello"}]', encoding="utf-8")
    with gr.Blocks() as demo:
        directory = gr.Textbox(str(tmp_path))
        dataset = gr.Dropdown(choices=["sample"], value=["sample"], multiselect=True)
        lang = gr.Dropdown(choices=["en", "zh"], value="zh")
        preview = create_preview_box(directory, dataset, lang)
    assert preview["data_preview_btn"].interactive is True
    callback = next(
        event for event in demo.fns.values() if (preview["data_preview_btn"]._id, "click") in event.targets
    )
    assert callback.inputs == [directory, dataset, preview["page_index"], lang]
    assert callback.fn(str(tmp_path), ["sample"], 0, "zh")[1] == [{"instruction": "hello"}]
    for component in (directory, dataset):
        reset = next(event for event in demo.fns.values() if (component._id, "change") in event.targets)
        assert reset.fn()[:3] == (0, 0, [])
        assert reset.fn()[3].visible is False
    language_event = next(event for event in demo.fns.values() if (lang._id, "change") in event.targets)
    assert language_event.fn(str(tmp_path), ["sample"], "zh") == PREVIEW_MESSAGES["zh"]["ready"].format(limit=100)
