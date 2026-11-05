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

"""Explicit, test-only preparation for the product's local-directory boundary.

This module is excluded from deployment archives. It never patches the product
loader or suppresses a failed download; missing/gated fixtures fail the test.
"""

from functools import lru_cache
from pathlib import Path
from typing import Any

from huggingface_hub import snapshot_download


METADATA_PATTERNS = ("*.json", "*.txt", "*.model", "*.tiktoken", "*.jinja", "*.py")


@lru_cache(maxsize=64)
def local_model_path(model: str, *, weights: bool = True) -> str:
    path = Path(model).expanduser()
    if path.is_dir():
        return str(path.resolve())
    # Never accidentally download production-size weights in a tokenizer test.
    if weights and not model.startswith("llamafactory/tiny-random-"):
        raise ValueError("Only tiny test repositories may download weights; provide a local fixture directory.")
    patterns = list(METADATA_PATTERNS)
    if weights:
        patterns.extend(("*.safetensors", "*.bin"))
    return snapshot_download(model, allow_patterns=patterns)


def local_model_args(arguments: dict[str, Any]) -> dict[str, Any]:
    result = dict(arguments)
    result["model_name_or_path"] = local_model_path(result["model_name_or_path"])
    return result
