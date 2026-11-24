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

"""Localized results of optional acceleration checks."""

LIGER_LOCALES = {
    "en": {
        "pending": "Liger: pending training-process verification; VRAM estimate uses standard kernels.",
        "available": "Liger Kernel",
        "standard": "Standard training (Liger off)",
        "disabled": "Liger Kernel is disabled; standard training will be used.",
        "missing": "Liger Kernel is not installed; standard training will be used.",
        "version": "The installed Liger Kernel version is unsupported; standard training will be used.",
        "runtime": "Liger Kernel did not pass the device compatibility check; standard training will be used.",
        "model": "The local model has no verified Liger patch; standard training will be used.",
    },
    "zh": {
        "pending": "Liger：将在训练子进程中验证；显存暂按标准内核估算。",
        "available": "Liger Kernel",
        "standard": "标准训练（Liger 已关闭）",
        "disabled": "Liger Kernel 已关闭，将使用标准训练。",
        "missing": "未安装 Liger Kernel，将使用标准训练。",
        "version": "已安装的 Liger Kernel 版本不满足要求，将使用标准训练。",
        "runtime": "Liger Kernel 未通过当前设备的兼容性检查，将使用标准训练。",
        "model": "当前本地模型没有通过检查的 Liger 适配，将使用标准训练。",
    },
    "ru": {
        "pending": "Liger: проверка при запуске; оценка VRAM без ускорения.",
        "available": "Liger Kernel",
        "standard": "Стандартное обучение (Liger выключен)",
        "disabled": "Liger Kernel отключён; используется стандартное обучение.",
        "missing": "Liger Kernel не установлен; используется стандартное обучение.",
        "version": "Версия Liger Kernel не поддерживается; используется стандартное обучение.",
        "runtime": "Liger Kernel не прошёл проверку совместимости устройства; используется стандартное обучение.",
        "model": "Для локальной модели нет проверенной адаптации Liger; используется стандартное обучение.",
    },
    "ko": {
        "pending": "Liger: 학습 프로세스에서 검사 예정; VRAM은 표준 커널로 추정합니다.",
        "available": "Liger Kernel",
        "standard": "표준 학습 (Liger 꺼짐)",
        "disabled": "Liger Kernel이 꺼져 있어 표준 학습을 사용합니다.",
        "missing": "Liger Kernel이 설치되지 않아 표준 학습을 사용합니다.",
        "version": "설치된 Liger Kernel 버전이 지원되지 않아 표준 학습을 사용합니다.",
        "runtime": "Liger Kernel이 장치 호환성 검사를 통과하지 못해 표준 학습을 사용합니다.",
        "model": "로컬 모델에 검증된 Liger 패치가 없어 표준 학습을 사용합니다.",
    },
    "ja": {
        "pending": "Liger：学習プロセスで検証予定。VRAMは標準カーネルで推定します。",
        "available": "Liger Kernel",
        "standard": "標準学習（Liger 無効）",
        "disabled": "Liger Kernel が無効のため、標準学習を使用します。",
        "missing": "Liger Kernel が未インストールのため、標準学習を使用します。",
        "version": "Liger Kernel のバージョンが非対応のため、標準学習を使用します。",
        "runtime": "Liger Kernel がデバイス互換性チェックに失敗したため、標準学習を使用します。",
        "model": "ローカルモデルに検証済みの Liger パッチがないため、標準学習を使用します。",
    },
}
