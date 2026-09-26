# Folio workflow

## Mode selection

Use the selected Folio capability mode before choosing the execution path.

- Quick: reference is the design authority.
- Guided: reference plus explicit preferences, or brief/content plus explicit preferences when no reference exists, are the design authority.
- Governed: the resolved active design system is the design authority.

Do not load governed resources in Quick or Guided mode.

## Reference-image path

When the user supplies a reference image, treat it as a composition proposal and visual specification.

1. Determine canvas ratio and safe-area behaviour.
2. Identify the narrative purpose of each visible region.
3. Extract the visual hierarchy: title, supporting copy, primary visual, secondary concepts, annotations, and atmosphere.
4. Classify every visible element as one of:
   - native text;
   - native PowerPoint geometry;
   - editable connector or line;
   - reusable SVG/vector component;
   - raster imagery that should remain raster;
   - background atmosphere.
5. In Quick mode, reconstruct directly from the reference.
6. In Guided mode, apply only the user-provided preferences while preserving source composition unless the user explicitly requests redesign.
7. In Governed mode, resolve the active design system first, then apply its available rules, components, archetypes and tokens.
8. Reconstruct the foreground before decorative layers.
9. Compare the rendered slide with the reference and iterate on geometry rather than flattening mismatched areas.

## Brief-to-deck path

When no reference image exists:

1. Model the message and information architecture.
2. In Guided mode:
   - build a local style contract directly from the user's explicit preferences;
   - compose slides from the content and that local contract;
   - use neutral host defaults for unspecified low-level details;
   - do not require a reference or invent formal governance.
3. In Governed mode:
   - resolve user-supplied or installed design-system resources;
   - select archetypes/prompts where the active system defines them;
   - apply the active system's available rules and assets.
4. Generate a visual reference only when visual exploration materially improves composition.
5. Treat any accepted generated reference as a specification and reconstruct it deterministically.

Quick mode normally requires a reference. If no reference or visual guidance exists, ask whether the user wants Guided or Governed mode rather than inventing a visual system.

## Component lifecycle

Apply a persistent component lifecycle only when the active Governed design system defines one.

For Lumen/Folio-governed components:

`need -> search registry -> candidate -> reconstruct/vectorise -> review -> approved -> reuse`

Never promote a candidate to approved without explicit review.
