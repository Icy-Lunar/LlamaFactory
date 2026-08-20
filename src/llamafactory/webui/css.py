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
  max-width: 1680px !important;
  padding: 18px clamp(14px, 2.5vw, 38px) 32px !important;
  background:
    radial-gradient(circle at 4% 0%, rgba(37, 99, 235, 0.08), transparent 24rem),
    var(--body-background-fill);
}

.enterprise-workspace-nav {
  position: sticky;
  z-index: 50;
  top: 8px;
  width: min(100%, 470px);
  margin: 0 auto 18px;
  gap: 5px !important;
  padding: 5px;
  border: 1px solid var(--border-color-primary);
  border-radius: 14px;
  background: color-mix(in srgb, var(--background-fill-primary) 92%, transparent);
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(14px);
}

.enterprise-workspace-nav button {
  min-width: min(42vw, 220px);
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
  margin: 12px 0 22px;
  padding: 30px 34px;
  border: 1px solid color-mix(in srgb, var(--border-color-primary) 72%, #2563eb 28%);
  border-radius: 20px;
  background:
    radial-gradient(circle at 88% 12%, rgba(37, 99, 235, 0.18), transparent 34%),
    linear-gradient(135deg, var(--background-fill-primary), var(--background-fill-secondary));
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
}

.oobe-hero::after {
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
  font-size: clamp(26px, 3vw, 38px);
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
  color: #2563eb;
  font-size: 12px;
  font-weight: 750;
  letter-spacing: 0.13em;
}

.oobe-page {
  gap: 16px !important;
  max-width: 1500px;
  margin-inline: auto;
}

.oobe-page-header {
  padding: 6px 4px 10px;
}

.oobe-page-header h2 {
  font-size: clamp(23px, 2.2vw, 31px);
}

.oobe-stepper {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  margin-top: 24px;
}

.oobe-step {
  position: relative;
  display: flex;
  align-items: center;
  gap: 9px;
  min-width: 0;
  padding: 11px 13px;
  border: 1px solid var(--border-color-primary);
  border-radius: 12px;
  color: var(--body-text-color-subdued);
  background: var(--background-fill-secondary);
  transition: border-color 160ms ease, background 160ms ease, color 160ms ease;
}

.oobe-step.is-active {
  border-color: #2563eb;
  color: var(--body-text-color);
  background: rgba(37, 99, 235, 0.1);
  box-shadow: inset 0 0 0 1px rgba(37, 99, 235, 0.08);
}

.oobe-step.is-done {
  color: #16803c;
  border-color: rgba(22, 128, 60, 0.28);
  background: rgba(22, 128, 60, 0.07);
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
  padding: 17px 18px 19px !important;
  border: 1px solid var(--border-color-primary) !important;
  border-radius: 16px !important;
  background: var(--background-fill-primary) !important;
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.055);
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
  min-width: min(100%, 26rem);
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
  background: color-mix(in srgb, var(--primary-50) 78%, transparent);
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
  background: color-mix(in srgb, #fee2e2 72%, var(--background-fill-primary));
  color: color-mix(in srgb, #991b1b 82%, var(--body-text-color));
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
  background: color-mix(in srgb, #dcfce7 68%, var(--background-fill-primary));
}

.oobe-memory-report.is-safe header > span {
  background: #16a34a;
}

.oobe-memory-report:not(.is-safe) {
  border-color: color-mix(in srgb, #d97706 48%, var(--border-color-primary));
}

.oobe-memory-report:not(.is-safe) header {
  background: color-mix(in srgb, #fef3c7 68%, var(--background-fill-primary));
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
  display: flex !important;
  overflow: auto;
  align-items: center;
  justify-content: center;
  padding: 1.25rem !important;
  border: 0 !important;
  border-radius: 0 !important;
  background: rgba(15, 23, 42, 0.68) !important;
  backdrop-filter: blur(3px);
}

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
  background: color-mix(in srgb, #fee2e2 60%, var(--background-fill-secondary));
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
  max-width: 1320px;
  margin-inline: auto;
  gap: 16px !important;
}

.merge-hero {
  position: relative;
  overflow: hidden;
  padding: 30px 34px;
  border: 1px solid color-mix(in srgb, var(--border-color-primary) 68%, #7c3aed 32%);
  border-radius: 20px;
  background:
    radial-gradient(circle at 90% 0%, rgba(124, 58, 237, 0.18), transparent 36%),
    linear-gradient(135deg, var(--background-fill-primary), var(--background-fill-secondary));
  box-shadow: 0 18px 46px rgba(15, 23, 42, 0.08);
}

.merge-hero::after {
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
  font-size: clamp(26px, 3vw, 37px);
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
    grid-template-columns: 1fr;
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

.modal-box {
  position: fixed !important;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%); /* center horizontally */
  max-width: 1000px;
  max-height: 750px;
  overflow-y: auto;
  background-color: var(--input-background-fill);
  flex-wrap: nowrap !important;
  border: 2px solid black !important;
  z-index: 1000;
  padding: 10px;
}

.dark .modal-box {
  border: 2px solid white !important;
}
"""
