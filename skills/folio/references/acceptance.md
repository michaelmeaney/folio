# Folio acceptance criteria

A reconstructed or generated deck is complete only when every applicable gate passes. Gates do not compensate for one another.

| Gate | Required evidence |
| --- | --- |
| Content and semantics | Source-to-output coverage, exact visible text unless rewriting is authorised, branch direction/labels and annotation associations |
| Composition and hierarchy | Source/final comparison at whole-slide and detail scale; protected geometry, grouping, reading order and primary visual weight |
| Design-system treatment | Registered tokens/components and mandatory constraints for Governed; local preferences or original treatment for Guided/Quick |
| Artefact and editability | Actual PowerPoint open/render check and claimed editing operations in a named application/version |

Record evidence references and a short list of material differences with authorisation for each. Check whether the same visual is dominant, the reading path remains intact, labels are proportionate and functional illustrations retain their role. Pixel similarity alone is unsuitable for Restyle.

Use the versioned execution-result contract when schema tooling is available. Every gate is pass, fail or unverified; accepted requires all four passes with evidence. A missing mandatory host check makes output partial, even when the package and semantic validators pass. Record source/baseline hashes, Folio commit, selected system revision (or none), renderer identity and target application. A gate record is evidence bookkeeping, not proof that a claimed review actually happened.

For attached connectors, inspect endpoint associations and test moving/resizing their components. An editable line is not an attached connector. A resizable SVG does not prove component geometry editing.

Connector attachment is not a universal requirement. Native editable text and independently movable major elements provide practical editability; disclose unattached lines and raster illustration crops. Apply exact topology checks to relationships carrying meaning, not incidental arrows inside illustrative artwork. The benchmark may report this practical milestone separately from full acceptance; it does not waive the accessibility or host evidence required for full acceptance.

## All modes

- The presentation opens as a normal editable PowerPoint file.
- All meaningful text is editable text, not rasterised text.
- Simple diagrams and containers are native shapes where practical.
- Flows remain editable rather than being embedded in a full-slide image.
- No text is clipped, overflowing, or unintentionally overlapping other content.
- Raster imagery is used only where raster content is appropriate.
- A rendered preview has been inspected for visual fidelity and obvious layout defects.
- Meaningful text remains legible: check its final colour, background, and opacity for at least 4.5:1 contrast, or 3:1 for large text. Do not rely on a token name as proof of contrast.
- Boundaries and connectors needed to understand a diagram remain distinguishable from adjacent colours at 3:1 or better; do not rely on a slight fill change alone to define a meaningful region.
- Meaning is not conveyed by colour alone. Check reading order and provide a text alternative for meaningful non-text content in the exported deck.
- If a reference image is supplied, major composition, hierarchy, proportions, and visual rhythm are recognisably faithful to it except for specific authorised deviations recorded in the composition contract. A Redesign request is not a blanket waiver.

If a source fails a required accessibility check, disclose the conflict with exact conversion and obtain permission for the necessary treatment change. Do not silently restyle Quick output or claim acceptance while the conflict remains unresolved.

## Quick mode

Additionally verify that:
- the supplied reference remains the design authority;
- no formal design-system compliance is claimed;
- vectors are reconstructed where practical without requiring component-registry metadata.

## Guided mode

Additionally verify that:
- explicit user preferences are applied consistently;
- unstated styling has not been elevated into invented governance rules;
- with a reference, the reference remains recognisable except for recorded, specifically authorised deviations;
- without a reference, the local style contract is derived from the user's brief/preferences and used consistently across the deck.

## Governed mode

Additionally verify that:
- the active design system was resolved from supplied or installed resources;
- validation covers the rules/resources that the active system actually provides;
- no Lumen defaults were silently substituted into another supplied/named system;
- canonical assets are used when the active system supplies them;
- component lifecycle rules are followed when the active system defines them;
- selected tokens/archetypes/layering rules are respected when the active system defines them;
- missing governance resources are disclosed rather than invented.
