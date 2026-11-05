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

CSS = r"""
.duplicate-button {
  margin: auto !important;
  color: white !important;
  background: black !important;
  border-radius: 100vh !important;
}

.gradio-container {
  --font: "Segoe UI", "Microsoft YaHei", system-ui, sans-serif;
  --cy-accent: #2563eb;
  --cy-tint: rgba(37, 99, 235, 0.065);
  --cy-line: #dce4f0;
  --cy-canvas: #f4f7fc;
  --cy-surface: #ffffff;
  --cy-text: #182940;
  --cy-muted: #55677f;
  max-width: 1360px !important;
  padding: 20px clamp(16px, 3vw, 40px) 36px !important;
  background:
    radial-gradient(circle at 98% 0%, var(--cy-tint), transparent 30rem),
    var(--cy-canvas);
  color: var(--cy-text);
  --body-text-color: var(--cy-text);
  --body-text-color-subdued: var(--cy-muted);
  --background-fill-primary: var(--cy-surface);
  --background-fill-secondary: var(--cy-canvas);
  --border-color-primary: var(--cy-line);
}

.dark .gradio-container {
  --cy-accent: #82b1ff;
  --cy-tint: rgba(99, 153, 255, 0.10);
  --cy-line: #2c3c53;
  --cy-canvas: #0f1726;
  --cy-surface: #182335;
  --cy-text: #e7edf6;
  --cy-muted: #adbbce;
}

.product-header {
  align-items: center !important;
  gap: 20px !important;
  padding: 4px 0 18px;
  border-bottom: 1px solid var(--cy-line);
}

.product-header > .column {
  gap: 6px !important;
}

.product-header center { text-align: left; }

.product-title h1 {
  margin: 0 !important;
  font-size: clamp(20px, 2vw, 27px);
  letter-spacing: -0.025em;
  line-height: 1.35;
}

.product-subtitle p {
  margin: 0 !important;
  color: var(--body-text-color-subdued);
  font-size: 13px;
}

.compact-language-row {
  flex: 1 1 auto !important;
  width: 100%;
  min-width: 0 !important;
  border: 0 !important;
  background: transparent !important;
  margin: 0;
}

.product-header > .form:has(.compact-language-row) {
  flex: 0 0 112px !important;
  min-width: 112px !important;
  border: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
  overflow: visible !important;
}

.enterprise-workspace-nav {
  flex: 0 1 520px !important;
  width: min(100%, 520px);
  margin: 0;
  gap: 5px !important;
  padding: 5px;
  border: 1px solid var(--border-color-primary);
  border-radius: 14px;
  background: color-mix(in srgb, var(--background-fill-primary) 92%, transparent);
}

.chat-page-header-wrap {
  padding: 18px 4px 8px;
}

.chat-page-header span {
  color: var(--cy-accent);
  font-size: 12px;
  font-weight: 750;
  letter-spacing: 0.13em;
}

.chat-page-header h2 {
  margin: 5px 0 6px;
  font-size: clamp(22px, 2vw, 28px);
  letter-spacing: -0.025em;
}

.chat-page-header p {
  max-width: 780px;
  margin: 0;
  color: var(--body-text-color-subdued);
  line-height: 1.6;
}

.chat-config-card,
.chat-session-card {
  padding: 18px !important;
  border: 1px solid var(--border-color-primary) !important;
  border-radius: 16px !important;
  background: var(--background-fill-primary) !important;
  box-shadow: 0 4px 18px rgba(15, 23, 42, 0.035);
}

.chat-config-card {
  gap: 18px !important;
  margin-bottom: 12px;
}

.chat-model-actions {
  justify-content: flex-end;
  gap: 10px !important;
}

.chat-model-actions button {
  flex: 0 1 220px !important;
  min-height: 44px;
  border-radius: 10px !important;
  font-weight: 650 !important;
}

.chat-session-card {
  margin-top: 14px;
}

.enterprise-workspace-nav button {
  min-width: 120px !important;
  min-height: 42px;
  border: 0 !important;
  border-radius: 10px !important;
  font-weight: 680 !important;
}

.enterprise-workspace-nav button.primary {
  color: white !important;
  background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
  box-shadow: 0 7px 18px rgba(37, 99, 235, 0.24);
}

.enterprise-workspace-panel {
  min-width: 0;
}

.oobe-hero {
  position: relative;
  overflow: hidden;
  margin: 4px 0 0;
  padding: 18px 22px;
  border: 1px solid color-mix(in srgb, var(--border-color-primary) 72%, #2563eb 28%);
  border-radius: 20px;
  background:
    radial-gradient(circle at 88% 12%, rgba(37, 99, 235, 0.18), transparent 34%),
    linear-gradient(135deg, var(--background-fill-primary), var(--background-fill-secondary));
  box-shadow: none;
}

.oobe-hero::after {
  pointer-events: none;
  content: "";
  position: absolute;
  width: 180px;
  height: 180px;
  right: -56px;
  bottom: -112px;
  border: 28px solid rgba(37, 99, 235, 0.08);
  border-radius: 50%;
}

.oobe-hero h1,
.oobe-page-header h2 {
  margin: 5px 0 8px;
  color: var(--body-text-color);
  letter-spacing: -0.025em;
}

.oobe-hero h1 {
  font-size: clamp(20px, 2vw, 26px);
  line-height: 1.15;
}

.oobe-hero p,
.oobe-page-header p {
  max-width: 820px;
  margin: 0;
  color: var(--body-text-color-subdued);
  line-height: 1.65;
}

.oobe-kicker {
  color: var(--cy-accent);
  font-size: 12px;
  font-weight: 750;
  letter-spacing: 0.13em;
}

.oobe-page {
  gap: 16px !important;
  max-width: 1200px;
  margin-inline: auto;
}

.oobe-page-header {
  padding: 10px 2px 4px;
}

.oobe-page-header h2 {
  font-size: clamp(22px, 2vw, 28px);
}

.oobe-stepper {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  margin-top: 18px;
}

.oobe-step {
  position: relative;
  display: flex;
  align-items: center;
  gap: 9px;
  min-width: 0;
  padding: 10px 8px;
  border: 0;
  border-bottom: 2px solid var(--cy-line);
  border-radius: 0;
  color: var(--body-text-color-subdued);
  background: transparent;
  transition: border-color 160ms ease, background 160ms ease, color 160ms ease;
}

.oobe-step.is-active {
  border-color: var(--cy-accent);
  color: var(--body-text-color);
  background: var(--cy-tint);
}

.oobe-step.is-done {
  color: var(--cy-accent);
  border-color: var(--cy-accent);
  background: transparent;
}

.oobe-step-number {
  display: grid;
  flex: 0 0 28px;
  width: 28px;
  height: 28px;
  place-items: center;
  border: 1px solid currentColor;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 750;
}

.oobe-step.is-active .oobe-step-number {
  color: white;
  border-color: #2563eb;
  background: #2563eb;
}

.oobe-step-label {
  overflow: hidden;
  font-size: 13px;
  font-weight: 650;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.oobe-card {
  padding: 20px !important;
  border: 1px solid var(--border-color-primary) !important;
  border-radius: 16px !important;
  background: var(--background-fill-primary) !important;
  box-shadow: 0 4px 18px rgba(15, 23, 42, 0.035);
}

.oobe-card > .wrap:first-child,
.oobe-card > div:first-child {
  margin-top: 0 !important;
}

.oobe-card h3 {
  margin: 0 0 3px;
  font-size: 17px;
}

.oobe-card p {
  margin-top: 0;
  color: var(--body-text-color-subdued);
}

.oobe-nav {
  justify-content: flex-end;
  gap: 10px !important;
  padding-top: 4px;
}

.oobe-nav button {
  flex: 0 1 280px !important;
  min-height: 46px;
  border-radius: 11px !important;
  font-weight: 650 !important;
}

.oobe-recommendation {
  display: grid;
  grid-template-columns: minmax(180px, 0.35fr) minmax(0, 1fr);
  gap: 18px;
  align-items: center;
  padding: 16px 18px;
  border: 1px solid rgba(37, 99, 235, 0.28);
  border-radius: 14px;
  background: rgba(37, 99, 235, 0.075);
}

.oobe-recommendation div {
  display: flex;
  flex-direction: column;
}

.oobe-recommendation strong {
  color: #2563eb;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.oobe-recommendation span {
  margin-top: 3px;
  font-size: 20px;
  font-weight: 730;
}

.oobe-recommendation p {
  margin: 0;
  color: var(--body-text-color-subdued);
  line-height: 1.55;
}

.oobe-questionnaire {
  border-color: color-mix(in srgb, var(--primary-500) 35%, var(--border-color-primary));
  background: linear-gradient(145deg, color-mix(in srgb, var(--primary-50) 72%, transparent), transparent 58%);
}

.oobe-questionnaire .gradio-radio {
  min-width: min(100%, 18rem);
}

.oobe-branch-selector {
  margin-bottom: 0.8rem;
  padding: 0.9rem 1rem;
  border: 1px solid color-mix(in srgb, var(--primary-500) 26%, var(--border-color-primary));
  border-radius: 0.9rem;
  background: var(--background-fill-primary);
}

.oobe-branch-selector label {
  min-height: 2.5rem;
}

.oobe-branch-panel {
  border-left: 4px solid var(--primary-500) !important;
}

.oobe-branch-panel h3 {
  margin-bottom: 0.2rem;
}

.oobe-profile-result {
  margin-top: 0.9rem;
  overflow: hidden;
  border: 1px solid color-mix(in srgb, var(--primary-500) 32%, var(--border-color-primary));
  border-radius: 0.9rem;
  background: var(--background-fill-primary);
}

.oobe-profile-result header {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  padding: 1rem 1.1rem;
  background: var(--cy-tint);
}

.oobe-profile-result header > span {
  display: grid;
  width: 1.65rem;
  height: 1.65rem;
  flex: 0 0 1.65rem;
  place-items: center;
  border-radius: 999px;
  background: var(--primary-500);
  color: white;
  font-weight: 800;
}

.oobe-profile-result header strong {
  display: block;
  color: var(--body-text-color);
  font-size: 1rem;
}

.oobe-profile-result header p,
.oobe-profile-result footer,
.oobe-profile-reason {
  margin: 0.2rem 0 0;
  color: var(--body-text-color-subdued);
}

.oobe-profile-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0;
  padding: 0.25rem 1.1rem;
}

.oobe-profile-grid > div {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 0.2rem;
  padding: 0.8rem 0.65rem;
}

.oobe-profile-grid span {
  color: var(--body-text-color-subdued);
  font-size: 0.78rem;
}

.oobe-profile-grid strong {
  overflow: hidden;
  color: var(--body-text-color);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.oobe-profile-reason,
.oobe-profile-result footer {
  padding: 0 1.1rem 0.85rem;
}

.oobe-profile-result footer {
  padding-top: 0.8rem;
  border-top: 1px solid var(--border-color-primary);
  font-size: 0.84rem;
}

.oobe-alert {
  display: flex;
  gap: 0.65rem;
  align-items: center;
  margin-top: 0.8rem;
  padding: 0.8rem 1rem;
  border: 1px solid color-mix(in srgb, #dc2626 46%, var(--border-color-primary));
  border-radius: 0.8rem;
  background: color-mix(in srgb, #dc2626 10%, var(--cy-surface));
  color: var(--cy-text);
  font-weight: 650;
}

.oobe-alert span {
  display: grid;
  width: 1.45rem;
  height: 1.45rem;
  flex: 0 0 1.45rem;
  place-items: center;
  border-radius: 999px;
  background: #dc2626;
  color: white;
}

.oobe-memory-report {
  margin: 0.9rem 0;
  overflow: hidden;
  border: 1px solid var(--border-color-primary);
  border-radius: 0.9rem;
  background: var(--background-fill-primary);
}

.oobe-memory-report header {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  padding: 1rem 1.1rem;
}

.oobe-memory-report header > span {
  display: grid;
  width: 1.7rem;
  height: 1.7rem;
  flex: 0 0 1.7rem;
  place-items: center;
  border-radius: 999px;
  color: white;
  font-weight: 800;
}

.oobe-memory-report header strong {
  display: block;
  font-size: 1rem;
}

.oobe-memory-report header p {
  margin: 0.2rem 0 0;
  color: var(--body-text-color-subdued);
}

.oobe-memory-report.is-safe {
  border-color: color-mix(in srgb, #16a34a 45%, var(--border-color-primary));
}

.oobe-memory-report.is-safe header {
  background: color-mix(in srgb, #16a34a 12%, var(--cy-surface));
}

.oobe-memory-report.is-safe header > span {
  background: #16a34a;
}

.oobe-memory-report:not(.is-safe) {
  border-color: color-mix(in srgb, #d97706 48%, var(--border-color-primary));
}

.oobe-memory-report:not(.is-safe) header {
  background: color-mix(in srgb, #d97706 12%, var(--cy-surface));
}

.oobe-memory-report:not(.is-safe) header > span {
  background: #d97706;
}

.oobe-memory-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  padding: 0.35rem 0.55rem 0.65rem;
}

.oobe-memory-grid > div {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 0.2rem;
  padding: 0.65rem;
}

.oobe-memory-grid span {
  color: var(--body-text-color-subdued);
  font-size: 0.78rem;
}

.oobe-memory-grid strong {
  overflow-wrap: anywhere;
}

.oobe-risk-modal {
  position: fixed !important;
  z-index: 1000 !important;
  inset: 0 !important;
  overflow: auto;
  align-items: center;
  justify-content: center;
  padding: 1.25rem !important;
  border: 0 !important;
  border-radius: 0 !important;
  background: rgba(15, 23, 42, 0.68) !important;
  backdrop-filter: blur(3px);
}

.oobe-risk-modal:not(.hide) {
  display: flex;
}

.oobe-risk-modal.hide,
.modal-box.hide {
  display: none !important;
  pointer-events: none !important;
}

.oobe-risk-modal > .styler,
.oobe-risk-modal > .wrap,
.oobe-risk-modal > .form {
  width: min(100%, 38rem);
  margin: auto;
  padding: 1.2rem !important;
  border: 1px solid color-mix(in srgb, #dc2626 45%, var(--border-color-primary));
  border-radius: 1rem !important;
  background: var(--background-fill-primary) !important;
  box-shadow: 0 28px 80px rgba(15, 23, 42, 0.38);
}

.oobe-risk-dialog {
  text-align: center;
}

.oobe-risk-icon {
  display: grid;
  width: 3rem;
  height: 3rem;
  margin: 0 auto 0.8rem;
  place-items: center;
  border-radius: 999px;
  background: #dc2626;
  color: white;
  font-size: 1.4rem;
  font-weight: 850;
}

.oobe-risk-dialog h2 {
  margin: 0;
  font-size: 1.3rem;
}

.oobe-risk-dialog p {
  margin: 0.65rem 0 0;
  color: var(--body-text-color-subdued);
}

.oobe-risk-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  align-items: center;
  justify-content: center;
  margin: 1rem 0;
  padding: 0.75rem;
  border-radius: 0.75rem;
  background: color-mix(in srgb, #dc2626 10%, var(--cy-surface));
}

.oobe-advanced {
  border-radius: 13px !important;
}

.oobe-summary {
  overflow: hidden;
  border: 1px solid var(--border-color-primary);
  border-radius: 16px;
  background: var(--background-fill-primary);
  box-shadow: 0 12px 34px rgba(15, 23, 42, 0.065);
}

.oobe-summary-title {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  padding: 17px 19px;
  border-bottom: 1px solid var(--border-color-primary);
  background: var(--background-fill-secondary);
}

.oobe-summary-title span {
  font-size: 18px;
  font-weight: 730;
}

.oobe-summary-title em {
  color: var(--body-text-color-subdued);
  font-size: 12px;
  font-style: normal;
}

.oobe-summary-row {
  display: grid;
  grid-template-columns: minmax(120px, 0.28fr) minmax(0, 1fr);
  gap: 18px;
  padding: 13px 19px;
  border-bottom: 1px solid var(--border-color-primary);
}

.oobe-summary-row:last-child {
  border-bottom: 0;
}

.oobe-summary-row > span {
  color: var(--body-text-color-subdued);
  font-size: 13px;
}

.oobe-summary-row strong {
  overflow-wrap: anywhere;
  font-weight: 630;
}

.oobe-summary-row small {
  display: block;
  margin-top: 3px;
  color: var(--body-text-color-subdued);
  font-size: 12px;
  font-weight: 450;
}

.dark .oobe-hero,
.dark .oobe-card,
.dark .oobe-summary {
  box-shadow: none;
}

.dark .oobe-kicker,
.dark .oobe-recommendation strong {
  color: #7da7ff;
}

.merge-page {
  max-width: 1080px;
  margin-inline: auto;
  gap: 16px !important;
}

.merge-hero {
  position: relative;
  overflow: hidden;
  padding: 22px 26px;
  border: 1px solid color-mix(in srgb, var(--border-color-primary) 68%, #7c3aed 32%);
  border-radius: 20px;
  background:
    radial-gradient(circle at 90% 0%, rgba(124, 58, 237, 0.18), transparent 36%),
    linear-gradient(135deg, var(--background-fill-primary), var(--background-fill-secondary));
  box-shadow: 0 18px 46px rgba(15, 23, 42, 0.08);
}

.merge-hero::after {
  pointer-events: none;
  position: absolute;
  right: -42px;
  bottom: -72px;
  width: 150px;
  height: 150px;
  border: 24px solid rgba(124, 58, 237, 0.075);
  border-radius: 50%;
  content: "";
}

.merge-kicker {
  color: #7c3aed;
  font-size: 12px;
  font-weight: 780;
  letter-spacing: 0.13em;
}

.merge-hero h1 {
  margin: 6px 0 8px;
  color: var(--body-text-color);
  font-size: clamp(22px, 2.5vw, 30px);
  line-height: 1.16;
  letter-spacing: -0.025em;
}

.merge-hero p {
  max-width: 850px;
  margin: 0;
  color: var(--body-text-color-subdued);
  line-height: 1.65;
}

.merge-card {
  padding: 18px 20px 20px !important;
  border: 1px solid var(--border-color-primary) !important;
  border-radius: 16px !important;
  background: var(--background-fill-primary) !important;
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.055);
}

.merge-card h3 {
  margin: 0 0 5px;
  font-size: 17px;
}

.merge-card p {
  margin-top: 0;
  color: var(--body-text-color-subdued);
}

.merge-card .block:has(.prose) {
  padding: 0 !important;
  border: 0 !important;
  background: transparent !important;
}

.merge-source-card {
  border-left: 4px solid #7c3aed !important;
  background:
    linear-gradient(90deg, rgba(124, 58, 237, 0.065), transparent 38%),
    var(--background-fill-primary) !important;
}

.merge-action {
  min-height: 48px !important;
  border-radius: 12px !important;
  font-weight: 720 !important;
}

.merge-status textarea {
  min-height: 58px !important;
}

.dark .enterprise-workspace-nav,
.dark .merge-hero,
.dark .merge-card {
  box-shadow: none;
}

.dark .merge-kicker {
  color: #b59aff;
}

@media (max-width: 820px) {
  .oobe-hero {
    padding: 24px 22px;
  }

  .oobe-stepper {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .oobe-recommendation {
    grid-template-columns: 1fr;
  }

  .merge-hero {
    padding: 24px 22px;
  }
}

@media (max-width: 520px) {
  .oobe-stepper {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .oobe-summary-row {
    grid-template-columns: 1fr;
    gap: 3px;
  }

  .oobe-profile-grid {
    grid-template-columns: 1fr 1fr;
  }

  .oobe-memory-grid {
    grid-template-columns: 1fr 1fr;
  }
}

/* Field help remains local to its component: hover, keyboard focus, or tap. */
.gradio-container .block:has(.field-help) {
  overflow: visible !important;
  position: relative;
}

.gradio-container .block:has(.field-help:hover),
.gradio-container .block:has(.field-help:focus-within) {
  z-index: 1100 !important;
}

.gradio-container :is(.form, .styler, .gr-group):has(.field-help:hover),
.gradio-container :is(.form, .styler, .gr-group):has(.field-help:focus-within) {
  overflow: visible !important;
}

.gradio-container .field-help {
  position: absolute;
  top: 8px;
  right: 8px;
  display: inline-flex;
  z-index: 30;
  font-weight: 400;
}

.gradio-container .field-help-trigger {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  padding: 0;
  border: 1px solid var(--cy-line);
  border-radius: 50%;
  background: var(--input-background-fill);
  color: var(--cy-muted);
  font-size: 13px;
  font-weight: 700;
  line-height: 1;
  cursor: help;
}

.gradio-container .field-help-trigger::before {
  content: "?";
}

.gradio-container .field-help-label {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip-path: inset(50%);
  white-space: nowrap;
}

.gradio-container .field-help-trigger:hover,
.gradio-container .field-help-trigger:focus-visible {
  color: var(--cy-text);
  border-color: #60a5fa;
  outline: 2px solid #60a5fa;
  outline-offset: 2px;
}

.gradio-container .field-help-content {
  display: none;
  position: absolute;
  top: calc(100% + 6px);
  right: 0;
  width: min(320px, calc(100vw - 64px));
  padding: 12px 14px;
  border: 1px solid var(--cy-line);
  border-radius: 10px;
  background: var(--input-background-fill);
  color: var(--cy-text) !important;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);
  line-height: 1.65;
  font-size: 13px;
  text-align: start;
  white-space: normal;
  overflow-wrap: anywhere;
  cursor: auto;
}

.gradio-container .field-help:hover .field-help-content,
.gradio-container .field-help:focus-within .field-help-content {
  display: block;
}

.gradio-container .block:has(.field-help) [data-testid="block-info"],
.gradio-container .block:has(.field-help) > label > span {
  padding-right: 32px;
}

.gradio-container div:has(> .md > p > .field-help),
.gradio-container div:has(> .md > .field-help) {
  margin-bottom: 0 !important;
  height: 0;
}

.modal-box {
  position: fixed !important;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%); /* center horizontally */
  width: min(1000px, calc(100vw - 32px)) !important;
  max-height: calc(100dvh - 48px);
  overflow-y: auto;
  background-color: var(--input-background-fill);
  flex-wrap: nowrap !important;
  border: 1px solid var(--cy-line) !important;
  border-radius: 18px !important;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.35);
  z-index: 1000;
  padding: 20px !important;
}

.gradio-container .block:has(> .prose),
.gradio-container .block:has(> .html-container) {
  border: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}

.oobe-card > .styler,
.merge-card > .styler,
.oobe-advanced > .styler {
  background: transparent !important;
}

.oobe-card .form,
.merge-card .form,
.oobe-advanced .form {
  gap: 12px !important;
  border: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}

.oobe-card .block,
.oobe-advanced .block,
.merge-card .block {
  border-color: transparent !important;
  background: transparent !important;
}

.gradio-container input:not([type="checkbox"]):not([type="radio"]):not([type="range"]),
.gradio-container textarea,
.gradio-container .secondary-wrap {
  color: var(--cy-text);
  border-radius: 9px !important;
}

.gradio-container button {
  transition: background 150ms ease, border-color 150ms ease, box-shadow 150ms ease;
}

.gradio-container button:is(.primary, .secondary, .stop) {
  border-radius: 10px !important;
  min-height: 42px;
}

.gradio-container button.stop {
  color: #fff !important;
  background: #b91c1c !important;
  border-color: #b91c1c !important;
}

.gradio-container button.stop:hover:not(:disabled) { background: #991b1b !important; }

.oobe-risk-modal .row { gap: 10px !important; }

.gradio-container button.primary {
  color: #fff !important;
  background: #2563eb !important;
  border-color: #2563eb !important;
}

.gradio-container button.primary:hover:not(:disabled) {
  background: #1d4ed8 !important;
  box-shadow: 0 4px 14px rgba(37, 99, 235, 0.22);
}

.gradio-container button.secondary {
  color: var(--cy-text) !important;
  background: var(--cy-surface) !important;
  border: 1px solid var(--cy-line) !important;
}

.gradio-container button.secondary:hover:not(:disabled) {
  background: var(--cy-tint) !important;
  border-color: var(--cy-accent) !important;
}

.gradio-container button:disabled {
  opacity: 0.48 !important;
  cursor: not-allowed !important;
  box-shadow: none !important;
}

.gradio-container :is(button, input, textarea, [tabindex]):focus-visible {
  outline: 2px solid var(--cy-accent) !important;
  outline-offset: 3px;
}

.oobe-questionnaire .gradio-radio label,
.oobe-branch-selector .wrap label {
  border: 1px solid var(--cy-line) !important;
  border-radius: 10px !important;
  padding: 11px 13px !important;
  color: var(--cy-muted);
  background: var(--cy-surface) !important;
  cursor: pointer;
}

.oobe-questionnaire .gradio-radio label:has(input:checked),
.oobe-branch-selector .wrap label:has(input:checked) {
  border-color: var(--cy-accent) !important;
  color: var(--cy-text);
  background: var(--cy-tint) !important;
}

.oobe-questionnaire .wrap,
.oobe-branch-selector .wrap { gap: 8px !important; }

.oobe-advanced {
  border: 1px solid var(--cy-line) !important;
  background: var(--cy-surface) !important;
  overflow: visible;
}

.oobe-advanced > button {
  padding: 16px 18px !important;
  min-height: 54px;
}

.oobe-advanced > button:hover { background: var(--cy-tint) !important; }

.oobe-advanced > .wrap { padding: 0 16px 16px !important; }

@media (max-width: 760px) {
  .enterprise-workspace-nav { flex-basis: 100% !important; width: 100%; }
  .product-header { gap: 12px !important; }
  .oobe-card, .merge-card { padding: 14px !important; }
  .oobe-nav button { flex: 1 1 180px !important; min-width: 0 !important; }
  .oobe-step-label { white-space: normal; }
}

.runtime-layout { gap: 20px !important; align-items: flex-start !important; }
.runtime-console { border: 1px solid var(--border-color-primary) !important; border-radius: 14px !important; }
.runtime-console h3 { margin: 0 0 8px !important; }
.runtime-console pre {
  background: #101c2e !important; color: #dbeafe !important;
  border: 1px solid #29405f !important; border-radius: 12px !important;
  min-height: 260px; max-height: 520px; overflow: auto !important;
  padding: 16px !important; font: 13px/1.65 ui-monospace, Consolas, monospace !important;
  white-space: pre-wrap !important; overflow-wrap: anywhere;
}
.runtime-dashboard { padding: 12px !important; border-radius: 12px !important; }
@media (max-width: 760px) {
  .runtime-layout > div { min-width: 0 !important; flex-basis: 100% !important; }
  .runtime-console pre { max-height: 380px; }
}
@media (prefers-reduced-motion: reduce) {
  .gradio-container *, .gradio-container *::after { transition: none !important; }
}
"""
