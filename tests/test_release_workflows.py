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

import pytest
import yaml


WORKFLOWS = Path(__file__).resolve().parents[1] / ".github" / "workflows"
UPSTREAM = "github.repository == 'hiyouga/LLaMA-Factory'"
RELEASE_GATE = f"{UPSTREAM} && (github.event_name != 'release' || !github.event.release.prerelease)"


@pytest.mark.parametrize("workflow,job", [("publish.yml", "publish"), ("docker_npu.yml", "build")])
def test_publication_only_workflows_require_upstream_and_non_preview_release(workflow, job):
    document = yaml.safe_load((WORKFLOWS / workflow).read_text(encoding="utf-8"))
    assert document["jobs"][job]["if"] == RELEASE_GATE


def test_cuda_docker_keeps_fork_builds_without_upstream_credentials_or_push():
    document = yaml.safe_load((WORKFLOWS / "docker.yml").read_text(encoding="utf-8"))
    job = document["jobs"]["build"]
    assert job["if"] == (f"github.event_name != 'release' || ({UPSTREAM} && !github.event.release.prerelease)")
    push_gate = "${{ " + UPSTREAM + " && github.event_name != 'pull_request' }}"
    login = next(step for step in job["steps"] if step.get("uses", "").startswith("docker/login-action@"))
    build = next(step for step in job["steps"] if step.get("uses", "").startswith("docker/build-push-action@"))
    assert login["if"] == push_gate
    assert build["with"]["push"] == push_gate
