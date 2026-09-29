# Reference composition contract

Establish this baseline from the source before building output. Never describe an output layout retrospectively as the source contract. In a standalone Skill, keep the same information in a local structured record; plugin JSON Schema tooling is optional for Quick and Guided work and does not introduce design-system governance.

## Authority and permissions

- Convert preserves content, composition and visual treatment.
- Restyle changes requested treatment while protecting meaning, relationships, grouping, reading order, dominant visual, relative region sizes, annotations, source slide count and visible content on each slide.
- Redesign changes explicitly authorised structure. It retains meaning, factual content and any expressly protected relationships or regions.
- For reference work, naming a system selects Governed Restyle by default. The system supplies treatment and mandatory constraints; default grids, archetypes and density preferences cannot authorise recomposition.
- A mandatory template, canvas or minimum readable type size may conflict with preservation. Describe the specific conflict and obtain a specific exception or structural permission. Do not silently sacrifice either side and claim fidelity or compliance.

Keep copy rewriting, slide splitting, consolidation, omission, replacing the primary visual and recomposition as separate permissions, each false by default. Record the user's authorisation and the scope of material deviations. A mode switch does not grant permissions.

## Baseline

Record source path/hash, source dimensions, source slide count and slide index; the baseline's own digest is locked into each scene. Record stable region IDs with normalised frames, per-region tolerances chosen before rendering, visible text, visual roles and confidence/ambiguity. Include the title footprint, primary visual, supporting visuals, important whitespace and grouping.

Record relationships separately from the object catalogue: endpoints, direction, labels and whether each relationship is technical, illustrative, annotation, containment, overlap or alignment. Never turn an illustrative association into a technical guarantee. Keep branching and convergence intact. Resolve material ambiguity before acceptance.

Record reading order and the primary region. The same explanation must remain visible on the same slide unless the user permits a change. Moving paragraphs into speaker notes or detail slides is a material deviation.

## Output trace and comparison

Map each material source region to one or more output objects, and every source relationship to its output relationship object. Preserve IDs through repairs. Account explicitly for omissions or consolidation with scoped authorisation; every functional output object must have a trace. Identify decoration separately.

Compare normalised output frames with the source's preselected tolerances. Compare visible text and relationships independently from geometry. Use actual rendered review for perceived hierarchy, graphic quality, text metrics and whitespace; bounding boxes alone cannot establish those qualities.

In schema 0.2.0, `visual-specification` holds the baseline, `scene.preservation` holds the trace, and `execution-result` records provenance, differences, gate evidence and host editing checks. Legacy 0.1.0 records remain readable but do not establish the new preservation or acceptance guarantees. See the plugin's `schemas/README.md` for migration and validation; a standalone Skill may not contain it.
