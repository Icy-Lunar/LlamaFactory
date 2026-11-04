"""Hugging Face-only quick-test chat workspace."""

import inspect
from typing import TYPE_CHECKING

from ...extras.packages import is_gradio_available
from ..locales import LOCALES


if is_gradio_available():
    import gradio as gr


if TYPE_CHECKING:
    from gradio.components import Component

    from ..engine import Engine


def create_chat_tab(engine: "Engine") -> dict[str, "Component"]:
    lang = engine.manager.get_elem_by_id("top.lang")

    header = gr.HTML(LOCALES["chat_header"]["en"]["value"], elem_classes="chat-page-header-wrap")
    with gr.Row(elem_classes="chat-config-card"):
        with gr.Column(scale=3, min_width=320):
            model_path = gr.Textbox()
            adapter_path = gr.Textbox()
        with gr.Column(scale=2, min_width=280):
            with gr.Row():
                quantization = gr.Dropdown(choices=["none", "8", "4"], value="none")
                dtype = gr.Dropdown(choices=["auto", "float16", "bfloat16", "float32"], value="auto")

    with gr.Row(elem_classes="chat-model-actions"):
        load_btn = gr.Button(variant="primary")
        unload_btn = gr.Button()
    status = gr.Textbox(show_label=False, interactive=False)

    with gr.Column(visible=False, elem_classes="chat-session-card") as chat_box:
        chatbot_parameters = inspect.signature(gr.Chatbot.__init__).parameters
        chatbot_kwargs = {"type": "messages", "height": 520, "show_label": False}
        if "buttons" in chatbot_parameters:
            chatbot_kwargs["buttons"] = ["copy"]
        elif "show_copy_button" in chatbot_parameters:
            chatbot_kwargs["show_copy_button"] = True
        if "resizable" in chatbot_parameters:
            chatbot_kwargs["resizable"] = True
        if "allow_tags" in chatbot_parameters:
            chatbot_kwargs["allow_tags"] = False
        chatbot = gr.Chatbot(**chatbot_kwargs)
        messages = gr.State([])
        system = gr.Textbox(show_label=False, lines=2)
        query = gr.Textbox(show_label=False, lines=4)
        with gr.Row():
            submit_btn = gr.Button(variant="primary", scale=3)
            clear_btn = gr.Button(scale=1)
        with gr.Accordion(open=False):
            with gr.Row():
                max_tokens = gr.Slider(minimum=8, maximum=8192, value=1024, step=1)
                top_p = gr.Slider(minimum=0.01, maximum=1.0, value=0.7, step=0.01)
                temperature = gr.Slider(minimum=0.01, maximum=1.5, value=0.95, step=0.01)
            with gr.Row():
                seed = gr.Number(value=-1, precision=0)
                thinking = gr.Checkbox(value=True)
                escape_html = gr.Checkbox(value=True)

    load_btn.click(
        engine.chatter.load_model,
        [lang, model_path, adapter_path, quantization, dtype],
        [status],
    ).then(lambda: gr.Column(visible=engine.chatter.loaded), outputs=[chat_box])
    unload_btn.click(engine.chatter.unload_model, [lang], [status]).then(
        lambda: ([], []), outputs=[chatbot, messages]
    ).then(lambda: gr.Column(visible=engine.chatter.loaded), outputs=[chat_box])

    submit_btn.click(
        engine.chatter.append,
        [chatbot, messages, lang, query, escape_html],
        [chatbot, messages, query],
    ).then(
        engine.chatter.stream,
        [
            chatbot,
            messages,
            lang,
            system,
            max_tokens,
            top_p,
            temperature,
            seed,
            escape_html,
            thinking,
        ],
        [chatbot, messages],
    )
    query.submit(
        engine.chatter.append,
        [chatbot, messages, lang, query, escape_html],
        [chatbot, messages, query],
    ).then(
        engine.chatter.stream,
        [
            chatbot,
            messages,
            lang,
            system,
            max_tokens,
            top_p,
            temperature,
            seed,
            escape_html,
            thinking,
        ],
        [chatbot, messages],
    )
    clear_btn.click(lambda: ([], []), outputs=[chatbot, messages])

    return {
        "chat_header": header,
        "chat_model_path": model_path,
        "chat_adapter_path": adapter_path,
        "chat_quantization": quantization,
        "chat_dtype": dtype,
        "chat_load_btn": load_btn,
        "chat_unload_btn": unload_btn,
        "chat_status": status,
        "chat_box": chat_box,
        "chatbot": chatbot,
        "messages": messages,
        "chat_system": system,
        "chat_query": query,
        "chat_submit_btn": submit_btn,
        "chat_clear_btn": clear_btn,
        "chat_max_tokens": max_tokens,
        "chat_top_p": top_p,
        "chat_temperature": temperature,
        "chat_seed": seed,
        "chat_thinking": thinking,
        "chat_escape_html": escape_html,
    }
