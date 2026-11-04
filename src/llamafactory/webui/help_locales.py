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

"""Localized choices and practical field help for the guided training interface."""

HELP_LABELS = {
    "en": "Help: {label}",
    "ru": "Справка: {label}",
    "zh": "帮助：{label}",
    "ko": "도움말: {label}",
    "ja": "ヘルプ：{label}",
}

FINETUNING_LABELS = {
    "en": {
        "full": "Full fine-tuning (Full)",
        "freeze": "Selected-layer fine-tuning (Freeze)",
        "lora": "Low-rank adapters (LoRA)",
        "oft": "Orthogonal fine-tuning (OFT)",
    },
    "ru": {
        "full": "Полное дообучение (Full)",
        "freeze": "Дообучение выбранных слоёв (Freeze)",
        "lora": "Адаптеры низкого ранга (LoRA)",
        "oft": "Ортогональное дообучение (OFT)",
    },
    "zh": {
        "full": "全参数微调（Full）",
        "freeze": "部分层微调（Freeze）",
        "lora": "低秩适配器微调（LoRA）",
        "oft": "正交微调（OFT）",
    },
    "ko": {
        "full": "전체 파라미터 미세 조정 (Full)",
        "freeze": "선택한 계층 미세 조정 (Freeze)",
        "lora": "저랭크 어댑터 미세 조정 (LoRA)",
        "oft": "직교 미세 조정 (OFT)",
    },
    "ja": {
        "full": "全パラメータの微調整（Full）",
        "freeze": "選択した層の微調整（Freeze）",
        "lora": "低ランクアダプターの微調整（LoRA）",
        "oft": "直交微調整（OFT）",
    },
}

QUANTIZATION_LABELS = {
    "en": [("No quantization", "none"), ("8-bit", "8"), ("4-bit", "4")],
    "ru": [("Без квантования", "none"), ("8 бит", "8"), ("4 бита", "4")],
    "zh": [("不量化", "none"), ("8 位量化", "8"), ("4 位量化", "4")],
    "ko": [("양자화 안 함", "none"), ("8비트", "8"), ("4비트", "4")],
    "ja": [("量子化なし", "none"), ("8 ビット", "8"), ("4 ビット", "4")],
}

FIELD_HELP = {
    "lang": {
        "en": "Choose the interface language. Changing it keeps your current training settings.",
        "ru": "Выберите язык интерфейса. При смене языка текущие настройки обучения сохраняются.",
        "zh": "选择界面显示语言。切换语言会保留当前训练设置。",
        "ko": "인터페이스 언어를 선택하세요. 언어를 바꿔도 현재 학습 설정은 유지됩니다.",
        "ja": "画面の表示言語を選びます。言語を切り替えても現在の学習設定は保持されます。",
    },
    "finetuning_type": {
        "en": (
            "LoRA trains small adapters and is a useful starting point with limited VRAM. "
            "Full updates all unfrozen parameters and needs much more memory. Freeze updates selected layers. "
            "OFT learns orthogonal weight transformations. Model compatibility and memory use vary by method."
        ),
        "ru": (
            "LoRA обучает небольшие адаптеры и подходит для начала при ограниченной видеопамяти. "
            "Full обновляет все незамороженные параметры и требует значительно больше памяти. "
            "Freeze обучает выбранные слои. OFT обучает ортогональные преобразования весов. "
            "Совместимость с моделью и расход памяти зависят от метода."
        ),
        "zh": (
            "LoRA 训练少量适配器参数，适合显存有限时起步。Full 更新所有未冻结参数，显存需求通常明显更高。"
            "Freeze 只更新指定层；OFT 学习权重的正交变换。不同方法的模型兼容性与显存需求不同。"
        ),
        "ko": (
            "LoRA는 작은 어댑터를 학습하므로 GPU 메모리가 부족할 때 시작하기 좋습니다. "
            "Full은 동결되지 않은 모든 파라미터를 갱신하여 메모리가 훨씬 많이 필요합니다. "
            "Freeze는 선택한 계층을, OFT는 가중치의 직교 변환을 학습합니다. "
            "모델 호환성과 메모리 사용량은 방법에 따라 다릅니다."
        ),
        "ja": (
            "LoRA は少量のアダプターパラメータを学習するため、GPU メモリが限られる場合の出発点に適しています。"
            "Full は凍結されていない全パラメータを更新し、より多くのメモリを必要とします。"
            "Freeze は選択した層を、OFT は重みの直交変換を学習します。モデルとの互換性とメモリ使用量は方式によって異なります。"
        ),
    },
    "checkpoint_path": {
        "en": (
            "For a new training run, leave this empty. To continue from saved weights, select a checkpoint "
            "that matches the base model and fine-tuning method. In the merge workspace, select the adapter to merge."
        ),
        "ru": (
            "Для нового обучения оставьте поле пустым. Чтобы продолжить с сохранённых весов, выберите "
            "контрольную точку для той же базовой модели и метода дообучения. В разделе слияния выберите адаптер для слияния."
        ),
        "zh": (
            "从基础模型开始新训练时留空；从已有权重继续微调时，选择与基础模型和微调方法匹配的检查点。"
            "在适配器合并页中，这里用于选择要合并的适配器。"
        ),
        "ko": (
            "새 학습은 비워 두세요. 저장한 가중치에서 계속하려면 기본 모델과 미세 조정 방법이 일치하는 "
            "체크포인트를 선택하세요. 병합 화면에서는 병합할 어댑터를 선택합니다."
        ),
        "ja": (
            "新規学習では空欄にします。保存済みの重みから続ける場合は、ベースモデルと微調整方式に合う"
            "チェックポイントを選びます。マージ画面では、統合するアダプターを選んでください。"
        ),
    },
    "dataset": {
        "en": (
            "Select one or more datasets registered in the data directory. Options follow the training goal. "
            "Preview a few samples to check that the input, answer, or preference fields are correct."
        ),
        "ru": (
            "Выберите один или несколько наборов, зарегистрированных в каталоге данных. Список зависит от цели обучения. "
            "Просмотрите несколько примеров и проверьте поля входных данных, ответов или предпочтений."
        ),
        "zh": "选择数据目录中已登记的一个或多个数据集，列表会按训练目标筛选。先预览几条样本，检查输入、回答或偏好字段是否正确。",
        "ko": (
            "데이터 디렉터리에 등록된 데이터셋을 하나 이상 선택하세요. 목록은 학습 목표에 따라 달라집니다. "
            "몇 개의 샘플을 미리 보고 입력, 답변 또는 선호도 필드가 올바른지 확인하세요."
        ),
        "ja": (
            "データディレクトリに登録されたデータセットを 1 つ以上選びます。候補は学習目的に応じて変わります。"
            "数件をプレビューし、入力・回答・選好のフィールドが正しいか確認してください。"
        ),
    },
    "compute_type": {
        "en": (
            "Prefer BF16 when the GPU supports it. FP16 is another mixed-precision option; FP32 uses more memory. "
            "Pure BF16 also stores trainable weights in BF16 and is an advanced choice. Keep the detected recommendation if unsure."
        ),
        "ru": (
            "Используйте BF16, если GPU его поддерживает. FP16 — другой вариант смешанной точности; FP32 требует больше памяти. "
            "Pure BF16 также хранит обучаемые веса в BF16 и предназначен для опытных пользователей. "
            "Если сомневаетесь, оставьте предложенное значение."
        ),
        "zh": (
            "显卡支持时优先考虑 BF16；FP16 也是混合精度选项，FP32 通常占用更多显存。"
            "Pure BF16 还会用 BF16 保存可训练权重，属于进阶选项。不确定时保留检测后的推荐值。"
        ),
        "ko": (
            "GPU가 지원하면 BF16을 우선 고려하세요. FP16도 혼합 정밀도 옵션이며 FP32는 메모리를 더 사용합니다. "
            "Pure BF16은 학습할 가중치도 BF16으로 저장하는 고급 옵션입니다. 확실하지 않으면 감지된 권장값을 유지하세요."
        ),
        "ja": (
            "GPU が対応していれば BF16 を優先します。FP16 も混合精度の選択肢で、FP32 はより多くのメモリを使います。"
            "Pure BF16 は学習対象の重みも BF16 で保持する上級者向けの設定です。迷った場合は検出後の推奨値を使用してください。"
        ),
    },
    "lr_scheduler_type": {
        "en": (
            "Controls how the learning rate changes during training. Cosine lowers it gradually along a curve; "
            "linear lowers it at a steady rate. Start with cosine unless your training recipe requires another schedule."
        ),
        "ru": (
            "Определяет изменение скорости обучения. Cosine плавно снижает её по кривой, linear — с постоянным темпом. "
            "Начните с cosine, если ваш рецепт обучения не требует другого расписания."
        ),
        "zh": "控制学习率随训练进度如何变化。cosine 按余弦曲线逐渐降低，linear 线性降低。没有特定训练方案时，可先使用 cosine。",
        "ko": (
            "학습 중 학습률이 변하는 방식을 정합니다. cosine은 곡선을 따라 서서히, linear는 일정한 비율로 낮춥니다. "
            "특정 학습 방식에서 다른 설정을 요구하지 않으면 cosine으로 시작하세요."
        ),
        "ja": (
            "学習の進行に伴う学習率の変化を指定します。cosine は曲線に沿って、linear は一定の割合で下げます。"
            "特定の学習手順で指定がなければ、cosine から始めてください。"
        ),
    },
    "train_seed": {
        "en": (
            "Keep the same integer, such as 42, when comparing runs to reduce differences from random sampling. "
            "Identical seeds do not guarantee identical results across hardware or software versions."
        ),
        "ru": (
            "При сравнении запусков используйте одно целое число, например 42, чтобы уменьшить влияние случайной выборки. "
            "Одинаковый seed не гарантирует одинаковый результат на другом оборудовании или версии ПО."
        ),
        "zh": "比较多次实验时，保持同一个整数（例如 42），可减少随机采样带来的差异。同一种子不保证不同硬件或软件版本产生完全相同的结果。",
        "ko": (
            "실험을 비교할 때 42처럼 같은 정수를 사용하면 무작위 샘플링에 따른 차이를 줄일 수 있습니다. "
            "같은 시드라도 하드웨어나 소프트웨어 버전이 다르면 결과가 완전히 같지는 않을 수 있습니다."
        ),
        "ja": (
            "実験を比較するときは 42 など同じ整数を使うと、ランダムなサンプリングによる差を減らせます。"
            "同じシードでも、ハードウェアやソフトウェアのバージョンが異なると結果が一致するとは限りません。"
        ),
    },
    "max_grad_norm": {
        "en": (
            "Limits unusually large gradients before an update. A value of 1.0 is a common starting point. "
            "Smaller values clip more strongly; 0 disables gradient clipping."
        ),
        "ru": (
            "Ограничивает слишком большие градиенты перед обновлением. Обычно начинают с 1.0. "
            "Меньшее значение сильнее ограничивает градиенты; 0 отключает ограничение."
        ),
        "zh": "在更新参数前限制过大的梯度，通常可从 1.0 开始。数值越小，裁剪越强；设为 0 会关闭梯度裁剪。",
        "ko": (
            "파라미터를 갱신하기 전에 지나치게 큰 그래디언트를 제한합니다. 보통 1.0으로 시작합니다. "
            "작을수록 더 강하게 제한하며, 0은 그래디언트 클리핑을 끕니다."
        ),
        "ja": "更新前に大きすぎる勾配を制限します。通常は 1.0 から始めます。小さい値ほど強く制限し、0 にすると勾配クリッピングを無効にします。",
    },
    "model_path": {
        "en": (
            "Enter an existing local folder containing config.json, model weights and tokenizer files. "
            "The interface reads this folder to identify the model and estimate memory; it does not download models."
        ),
        "ru": (
            "Укажите существующую локальную папку с config.json, весами модели и файлами токенизатора. "
            "Интерфейс читает её для определения модели и оценки памяти; модели не скачиваются."
        ),
        "zh": "填写已有的本地文件夹，其中应包含 config.json、模型权重和分词器文件。界面会读取该目录识别模型并估算显存，不会下载模型。",
        "ko": (
            "config.json, 모델 가중치 및 토크나이저 파일이 있는 기존 로컬 폴더를 입력하세요. "
            "이 폴더를 읽어 모델을 식별하고 메모리를 추정하며, 모델을 다운로드하지 않습니다."
        ),
        "ja": (
            "config.json、モデルの重み、トークナイザーファイルがある既存のローカルフォルダーを指定します。"
            "このフォルダーからモデルを識別しメモリ使用量を推定します。モデルのダウンロードは行いません。"
        ),
    },
    "quantization_bit": {
        "en": (
            "No quantization keeps the normal weight precision. 8-bit or 4-bit lowers base-model memory use for compatible "
            "adapter methods, with possible quality or speed tradeoffs. Full and Freeze disable this setting. "
            "The VRAM estimate updates, but does not guarantee that training will fit."
        ),
        "ru": (
            "Без квантования сохраняется обычная точность весов. 8 или 4 бита уменьшают память базовой модели для совместимых "
            "адаптерных методов, но могут влиять на качество и скорость. Для Full и Freeze квантование отключено. "
            "Оценка видеопамяти обновляется, но не гарантирует, что памяти хватит."
        ),
        "zh": (
            "不量化会保留正常权重精度。8 位或 4 位可降低兼容适配器微调方式的基础模型显存占用，但可能影响质量或速度。"
            "Full 和 Freeze 禁用此项。显存估算会随之更新，但不保证实际训练一定能容纳。"
        ),
        "ko": (
            "양자화하지 않으면 일반적인 가중치 정밀도를 유지합니다. 8비트 또는 4비트는 호환되는 어댑터 학습에서 "
            "기본 모델의 메모리를 줄이지만 품질이나 속도에 영향을 줄 수 있습니다. Full과 Freeze에서는 비활성화됩니다. "
            "GPU 메모리 추정값이 갱신되지만 실제 학습에 메모리가 충분하다는 보장은 아닙니다."
        ),
        "ja": (
            "量子化なしでは通常の重み精度を保持します。8 ビットや 4 ビットは対応するアダプター学習でベースモデルの"
            "メモリを削減しますが、品質や速度に影響する場合があります。Full と Freeze では無効です。"
            "GPU メモリの推定値は更新されますが、実際の学習に収まる保証ではありません。"
        ),
    },
    "quantization_method": {
        "en": (
            "This interface uses bitsandbytes (bnb) for 8-bit and 4-bit training quantization. "
            "The backend is fixed; only the bit depth is selectable. It has no effect when quantization is off."
        ),
        "ru": (
            "Интерфейс использует bitsandbytes (bnb) для 8- и 4-битного квантования при обучении. "
            "Бэкенд фиксирован: выбирается только разрядность. При отключённом квантовании не влияет на обучение."
        ),
        "zh": "本界面固定使用 bitsandbytes（bnb）进行 8 位或 4 位训练量化，只需选择量化位数；关闭量化时，此设置不生效。",
        "ko": (
            "이 화면은 8비트 및 4비트 학습 양자화에 bitsandbytes (bnb)를 사용합니다. "
            "백엔드는 고정되어 비트 수만 선택할 수 있습니다. 양자화가 꺼져 있으면 적용되지 않습니다."
        ),
        "ja": (
            "この画面は学習時の 8 ビット・4 ビット量子化に bitsandbytes（bnb）を使用します。"
            "バックエンドは固定で、ビット数のみ選択できます。量子化が無効な場合は適用されません。"
        ),
    },
    "booster": {
        "en": (
            "Training acceleration is fixed to Liger Kernel. It uses supported GPU kernels to reduce some memory use "
            "and computation; results depend on the model and environment. Other acceleration backends are not selectable here."
        ),
        "ru": (
            "Для ускорения обучения выбран Liger Kernel. Поддерживаемые GPU-ядра уменьшают часть затрат памяти "
            "и вычислений; результат зависит от модели и окружения. Другие бэкенды ускорения здесь недоступны."
        ),
        "zh": "训练加速固定为 Liger Kernel。它通过受支持的 GPU 算子减少部分显存和计算开销，具体效果取决于模型和运行环境；此处不提供其他加速后端。",
        "ko": (
            "학습 가속은 Liger Kernel로 고정됩니다. 지원되는 GPU 커널로 일부 메모리와 연산 부담을 줄이며, "
            "효과는 모델과 실행 환경에 따라 다릅니다. 다른 가속 백엔드는 이 화면에서 선택할 수 없습니다."
        ),
        "ja": (
            "学習の高速化は Liger Kernel に固定されています。対応する GPU カーネルで一部のメモリや計算負荷を削減しますが、"
            "効果はモデルと実行環境によって異なります。この画面では他の高速化バックエンドは選択できません。"
        ),
    },
    "preview_count": {
        "en": "Shows the number of samples available in this preview; it does not change how many samples are used for training.",
        "ru": "Число доступных для просмотра примеров. Оно не меняет количество примеров, используемых при обучении.",
        "zh": "显示当前可预览的样本数量，不会改变实际用于训练的样本数。",
        "ko": "미리 볼 수 있는 샘플 수입니다. 실제 학습에 사용할 샘플 수는 바뀌지 않습니다.",
        "ja": "プレビューできるサンプル数を表示します。実際の学習に使うサンプル数は変更しません。",
    },
    "page_index": {
        "en": "Use the previous and next buttons to inspect other sample pages. Preview navigation does not change the dataset.",
        "ru": "Кнопками «Предыдущая» и «Следующая» просмотрите другие страницы примеров. Просмотр не изменяет набор данных.",
        "zh": "使用上一页和下一页按钮查看其他样本页；翻页只影响预览，不会修改数据集。",
        "ko": "이전 및 다음 버튼으로 다른 샘플 페이지를 확인하세요. 페이지 이동은 데이터셋을 수정하지 않습니다.",
        "ja": "前へ・次へボタンで他のサンプルページを確認できます。ページを移動してもデータセットは変更されません。",
    },
    "swanlab_project": {
        "en": (
            "When SwanLab tracking is enabled, runs with this project name are grouped together. "
            "Use the same name for experiments you want to compare; it does not set the local output directory."
        ),
        "ru": (
            "При включённом отслеживании SwanLab запуски с этим именем проекта объединяются в одну группу. "
            "Для сравниваемых экспериментов используйте одно имя. Оно не задаёт локальный каталог результатов."
        ),
        "zh": "启用 SwanLab 记录时，同一项目名下的实验会归为一组。需要相互比较的实验可使用同一名称；此项不决定本地输出目录。",
        "ko": (
            "SwanLab 기록이 활성화되면 같은 프로젝트 이름을 가진 실행이 한 그룹으로 모입니다. "
            "비교할 실험에는 같은 이름을 사용하세요. 로컬 출력 디렉터리를 지정하는 설정은 아닙니다."
        ),
        "ja": (
            "SwanLab の記録が有効な場合、同じプロジェクト名の実験がまとめられます。比較したい実験には同じ名前を使ってください。"
            "この設定でローカルの出力先は変わりません。"
        ),
    },
    "swanlab_run_name": {
        "en": (
            "Give this experiment a recognizable name in SwanLab, such as a model name and learning rate. "
            "This name is used only when SwanLab tracking is enabled and does not change the training parameters."
        ),
        "ru": (
            "Задайте понятное имя эксперимента в SwanLab, например модель и скорость обучения. "
            "Имя используется только при включённом отслеживании SwanLab и не меняет параметры обучения."
        ),
        "zh": "为本次 SwanLab 实验填写便于识别的名称，例如模型名和学习率。此名称仅在启用 SwanLab 记录时使用，不会改变训练参数。",
        "ko": (
            "모델 이름과 학습률처럼 SwanLab에서 알아보기 쉬운 실험 이름을 입력하세요. "
            "SwanLab 기록이 활성화된 경우에만 사용되며 학습 파라미터에는 영향을 주지 않습니다."
        ),
        "ja": (
            "モデル名と学習率など、SwanLab で見分けやすい実験名を付けます。"
            "SwanLab の記録が有効な場合にのみ使用され、学習パラメータは変わりません。"
        ),
    },
}
