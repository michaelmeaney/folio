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

## All modes

- The presentation opens as a normal editable PowerPoint file.
- All meaningful text is editable text, not rasterised text.
- Simple diagrams and containers are native shapes where practical.
- Flows remain editable rather than being embedded in a full-slide image.
- No text is clipped, overflowing, or unintentionally overlapping other content.
- Raster imagery is used only where raster content is appropriate.
- A rendered preview has been inspected for visual fidelity and obvious layout defects.
- If a reference image is supplied, major composition, hierarchy, proportions, and visual rhythm are recognisably faithful to it except for specific authorised deviations recorded in the composition contract. A Redesign request is not a blanket waiver.

## Quick mode

Additionally verify that:
- the supplied reference remains the design authority;
- no formal design-system compliance is claimed;
- vectors are reconstructed where practical without requiring component-registry metadata.

## Guided mode

Additionally verify that:
- explicit user preferences are applied consistently;
- unstated styling has not been elevated into invented governance rules;
- with a reference, the reference remains recognisable unless the user requested a redesign;
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
