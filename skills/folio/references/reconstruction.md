# Reconstruction rules

## Priority order

1. Preserve semantic hierarchy.
2. Preserve composition and relative geometry when a reference exists.
3. Apply the selected mode's design authority.
4. Preserve editability.
5. Match decorative detail.

Design authority by mode:

- Quick: the supplied reference.
- Guided with a reference: the supplied reference plus explicit user preferences.
- Guided without a reference: the user's brief/content plus explicit visual preferences and the resulting local style contract.
- Governed: the resolved active design system, whether user-supplied or installed.

## Object mapping

- Text: native PowerPoint text.
- Simple boxes, circles, lines, dividers and containers: native PowerPoint shapes.
- Flows: editable connectors or lines where practical.
- Reusable illustrations and icons: SVG/vector assets.
- In Governed mode, use canonical registered assets when the active system supplies them.
- Photographic or intrinsically raster content: raster image, cropped rather than stretched.
- Generated or supplied slide references: never use as the complete slide background when the functional content can be reconstructed.

## Layering

Reconstruct functional foreground content before decorative layers in every mode.

- Quick: infer layering from the reference.
- Guided with a reference: infer layering from the reference, modified only by explicit preferences.
- Guided without a reference: derive layering from content semantics and the local style contract.
- Governed: follow the active design system's layer rules. For Lumen, functional foreground content owns the slide and background atmosphere is placed only after a whitespace map exists.

## Fidelity

Prefer geometry corrections over raster substitution. If exact visual fidelity conflicts with editability, preserve semantic structure and editability unless the user explicitly requests a flattened visual deliverable.

Do not introduce design-system constraints in Quick or Guided mode merely because Folio has governed resources available. Do not import Lumen constraints into a different supplied Governed design system unless requested.
