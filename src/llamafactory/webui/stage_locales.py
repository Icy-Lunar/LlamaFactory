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

"""Localized stage guidance and training-validation controls for the guided WebUI."""

LANGUAGES = ("en", "zh", "ru", "ko", "ja")

GOAL_STAGES = {
    "instruction": "Supervised Fine-Tuning",
    "preference": "DPO",
    "pretrain": "Pre-Training",
    "reward": "Reward Modeling",
    "ppo": "PPO",
    "kto": "KTO",
}

_GOAL_LABELS = {
    "en": (
        "Follow instructions · SFT",
        "Compare preferred answers · DPO",
        "Continue pre-training · PT",
        "Learn reward scores · RM",
        "Optimize with rewards · PPO",
        "Learn from feedback · KTO",
    ),
    "zh": (
        "学习指令回答 · SFT",
        "比较偏好回答 · DPO",
        "继续预训练 · PT",
        "学习奖励评分 · RM",
        "使用奖励优化 · PPO",
        "学习正负反馈 · KTO",
    ),
    "ru": (
        "Следовать инструкциям · SFT",
        "Сравнивать ответы · DPO",
        "Продолжить предобучение · PT",
        "Обучить оценку награды · RM",
        "Оптимизировать по награде · PPO",
        "Учиться на отзывах · KTO",
    ),
    "ko": (
        "지시 응답 학습 · SFT",
        "선호 응답 비교 · DPO",
        "사전 학습 계속 · PT",
        "보상 점수 학습 · RM",
        "보상으로 최적화 · PPO",
        "긍정·부정 피드백 학습 · KTO",
    ),
    "ja": (
        "指示への応答を学習 · SFT",
        "好ましい回答を比較 · DPO",
        "事前学習を継続 · PT",
        "報酬スコアを学習 · RM",
        "報酬で最適化 · PPO",
        "正負の評価から学習 · KTO",
    ),
}
STAGE_GOAL_CHOICES = {lang: list(zip(labels, GOAL_STAGES, strict=True)) for lang, labels in _GOAL_LABELS.items()}

STAGE_GUIDES = {
    "en": {
        "sft": "**SFT · learn from example answers.** By default only assistant responses contribute to loss. Adjust prompt/history masking only when your data needs it; leave noise at 0 for a first run.",
        "pt": "**PT · continue next-token pre-training.** Packing combines short texts to use sequence space efficiently. Resize the vocabulary only after adding tokens to the local tokenizer.",
        "dpo": "**DPO · learn from chosen/rejected answer pairs.** Start with sigmoid loss, beta 0.1 and SFT weight 0. Other losses reveal only their relevant settings.",
        "kto": "**KTO · learn from individual positive/negative feedback.** Use datasets with desirability labels, not DPO answer pairs. Start with equal chosen/rejected weights and beta 0.1.",
        "ppo": "**PPO · optimize against a reward model.** Select a local reward checkpoint/adapter first. Start with 4 update epochs and a buffer of 1; PPO has no training-validation split in this workflow.",
        "rm": "**RM · train a reward score from chosen/rejected pairs.** The pairwise reward loss needs no additional stage-specific coefficients. Adjust learning rate and epochs above, and enable a validation set below to monitor reward loss.",
    },
    "zh": {
        "sft": "**SFT · 从示例回答中学习。** 默认仅对助手回答计算损失。只有数据确实需要时才调整提示词或历史消息掩码；首次训练建议保持噪声为 0。",
        "pt": "**PT · 继续下一词预测预训练。** 样本打包可拼接短文本，提高序列空间利用率。仅在本地分词器新增词元后才调整词表大小。",
        "dpo": "**DPO · 学习优选和拒绝回答对。** 建议从 sigmoid 损失、beta 0.1、SFT 权重 0 开始。选择其他损失后，仅显示与其相关的设置。",
        "kto": "**KTO · 学习单条回答的正负反馈。** 请使用包含好坏标签的数据，而非 DPO 回答对。建议从正负样本等权重和 beta 0.1 开始。",
        "ppo": "**PPO · 利用奖励模型优化。** 请先选择本地奖励检查点或适配器。建议从 4 轮更新、缓冲区 1 开始；此流程中的 PPO 不支持训练验证集划分。",
        "rm": "**RM · 从优选和拒绝回答对中学习奖励评分。** 成对奖励损失无需额外阶段系数。可在上方调整学习率和训练轮数，并在下方启用验证集以观察奖励损失。",
    },
    "ru": {
        "sft": "**SFT · обучение на примерах ответов.** По умолчанию потери считаются только по ответам ассистента. Меняйте маски запросов и истории только при необходимости; для первого запуска оставьте шум 0.",
        "pt": "**PT · продолжение предобучения следующего токена.** Упаковка объединяет короткие тексты. Меняйте размер словаря только после добавления токенов в локальный токенизатор.",
        "dpo": "**DPO · обучение на парах принятых и отклонённых ответов.** Начните с sigmoid, beta 0.1 и веса SFT 0. Для других функций потерь показываются только применимые настройки.",
        "kto": "**KTO · обучение по положительным и отрицательным отзывам.** Нужны метки желательности отдельных ответов, не пары DPO. Начните с равных весов и beta 0.1.",
        "ppo": "**PPO · оптимизация с моделью награды.** Сначала выберите локальный checkpoint или адаптер награды. Начните с 4 эпох обновления и буфера 1; в этом режиме нет валидации во время обучения.",
        "rm": "**RM · оценка награды по парам ответов.** Парная функция потерь не требует дополнительных коэффициентов. Настройте скорость обучения и эпохи выше, а валидацию для контроля потерь — ниже.",
    },
    "ko": {
        "sft": "**SFT · 예시 응답으로 학습합니다.** 기본적으로 어시스턴트 응답만 손실에 반영합니다. 데이터에 필요한 경우만 프롬프트·대화 이력 마스킹을 바꾸고 첫 실행은 잡음 0을 권장합니다.",
        "pt": "**PT · 다음 토큰 사전 학습을 계속합니다.** 패킹은 짧은 텍스트를 연결해 공간을 활용합니다. 로컬 토크나이저에 토큰을 추가한 경우에만 어휘 크기를 변경하세요.",
        "dpo": "**DPO · 선호·비선호 응답 쌍으로 학습합니다.** sigmoid 손실, beta 0.1, SFT 가중치 0부터 시작하세요. 다른 손실은 관련 설정만 표시합니다.",
        "kto": "**KTO · 개별 응답의 긍정·부정 피드백으로 학습합니다.** DPO 쌍이 아닌 선호도 라벨 데이터가 필요합니다. 동일 가중치와 beta 0.1부터 시작하세요.",
        "ppo": "**PPO · 보상 모델로 최적화합니다.** 로컬 보상 체크포인트나 어댑터를 먼저 선택하세요. 업데이트 4회, 버퍼 1을 권장하며 이 흐름의 PPO는 학습 검증 분할을 지원하지 않습니다.",
        "rm": "**RM · 응답 쌍의 보상 점수를 학습합니다.** 쌍별 손실에 추가 계수가 필요하지 않습니다. 위에서 학습률과 에포크를 조정하고 아래에서 검증을 켜 보상 손실을 확인하세요.",
    },
    "ja": {
        "sft": "**SFT · 回答例から学習します。** 既定ではアシスタントの回答のみを損失に含めます。必要な場合のみプロンプトや履歴のマスクを変更し、初回はノイズ 0 を推奨します。",
        "pt": "**PT · 次トークン予測の事前学習を継続します。** パッキングで短文を連結して領域を活用します。語彙サイズの変更はローカルトークナイザーにトークンを追加した場合だけにしてください。",
        "dpo": "**DPO · 採用・不採用の回答ペアから学習します。** sigmoid 損失、beta 0.1、SFT 重み 0 から開始してください。他の損失では関連する設定のみ表示します。",
        "kto": "**KTO · 個別回答の正負の評価から学習します。** DPO ペアではなく望ましさのラベルを持つデータが必要です。同じ重みと beta 0.1 から開始してください。",
        "ppo": "**PPO · 報酬モデルで最適化します。** 最初にローカル報酬チェックポイントまたはアダプターを選択します。更新 4 エポック、バッファー 1 を推奨します。この PPO フローでは学習中の検証分割をサポートしません。",
        "rm": "**RM · 回答ペアから報酬スコアを学習します。** ペア損失に追加係数は不要です。上で学習率とエポックを調整し、下で検証を有効にして報酬損失を確認してください。",
    },
}


def _field(labels, descriptions):
    return {
        lang: {"label": label, "info": description}
        for lang, label, description in zip(LANGUAGES, labels, descriptions, strict=True)
    }


def _labels(values):
    return {lang: {"label": value} for lang, value in zip(LANGUAGES, values, strict=True)}


STAGE_LOCALES = {
    "wizard_stage_params": _labels(
        (
            "Adjust for your training goal",
            "按训练目标调整",
            "Настройки цели обучения",
            "학습 목표별 조정",
            "学習目的に合わせて調整",
        )
    ),
    "wizard_validation_params": _labels(
        (
            "Monitor training with a validation set",
            "通过验证集观察训练效果",
            "Контроль обучения на валидации",
            "검증 데이터로 학습 모니터링",
            "検証データで学習を確認",
        )
    ),
    "validation_mode": _field(
        (
            "Use a validation set?",
            "是否使用验证集？",
            "Использовать валидацию?",
            "검증 데이터를 사용할까요?",
            "検証データを使いますか？",
        ),
        (
            "Validation measures loss on held-out data without updating weights. Start with a 10% split; a separate dataset must not overlap training data. It adds time and memory use.",
            "验证会使用未参与训练的数据计算损失，不更新权重。建议先划分 10%；独立验证集不能与训练数据重叠。验证会增加时间和显存开销。",
            "Валидация измеряет потери без обновления весов. Начните с 10%; отдельный набор не должен пересекаться с обучающим. Требуются дополнительное время и память.",
            "검증은 가중치 갱신 없이 별도 데이터의 손실을 측정합니다. 10% 분할부터 시작하세요. 별도 데이터는 학습 데이터와 겹치면 안 되며 시간과 메모리가 추가됩니다.",
            "検証は重みを更新せず未学習データの損失を測ります。まず 10% 分割を推奨します。別データは学習データと重複させないでください。時間とメモリが増えます。",
        ),
    ),
    "val_size": _field(
        (
            "Validation split (%)",
            "验证集划分比例（%）",
            "Доля валидации (%)",
            "검증 데이터 분할 비율(%)",
            "検証データの分割割合（%）",
        ),
        (
            "10 reserves 10% of training examples for validation. The split is percentage-based; validation runs whenever a checkpoint is saved.",
            "10 表示按比例保留 10% 的训练样本用于验证。划分始终按百分比进行，每次保存检查点时同步验证。",
            "10 резервирует 10% обучающих примеров для валидации. Разделение задаётся в процентах; валидация выполняется при каждом сохранении контрольной точки.",
            "10은 학습 예제의 10%를 검증용으로 분할합니다. 분할은 백분율 기준이며 체크포인트를 저장할 때마다 검증합니다.",
            "10 は学習例の 10% を検証用に分割します。分割は割合で行い、チェックポイントを保存するたびに検証します。",
        ),
    ),
    "eval_dataset": _field(
        (
            "Separate validation dataset",
            "独立验证集",
            "Отдельный набор валидации",
            "별도 검증 데이터",
            "別の検証データセット",
        ),
        (
            "Choose registered datasets from the same data directory and in the same stage format. Do not select training datasets here. This replaces the fractional split.",
            "从同一数据目录选择已注册且符合当前训练阶段格式的数据集。不要选择训练集本身；此选项会替代比例划分。",
            "Выберите зарегистрированные наборы из той же папки в формате выбранного этапа. Не выбирайте обучающие наборы; это заменяет разделение по доле.",
            "같은 데이터 폴더에서 현재 단계 형식으로 등록된 데이터를 고르세요. 학습 데이터는 선택하지 마세요. 비율 분할 대신 사용합니다.",
            "同じデータフォルダーから現在の段階の形式で登録されたデータを選択します。学習データ自体を選ばないでください。割合分割の代わりに使います。",
        ),
    ),
    "eval_batch_size": _field(
        (
            "Validation batch per device",
            "每设备验证批大小",
            "Пакет валидации на устройство",
            "장치당 검증 배치",
            "デバイスごとの検証バッチ",
        ),
        (
            "Start with 1 to limit validation memory. Larger values can run faster but can exhaust GPU memory even if training fits.",
            "建议从 1 开始以降低验证显存。更大数值可能更快，但即使训练显存足够，验证也可能耗尽显存。",
            "Начните с 1 для экономии памяти. Большие значения ускоряют валидацию, но могут переполнить GPU даже при успешном обучении.",
            "검증 메모리를 줄이려면 1부터 시작하세요. 값이 크면 빨라질 수 있지만 학습이 가능해도 검증 중 메모리가 부족할 수 있습니다.",
            "メモリを抑えるため 1 から開始します。大きいと速くなる場合がありますが、学習可能でも検証中に GPU メモリ不足になることがあります。",
        ),
    ),
    "dpo_label_smoothing": _field(
        ("DPO label smoothing", "DPO 标签平滑", "Сглаживание меток DPO", "DPO 라벨 평활화", "DPO ラベル平滑化"),
        (
            "For sigmoid loss only. Start at 0; raise slightly for noisy preference labels. Valid range: 0 to 0.5.",
            "仅适用于 sigmoid 损失。建议从 0 开始；偏好标签噪声较大时可略微提高。范围为 0 至 0.5。",
            "Только для sigmoid. Начните с 0; слегка увеличьте при шумных предпочтениях. Диапазон: 0–0.5.",
            "sigmoid 전용입니다. 0부터 시작하고 선호 라벨에 잡음이 많으면 조금 높이세요. 범위는 0~0.5입니다.",
            "sigmoid のみ。0 から開始し、評価ラベルにノイズがあれば少し上げます。範囲は 0～0.5 です。",
        ),
    ),
    "simpo_gamma": _field(
        ("SimPO reward margin", "SimPO 奖励间隔", "Отступ награды SimPO", "SimPO 보상 마진", "SimPO 報酬マージン"),
        (
            "Only used by SimPO loss. The target separation between preferred and rejected answers; start with 0.5.",
            "仅用于 SimPO 损失，表示优选与拒绝回答之间的目标奖励间隔；建议从 0.5 开始。",
            "Только для SimPO: целевой разрыв награды между принятым и отклонённым ответом. Начните с 0.5.",
            "SimPO 전용입니다. 선호·비선호 응답 사이 목표 보상 차이며 0.5부터 시작하세요.",
            "SimPO のみ。採用・不採用回答の目標報酬差です。0.5 から開始してください。",
        ),
    ),
    "kto_chosen_weight": _field(
        (
            "KTO positive-feedback weight",
            "KTO 正反馈权重",
            "Вес положительных отзывов KTO",
            "KTO 긍정 피드백 가중치",
            "KTO 正の評価の重み",
        ),
        (
            "Scales loss from desirable examples. Start with 1; adjust with the negative-feedback weight for imbalanced data.",
            "控制正反馈样本的损失权重。建议为 1；数据不均衡时与负反馈权重一起调整。",
            "Масштабирует потери желательных примеров. Начните с 1; настройте вместе с отрицательным весом при дисбалансе.",
            "바람직한 예시의 손실 가중치입니다. 1부터 시작하고 불균형 데이터에서는 부정 피드백 가중치와 함께 조정하세요.",
            "望ましい例の損失の重みです。1 から開始し、不均衡時は負の評価の重みと併せて調整します。",
        ),
    ),
    "kto_rejected_weight": _field(
        (
            "KTO negative-feedback weight",
            "KTO 负反馈权重",
            "Вес отрицательных отзывов KTO",
            "KTO 부정 피드백 가중치",
            "KTO 負の評価の重み",
        ),
        (
            "Scales loss from undesirable examples. Start with 1; higher values make negative feedback more influential.",
            "控制负反馈样本的损失权重。建议为 1；提高数值会增强负反馈的影响。",
            "Масштабирует потери нежелательных примеров. Начните с 1; большее значение усиливает отрицательный отзыв.",
            "바람직하지 않은 예시의 손실 가중치입니다. 1부터 시작하며 높일수록 부정 피드백의 영향이 커집니다.",
            "望ましくない例の損失の重みです。1 から開始し、値を上げると負の評価の影響が強まります。",
        ),
    ),
    "ppo_epochs": _field(
        ("PPO update epochs", "PPO 更新轮数", "Эпохи обновления PPO", "PPO 업데이트 에포크", "PPO 更新エポック"),
        (
            "How often each collected experience batch is reused. Default 4; too many updates can destabilize learning.",
            "每批已收集经验重复用于更新的次数。默认 4；更新次数过多可能导致训练不稳定。",
            "Сколько раз повторно использовать собранный опыт. По умолчанию 4; слишком много обновлений может нарушить стабильность.",
            "수집한 경험 배치를 재사용하는 횟수입니다. 기본 4이며 너무 많으면 학습이 불안정해질 수 있습니다.",
            "収集済み経験バッチを再利用する回数です。既定は 4 で、多すぎると学習が不安定になります。",
        ),
    ),
    "ppo_buffer_size": _field(
        ("PPO experience buffer", "PPO 经验缓冲区", "Буфер опыта PPO", "PPO 경험 버퍼", "PPO 経験バッファー"),
        (
            "Mini-batches collected per PPO update. Start with 1; increasing this requires more experience storage and time.",
            "每次 PPO 更新收集的微批次数。建议从 1 开始；增大会增加经验存储和时间开销。",
            "Мини-пакеты опыта на обновление PPO. Начните с 1; увеличение требует больше памяти и времени.",
            "PPO 갱신마다 모으는 미니 배치 수입니다. 1부터 시작하며 늘리면 저장 공간과 시간이 더 필요합니다.",
            "PPO 更新ごとに集めるミニバッチ数です。1 から開始し、増やすと保存領域と時間が必要になります。",
        ),
    ),
    "ppo_target": _field(
        ("PPO target KL", "PPO 目标 KL", "Целевой KL PPO", "PPO 목표 KL", "PPO 目標 KL"),
        (
            "Target divergence from the reference policy for adaptive KL control. Default 6; tune only after checking reward and KL curves.",
            "自适应 KL 控制使用的参考策略目标偏离程度。默认 6；建议观察奖励和 KL 曲线后再调整。",
            "Целевое отклонение от опорной политики для адаптивного KL. По умолчанию 6; меняйте после анализа награды и KL.",
            "적응형 KL 제어를 위한 참조 정책과의 목표 차이입니다. 기본 6이며 보상·KL 곡선을 확인한 뒤 조정하세요.",
            "適応 KL 制御における参照方策からの目標乖離です。既定は 6 で、報酬と KL 曲線を確認してから調整します。",
        ),
    ),
}

_VALIDATION_CHOICES = {
    "en": ("No validation", "Reserve a fraction of training data", "Use a separate dataset"),
    "zh": ("暂不验证", "从训练数据中划分", "使用独立验证集"),
    "ru": ("Без валидации", "Выделить долю обучающих данных", "Отдельный набор"),
    "ko": ("검증 안 함", "학습 데이터 일부 분할", "별도 데이터 사용"),
    "ja": ("検証しない", "学習データから分割", "別のデータを使用"),
}
_VALIDATION_GUIDES = (
    "Optional: monitor held-out loss during training. Start with a 10% split and a validation batch of 1. Training and validation data should not overlap. PPO does not support this panel.",
    "可选：训练期间观察未参与训练的数据损失。建议从 10% 划分、验证批大小 1 开始。训练集与验证集不应重叠。PPO 不支持此面板。",
    "Необязательно: следите за потерями на отложенных данных. Начните с доли 10% и пакета 1. Данные не должны пересекаться с обучением. Панель недоступна для PPO.",
    "선택 사항: 학습 중 별도 데이터의 손실을 확인합니다. 10% 분할과 검증 배치 1부터 시작하세요. 학습 데이터와 검증 데이터는 겹치면 안 됩니다. PPO에서는 지원하지 않습니다.",
    "任意：学習中に未学習データの損失を確認します。10% 分割と検証バッチ 1 から開始してください。学習と検証のデータは重複させません。PPO では使えません。",
)
STAGE_LOCALES["wizard_validation_guide"] = {
    lang: {"value": value} for lang, value in zip(LANGUAGES, _VALIDATION_GUIDES, strict=True)
}
for _lang in LANGUAGES:
    STAGE_LOCALES["validation_mode"][_lang]["choices"] = list(
        zip(_VALIDATION_CHOICES[_lang], ("none", "split", "separate"), strict=True)
    )

STAGE_VALIDATION_ERRORS = {
    "en": {
        "dataset": "Choose a separate validation dataset or turn validation off.",
        "split": "The validation percentage must be greater than 0 and less than 100.",
    },
    "zh": {"dataset": "请选择独立验证集，或关闭验证。", "split": "验证集百分比必须大于 0 且小于 100。"},
    "ru": {
        "dataset": "Выберите отдельный набор валидации или отключите её.",
        "split": "Процент валидации должен быть больше 0 и меньше 100.",
    },
    "ko": {
        "dataset": "별도 검증 데이터를 선택하거나 검증을 끄세요.",
        "split": "검증 백분율은 0보다 크고 100보다 작아야 합니다.",
    },
    "ja": {
        "dataset": "別の検証データを選択するか検証を無効にしてください。",
        "split": "検証の百分率は 0 より大きく 100 より小さくしてください。",
    },
}
