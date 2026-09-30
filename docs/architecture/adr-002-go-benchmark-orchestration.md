---
title: "Go benchmark orchestration with external evaluators"
type: adr
status: approved
number: "002"
date: "2026-09-30"
---

# Go benchmark orchestration with external evaluators

## Context

[PRD 003](../prds/prd-003-folio-bench-go.md) requires portable, deterministic orchestration while preserving existing evaluator judgment. [ADR 001](adr-001-composition-preserving-transformations.md) continues to govern presentation semantics and independent acceptance gates.

## Decision

Use a compiled `folio-bench` CLI and a versioned JSON protocol. The `internal/benchmark` package separates configuration, snapshots, process supervision, evaluator adapters, results, comparison and reporting in focused files. Cases select named trusted commands/evaluators. The Go layer does not generate slides or reimplement presentation acceptance.

Use bounded workers with ordered results and atomic persistence. Give every trial isolated artifacts, fresh generation and review sessions, controlled child environment, separate logs and an overall trial timeout. Terminate Unix process groups and Windows process trees on cancellation. Snapshot declared evaluator resources and plugin files; fingerprint all frozen inputs and capture actual runtime through review.

Retain legacy Python judgment behind an external protocol adapter. Native file assertions are reserved for synthetic harness tests. Unperformed presentation checks remain unverified. Preserve the historical Python runner until migration acceptance criteria have evidence; no blanket retirement follows from successful compilation.

## Consequences

Native orchestration and native evaluator cases require no Python environment. Presentation evaluation still depends on Python while migrated selectively. CI exercises the same binary using synthetic assets; real model/application acceptance remains separate. Release archives are generated automatically, but public distribution and signed provenance need release-side evidence.
