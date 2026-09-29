---
title: "Design system schema foundation and Lumen pilot"
type: plan
status: draft
number: "001"
date: "2026-09-28"
owner: folio-maintainers
updated: "2026-09-29"
supersedes: null
superseded_by: null
related:
  - ../prds/prd-001-design-system-schema.md
  - ../design/README.md
tags:
  - design-system
  - schema
  - tokens
  - migration
---

# Design system schema foundation and Lumen pilot

## Context and outcome

The [schema PRD](../prds/prd-001-design-system-schema.md) proposes DTCG tokens, semantic components, patterns, archetypes, compositions, scenes and a bounded rendering loop. This plan sequences that proposal into a narrow, inspectable first delivery. The PRD is still a draft; the plan is a proposed route through it, not approval of its open contract decisions.

The first useful result is a **resolved Lumen token context** that retains its current visual decisions, plus one labelled, editable PowerPoint flow and one metric slide generated through versioned semantic contracts. The agent should retrieve a small component contract and resolved token subset for each task rather than repeatedly restating the entire design system. Reduced prompt size and improved quality are hypotheses to measure against the current workflow.

## Starting baseline and scope

- At the start of this plan, `design-systems/lumen/system.json` pointed to one combined `tokens.json`. `design/tokens.json` also exists and needs a consumer inventory before the legacy path is retired.
- Lumen's legacy token file uses hexadecimal colours, point/inch dimensions and custom typography fields. These values are useful migration inputs, but that file is not a DTCG token document.
- The shared and Lumen component registries contain no approved components. Existing archetype YAML and Skill instructions must be mapped before changing their resolution path.
- The authoritative plugin checkout contains Aperture, Meridian, Mosaic, Gridline and Werk as well as Lumen. Their DTCG conversion can be checked structurally now; visual parity still needs rendered review for each system.
- Quick and Guided retain their existing authority rules. The new package resolver applies to Governed work or an explicit developer contract request.

## Composition preservation delivery

[ADR 001](../architecture/adr-001-composition-preserving-transformations.md) and [implementation 003](../implementation/implementation-003-composition-preservation.md) refine phases 0 and 3 without introducing another scene model. The plugin implementation starts from current plugin main; conflicts in the separate archive checkout are unrelated.

1. Align the Skill, mode/workflow/reconstruction/acceptance references, README and Lumen prompts around independent transformation intent and authority by concern. Remove legacy global design authority.
2. Publish draft 0.2.0 contracts alongside readable 0.1.0 contracts. Freeze source analysis before output, map regions and relationships into scenes, and require evidence-backed acceptance. Migrate deliberately; never manufacture observations or passing evidence for old runs.
3. Run synthetic preservation failures and authorised Redesign controls with the inexpensive contract tests in CI. Keep these distinct from visual and host editing verification.
4. In a supported rendering environment, run [the composition regression procedure](../implementation/runbook-002-composition-regression.md) with a cleared source and reviewed target. Review whole-slide/detail fidelity and actual editing capabilities before promoting generated artefacts or claiming presentation-quality acceptance.

Contract delivery is tracked independently from host evidence. The original failed example is not present as a cleared source/target/failed-output set, and no native renderer implementation is supplied by the schema work.

## Work sequence

### 0. Ratify the smallest contract

**Owner:** Folio maintainers, with a renderer implementer. **Dependency:** PRD review.

1. Keep the numbered PRD at document version `0.2.0` and mark it draft until the decisions below are made.
2. Record short ADRs for the MVP DTCG support profile and units; package identity and source precedence; constraint operations and deterministic tie-breaks; target PowerPoint editing claims; semantic ID retention; and the OpenUI projection boundary. State what is deferred.
3. Freeze a `schemaVersion: 0.1.0` fixture set for a design-system manifest, presentation profile, component, binding, pattern, composition, scene and execution result. Give each contract an owner and an explicit required/optional field list. Do not publish a stable schema claim yet.

**Exit:** the examples validate against the selected JSON Schema dialect, and every open PRD decision affecting the pilot has a recorded disposition.

### 1. Make tokens reliable and useful

**Owner:** token/schema implementer. **Dependency:** unit and source-precedence ADRs.

1. Inventory every reader of Lumen `tokens.json`, `design/tokens.json`, `system.json`, the archetype YAML and prompts. Capture representative rendered slides as a visual baseline, including typography, line weights and safe areas.
2. Convert Lumen colours, fonts, dimensions and typography to DTCG 2025.10 documents. Separate reusable visual values from canvas, grid, layer order and behaviour in a presentation profile. Preserve legacy source values in migration fixtures; convert `pt` and `in` explicitly at the rendering boundary using the declared 96 px/in and 72 pt/in policy. Do not round away meaningful precision.
3. Implement a resolver for the **declared MVP token types only**: colour, dimension, font family, font weight, number, typography, border, stroke style, shadow and gradient as needed by the Lumen pilot. Reject missing references, cycles, duplicate leaf paths and unsupported required values. Preserve unknown optional extension data. Pin a DTCG Resolver adapter only if the pilot actually needs contextual modes.
4. Emit a compact resolved token index with stable names, descriptions, source paths and values. Give the agent the relevant subset for a selected component or archetype; retain the full resolved context for deterministic rendering and auditing.
5. Provide one canonical source after cutover. A versioned compatibility reader may accept legacy files during migration, but it must report the source and must not silently merge two editable copies.

**Exit:** all token fixtures resolve or fail with actionable diagnostics; representative Lumen slides retain approved appearance within declared, preselected tolerances; the compact retrieval path returns the same values as the full context.

### 2. Prove the semantic path with a small catalogue

**Owner:** component and rendering implementers. **Dependency:** phase 1.

1. Build a package loader that follows only manifest-declared resources, validates paths and locked dependencies, and reports absent governed resources. Add semantic validation after JSON Schema validation: unique IDs, valid defaults and slots, acyclic pattern expansion, resolvable anchors and supported required capabilities.
2. Create reviewed semantic definitions for a customer, control, application, data store, metric and callout. Give each a stable ID, content/slot contract, intended use and provenance. Add only the Lumen bindings needed for the pilot; keep candidate assets out of the approved catalogue.
3. Implement direct composition first, then one linear/control-flow pattern and one architecture or metric archetype. Resolve them into a backend-neutral scene with instance IDs, source references, reading order, frames and connector endpoints. Specify deterministic handling for the pilot constraint operations before claiming solver support.
4. Bind native text, shapes/groups and connectors to PowerPoint. Use SVG or raster only where the representation policy permits it. Declare editing operations per binding and verify them in named target applications.

**Exit:** a labelled flow and metric slide open, can be edited in the declared target, rerender correctly, and retain their required text, numbers and relationships. Unsupported edit operations are reported rather than claimed.

### 3. Add visual guidance and bounded repair

**Owner:** workflow and evaluation implementers. **Dependency:** phase 2.

1. Capture supplied or generated visual targets in a 0.2.0 visual-specification record before output generation. Record authority by concern, source hashes, typed regions and relationships, hierarchy, uncertainty and explicit transformation permissions. Map each source region and relationship into the resolved scene and lock the baseline digest.
2. Render, inspect and report object-level findings. Repair only affected scene objects and their dependent connectors; preserve already-correct content and instance IDs.
3. Enforce declared candidate, repair, time and measurable cost limits. Return `accepted`, `partial`, `failed` or `cancelled` with produced artefacts, stop reason and evidence for all four independent gates. Accepted output needs source/final comparison and host editing checks; missing checks remain partial. A preview alone is not an accepted editable deck.

**Exit:** direct composition and supplied-reference runs reach the same output contract. The optional generated-reference path is introduced only after its costs and failure modes can be measured. Exhausted budgets terminate with usable diagnostics.

### 4. Prove value and prepare independent consumption

**Owner:** maintainers and evaluators. **Dependency:** phase 3.

1. Freeze a versioned evaluation corpus spanning simple and dense diagrams, long/multilingual labels, photographs, vectors, charts and progressive reveals, including unsatisfiable cases.
2. Compare the current Folio path with the compact-token/semantic path on the same tasks and budgets. Record accepted output rate, required-content and relationship accuracy, editing coverage, visual review, prompt and total token use where exposed, repair rounds, elapsed time and cost per accepted artefact. Include failed runs.
3. Publish contract examples, failure fixtures, supported capabilities and a minimal independent reader or adapter. Record projection losses for the experimental OpenUI export. Release only supported claims, with migration notes for breaking contracts.

**Exit:** improvement claims have measured evidence; a separate reader can validate and interpret the semantic contracts without private Folio behaviour.

## Acceptance and decision gates

| Gate | Evidence | PRD criteria |
| --- | --- | --- |
| Contract and token migration | Schema/semantic fixtures, reference and unit diagnostics, reviewed before/after Lumen renders | AC-03, AC-04, AC-08, AC-09 |
| Native output | Source-to-object trace, actual PowerPoint edit/open/rerender results, connector checks | AC-01, AC-02, AC-05, AC-06 |
| Governed behaviour | Manifest/resource resolution report and explicit rule coverage | AC-10 |
| Visual workflow | Bounded repair history, retained checkpoint and honest result state | AC-07 |
| Product and efficiency | First-use walkthrough and repeated full-pipeline comparison including failures | AC-11, AC-12 |

Before implementing beyond the pilot, review the PRD's breadth against evidence. In particular, defer a broad catalogue, full DTCG Resolver support, PowerPoint round trips and stable conformance claims until the preceding gates pass. Each phase should update the implementation record with source paths, supported versions, target applications and remaining gaps.
