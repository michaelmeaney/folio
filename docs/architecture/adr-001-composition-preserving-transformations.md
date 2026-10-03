---
title: "Composition-preserving transformations"
type: adr
status: implemented
number: "001"
date: "2026-09-29"
related:
  - ../prds/prd-001-design-system-schema.md
  - ../plans/plan-001-design-system-schema-foundation.md
  - ../implementation/implementation-003-composition-preservation.md
---

# Composition-preserving transformations

## Context

The composition review found that Convert mapped to Quick and applying a design system mapped to Redesign/Governed. This unintentionally allowed a named design system to override reference composition and weaken fidelity acceptance. Reconstruction rules simultaneously required preserving that composition. Lumen's default splitting, typography and archetype guidance amplified the contradiction.

## Decision

Transformation intent and capability mode are separate. Convert preserves representation-independent content, composition and treatment. Restyle changes treatment while preserving meaning, relative hierarchy, grouping and slide allocation. Redesign allows explicitly scoped structural changes. Guided and Governed can both restyle or redesign. Quick remains faithful conversion without governance.

For Restyle, the reference controls composition and meaning, the selected system controls treatment, and the user controls structural permissions. A mandatory system rule may create a real conflict; surface that conflict and obtain a specific exception or redesign permission. Preferred archetypes, density targets and grids do not grant permission to recompose.

Freeze the source composition baseline before generation. Extend the existing visual-specification, scene and execution-result contracts in schema 0.2.0. Keep 0.1.0 readable for legacy packages; it supplies no evidence of the new guarantees. Record scoped deviations and compare source relationships and visible text independently from geometry.

Require four non-compensating gates: content/semantics, composition/hierarchy, treatment, and artefact/editability. A required check that cannot run is unverified and prevents acceptance. Evidence references and hashes bind a report to its inputs and outputs; they cannot prove that a human or host actually performed the reported check.

## Consequences

Lumen selects typography tokens inside protected regions and preserves explanatory graphics as functional content. New composition and authorised redesign retain their layout freedom. Existing explicit system selections and confirmations remain valid.

Normalised geometry tolerances are chosen per region before generation; there is no universal fidelity percentage. Baseline hashes catch inconsistent records, not a dishonest rewrite of both baseline and digest. Render review remains necessary for visual weight, text metrics and illustration quality. Native PowerPoint editing still requires a supported host.

The new version is a draft validation contract, not a renderer, solver or stable conformance promise. Unsupported cross-slide relationship reconstruction fails explicitly. Broader renderer work remains in the schema foundation plan.
