---
title: "Go benchmark harness delivery"
type: plan
status: implemented
number: "003"
date: "2026-09-30"
---

# Go benchmark harness delivery

Implements [PRD 003](../prds/prd-003-folio-bench-go.md), building on [implementation 004](../implementation/implementation-004-presentation-benchmark.md).

## Review and decisions

The PRD's orchestration/evaluation/generation boundary is appropriate. Its conceptual contracts need a concrete wire format, trusted command configuration, conservative concurrency, cancellation semantics and migration evidence before retiring Python. Native binaries remove Python from orchestration; choosing a Python evaluator still requires Python. Private slide assets and model credentials cannot be assumed in CI.

Use JSON schema version 1, explicit argv command registries selected by cases, a bounded worker pool (default one), isolated trial directories and stable ordered results. Configurations are trusted operator inputs; cases choose named commands and cannot embed shell fragments. Pass evaluator JSON on stdin and accept one structured JSON result on stdout; stderr remains diagnostics. Capture all diagnostics with configured secret values redacted. Secrets enter explicit child environment variables from the parent, never manifests. Output is a unique child of the specified root.

Retain the three fixed suite cases and answer key. Snapshot the plugin, reference, prompts, criteria, evaluator code and configuration. Record file digests, OS/architecture, plugin version and commit/branch, controls, selected cases and concurrency. Preparation authorises the fixed briefs, not a change to normal Folio governance. Generation and optional review commands must start fresh sessions; reviews verify unique context IDs. The coordinator does not embed presentation generation.

Result statuses: pass, fail, error, timeout, skipped and unverified. Exit precedence: configuration 2 before execution; after execution timeout 4, error/unverified 3, assertion fail 1, otherwise 0. Cancellation persists skipped/unverified results and exits 3. Missing evidence never passes. Compare separates case/configuration changes from regressions, reports score/time/violation deltas, and uses configured score thresholds.

## Implementation sequence

1. Add the Go module, CLI, configuration and evaluator protocol; discover/list/validate the existing suite without executing commands.
2. Implement snapshots, manifest/results, argv execution, controlled environment, timeout/cancellation, bounded workers and diagnostics.
3. Adapt existing Python judgment behind the protocol; add native file assertions for deterministic harness fixtures.
4. Implement comparison and offline human/HTML reports; document the same commands for developers and CI.
5. Verify failures, malformed evaluator output, timeouts including descendants, cancellation, isolation, redaction and legacy judgment parity.
6. Build five target binaries with checksums and add CI using the same CLI. Keep Python retirement gated on representative real runs and actual macOS/Linux binary execution.

## Acceptance evidence

Run Go tests (including race detection), Python tests/package validation, native CLI smoke cases, parity tests and cross-compilation. Exercise macOS locally; exercise Linux in CI. Cross-compilation alone does not count as platform execution. Do not claim a Homebrew release or signed provenance exists before the public distribution is configured and exercised. Keep retirement and publication gaps explicit in implementation 005.
