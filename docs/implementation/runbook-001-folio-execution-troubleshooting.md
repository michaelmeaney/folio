---
title: Folio execution troubleshooting and Q&A
type: runbook
status: in-progress
number: 1
date: 2026-09-26
---

# Troubleshooting and Q&A

This page records operational failure modes observed while using Folio.

## Do I need a fresh chat?

For a substantial Folio conversion or redesign, a fresh chat is the safest execution environment.

Folio is a multi-step workflow: intent confirmation, design-authority resolution, decomposition, generation, deterministic reconstruction, rendering and validation all require working context. A conversation that is already very long or close to its context limit can make execution less reliable.

If the current conversation contains substantial unrelated prior context, start a fresh chat before the actual presentation build. Carry forward only the confirmed Folio brief, source material, selected transformation and selected design system.

## What are the warning signs that context is becoming a problem?

Treat these as reasons to restart the build in a fresh chat:

- Folio stops following the confirmed Convert vs Redesign intent;
- it forgets or substitutes the selected design system;
- it repeats questions that were already resolved;
- it skips required workflow or validation stages;
- execution becomes inconsistent, stalls, or fails to complete the presentation artefact.

Do not try to recover a degraded long-running build by repeatedly adding more corrective context. Preserve the agreed brief and restart cleanly.

## Should I generate the presentation in the same chat where I designed or debugged Folio?

Prefer a fresh chat when that conversation is already context-heavy. Repository work, prompt design, debugging and presentation execution consume different context. Once the brief is agreed, move the actual build into a fresh chat when practical.

## Does a released model automatically work with Folio?

No. Folio compatibility is empirical. A model is **Verified** only after it completes the same end-to-end Folio workflow and acceptance checks. See [Model compatibility](implementation-001-model-compatibility.md).

## Which model should execute Folio today?

GPT-6 Astra is the currently verified and required model for the actual conversion/reconstruction step. GPT-6 Luna and GPT-6 Sol are **Test required** until evaluated.

## What should I include when starting a fresh Folio chat?

Provide the minimum authoritative execution context:

1. the source image, deck, brief or other input;
2. whether the task is **Convert** or **Redesign**;
3. the selected design system for a Redesign, including an external repository link where applicable;
4. any explicit content or output constraints.

Folio should play that intent back for confirmation before generation starts.

## Does context-window size determine Folio reliability?

Not by itself. Record nominal context capacity when useful, but Folio compatibility is based on observed end-to-end execution. The important condition is whether the model retains the confirmed transformation, design authority and workflow state as context pressure increases.

The compatibility suite therefore includes both clean-context and context-loaded runs. A model can pass in a fresh chat and still exhibit degradation in a long conversation; record those as distinct results.

## Does reasoning effort matter?

Potentially. Where ChatGPT exposes selectable reasoning effort, record it with the test result. Do not generalise a result from one reasoning setting to another without testing. Presentation decomposition, spatial decisions, design-system application and QA may all be sensitive to reasoning configuration.
