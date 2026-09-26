# Reconstruction Instructions

Convert an accepted visual reference into an editable PowerPoint slide without flattening the design.

## Priority order

1. Preserve semantic hierarchy.
2. Preserve composition and relative geometry.
3. Use exact design tokens.
4. Reuse approved components.
5. Preserve editability.
6. Match decorative detail.

## Reconstruction rules

- Recreate all text as native PowerPoint text.
- Recreate simple geometry as native PowerPoint shapes.
- Recreate flows as editable lines/connectors where practical.
- Use canonical SVG assets for registered components.
- Do not trace an approved component from pixels when its canonical SVG exists.
- Group logical component assemblies.
- Maintain stable component IDs in generation metadata where possible.
- Preserve the defined layer order.
- Send all BG.ATMOSPHERE and BG.OBJECT assets behind foreground content.
- Validate that background components do not overlap functional whitespace, text or detailed primary visuals.
- Do not rasterise the complete slide.

If the reference contains a novel reusable visual, reconstruct it as a candidate SVG and register it as candidate rather than silently treating it as approved.
