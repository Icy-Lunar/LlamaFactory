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

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_beginner_guide_covers_the_complete_first_training_path():
    guide = (PROJECT_ROOT / "BEGINNER_GUIDE_ZH.md").read_text(encoding="utf-8")
    required_topics = (
        "start_multibackend.cmd",
        "start_multibackend.ps1",
        "start_multibackend.sh",
        "start_wizard.ps1",
        "start_wizard.sh",
        "alpaca_zh_demo",
        "dataset_info.json",
        "register_my_dataset.py",
        "显存估计",
        "eval_steps = save_steps",
        "TensorBoard",
        "checkpoint",
        "适配器合并",
        "training_args.yaml",
        "webui_subprocess.log",
    )
    for topic in required_topics:
        assert topic in guide
    assert guide.count("```") % 2 == 0


def test_primary_chinese_docs_link_to_beginner_guide():
    for relative in ("README_zh.md", "MULTIBACKEND_DEPLOYMENT.md"):
        content = (PROJECT_ROOT / relative).read_text(encoding="utf-8")
        assert "BEGINNER_GUIDE_ZH.md" in content
