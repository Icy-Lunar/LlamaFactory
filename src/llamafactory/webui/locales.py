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

LOCALES = {
    "title": {
        "en": {
            "value": "<h1><center>Cyrene Yield · Guided Model Training</center></h1>",
        },
        "ru": {
            "value": "<h1><center>Cyrene Yield · Пошаговое обучение моделей</center></h1>",
        },
        "zh": {
            "value": "<h1><center>Cyrene Yield · 引导式模型训练</center></h1>",
        },
        "ko": {
            "value": "<h1><center>Cyrene Yield · 안내형 모델 학습</center></h1>",
        },
        "ja": {
            "value": "<h1><center>Cyrene Yield · ガイド付きモデル学習</center></h1>",
        },
    },
    "subtitle": {
        "en": {
            "value": (
                "<p><center>Local-only model workflow · automatic configuration · VRAM safety check · "
                "adapter merge · <a href='https://github.com/DoHorizon-AI/Cyrene-Yield' target='_blank'>"
                "project repository</a></center></p>"
            ),
        },
        "ru": {
            "value": (
                "<p><center>Локальные модели · автоматическая настройка · проверка видеопамяти · "
                "слияние адаптеров · <a href='https://github.com/DoHorizon-AI/Cyrene-Yield' target='_blank'>"
                "репозиторий проекта</a></center></p>"
            ),
        },
        "zh": {
            "value": (
                "<p><center>仅使用本地模型 · 自动生成配置 · 训练前显存检查 · 适配器合并 · "
                "<a href='https://github.com/DoHorizon-AI/Cyrene-Yield' target='_blank'>项目仓库</a>"
                "</center></p>"
            ),
        },
        "ko": {
            "value": (
                "<p><center>로컬 모델 전용 · 자동 구성 · 학습 전 GPU 메모리 확인 · 어댑터 병합 · "
                "<a href='https://github.com/DoHorizon-AI/Cyrene-Yield' target='_blank'>프로젝트 저장소</a>"
                "</center></p>"
            ),
        },
        "ja": {
            "value": (
                "<p><center>ローカルモデル専用 · 自動構成 · 学習前の GPU メモリ確認 · アダプターマージ · "
                "<a href='https://github.com/DoHorizon-AI/Cyrene-Yield' target='_blank'>プロジェクトリポジトリ</a>"
                "</center></p>"
            ),
        },
    },
    "lang": {
        "en": {
            "label": "Language",
        },
        "ru": {
            "label": "Язык",
        },
        "zh": {
            "label": "语言",
        },
        "ko": {
            "label": "언어",
        },
        "ja": {
            "label": "言語",
        },
    },
    "model_path": {
        "en": {
            "label": "Local model directory",
            "info": "Enter an existing local directory containing config.json and model weight files.",
        },
        "ru": {
            "label": "Локальный каталог модели",
            "info": "Укажите существующий локальный каталог с config.json и файлами весов модели.",
        },
        "zh": {
            "label": "本地模型目录",
            "info": "请输入包含 config.json 和模型权重文件的现有本地目录。",
        },
        "ko": {
            "label": "로컬 모델 디렉터리",
            "info": "config.json 및 모델 가중치 파일이 있는 기존 로컬 디렉터리를 입력하세요.",
        },
        "ja": {
            "label": "ローカルモデルディレクトリ",
            "info": "config.json とモデル重みファイルを含む既存のローカルディレクトリを入力してください。",
        },
    },
    "finetuning_type": {
        "en": {
            "label": "Finetuning method",
        },
        "ru": {
            "label": "Метод дообучения",
        },
        "zh": {
            "label": "微调方法",
        },
        "ko": {
            "label": "파인튜닝 방법",
        },
        "ja": {
            "label": "ファインチューニング方法",
        },
    },
    "checkpoint_path": {
        "en": {
            "label": "Checkpoint path",
        },
        "ru": {
            "label": "Путь контрольной точки",
        },
        "zh": {
            "label": "检查点路径",
        },
        "ko": {
            "label": "체크포인트 경로",
        },
        "ja": {
            "label": "チェックポイントパス",
        },
    },
    "quantization_bit": {
        "en": {
            "label": "Quantization bit",
            "info": "Enable quantization (QLoRA).",
        },
        "ru": {
            "label": "Уровень квантования",
            "info": "Включить квантование (QLoRA).",
        },
        "zh": {
            "label": "量化等级",
            "info": "启用量化（QLoRA）。",
        },
        "ko": {
            "label": "양자화 비트",
            "info": "양자화 활성화 (QLoRA).",
        },
        "ja": {
            "label": "量子化ビット",
            "info": "量子化を有効にする (QLoRA)。",
        },
    },
    "quantization_method": {
        "en": {
            "label": "Quantization method",
            "info": "Quantization algorithm to use.",
        },
        "ru": {
            "label": "Метод квантования",
            "info": "Алгоритм квантования, который следует использовать.",
        },
        "zh": {
            "label": "量化方法",
            "info": "使用的量化算法。",
        },
        "ko": {
            "label": "양자화 방법",
            "info": "사용할 양자화 알고리즘.",
        },
        "ja": {
            "label": "量子化方法",
            "info": "使用する量子化アルゴリズム。",
        },
    },
    "template": {
        "en": {
            "label": "Chat template",
            "info": "The chat template used in constructing prompts.",
        },
        "ru": {
            "label": "Шаблон чата",
            "info": "Шаблон чата используемый для составления подсказок.",
        },
        "zh": {
            "label": "对话模板",
            "info": "构建提示词时使用的模板。",
        },
        "ko": {
            "label": "채팅 템플릿",
            "info": "프롬프트 작성에 사용되는 채팅 템플릿.",
        },
        "ja": {
            "label": "チャットテンプレート",
            "info": "プロンプトの構築に使用されるチャットテンプレート。",
        },
    },
    "rope_scaling": {
        "en": {
            "label": "RoPE scaling",
            "info": "RoPE scaling method to use.",
        },
        "ru": {
            "label": "Масштабирование RoPE",
            "info": "Метод масштабирования RoPE для использования.",
        },
        "zh": {"label": "RoPE 插值方法", "info": "RoPE 插值时使用的方法。"},
        "ko": {
            "label": "RoPE 스케일링",
            "info": "사용할 RoPE 스케일링 방법.",
        },
        "ja": {
            "label": "RoPE スケーリング",
            "info": "使用する RoPE スケーリング方法。",
        },
    },
    "booster": {
        "en": {
            "label": "Booster",
            "info": "Approach used to boost training speed.",
        },
        "ru": {
            "label": "Ускоритель",
            "info": "Подход, используемый для ускорения обучения.",
        },
        "zh": {"label": "加速方式", "info": "使用的加速方法。"},
        "ko": {
            "label": "부스터",
            "info": "훈련 속도를 향상시키기 위해 사용된 접근 방식.",
        },
        "ja": {
            "label": "ブースター",
            "info": "トレーニング速度を向上させるためのアプローチ。",
        },
    },
    "training_stage": {
        "en": {
            "label": "Stage",
            "info": "The stage to perform in training.",
        },
        "ru": {
            "label": "Этап",
            "info": "Этап выполнения обучения.",
        },
        "zh": {
            "label": "训练阶段",
            "info": "目前采用的训练方式。",
        },
        "ko": {
            "label": "학습 단계",
            "info": "수행할 학습 방법.",
        },
        "ja": {
            "label": "ステージ",
            "info": "トレーニングで実行するステージ。",
        },
    },
    "dataset_dir": {
        "en": {
            "label": "Data dir",
            "info": "Path to the data directory.",
        },
        "ru": {
            "label": "Директория данных",
            "info": "Путь к директории данных.",
        },
        "zh": {
            "label": "数据路径",
            "info": "数据文件夹的路径。",
        },
        "ko": {
            "label": "데이터 디렉토리",
            "info": "데이터 디렉토리의 경로.",
        },
        "ja": {
            "label": "データディレクトリ",
            "info": "データディレクトリへのパス。",
        },
    },
    "dataset": {
        "en": {
            "label": "Dataset",
        },
        "ru": {
            "label": "Набор данных",
        },
        "zh": {
            "label": "数据集",
        },
        "ko": {
            "label": "데이터셋",
        },
        "ja": {
            "label": "データセット",
        },
    },
    "data_preview_btn": {
        "en": {
            "value": "Preview dataset",
        },
        "ru": {
            "value": "Просмотреть набор данных",
        },
        "zh": {
            "value": "预览数据集",
        },
        "ko": {
            "value": "데이터셋 미리보기",
        },
        "ja": {
            "value": "データセットをプレビュー",
        },
    },
    "preview_count": {
        "en": {
            "label": "Count",
        },
        "ru": {
            "label": "Количество",
        },
        "zh": {
            "label": "数量",
        },
        "ko": {
            "label": "개수",
        },
        "ja": {
            "label": "カウント",
        },
    },
    "page_index": {
        "en": {
            "label": "Page",
        },
        "ru": {
            "label": "Страница",
        },
        "zh": {
            "label": "页数",
        },
        "ko": {
            "label": "페이지",
        },
        "ja": {
            "label": "ページ",
        },
    },
    "prev_btn": {
        "en": {
            "value": "Prev",
        },
        "ru": {
            "value": "Предыдущая",
        },
        "zh": {
            "value": "上一页",
        },
        "ko": {
            "value": "이전",
        },
        "ja": {
            "value": "前へ",
        },
    },
    "next_btn": {
        "en": {
            "value": "Next",
        },
        "ru": {
            "value": "Следующая",
        },
        "zh": {
            "value": "下一页",
        },
        "ko": {
            "value": "다음",
        },
        "ja": {
            "value": "次へ",
        },
    },
    "close_btn": {
        "en": {
            "value": "Close",
        },
        "ru": {
            "value": "Закрыть",
        },
        "zh": {
            "value": "关闭",
        },
        "ko": {
            "value": "닫기",
        },
        "ja": {
            "value": "閉じる",
        },
    },
    "preview_samples": {
        "en": {
            "label": "Samples",
        },
        "ru": {
            "label": "Примеры",
        },
        "zh": {
            "label": "样例",
        },
        "ko": {
            "label": "샘플",
        },
        "ja": {
            "label": "サンプル",
        },
    },
    "learning_rate": {
        "en": {
            "label": "Learning rate",
            "info": "Initial learning rate for AdamW.",
        },
        "ru": {
            "label": "Скорость обучения",
            "info": "Начальная скорость обучения для AdamW.",
        },
        "zh": {
            "label": "学习率",
            "info": "AdamW 优化器的初始学习率。",
        },
        "ko": {
            "label": "학습률",
            "info": "AdamW의 초기 학습률.",
        },
        "ja": {
            "label": "学習率",
            "info": "AdamW の初期学習率。",
        },
    },
    "num_train_epochs": {
        "en": {
            "label": "Epochs",
            "info": "Total number of training epochs to perform.",
        },
        "ru": {
            "label": "Эпохи",
            "info": "Общее количество эпох обучения.",
        },
        "zh": {
            "label": "训练轮数",
            "info": "需要执行的训练总轮数。",
        },
        "ko": {
            "label": "에포크",
            "info": "수행할 총 학습 에포크 수.",
        },
        "ja": {
            "label": "エポック数",
            "info": "実行するトレーニングの総エポック数。",
        },
    },
    "max_grad_norm": {
        "en": {
            "label": "Maximum gradient norm",
            "info": "Norm for gradient clipping.",
        },
        "ru": {
            "label": "Максимальная норма градиента",
            "info": "Норма для обрезки градиента.",
        },
        "zh": {
            "label": "最大梯度范数",
            "info": "用于梯度裁剪的范数。",
        },
        "ko": {
            "label": "최대 그레디언트 노름(norm)",
            "info": "그레디언트 클리핑을 위한 노름(norm).",
        },
        "ja": {
            "label": "最大勾配ノルム",
            "info": "勾配クリッピングのためのノルム。",
        },
    },
    "train_seed": {
        "en": {
            "label": "Seed",
            "info": "Random seed for training.",
        },
        "ru": {
            "label": "Seed",
            "info": "Random seed for training.",
        },
        "zh": {
            "label": "随机种子",
            "info": "训练使用的随机种子。",
        },
        "ko": {
            "label": "Seed",
            "info": "Random seed for training.",
        },
        "ja": {
            "label": "Seed",
            "info": "Random seed for training.",
        },
    },
    "max_samples": {
        "en": {
            "label": "Max samples",
            "info": "Maximum samples per dataset.",
        },
        "ru": {
            "label": "Максимальное количество образцов",
            "info": "Максимальное количество образцов на набор данных.",
        },
        "zh": {
            "label": "最大样本数",
            "info": "每个数据集的最大样本数。",
        },
        "ko": {
            "label": "최대 샘플 수",
            "info": "데이터셋 당 최대 샘플 수.",
        },
        "ja": {
            "label": "最大サンプル数",
            "info": "データセットごとの最大サンプル数。",
        },
    },
    "compute_type": {
        "en": {
            "label": "Compute type",
            "info": "Whether to use mixed precision training.",
        },
        "ru": {
            "label": "Тип вычислений",
            "info": "Использовать ли обучение смешанной точности.",
        },
        "zh": {
            "label": "计算类型",
            "info": "是否使用混合精度训练。",
        },
        "ko": {
            "label": "연산 유형",
            "info": "혼합 정밀도 훈련을 사용할지 여부.",
        },
        "ja": {
            "label": "計算タイプ",
            "info": "混合精度トレーニングを使用するかどうか。",
        },
    },
    "cutoff_len": {
        "en": {
            "label": "Cutoff length",
            "info": "Max tokens in input sequence.",
        },
        "ru": {
            "label": "Длина обрезки",
            "info": "Максимальное количество токенов во входной последовательности.",
        },
        "zh": {
            "label": "截断长度",
            "info": "输入序列分词后的最大长度。",
        },
        "ko": {
            "label": "컷오프 길이",
            "info": "입력 시퀀스의 최대 토큰 수.",
        },
        "ja": {
            "label": "カットオフ長",
            "info": "入力シーケンスの最大トークン数。",
        },
    },
    "batch_size": {
        "en": {
            "label": "Batch size",
            "info": "Number of samples processed on each GPU.",
        },
        "ru": {
            "label": "Размер пакета",
            "info": "Количество образцов для обработки на каждом GPU.",
        },
        "zh": {
            "label": "批处理大小",
            "info": "每个 GPU 处理的样本数量。",
        },
        "ko": {
            "label": "배치 크기",
            "info": "각 GPU에서 처리되는 샘플 수.",
        },
        "ja": {
            "label": "バッチサイズ",
            "info": "各 GPU で処理されるサンプル数。",
        },
    },
    "gradient_accumulation_steps": {
        "en": {
            "label": "Gradient accumulation",
            "info": "Number of steps for gradient accumulation.",
        },
        "ru": {
            "label": "Накопление градиента",
            "info": "Количество шагов накопления градиента.",
        },
        "zh": {
            "label": "梯度累积",
            "info": "梯度累积的步数。",
        },
        "ko": {
            "label": "그레디언트 누적",
            "info": "그레디언트 누적 단계 수.",
        },
        "ja": {
            "label": "勾配累積",
            "info": "勾配累積のステップ数。",
        },
    },
    "lr_scheduler_type": {
        "en": {
            "label": "LR scheduler",
            "info": "Name of the learning rate scheduler.",
        },
        "ru": {
            "label": "Планировщик скорости обучения",
            "info": "Название планировщика скорости обучения.",
        },
        "zh": {
            "label": "学习率调节器",
            "info": "学习率调度器的名称。",
        },
        "ko": {
            "label": "LR 스케줄러",
            "info": "학습률 스케줄러의 이름.",
        },
        "ja": {
            "label": "学習率スケジューラ",
            "info": "学習率スケジューラの名前。",
        },
    },
    "extra_tab": {
        "en": {
            "label": "Extra configurations",
        },
        "ru": {
            "label": "Дополнительные конфигурации",
        },
        "zh": {
            "label": "其它参数设置",
        },
        "ko": {
            "label": "추가 구성(configuration)",
        },
        "ja": {
            "label": "追加設定",
        },
    },
    "logging_steps": {
        "en": {
            "label": "Logging steps",
            "info": "Number of steps between two logs.",
        },
        "ru": {
            "label": "Шаги логирования",
            "info": "Количество шагов между двумя записями в журнале.",
        },
        "zh": {
            "label": "日志间隔",
            "info": "每两次日志输出间的更新步数。",
        },
        "ko": {
            "label": "로깅 스텝",
            "info": "이전 로깅과 다음 로깅 간 스텝 수.",
        },
        "ja": {
            "label": "ロギングステップ",
            "info": "2 つのログ間のステップ数。",
        },
    },
    "save_steps": {
        "en": {
            "label": "Save steps",
            "info": "Number of steps between two checkpoints.",
        },
        "ru": {
            "label": "Шаги сохранения",
            "info": "Количество шагов между двумя контрольными точками.",
        },
        "zh": {
            "label": "保存间隔",
            "info": "每两次断点保存间的更新步数。",
        },
        "ko": {
            "label": "저장 스텝",
            "info": "이전 체크포인트와 다음 체크포인트 사이의 스텝 수.",
        },
        "ja": {
            "label": "保存ステップ",
            "info": "2 つのチェックポイント間のステップ数。",
        },
    },
    "warmup_steps": {
        "en": {
            "label": "Warmup steps",
            "info": "Number of steps used for warmup.",
        },
        "ru": {
            "label": "Шаги прогрева",
            "info": "Количество шагов, используемых для прогрева.",
        },
        "zh": {
            "label": "预热步数",
            "info": "学习率预热采用的步数。",
        },
        "ko": {
            "label": "Warmup 스텝",
            "info": "Warmup에 사용되는 스텝 수.",
        },
        "ja": {
            "label": "ウォームアップステップ",
            "info": "ウォームアップに使用されるステップ数。",
        },
    },
    "neftune_alpha": {
        "en": {
            "label": "NEFTune alpha",
            "info": "Magnitude of noise adding to embedding vectors.",
        },
        "ru": {
            "label": "NEFTune alpha",
            "info": "Величина шума, добавляемого к векторам вложений.",
        },
        "zh": {
            "label": "NEFTune 噪声参数",
            "info": "嵌入向量所添加的噪声大小。",
        },
        "ko": {
            "label": "NEFTune 알파",
            "info": "임베딩 벡터에 추가되는 노이즈의 크기.",
        },
        "ja": {
            "label": "NEFTune alpha",
            "info": "埋め込みベクトルに追加されるノイズの大きさ。",
        },
    },
    "extra_args": {
        "en": {
            "label": "Extra arguments",
            "info": "Extra arguments passed to the trainer in JSON format.",
        },
        "ru": {
            "label": "Дополнительные аргументы",
            "info": "Дополнительные аргументы, которые передаются тренеру в формате JSON.",
        },
        "zh": {
            "label": "额外参数",
            "info": "以 JSON 格式传递给训练器的额外参数。",
        },
        "ko": {
            "label": "추가 인수",
            "info": "JSON 형식으로 트레이너에게 전달할 추가 인수입니다.",
        },
        "ja": {
            "label": "追加引数",
            "info": "JSON 形式でトレーナーに渡される追加引数。",
        },
    },
    "packing": {
        "en": {
            "label": "Pack sequences",
            "info": "Pack sequences into samples of fixed length.",
        },
        "ru": {
            "label": "Упаковка последовательностей",
            "info": "Упаковка последовательностей в образцы фиксированной длины.",
        },
        "zh": {
            "label": "序列打包",
            "info": "将序列打包为等长样本。",
        },
        "ko": {
            "label": "시퀀스 패킹",
            "info": "고정된 길이의 샘플로 시퀀스를 패킹합니다.",
        },
        "ja": {
            "label": "シーケンスパッキング",
            "info": "シーケンスを固定長のサンプルにパッキングします。",
        },
    },
    "neat_packing": {
        "en": {
            "label": "Use neat packing",
            "info": "Avoid cross-attention between packed sequences.",
        },
        "ru": {
            "label": "Используйте аккуратную упаковку",
            "info": "избегайте перекрестного внимания между упакованными последовательностями.",
        },
        "zh": {
            "label": "使用无污染打包",
            "info": "避免打包后的序列产生交叉注意力。",
        },
        "ko": {
            "label": "니트 패킹 사용",
            "info": "패킹된 시퀀스 간의 크로스 어텐션을 피합니다.",
        },
        "ja": {
            "label": "無汚染パッキングを使用",
            "info": "パッキング後のシーケンス間のクロスアテンションを避けます。",
        },
    },
    "train_on_prompt": {
        "en": {
            "label": "Train on prompt",
            "info": "Disable the label mask on the prompt (only for SFT).",
        },
        "ru": {
            "label": "Тренировка на подсказке",
            "info": "Отключить маску меток на подсказке (только для SFT).",
        },
        "zh": {
            "label": "学习提示词",
            "info": "不在提示词的部分添加掩码（仅适用于 SFT）。",
        },
        "ko": {
            "label": "프롬프트도 학습",
            "info": "프롬프트에서 라벨 마스킹을 비활성화합니다 (SFT에만 해당).",
        },
        "ja": {
            "label": "プロンプトで学習",
            "info": "プロンプト部分にマスクを追加しない（SFT のみ）。",
        },
    },
    "mask_history": {
        "en": {
            "label": "Mask history",
            "info": "Train on the last turn only (only for SFT).",
        },
        "ru": {
            "label": "История масок",
            "info": "Тренироваться только на последнем шаге (только для SFT).",
        },
        "zh": {
            "label": "不学习历史对话",
            "info": "仅学习最后一轮对话（仅适用于 SFT）。",
        },
        "ko": {
            "label": "히스토리 마스킹",
            "info": "대화 데이터의 마지막 턴만 학습합니다 (SFT에만 해당).",
        },
        "ja": {
            "label": "履歴をマスク",
            "info": "最後のターンのみを学習する（SFT のみ）。",
        },
    },
    "resize_vocab": {
        "en": {
            "label": "Resize token embeddings",
            "info": "Resize the tokenizer vocab and the embedding layers.",
        },
        "ru": {
            "label": "Изменение размера токенных эмбеддингов",
            "info": "Изменить размер словаря токенизатора и слоев эмбеддинга.",
        },
        "zh": {
            "label": "更改词表大小",
            "info": "更改分词器词表和嵌入层的大小。",
        },
        "ko": {
            "label": "토큰 임베딩의 사이즈 조정",
            "info": "토크나이저 어휘와 임베딩 레이어의 크기를 조정합니다.",
        },
        "ja": {
            "label": "トークン埋め込みのサイズ変更",
            "info": "トークナイザーの語彙と埋め込み層のサイズを変更します。",
        },
    },
    "use_llama_pro": {
        "en": {
            "label": "Enable LLaMA Pro",
            "info": "Make the parameters in the expanded blocks trainable.",
        },
        "ru": {
            "label": "Включить LLaMA Pro",
            "info": "Сделать параметры в расширенных блоках обучаемыми.",
        },
        "zh": {
            "label": "使用 LLaMA Pro",
            "info": "仅训练块扩展后的参数。",
        },
        "ko": {
            "label": "LLaMA Pro 사용",
            "info": "확장된 블록의 매개변수를 학습 가능하게 만듭니다.",
        },
        "ja": {
            "label": "LLaMA Pro を有効化",
            "info": "拡張ブロックのパラメータのみをトレーニングします。",
        },
    },
    "enable_thinking": {
        "en": {
            "label": "Enable thinking",
            "info": "Whether or not to enable thinking mode for reasoning models.",
        },
        "ru": {
            "label": "Включить мысли",
            "info": "Включить режим мысли для моделей решающего характера.",
        },
        "zh": {
            "label": "启用思考模式",
            "info": "是否启用推理模型的思考模式。",
        },
        "ko": {
            "label": "생각 모드 활성화",
            "info": "추론 모델의 생각 모드를 활성화할지 여부.",
        },
        "ja": {
            "label": "思考モードを有効化",
            "info": "推論モデルの思考モードを有効にするかどうか。",
        },
    },
    "report_to": {
        "en": {
            "label": "Enable external logger",
            "info": "Use TensorBoard or wandb to log experiment.",
        },
        "ru": {
            "label": "Включить внешний регистратор",
            "info": "Использовать TensorBoard или wandb для ведения журнала экспериментов.",
        },
        "zh": {
            "label": "启用外部记录面板",
            "info": "使用 TensorBoard 或 wandb 记录实验。",
        },
        "ko": {
            "label": "외부 logger 활성화",
            "info": "TensorBoard 또는 wandb를 사용하여 실험을 기록합니다.",
        },
        "ja": {
            "label": "外部ロガーを有効化",
            "info": "TensorBoard または wandb を使用して実験を記録します。",
        },
    },
    "freeze_tab": {
        "en": {
            "label": "Freeze tuning configurations",
        },
        "ru": {
            "label": "конфигурации для настройки заморозки",
        },
        "zh": {
            "label": "部分参数微调设置",
        },
        "ko": {
            "label": "Freeze tuning 설정",
        },
        "ja": {
            "label": "フリーズチューニング設定",
        },
    },
    "freeze_trainable_layers": {
        "en": {
            "label": "Trainable layers",
            "info": "Number of the last(+)/first(-) hidden layers to be set as trainable.",
        },
        "ru": {
            "label": "Обучаемые слои",
            "info": "Количество последних (+)/первых (-) скрытых слоев, которые будут установлены как обучаемые.",
        },
        "zh": {
            "label": "可训练层数",
            "info": "最末尾（+）/最前端（-）可训练隐藏层的数量。",
        },
        "ko": {
            "label": "학습 가능한 레이어",
            "info": "학습 가능하게 설정할 마지막(+)/처음(-) 히든 레이어의 수.",
        },
        "ja": {
            "label": "学習可能なレイヤー",
            "info": "最後（+）/最初（-）の学習可能な隠れ層の数。",
        },
    },
    "freeze_trainable_modules": {
        "en": {
            "label": "Trainable modules",
            "info": "Name(s) of trainable modules. Use commas to separate multiple modules.",
        },
        "ru": {
            "label": "Обучаемые модули",
            "info": "Название обучаемых модулей. Используйте запятые для разделения нескольких модулей.",
        },
        "zh": {
            "label": "可训练模块",
            "info": "可训练模块的名称。使用英文逗号分隔多个名称。",
        },
        "ko": {
            "label": "학습 가능한 모듈",
            "info": "학습 가능한 모듈의 이름. 여러 모듈을 구분하려면 쉼표(,)를 사용하세요.",
        },
        "ja": {
            "label": "学習可能なモジュール",
            "info": "学習可能なモジュールの名前。複数のモジュールを区切るにはカンマを使用します。",
        },
    },
    "freeze_extra_modules": {
        "en": {
            "label": "Extra modules (optional)",
            "info": (
                "Name(s) of modules apart from hidden layers to be set as trainable. "
                "Use commas to separate multiple modules."
            ),
        },
        "ru": {
            "label": "Дополнительные модули (опционально)",
            "info": (
                "Имена модулей, кроме скрытых слоев, которые следует установить в качестве обучаемых. "
                "Используйте запятые для разделения нескольких модулей."
            ),
        },
        "zh": {
            "label": "额外模块（非必填）",
            "info": "除隐藏层以外的可训练模块名称。使用英文逗号分隔多个名称。",
        },
        "ko": {
            "label": "추가 모듈 (선택 사항)",
            "info": "히든 레이어 외에 학습 가능하게 설정할 모듈의 이름. 모듈 간에는 쉼표(,)로 구분하십시오.",
        },
        "ja": {
            "label": "追加モジュール（オプション）",
            "info": "隠れ層以外の学習可能なモジュールの名前。複数のモジュールを区切るにはカンマを使用します。",
        },
    },
    "lora_tab": {
        "en": {
            "label": "LoRA configurations",
        },
        "ru": {
            "label": "Конфигурации LoRA",
        },
        "zh": {
            "label": "LoRA 参数设置",
        },
        "ko": {
            "label": "LoRA 구성",
        },
        "ja": {
            "label": "LoRA 設定",
        },
    },
    "lora_rank": {
        "en": {
            "label": "LoRA rank",
            "info": "The rank of LoRA matrices.",
        },
        "ru": {
            "label": "Ранг матриц LoRA",
            "info": "Ранг матриц LoRA.",
        },
        "zh": {
            "label": "LoRA 秩",
            "info": "LoRA 矩阵的秩大小。",
        },
        "ko": {
            "label": "LoRA 랭크",
            "info": "LoRA 행렬의 랭크.",
        },
        "ja": {
            "label": "LoRA ランク",
            "info": "LoRA 行列のランク。",
        },
    },
    "lora_alpha": {
        "en": {
            "label": "LoRA alpha",
            "info": "Lora scaling coefficient.",
        },
        "ru": {
            "label": "LoRA alpha",
            "info": "Коэффициент масштабирования LoRA.",
        },
        "zh": {
            "label": "LoRA 缩放系数",
            "info": "LoRA 缩放系数大小。",
        },
        "ko": {
            "label": "LoRA 알파",
            "info": "LoRA 스케일링 계수.",
        },
        "ja": {
            "label": "LoRA alpha",
            "info": "LoRA スケーリング係数。",
        },
    },
    "lora_dropout": {
        "en": {
            "label": "LoRA dropout",
            "info": "Dropout ratio of LoRA weights.",
        },
        "ru": {
            "label": "Вероятность отсева LoRA",
            "info": "Вероятность отсева весов LoRA.",
        },
        "zh": {
            "label": "LoRA 随机丢弃",
            "info": "LoRA 权重随机丢弃的概率。",
        },
        "ko": {
            "label": "LoRA 드롭아웃",
            "info": "LoRA 가중치의 드롭아웃 비율.",
        },
        "ja": {
            "label": "LoRA ドロップアウト",
            "info": "LoRA 重みのドロップアウト確率。",
        },
    },
    "loraplus_lr_ratio": {
        "en": {
            "label": "LoRA+ LR ratio",
            "info": "The LR ratio of the B matrices in LoRA.",
        },
        "ru": {
            "label": "LoRA+ LR коэффициент",
            "info": "Коэффициент LR матриц B в LoRA.",
        },
        "zh": {
            "label": "LoRA+ 学习率比例",
            "info": "LoRA+ 中 B 矩阵的学习率倍数。",
        },
        "ko": {
            "label": "LoRA+ LR 비율",
            "info": "LoRA에서 B 행렬의 LR 비율.",
        },
        "ja": {
            "label": "LoRA+ LR 比率",
            "info": "LoRA+ の B 行列の学習率倍率。",
        },
    },
    "create_new_adapter": {
        "en": {
            "label": "Create new adapter",
            "info": "Create a new adapter with randomly initialized weight upon the existing one.",
        },
        "ru": {
            "label": "Создать новый адаптер",
            "info": "Создать новый адаптер с случайной инициализацией веса на основе существующего.",
        },
        "zh": {
            "label": "新建适配器",
            "info": "在现有的适配器上创建一个随机初始化后的新适配器。",
        },
        "ko": {
            "label": "새 어댑터 생성",
            "info": "기존 어댑터 위에 무작위로 초기화된 가중치를 가진 새 어댑터를 생성합니다.",
        },
        "ja": {
            "label": "新しいアダプターを作成",
            "info": "既存のアダプター上にランダムに初期化された新しいアダプターを作成します。",
        },
    },
    "use_rslora": {
        "en": {
            "label": "Use rslora",
            "info": "Use the rank stabilization scaling factor for LoRA layer.",
        },
        "ru": {
            "label": "Использовать rslora",
            "info": "Использовать коэффициент масштабирования стабилизации ранга для слоя LoRA.",
        },
        "zh": {
            "label": "使用 rslora",
            "info": "对 LoRA 层使用秩稳定缩放方法。",
        },
        "ko": {
            "label": "rslora 사용",
            "info": "LoRA 레이어에 랭크 안정화 스케일링 계수를 사용합니다.",
        },
        "ja": {
            "label": "rslora を使用",
            "info": "LoRA 層にランク安定化スケーリング方法を使用します。",
        },
    },
    "use_dora": {
        "en": {
            "label": "Use DoRA",
            "info": "Use weight-decomposed LoRA.",
        },
        "ru": {
            "label": "Используйте DoRA",
            "info": "Используйте LoRA с декомпозицией весов.",
        },
        "zh": {
            "label": "使用 DoRA",
            "info": "使用权重分解的 LoRA。",
        },
        "ko": {
            "label": "DoRA 사용",
            "info": "가중치-분해 LoRA를 사용합니다.",
        },
        "ja": {
            "label": "DoRA を使用",
            "info": "重み分解された LoRA を使用します。",
        },
    },
    "use_pissa": {
        "en": {
            "label": "Use PiSSA",
            "info": "Use PiSSA method.",
        },
        "ru": {
            "label": "используйте PiSSA",
            "info": "Используйте метод PiSSA.",
        },
        "zh": {
            "label": "使用 PiSSA",
            "info": "使用 PiSSA 方法。",
        },
        "ko": {
            "label": "PiSSA 사용",
            "info": "PiSSA 방법을 사용합니다.",
        },
        "ja": {
            "label": "PiSSA を使用",
            "info": "PiSSA メソッドを使用します。",
        },
    },
    "lora_target": {
        "en": {
            "label": "LoRA modules (optional)",
            "info": "Name(s) of modules to apply LoRA. Use commas to separate multiple modules.",
        },
        "ru": {
            "label": "Модули LoRA (опционально)",
            "info": "Имена модулей для применения LoRA. Используйте запятые для разделения нескольких модулей.",
        },
        "zh": {
            "label": "LoRA 作用模块（非必填）",
            "info": "应用 LoRA 的模块名称。使用英文逗号分隔多个名称。",
        },
        "ko": {
            "label": "LoRA 모듈 (선택 사항)",
            "info": "LoRA를 적용할 모듈의 이름. 모듈 간에는 쉼표(,)로 구분하십시오.",
        },
        "ja": {
            "label": "LoRA モジュール（オプション）",
            "info": "LoRA を適用するモジュールの名前。複数のモジュールを区切るにはカンマを使用します。",
        },
    },
    "additional_target": {
        "en": {
            "label": "Additional modules (optional)",
            "info": (
                "Name(s) of modules apart from LoRA layers to be set as trainable. "
                "Use commas to separate multiple modules."
            ),
        },
        "ru": {
            "label": "Дополнительные модули (опционально)",
            "info": (
                "Имена модулей, кроме слоев LoRA, которые следует установить в качестве обучаемых. "
                "Используйте запятые для разделения нескольких модулей."
            ),
        },
        "zh": {
            "label": "附加模块（非必填）",
            "info": "除 LoRA 层以外的可训练模块名称。使用英文逗号分隔多个名称。",
        },
        "ko": {
            "label": "추가 모듈 (선택 사항)",
            "info": "LoRA 레이어 외에 학습 가능하게 설정할 모듈의 이름. 모듈 간에는 쉼표(,)로 구분하십시오.",
        },
        "ja": {
            "label": "追加モジュール（オプション）",
            "info": "LoRA 層以外の学習可能なモジュールの名前。複数のモジュールを区切るにはカンマを使用します。",
        },
    },
    "rlhf_tab": {
        "en": {
            "label": "RLHF configurations",
        },
        "ru": {
            "label": "Конфигурации RLHF",
        },
        "zh": {
            "label": "RLHF 参数设置",
        },
        "ko": {
            "label": "RLHF 구성",
        },
        "ja": {
            "label": "RLHF 設定",
        },
    },
    "pref_beta": {
        "en": {
            "label": "Beta value",
            "info": "Value of the beta parameter in the loss.",
        },
        "ru": {
            "label": "Бета значение",
            "info": "Значение параметра бета в функции потерь.",
        },
        "zh": {
            "label": "Beta 参数",
            "info": "损失函数中 beta 超参数大小。",
        },
        "ko": {
            "label": "베타 값",
            "info": "손실 함수에서 베타 매개 변수의 값.",
        },
        "ja": {
            "label": "Beta 値",
            "info": "損失関数における beta ハイパーパラメータの値。",
        },
    },
    "pref_ftx": {
        "en": {
            "label": "Ftx gamma",
            "info": "The weight of SFT loss in the final loss.",
        },
        "ru": {
            "label": "Ftx гамма",
            "info": "Вес потери SFT в итоговой потере.",
        },
        "zh": {
            "label": "Ftx gamma",
            "info": "损失函数中 SFT 损失的权重大小。",
        },
        "ko": {
            "label": "Ftx 감마",
            "info": "최종 로스 함수에서 SFT 로스의 가중치.",
        },
        "ja": {
            "label": "Ftx gamma",
            "info": "損失関数における SFT 損失の重み。",
        },
    },
    "pref_loss": {
        "en": {
            "label": "Loss type",
            "info": "The type of the loss function.",
        },
        "ru": {
            "label": "Тип потерь",
            "info": "Тип функции потерь.",
        },
        "zh": {
            "label": "损失类型",
            "info": "损失函数的类型。",
        },
        "ko": {
            "label": "로스 유형",
            "info": "로스 함수의 유형.",
        },
        "ja": {
            "label": "損失タイプ",
            "info": "損失関数のタイプ。",
        },
    },
    "reward_model": {
        "en": {
            "label": "Reward model",
            "info": "Adapter of the reward model in PPO training.",
        },
        "ru": {
            "label": "Модель вознаграждения",
            "info": "Адаптер модели вознаграждения для обучения PPO.",
        },
        "zh": {
            "label": "奖励模型",
            "info": "PPO 训练中奖励模型的适配器路径。",
        },
        "ko": {
            "label": "리워드 모델",
            "info": "PPO 학습에서 사용할 리워드 모델의 어댑터.",
        },
        "ja": {
            "label": "報酬モデル",
            "info": "PPO トレーニングにおける報酬モデルのアダプター。",
        },
    },
    "ppo_score_norm": {
        "en": {
            "label": "Score norm",
            "info": "Normalizing scores in PPO training.",
        },
        "ru": {
            "label": "Норма оценок",
            "info": "Нормализация оценок в тренировке PPO.",
        },
        "zh": {
            "label": "归一化分数",
            "info": "PPO 训练中归一化奖励分数。",
        },
        "ko": {
            "label": "스코어 정규화",
            "info": "PPO 학습에서 스코어를 정규화합니다.",
        },
        "ja": {
            "label": "スコア正規化",
            "info": "PPO トレーニングにおける報酬スコアの正規化。",
        },
    },
    "ppo_whiten_rewards": {
        "en": {
            "label": "Whiten rewards",
            "info": "Whiten the rewards in PPO training.",
        },
        "ru": {
            "label": "Белые вознаграждения",
            "info": "Осветлите вознаграждения в обучении PPO.",
        },
        "zh": {
            "label": "白化奖励",
            "info": "PPO 训练中将奖励分数做白化处理。",
        },
        "ko": {
            "label": "보상 백화",
            "info": "PPO 훈련에서 보상을 백화(Whiten)합니다.",
        },
        "ja": {
            "label": "報酬のホワイトニング",
            "info": "PPO トレーニングにおいて報酬スコアをホワイトニング処理します。",
        },
    },
    "mm_tab": {
        "en": {
            "label": "Multimodal configurations",
        },
        "ru": {
            "label": "Конфигурации мультимедиа",
        },
        "zh": {
            "label": "多模态参数设置",
        },
        "ko": {
            "label": "멀티모달 구성",
        },
        "ja": {
            "label": "多モーダル設定",
        },
    },
    "freeze_vision_tower": {
        "en": {
            "label": "Freeze vision tower",
            "info": "Freeze the vision tower in the model.",
        },
        "ru": {
            "label": "Заморозить башню визиона",
            "info": "Заморозить башню визиона в модели.",
        },
        "zh": {
            "label": "冻结视觉编码器",
            "info": "冻结模型中的视觉编码器。",
        },
        "ko": {
            "label": "비전 타워 고정",
            "info": "모델의 비전 타워를 고정합니다.",
        },
        "ja": {
            "label": "ビジョンタワーの固定",
            "info": "モデルのビジョンタワーを固定します。",
        },
    },
    "freeze_multi_modal_projector": {
        "en": {
            "label": "Freeze multi-modal projector",
            "info": "Freeze the multi-modal projector in the model.",
        },
        "ru": {
            "label": "Заморозить мультимодальный проектор",
            "info": "Заморозить мультимодальный проектор в модели.",
        },
        "zh": {
            "label": "冻结多模态投影器",
            "info": "冻结模型中的多模态投影器。",
        },
        "ko": {
            "label": "멀티모달 프로젝터 고정",
            "info": "모델의 멀티모달 프로젝터를 고정합니다.",
        },
        "ja": {
            "label": "多モーダルプロジェクターの固定",
            "info": "モデルの多モーダルプロジェクターを固定します。",
        },
    },
    "freeze_language_model": {
        "en": {
            "label": "Freeze language model",
            "info": "Freeze the language model in the model.",
        },
        "ru": {
            "label": "Заморозить язык модели",
            "info": "Заморозить язык модели в модели.",
        },
        "zh": {
            "label": "冻结语言模型",
            "info": "冻结模型中的语言模型。",
        },
        "ko": {
            "label": "언어 모델 고정",
            "info": "모델의 언어 모델을 고정합니다.",
        },
        "ja": {
            "label": "言語モデルの固定",
            "info": "モデルの言語モデルを固定します。",
        },
    },
    "image_max_pixels": {
        "en": {
            "label": "Image max pixels",
            "info": "The maximum number of pixels of image inputs.",
        },
        "ru": {
            "label": "Максимальное количество пикселей изображения",
            "info": "Максимальное количество пикселей изображения.",
        },
        "zh": {
            "label": "图像最大像素",
            "info": "输入图像的最大像素数。",
        },
        "ko": {
            "label": "이미지 최대 픽셀",
            "info": "이미지 입력의 최대 픽셀 수입니다.",
        },
        "ja": {
            "label": "画像最大ピクセル",
            "info": "画像入力の最大ピクセル数です。",
        },
    },
    "image_min_pixels": {
        "en": {
            "label": "Image min pixels",
            "info": "The minimum number of pixels of image inputs.",
        },
        "ru": {
            "label": "Минимальное количество пикселей изображения",
            "info": "Минимальное количество пикселей изображения.",
        },
        "zh": {
            "label": "图像最小像素",
            "info": "输入图像的最小像素数。",
        },
        "ko": {
            "label": "이미지 최소 픽셀",
            "info": "이미지 입력의 최소 픽셀 수입니다.",
        },
        "ja": {
            "label": "画像最小ピクセル",
            "info": "画像入力の最小ピクセル数です。",
        },
    },
    "video_max_pixels": {
        "en": {
            "label": "Video max pixels",
            "info": "The maximum number of pixels of video inputs.",
        },
        "ru": {
            "label": "Максимальное количество пикселей видео",
            "info": "Максимальное количество пикселей видео.",
        },
        "zh": {
            "label": "视频最大像素",
            "info": "输入视频的最大像素数。",
        },
        "ko": {
            "label": "비디오 최대 픽셀",
            "info": "비디오 입력의 최대 픽셀 수입니다.",
        },
        "ja": {
            "label": "ビデオ最大ピクセル",
            "info": "ビデオ入力の最大ピクセル数です。",
        },
    },
    "video_min_pixels": {
        "en": {
            "label": "Video min pixels",
            "info": "The minimum number of pixels of video inputs.",
        },
        "ru": {
            "label": "Минимальное количество пикселей видео",
            "info": "Минимальное количество пикселей видео.",
        },
        "zh": {
            "label": "视频最小像素",
            "info": "输入视频的最小像素数。",
        },
        "ko": {
            "label": "비디오 최소 픽셀",
            "info": "비디오 입력의 최소 픽셀 수입니다.",
        },
        "ja": {
            "label": "ビデオ最小ピクセル",
            "info": "ビデオ入力の最小ピクセル数です。",
        },
    },
    "galore_tab": {
        "en": {
            "label": "GaLore configurations",
        },
        "ru": {
            "label": "Конфигурации GaLore",
        },
        "zh": {
            "label": "GaLore 参数设置",
        },
        "ko": {
            "label": "GaLore 구성",
        },
        "ja": {
            "label": "GaLore 設定",
        },
    },
    "use_galore": {
        "en": {
            "label": "Use GaLore",
            "info": "Use [GaLore](https://github.com/jiaweizzhao/GaLore) optimizer.",
        },
        "ru": {
            "label": "Использовать GaLore",
            "info": "Используйте оптимизатор [GaLore](https://github.com/jiaweizzhao/GaLore).",
        },
        "zh": {
            "label": "使用 GaLore",
            "info": "使用 [GaLore](https://github.com/jiaweizzhao/GaLore) 优化器。",
        },
        "ko": {
            "label": "GaLore 사용",
            "info": "[GaLore](https://github.com/jiaweizzhao/GaLore) 최적화를 사용하세요.",
        },
        "ja": {
            "label": "GaLore を使用",
            "info": "[GaLore](https://github.com/jiaweizzhao/GaLore) オプティマイザーを使用します。",
        },
    },
    "galore_rank": {
        "en": {
            "label": "GaLore rank",
            "info": "The rank of GaLore gradients.",
        },
        "ru": {
            "label": "Ранг GaLore",
            "info": "Ранг градиентов GaLore.",
        },
        "zh": {
            "label": "GaLore 秩",
            "info": "GaLore 梯度的秩大小。",
        },
        "ko": {
            "label": "GaLore 랭크",
            "info": "GaLore 그레디언트의 랭크.",
        },
        "ja": {
            "label": "GaLore ランク",
            "info": "GaLore 勾配のランク。",
        },
    },
    "galore_update_interval": {
        "en": {
            "label": "Update interval",
            "info": "Number of steps to update the GaLore projection.",
        },
        "ru": {
            "label": "Интервал обновления",
            "info": "Количество шагов для обновления проекции GaLore.",
        },
        "zh": {
            "label": "更新间隔",
            "info": "相邻两次投影更新的步数。",
        },
        "ko": {
            "label": "업데이트 간격",
            "info": "GaLore 프로젝션을 업데이트할 간격의 스텝 수.",
        },
        "ja": {
            "label": "更新間隔",
            "info": "隣接する 2 回の投影更新間のステップ数。",
        },
    },
    "galore_scale": {
        "en": {
            "label": "GaLore scale",
            "info": "GaLore scaling coefficient.",
        },
        "ru": {
            "label": "LoRA Alpha",
            "info": "Коэффициент масштабирования GaLore.",
        },
        "zh": {
            "label": "GaLore 缩放系数",
            "info": "GaLore 缩放系数大小。",
        },
        "ko": {
            "label": "GaLore 스케일",
            "info": "GaLore 스케일링 계수.",
        },
        "ja": {
            "label": "GaLore スケール",
            "info": "GaLore スケーリング係数。",
        },
    },
    "galore_target": {
        "en": {
            "label": "GaLore modules",
            "info": "Name(s) of modules to apply GaLore. Use commas to separate multiple modules.",
        },
        "ru": {
            "label": "Модули GaLore",
            "info": "Имена модулей для применения GaLore. Используйте запятые для разделения нескольких модулей.",
        },
        "zh": {
            "label": "GaLore 作用模块",
            "info": "应用 GaLore 的模块名称。使用英文逗号分隔多个名称。",
        },
        "ko": {
            "label": "GaLore 모듈",
            "info": "GaLore를 적용할 모듈의 이름. 모듈 간에는 쉼표(,)로 구분하십시오.",
        },
        "ja": {
            "label": "GaLore モジュール",
            "info": "GaLore を適用するモジュールの名前。複数のモジュールを区切るにはカンマを使用します。",
        },
    },
    "apollo_tab": {
        "en": {
            "label": "APOLLO configurations",
        },
        "ru": {
            "label": "Конфигурации APOLLO",
        },
        "zh": {
            "label": "APOLLO 参数设置",
        },
        "ko": {
            "label": "APOLLO 구성",
        },
        "ja": {
            "label": "APOLLO 設定",
        },
    },
    "use_apollo": {
        "en": {
            "label": "Use APOLLO",
            "info": "Use [APOLLO](https://github.com/zhuhanqing/APOLLO) optimizer.",
        },
        "ru": {
            "label": "Использовать APOLLO",
            "info": "Используйте оптимизатор [APOLLO](https://github.com/zhuhanqing/APOLLO).",
        },
        "zh": {
            "label": "使用 APOLLO",
            "info": "使用 [APOLLO](https://github.com/zhuhanqing/APOLLO) 优化器。",
        },
        "ko": {
            "label": "APOLLO 사용",
            "info": "[APOLLO](https://github.com/zhuhanqing/APOLLO) 최적화를 사용하세요.",
        },
        "ja": {
            "label": "APOLLO を使用",
            "info": "[APOLLO](https://github.com/zhuhanqing/APOLLO) オプティマイザーを使用します。",
        },
    },
    "apollo_rank": {
        "en": {
            "label": "APOLLO rank",
            "info": "The rank of APOLLO gradients.",
        },
        "ru": {
            "label": "Ранг APOLLO",
            "info": "Ранг градиентов APOLLO.",
        },
        "zh": {
            "label": "APOLLO 秩",
            "info": "APOLLO 梯度的秩大小。",
        },
        "ko": {
            "label": "APOLLO 랭크",
            "info": "APOLLO 그레디언트의 랭크.",
        },
        "ja": {
            "label": "APOLLO ランク",
            "info": "APOLLO 勾配のランク。",
        },
    },
    "apollo_update_interval": {
        "en": {
            "label": "Update interval",
            "info": "Number of steps to update the APOLLO projection.",
        },
        "ru": {
            "label": "Интервал обновления",
            "info": "Количество шагов для обновления проекции APOLLO.",
        },
        "zh": {
            "label": "更新间隔",
            "info": "相邻两次投影更新的步数。",
        },
        "ko": {
            "label": "업데이트 간격",
            "info": "APOLLO 프로젝션을 업데이트할 간격의 스텝 수.",
        },
        "ja": {
            "label": "更新間隔",
            "info": "隣接する 2 回の投影更新間のステップ数。",
        },
    },
    "apollo_scale": {
        "en": {
            "label": "APOLLO scale",
            "info": "APOLLO scaling coefficient.",
        },
        "ru": {
            "label": "LoRA Alpha",
            "info": "Коэффициент масштабирования APOLLO.",
        },
        "zh": {
            "label": "APOLLO 缩放系数",
            "info": "APOLLO 缩放系数大小。",
        },
        "ko": {
            "label": "APOLLO 스케일",
            "info": "APOLLO 스케일링 계수.",
        },
        "ja": {
            "label": "APOLLO スケール",
            "info": "APOLLO スケーリング係数。",
        },
    },
    "apollo_target": {
        "en": {
            "label": "APOLLO modules",
            "info": "Name(s) of modules to apply APOLLO. Use commas to separate multiple modules.",
        },
        "ru": {
            "label": "Модули APOLLO",
            "info": "Имена модулей для применения APOLLO. Используйте запятые для разделения нескольких модулей.",
        },
        "zh": {
            "label": "APOLLO 作用模块",
            "info": "应用 APOLLO 的模块名称。使用英文逗号分隔多个名称。",
        },
        "ko": {
            "label": "APOLLO 모듈",
            "info": "APOLLO를 적용할 모듈의 이름. 모듈 간에는 쉼표(,)로 구분하십시오.",
        },
        "ja": {
            "label": "APOLLO モジュール",
            "info": "APOLLO を適用するモジュールの名前。複数のモジュールを区切るにはカンマを使用します。",
        },
    },
    "badam_tab": {
        "en": {
            "label": "BAdam configurations",
        },
        "ru": {
            "label": "Конфигурации BAdam",
        },
        "zh": {
            "label": "BAdam 参数设置",
        },
        "ko": {
            "label": "BAdam 설정",
        },
        "ja": {
            "label": "BAdam 設定",
        },
    },
    "use_badam": {
        "en": {
            "label": "Use BAdam",
            "info": "Enable the [BAdam](https://github.com/Ledzy/BAdam) optimizer.",
        },
        "ru": {
            "label": "Использовать BAdam",
            "info": "Включите оптимизатор [BAdam](https://github.com/Ledzy/BAdam).",
        },
        "zh": {
            "label": "使用 BAdam",
            "info": "使用 [BAdam](https://github.com/Ledzy/BAdam) 优化器。",
        },
        "ko": {
            "label": "BAdam 사용",
            "info": "[BAdam](https://github.com/Ledzy/BAdam) 옵티마이저를 사용합니다.",
        },
        "ja": {
            "label": "BAdam を使用",
            "info": "[BAdam](https://github.com/Ledzy/BAdam) オプティマイザーを使用します。",
        },
    },
    "badam_mode": {
        "en": {
            "label": "BAdam mode",
            "info": "Whether to use layer-wise or ratio-wise BAdam optimizer.",
        },
        "ru": {
            "label": "Режим BAdam",
            "info": "Использовать ли оптимизатор BAdam с послоевой или пропорциональной настройкой.",
        },
        "zh": {
            "label": "BAdam 模式",
            "info": "使用 layer-wise 或 ratio-wise BAdam 优化器。",
        },
        "ko": {
            "label": "BAdam 모드",
            "info": "레이어-BAdam 옵티마이저인지 비율-BAdam 옵티마이저인지.",
        },
        "ja": {
            "label": "BAdam モード",
            "info": "layer-wise または ratio-wise BAdam オプティマイザーを使用します。",
        },
    },
    "badam_switch_mode": {
        "en": {
            "label": "Switch mode",
            "info": "The strategy of picking block to update for layer-wise BAdam.",
        },
        "ru": {
            "label": "Режим переключения",
            "info": "Стратегия выбора блока для обновления для послойного BAdam.",
        },
        "zh": {
            "label": "切换策略",
            "info": "Layer-wise BAdam 优化器的块切换策略。",
        },
        "ko": {
            "label": "스위치 모드",
            "info": "레이어-BAdam을 위한 블록 선택 전략.",
        },
        "ja": {
            "label": "切り替え戦略",
            "info": "Layer-wise BAdam オプティマイザーのブロック切り替え戦略。",
        },
    },
    "badam_switch_interval": {
        "en": {
            "label": "Switch interval",
            "info": "Number of steps to update the block for layer-wise BAdam.",
        },
        "ru": {
            "label": "Интервал переключения",
            "info": "количество шагов для обновления блока для пошагового BAdam.",
        },
        "zh": {
            "label": "切换频率",
            "info": "Layer-wise BAdam 优化器的块切换频率。",
        },
        "ko": {
            "label": "전환 간격",
            "info": "레이어-BAdam을 위한 블록 업데이트 간 스텝 수.",
        },
        "ja": {
            "label": "切り替え頻度",
            "info": "Layer-wise BAdam オプティマイザーのブロック切り替え頻度。",
        },
    },
    "badam_update_ratio": {
        "en": {
            "label": "Update ratio",
            "info": "The ratio of the update for ratio-wise BAdam.",
        },
        "ru": {
            "label": "Коэффициент обновления",
            "info": "Коэффициент обновления для BAdam с учётом соотношений.",
        },
        "zh": {
            "label": "Block 更新比例",
            "info": "Ratio-wise BAdam 优化器的更新比例。",
        },
        "ko": {
            "label": "업데이트 비율",
            "info": "비율-BAdam의 업데이트 비율.",
        },
        "ja": {
            "label": "ブロック更新比率",
            "info": "Ratio-wise BAdam オプティマイザーの更新比率。",
        },
    },
    "swanlab_tab": {
        "en": {
            "label": "SwanLab configurations",
        },
        "ru": {
            "label": "Конфигурации SwanLab",
        },
        "zh": {
            "label": "SwanLab 参数设置",
        },
        "ko": {
            "label": "SwanLab 설정",
        },
        "ja": {
            "label": "SwanLab 設定",
        },
    },
    "use_swanlab": {
        "en": {
            "label": "Use SwanLab",
            "info": "Enable [SwanLab](https://swanlab.cn/) for experiment tracking and visualization.",
        },
        "ru": {
            "label": "Использовать SwanLab",
            "info": "Включить [SwanLab](https://swanlab.cn/) для отслеживания и визуализации экспериментов.",
        },
        "zh": {
            "label": "使用 SwanLab",
            "info": "启用 [SwanLab](https://swanlab.cn/) 进行实验跟踪和可视化。",
        },
        "ko": {
            "label": "SwanLab 사용",
            "info": "[SwanLab](https://swanlab.cn/) 를 사용하여 실험을 추적하고 시각화합니다.",
        },
        "ja": {
            "label": "SwanLab を使用",
            "info": "[SwanLab](https://swanlab.cn/) を有効にして実験の追跡と可視化を行います。",
        },
    },
    "swanlab_project": {
        "en": {
            "label": "SwanLab project",
        },
        "ru": {
            "label": "SwanLab Проект",
        },
        "zh": {
            "label": "SwanLab 项目名",
        },
        "ko": {
            "label": "SwanLab 프로젝트",
        },
        "ja": {
            "label": "SwanLab プロジェクト",
        },
    },
    "swanlab_run_name": {
        "en": {
            "label": "SwanLab experiment name (optional)",
        },
        "ru": {
            "label": "SwanLab Имя эксперимента (опционально)",
        },
        "zh": {
            "label": "SwanLab 实验名（非必填）",
        },
        "ko": {
            "label": "SwanLab 실험 이름 (선택 사항)",
        },
        "ja": {
            "label": "SwanLab 実験名（オプション）",
        },
    },
    "swanlab_workspace": {
        "en": {
            "label": "SwanLab workspace (optional)",
            "info": "Workspace for SwanLab. Defaults to the personal workspace.",
        },
        "ru": {
            "label": "SwanLab Рабочая область (опционально)",
            "info": "Рабочая область SwanLab, если не заполнено, то по умолчанию в личной рабочей области.",
        },
        "zh": {
            "label": "SwanLab 工作区（非必填）",
            "info": "SwanLab 的工作区，默认在个人工作区下。",
        },
        "ko": {
            "label": "SwanLab 작업 영역 (선택 사항)",
            "info": "SwanLab 조직의 작업 영역, 비어 있으면 기본적으로 개인 작업 영역에 있습니다.",
        },
        "ja": {
            "label": "SwanLab ワークスペース（オプション）",
            "info": "SwanLab のワークスペース。デフォルトでは個人ワークスペースです。",
        },
    },
    "swanlab_api_key": {
        "en": {
            "label": "SwanLab API key (optional)",
            "info": "API key for SwanLab.",
        },
        "ru": {
            "label": "SwanLab API ключ (опционально)",
            "info": "API ключ для SwanLab.",
        },
        "zh": {
            "label": "SwanLab API 密钥（非必填）",
            "info": "用于在编程环境登录 SwanLab，已登录则无需填写。",
        },
        "ko": {
            "label": "SwanLab API 키 (선택 사항)",
            "info": "SwanLab의 API 키.",
        },
        "ja": {
            "label": "SwanLab API キー（オプション）",
            "info": "SwanLab の API キー。",
        },
    },
    "swanlab_mode": {
        "en": {
            "label": "SwanLab mode",
            "info": "Cloud or offline version.",
        },
        "ru": {
            "label": "SwanLab Режим",
            "info": "Версия в облаке или локальная версия.",
        },
        "zh": {
            "label": "SwanLab 模式",
            "info": "使用云端版或离线版 SwanLab。",
        },
        "ko": {
            "label": "SwanLab 모드",
            "info": "클라우드 버전 또는 오프라인 버전.",
        },
        "ja": {
            "label": "SwanLab モード",
            "info": "クラウド版またはオフライン版 SwanLab を使用します。",
        },
    },
    "swanlab_logdir": {
        "en": {
            "label": "SwanLab log directory",
            "info": "The log directory for SwanLab.",
        },
        "ru": {
            "label": "SwanLab 로그 디렉토리",
            "info": "SwanLab의 로그 디렉토리.",
        },
        "zh": {
            "label": "SwanLab 日志目录",
            "info": "SwanLab 的日志目录。",
        },
        "ko": {
            "label": "SwanLab 로그 디렉토리",
            "info": "SwanLab의 로그 디렉토리.",
        },
        "ja": {
            "label": "SwanLab ログ ディレクトリ",
            "info": "SwanLab のログ ディレクトリ。",
        },
    },
    "cmd_preview_btn": {
        "en": {
            "value": "Preview command",
        },
        "ru": {
            "value": "Просмотр команды",
        },
        "zh": {
            "value": "预览命令",
        },
        "ko": {
            "value": "명령어 미리보기",
        },
        "ja": {
            "value": "コマンドをプレビュー",
        },
    },
    "arg_save_btn": {
        "en": {
            "value": "Save arguments",
        },
        "ru": {
            "value": "Сохранить аргументы",
        },
        "zh": {
            "value": "保存训练参数",
        },
        "ko": {
            "value": "Argument 저장",
        },
        "ja": {
            "value": "引数を保存",
        },
    },
    "arg_load_btn": {
        "en": {
            "value": "Load arguments",
        },
        "ru": {
            "value": "Загрузить аргументы",
        },
        "zh": {
            "value": "载入训练参数",
        },
        "ko": {
            "value": "Argument 불러오기",
        },
        "ja": {
            "value": "引数を読み込む",
        },
    },
    "start_btn": {
        "en": {
            "value": "Start",
        },
        "ru": {
            "value": "Начать",
        },
        "zh": {
            "value": "开始",
        },
        "ko": {
            "value": "시작",
        },
        "ja": {
            "value": "開始",
        },
    },
    "stop_btn": {
        "en": {
            "value": "Abort",
        },
        "ru": {
            "value": "Прервать",
        },
        "zh": {
            "value": "中断",
        },
        "ko": {
            "value": "중단",
        },
        "ja": {
            "value": "中断",
        },
    },
    "output_dir": {
        "en": {
            "label": "Output dir",
            "info": "Directory for saving results.",
        },
        "ru": {
            "label": "Выходной каталог",
            "info": "Каталог для сохранения результатов.",
        },
        "zh": {
            "label": "输出目录",
            "info": "保存结果的路径。",
        },
        "ko": {
            "label": "출력 디렉토리",
            "info": "결과를 저장할 디렉토리.",
        },
        "ja": {
            "label": "出力ディレクトリ",
            "info": "結果を保存するパス。",
        },
    },
    "config_path": {
        "en": {
            "label": "Config path",
            "info": "Path to config saving arguments.",
        },
        "ru": {
            "label": "Путь к конфигурации",
            "info": "Путь для сохранения аргументов конфигурации.",
        },
        "zh": {
            "label": "配置路径",
            "info": "保存训练参数的配置文件路径。",
        },
        "ko": {
            "label": "설정 경로",
            "info": "Arguments 저장 파일 경로.",
        },
        "ja": {
            "label": "設定パス",
            "info": "トレーニングパラメータを保存する設定ファイルのパス。",
        },
    },
    "device_count": {
        "en": {
            "label": "Device count",
            "info": "Number of devices available.",
        },
        "ru": {
            "label": "Количество устройств",
            "info": "Количество доступных устройств.",
        },
        "zh": {
            "label": "设备数量",
            "info": "当前可用的运算设备数。",
        },
        "ko": {
            "label": "디바이스 수",
            "info": "사용 가능한 디바이스 수.",
        },
        "ja": {
            "label": "デバイス数",
            "info": "現在利用可能な演算デバイス数。",
        },
    },
    "ds_stage": {
        "en": {
            "label": "DeepSpeed stage",
            "info": "DeepSpeed stage for distributed training.",
        },
        "ru": {
            "label": "Этап DeepSpeed",
            "info": "Этап DeepSpeed для распределенного обучения.",
        },
        "zh": {
            "label": "DeepSpeed stage",
            "info": "多卡训练的 DeepSpeed stage。",
        },
        "ko": {
            "label": "DeepSpeed 단계",
            "info": "분산 학습을 위한 DeepSpeed 단계.",
        },
        "ja": {
            "label": "DeepSpeed stage",
            "info": "マルチ GPU トレーニングの DeepSpeed stage。",
        },
    },
    "ds_offload": {
        "en": {
            "label": "Enable offload",
            "info": "Enable DeepSpeed offload (slow down training).",
        },
        "ru": {
            "label": "Включить выгрузку",
            "info": "включить выгрузку DeepSpeed (замедлит обучение).",
        },
        "zh": {
            "label": "使用 offload",
            "info": "使用 DeepSpeed offload（会减慢速度）。",
        },
        "ko": {
            "label": "오프로딩 활성화",
            "info": "DeepSpeed 오프로딩 활성화 (훈련 속도 느려짐).",
        },
        "ja": {
            "label": "オフロードを使用",
            "info": "DeepSpeed オフロードを使用します（速度が遅くなります）。",
        },
    },
    "output_box": {
        "en": {
            "value": "Ready.",
        },
        "ru": {
            "value": "Готово.",
        },
        "zh": {
            "value": "准备就绪。",
        },
        "ko": {
            "value": "준비 완료.",
        },
        "ja": {
            "value": "準備完了。",
        },
    },
    "loss_viewer": {
        "en": {
            "label": "Loss",
        },
        "ru": {
            "label": "Потери",
        },
        "zh": {
            "label": "损失",
        },
        "ko": {
            "label": "손실",
        },
        "ja": {
            "label": "損失",
        },
    },
    "predict": {
        "en": {
            "label": "Save predictions",
        },
        "ru": {
            "label": "Сохранить предсказания",
        },
        "zh": {
            "label": "保存预测结果",
        },
        "ko": {
            "label": "예측 결과 저장",
        },
        "ja": {
            "label": "予測結果を保存",
        },
    },
    "infer_backend": {
        "en": {
            "label": "Inference engine",
        },
        "ru": {
            "label": "Инференс движок",
        },
        "zh": {
            "label": "推理引擎",
        },
        "ko": {
            "label": "추론 엔진",
        },
        "ja": {
            "label": "推論エンジン",
        },
    },
    "infer_dtype": {
        "en": {
            "label": "Inference data type",
        },
        "ru": {
            "label": "Тип данных для вывода",
        },
        "zh": {
            "label": "推理数据类型",
        },
        "ko": {
            "label": "추론 데이터 유형",
        },
        "ja": {
            "label": "推論データタイプ",
        },
    },
    "load_btn": {
        "en": {
            "value": "Load model",
        },
        "ru": {
            "value": "Загрузить модель",
        },
        "zh": {
            "value": "加载模型",
        },
        "ko": {
            "value": "모델 불러오기",
        },
        "ja": {
            "value": "モデルを読み込む",
        },
    },
    "unload_btn": {
        "en": {
            "value": "Unload model",
        },
        "ru": {
            "value": "Выгрузить модель",
        },
        "zh": {
            "value": "卸载模型",
        },
        "ko": {
            "value": "모델 언로드",
        },
        "ja": {
            "value": "モデルをアンロード",
        },
    },
    "info_box": {
        "en": {
            "value": "Model unloaded, please load a model first.",
        },
        "ru": {
            "value": "Модель не загружена, загрузите модель сначала.",
        },
        "zh": {
            "value": "模型未加载，请先加载模型。",
        },
        "ko": {
            "value": "모델이 언로드되었습니다. 모델을 먼저 불러오십시오.",
        },
        "ja": {
            "value": "モデルがロードされていません。最初にモデルをロードしてください。",
        },
    },
    "role": {
        "en": {
            "label": "Role",
        },
        "ru": {
            "label": "Роль",
        },
        "zh": {
            "label": "角色",
        },
        "ko": {
            "label": "역할",
        },
        "ja": {
            "label": "役割",
        },
    },
    "system": {
        "en": {
            "placeholder": "System prompt (optional)",
        },
        "ru": {
            "placeholder": "Системный запрос (по желанию)",
        },
        "zh": {
            "placeholder": "系统提示词（非必填）",
        },
        "ko": {
            "placeholder": "시스템 프롬프트 (선택 사항)",
        },
        "ja": {
            "placeholder": "システムプロンプト（オプション）",
        },
    },
    "tools": {
        "en": {
            "placeholder": "Tools (optional)",
        },
        "ru": {
            "placeholder": "Инструменты (по желанию)",
        },
        "zh": {
            "placeholder": "工具列表（非必填）",
        },
        "ko": {
            "placeholder": "툴 (선택 사항)",
        },
        "ja": {
            "placeholder": "ツールリスト（オプション）",
        },
    },
    "image": {
        "en": {
            "label": "Image (optional)",
        },
        "ru": {
            "label": "Изображение (по желанию)",
        },
        "zh": {
            "label": "图像（非必填）",
        },
        "ko": {
            "label": "이미지 (선택 사항)",
        },
        "ja": {
            "label": "画像（オプション）",
        },
    },
    "video": {
        "en": {
            "label": "Video (optional)",
        },
        "ru": {
            "label": "Видео (по желанию)",
        },
        "zh": {
            "label": "视频（非必填）",
        },
        "ko": {
            "label": "비디오 (선택 사항)",
        },
        "ja": {
            "label": "動画（オプション）",
        },
    },
    "query": {
        "en": {
            "placeholder": "Input...",
        },
        "ru": {
            "placeholder": "Ввод...",
        },
        "zh": {
            "placeholder": "输入...",
        },
        "ko": {
            "placeholder": "입력...",
        },
        "ja": {
            "placeholder": "入力...",
        },
    },
    "submit_btn": {
        "en": {
            "value": "Submit",
        },
        "ru": {
            "value": "Отправить",
        },
        "zh": {
            "value": "提交",
        },
        "ko": {
            "value": "제출",
        },
        "ja": {
            "value": "送信",
        },
    },
    "max_length": {
        "en": {
            "label": "Maximum length",
        },
        "ru": {
            "label": "Максимальная длина",
        },
        "zh": {
            "label": "最大长度",
        },
        "ko": {
            "label": "최대 길이",
        },
        "ja": {
            "label": "最大長",
        },
    },
    "max_new_tokens": {
        "en": {
            "label": "Maximum new tokens",
        },
        "ru": {
            "label": "Максимальное количество новых токенов",
        },
        "zh": {
            "label": "最大生成长度",
        },
        "ko": {
            "label": "응답의 최대 길이",
        },
        "ja": {
            "label": "最大生成長",
        },
    },
    "top_p": {
        "en": {
            "label": "Top-p",
        },
        "ru": {
            "label": "Лучшие-p",
        },
        "zh": {
            "label": "Top-p 采样值",
        },
        "ko": {
            "label": "Top-p",
        },
        "ja": {
            "label": "Top-p",
        },
    },
    "temperature": {
        "en": {
            "label": "Temperature",
        },
        "ru": {
            "label": "Температура",
        },
        "zh": {
            "label": "温度系数",
        },
        "ko": {
            "label": "온도",
        },
        "ja": {
            "label": "温度",
        },
    },
    "seed": {
        "en": {
            "label": "Generation seed (-1 for random)",
        },
        "ru": {
            "label": "Generation seed (-1 = random)",
        },
        "zh": {
            "label": "生成随机种子（-1 表示随机）",
        },
        "ko": {
            "label": "Generation seed (-1 = random)",
        },
        "ja": {
            "label": "Generation seed (-1 = random)",
        },
    },
    "eval_seed": {
        "en": {
            "label": "Seed",
            "info": "Random seed for evaluation and prediction.",
        },
        "ru": {
            "label": "Seed",
            "info": "Random seed for evaluation and prediction.",
        },
        "zh": {
            "label": "随机种子",
            "info": "评估和预测使用的随机种子。",
        },
        "ko": {
            "label": "Seed",
            "info": "Random seed for evaluation and prediction.",
        },
        "ja": {
            "label": "Seed",
            "info": "Random seed for evaluation and prediction.",
        },
    },
    "skip_special_tokens": {
        "en": {
            "label": "Skip special tokens",
        },
        "ru": {
            "label": "Пропустить специальные токены",
        },
        "zh": {
            "label": "跳过特殊 token",
        },
        "ko": {
            "label": "스페셜 토큰을 건너뛰기",
        },
        "ja": {
            "label": "スペシャルトークンをスキップ",
        },
    },
    "escape_html": {
        "en": {
            "label": "Escape HTML tags",
        },
        "ru": {
            "label": "Исключить HTML теги",
        },
        "zh": {
            "label": "转义 HTML 标签",
        },
        "ko": {
            "label": "HTML 태그 이스케이프",
        },
        "ja": {
            "label": "HTML タグをエスケープ",
        },
    },
    "clear_btn": {
        "en": {
            "value": "Clear history",
        },
        "ru": {
            "value": "Очистить историю",
        },
        "zh": {
            "value": "清空历史",
        },
        "ko": {
            "value": "기록 지우기",
        },
        "ja": {
            "value": "履歴をクリア",
        },
    },
    "export_size": {
        "en": {
            "label": "Max shard size (GB)",
            "info": "The maximum size for a model file.",
        },
        "ru": {
            "label": "Максимальный размер фрагмента (ГБ)",
            "info": "Максимальный размер файла модели.",
        },
        "zh": {
            "label": "最大分块大小（GB）",
            "info": "单个模型文件的最大大小。",
        },
        "ko": {
            "label": "최대 샤드 크기 (GB)",
            "info": "모델 파일의 최대 크기.",
        },
        "ja": {
            "label": "最大シャードサイズ（GB）",
            "info": "単一のモデルファイルの最大サイズ。",
        },
    },
    "export_quantization_bit": {
        "en": {
            "label": "Export quantization bit.",
            "info": "Quantizing the exported model.",
        },
        "ru": {
            "label": "Экспорт бита квантования",
            "info": "Квантование экспортируемой модели.",
        },
        "zh": {
            "label": "导出量化等级",
            "info": "量化导出模型。",
        },
        "ko": {
            "label": "양자화 비트 내보내기",
            "info": "내보낸 모델의 양자화.",
        },
        "ja": {
            "label": "量子化ビットをエクスポート",
            "info": "エクスポートするモデルを量子化します。",
        },
    },
    "export_quantization_dataset": {
        "en": {
            "label": "Export quantization dataset",
            "info": "The calibration dataset used for quantization.",
        },
        "ru": {
            "label": "Экспорт набора данных для квантования",
            "info": "Набор данных калибровки, используемый для квантования.",
        },
        "zh": {
            "label": "导出量化数据集",
            "info": "量化过程中使用的校准数据集。",
        },
        "ko": {
            "label": "양자화 데이터셋 내보내기",
            "info": "양자화에 사용되는 교정 데이터셋.",
        },
        "ja": {
            "label": "量子化データセットをエクスポート",
            "info": "量子化プロセスで使用されるキャリブレーションデータセット。",
        },
    },
    "export_device": {
        "en": {
            "label": "Export device",
            "info": "Which device should be used to export model.",
        },
        "ru": {
            "label": "Экспорт устройство",
            "info": "Какое устройство следует использовать для экспорта модели.",
        },
        "zh": {
            "label": "导出设备",
            "info": "导出模型使用的设备类型。",
        },
        "ko": {
            "label": "내보낼 장치",
            "info": "모델을 내보내는 데 사용할 장치.",
        },
        "ja": {
            "label": "エクスポートデバイス",
            "info": "モデルをエクスポートするために使用するデバイスタイプ。",
        },
    },
    "export_legacy_format": {
        "en": {
            "label": "Export legacy format",
            "info": "Do not use safetensors to save the model.",
        },
        "ru": {
            "label": "Экспорт в устаревший формат",
            "info": "Не использовать safetensors для сохранения модели.",
        },
        "zh": {
            "label": "导出旧格式",
            "info": "不使用 safetensors 格式保存模型。",
        },
        "ko": {
            "label": "레거시 형식 내보내기",
            "info": "모델을 저장하는 데 safetensors를 사용하지 않습니다.",
        },
        "ja": {
            "label": "レガシーフォーマットをエクスポート",
            "info": "safetensors フォーマットを使用せずにモデルを保存します。",
        },
    },
    "export_dir": {
        "en": {
            "label": "Export dir",
            "info": "Directory to save exported model.",
        },
        "ru": {
            "label": "Каталог экспорта",
            "info": "Каталог для сохранения экспортированной модели.",
        },
        "zh": {
            "label": "导出目录",
            "info": "保存导出模型的文件夹路径。",
        },
        "ko": {
            "label": "내보내기 디렉토리",
            "info": "내보낸 모델을 저장할 디렉토리.",
        },
        "ja": {
            "label": "エクスポートディレクトリ",
            "info": "エクスポートしたモデルを保存するフォルダのパス。",
        },
    },
    "export_btn": {
        "en": {
            "value": "Export",
        },
        "ru": {
            "value": "Экспорт",
        },
        "zh": {
            "value": "开始导出",
        },
        "ko": {
            "value": "내보내기",
        },
        "ja": {
            "value": "エクスポート",
        },
    },
    "device_memory": {
        "en": {
            "label": "Device memory",
            "info": "Current memory usage of the device (GB).",
        },
        "ru": {
            "label": "Память устройства",
            "info": "Текущая память на устройстве (GB).",
        },
        "zh": {
            "label": "设备显存",
            "info": "当前设备的显存（GB）。",
        },
        "ko": {
            "label": "디바이스 메모리",
            "info": "지금 사용 중인 기기 메모리 (GB).",
        },
        "ja": {
            "label": "デバイスメモリ",
            "info": "現在のデバイスのメモリ（GB）。",
        },
    },
}


_WIZARD_TRANSLATIONS = {
    "en": {
        "steps": ("Model & goal", "Dataset", "Optional adjustments", "Safety check"),
        "hero_kicker": "GUIDED SETUP",
        "hero_title": "Start training in four guided steps",
        "hero_description": (
            "Choose a local model and dataset, accept or adjust the generated settings, "
            "then pass the VRAM safety check."
        ),
        "headers": (
            (
                "Choose a local model and training goal",
                "Enter the model directory and desired outcome. Hardware is detected and the starting configuration is generated automatically.",
            ),
            (
                "Choose the training dataset",
                "The training mode already follows your goal. Select a dataset and preview a sample before continuing.",
            ),
            (
                "Adjust only what matters",
                "Use the generated configuration unchanged, or open one focused branch for resources or learning quality.",
            ),
            (
                "Run the safety check and start",
                "Confirm the output directory, review the configuration, and check available VRAM before training.",
            ),
        ),
        "model_card": (
            "### 1. Local model directory\n"
            "Enter a directory already present on this machine. The system reads config.json and totals the model weight files automatically."
        ),
        "environment_card": (
            "### 2. Results and compute environment\n"
            "The output directory and configuration filename are generated automatically and remain editable."
        ),
        "data_guide": (
            "### Choose and verify the data\n"
            "- Only datasets compatible with the goal from Step 1 are listed.\n"
            "- Preview a sample now; for the first run, begin with a small dataset."
        ),
        "recommendation_title": "RECOMMENDED BASELINE",
        "recommendation_value": "LoRA / QLoRA",
        "recommendation_description": (
            "Start with a learning rate of 5e-5. If memory is insufficient, reduce the per-device batch size or "
            "sequence length first, then increase gradient accumulation to preserve the effective batch size."
        ),
        "core_params": (
            "### Core parameters\nThese settings have the largest impact on speed, memory usage, and convergence."
        ),
        "launch_card": (
            "### Save and check\n"
            "Choose where to save the result. The final configuration is saved with the run automatically."
        ),
        "buttons": (
            "Next: choose dataset  →",
            "←  Back: model & goal",
            "Next: review settings  →",
            "←  Back: dataset",
            "Next: review configuration  →",
            "←  Back: adjustments",
        ),
        "accordions": (
            "Advanced training parameters (optional)",
            "Freeze tuning parameters",
            "LoRA parameters",
            "Preference training / RLHF parameters",
            "Multimodal parameters",
            "GaLore parameters",
            "APOLLO parameters",
            "BAdam parameters",
            "SwanLab parameters",
        ),
    },
    "ru": {
        "steps": ("Модель и цель", "Данные", "Настройки", "Проверка безопасности"),
        "hero_kicker": "ПОШАГОВАЯ НАСТРОЙКА",
        "hero_title": "Запустите обучение за четыре понятных шага",
        "hero_description": (
            "Выберите локальную модель и данные, примите или измените созданные параметры, затем проверьте видеопамять."
        ),
        "headers": (
            (
                "Выберите локальную модель и цель",
                "Укажите каталог модели и желаемый результат. Оборудование определяется, а начальные параметры создаются автоматически.",
            ),
            (
                "Выберите набор данных",
                "Режим обучения уже определён по цели. Выберите набор данных и просмотрите пример.",
            ),
            (
                "Измените только нужные параметры",
                "Оставьте созданную конфигурацию или откройте одну ветку: ресурсы либо качество обучения.",
            ),
            (
                "Проверьте безопасность и запустите обучение",
                "Подтвердите каталог результатов, конфигурацию и доступную видеопамять.",
            ),
        ),
        "model_card": (
            "### 1. Локальный каталог модели\n"
            "Укажите каталог, уже находящийся на этом компьютере. Система прочитает config.json и автоматически суммирует файлы весов."
        ),
        "environment_card": (
            "### 2. Результаты и вычислительная среда\n"
            "Каталог результатов и имя конфигурации создаются автоматически, но их можно изменить."
        ),
        "data_guide": (
            "### Выберите и проверьте данные\n"
            "- Показаны только наборы данных, совместимые с целью из первого шага.\n"
            "- Просмотрите пример; для первого запуска используйте небольшой набор."
        ),
        "recommendation_title": "РЕКОМЕНДУЕМЫЕ НАСТРОЙКИ",
        "recommendation_value": "LoRA / QLoRA",
        "recommendation_description": (
            "Начните со скорости обучения 5e-5. При нехватке памяти сначала уменьшите размер пакета или длину "
            "последовательности, затем увеличьте накопление градиента."
        ),
        "core_params": ("### Основные параметры\nОни сильнее всего влияют на скорость, расход памяти и сходимость."),
        "launch_card": (
            "### Сохранение и проверка\n"
            "Выберите каталог результатов. Итоговая конфигурация будет автоматически сохранена вместе с запуском."
        ),
        "buttons": (
            "Далее: выбрать данные  →",
            "←  Назад: модель и цель",
            "Далее: проверить настройки  →",
            "←  Назад: данные",
            "Далее: проверить конфигурацию  →",
            "←  Назад: настройки",
        ),
        "accordions": (
            "Расширенные параметры обучения (необязательно)",
            "Параметры замороженного обучения",
            "Параметры LoRA",
            "Параметры предпочтений / RLHF",
            "Параметры мультимодальности",
            "Параметры GaLore",
            "Параметры APOLLO",
            "Параметры BAdam",
            "Параметры SwanLab",
        ),
    },
    "zh": {
        "steps": ("模型与目标", "选择数据", "按需调整", "安全检查"),
        "hero_kicker": "分步配置",
        "hero_title": "四步完成配置并开始训练",
        "hero_description": ("选择本地模型和数据，确认或修改自动生成的配置，再通过训练前显存安全检查。"),
        "headers": (
            (
                "选择本地模型与训练目标",
                "填写模型目录并选择期望效果。系统会自动检测硬件并生成起始配置。",
            ),
            (
                "选择训练数据",
                "训练方式已经根据目标自动确定。请选择数据集，并在继续前预览样本。",
            ),
            (
                "只调整真正需要的参数",
                "可以直接使用自动配置，也可以只打开显存与速度或学习质量中的一个分支。",
            ),
            (
                "完成安全检查并启动训练",
                "确认输出目录和最终配置，系统会在启动前检查当前可用显存。",
            ),
        ),
        "model_card": (
            "### 1. 本地模型目录\n填写本机已经存在的模型目录。系统会读取 config.json，并自动汇总模型权重文件大小。"
        ),
        "environment_card": ("### 2. 结果保存与计算环境\n输出目录和配置文件会自动按当前时间生成，也可以手动修改。"),
        "data_guide": (
            "### 选择并检查数据\n"
            "- 页面只列出与第 1 步训练目标匹配的数据集。\n"
            "- 请先预览样本；首次运行建议使用小数据集。"
        ),
        "recommendation_title": "推荐起点",
        "recommendation_value": "LoRA / QLoRA",
        "recommendation_description": (
            "学习率可从 5e-5 开始；显存不足时先降低单卡批次或序列长度，再增加梯度累积保持有效批次。"
        ),
        "core_params": "### 核心参数\n这些参数最直接地影响训练速度、显存和收敛效果。",
        "launch_card": ("### 保存并检查\n选择结果保存位置；最终训练配置会随任务自动保存。"),
        "buttons": (
            "下一步：选择数据  →",
            "←  上一步：模型与目标",
            "下一步：确认参数  →",
            "←  上一步：选择数据",
            "下一步：确认配置  →",
            "←  上一步：按需调整",
        ),
        "accordions": (
            "高级训练参数（可选）",
            "冻结微调参数",
            "LoRA 参数",
            "偏好训练 / RLHF 参数",
            "多模态参数",
            "GaLore 参数",
            "APOLLO 参数",
            "BAdam 参数",
            "SwanLab 参数",
        ),
    },
    "ko": {
        "steps": ("모델 및 목표", "데이터", "선택 조정", "안전 확인"),
        "hero_kicker": "단계별 설정",
        "hero_title": "네 단계로 설정하고 학습 시작",
        "hero_description": (
            "로컬 모델과 데이터를 선택하고 자동 구성을 확인하거나 수정한 뒤 GPU 메모리 안전 검사를 실행합니다."
        ),
        "headers": (
            (
                "로컬 모델 및 목표 선택",
                "모델 디렉터리와 원하는 결과를 선택하세요. 하드웨어와 시작 구성은 자동으로 결정됩니다.",
            ),
            (
                "학습 데이터 선택",
                "학습 방식은 목표에 따라 이미 설정되었습니다. 데이터셋을 선택하고 샘플을 미리 보세요.",
            ),
            ("필요한 항목만 조정", "자동 구성을 그대로 사용하거나 리소스 또는 학습 품질 중 한 가지만 조정하세요."),
            (
                "안전 확인 후 학습 시작",
                "출력 디렉터리와 구성을 확인하고 학습 전에 사용 가능한 GPU 메모리를 검사하세요.",
            ),
        ),
        "model_card": (
            "### 1. 로컬 모델 디렉터리\n"
            "이 컴퓨터에 이미 있는 디렉터리를 입력하세요. 시스템이 config.json을 읽고 모델 가중치 파일 크기를 자동으로 합산합니다."
        ),
        "environment_card": (
            "### 2. 결과 및 컴퓨팅 환경\n출력 디렉터리와 설정 파일명은 자동 생성되며 수정할 수 있습니다."
        ),
        "data_guide": (
            "### 데이터 선택 및 확인\n"
            "- 1단계 목표와 호환되는 데이터셋만 표시됩니다.\n"
            "- 샘플을 미리 보고, 첫 실행에는 작은 데이터셋을 사용하세요."
        ),
        "recommendation_title": "권장 기준값",
        "recommendation_value": "LoRA / QLoRA",
        "recommendation_description": (
            "학습률 5e-5에서 시작하세요. 메모리가 부족하면 장치별 배치나 시퀀스 길이를 먼저 줄이고 "
            "그래디언트 누적을 늘려 유효 배치를 유지하세요."
        ),
        "core_params": "### 핵심 파라미터\n속도, 메모리 사용량 및 수렴에 가장 큰 영향을 줍니다.",
        "launch_card": ("### 저장 및 확인\n결과 디렉터리를 선택하세요. 최종 구성은 실행과 함께 자동 저장됩니다."),
        "buttons": (
            "다음: 데이터 선택  →",
            "←  이전: 모델 및 목표",
            "다음: 설정 확인  →",
            "←  이전: 데이터",
            "다음: 설정 검토  →",
            "←  이전: 선택 조정",
        ),
        "accordions": (
            "고급 학습 파라미터(선택)",
            "동결 튜닝 파라미터",
            "LoRA 파라미터",
            "선호 학습 / RLHF 파라미터",
            "멀티모달 파라미터",
            "GaLore 파라미터",
            "APOLLO 파라미터",
            "BAdam 파라미터",
            "SwanLab 파라미터",
        ),
    },
    "ja": {
        "steps": ("モデルと目的", "データ", "必要な調整", "安全確認"),
        "hero_kicker": "ガイド付きセットアップ",
        "hero_title": "4 ステップで設定して学習を開始",
        "hero_description": (
            "ローカルモデルとデータを選び、自動構成を確認または修正してから GPU メモリの安全確認を行います。"
        ),
        "headers": (
            (
                "ローカルモデルと目的を選択",
                "モデルディレクトリと目的を選びます。ハードウェアと初期構成は自動的に決まります。",
            ),
            ("学習データを選択", "学習方式は目的に応じて設定済みです。データセットを選び、サンプルを確認します。"),
            ("必要な項目だけ調整", "自動構成をそのまま使うか、リソースまたは学習品質の一方だけを調整します。"),
            (
                "安全確認後に学習を開始",
                "出力先と構成を確認し、学習前に利用可能な GPU メモリを検査します。",
            ),
        ),
        "model_card": (
            "### 1. ローカルモデルディレクトリ\n"
            "このコンピューターに既に存在するディレクトリを入力してください。config.json を読み取り、モデル重みファイルのサイズを自動集計します。"
        ),
        "environment_card": (
            "### 2. 結果と計算環境\n出力先と設定ファイル名は自動生成され、必要に応じて変更できます。"
        ),
        "data_guide": (
            "### データを選択して確認\n"
            "- ステップ 1 の目的に対応するデータセットだけが表示されます。\n"
            "- サンプルを確認し、初回は小さなデータセットから始めてください。"
        ),
        "recommendation_title": "推奨設定",
        "recommendation_value": "LoRA / QLoRA",
        "recommendation_description": (
            "学習率 5e-5 から始めます。メモリ不足の場合は、デバイスごとのバッチまたは系列長を先に下げ、"
            "勾配累積を増やして有効バッチを維持します。"
        ),
        "core_params": "### 主要パラメータ\n速度、メモリ使用量、収束に最も大きく影響します。",
        "launch_card": ("### 保存と確認\n出力先を選択します。最終構成は実行時に自動保存されます。"),
        "buttons": (
            "次へ：データを選択  →",
            "←  戻る：モデルと目的",
            "次へ：設定を確認  →",
            "←  戻る：データ",
            "次へ：設定を確認  →",
            "←  戻る：必要な調整",
        ),
        "accordions": (
            "高度な学習パラメータ（任意）",
            "Freeze チューニングパラメータ",
            "LoRA パラメータ",
            "選好学習 / RLHF パラメータ",
            "マルチモーダルパラメータ",
            "GaLore パラメータ",
            "APOLLO パラメータ",
            "BAdam パラメータ",
            "SwanLab パラメータ",
        ),
    },
}


def _build_wizard_hero(lang: str) -> str:
    text = _WIZARD_TRANSLATIONS[lang]
    return (
        '<section class="oobe-hero">'
        f'<div class="oobe-kicker">{text["hero_kicker"]}</div>'
        f"<h1>{text['hero_title']}</h1><p>{text['hero_description']}</p>"
        "</section>"
    )


def _build_wizard_header(lang: str, step: int) -> str:
    text = _WIZARD_TRANSLATIONS[lang]
    step_items = []
    for index, label in enumerate(text["steps"], start=1):
        state = "is-active" if index == step else "is-done" if index < step else ""
        step_items.append(
            f'<div class="oobe-step {state}"><span class="oobe-step-number">{index}</span>'
            f'<span class="oobe-step-label">{label}</span></div>'
        )

    title, description = text["headers"][step - 1]
    return (
        '<section class="oobe-page-header">'
        f'<div class="oobe-kicker">{step} / {len(text["steps"])}</div>'
        f"<h2>{title}</h2><p>{description}</p>"
        f'<div class="oobe-stepper">{"".join(step_items)}</div>'
        "</section>"
    )


LOCALES.update(
    {
        "wizard_hero": {lang: {"value": _build_wizard_hero(lang)} for lang in _WIZARD_TRANSLATIONS},
        **{
            f"wizard_header_{step}": {
                lang: {"value": _build_wizard_header(lang, step)} for lang in _WIZARD_TRANSLATIONS
            }
            for step in range(1, 5)
        },
        "wizard_model_card": {lang: {"value": text["model_card"]} for lang, text in _WIZARD_TRANSLATIONS.items()},
        "wizard_data_guide": {lang: {"value": text["data_guide"]} for lang, text in _WIZARD_TRANSLATIONS.items()},
        "wizard_launch_card": {lang: {"value": text["launch_card"]} for lang, text in _WIZARD_TRANSLATIONS.items()},
        **{
            key: {lang: {"value": text["buttons"][index]} for lang, text in _WIZARD_TRANSLATIONS.items()}
            for index, key in enumerate(
                (
                    "wizard_model_next_btn",
                    "wizard_data_back_btn",
                    "wizard_data_next_btn",
                    "wizard_params_back_btn",
                    "wizard_params_next_btn",
                    "wizard_review_back_btn",
                )
            )
        },
    }
)


WIZARD_SUMMARY_LOCALES = {
    "en": {
        "missing_model": "Not selected",
        "missing_path": "Not provided",
        "missing_dataset": "Not selected",
        "missing_output": "Not provided",
        "no_quantization": "No quantization",
        "quantization": "{bit}-bit QLoRA",
        "title": "Configuration summary",
        "subtitle": "Review these settings before starting training",
        "labels": ("Model", "Finetuning", "Training task", "Learning", "Batch", "Sequence & precision", "Output"),
        "learning": "LR {learning_rate} · {epochs} epochs",
        "batch": "Per-device {batch_size} × accumulation {accumulation} = effective batch {effective_batch}",
        "sequence": "{cutoff_len} tokens · {compute_type}",
        "stages": {
            "Supervised Fine-Tuning": "Supervised fine-tuning",
            "Reward Modeling": "Reward modeling",
            "PPO": "PPO",
            "DPO": "DPO",
            "KTO": "KTO",
            "Pre-Training": "Pre-training",
        },
    },
    "ru": {
        "missing_model": "Не выбрано",
        "missing_path": "Не указано",
        "missing_dataset": "Не выбрано",
        "missing_output": "Не указано",
        "no_quantization": "Без квантования",
        "quantization": "QLoRA, {bit} бит",
        "title": "Сводка конфигурации",
        "subtitle": "Проверьте параметры перед запуском обучения",
        "labels": (
            "Модель",
            "Дообучение",
            "Задача",
            "Обучение",
            "Пакет",
            "Последовательность и точность",
            "Результаты",
        ),
        "learning": "LR {learning_rate} · эпох: {epochs}",
        "batch": "На устройство {batch_size} × накопление {accumulation} = эффективный пакет {effective_batch}",
        "sequence": "{cutoff_len} токенов · {compute_type}",
        "stages": {
            "Supervised Fine-Tuning": "Обучение по инструкциям",
            "Reward Modeling": "Обучение модели награды",
            "PPO": "PPO",
            "DPO": "DPO",
            "KTO": "KTO",
            "Pre-Training": "Предварительное обучение",
        },
    },
    "zh": {
        "missing_model": "尚未选择",
        "missing_path": "尚未填写",
        "missing_dataset": "尚未选择",
        "missing_output": "尚未填写",
        "no_quantization": "不量化",
        "quantization": "{bit}-bit QLoRA",
        "title": "配置摘要",
        "subtitle": "请确认后再启动训练",
        "labels": ("模型", "微调方案", "训练任务", "学习设置", "批处理", "序列与精度", "输出目录"),
        "learning": "学习率 {learning_rate} · {epochs} 个周期",
        "batch": "单卡 {batch_size} × 累积 {accumulation} = 有效批次 {effective_batch}",
        "sequence": "{cutoff_len} tokens · {compute_type}",
        "stages": {
            "Supervised Fine-Tuning": "监督微调",
            "Reward Modeling": "奖励模型训练",
            "PPO": "PPO",
            "DPO": "DPO",
            "KTO": "KTO",
            "Pre-Training": "预训练",
        },
    },
    "ko": {
        "missing_model": "선택하지 않음",
        "missing_path": "입력하지 않음",
        "missing_dataset": "선택하지 않음",
        "missing_output": "입력하지 않음",
        "no_quantization": "양자화 없음",
        "quantization": "{bit}-bit QLoRA",
        "title": "설정 요약",
        "subtitle": "학습을 시작하기 전에 설정을 확인하세요",
        "labels": ("모델", "파인튜닝", "학습 작업", "학습 설정", "배치", "시퀀스 및 정밀도", "출력"),
        "learning": "학습률 {learning_rate} · {epochs} 에폭",
        "batch": "장치별 {batch_size} × 누적 {accumulation} = 유효 배치 {effective_batch}",
        "sequence": "{cutoff_len} 토큰 · {compute_type}",
        "stages": {
            "Supervised Fine-Tuning": "지도 미세 조정",
            "Reward Modeling": "보상 모델 학습",
            "PPO": "PPO",
            "DPO": "DPO",
            "KTO": "KTO",
            "Pre-Training": "사전 학습",
        },
    },
    "ja": {
        "missing_model": "未選択",
        "missing_path": "未入力",
        "missing_dataset": "未選択",
        "missing_output": "未入力",
        "no_quantization": "量子化なし",
        "quantization": "{bit}-bit QLoRA",
        "title": "設定の概要",
        "subtitle": "学習を開始する前に設定を確認してください",
        "labels": ("モデル", "ファインチューニング", "学習タスク", "学習設定", "バッチ", "系列と精度", "出力先"),
        "learning": "学習率 {learning_rate} · {epochs} エポック",
        "batch": "デバイスごと {batch_size} × 累積 {accumulation} = 有効バッチ {effective_batch}",
        "sequence": "{cutoff_len} トークン · {compute_type}",
        "stages": {
            "Supervised Fine-Tuning": "教師ありファインチューニング",
            "Reward Modeling": "報酬モデル学習",
            "PPO": "PPO",
            "DPO": "DPO",
            "KTO": "KTO",
            "Pre-Training": "事前学習",
        },
    },
}


WIZARD_GUIDANCE_LOCALES = {
    "en": {
        "questionnaire": "### Tell us what you want to train\nChoose the goal and priority. Hardware is detected automatically and the starting configuration updates immediately.",
        "goal_label": "What do you want the model to learn?",
        "goal_info": "Choose the outcome closest to your use case.",
        "goal_choices": (
            ("Follow instructions and answer questions", "instruction"),
            ("Prefer better answers", "preference"),
            ("Continue learning from raw text", "pretrain"),
        ),
        "hardware_label": "How much GPU memory is available?",
        "hardware_info": "Choose the memory of one GPU. Select multi-GPU only when distributed training is configured.",
        "hardware_choices": (
            ("8 GB or less", "low"),
            ("12–16 GB", "mid"),
            ("24–48 GB", "high"),
            ("Multi-GPU / 80 GB+", "multi"),
        ),
        "priority_label": "What should the system prioritize?",
        "priority_info": "Balanced is recommended for the first run.",
        "params_guide": "### Choose only what you want to change\nThe recommended configuration is already complete. Select one branch below; unrelated parameters stay hidden.",
        "param_mode_label": "What do you want to adjust?",
        "param_mode_info": "The branch suggested by your earlier priority is selected automatically.",
        "param_mode_choices": (
            ("Nothing — use the recommendation", "recommended"),
            ("GPU memory and training speed", "resources"),
            ("Learning quality and convergence", "learning"),
        ),
        "resource_params_guide": "### GPU memory and speed\nOnly the four settings that directly affect peak VRAM and throughput are shown.",
        "learning_params_guide": "### Learning quality and convergence\nAdjust the learning schedule without exposing infrastructure or expert options.",
        "show_advanced_label": "I want to manually adjust the generated parameters",
        "show_advanced_info": "Optional. Turning this on exposes technical and expert settings.",
        "priority_choices": (
            ("Balanced and reliable", "balanced"),
            ("Use less GPU memory", "memory"),
            ("Train faster", "speed"),
            ("Maximum quality", "quality"),
        ),
        "apply_button": "Generate my recommended configuration",
        "manual_settings": "Model-specific settings (optional)",
        "result_title": "Recommended configuration applied",
        "result_intro": "These values are a safe starting point for the selected goal and hardware.",
        "result_labels": (
            "Local weight files",
            "Method",
            "Quantization",
            "Precision",
            "Sequence",
            "Effective batch",
        ),
        "weight_size": "{value:.2f} GiB",
        "none": "None",
        "tokens": "{value} tokens",
        "effective_batch": "{value} samples",
        "reason_balanced": "Balanced mode keeps memory use predictable while preserving training stability.",
        "reason_memory": "Memory-saving mode uses smaller batches and 4-bit loading where supported.",
        "reason_speed": "Speed mode increases device batch size when the selected hardware has room.",
        "reason_quality": "Quality mode preserves precision and context length when the selected hardware can support it.",
        "result_footer": "Continue with these values, or use Step 3 to change only the settings that matter to you.",
        "error_profile": "Provide a valid local model directory and wait for the automatic configuration before continuing.",
        "error_path": "Provide an existing local model directory before continuing.",
        "model_scan_error": "The local model directory could not be read. Verify config.json and the model weight files, then try again.",
        "error_output": "Choose an output directory before continuing.",
        "error_dataset": "Select at least one training dataset before continuing.",
        "error_learning_rate": "Learning rate must be a positive number.",
        "error_epochs": "Training epochs must be a positive number.",
        "error_batch": "Batch size and gradient accumulation must both be at least 1.",
    },
    "ru": {
        "questionnaire": "### Расскажите, чему нужно обучить модель\nВыберите цель и приоритет. Оборудование определяется автоматически, а начальная конфигурация обновляется сразу.",
        "goal_label": "Чему должна научиться модель?",
        "goal_info": "Выберите результат, наиболее близкий к вашему сценарию.",
        "goal_choices": (
            ("Следовать инструкциям и отвечать", "instruction"),
            ("Предпочитать лучшие ответы", "preference"),
            ("Продолжить обучение на текстах", "pretrain"),
        ),
        "hardware_label": "Сколько видеопамяти доступно?",
        "hardware_info": "Укажите память одной GPU. Мульти-GPU выбирайте только при настроенном распределённом обучении.",
        "hardware_choices": (
            ("8 ГБ или меньше", "low"),
            ("12–16 ГБ", "mid"),
            ("24–48 ГБ", "high"),
            ("Мульти-GPU / 80 ГБ+", "multi"),
        ),
        "priority_label": "Что важнее всего?",
        "priority_info": "Для первого запуска рекомендуется сбалансированный режим.",
        "params_guide": "### Выберите только то, что хотите изменить\nРекомендуемая конфигурация уже готова. Выберите одну ветку — остальные параметры останутся скрыты.",
        "param_mode_label": "Что вы хотите изменить?",
        "param_mode_info": "Ветка выбирается автоматически по указанному ранее приоритету.",
        "param_mode_choices": (
            ("Ничего — использовать рекомендацию", "recommended"),
            ("Видеопамять и скорость", "resources"),
            ("Качество и сходимость", "learning"),
        ),
        "resource_params_guide": "### Видеопамять и скорость\nПоказаны только четыре параметра, напрямую влияющие на пик памяти и производительность.",
        "learning_params_guide": "### Качество и сходимость\nНастройте процесс обучения без инфраструктурных и экспертных параметров.",
        "show_advanced_label": "Я хочу изменить созданные параметры вручную",
        "show_advanced_info": "Необязательно. Этот переключатель открывает технические и экспертные настройки.",
        "priority_choices": (
            ("Баланс и надёжность", "balanced"),
            ("Меньше видеопамяти", "memory"),
            ("Быстрее обучение", "speed"),
            ("Максимум качества", "quality"),
        ),
        "apply_button": "Создать рекомендуемую конфигурацию",
        "manual_settings": "Параметры модели (необязательно)",
        "result_title": "Рекомендуемая конфигурация применена",
        "result_intro": "Это безопасные начальные значения для выбранной задачи и оборудования.",
        "result_labels": (
            "Локальные файлы весов",
            "Метод",
            "Квантизация",
            "Точность",
            "Последовательность",
            "Эффективный пакет",
        ),
        "weight_size": "{value:.2f} GiB",
        "none": "Нет",
        "tokens": "{value} токенов",
        "effective_batch": "{value} примеров",
        "reason_balanced": "Сбалансированный режим делает расход памяти предсказуемым и сохраняет стабильность обучения.",
        "reason_memory": "Экономный режим уменьшает пакет и использует 4-битную загрузку, когда она поддерживается.",
        "reason_speed": "Быстрый режим увеличивает пакет на устройство, если выбранное оборудование это позволяет.",
        "reason_quality": "Режим качества сохраняет точность и длину контекста, если хватает оборудования.",
        "result_footer": "Продолжайте с этими значениями или измените только нужные параметры на шаге 3.",
        "error_profile": "Укажите корректный локальный каталог модели и дождитесь автоматической настройки.",
        "error_path": "Перед продолжением укажите существующий локальный каталог модели.",
        "model_scan_error": "Не удалось прочитать локальный каталог модели. Проверьте config.json и файлы весов, затем повторите попытку.",
        "error_output": "Перед продолжением выберите каталог результатов.",
        "error_dataset": "Перед продолжением выберите хотя бы один набор данных.",
        "error_learning_rate": "Скорость обучения должна быть положительным числом.",
        "error_epochs": "Количество эпох должно быть положительным числом.",
        "error_batch": "Размер пакета и накопление градиента должны быть не меньше 1.",
    },
    "zh": {
        "questionnaire": "### 告诉我们你想训练什么\n选择训练目标和优化重点；硬件会自动检测，起始配置会立即生成。",
        "goal_label": "你希望模型学会什么？",
        "goal_info": "请选择最接近实际业务目标的一项。",
        "goal_choices": (
            ("遵循指令并回答问题", "instruction"),
            ("更偏好高质量回答", "preference"),
            ("从原始文本继续学习", "pretrain"),
        ),
        "hardware_label": "可用的 GPU 显存是多少？",
        "hardware_info": "请选择单张 GPU 的显存；仅在已配置分布式训练时选择多卡。",
        "hardware_choices": (
            ("8 GB 或更少", "low"),
            ("12–16 GB", "mid"),
            ("24–48 GB", "high"),
            ("多卡 / 80 GB 以上", "multi"),
        ),
        "priority_label": "这次训练优先考虑什么？",
        "priority_info": "首次运行建议选择均衡可靠。",
        "params_guide": "### 只选择你想调整的内容\n推荐配置已经完整生成。请选择一个分支，其他无关参数会保持隐藏。",
        "param_mode_label": "你想调整哪一部分？",
        "param_mode_info": "系统会根据前面选择的优化重点自动进入建议分支。",
        "param_mode_choices": (
            ("不调整，直接使用推荐配置", "recommended"),
            ("显存占用与训练速度", "resources"),
            ("学习质量与收敛效果", "learning"),
        ),
        "resource_params_guide": "### 显存占用与训练速度\n这里只显示直接影响峰值显存和吞吐量的四个参数。",
        "learning_params_guide": "### 学习质量与收敛效果\n只调整学习策略，不显示基础设施和专家选项。",
        "show_advanced_label": "我要手动调整系统生成的参数",
        "show_advanced_info": "可选。开启后会显示技术参数和专家设置。",
        "priority_choices": (
            ("均衡可靠", "balanced"),
            ("节省显存", "memory"),
            ("更快训练", "speed"),
            ("最高质量", "quality"),
        ),
        "apply_button": "生成我的推荐配置",
        "manual_settings": "模型专项设置（可选）",
        "result_title": "已应用推荐配置",
        "result_intro": "这些参数是根据你的目标和硬件生成的安全起始值。",
        "result_labels": ("本地权重文件", "微调方法", "量化", "计算精度", "序列长度", "有效批次"),
        "weight_size": "{value:.2f} GiB",
        "none": "无",
        "tokens": "{value} 个 token",
        "effective_batch": "{value} 个样本",
        "reason_balanced": "均衡模式会控制显存占用，同时保持训练稳定性。",
        "reason_memory": "显存优先模式会缩小批次，并在支持时使用 4 位加载。",
        "reason_speed": "速度优先模式会在硬件允许时增大单卡批次。",
        "reason_quality": "质量优先模式会在硬件允许时保留更高精度和更长上下文。",
        "result_footer": "可以直接使用这些值，也可以在第 3 步只修改自己关心的参数。",
        "error_profile": "请先填写有效的本地模型目录，等待系统自动生成配置后再继续。",
        "error_path": "请先填写已经存在的本地模型目录，再继续下一步。",
        "model_scan_error": "无法读取本地模型目录。请检查 config.json 和模型权重文件后重试。",
        "error_output": "请先选择输出目录，再继续下一步。",
        "error_dataset": "请至少选择一个训练数据集，再继续下一步。",
        "error_learning_rate": "学习率必须是大于 0 的数字。",
        "error_epochs": "训练轮数必须是大于 0 的数字。",
        "error_batch": "批处理大小和梯度累积都必须至少为 1。",
    },
    "ko": {
        "questionnaire": "### 무엇을 학습할지 알려 주세요\n목표와 우선순위를 선택하세요. 하드웨어는 자동 감지되고 시작 구성은 즉시 갱신됩니다.",
        "goal_label": "모델이 무엇을 학습해야 하나요?",
        "goal_info": "사용 목적과 가장 가까운 결과를 선택하세요.",
        "goal_choices": (
            ("지시를 따르고 질문에 답하기", "instruction"),
            ("더 좋은 답변을 선호하기", "preference"),
            ("원시 텍스트로 계속 학습하기", "pretrain"),
        ),
        "hardware_label": "사용 가능한 GPU 메모리는 얼마인가요?",
        "hardware_info": "GPU 한 장의 메모리를 선택하세요. 분산 학습이 구성된 경우에만 멀티 GPU를 선택하세요.",
        "hardware_choices": (
            ("8 GB 이하", "low"),
            ("12–16 GB", "mid"),
            ("24–48 GB", "high"),
            ("멀티 GPU / 80 GB 이상", "multi"),
        ),
        "priority_label": "이번 학습에서 무엇을 우선할까요?",
        "priority_info": "첫 실행에는 균형 및 안정 모드를 권장합니다.",
        "params_guide": "### 변경할 항목만 선택하세요\n권장 구성이 이미 완성되었습니다. 하나의 분기를 선택하면 관련 없는 파라미터는 숨겨집니다.",
        "param_mode_label": "무엇을 조정할까요?",
        "param_mode_info": "앞에서 선택한 우선순위에 따라 권장 분기가 자동 선택됩니다.",
        "param_mode_choices": (
            ("변경 없이 권장값 사용", "recommended"),
            ("GPU 메모리와 학습 속도", "resources"),
            ("학습 품질과 수렴", "learning"),
        ),
        "resource_params_guide": "### GPU 메모리와 학습 속도\n최대 메모리와 처리량에 직접 영향을 주는 네 가지 설정만 표시합니다.",
        "learning_params_guide": "### 학습 품질과 수렴\n인프라 및 전문가 옵션을 노출하지 않고 학습 전략만 조정합니다.",
        "show_advanced_label": "생성된 파라미터를 수동으로 조정하겠습니다",
        "show_advanced_info": "선택 사항입니다. 켜면 기술 및 전문가 설정이 표시됩니다.",
        "priority_choices": (
            ("균형 및 안정", "balanced"),
            ("GPU 메모리 절약", "memory"),
            ("더 빠른 학습", "speed"),
            ("최고 품질", "quality"),
        ),
        "apply_button": "권장 구성 생성",
        "manual_settings": "모델별 설정(선택 사항)",
        "result_title": "권장 구성이 적용됨",
        "result_intro": "선택한 목표와 하드웨어에 맞는 안전한 시작값입니다.",
        "result_labels": ("로컬 가중치 파일", "방식", "양자화", "정밀도", "시퀀스", "유효 배치"),
        "weight_size": "{value:.2f} GiB",
        "none": "없음",
        "tokens": "{value} 토큰",
        "effective_batch": "{value} 샘플",
        "reason_balanced": "균형 모드는 메모리 사용량을 예측 가능하게 유지하면서 학습 안정성을 보존합니다.",
        "reason_memory": "메모리 절약 모드는 배치를 줄이고 지원되는 경우 4비트 로딩을 사용합니다.",
        "reason_speed": "속도 모드는 선택한 하드웨어에 여유가 있을 때 장치 배치를 늘립니다.",
        "reason_quality": "품질 모드는 하드웨어가 지원할 때 정밀도와 컨텍스트 길이를 유지합니다.",
        "result_footer": "이 값을 그대로 사용하거나 3단계에서 필요한 설정만 변경하세요.",
        "error_profile": "유효한 로컬 모델 디렉터리를 입력하고 자동 구성이 완료될 때까지 기다리세요.",
        "error_path": "계속하기 전에 기존 로컬 모델 디렉터리를 입력하세요.",
        "model_scan_error": "로컬 모델 디렉터리를 읽을 수 없습니다. config.json과 모델 가중치 파일을 확인한 뒤 다시 시도하세요.",
        "error_output": "계속하기 전에 출력 디렉터리를 선택하세요.",
        "error_dataset": "계속하기 전에 학습 데이터셋을 하나 이상 선택하세요.",
        "error_learning_rate": "학습률은 0보다 큰 숫자여야 합니다.",
        "error_epochs": "학습 에포크는 0보다 큰 숫자여야 합니다.",
        "error_batch": "배치 크기와 그래디언트 누적은 모두 1 이상이어야 합니다.",
    },
    "ja": {
        "questionnaire": "### 何を学習させたいか教えてください\n目的と優先事項を選択します。ハードウェアは自動検出され、初期構成がすぐ更新されます。",
        "goal_label": "モデルに何を学習させますか？",
        "goal_info": "用途に最も近い結果を選択してください。",
        "goal_choices": (
            ("指示に従って質問に答える", "instruction"),
            ("より良い回答を優先する", "preference"),
            ("生テキストから継続学習する", "pretrain"),
        ),
        "hardware_label": "利用可能な GPU メモリは？",
        "hardware_info": "GPU 1枚のメモリを選択してください。分散学習を構成済みの場合だけマルチ GPU を選びます。",
        "hardware_choices": (
            ("8 GB 以下", "low"),
            ("12–16 GB", "mid"),
            ("24–48 GB", "high"),
            ("マルチ GPU / 80 GB 以上", "multi"),
        ),
        "priority_label": "今回の学習で何を優先しますか？",
        "priority_info": "初回はバランスと安定性を推奨します。",
        "params_guide": "### 変更したい項目だけ選択してください\n推奨構成は完成済みです。1つの分岐を選ぶと、関係のないパラメータは非表示になります。",
        "param_mode_label": "何を調整しますか？",
        "param_mode_info": "前に選択した優先事項に応じて推奨分岐が自動選択されます。",
        "param_mode_choices": (
            ("変更せず推奨値を使用", "recommended"),
            ("GPU メモリと学習速度", "resources"),
            ("学習品質と収束", "learning"),
        ),
        "resource_params_guide": "### GPU メモリと学習速度\nピークメモリとスループットに直接影響する4項目だけを表示します。",
        "learning_params_guide": "### 学習品質と収束\nインフラやエキスパート設定を表示せずに学習戦略だけを調整します。",
        "show_advanced_label": "生成されたパラメータを手動で調整する",
        "show_advanced_info": "任意です。有効にすると技術設定とエキスパート設定が表示されます。",
        "priority_choices": (
            ("バランスと安定性", "balanced"),
            ("GPU メモリを節約", "memory"),
            ("より高速に学習", "speed"),
            ("最高品質", "quality"),
        ),
        "apply_button": "推奨構成を生成",
        "manual_settings": "モデル固有の設定（任意）",
        "result_title": "推奨構成を適用しました",
        "result_intro": "選択した目的とハードウェアに合う安全な初期値です。",
        "result_labels": ("ローカル重みファイル", "方式", "量子化", "精度", "シーケンス", "有効バッチ"),
        "weight_size": "{value:.2f} GiB",
        "none": "なし",
        "tokens": "{value} トークン",
        "effective_batch": "{value} サンプル",
        "reason_balanced": "バランスモードはメモリ使用量を予測可能にしながら学習の安定性を維持します。",
        "reason_memory": "省メモリモードはバッチを小さくし、対応時は4ビット読み込みを使用します。",
        "reason_speed": "速度モードは選択したハードウェアに余裕がある場合、デバイスバッチを増やします。",
        "reason_quality": "品質モードはハードウェアが対応できる場合、精度とコンテキスト長を維持します。",
        "result_footer": "この値のまま続行するか、ステップ 3 で必要な項目だけ変更してください。",
        "error_profile": "有効なローカルモデルディレクトリを入力し、自動構成の完了を待ってください。",
        "error_path": "続行する前に既存のローカルモデルディレクトリを入力してください。",
        "model_scan_error": "ローカルモデルディレクトリを読み取れません。config.json とモデル重みファイルを確認して再試行してください。",
        "error_output": "続行する前に出力先を選択してください。",
        "error_dataset": "続行する前に学習データセットを1つ以上選択してください。",
        "error_learning_rate": "学習率は0より大きい数値である必要があります。",
        "error_epochs": "学習エポック数は0より大きい数値である必要があります。",
        "error_batch": "バッチサイズと勾配累積はどちらも1以上である必要があります。",
    },
}


WIZARD_MEMORY_LOCALES = {
    "en": {
        "live_intro": "### Live VRAM estimate\nThis estimate updates when model loading, precision, sequence length, per-device batch size, or another memory-sensitive setting changes.",
        "intro": "### Check VRAM before training\nThe system totals local model weight files, reads the model and final training configurations, estimates peak VRAM per device, and adds a 10% safety margin.",
        "check_button": "Check VRAM and continue",
        "force_ack_label": "I understand that training may fail or become unstable",
        "force_ack_info": "Required before force-starting with insufficient or uncertain VRAM.",
        "force_button": "Force training",
        "cancel_button": "Go back and adjust settings",
        "titles": {
            "safe": "VRAM check passed",
            "below": "VRAM is below the recommended value",
            "insufficient": "VRAM is insufficient",
            "uncertain": "VRAM safety could not be verified",
        },
        "descriptions": {
            "safe": "Current free VRAM meets the estimate plus the 10% safety margin. The result updates when memory-sensitive settings change.",
            "below": "The model may fit the raw estimate, but the 10% safety margin is not available. Training is not recommended.",
            "insufficient": "Currently free VRAM is below the estimated peak. Training is not recommended.",
            "uncertain": "The system could not verify the model configuration or available accelerator memory. Training is not recommended without manual verification.",
        },
        "labels": (
            "Local weight files",
            "Model parameters",
            "Estimated peak",
            "Recommended with 10% margin",
            "Free / total VRAM",
            "Devices",
            "Estimate basis",
        ),
        "local_source": "Local weights + model config + training config",
        "unavailable_source": "Local model inspection unavailable",
        "model_read_error": "The local model directory could not be inspected. Verify config.json and the weight files before training.",
        "unknown": "Not detected",
        "risk_title": "Force training despite the VRAM warning?",
        "risk_body": "The safety check does not recommend starting with the current configuration. A forced run can fail with an out-of-memory error, interrupt work, or leave incomplete output.",
        "risk_action": "Return to Step 3, choose the memory and speed branch, reduce batch size or sequence length, and run the check again.",
    },
    "ru": {
        "live_intro": "### Оценка видеопамяти в реальном времени\nОценка обновляется при изменении загрузки модели, точности, длины последовательности, размера пакета на устройство и других параметров памяти.",
        "intro": "### Проверка видеопамяти перед обучением\nСистема суммирует локальные файлы весов, читает конфигурации модели и обучения, оценивает пик памяти на устройство и добавляет запас 10%.",
        "check_button": "Проверить видеопамять и продолжить",
        "force_ack_label": "Я понимаю, что обучение может завершиться ошибкой или работать нестабильно",
        "force_ack_info": "Обязательно для принудительного запуска при недостаточной или неопределённой памяти.",
        "force_button": "Запустить принудительно",
        "cancel_button": "Вернуться и изменить настройки",
        "titles": {
            "safe": "Проверка памяти пройдена",
            "below": "Память ниже рекомендуемого значения",
            "insufficient": "Недостаточно видеопамяти",
            "uncertain": "Не удалось подтвердить безопасность памяти",
        },
        "descriptions": {
            "safe": "Свободной видеопамяти достаточно для оценки с запасом 10%. Результат обновляется при изменении параметров памяти.",
            "below": "Модель может поместиться по базовой оценке, но запаса 10% нет. Запуск не рекомендуется.",
            "insufficient": "Свободная видеопамять ниже оценочного пика. Запуск не рекомендуется.",
            "uncertain": "Не удалось проверить конфигурацию модели или доступную память ускорителя. Без ручной проверки запуск не рекомендуется.",
        },
        "labels": (
            "Локальные файлы весов",
            "Параметры модели",
            "Оценочный пик",
            "Рекомендация с запасом 10%",
            "Свободно / всего",
            "Устройства",
            "Основа оценки",
        ),
        "local_source": "Локальные веса, конфигурация модели и обучения",
        "unavailable_source": "Локальная модель не проверена",
        "model_read_error": "Не удалось проверить локальный каталог модели. Перед обучением проверьте config.json и файлы весов.",
        "unknown": "Не обнаружено",
        "risk_title": "Запустить обучение вопреки предупреждению?",
        "risk_body": "Проверка безопасности не рекомендует запуск с текущей конфигурацией. Принудительный запуск может вызвать ошибку нехватки памяти, прервать работу или оставить неполный результат.",
        "risk_action": "Вернитесь к шагу 3, выберите ветку памяти и скорости, уменьшите пакет или длину последовательности и повторите проверку.",
    },
    "zh": {
        "live_intro": "### 实时显存估算\n修改模型加载方式、计算精度、序列长度、单卡批处理大小等显存相关参数时，估算结果会自动更新。",
        "intro": "### 训练前检查显存\n系统会汇总本地模型权重文件，读取模型配置和最终训练配置，估算每张设备的峰值显存，并额外保留 10% 安全余量。",
        "check_button": "检查显存并继续",
        "force_ack_label": "我已了解训练可能失败或出现不稳定",
        "force_ack_info": "显存不足或无法确认时，强制启动前必须勾选。",
        "force_button": "仍然强制训练",
        "cancel_button": "返回调整配置",
        "titles": {
            "safe": "显存检查通过",
            "below": "显存低于建议值",
            "insufficient": "显存不足",
            "uncertain": "无法确认显存安全性",
        },
        "descriptions": {
            "safe": "当前空闲显存满足峰值估算及额外 10% 安全余量；修改显存相关参数后会自动更新。",
            "below": "当前显存可能达到基础估算值，但未达到额外保留 10% 后的建议值，因此不建议训练。",
            "insufficient": "当前空闲显存低于预计峰值，因此不建议训练。",
            "uncertain": "系统无法确认模型配置或可用加速设备显存。未经人工核对，不建议训练。",
        },
        "labels": (
            "本地权重文件",
            "模型参数量",
            "预计峰值",
            "包含 10% 余量的建议值",
            "空闲 / 总显存",
            "设备数量",
            "估算依据",
        ),
        "local_source": "本地权重 + 模型配置 + 训练配置",
        "unavailable_source": "无法检查本地模型",
        "model_read_error": "无法检查本地模型目录。训练前请确认 config.json 和权重文件完整可读。",
        "unknown": "未检测到",
        "risk_title": "确定忽略显存警告并强制训练吗？",
        "risk_body": "安全检查不建议使用当前配置启动。强制训练可能发生显存溢出、任务中断，或留下不完整的输出结果。",
        "risk_action": "请返回第 3 步，选择“显存占用与训练速度”，减小批处理大小或序列长度后重新检查。",
    },
    "ko": {
        "live_intro": "### 실시간 GPU 메모리 추정\n모델 로딩, 계산 정밀도, 시퀀스 길이, 장치당 배치 크기 등 메모리 관련 설정이 바뀌면 추정치가 자동으로 업데이트됩니다.",
        "intro": "### 학습 전 GPU 메모리 확인\n시스템이 로컬 모델 가중치 파일을 합산하고 모델 및 최종 학습 구성을 읽은 뒤 장치당 최대 메모리와 10% 안전 여유를 계산합니다.",
        "check_button": "GPU 메모리 확인 후 계속",
        "force_ack_label": "학습이 실패하거나 불안정할 수 있음을 이해했습니다",
        "force_ack_info": "메모리가 부족하거나 불확실한 상태에서 강제 시작하려면 필요합니다.",
        "force_button": "강제로 학습 시작",
        "cancel_button": "돌아가서 설정 조정",
        "titles": {
            "safe": "GPU 메모리 확인 통과",
            "below": "GPU 메모리가 권장값보다 낮음",
            "insufficient": "GPU 메모리 부족",
            "uncertain": "GPU 메모리 안전성을 확인할 수 없음",
        },
        "descriptions": {
            "safe": "현재 여유 메모리가 추정치와 10% 안전 여유를 충족합니다. 메모리 관련 설정이 바뀌면 결과가 자동으로 업데이트됩니다.",
            "below": "기본 추정치에는 맞을 수 있지만 10% 안전 여유가 없습니다. 학습을 권장하지 않습니다.",
            "insufficient": "현재 여유 메모리가 예상 최대치보다 낮습니다. 학습을 권장하지 않습니다.",
            "uncertain": "모델 구성 또는 사용 가능한 가속기 메모리를 확인할 수 없습니다. 수동 확인 없이는 학습을 권장하지 않습니다.",
        },
        "labels": (
            "로컬 가중치 파일",
            "모델 파라미터",
            "예상 최대치",
            "10% 여유 포함 권장값",
            "여유 / 전체 메모리",
            "장치",
            "추정 기준",
        ),
        "local_source": "로컬 가중치 + 모델 구성 + 학습 구성",
        "unavailable_source": "로컬 모델 검사 불가",
        "model_read_error": "로컬 모델 디렉터리를 검사할 수 없습니다. 학습 전에 config.json과 가중치 파일을 확인하세요.",
        "unknown": "감지되지 않음",
        "risk_title": "GPU 메모리 경고를 무시하고 강제 학습할까요?",
        "risk_body": "안전 확인 결과 현재 구성으로 시작하는 것을 권장하지 않습니다. 강제 실행 시 메모리 부족 오류, 작업 중단 또는 불완전한 출력이 발생할 수 있습니다.",
        "risk_action": "3단계로 돌아가 GPU 메모리 및 속도 분기를 선택하고 배치 크기나 시퀀스 길이를 줄인 뒤 다시 확인하세요.",
    },
    "ja": {
        "live_intro": "### GPU メモリのリアルタイム推定\nモデルの読み込み方法、計算精度、シーケンス長、デバイスごとのバッチサイズなどを変更すると、推定値が自動更新されます。",
        "intro": "### 学習前に GPU メモリを確認\nローカルモデルの重みファイルを集計し、モデル構成と最終学習設定を読み取って、デバイスごとのピークと10%の安全余裕を計算します。",
        "check_button": "GPU メモリを確認して続行",
        "force_ack_label": "学習が失敗または不安定になる可能性を理解しました",
        "force_ack_info": "メモリ不足または不確実な状態で強制開始する場合に必要です。",
        "force_button": "強制的に学習を開始",
        "cancel_button": "戻って設定を調整",
        "titles": {
            "safe": "GPU メモリ確認に合格",
            "below": "GPU メモリが推奨値未満",
            "insufficient": "GPU メモリ不足",
            "uncertain": "GPU メモリの安全性を確認できません",
        },
        "descriptions": {
            "safe": "現在の空きメモリは推定値と10%の安全余裕を満たしています。メモリ関連の設定を変更すると結果が自動更新されます。",
            "below": "基本推定値には収まる可能性がありますが、10%の安全余裕がありません。学習は推奨されません。",
            "insufficient": "現在の空きメモリは推定ピーク未満です。学習は推奨されません。",
            "uncertain": "モデル構成または利用可能なアクセラレータメモリを確認できません。手動確認なしの学習は推奨されません。",
        },
        "labels": (
            "ローカル重みファイル",
            "モデルパラメータ",
            "推定ピーク",
            "10%余裕込み推奨値",
            "空き / 総メモリ",
            "デバイス",
            "推定根拠",
        ),
        "local_source": "ローカル重み + モデル構成 + 学習構成",
        "unavailable_source": "ローカルモデルを検査できません",
        "model_read_error": "ローカルモデルディレクトリを検査できません。学習前に config.json と重みファイルを確認してください。",
        "unknown": "未検出",
        "risk_title": "GPU メモリ警告を無視して強制学習しますか？",
        "risk_body": "安全確認では現在の構成での開始を推奨していません。強制実行するとメモリ不足、処理中断、不完全な出力が発生する可能性があります。",
        "risk_action": "ステップ 3 に戻って GPU メモリと速度を選び、バッチサイズまたはシーケンス長を下げて再確認してください。",
    },
}


LOCALES.update(
    {
        "wizard_questionnaire": {
            lang: {"value": text["questionnaire"]} for lang, text in WIZARD_GUIDANCE_LOCALES.items()
        },
        "wizard_goal": {
            lang: {"label": text["goal_label"], "info": text["goal_info"], "choices": text["goal_choices"]}
            for lang, text in WIZARD_GUIDANCE_LOCALES.items()
        },
        "wizard_priority": {
            lang: {"label": text["priority_label"], "info": text["priority_info"], "choices": text["priority_choices"]}
            for lang, text in WIZARD_GUIDANCE_LOCALES.items()
        },
        "wizard_params_guide": {
            lang: {"value": text["params_guide"]} for lang, text in WIZARD_GUIDANCE_LOCALES.items()
        },
        "wizard_param_mode": {
            lang: {
                "label": text["param_mode_label"],
                "info": text["param_mode_info"],
                "choices": text["param_mode_choices"],
            }
            for lang, text in WIZARD_GUIDANCE_LOCALES.items()
        },
        "wizard_resource_params_guide": {
            lang: {"value": text["resource_params_guide"]} for lang, text in WIZARD_GUIDANCE_LOCALES.items()
        },
        "wizard_learning_params_guide": {
            lang: {"value": text["learning_params_guide"]} for lang, text in WIZARD_GUIDANCE_LOCALES.items()
        },
        "manual_settings": {
            lang: {"label": text["manual_settings"]} for lang, text in WIZARD_GUIDANCE_LOCALES.items()
        },
        "wizard_live_memory_intro": {
            lang: {"value": text["live_intro"]} for lang, text in WIZARD_MEMORY_LOCALES.items()
        },
        "wizard_memory_intro": {lang: {"value": text["intro"]} for lang, text in WIZARD_MEMORY_LOCALES.items()},
        "wizard_preflight_btn": {
            lang: {"value": text["check_button"]} for lang, text in WIZARD_MEMORY_LOCALES.items()
        },
        "wizard_force_ack": {
            lang: {"label": text["force_ack_label"], "info": text["force_ack_info"]}
            for lang, text in WIZARD_MEMORY_LOCALES.items()
        },
        "wizard_force_start_btn": {
            lang: {"value": text["force_button"]} for lang, text in WIZARD_MEMORY_LOCALES.items()
        },
        "wizard_force_cancel_btn": {
            lang: {"value": text["cancel_button"]} for lang, text in WIZARD_MEMORY_LOCALES.items()
        },
    }
)


MERGE_WORKSPACE_LOCALES = {
    "en": {
        "train_tab": "Guided Training",
        "merge_tab": "Adapter Merge",
        "kicker": "MODEL DELIVERY",
        "title": "Merge an adapter into its base model",
        "description": "Create a standalone local model from a trained adapter. Only the source, destination, and merge action are required.",
        "source": "### 1. Select the adapter\nChoose the local base model in **Guided Training → Step 1**, then select one or more trained adapters here.",
        "settings": "The defaults preserve model quality. Change these options only when a smaller or differently sharded artifact is required.",
        "optional_label": "Output format (optional)",
        "destination": "### 2. Choose a local destination\nEnter the directory where the standalone merged model will be saved.",
        "action": "Merge adapter and export model",
    },
    "ru": {
        "train_tab": "Пошаговое обучение",
        "merge_tab": "Слияние адаптеров",
        "kicker": "ПОДГОТОВКА МОДЕЛИ",
        "title": "Объедините адаптер с базовой моделью",
        "description": "Создайте самостоятельную локальную модель из обученного адаптера. Обязательны только источник, каталог и запуск слияния.",
        "source": "### 1. Выберите адаптер\nУкажите локальную базовую модель в разделе **Пошаговое обучение → Шаг 1**, затем выберите здесь один или несколько адаптеров.",
        "settings": "Настройки по умолчанию сохраняют качество. Меняйте их только если нужен меньший файл или другая разбивка.",
        "optional_label": "Формат вывода (необязательно)",
        "destination": "### 2. Выберите локальный каталог\nУкажите каталог для сохранения объединённой модели.",
        "action": "Объединить адаптер и экспортировать модель",
    },
    "zh": {
        "train_tab": "引导式训练",
        "merge_tab": "适配器合并",
        "kicker": "模型交付",
        "title": "将适配器合并到基础模型",
        "description": "将训练好的适配器生成独立的本地模型。只需确认来源、保存位置并开始合并。",
        "source": "### 1. 选择适配器\n请先在 **引导式训练 → 第 1 步** 选择本地基础模型，再在此选择一个或多个已训练适配器。",
        "settings": "默认设置会保留模型质量。仅在需要更小文件或不同分块方式时修改。",
        "optional_label": "输出格式（可选）",
        "destination": "### 2. 选择本地保存位置\n请输入独立合并模型的保存目录。",
        "action": "合并适配器并导出模型",
    },
    "ko": {
        "train_tab": "안내형 학습",
        "merge_tab": "어댑터 병합",
        "kicker": "모델 제공",
        "title": "어댑터를 기본 모델에 병합",
        "description": "학습된 어댑터에서 독립 로컬 모델을 만듭니다. 원본, 저장 위치 및 병합 실행만 필요합니다.",
        "source": "### 1. 어댑터 선택\n**안내형 학습 → 1단계**에서 로컬 기본 모델을 선택한 뒤 여기에서 하나 이상의 학습된 어댑터를 선택하세요.",
        "settings": "기본값은 모델 품질을 유지합니다. 더 작은 파일이나 다른 샤딩이 필요한 경우에만 변경하세요.",
        "optional_label": "출력 형식(선택 사항)",
        "destination": "### 2. 로컬 저장 위치 선택\n병합된 독립 모델을 저장할 디렉터리를 입력하세요.",
        "action": "어댑터 병합 및 모델 내보내기",
    },
    "ja": {
        "train_tab": "ガイド付き学習",
        "merge_tab": "アダプターマージ",
        "kicker": "モデルの提供",
        "title": "アダプターをベースモデルにマージ",
        "description": "学習済みアダプターから独立したローカルモデルを作成します。入力元、保存先、マージ実行だけが必要です。",
        "source": "### 1. アダプターを選択\n**ガイド付き学習 → ステップ 1** でローカルのベースモデルを選び、ここで学習済みアダプターを選択します。",
        "settings": "既定値はモデル品質を維持します。小さいファイルや別の分割方式が必要な場合だけ変更してください。",
        "optional_label": "出力形式（任意）",
        "destination": "### 2. ローカル保存先を選択\nマージした単体モデルを保存するディレクトリを入力してください。",
        "action": "アダプターをマージしてモデルをエクスポート",
    },
}


def _build_merge_hero(lang: str) -> str:
    text = MERGE_WORKSPACE_LOCALES[lang]
    return (
        '<section class="merge-hero">'
        f'<div class="merge-kicker">{text["kicker"]}</div>'
        f"<h1>{text['title']}</h1><p>{text['description']}</p>"
        "</section>"
    )


LOCALES.update(
    {
        "train_workspace_btn": {lang: {"value": text["train_tab"]} for lang, text in MERGE_WORKSPACE_LOCALES.items()},
        "merge_workspace_btn": {lang: {"value": text["merge_tab"]} for lang, text in MERGE_WORKSPACE_LOCALES.items()},
        "merge_hero": {lang: {"value": _build_merge_hero(lang)} for lang in MERGE_WORKSPACE_LOCALES},
        "merge_source_guide": {lang: {"value": text["source"]} for lang, text in MERGE_WORKSPACE_LOCALES.items()},
        "merge_settings_guide": {lang: {"value": text["settings"]} for lang, text in MERGE_WORKSPACE_LOCALES.items()},
        "merge_optional_settings": {
            lang: {"label": text["optional_label"]} for lang, text in MERGE_WORKSPACE_LOCALES.items()
        },
        "merge_destination_guide": {
            lang: {"value": text["destination"]} for lang, text in MERGE_WORKSPACE_LOCALES.items()
        },
        "merge_export_btn": {lang: {"value": text["action"]} for lang, text in MERGE_WORKSPACE_LOCALES.items()},
    }
)


ALERTS = {
    "err_conflict": {
        "en": "A process is in running, please abort it first.",
        "ru": "Процесс уже запущен, пожалуйста, сначала прервите его.",
        "zh": "任务已存在，请先中断训练。",
        "ko": "프로세스가 실행 중입니다. 먼저 중단하십시오.",
        "ja": "プロセスが実行中です。最初に中断してください。",
    },
    "err_exists": {
        "en": "You have loaded a model, please unload it first.",
        "ru": "Вы загрузили модель, сначала разгрузите ее.",
        "zh": "模型已存在，请先卸载模型。",
        "ko": "모델이 로드되었습니다. 먼저 언로드하십시오.",
        "ja": "モデルがロードされています。最初にアンロードしてください。",
    },
    "err_no_model": {
        "en": "Please select a model.",
        "ru": "Пожалуйста, выберите модель.",
        "zh": "请选择模型。",
        "ko": "모델을 선택하십시오.",
        "ja": "モデルを選択してください。",
    },
    "err_no_path": {
        "en": "The local model directory does not exist.",
        "ru": "Локальный каталог модели не существует.",
        "zh": "本地模型目录不存在。",
        "ko": "로컬 모델 디렉터리가 존재하지 않습니다.",
        "ja": "ローカルモデルディレクトリが存在しません。",
    },
    "err_no_dataset": {
        "en": "Please choose a dataset.",
        "ru": "Пожалуйста, выберите набор данных.",
        "zh": "请选择数据集。",
        "ko": "데이터 세트를 선택하십시오.",
        "ja": "データセットを選択してください。",
    },
    "err_no_adapter": {
        "en": "Please select an adapter.",
        "ru": "Пожалуйста, выберите адаптер.",
        "zh": "请选择适配器。",
        "ko": "어댑터를 선택하십시오.",
        "ja": "アダプターを選択してください。",
    },
    "err_no_output_dir": {
        "en": "Please provide output dir.",
        "ru": "Пожалуйста, укажите выходную директорию.",
        "zh": "请填写输出目录。",
        "ko": "출력 디렉토리를 제공하십시오.",
        "ja": "出力ディレクトリを入力してください。",
    },
    "err_no_reward_model": {
        "en": "Please select a reward model.",
        "ru": "Пожалуйста, выберите модель вознаграждения.",
        "zh": "请选择奖励模型。",
        "ko": "리워드 모델을 선택하십시오.",
        "ja": "報酬モデルを選択してください。",
    },
    "err_no_export_dir": {
        "en": "Please provide export dir.",
        "ru": "Пожалуйста, укажите каталог для экспорта.",
        "zh": "请填写导出目录。",
        "ko": "Export 디렉토리를 제공하십시오.",
        "ja": "エクスポートディレクトリを入力してください。",
    },
    "err_gptq_lora": {
        "en": "Please merge adapters before quantizing the model.",
        "ru": "Пожалуйста, объедините адаптеры перед квантованием модели.",
        "zh": "量化模型前请先合并适配器。",
        "ko": "모델을 양자화하기 전에 어댑터를 병합하십시오.",
        "ja": "モデルを量子化する前にアダプターをマージしてください。",
    },
    "err_failed": {
        "en": "Failed.",
        "ru": "Ошибка.",
        "zh": "训练出错。",
        "ko": "실패했습니다.",
        "ja": "失敗しました。",
    },
    "err_demo": {
        "en": "Training is unavailable in demo mode, duplicate the space to a private one first.",
        "ru": "Обучение недоступно в демонстрационном режиме, сначала скопируйте пространство в частное.",
        "zh": "展示模式不支持训练，请先复制到私人空间。",
        "ko": "데모 모드에서는 훈련을 사용할 수 없습니다. 먼저 프라이빗 레포지토리로 작업 공간을 복제하십시오.",
        "ja": "デモモードではトレーニングは利用できません。最初にプライベートスペースに複製してください。",
    },
    "err_tool_name": {
        "en": "Tool name not found.",
        "ru": "Имя инструмента не найдено.",
        "zh": "工具名称未找到。",
        "ko": "툴 이름을 찾을 수 없습니다.",
        "ja": "ツール名が見つかりません。",
    },
    "err_json_schema": {
        "en": "Invalid JSON schema.",
        "ru": "Неверная схема JSON.",
        "zh": "Json 格式错误。",
        "ko": "잘못된 JSON 스키마입니다.",
        "ja": "JSON スキーマが無効です。",
    },
    "err_config_not_found": {
        "en": "Config file is not found.",
        "ru": "Файл конфигурации не найден.",
        "zh": "未找到配置文件。",
        "ko": "Config 파일을 찾을 수 없습니다.",
        "ja": "設定ファイルが見つかりません。",
    },
    "warn_no_cuda": {
        "en": "CUDA environment was not detected.",
        "ru": "Среда CUDA не обнаружена.",
        "zh": "未检测到 CUDA 环境。",
        "ko": "CUDA 환경이 감지되지 않았습니다.",
        "ja": "CUDA 環境が検出されませんでした。",
    },
    "warn_output_dir_exists": {
        "en": "Output dir already exists, will resume training from here.",
        "ru": "Выходной каталог уже существует, обучение будет продолжено отсюда.",
        "zh": "输出目录已存在，将从该断点恢复训练。",
        "ko": "출력 디렉토리가 이미 존재합니다. 위 출력 디렉토리에 저장된 학습을 재개합니다.",
        "ja": "出力ディレクトリが既に存在します。このチェックポイントからトレーニングを再開します。",
    },
    "warn_no_instruct": {
        "en": "You are using a non-instruct model, please fine-tune it first.",
        "ru": "Вы используете модель без инструкции, пожалуйста, primeros выполните донастройку этой модели.",
        "zh": "您正在使用非指令模型，请先对其进行微调。",
        "ko": "당신은 지시하지 않은 모델을 사용하고 있습니다. 먼저 이를 미세 조정해 주세요.",
        "ja": "インストラクションモデルを使用していません。まずモデルをアダプターに適合させてください。",
    },
    "info_aborting": {
        "en": "Aborted, wait for terminating...",
        "ru": "Прервано, ожидание завершения...",
        "zh": "训练中断，正在等待进程结束……",
        "ko": "중단되었습니다. 종료를 기다리십시오...",
        "ja": "トレーニングが中断されました。プロセスの終了を待っています...",
    },
    "info_aborted": {
        "en": "Ready.",
        "ru": "Готово.",
        "zh": "准备就绪。",
        "ko": "준비되었습니다.",
        "ja": "準備完了。",
    },
    "info_finished": {
        "en": "Finished.",
        "ru": "Завершено.",
        "zh": "训练完毕。",
        "ko": "완료되었습니다.",
        "ja": "トレーニングが完了しました。",
    },
    "info_config_saved": {
        "en": "Arguments have been saved at: ",
        "ru": "Аргументы были сохранены по адресу: ",
        "zh": "训练参数已保存至：",
        "ko": "매개변수가 저장되었습니다: ",
        "ja": "トレーニングパラメータが保存されました: ",
    },
    "info_config_loaded": {
        "en": "Arguments have been restored.",
        "ru": "Аргументы были восстановлены.",
        "zh": "训练参数已载入。",
        "ko": "매개변수가 복원되었습니다.",
        "ja": "トレーニングパラメータが読み込まれました。",
    },
    "info_loading": {
        "en": "Loading model...",
        "ru": "Загрузка модели...",
        "zh": "加载中……",
        "ko": "모델 로딩 중...",
        "ja": "モデルをロード中...",
    },
    "info_unloading": {
        "en": "Unloading model...",
        "ru": "Выгрузка модели...",
        "zh": "卸载中……",
        "ko": "모델 언로딩 중...",
        "ja": "モデルをアンロード中...",
    },
    "info_loaded": {
        "en": "Model loaded, now you can chat with your model!",
        "ru": "Модель загружена, теперь вы можете общаться с вашей моделью!",
        "zh": "模型已加载，可以开始聊天了！",
        "ko": "모델이 로드되었습니다. 이제 모델과 채팅할 수 있습니다!",
        "ja": "モデルがロードされました。チャットを開始できます！",
    },
    "info_unloaded": {
        "en": "Model unloaded.",
        "ru": "Модель выгружена.",
        "zh": "模型已卸载。",
        "ko": "모델이 언로드되었습니다.",
        "ja": "モデルがアンロードされました。",
    },
    "info_thinking": {
        "en": "🌀 Thinking...",
        "ru": "🌀 Думаю...",
        "zh": "🌀 思考中...",
        "ko": "🌀 생각 중...",
        "ja": "🌀 考えています...",
    },
    "info_thought": {
        "en": "✅ Thought",
        "ru": "✅ Думать закончено",
        "zh": "✅ 思考完成",
        "ko": "✅ 생각이 완료되었습니다",
        "ja": "✅ 思考完了",
    },
    "info_exporting": {
        "en": "Exporting model...",
        "ru": "Экспорт модели...",
        "zh": "正在导出模型……",
        "ko": "모델 내보내기 중...",
        "ja": "モデルをエクスポート中...",
    },
    "info_exported": {
        "en": "Model exported.",
        "ru": "Модель экспортирована.",
        "zh": "模型导出完成。",
        "ko": "모델이 내보내졌습니다.",
        "ja": "モデルのエクスポートが完了しました。",
    },
    "info_swanlab_link": {
        "en": "### SwanLab Link\n",
        "ru": "### SwanLab ссылка\n",
        "zh": "### SwanLab 链接\n",
        "ko": "### SwanLab 링크\n",
        "ja": "### SwanLab リンク\n",
    },
}
