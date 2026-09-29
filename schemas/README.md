# Folio semantic schemas

`folio-0.1.0.schema.json` describes the draft, renderer-neutral contracts for design-system manifests, presentation profiles, components, bindings, patterns, archetypes, compositions, scenes, visual specifications and execution results. The schemas validate structure. `scripts/folio_schema.py` adds package, token and cross-contract checks. Neither check establishes visual fidelity or PowerPoint editing capability.

The six bundled systems now declare `resources.tokens` and `resources.presentation`. Edit these DTCG tokens and profiles as the canonical source. The top-level `tokens` paths remain derived compatibility files for existing Folio installations. Run `scripts/migrate_design_system_tokens.py <system> --sync-legacy` after canonical edits, then `--check` to detect drift. `--from-legacy` is only for bootstrapping a previously unmigrated system because it overwrites schema resources.

Each migrated system includes semantic aliases for canvas and text, plus muted text, a single focus colour and status colours where its own palette defines them. Werk deliberately has no single focus alias because its red, blue and yellow accents are chosen by context. Aliases point to the system's existing colours; they do not add new palette values.

## Validate

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-schema.txt
python3 scripts/validate_plugin.py .
.venv/bin/python scripts/folio_schema.py design-systems/lumen schemas/examples/components/database.json schemas/examples/components/bindings/database.native.json schemas/examples/components/scenes/database.scene.json schemas/examples/patterns/data-flow.json schemas/examples/compositions/data-flow.json schemas/examples/scenes/data-flow.json schemas/examples/archetype.json schemas/examples/visual-specification.json schemas/examples/execution-result.json
python3 scripts/migrate_design_system_tokens.py design-systems/lumen --check
```

Run the schema and drift checks for each registered design system. `--show-tokens color.primary typography.body` prints only the selected resolved values for an agent or renderer. Every emitted value retains its source path; migrated dimensions also retain the legacy unit and value under the Folio DTCG extension key.

## Boundaries

The token resolver supports the declared initial types, curly aliases and local JSON Pointer values. It rejects duplicate leaf paths, missing references, cycles and invalid units. The schema does not yet implement DTCG group extension, Resolver contexts, arbitrary color spaces, rendering, constraint solving, OpenUI projection, or PowerPoint editing tests. Unknown required capabilities must fail until implemented. The examples demonstrate contracts and validation only; they are not finished deck artefacts.

## Composition preservation in 0.2.0

`folio-0.2.0.schema.json` versions the three changed document kinds: visual-specification, scene and execution-result. Other kinds continue to use 0.1.0. The CLI selects the schema by each document's `schemaVersion`; 0.1.0 system/token packages can coexist with 0.2.0 visual specifications, scenes and execution results. The old schema and examples remain readable. A legacy `accepted` value does not establish the newer preservation or evidence guarantees.

For new reference runs, use 0.2.0:

- `visual-specification` replaces untyped `observations` with required source dimensions/hash/slide count, stable regions, normalised frames and per-region tolerances, typed relationships, hierarchy, confidence/ambiguity, intent and scoped deviations. Empty source analysis fails. Confirm the analysis before output generation.
- `scene.preservation` identifies its visual specification and baseline digest, maps every region/relationship to output objects, and declares the primary region. One source region may map to multiple native objects. Functional objects must be traced; decoration is explicit. Region geometry and visible text, relationship types/direction/labels/endpoints, grouping and reading order are checked independently. The scene's `slideIndex` exposes unauthorised moves to detail slides.
- `execution-result` records intent, delivered scenes, provenance, material differences, four independent gate results and host editing checks. Accepted requires every gate to pass with current local evidence and no unresolved findings. The composition gate includes source and final render; the artefact gate fingerprints the actual `.pptx` and render. Claimed editing operations require named application/version test records.

Baseline digests use SHA-256 of UTF-8 JSON with sorted keys, compact separators, unescaped Unicode and finite numbers (`folio_preservation.baseline_digest`). Source and evidence digests use raw file bytes. Paths are local to the run directory and referenced scene/specification directories; remote reports must first be saved locally. Record authorisation references from the actual user instruction or confirmed scope, not invented approval.

Each region and relationship maps once across the output slides. Splitting one source region into multiple slides or mapping a relationship across slides is not yet supported. A whole region may move only with scoped slide-splitting permission, and its relationship endpoints must remain representable together. Relationships must preserve their meaning even during Redesign. Geometry drift needs `recompose` permission and a deviation naming each affected region; `Redesign` alone is not a blanket exemption. Copy rewriting, omission, consolidation and primary-visual replacement have separate permissions. Every material deviation must appear in accepted execution differences.

Migrate by inspecting the actual source and producing the new baseline and trace; changing the version string alone is insufficient. Old runs without source analysis or host evidence remain legacy/partial. Do not invent missing data or promote old accepted states automatically.

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/folio_schema.py design-systems/lumen \
  tests/fixtures/composition/specification.json \
  tests/fixtures/composition/scene.json \
  tests/fixtures/composition/result.json
```

The fixture remains partial because no deck was rendered or edited. Tests that simulate accepted evidence use temporary synthetic files and validate bookkeeping only. The validator checks digests and record consistency, not evidence authenticity, baseline capture time, text measurements, visual hierarchy or actual host editing behaviour. Office package-part and slide-count checks do not establish that PowerPoint opens or renders correctly. Follow [the host regression procedure](../docs/implementation/runbook-002-composition-regression.md) before claiming output acceptance.
