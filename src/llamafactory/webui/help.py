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

"""Accessible, localized field help shared by the training and merge workspaces."""

from html import escape


def field_help(label: str, text: str, lang: str, key: str) -> str:
    """Render trusted resource text without allowing it to inject markup.

    Gradio's info fields accept sanitized HTML. The non-labelable trigger does not
    steal the enclosing label from its input. Help stays local across rerenders.
    """
    from .help_locales import HELP_LABELS

    name = HELP_LABELS.get(lang, HELP_LABELS["en"]).format(label=label)
    tooltip_id = f"help-{key.replace('.', '-')}"
    return (
        '<span class="field-help">'
        '<span class="field-help-trigger" role="button" tabindex="0">'
        f'<span class="field-help-label">{escape(name)}</span></span>'
        f'<span class="field-help-content" id="{escape(tooltip_id, quote=True)}" role="tooltip">'
        f"{escape(text)}</span></span>"
    )


HELP_JS = """() => {
    const root = document.querySelector('.gradio-container');
    if (!root || root.dataset.fieldHelpReady) return;
    root.dataset.fieldHelpReady = 'true';
    const annotate = () => {
        root.querySelectorAll('.field-help').forEach(help => {
            const trigger = help.querySelector('.field-help-trigger');
            const content = help.querySelector('.field-help-content');
            if (!trigger || !content) return;
            // Gradio sanitizes aria attributes in info HTML; restore only our own metadata.
            trigger.setAttribute('tabindex', '0');
            trigger.setAttribute('aria-label', trigger.textContent.trim());
            trigger.setAttribute('aria-describedby', content.id);
        });
    };
    annotate();
    new MutationObserver(annotate).observe(root, {childList: true, subtree: true});
    root.addEventListener('click', event => {
        const trigger = event.target.closest('.field-help-trigger');
        if (!trigger) return;
        event.preventDefault();
        event.stopPropagation();
        trigger.focus();
    }, true);
    root.addEventListener('keydown', event => {
        const trigger = event.target.closest('.field-help-trigger');
        if (!trigger) return;
        if (event.key === 'Escape') { event.preventDefault(); trigger.blur(); }
        if (event.key === 'Enter' || event.key === ' ') event.preventDefault();
    });
}"""
