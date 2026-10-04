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

Local tests exercise ordered parallel results/artifact isolation, explicit failure versus assertions, malformed evaluator protocol, frozen input mutation, traversal/duplicate IDs, environment isolation, chunked secret redaction, timeout/cancellation persistence and descendant termination. Python parity fixtures cover accepted, failed and unverified legacy judgments. CI uses the exact developer binary/commands. Draft PR #8 verified commit `5b25fe4`: macOS and Linux benchmark jobs, package validation, OpenGrep, actionlint and zizmor all passed. [Benchmark workflow evidence](https://github.com/michaelmeaney/folio/actions/runs/36689743774).

The migration has not retired `bench/runner.py`: representative real generated-deck parity, representative real presentation parity and continuing CI stability are still required. Native macOS/Linux CLI execution is verified locally/in CI; five-target cross-compilation does not establish Windows or every architecture's execution. The governed restyle case has now completed a real generation and independent review, as recorded below; Quick conversion and governed redesign remain unexecuted. No actual presentation acceptance or public release/Homebrew availability is claimed.

## Remaining release work

1. Exercise the packaged release archives on supported target architectures; native macOS/Linux CI execution is already green.
2. Execute/review real reference cases through Go and compare evaluator judgment against corresponding legacy records.
3. Publish reviewed native archives/checksums through the Folio release process, configure the public Homebrew distribution and add release provenance/signing as that pipeline matures.
4. Retire Python orchestration only after all PRD migration gates have evidence; keep justified Python evaluators.

## 0.4.1 production preflight correction

The first real `run` failed because Go decoded every design-system resource as a string, while canonical `resources.tokens` is an array. The harness now decodes only the presentation resource it consumes. `validate` checks the same governed resource resolution before execution. Regression tests cover all six real system manifests and preparation of the bundled three-case presentation suite with a synthetic source; the private image is not required by CI. Harness version is 0.1.1 and plugin version is 0.4.1. Earlier synthetic execution evidence did not prove the real presentation run.

The first live generation also exposed worker-role ambiguity and linked runtime dependencies under build output. Version 0.4.2/harness 0.1.2 assigns the fresh session directly to generation/review, and excludes node_modules/virtualenv/cache/Git dependencies from artifact retention while retaining reconstruction source and rejecting other symlinks.

## Real governed restyle run

On 2026-10-03, installed harness 0.1.2 and plugin 0.4.2 completed `folio-bench run --case governed-restyle --verbose` against the private local reference. Run `20261003T201830Z-2e57e9954d4a` finished in 1161.679 seconds with exit code 1: zero passes, one acceptance failure, zero infrastructure errors and zero timeouts. Generation and review each exited successfully in separate ephemeral Codex sessions, with distinct recorded context IDs. Artifact collection retained the PowerPoint, renders, reconstruction source and review evidence while excluding the linked dependency directory.

The resulting single slide has 356 native shapes, including 37 native text shapes, and no embedded pictures. Independent review failed content, composition and treatment: text overlap, enlarged risk labels, weak functional contrast and missing shape alternatives were observed. Artefact editing acceptance remains unverified. Model/effort identity was not established from execution evidence, so runtime comparisons also failed; this run does not establish controlled-runtime parity. Evidence remains in the local ignored `bench/runs/` directory, because the input is private. This confirms completion of the real harness path and its failure reporting, not presentation acceptance or all-case coverage.

## Practical quality policy follow-up

[ADR 003](../architecture/adr-003-practical-benchmark-quality.md) and [plan 004](../plans/plan-004-practical-benchmark-quality.md) record the user-approved benchmark changes. Plugin 0.5.0, harness 0.2.0 and suite/evaluator 1.2.0 separate practical quality from full acceptance. Reference purpose and relationship scope distinguish illustrative internal artwork from meaningful technical relationships. Evidence-backed minor illustrative differences become observations; required content and technical correctness remain blockers. Visual fidelity, content/meaning, editability, accessibility and verification are independently reported in JSON/text/HTML; comparisons include before/after dimensions and require runtime evidence.

Attached connectors are optional unless the case opts in. Practical editing requires native editable text and independently movable major elements; raster crops and unattached lines must be disclosed. Full strict Folio acceptance remains in evaluator diagnostics. Accessibility gaps and unavailable application checks are retained, not relabelled as compliant.

The standard configuration allows 1200 seconds for generation and a separate 900 seconds for review, plus bounded evaluators. Omitted review allowances retain legacy shared-timeout behavior. Phase cancellation remains bounded; review timeouts preserve generation status, artifacts and partial evaluation. Regression tests verify independent budgets/timeout evidence, illustrative versus technical failures, attachment opt-in, missing required source text and stale evidence. Go race tests/vet, Python tests and plugin validation passed. No real deck was regenerated or historical result overwritten under this policy; prior Quick timeout and governed failure remain their original evidence.
