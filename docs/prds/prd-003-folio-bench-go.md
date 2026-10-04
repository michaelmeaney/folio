---
title: "Folio Go benchmark harness"
type: prd
status: in-progress
number: "003"
date: "2026-09-30"
---

Folio Benchmark Harness

Status: Draft
Product: Folio
Component: Benchmark Harness
Implementation: Go
Replaces: Python benchmark runner

1. Purpose

Folio currently uses a Python-based benchmark harness to execute benchmark cases and assess generated outputs.

The benchmark has evolved from development tooling into part of Folio’s engineering infrastructure. It now needs to operate as a first-class, reproducible tool suitable for local development, CI/CD, regression testing and release validation.

The existing Python implementation should therefore be replaced by a compiled Go executable with explicit interfaces, deterministic execution, structured results and portable distribution.

The objective is not to rewrite benchmark logic unnecessarily. The initial migration should separate benchmark orchestration from benchmark evaluation, allowing existing Python evaluators to continue operating where appropriate while Go becomes the authoritative execution layer.

⸻

2. Problem

The current Python benchmark was appropriate for rapid experimentation but introduces increasing operational friction as Folio matures.

The benchmark needs to become:

* straightforward to install and execute;
* independent of developer Python environments;
* reproducible between local and CI execution;
* deterministic in its orchestration behaviour;
* capable of parallel benchmark execution;
* resilient to failed or hung benchmark processes;
* capable of collecting complete diagnostic evidence;
* machine-readable for CI and automation;
* human-readable for development;
* portable across supported operating systems;
* versioned alongside Folio;
* suitable as a foundation for future benchmark capabilities.

A benchmark failure should mean that the benchmark detected a failure, not that a developer happened to have the wrong Python environment.

⸻

3. Goals

The Go benchmark harness SHALL:

1. Replace Python as the primary benchmark orchestration runtime.
2. Ship as a standalone folio-bench executable.
3. Execute Folio benchmark cases consistently locally and in CI.
4. Support deterministic benchmark discovery and execution.
5. Capture complete execution evidence and generated artefacts.
6. Provide stable machine-readable result formats.
7. Provide useful terminal output for humans.
8. Enforce benchmark-level timeouts and cancellation.
9. Support controlled parallel execution.
10. Preserve compatibility with existing benchmark evaluators during migration.
11. Provide meaningful process exit codes for CI.
12. Support comparison against previous or baseline benchmark runs.
13. Make benchmark execution sufficiently simple that contributors can run the same tests as CI.

⸻

4. Non-goals

The project SHALL NOT initially:

* rewrite Folio itself in Go;
* replace evaluators merely because they are written in Python;
* embed slide-generation logic into the benchmark harness;
* duplicate Folio validation logic;
* introduce a benchmark service or central control plane;
* require network infrastructure merely to execute benchmarks;
* make benchmark results dependent on terminal formatting;
* attempt to provide a general-purpose testing framework.

folio-bench is an orchestration and evidence-collection tool.

⸻

5. Design Principles

5.1 Harness, not implementation

The harness coordinates benchmark execution.

It SHOULD understand:

* cases;
* runs;
* commands;
* evaluators;
* artefacts;
* results;
* assertions;
* timing;
* diagnostics.

It SHOULD NOT understand how Folio internally generates slides.

This boundary prevents the benchmark and product implementation becoming coupled.

5.2 Results are data

Terminal output is a presentation of benchmark results, not the authoritative result.

Every run SHALL produce structured result data.

This enables:

* CI integration;
* regression analysis;
* historical comparison;
* alternative reporting;
* future dashboards;
* automated quality gates.

5.3 Evidence over opaque scores

A benchmark score alone is insufficient.

Results SHOULD preserve the underlying evidence necessary to understand why a case passed, failed or changed.

5.4 Deterministic orchestration

Given identical inputs and external dependencies, the harness SHOULD execute the same cases with the same configuration and evaluation sequence.

Where generation itself is non-deterministic, that uncertainty MUST be distinguished from harness behaviour.

5.5 Progressive migration

The Go migration MUST NOT require a big-bang rewrite of existing Python benchmark logic.

⸻

6. User Personas

Folio developer

Needs to run:

folio-bench run

and determine whether a change has improved, degraded or broken Folio.

Contributor

Needs a documented benchmark command that works without reconstructing the maintainer’s Python environment.

CI/CD pipeline

Needs deterministic execution, structured output and meaningful exit status.

Maintainer

Needs to compare runs, inspect failed artefacts and evolve benchmark criteria without redesigning the runner.

⸻

7. CLI

The executable SHALL be named:

folio-bench

Initial command structure:

folio-bench run
folio-bench list
folio-bench validate
folio-bench compare
folio-bench report
folio-bench version

7.1 run

Executes benchmark cases.

Examples:

folio-bench run
folio-bench run composition
folio-bench run --case composition-001
folio-bench run --category reconstruction
folio-bench run --parallel 4
folio-bench run --output ./runs

The command SHALL:

1. load benchmark configuration;
2. discover applicable cases;
3. validate case definitions;
4. create a unique run;
5. execute cases;
6. invoke configured evaluators;
7. collect artefacts;
8. persist results;
9. display a summary;
10. return the appropriate exit code.

⸻

7.2 list

Lists available benchmark cases and metadata.

Example:

CASE                         CATEGORY          EVALUATORS
composition-001              composition       geometry, visual
typography-001               typography        typography
reconstruction-001           reconstruction    geometry, visual

⸻

7.3 validate

Validates benchmark definitions without performing generation.

It SHOULD detect:

* malformed configuration;
* missing fixtures;
* missing reference assets;
* unknown evaluators;
* duplicate case IDs;
* invalid paths;
* unsupported schema versions.

This SHOULD be fast enough to use as a pre-commit or CI validation step.

⸻

7.4 compare

Compares two benchmark runs.

Example:

folio-bench compare \
  runs/baseline/results.json \
  runs/current/results.json

Comparison SHOULD identify:

* newly passing cases;
* newly failing cases;
* score changes;
* changed violations;
* execution-time changes;
* missing or added cases.

The command SHOULD distinguish structural benchmark changes from actual regressions.

⸻

7.5 report

Produces a human-readable report from structured benchmark results without re-running benchmarks.

This separation ensures presentation changes do not require benchmark execution.

⸻

8. Benchmark Structure

Recommended repository structure:

benchmark/
├── cases/
│   ├── composition/
│   ├── typography/
│   ├── reconstruction/
│   ├── diagrams/
│   └── governed/
│
├── fixtures/
├── references/
├── evaluators/
└── schemas/
cmd/
└── folio-bench/
internal/
├── benchmark/
├── runner/
├── evaluator/
├── artifact/
├── result/
├── compare/
└── report/

Generated data SHOULD remain outside the source benchmark definitions:

runs/
└── <run-id>/
    ├── manifest.json
    ├── results.json
    ├── logs/
    └── artefacts/

⸻

9. Benchmark Case Contract

Every benchmark SHALL have a stable unique identifier.

Conceptually:

id: reconstruction-001
name: Preserve reference composition
category: reconstruction
input:
  prompt: prompt.md
  reference: reference.png
execution:
  timeout: 120s
evaluators:
  - composition
  - typography
  - visual
tags:
  - lumen
  - governed

The exact serialisation format MAY evolve, but the logical contract SHOULD remain stable.

Case definitions SHOULD contain configuration rather than executable orchestration logic.

⸻

10. Run Manifest

Every invocation SHALL generate a manifest describing the execution environment.

The manifest SHOULD include:

run_id
timestamp
folio_bench_version
folio_version
git_commit
git_branch
operating_system
architecture
benchmark_schema_version
configuration
selected_cases
parallelism

Where relevant it MAY additionally capture model/provider configuration required to reproduce the generation environment.

Secrets MUST NOT be written to manifests.

⸻

11. Result Model

The Go implementation SHALL define a stable internal result model.

Conceptually:

type Result struct {
    CaseID      string        `json:"case_id"`
    Status      Status        `json:"status"`
    Duration    time.Duration `json:"duration"`
    Score       *float64      `json:"score,omitempty"`
    Violations  []Violation   `json:"violations,omitempty"`
    Artifacts   []Artifact    `json:"artifacts,omitempty"`
    Diagnostics Diagnostics   `json:"diagnostics"`
}

Status SHOULD distinguish at minimum:

pass
fail
error
timeout
skipped

A benchmark assertion failure is not equivalent to infrastructure failure.

For example:

FAIL

means Folio generated an output that failed evaluation.

ERROR

means the benchmark could not successfully evaluate the case.

This distinction is essential for CI signal quality.

⸻

12. Evaluator Interface

Evaluators SHALL operate behind an explicit interface.

Conceptually:

type Evaluator interface {
    Name() string
    Evaluate(
        ctx context.Context,
        input EvaluationInput,
    ) (EvaluationResult, error)
}

An evaluator receives declared inputs and returns structured results.

The harness SHALL NOT require all evaluators to be implemented in Go.

⸻

13. Legacy Python Compatibility

Existing Python evaluation logic SHOULD initially be retained where rewriting it provides no immediate benefit.

The Go harness SHALL support external evaluators.

Conceptually:

Go harness
    │
    ├── Native Go evaluator
    │
    └── External evaluator
            │
            └── Python

Communication SHOULD use a documented structured protocol rather than parsing human-readable stdout.

For example:

stdin  → EvaluationInput JSON
stdout ← EvaluationResult JSON
stderr ← diagnostic logging

This creates a language-neutral evaluator boundary.

The Python implementation can therefore progressively shrink without blocking delivery of the Go harness.

⸻

14. Process Execution

The harness SHALL provide robust subprocess management.

Requirements:

* use context.Context for cancellation;
* enforce configurable timeouts;
* capture stdout;
* capture stderr;
* preserve exit codes;
* terminate child processes following cancellation;
* prevent hung benchmarks from blocking the complete run;
* record execution duration;
* preserve diagnostics following failure.

A failed benchmark process MUST NOT normally terminate unrelated benchmark cases.

⸻

15. Parallel Execution

The harness SHALL support parallel case execution.

Parallelism MUST be bounded.

Example:

folio-bench run --parallel 4

Implementation SHOULD use a bounded worker pool rather than unconstrained goroutines.

Default concurrency SHOULD be conservative and configurable.

Individual benchmark artefacts MUST be isolated to prevent concurrent cases modifying one another’s state.

⸻

16. Artefact Management

Every case SHALL receive an isolated working directory.

Example:

runs/<run-id>/artefacts/reconstruction-001/

The harness SHOULD retain relevant artefacts including:

* generated PPTX;
* rendered slide images;
* evaluator outputs;
* comparison images;
* validation reports;
* relevant logs;
* diagnostic metadata.

Artefacts SHOULD be retained for failed cases by default.

Retention of successful-case artefacts MAY be configurable to control CI storage.

⸻

17. Logging

Logging SHALL distinguish:

* normal user-facing progress;
* structured diagnostics;
* subprocess output.

Interactive execution SHOULD remain concise.

Example:

Folio Benchmark 0.1.0
Running 42 cases with 4 workers
PASS  composition-001          8.2s
PASS  composition-002          7.9s
FAIL  reconstruction-004      11.4s
PASS  typography-001           6.1s
41 passed
1 failed
0 errors
Duration: 1m 48s

Verbose diagnostics SHOULD be available through an explicit option.

⸻

18. Exit Codes

Exit status SHALL have stable semantics.

Recommended contract:

0   All selected benchmarks passed
1   One or more benchmark assertions failed
2   Harness/configuration error
3   One or more benchmark executions errored
4   One or more benchmarks timed out

Where multiple conditions occur, precedence MUST be documented and deterministic.

CI SHOULD therefore be able to distinguish:

Folio regression

from:

benchmark infrastructure broken

⸻

19. Comparison and Regression Detection

A benchmark system becomes substantially more useful when it can evaluate change rather than merely current state.

folio-bench compare SHOULD therefore treat benchmark runs as comparable datasets.

For each case it SHOULD identify:

previous → current
PASS → PASS
PASS → FAIL
FAIL → PASS
FAIL → FAIL

Where numerical measurements exist, it SHOULD report deltas rather than merely replacing previous values.

Example:

composition-004
Composition similarity
0.91 → 0.84 (-0.07)
Typography violations
1 → 3 (+2)
Status
PASS → FAIL

Threshold policy SHOULD remain part of benchmark configuration rather than being hard-coded into the comparison engine.

⸻

20. Reproducibility

The harness SHALL capture enough metadata to establish what was actually tested.

Where available:

* Folio version;
* benchmark version;
* Git SHA;
* model identifier;
* benchmark configuration;
* evaluator versions;
* relevant generation parameters.

Exact reproducibility cannot be guaranteed where model generation is stochastic.

The harness SHOULD therefore distinguish execution reproducibility from generation determinism.

⸻

21. Security

The benchmark harness executes external processes and handles generated files.

Baseline controls:

* arguments SHALL be passed as structured process arguments rather than shell-concatenated strings;
* benchmark IDs SHALL NOT permit path traversal;
* output directories SHALL be controlled by the harness;
* secrets SHALL be redacted from logs and manifests;
* evaluator environment variables SHOULD be explicitly controlled;
* downloaded or external benchmark fixtures SHOULD NOT implicitly become executable;
* untrusted benchmark definitions MUST NOT be interpreted as arbitrary shell commands.

The harness SHOULD treat evaluator execution as a trust boundary.

Future sandboxing MAY be introduced if Folio begins accepting third-party benchmark suites or evaluator plugins.

⸻

22. Distribution

The harness SHOULD be released as native binaries for:

darwin/arm64
darwin/amd64
linux/amd64
linux/arm64
windows/amd64

Primary developer distribution SHOULD support:

brew install folio-bench

GitHub Releases SHOULD expose the underlying binaries and checksums.

Release artefacts SHOULD be generated automatically.

Release binaries SHOULD be signed or accompanied by verifiable provenance as the Folio release pipeline matures.

⸻

23. CI Integration

CI SHOULD execute the same binary developers execute locally.

No separate “CI benchmark implementation” SHOULD exist.

A typical pipeline becomes:

Build Folio
      ↓
Install/build folio-bench
      ↓
folio-bench validate
      ↓
folio-bench run
      ↓
folio-bench compare baseline current
      ↓
Upload results + failed artefacts

The structured results.json SHALL be treated as the canonical CI output.

⸻

24. Migration Strategy

Phase 1 — Establish Go Harness

Implement:

* CLI;
* configuration loading;
* case discovery;
* execution lifecycle;
* run directories;
* result schema;
* logging;
* exit codes;
* process supervision.

The objective is functional parity with the current Python orchestration.

No evaluator rewrite is required.

Phase 2 — External Python Evaluators

Wrap existing Python evaluation logic behind the evaluator protocol.

Go becomes authoritative for:

discovery
execution
timeouts
parallelism
artefacts
results
reporting
exit status

Python remains responsible only for evaluation logic that still benefits from Python.

Phase 3 — Comparison and Reporting

Introduce:

folio-bench compare
folio-bench report

Establish baseline and regression workflows.

Phase 4 — Selective Native Migration

Review remaining Python evaluators individually.

Move an evaluator to Go only where doing so improves:

* portability;
* performance;
* reliability;
* dependency reduction;
* maintainability.

Python removal is an outcome, not an arbitrary requirement.

Phase 5 — Retire Python Harness

Once orchestration parity and CI stability are demonstrated:

* remove the Python runner;
* retain only explicitly justified Python evaluators;
* update contributor documentation;
* make folio-bench the sole supported benchmark entry point.

⸻

25. Migration Acceptance Criteria

The Python harness SHALL NOT be retired until:

1. Every existing benchmark can be discovered by folio-bench.
2. Existing benchmark cases execute successfully through the Go runner.
3. Result parity has been validated against representative Python runs.
4. Timeout behaviour has been verified.
5. Failure and infrastructure-error states are correctly distinguished.
6. Parallel execution does not corrupt benchmark artefacts.
7. Local and CI execution use the same benchmark interface.
8. Results are persisted as structured data.
9. Failed cases preserve sufficient diagnostics for investigation.
10. macOS and Linux release binaries have been exercised.
11. Benchmark documentation references the Go harness as the primary interface.

⸻

26. Success Metrics

The migration is successful when:

Developer experience

A clean Folio checkout can execute benchmarks without establishing a project-specific Python environment for the harness.

Reliability

Harness failures are distinguishable from Folio benchmark failures.

Reproducibility

Every benchmark run produces a manifest identifying the code, configuration and benchmark suite executed.

CI integration

The same executable and command contract are used locally and in CI.

Portability

Supported developer and CI platforms can execute an officially built binary.

Maintainability

Adding a benchmark case primarily involves declaring the case and its evaluators rather than modifying runner control flow.

⸻

27. Architectural Constraint

The most important long-term constraint is:

folio-bench owns execution. Evaluators own judgement. Folio owns generation.

These boundaries SHOULD remain explicit.

The benchmark harness should become infrastructure: predictable, portable and comparatively boring.

That leaves benchmark sophistication — composition analysis, visual comparison, typography, design-system conformance and future model-based evaluation — free to evolve independently of the machinery responsible for running it.