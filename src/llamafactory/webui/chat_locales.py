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

"""Localized resources for the Hugging Face quick-test chat workspace."""

LANGUAGES = ("en", "zh", "ru", "ko", "ja")

CHAT_TEXT = {
    "en": {
        "workspace": "Quick test",
        "header": "<div class='chat-page-header'><span>HUGGING FACE</span><h2>Quick model test</h2><p>Load a local base model or LoRA checkpoint and check its responses before deployment.</p></div>",
        "model_path": "Local model directory",
        "model_path_info": "An existing local Hugging Face model directory containing config.json and weight files.",
        "adapter_path": "LoRA adapter directory (optional)",
        "adapter_path_info": "An existing local adapter or checkpoint directory. Leave empty when testing a base or merged model.",
        "quantization": "Load quantization",
        "quantization_info": (
            "none (recommended for the first test) keeps the original weights and has the best compatibility, "
            "but uses the most VRAM. 8-bit roughly halves weight memory; 4-bit reduces it further but may change "
            "speed or response quality. 8/4-bit require a working bitsandbytes build compatible with this device; "
            "support varies by accelerator, operating system, and model."
        ),
        "dtype": "Inference precision",
        "dtype_info": (
            "auto (recommended) lets Transformers follow the model configuration. bfloat16 is preferred on modern "
            "accelerators that support BF16; float16 is widely used on GPUs; float32 provides the largest numeric "
            "range but usually needs about twice the memory of 16-bit and runs slower. With 4/8-bit loading, this "
            "setting mainly affects unquantized layers and activations."
        ),
        "load": "Load model",
        "unload": "Unload model",
        "status": "No model is loaded.",
        "system": "System prompt (optional)",
        "query": "Write a message…",
        "submit": "Send",
        "clear": "Clear conversation",
        "max_tokens": "Maximum response tokens",
        "max_tokens_info": "Maximum number of new tokens generated for one response.",
        "top_p": "Top-p",
        "top_p_info": "Nucleus sampling probability threshold.",
        "temperature": "Temperature",
        "temperature_info": "Higher values make responses more varied.",
        "seed": "Random seed",
        "seed_info": "Use -1 for a random seed.",
        "thinking": "Enable model thinking mode",
        "thinking_info": "Enable the template's thinking mode when the selected model supports it.",
        "escape_html": "Escape HTML in responses",
        "escape_html_info": "Display generated HTML as text instead of rendering it.",
    },
    "zh": {
        "workspace": "快速测试",
        "header": "<div class='chat-page-header'><span>HUGGING FACE</span><h2>快速测试模型</h2><p>加载本地基础模型或 LoRA 检查点，在部署前检查模型回答。</p></div>",
        "model_path": "本地模型目录",
        "model_path_info": "包含 config.json 和权重文件的现有本地 Hugging Face 模型目录。",
        "adapter_path": "LoRA 适配器目录（可选）",
        "adapter_path_info": "现有本地适配器或检查点目录。测试基础模型或已合并模型时留空。",
        "quantization": "加载量化",
        "quantization_info": (
            "none（首次测试推荐）保留原始权重，兼容性最好，但占用显存最多；8 位通常可将权重显存降至约一半；"
            "4 位还能进一步降低显存，但可能影响速度或回答质量。8/4 位依赖与当前设备兼容的 bitsandbytes，"
            "能否使用取决于加速器、操作系统和模型。"
        ),
        "dtype": "推理精度",
        "dtype_info": (
            "auto（推荐）让 Transformers 按模型配置自动选择；支持 BF16 的新款加速器优先选 bfloat16；"
            "float16 在 GPU 上兼容较广；float32 数值范围最大，但显存通常约为 16 位的两倍且速度更慢。"
            "使用 4/8 位加载时，此项主要影响未量化层和激活值。"
        ),
        "load": "加载模型",
        "unload": "卸载模型",
        "status": "尚未加载模型。",
        "system": "系统提示词（可选）",
        "query": "输入消息……",
        "submit": "发送",
        "clear": "清空对话",
        "max_tokens": "最大回答长度",
        "max_tokens_info": "单次回答最多生成的新 token 数量。",
        "top_p": "Top-p",
        "top_p_info": "核采样概率阈值。",
        "temperature": "温度",
        "temperature_info": "数值越高，回答的变化越丰富。",
        "seed": "随机种子",
        "seed_info": "设置为 -1 时使用随机种子。",
        "thinking": "启用模型思考模式",
        "thinking_info": "所选模型支持时，启用模板的思考模式。",
        "escape_html": "转义回答中的 HTML",
        "escape_html_info": "将生成的 HTML 作为文本显示，不进行渲染。",
    },
    "ru": {
        "workspace": "Быстрый тест",
        "header": "<div class='chat-page-header'><span>HUGGING FACE</span><h2>Быстрая проверка модели</h2><p>Загрузите локальную базовую модель или LoRA и проверьте ответы перед развёртыванием.</p></div>",
        "model_path": "Каталог локальной модели",
        "model_path_info": "Существующий локальный каталог модели Hugging Face с config.json и файлами весов.",
        "adapter_path": "Каталог адаптера LoRA (необязательно)",
        "adapter_path_info": "Локальный каталог адаптера или контрольной точки. Оставьте пустым для базовой или объединённой модели.",
        "quantization": "Квантование при загрузке",
        "quantization_info": (
            "none (рекомендуется для первого теста) сохраняет исходные веса и лучшую совместимость, но требует "
            "больше видеопамяти. 8 бит примерно вдвое уменьшают память весов; 4 бита экономят ещё больше, но могут "
            "повлиять на скорость или качество. Для 8/4 бит нужна совместимая с устройством сборка bitsandbytes; "
            "поддержка зависит от ускорителя, ОС и модели."
        ),
        "dtype": "Точность инференса",
        "dtype_info": (
            "auto (рекомендуется) использует настройку модели. bfloat16 предпочтителен на современных ускорителях "
            "с BF16; float16 широко поддерживается GPU; float32 даёт больший числовой диапазон, но обычно требует "
            "примерно вдвое больше памяти и работает медленнее. При загрузке в 4/8 бит параметр в основном влияет "
            "на неквантованные слои и активации."
        ),
        "load": "Загрузить модель",
        "unload": "Выгрузить модель",
        "status": "Модель не загружена.",
        "system": "Системный промпт (необязательно)",
        "query": "Введите сообщение…",
        "submit": "Отправить",
        "clear": "Очистить диалог",
        "max_tokens": "Максимум токенов ответа",
        "max_tokens_info": "Максимальное число новых токенов в одном ответе.",
        "top_p": "Top-p",
        "top_p_info": "Порог вероятности nucleus sampling.",
        "temperature": "Температура",
        "temperature_info": "Более высокое значение повышает разнообразие ответов.",
        "seed": "Случайное зерно",
        "seed_info": "Используйте -1 для случайного значения.",
        "thinking": "Режим размышления модели",
        "thinking_info": "Включает режим размышления шаблона, если модель его поддерживает.",
        "escape_html": "Экранировать HTML в ответах",
        "escape_html_info": "Показывать созданный HTML как текст.",
    },
    "ko": {
        "workspace": "빠른 테스트",
        "header": "<div class='chat-page-header'><span>HUGGING FACE</span><h2>빠른 모델 테스트</h2><p>로컬 기본 모델 또는 LoRA 체크포인트를 로드하여 배포 전에 응답을 확인합니다.</p></div>",
        "model_path": "로컬 모델 디렉터리",
        "model_path_info": "config.json과 가중치 파일이 있는 기존 로컬 Hugging Face 모델 디렉터리입니다.",
        "adapter_path": "LoRA 어댑터 디렉터리(선택)",
        "adapter_path_info": "기존 로컬 어댑터 또는 체크포인트 디렉터리입니다. 기본 또는 병합 모델은 비워 두세요.",
        "quantization": "로드 양자화",
        "quantization_info": (
            "none(첫 테스트 권장)은 원본 가중치를 유지해 호환성이 가장 좋지만 VRAM을 가장 많이 사용합니다. "
            "8비트는 가중치 메모리를 대략 절반으로 줄이고, 4비트는 더 줄이지만 속도나 응답 품질에 영향을 "
            "줄 수 있습니다. 8/4비트에는 현재 장치와 호환되는 bitsandbytes 빌드가 필요하며 가속기, 운영체제, "
            "모델에 따라 지원 여부가 달라집니다."
        ),
        "dtype": "추론 정밀도",
        "dtype_info": (
            "auto(권장)는 Transformers가 모델 설정을 따르게 합니다. BF16을 지원하는 최신 가속기에서는 "
            "bfloat16이 적합하고, float16은 GPU에서 널리 사용됩니다. float32는 수치 범위가 가장 넓지만 "
            "보통 16비트보다 약 두 배의 메모리가 필요하고 느립니다. 4/8비트 로드에서는 이 설정이 주로 "
            "양자화되지 않은 레이어와 활성값에 적용됩니다."
        ),
        "load": "모델 로드",
        "unload": "모델 언로드",
        "status": "로드된 모델이 없습니다.",
        "system": "시스템 프롬프트(선택)",
        "query": "메시지 입력…",
        "submit": "보내기",
        "clear": "대화 지우기",
        "max_tokens": "최대 응답 토큰",
        "max_tokens_info": "한 응답에서 생성할 최대 새 토큰 수입니다.",
        "top_p": "Top-p",
        "top_p_info": "핵 샘플링 확률 임계값입니다.",
        "temperature": "온도",
        "temperature_info": "값이 높을수록 응답이 다양해집니다.",
        "seed": "랜덤 시드",
        "seed_info": "-1이면 무작위 시드를 사용합니다.",
        "thinking": "모델 사고 모드 사용",
        "thinking_info": "선택한 모델이 지원할 때 템플릿 사고 모드를 사용합니다.",
        "escape_html": "응답 HTML 이스케이프",
        "escape_html_info": "생성된 HTML을 렌더링하지 않고 텍스트로 표시합니다.",
    },
    "ja": {
        "workspace": "クイックテスト",
        "header": "<div class='chat-page-header'><span>HUGGING FACE</span><h2>モデルをすばやくテスト</h2><p>ローカルのベースモデルまたは LoRA を読み込み、展開前に応答を確認します。</p></div>",
        "model_path": "ローカルモデルディレクトリ",
        "model_path_info": "config.json と重みファイルを含む既存のローカル Hugging Face モデルディレクトリ。",
        "adapter_path": "LoRA アダプターディレクトリ（任意）",
        "adapter_path_info": "既存のローカルアダプターまたはチェックポイント。ベースまたはマージ済みモデルでは空欄にします。",
        "quantization": "読み込み時の量子化",
        "quantization_info": (
            "none（初回テスト推奨）は元の重みを保つため互換性が最も高い一方、VRAM を最も多く使います。"
            "8 ビットは重みのメモリをおよそ半分にし、4 ビットはさらに削減しますが、速度や応答品質に"
            "影響する場合があります。8/4 ビットには現在のデバイスに対応した bitsandbytes が必要で、"
            "アクセラレータ、OS、モデルによって対応状況が異なります。"
        ),
        "dtype": "推論精度",
        "dtype_info": (
            "auto（推奨）は Transformers にモデル設定を使わせます。BF16 対応の新しいアクセラレータでは "
            "bfloat16 が適し、float16 は GPU で広く使われます。float32 は数値範囲が最も広い一方、通常は "
            "16 ビットの約 2 倍のメモリを使い低速です。4/8 ビット読み込み時は、主に非量子化レイヤーと"
            "活性値に適用されます。"
        ),
        "load": "モデルを読み込む",
        "unload": "モデルをアンロード",
        "status": "モデルは読み込まれていません。",
        "system": "システムプロンプト（任意）",
        "query": "メッセージを入力…",
        "submit": "送信",
        "clear": "会話を消去",
        "max_tokens": "最大応答トークン",
        "max_tokens_info": "1 回の応答で生成する新しいトークンの最大数。",
        "top_p": "Top-p",
        "top_p_info": "Nucleus sampling の確率しきい値。",
        "temperature": "温度",
        "temperature_info": "値を高くすると応答の多様性が増します。",
        "seed": "乱数シード",
        "seed_info": "-1 でランダムなシードを使用します。",
        "thinking": "モデルの思考モードを有効化",
        "thinking_info": "選択したモデルが対応する場合にテンプレートの思考モードを有効にします。",
        "escape_html": "応答内の HTML をエスケープ",
        "escape_html_info": "生成された HTML をレンダリングせずテキストとして表示します。",
    },
}


def _component(label_key: str, info_key: str | None = None) -> dict[str, dict[str, str]]:
    output = {}
    for language in LANGUAGES:
        output[language] = {"label": CHAT_TEXT[language][label_key]}
        if info_key:
            output[language]["info"] = CHAT_TEXT[language][info_key]
    return output


CHAT_LOCALES = {
    "chat_workspace_btn": {language: {"value": CHAT_TEXT[language]["workspace"]} for language in LANGUAGES},
    "chat_header": {language: {"value": CHAT_TEXT[language]["header"]} for language in LANGUAGES},
    "chat_model_path": _component("model_path", "model_path_info"),
    "chat_adapter_path": _component("adapter_path", "adapter_path_info"),
    "chat_quantization": _component("quantization", "quantization_info"),
    "chat_dtype": _component("dtype", "dtype_info"),
    "chat_load_btn": {language: {"value": CHAT_TEXT[language]["load"]} for language in LANGUAGES},
    "chat_unload_btn": {language: {"value": CHAT_TEXT[language]["unload"]} for language in LANGUAGES},
    "chat_status": {language: {"value": CHAT_TEXT[language]["status"]} for language in LANGUAGES},
    "chat_system": {language: {"placeholder": CHAT_TEXT[language]["system"]} for language in LANGUAGES},
    "chat_query": {language: {"placeholder": CHAT_TEXT[language]["query"]} for language in LANGUAGES},
    "chat_submit_btn": {language: {"value": CHAT_TEXT[language]["submit"]} for language in LANGUAGES},
    "chat_clear_btn": {language: {"value": CHAT_TEXT[language]["clear"]} for language in LANGUAGES},
    "chat_max_tokens": _component("max_tokens", "max_tokens_info"),
    "chat_top_p": _component("top_p", "top_p_info"),
    "chat_temperature": _component("temperature", "temperature_info"),
    "chat_seed": _component("seed", "seed_info"),
    "chat_thinking": _component("thinking", "thinking_info"),
    "chat_escape_html": _component("escape_html", "escape_html_info"),
}


CHAT_ALERTS = {
    "model_missing": {
        "en": "Select an existing local model directory.",
        "zh": "请选择现有的本地模型目录。",
        "ru": "Выберите существующий каталог локальной модели.",
        "ko": "기존 로컬 모델 디렉터리를 선택하세요.",
        "ja": "既存のローカルモデルディレクトリを選択してください。",
    },
    "adapter_missing": {
        "en": "The LoRA adapter directory does not exist.",
        "zh": "LoRA 适配器目录不存在。",
        "ru": "Каталог адаптера LoRA не существует.",
        "ko": "LoRA 어댑터 디렉터리가 없습니다.",
        "ja": "LoRA アダプターディレクトリが存在しません。",
    },
    "already_loaded": {
        "en": "Unload the current model before loading another one.",
        "zh": "请先卸载当前模型，再加载其他模型。",
        "ru": "Выгрузите текущую модель перед загрузкой другой.",
        "ko": "다른 모델을 로드하기 전에 현재 모델을 언로드하세요.",
        "ja": "別のモデルを読み込む前に現在のモデルをアンロードしてください。",
    },
    "load_failed": {
        "en": "Model loading failed: {error}",
        "zh": "模型加载失败：{error}",
        "ru": "Не удалось загрузить модель: {error}",
        "ko": "모델 로드 실패: {error}",
        "ja": "モデルの読み込みに失敗しました: {error}",
    },
    "not_loaded": {
        "en": "Load a model before sending a message.",
        "zh": "请先加载模型，再发送消息。",
        "ru": "Загрузите модель перед отправкой сообщения.",
        "ko": "메시지를 보내기 전에 모델을 로드하세요.",
        "ja": "メッセージを送信する前にモデルを読み込んでください。",
    },
    "empty_query": {
        "en": "Enter a message first.",
        "zh": "请先输入消息。",
        "ru": "Сначала введите сообщение.",
        "ko": "먼저 메시지를 입력하세요.",
        "ja": "先にメッセージを入力してください。",
    },
}
