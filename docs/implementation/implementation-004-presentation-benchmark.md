---
title: "Presentation benchmark harness"
type: implementation
status: in-progress
number: "004"
date: "2026-09-29"
---

# Presentation benchmark harness

Implements [PRD 002](../prds/prd-002-presentation-benchmark.md).

## Delivered

- `bench/suite.json`: three fixed cases, four independent gates and operation-specific criteria.
- `bench/prompts/`: Quick Convert, Governed Restyle and five-slide Governed Redesign briefs.
- `bench/reference/reference.json`: hashed private reference identity, visible-copy transcription, semantic facts and approximate composition regions for review.
- `bench/runner.py`: immutable input snapshots, fresh-process executor adapter, timeout/log capture, PowerPoint/PNG inspection, evidence fingerprint checks, local HTML reports and comparable-run checks.
- `tests/test_folio_bench.py`: 14 synthetic harness tests covering frozen inputs, text/flattening failures, independent gates, evidence validity, runtime mismatches, execution status and regression comparison.
- [Benchmark instructions](../../bench/README.md): preparation, execution, real application review and comparison.

The reference image and generated runs are gitignored. CI tests need neither the private image nor a model. Existing unittest discovery includes the harness tests.

## Verification and remaining work

The harness is implemented; presentation performance remains unverified until the three real cases are executed and reviewed. Initial acceptance requires actual PowerPoints, rendered slides, source comparisons, accessibility checks and editing evidence from a named application. Creating a baseline directory or passing synthetic tests does not satisfy this requirement.

Next: execute the prepared baseline against Folio 0.3.0, review all four gates per case, record failures, then repeat with matching controls for a candidate version. Promote no generated output to examples before review.

## Fresh context integration

Folio 0.3.1 routes benchmark requests to `skills/folio/references/benchmark.md`. Suite 1.1.0 prepares separate generation and review briefs; reviews require unique context IDs and verified absent inheritance. Codex dispatch uses `fork_turns="none"` for each task. Runtime changes do not imply the real benchmark has passed.
