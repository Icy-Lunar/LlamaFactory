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

"""Translations for the guided local dataset preview."""

PREVIEW_MESSAGES = {
    "en": {
        "select_dataset": "Select a dataset, then click Preview dataset to inspect its original records.",
        "local_only": "Preview reads local files only. Select a dataset with file_name in dataset_info.json.",
        "invalid_catalog": "Cannot read dataset_info.json. Check the dataset directory and that the file contains valid JSON.",
        "unknown_dataset": "This selection is not registered in dataset_info.json. Refresh the dataset list and select it again.",
        "missing_file": "The selected dataset file is missing. Check its file_name and dataset directory.",
        "unsupported_format": "Preview supports local JSON, JSONL, CSV, Parquet, Arrow and TXT files.",
        "empty_dataset": "No records were found. Check that the selected file or directory contains dataset records.",
        "invalid_data": "Could not read the dataset. Check the file format, UTF-8 encoding and read permissions.",
        "sample_too_large": "The first records exceed the preview reading limit. Use smaller records or a smaller local sample file.",
        "ready": "Preview shows up to {limit} records from the first selected dataset, two per page. It does not load the full dataset or change training data.",
    },
    "zh": {
        "select_dataset": "选择数据集后，点击“预览数据集”即可查看原始样本。",
        "local_only": "预览仅读取本地文件。请在 dataset_info.json 中选择配置了 file_name 的数据集。",
        "invalid_catalog": "无法读取 dataset_info.json。请检查数据集目录，并确认该文件是有效的 JSON。",
        "unknown_dataset": "所选数据集未在 dataset_info.json 中注册。请刷新数据集列表后重新选择。",
        "missing_file": "找不到所选数据集文件。请检查 file_name 和数据集目录。",
        "unsupported_format": "预览支持本地 JSON、JSONL、CSV、Parquet、Arrow 和 TXT 文件。",
        "empty_dataset": "未找到样本。请确认所选文件或目录中包含数据记录。",
        "invalid_data": "无法读取数据集。请检查文件格式、UTF-8 编码和读取权限。",
        "sample_too_large": "前面的样本超过预览读取上限。请缩小单条样本，或使用较小的本地样本文件。",
        "ready": "预览第一个所选数据集的前 {limit} 条以内样本，每页两条；不会加载整个数据集，也不会更改训练数据。",
    },
    "ru": {
        "select_dataset": "Выберите набор данных и нажмите «Просмотреть набор данных», чтобы увидеть исходные записи.",
        "local_only": "Предпросмотр читает только локальные файлы. Выберите набор с file_name в dataset_info.json.",
        "invalid_catalog": "Не удалось прочитать dataset_info.json. Проверьте каталог и корректность JSON.",
        "unknown_dataset": "Этот набор не зарегистрирован в dataset_info.json. Обновите список и выберите его снова.",
        "missing_file": "Файл выбранного набора не найден. Проверьте file_name и каталог данных.",
        "unsupported_format": "Поддерживаются локальные файлы JSON, JSONL, CSV, Parquet, Arrow и TXT.",
        "empty_dataset": "Записи не найдены. Проверьте, что выбранный файл или каталог содержит данные.",
        "invalid_data": "Не удалось прочитать данные. Проверьте формат, кодировку UTF-8 и права чтения.",
        "sample_too_large": "Первые записи превышают лимит чтения. Используйте меньшие записи или небольшой локальный пример.",
        "ready": "Показываются до {limit} записей первого выбранного набора, по две на странице. Полный набор не загружается; обучающие данные не меняются.",
    },
    "ko": {
        "select_dataset": "데이터셋을 선택한 후 미리보기를 클릭하여 원본 샘플을 확인하세요.",
        "local_only": "미리보기는 로컬 파일만 읽습니다. dataset_info.json에 file_name이 있는 데이터셋을 선택하세요.",
        "invalid_catalog": "dataset_info.json을 읽을 수 없습니다. 데이터셋 폴더와 JSON 형식을 확인하세요.",
        "unknown_dataset": "선택한 데이터셋이 dataset_info.json에 없습니다. 목록을 새로 고친 후 다시 선택하세요.",
        "missing_file": "선택한 데이터셋 파일이 없습니다. file_name과 데이터셋 폴더를 확인하세요.",
        "unsupported_format": "로컬 JSON, JSONL, CSV, Parquet, Arrow 및 TXT 파일을 지원합니다.",
        "empty_dataset": "샘플이 없습니다. 선택한 파일이나 폴더에 데이터가 있는지 확인하세요.",
        "invalid_data": "데이터셋을 읽을 수 없습니다. 파일 형식, UTF-8 인코딩 및 읽기 권한을 확인하세요.",
        "sample_too_large": "앞부분의 샘플이 미리보기 읽기 제한을 초과합니다. 더 작은 샘플이나 로컬 예제 파일을 사용하세요.",
        "ready": "첫 번째 선택 데이터셋의 최대 {limit}개 샘플을 페이지당 두 개씩 표시합니다. 전체 데이터셋을 로드하거나 학습 데이터를 변경하지 않습니다.",
    },
    "ja": {
        "select_dataset": "データセットを選び、プレビューをクリックすると元のレコードを確認できます。",
        "local_only": "プレビューはローカルファイルのみを読み込みます。dataset_info.json で file_name が指定されたデータセットを選択してください。",
        "invalid_catalog": "dataset_info.json を読み込めません。データセットのフォルダーと JSON の形式を確認してください。",
        "unknown_dataset": "選択したデータセットは dataset_info.json に登録されていません。一覧を更新して選び直してください。",
        "missing_file": "選択したデータセットファイルがありません。file_name とフォルダーを確認してください。",
        "unsupported_format": "ローカルの JSON、JSONL、CSV、Parquet、Arrow、TXT ファイルに対応しています。",
        "empty_dataset": "レコードが見つかりません。選択したファイルまたはフォルダーにデータがあるか確認してください。",
        "invalid_data": "データセットを読み込めません。ファイル形式、UTF-8 エンコード、読み取り権限を確認してください。",
        "sample_too_large": "先頭のレコードがプレビューの読み取り上限を超えています。小さいレコードまたは小さいローカルサンプルを使用してください。",
        "ready": "最初に選択したデータセットの最大 {limit} 件を 1 ページ 2 件ずつ表示します。全データの読み込みや学習データの変更は行いません。",
    },
}

PREVIEW_LOCALES = {
    "preview_status": {lang: {"value": text["select_dataset"]} for lang, text in PREVIEW_MESSAGES.items()},
    "preview_count": {
        "en": {"label": "Preview samples (up to 100)"},
        "zh": {"label": "预览样本数（最多 100 条）"},
        "ru": {"label": "Записи предпросмотра (до 100)"},
        "ko": {"label": "미리보기 샘플 수 (최대 100개)"},
        "ja": {"label": "プレビュー件数（最大 100 件）"},
    },
}
