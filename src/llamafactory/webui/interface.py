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

import os
import platform

from ..extras.misc import fix_proxy, is_env_enabled
from ..extras.packages import is_gradio_available
from .common import save_config
from .components import create_export_tab, create_footer, create_train_tab
from .css import CSS
from .engine import Engine
from .locales import LOCALES


if is_gradio_available():
    import gradio as gr


def _switch_workspace(lang: str, show_merge: bool):
    return (
        gr.Button(
            value=LOCALES["train_workspace_btn"][lang]["value"],
            variant="secondary" if show_merge else "primary",
        ),
        gr.Button(
            value=LOCALES["merge_workspace_btn"][lang]["value"],
            variant="primary" if show_merge else "secondary",
        ),
        gr.Column(visible=not show_merge),
        gr.Column(visible=show_merge),
    )


def create_ui(demo_mode: bool = False) -> "gr.Blocks":
    engine = Engine(demo_mode=demo_mode)
    hostname = os.getenv("HOSTNAME", os.getenv("COMPUTERNAME", platform.node())).split(".")[0]

    theme = gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="blue",
        neutral_hue="slate",
    ).set(
        block_label_background_fill="transparent",
        block_label_background_fill_dark="transparent",
        block_label_border_width="0px",
        block_label_shadow="none",
        block_label_padding="0px",
        block_label_text_color="*body_text_color",
        block_label_text_color_dark="*body_text_color",
        block_title_background_fill="transparent",
        block_title_text_color="*body_text_color",
        block_title_text_color_dark="*body_text_color",
        input_background_fill_dark="#101b2c",
        input_border_color="#cbd6e5",
        input_border_color_dark="#3a4c65",
    )
    with gr.Blocks(title=f"Cyrene Yield Training ({hostname})", theme=theme, css=CSS) as demo:
        with gr.Row(elem_classes="product-header"):
            with gr.Column(scale=3, min_width=280):
                title = gr.HTML(elem_classes="product-title", padding=False)
                subtitle = gr.HTML(elem_classes="product-subtitle", padding=False)

            with gr.Row(elem_classes="enterprise-workspace-nav"):
                train_workspace_btn = gr.Button(LOCALES["train_workspace_btn"]["en"]["value"], variant="primary")
                if not demo_mode:
                    merge_workspace_btn = gr.Button(LOCALES["merge_workspace_btn"]["en"]["value"])
            lang = gr.Dropdown(
                choices=["en", "ru", "zh", "ko", "ja"],
                value="zh",
                min_width=100,
                scale=0,
                elem_classes="compact-language-row",
            )
        engine.manager.add_elems("top", {"lang": lang})
        if demo_mode:
            gr.DuplicateButton(value="Duplicate Space for private use", elem_classes="duplicate-button")

        engine.manager.add_elems("head", {"title": title, "subtitle": subtitle})

        with gr.Column(elem_classes="enterprise-workspace-panel") as train_workspace:
            engine.manager.add_elems("train", create_train_tab(engine))

        workspace_elems = {"train_workspace_btn": train_workspace_btn}
        if not demo_mode:
            with gr.Column(visible=False, elem_classes="enterprise-workspace-panel") as merge_workspace:
                engine.manager.add_elems("export", create_export_tab(engine))

            workspace_elems["merge_workspace_btn"] = merge_workspace_btn

        engine.manager.add_elems("workspace", workspace_elems)

        lang: gr.Dropdown = engine.manager.get_elem_by_id("top.lang")
        if not demo_mode:
            workspace_outputs = [
                train_workspace_btn,
                merge_workspace_btn,
                train_workspace,
                merge_workspace,
            ]
            train_workspace_btn.click(
                lambda current_lang: _switch_workspace(current_lang, False),
                [lang],
                workspace_outputs,
                queue=False,
            )
            merge_workspace_btn.click(
                lambda current_lang: _switch_workspace(current_lang, True),
                [lang],
                workspace_outputs,
                queue=False,
            )

        engine.manager.add_elems("footer", create_footer())
        demo.load(engine.resume, outputs=engine.manager.get_elem_list(), concurrency_limit=None)
        lang.change(engine.change_lang, [lang], engine.manager.get_elem_list(), queue=False)
        lang.input(save_config, inputs=[lang], queue=False)

    return demo


def run_web_ui() -> None:
    gradio_ipv6 = is_env_enabled("GRADIO_IPV6")
    gradio_share = is_env_enabled("GRADIO_SHARE")
    server_name = os.getenv("GRADIO_SERVER_NAME", "[::]" if gradio_ipv6 else "0.0.0.0")
    print("Visit http://ip:port for Web UI, e.g., http://127.0.0.1:7860")
    fix_proxy(ipv6_enabled=gradio_ipv6)
    create_ui().queue().launch(share=gradio_share, server_name=server_name, inbrowser=True)
