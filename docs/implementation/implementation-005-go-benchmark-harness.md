---
title: "Go benchmark harness implementation"
type: implementation
status: in-progress
number: "005"
date: "2026-09-30"
---

# Go benchmark harness implementation

Implements [PRD 003](../prds/prd-003-folio-bench-go.md), [plan 003](../plans/plan-003-go-benchmark-harness.md) and [ADR 002](../architecture/adr-002-go-benchmark-orchestration.md). Folio package version 0.4.0 includes harness source and the updated benchmark contract; the independently versioned executable is 0.1.0, with protocol/results schema 1.

## Delivered

- `cmd/folio-bench`: run, list, validate, compare, report and version commands.
- `internal/benchmark`: typed contracts, trusted JSON configuration, deterministic discovery, regular-file snapshots/hashes, bounded workers, isolated trials, stdout/stderr/exit-code capture, context cancellation, trial/command timeouts and atomic manifest/results persistence.
- External JSON evaluator interface and native file assertions. `bench/evaluators/presentation.py` retains existing PowerPoint/PNG/semantic/evidence judgment without orchestration. Responses are bounded, strictly parsed and kept separately from diagnostic logs.
- Comparison distinguishes changed datasets from regressions and reports statuses, score/time deltas and violations, using configured score thresholds. Offline text/HTML reporting consumes results only.
- `bench/benchmark.json`: the three existing presentation cases, explicit generation controls and independent fresh Codex execution/review commands. `bench/ci/` provides synthetic parallel fixtures requiring neither model calls nor the private image.
- Protocol/results schemas, primary Go operating instructions and retained historical Python instructions.
- `scripts/build_bench.py`: five native binary archives plus checksums. The pinned CI workflow builds/exercises macOS and Linux and retains results, evidence and portable archives.

## Evidence and gates

Local verification passed: nine Go behavioral tests with race detection, Go vet, 53 Python tests, package validation, actionlint, zizmor and pinact age/comment checks. OpenGrep passed with a documented audit exception for the deliberate trusted dynamic-argv execution boundary. The compiled macOS CLI successfully validated all three real case definitions and executed/reported/compared a parallel synthetic run. Five target archives/checksums were built.

Local tests exercise ordered parallel results/artifact isolation, explicit failure versus assertions, malformed evaluator protocol, frozen input mutation, traversal/duplicate IDs, environment isolation, chunked secret redaction, timeout/cancellation persistence and descendant termination. Python parity fixtures cover accepted, failed and unverified legacy judgments. CI uses the exact developer binary/commands; CI execution status must be checked after publication.

The migration has not retired `bench/runner.py`: representative real generated-deck parity, observed Linux release-binary execution and CI stability are still required. macOS execution is verified locally; five-target cross-compilation is build evidence only. The configured real model cases have not been executed as part of harness implementation. No actual presentation acceptance or public release/Homebrew availability is claimed.

## Remaining release work

1. Observe green macOS/Linux CI execution against this commit and exercise archived binaries on target hosts.
2. Execute/review real reference cases through Go and compare evaluator judgment against corresponding legacy records.
3. Publish reviewed native archives/checksums through the Folio release process, configure the public Homebrew distribution and add release provenance/signing as that pipeline matures.
4. Retire Python orchestration only after all PRD migration gates have evidence; keep justified Python evaluators.
