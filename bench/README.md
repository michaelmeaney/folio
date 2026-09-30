# Folio benchmark

`folio-bench` is the primary orchestration interface. Go owns discovery, fresh-process execution, bounded concurrency, timeouts, artifacts, results, comparison and reports. Evaluators own judgment; Folio owns generation. The retained Python presentation evaluator uses the same acceptance logic as the historical runner.

## Install and inspect

Build with Go 1.25 or later; no Python is needed for the harness or native file evaluator:

```bash
go build -trimpath -o dist/folio-bench ./cmd/folio-bench
dist/folio-bench version
dist/folio-bench list
dist/folio-bench validate
```

The binary can be placed on PATH. Run from a Folio checkout or pass `--config /absolute/path/to/benchmark.json`. `list` works without the private image; `validate` requires all fixtures and hashes to match. The actual presentation evaluator requires Python 3.10+; optional semantic schema checks use `requirements-schema.txt`. This dependency belongs to the selected evaluator, not Go orchestration.

`python3 scripts/build_bench.py` builds archives and SHA-256 checksums for Darwin arm64/amd64, Linux arm64/amd64 and Windows amd64 under `dist/folio-bench-release/`. CI builds these automatically and uploads them as artifacts. GitHub release publication, a public Homebrew tap and signed provenance remain release work; they are not claimed by a local build.

## Cases and reference

| Case | Category | Operation | Output |
| --- | --- | --- | --- |
| quick-convert | reconstruction | Quick Convert | One faithful editable slide |
| governed-restyle | governed | Governed Restyle | One composition-preserving slide |
| governed-story | composition | Governed Redesign | Five slides forming a coherent story |

The default selected system is Lumen, explicitly preconfirmed by the fixed benchmark brief. Quick loads no system. Another registered system can be selected in configuration. Five slides is a benchmark control, not a general Folio rule.

Place the original `Banner for Azure-Sample.png` in `bench/reference/` or set the configuration's `reference` path. `reference/reference.json` fingerprints it and provides a reviewer answer key: visible text, semantic facts and approximate regions. The image and runs stay gitignored. The generator receives the image and fixed brief, not the answer key. Source product claims are benchmark content, not independently verified claims.

## Run

```bash
dist/folio-bench run
dist/folio-bench run composition --parallel 1
dist/folio-bench run --case quick-convert --output bench/runs --json
dist/folio-bench run --category governed --verbose
```

`bench/benchmark.json` configures fresh `codex exec` sessions for generation and independent review. The command uses the configured model and effort, an ephemeral session, the workspace-write sandbox and the trial directory as an additional writable root. Authentication and model access must already be configured. The harness never bypasses approval or sandboxing. A host that cannot perform real editing leaves those checks unverified.

Change trusted command registry entries to use another executor. Commands are argv arrays with no implicit shell; stdin carries the prepared generation/review brief. One fresh process/session is started per task. Never configure `resume` or pass accumulated parent conversation. When using collaboration agents directly, use `fork_turns="none"` for each generation and each review. The reviewer must verify actual context IDs and runtime; a process start alone does not establish absent conversation inheritance.

Start with one repetition for a smoke run. Use three repetitions for release comparisons. Set controls explicitly: model, effort, surface, design system, repetition count and timeout. `--parallel` is bounded to 1..64, defaults to one and controls complete trial pipelines. Each trial's timeout bounds generation plus review plus evaluation; individual command timeouts can be shorter. Ctrl-C cancels running subprocess trees and persists remaining cases as skipped. Failures leave all artifacts and logs in place.

Every run gets a new directory:

```text
bench/runs/<unique-id>/
  manifest.json
  results.json
  inputs/                    # frozen plugin, suite, reference, prompts and evaluator resources
  artefacts/<case>/rNN/
    prompt.md
    review-prompt.md
    review.json
    execution.json
    evaluation-<name>.json
    logs/
    output/deck.pptx
    output/render/slide-01.png
    output/execution-notes.md
```

Results are written initially and after each completed trial, then atomically finalized in stable case/repetition order. The manifest records harness/plugin/suite versions, plugin hashes and Git identity when available, platform, controls, parallelism and all frozen input hashes. The harness detects modified frozen inputs. This is change detection, not filesystem sandbox isolation.

## Evaluation and review

The native `files` evaluator checks declared files for existence/nonempty content. It is suitable for harness fixtures, not presentation quality. The external `presentation` evaluator receives protocol JSON and calls retained Python judgment. See [the evaluator protocol](evaluators/README.md).

Generation must produce actual PowerPoint and per-slide renders. Review each slide at whole-slide and detail scale, verify visible copy and relationships, and exercise claimed editing operations in a named application. Follow [the editing procedure](../docs/implementation/runbook-002-composition-regression.md). Put review evidence under the trial's `output/review/` directory and fingerprint evidence, deck and renders in `review.json`. Generation and review context IDs must be distinct and unique across the run. Missing context/runtime/editing evidence is unverified; reused contexts fail.

Content, composition, treatment and artefact gates pass independently. XML text matches may be hidden or clipped; shape counts do not prove meaningful editing or attachment; valid PNG chunks do not prove the image came from this deck. Quick accessibility conflicts must be disclosed rather than silently restyled. A coherent story retains every material source fact visibly without unsupported technical inventions. Evidence references are bookkeeping, not proof that a review happened.

## Results, exit codes and comparisons

Statuses: `pass`, `fail` (assertion), `error` (execution/evaluation infrastructure), `timeout`, `skipped` (cancellation), `unverified` (incomplete acceptance evidence).

| Exit | Meaning |
| --- | --- |
| 0 | All selected cases passed |
| 1 | Assertions failed, or a comparable candidate regressed |
| 2 | Configuration/schema/input/report error, or structurally incomparable datasets |
| 3 | Execution/evaluation error, cancellation or unverified acceptance |
| 4 | Execution timed out |

Before execution, configuration errors exit 2. After execution, cancellation exits 3; otherwise precedence is timeout 4, error/unverified/skipped 3, assertion failure 1, success 0. A failed generation process is infrastructure error even if evaluators find missing content. A failed evaluator assertion is fail, not process failure.

```bash
dist/folio-bench report bench/runs/<id>/results.json
dist/folio-bench report --output bench/runs/<id>/report.html bench/runs/<id>/results.json
dist/folio-bench compare runs/baseline/results.json runs/candidate/results.json
```

Reports read structured results without re-running generation or evaluation. HTML must be beside results.json to preserve portable artifact links. Comparisons report added/missing cases, status transitions, scores, time deltas and changed violations. Suite/prompts/evaluator resources, command configuration, model/effort/system controls and comparison policy must match before claiming regression. Verified actual renderer/application profiles must also match when the evaluator supplies them. Generation context IDs deliberately differ across runs.

`comparison.maxScoreDrop` sets the allowed negative score delta; no aesthetic threshold is embedded in the runner. A single evaluator's score is retained; multiple evaluators retain individual scores without averaging them into an opaque grade. Equal pass counts do not prove statistical equivalence.

## CI and migration

```bash
go test -race ./...
go vet ./...
go build -o dist/bench-fixture ./bench/ci
dist/folio-bench validate --config bench/ci/benchmark.json
dist/folio-bench run --config bench/ci/benchmark.json --parallel 2
```

The CI configuration uses deterministic synthetic files, no model calls and no private slide. It validates orchestration, not Folio presentation quality. macOS and Linux CI use the same executable and commands as developers.

The [historical Python procedure](legacy-python.md) remains available for existing frozen Python runs. Do not compare its run.json/report.json directly with Go results.json. Keep the Python runner until all PRD migration gates, including real presentation parity and observed macOS/Linux execution, have evidence. See [implementation 005](../docs/implementation/implementation-005-go-benchmark-harness.md).
