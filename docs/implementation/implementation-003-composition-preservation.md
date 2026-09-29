---
title: "Composition preservation implementation"
type: implementation
status: in-progress
number: "003"
date: "2026-09-29"
related:
  - ../architecture/adr-001-composition-preserving-transformations.md
  - ../prds/prd-001-design-system-schema.md
  - ../plans/plan-001-design-system-schema-foundation.md
  - runbook-002-composition-regression.md
---

# Composition preservation implementation

## Delivered

- The canonical Skill separates Convert, Restyle and Redesign from Quick, Guided and Governed. Its composition contract assigns authority by concern, protects slide allocation and hierarchy, and requires scoped permission for deviations.
- Lumen guidance, prompts and the reference-constrained archetype choose approved type tokens inside source geometry, preserve explanatory graphics and qualify splitting by intent/permission. Root design guidance and legacy prompts defer to canonical instructions.
- `schemas/folio-0.2.0.schema.json` versions typed baseline regions, relationships, hierarchy, ambiguity, permissions, scene traceability and execution evidence. The 0.1.0 schema is unchanged for legacy reading.
- `scripts/folio_preservation.py` checks source/baseline hashes, normalised region bounds, per-region drift, visible text, reading order, primary-region identity, relationship meaning/labels/endpoints, grouping geometry and source coverage. Accepted execution records require all four gates, local evidence hashes, complete source-slide accounting and tests for claimed editing operations.
- `tests/test_composition_preservation.py` exercises synthetic pipeline preservation failures plus valid Restyle, one-to-many reconstruction, editable-line and authorised Redesign controls. Plugin CI runs these alongside existing schema/token tests.
- Codex package version advances to 0.3.0 so a published update can invalidate marketplace caches.

## Verification

Run the package validator, all unit tests and `pinact run --check --verify-min-age --verify-comment`. Validate the connected composition fixture with the schema CLI. Workflow changes additionally require actionlint, zizmor and the pinned OpenGrep scan. See the schema README for exact commands.

Local verification passed on 2026-09-29: package validation, 38 unit tests, the connected composition fixture, action pin age/comment verification, actionlint and zizmor. OpenGrep v1.30.0 (macOS arm64 release asset, verified SHA-256) reported zero findings in the repository scan.

These are contract checks. The synthetic scene has no rendered deck and its execution result is deliberately `partial`, with unverified gates. The unit test that constructs an accepted record uses fabricated temporary evidence to test bookkeeping; it does not claim host or visual acceptance.

## Remaining evidence

The original failure's cleared source, reviewed target and failed output are not available as a verified fixture set. Existing private archive outputs have not been promoted. A renderer/host owner must run the linked regression procedure and record actual source/final comparisons and PowerPoint move/resize tests before marking this delivery fully verified.

The schema validator does not render slides, solve constraints, measure text, assess graphic quality or open PowerPoint. It only checks that an Office ZIP contains expected parts and the declared number of slides; this is not an application-open test. Evidence authenticity and baseline capture time remain workflow responsibilities. The source-to-output trace currently maps each region and relationship once across output slides; splitting a single source region or a connector across slides requires a future explicit contract extension.
