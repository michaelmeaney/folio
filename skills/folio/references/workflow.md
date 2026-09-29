# Folio workflow

## Intent confirmation

Before choosing the execution path, play back Folio's interpretation of the requested transformation and obtain user confirmation.

Choose Convert, Restyle or explicitly scoped Redesign independently of Quick, Guided or Governed. Confirm the intent, system/preferences, preservation scope and slide count together. Reuse an already selected system and already confirmed scope. Do not load governed resources in Quick or Guided mode.

## Reference-image path

1. Inspect the actual source before creating any output. Record its hash, dimensions and slide count.
2. Create the composition contract described in `composition-contract.md`: regions and normalised geometry, grouping, whitespace, hierarchy, reading order, text, relationships, ambiguities and permissions. Freeze and hash this baseline before output generation.
3. Resolve the selected mode's treatment resources and distinguish mandatory constraints from layout preferences. Surface conflicts with the baseline.
4. Draft text-aware geometry inside the protected regions. Use realistic text measurements and representative visuals, including the dominant explanatory graphic. Choose an archetype only if it fits the contract.
5. Classify elements into native text, shapes, lines/connectors, editable vector geometry, reusable SVG, intrinsic raster and decoration. Record the editing operations actually supported.
6. Apply the requested treatment, reconstruct functional foreground first, and trace every source region and relationship to output objects. Preserve slide allocation and visible content unless explicitly authorised otherwise.
7. Compare the source and final render at whole-slide and detail scale. Record material differences and their permission references, then repair affected objects and dependent connectors.
8. Evaluate the four acceptance gates. Unperformed mandatory render or editing checks are unverified; return partial output rather than accepted output.

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
