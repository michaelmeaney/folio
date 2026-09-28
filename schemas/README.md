# Folio schema 0.1.0

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
