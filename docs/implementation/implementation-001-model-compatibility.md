---
title: Folio model compatibility
type: implementation
status: in-progress
number: 1
date: 2026-09-26
---

# Model compatibility

Folio is model-independent at the harness level, but presentation reconstruction is not assumed to be model-equivalent. Compatibility is established by running the Folio workflow end to end and recording the result.

## Compatibility states

- **Verified** — exercised end to end for editable presentation conversion and accepted as a working execution model.
- **Test required** — available for evaluation but not yet verified for Folio conversion.
- **Known incompatible** — tested and failed the Folio acceptance workflow. Record the observed failure and test date before assigning this state.

## Current matrix

Compatibility is recorded for a specific **model × reasoning effort × ChatGPT execution surface × Folio workflow**. A successful result in one combination does not establish compatibility for another.

| Model | Reasoning | Chat — Convert | Chat — Governed redesign | Work — Convert | Work — Governed redesign | Status / notes |
| --- | --- | --- | --- | --- | --- | --- |
| GPT-6 Astra | Medium | **Verified** | **Verified** | **Test required** | **Test required** | Current verified executor in Chat at Medium reasoning. Work still requires end-to-end testing. |
| GPT-6 Luna | To test | **Test required** | **Test required** | **Test required** | **Test required** | Released; test supported reasoning configurations before compatibility is claimed. |
| GPT-6 Sol | To test | **Test required** | **Test required** | **Test required** | **Test required** | Released; test supported reasoning configurations before compatibility is claimed. |

No model/surface combination is currently recorded as **Known incompatible**. Add compatibility only after an observed Folio test result; do not infer it from release status, another execution surface, or general model capability.

## Test contract

A model should not be promoted to **Verified** merely because it can create a plausible slide. Test the complete Folio contract:

1. confirm Convert vs Redesign intent before execution;
2. resolve the requested design authority correctly;
3. decompose the reference into appropriate editable representations;
4. create an editable presentation rather than flattening reconstructable content;
5. render and visually inspect the result;
6. complete the applicable Folio acceptance checks;
7. record material failure modes.

Use the same reference fixture, design-system selection and acceptance criteria when comparing models or execution surfaces.

Record the **model, reasoning effort, execution surface, workflow, fixture and context condition** with every result.

Reasoning effort is part of the compatibility result where the product exposes it. Do not assume a model verified at one reasoning level is equivalent at another.

Context must also be treated as an experimental condition. Distinguish at least:
- **clean context** — a fresh chat containing only the authoritative Folio execution material;
- **context-loaded** — a deliberately long/context-heavy conversation used to measure degradation and specification retention.

The nominal context-window size is useful metadata, but the test should measure observed behaviour under context pressure rather than infer reliability from the advertised maximum.

At minimum, distinguish execution surfaces:
- **ChatGPT Chat** — normal conversational execution;
- **ChatGPT Work** — Work-mode execution using its own workspace/cloud-computer workflow.

A model verified in Chat must be retested in Work before Work compatibility is claimed. Differences in orchestration, available tools, file handling, persistence and execution behaviour can affect the Folio workflow independently of the underlying model.

## Runtime requirement

For **ChatGPT Chat**, GPT-6 Astra is currently the verified Folio conversion/reconstruction executor. GPT-6 Luna and GPT-6 Sol require testing.

**ChatGPT Work is not yet verified for Folio conversion on any listed model.** Treat all Work combinations as test-required until the same end-to-end fixtures and acceptance checks have been completed there.

## Major-model-release evaluation

Re-run the Folio evaluation suite for each significant model generation or materially changed execution runtime. Publish results only for combinations actually tested.

Recommended stable fixtures:

| Fixture | Purpose |
| --- | --- |
| A — faithful reconstruction | Reference image to editable slide; tests visual fidelity, primitive selection and editability. |
| B — governed redesign | Same semantic content rebuilt with a selected design system; tests separation of content from visual authority and design-system compliance. |
| C — complex architecture | Dense zones, connectors, labels and repeated components; tests spatial reasoning and representation choices. |
| D — multi-slide deck | 5–10 slides; tests cross-slide consistency and degradation over a longer execution. |
| E — context pressure | Repeat a stable fixture in clean and context-loaded chats; tests retention of intent, design authority and workflow state. |

For each run record, where observable:
- completion and valid PPTX production;
- text/content accuracy;
- editability and representation quality;
- visual fidelity for Convert;
- design-system violations for Governed Redesign;
- overflow/layout defects;
- number of repair iterations;
- execution time;
- human intervention required;
- workflow-stage omissions or context-loss symptoms.

The public compatibility matrix should remain concise. Detailed evaluation records can retain the full test dimensions and evidence behind each status.
