# Folio acceptance criteria

A reconstructed or generated deck is complete only when all criteria for the selected mode pass.

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
- If a reference image is supplied, major composition, hierarchy, proportions, and visual rhythm are recognisably faithful to it unless redesign was explicitly requested.

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
