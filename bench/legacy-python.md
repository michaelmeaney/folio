# Folio presentation benchmark

Run the same reference through three fixed tasks when evaluating a plugin version.

| Case | Mode / operation | Output | What it tests |
| --- | --- | --- | --- |
| `quick-convert` | Quick / Convert | 1 slide | Faithful composition, source styling, visible copy and editable reconstruction |
| `governed-restyle` | Governed / Restyle | 1 slide | Selected design system applied while preserving content, relationships and composition |
| `governed-story` | Governed / Redesign | 5 slides | Coherent narrative, meaningful decomposition, all source facts and editable diagrams |

Lumen is the default system. `--design-system` accepts another system registered in the plugin under test. Quick never loads that system. Five slides is a fixed benchmark requirement, not a general Folio rule.

## Reference and versioning

Place the original `Banner for Azure-Sample.png` in `bench/reference/`, or supply `--reference /absolute/path/to/image.png`. Its SHA-256 must match `reference/reference.json`. The image and generated runs are local and gitignored; they are not publication-cleared examples. Source product claims are test content, not independently verified claims.

`reference/reference.json` is the reviewer answer key: source text, facts, approximate regions and interpretation cautions. The generator receives the actual image and case brief, not that answer key. Reviewers should inspect the image as well: neither approximate frames nor automatic text matches prove visual fidelity.

Freeze this benchmark when comparing releases. Changes to its prompts, fixture, criteria or runner require a suite version bump and a new baseline. Every run fingerprints these inputs and snapshots the plugin files, so even equal plugin version labels can be distinguished by content. Hashes detect accidental changes; they are not a secure isolation boundary against the executing agent.

## 1. Prepare a run

Python 3.10+ is sufficient for the runner. PowerPoint generation and rendering dependencies belong to the executor.

From the repository root:

```bash
python3 bench/runner.py prepare \
  --plugin-root /Users/michaelmeaney/plugins/folio \
  --model gpt-6-astra --effort medium --surface codex \
  --design-system lumen --repetitions 1 \
  --output bench/runs/folio-0.3.0-baseline
```

Use three repetitions for a release comparison; one is a smoke run. Prepare baseline and candidate with the same reference, suite, model, effort, surface, design-system selection, repetition count and timeout. Record exact model IDs and actual renderer/application versions. A design-system change bundled in a plugin is part of the candidate change; changing which system is selected makes runs incomparable.

The result contains frozen `inputs/`, a `run.json` manifest, and one independent `cases/<case>/rNN/` directory per trial. Each trial contains `prompt.md`, `review-prompt.md`, an empty `output/`, and a pending `review.json`. Preparing a run does not execute a model.

## 2. Execute each brief in fresh context

Dispatch each `prompt.md` to a new subagent with `fork_turns="none"` when using Codex collaboration tools, or a new session without inherited conversation on another host, with the frozen plugin and image accessible. Use the recorded model and effort. Do not expose previous outputs, other trials or the answer key to the generator. The benchmark grants the stated operation and permissions in advance. Record any additional human intervention or repair in execution notes.

For automated execution, use an executor command that starts a fresh session for every invocation and reads the brief from stdin:

```bash
python3 bench/runner.py run bench/runs/folio-0.3.0-baseline \
  --case quick-convert --executor /absolute/path/to/fresh-session-executor
```

Omit `--case` to run every prepared trial sequentially. Additional arguments after `--executor` belong to that command. Literal placeholders `{prompt}`, `{reference}`, `{plugin}` and `{output}` expand to absolute paths. No shell expansion is performed. Configure the executor's actual model, effort, tools and permissions yourself; preparation metadata does not configure them. A fresh process alone does not prove fresh model context: the executor must not resume a session.

The runner captures stdout, stderr, elapsed time, exit status and timeout. It refuses to overwrite an attempted trial. Prepare a new run for another attempt. Token usage, cost, repairs and interventions remain unobserved unless recorded from real evidence. Manual execution is supported but has no runner-measured time.

Required output per trial:

- `output/deck.pptx` with native editable text and reconstructable diagrams.
- `output/render/slide-01.png` etc., actual renders at least 1280 pixels wide.
- `output/execution-notes.md`, source analysis, useful reconstruction scripts and source-to-object mapping.

## 3. Review the actual result

Dispatch each `review-prompt.md` to another new subagent with `fork_turns="none"`, or an independent fresh session on another host. A human may perform the application editing checks and supply evidence to that reviewer. Read the frozen suite's criterion descriptions and reference facts. Inspect all slides at whole-slide and detail scale, and open the actual deck in the recorded application. Follow [the editing regression procedure](../docs/implementation/runbook-002-composition-regression.md) for text, shapes and every claimed connector attachment family. Edit a copy so the delivered deck remains fingerprinted.

Fill `review.json` with unique generation/review context IDs and verified `inheritance: "none"`, reviewer identity, actual runtime, deck SHA-256 and each render SHA-256. Each criterion and source fact requires `pass`, `fail` or `unverified`, concrete notes and evidence. Evidence paths are relative to the trial directory and must identify existing files with matching SHA-256 values. Example:

```json
{
  "status": "pass",
  "notes": "Moved both connector endpoints independently, saved and reopened; both attachments survived. See before/after captures and editing log.",
  "evidence": [
    {"path": "output/review/editing-log.md", "sha256": "<actual SHA-256>"}
  ]
}
```

A note claiming success does not replace the observed operation. The runner checks evidence linkage, not the truth of a review. In particular:

- Source text found in XML may be clipped, hidden or unreadable; check visible copy.
- Shape/connector counts do not prove semantic editability or valid attachments.
- A large image can be decorative; review its role before judging flattening.
- PNG validation does not establish that it came from this PowerPoint; inspect actual rendering.
- Quick fidelity can conflict with mandatory accessibility; disclose the conflict and leave the affected requirement failed or unverified. Never silently restyle to make the case pass.
- Story quality requires a coherent beginning, progression and conclusion. All material source facts must appear on visible slides. Do not reward unsupported technical inventions or five disconnected crops.

Content, composition, treatment and artefact gates must pass independently. Missing context evidence is `partial`; reused generation/review context IDs fail. Missing evidence is `partial`; an explicit failed gate or structural check is `failed`. No deck is `not-run` until an execution attempt is recorded, then `failed`. No aggregate aesthetic score can hide a failure.

## 4. Inspect and compare

```bash
python3 bench/runner.py check bench/runs/folio-0.3.0-baseline
python3 bench/runner.py compare bench/runs/folio-0.3.0-baseline bench/runs/candidate
```

`check` writes `report.json` and a local `report.html` showing the source, output slides and outstanding gates. Exit codes: 0 all accepted; 1 incomplete or failed; 2 invalid inputs/run.

`compare` requires completed reviews, identical benchmark controls, and verified matching model/renderer/application profiles, including for failed attempts. It reports accepted trials per case and median elapsed time for accepted executions. Exit codes: 0 no acceptance-count regression; 1 regression; 2 incomparable or incomplete. Equal acceptance counts do not establish statistical equivalence or equal visual quality. Review the actual slides and evidence alongside the report.

Use the frozen `inputs/runner.py` to inspect historical runs after this harness changes. Keep generated decks local until reviewed and explicitly approved for publication.

## Harness verification

```bash
python3 -m unittest discover -s tests -p 'test_folio_bench.py' -v
```

Synthetic tests exercise the harness without requiring the private source image, a model call or presentation software. They do not establish plugin benchmark acceptance.
