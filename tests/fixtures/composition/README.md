# Synthetic composition regression input

This original, synthetic pipeline fixture reproduces the failure mechanisms described in the composition review without publishing private material. `source.svg` shows three distinct inputs converging on a dominant architecture canvas and branching into two outputs. `specification.json` records the source baseline; `scene.json` demonstrates editable-object mappings within it.

`result.json` is deliberately partial: there is no renderer-produced PowerPoint, visual review or host editing evidence. This directory is a contract test fixture, not an approved presentation example. Negative cases are derived in memory by `test_composition_preservation.py`; no intentionally invalid output is published as valid.

The tests reject title expansion, primary visual shrinkage, collapsed routes, changed direction/labels/endpoints, missing visible text, unapproved slide moves, unsupported attached-connector claims, stale baselines and unsupported acceptance. Positive controls preserve authorised Redesign and one-to-many source-to-object mapping.

Use `docs/implementation/runbook-002-composition-regression.md` for actual render and target-application testing. The source dimensions are pixels; region frames/tolerances are fractions of the source canvas. Scene frames are pixels normalised against the output canvas by the validator.
