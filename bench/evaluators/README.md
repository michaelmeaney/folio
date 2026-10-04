# Evaluator protocol v1

Configuration schema 1 maps trusted evaluator names to either `kind: files` or `kind: external`. Cases name evaluators; they contain no command logic. External command definitions have argv, optional timeoutSeconds, explicit environment mappings (child variable -> parent variable), and secretEnvironment listing mapped child variables whose values must be redacted. Never put credentials in argv or checked-in JSON. Child processes inherit only PATH, HOME/USERPROFILE, system/temp/locale variables and explicit mappings. Secrets are not included in the manifest. Redaction covers declared secret values in captured logs/structured metadata; it cannot inspect arbitrary generated binary artifacts.

The trusted command registry is an execution trust boundary. No shell is inserted by the harness. A maintainer can explicitly configure an executable interpreter; the runner does not treat external fixtures as commands. IDs and artifact paths cannot traverse outside their declared roots. Frozen resource copies are regular files; symlinks are rejected.

Placeholders: `{prompt}`, `{review_prompt}`, `{reference}`, `{plugin}`, `{output}`, `{trial}`, `{run}`, `{config}`, `{model}`, `{effort}`, `{surface}`. External evaluators also receive `{resources}`, their frozen resource directory. Declare each resource path relative to configuration location; it is copied with that relative path under the evaluator resource directory.

stdin is exactly one EvaluationInput JSON object. Required fields are schemaVersion=1, runDirectory, trialDirectory, trialPath, case, reference, controls, systemCanvas; configurationDirectory identifies the trusted configuration location. Paths are absolute except trialPath. stdout is exactly one EvaluationResult object, no banners or progress. stderr is diagnostic logging. Responses over 10 MiB, malformed JSON, unknown result fields, unknown schema/status or nonzero process exits are infrastructure errors. Logs and evaluator JSON remain in each trial.

Example response:

```json
{
  "schemaVersion": 1,
  "status": "fail",
  "score": 0.84,
  "violations": [{"id": "composition", "message": "Primary diagram lost its explanatory weight"}],
  "diagnostics": {"sourceComparison": "output/review/comparison.png"},
  "contextIds": ["actual-generator-id", "actual-reviewer-id"],
  "runtime": {"model": "actual-model", "effort": "medium", "surface": "codex", "renderer": "actual-version", "application": "actual-version"}
}
```

Score, diagnostics, contextIds and runtime are optional for generic evaluators. Status is one of pass/fail/error/timeout/skipped/unverified. Source gates and runtime/context verification are owned by presentation judgment, not invented by the Go runner. Cross-trial context reuse is additionally checked by Go. Protocol schema is [../schemas/evaluator-v1.schema.json](../schemas/evaluator-v1.schema.json).

`presentation.py` is the migration adapter: it calls existing `check_trial`, maps accepted/failed/partial/not-run to pass/fail/unverified/unverified, and exposes the original metrics, missing evidence, gates and runtime. It performs no generation, orchestration, parallelism, process launching or report rendering.
