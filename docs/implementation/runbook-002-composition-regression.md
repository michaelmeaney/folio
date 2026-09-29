---
title: "Composition and editing regression procedure"
type: runbook
status: approved
number: "002"
date: "2026-09-29"
related:
  - implementation-003-composition-preservation.md
  - ../architecture/adr-001-composition-preserving-transformations.md
---

# Composition and editing regression procedure

## Inputs and baseline

Use a publication-cleared source, or retain private source assets outside public examples. Record the source image hash, Folio commit, selected system revision, renderer identity/version, fonts, target application/version and confirmed transformation scope. Inspect the source and freeze a 0.2.0 visual specification before generating the output. Store its canonical JSON SHA-256 in the scene; retain the original baseline for review.

Begin with the synthetic integrated architecture case under `tests/fixtures/composition/`. It protects structured parsing, unstructured inference and existing-diagram rendering as separate routes into a dominant architecture canvas. It is a test input, not a reviewed finished slide or an exact reproduction of the private failure.

## Generation and visual checks

Generate a Governed Restyle using Lumen with one output slide and all structural permissions false. Reconstruct text, shapes and connectors, using representative artwork and measured text before final rendering. Follow the canonical Skill's confirmation rules.

Inspect source and actual final render together at whole-slide and detail scale. Record whether the architecture canvas remains dominant, the title has proportional weight, input branches remain distinct, outputs preserve their associations, and all visible text remains on the same slide. Record material differences and their authorisation; require all four gates to pass independently.

Repeat with an explicitly scoped Redesign that moves selected regions. Confirm that permitted changes pass while unpermitted omissions, route changes or slide splits still fail. Preserve both evidence sets with source/baseline and final artefact hashes.

## Target-application editing checks

Open the actual `.pptx` in the named supported application/version. Check for repair warnings and missing objects. Render every slide and compare the actual slide count and contents with the execution record.

For every representation family whose capability is claimed, edit a copy of the deck. Change native text, resize a native shape, and resize any vector. For each connector relationship, inspect its stored endpoint associations, move each endpoint independently, resize both endpoint components, save, close, reopen and rerender. Both attachments and the intended direction/label must survive. Capture evidence of before/after state and endpoint associations. A line that merely touches an object passes only an editable-line claim; a resized SVG proves resizing only.

If an operation fails, mark that editing check and the artefact gate failed. If the host or operation is unavailable, mark it unverified. Return `partial` with artefacts and diagnostics; do not manufacture a passing check.

## Evidence and promotion

Write the gate reports, actual source/final renders, actual PowerPoint and editing evidence to the execution directory. Reference local files and SHA-256 digests from the execution result. Include the source and final render in the composition gate, and fingerprint the delivered PowerPoint and render in the artefact gate. Validate the whole connected bundle with `scripts/folio_schema.py`.

A successful validator result confirms record consistency only. Promote a generated target into examples or a reusable component into an approved registry only after explicit review. Update implementation 003 with the actual host, renderer, results and any remaining limitations.
