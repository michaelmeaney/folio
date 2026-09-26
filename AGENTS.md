# Folio plugin agent guide

Folio is a model-independent presentation-engineering harness packaged as a Codex plugin. This repository is the canonical source for the plugin and its bundled resources.

## Project map

- `.codex-plugin/plugin.json` defines the plugin package.
- `skills/folio/SKILL.md` is the agent-facing contract. Read the relevant references before changing mode selection, reconstruction, design-system resolution or acceptance behaviour.
- `design-systems/` contains registered systems, including Lumen; follow each `system.json` for its declared resources.
- `components/`, `catalogue/` and `examples/` contain the shared semantics, discovery material and reviewed examples.
- `docs/` records plugin decisions and implementation evidence.
- `scripts/validate_plugin.py` checks packaging and resource consistency.

## Working rules

- Preserve the Quick, Guided and Governed boundaries documented by the Skill. Do not apply Lumen or invent formal governance to Quick or Guided work.
- For governed changes, use supplied or named design-system resources before Lumen, and never claim compliance with resources that are unavailable.
- Prefer canonical registered assets and editable/native representations; do not flatten reconstructable presentation content into a full-slide image.
- Treat catalogues and generated presentation/preview files as derived artefacts. Do not add generated files to examples until reviewed.
- Keep documentation, manifests, registries, tokens, prompts and referenced paths in sync. Avoid unrelated changes.
- Keep project-work documents under `docs/` with names `<type>-<nnn>-<kebab-case-title>.md`, controlled type slugs, unique zero-padded numbers and required YAML front matter.
- Treat `docs/` as authoritative. Do not silently rewrite an approved or superseded ADR; create a successor and link it.
- Keep GitHub Actions pinned to immutable commit SHAs, preserve least-privilege permissions, and only adopt action releases at least seven days old.
- Use `.pinact.yaml` for action updates: run `pinact run --update --min-age 7`, then `pinact run --check --verify-min-age --verify-comment`. Do not hand-edit SHAs or bypass the age policy.
- Keep OpenGrep scans non-executing. Do not add `--allow-local-builds` to CI.

## Verification

From the repository root, run:

```bash
python3 scripts/validate_plugin.py .
pinact run --check --verify-min-age --verify-comment
```

For workflow changes, also run `actionlint`, `zizmor`, and the pinned OpenGrep scan.
