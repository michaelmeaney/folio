---
title: "Design system schema implementation"
type: implementation
status: in-progress
number: "002"
date: "2026-09-28"
owner: folio-maintainers
updated: "2026-09-28"
supersedes: null
superseded_by: null
related:
  - ../prds/prd-001-design-system-schema.md
  - ../plans/plan-001-design-system-schema-foundation.md
tags:
  - design-system
  - schema
  - tokens
---

# Design system schema implementation

## Delivered contract foundation

- `schemas/folio-0.1.0.schema.json` defines ten draft Folio document kinds. `schemas/examples/` provides a connected component, binding, pattern, composition and scene bundle, plus the remaining contract examples.
- `scripts/folio_schema.py` validates JSON Schema shape, package resource paths, an initial DTCG profile, aliases, duplicate token names and cross-contract references. It can return a selected resolved token subset with source attribution.
- All six installed system manifests declare DTCG token and presentation resources. `scripts/migrate_design_system_tokens.py` bootstrapped their values and rebuilds the derived legacy files from the canonical schema resources. A reverse check catches drift. Existing consumers can keep reading their legacy paths during migration.
- A small semantic alias layer maps canvas, text and applicable focus/status roles to each system's existing palette. It gives components stable role names without introducing new colours or forcing one focus colour where the system does not define one.
- `skills/folio/` documents this resource precedence for Governed mode. Quick and Guided authority rules are unchanged.

## Evidence and remaining work

The repository validator, schema validator, migration drift checks and semantic fixtures form the contract gate. Conversion preserves source colour hex values and records source units for migrated dimensions. Rendered before/after comparison and target-application editing checks are still required before claiming visual parity or native-editing support.

The implementation covers the first contract and token portion of [the plan](../plans/plan-001-design-system-schema-foundation.md). The catalogue is a schema fixture, not a reviewed production catalogue. Constraint solving, native PowerPoint bindings, bounded repairs, DTCG Resolver modes, safe SVG ingestion, OpenUI projection, independent consumption and comparative token/cost measurement remain open. No stable conformance claim is made.

Composition-preserving transformation contracts and acceptance evidence are extended in [implementation 003](implementation-003-composition-preservation.md), using schema 0.2.0 alongside these original contracts.
