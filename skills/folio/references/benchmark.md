# Independent benchmark execution

Use this procedure when the user requests the standard benchmark or a plugin version comparison. The repository's `folio-bench` Go executable is the primary execution interface. `bench/README.md` describes configuration, execution and reporting; `bench/suite.json` fixes the cases. The Python runner is retained for historical runs and evaluator migration, not the primary orchestrator. A standalone installation may use an externally prepared run without the repository tooling.

Only the benchmark coordinator dispatches workers. If you have already been assigned one generation or review trial in a fresh context, perform that task directly; do not dispatch another agent, wait for agents or restart the harness.

## Generation contexts

Use one new agent/session per case and repetition. For Codex collaboration tools, spawn with `fork_turns="none"`; do not reuse that worker for another trial. Other hosts must start a new session without inherited conversation or a resume flag. If the host cannot establish fresh context, record the limitation and leave isolation unverified.

Give each worker its prepared `prompt.md`, the source image, the frozen plugin Skill and declared resources, and its own output directory. The prompt already confirms operation, mode, selected system, preservation permissions and slide count. Follow that scope without asking for confirmation again unless an actual conflict blocks execution.

Keep the reviewer answer key, earlier outputs, other trials and parent analysis out of the generation handoff. Read the image directly. The coordinator may inspect manifests and execution status but should not supply its own reconstruction or narrative to the generator. Record the actual worker/session ID, inheritance setting, model and effort in execution notes. A fresh operating-system process is insufficient if it resumes a model session.

## Review contexts

After generation, dispatch another new agent/session with no inherited conversation. Give it the prepared `review-prompt.md`, reference, frozen rubric/answer key, actual PowerPoint, rendered slides and execution evidence. Do not supply the generator's conclusion as the intended grade. Each reviewer evaluates one trial and records a distinct context ID.

Inspect visible content, composition, selected treatment and real application editing separately. Record failed requirements and unavailable checks honestly. File existence, XML text matches and passing validators do not prove visual fidelity or application editing. A reviewer may return partial evidence if presentation software is unavailable; the coordinator must preserve that result.

The standard suite uses `practical-v1`: report visual fidelity, content/meaning, practical editability and accessibility independently, with pass, needs-work or unverified. Full Folio acceptance and runtime/application verification remain separate evidence, not implied by the practical quality result. Accessibility conflicts stay visible even when a faithful conversion preserves them.

Use each reference region's purpose and relationship scope. Illustrative artwork conveys recognisability and visual weight; its unlabelled internal arrows do not necessarily assert technical topology. Exact direction/endpoint checks apply where relationships carry meaning. For a minor illustrative difference, record region, purpose=illustrative, severity=minor, notes and hashed evidence. Missing required content, unreadable text, changed technical meaning and flattened core content are material. Never downgrade a technical relationship failure because the drawing is visually attractive.

Practical editability means editable native text and independently movable major elements. Inspect object representations and grouping; disclose image crops and unattached lines. Attached connectors are an optional capability unless the case explicitly sets `requireAttachedConnectors`. Only claim endpoint attachment after the named application move/resize test. Unavailable PowerPoint checks remain unverified; do not invent host validation.

Generation and review have independent time allowances in the standard configuration. Preserve generation status, deck and render if review times out; report incomplete review independently from presentation quality. Do not reinterpret or overwrite historical frozen results under a newer rubric.

## Coordination and comparisons

The parent dispatches workers, waits for completion, checks delivered files and produces the report. It does not generate all cases in its own context or accept its own accumulated analysis as independent review. Context IDs must be unique across generation and review tasks in a run. Retain actual runtime evidence for failed attempts too.

Run baseline and candidate with identical frozen benchmark inputs and controls, and fresh workers for every trial. A candidate receives no baseline results during generation. Use the frozen run's checker to report four independent gates and compare only fully reviewed, comparable runs. Keep unreviewed decks local; benchmark execution does not authorise publication or promotion into examples.
