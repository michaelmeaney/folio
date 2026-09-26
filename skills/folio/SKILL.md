---
name: folio
description: Create editable PowerPoint presentations from reference images, briefs, diagrams, architecture, or reports using Folio. Use for quick image-to-slide reconstruction with native text/shapes/vectors, guided creation or reconstruction with lightweight visual preferences, or governed presentation generation using an installed or user-supplied design system with tokens, archetypes, component registries, and validation.
---

# Folio

Treat supplied or generated imagery as a visual specification, not the final presentation artefact.

## Select a capability mode

Determine the mode before doing presentation work.

If the user's request clearly implies a mode, use it without asking. Otherwise ask one concise question:

"Which Folio mode do you want?
1. Quick — recreate the reference as an editable slide/deck; no design system.
2. Guided — create or reconstruct with lightweight visual preferences; no formal design system.
3. Governed — apply an installed or supplied design system, including its tokens, archetypes/components where available, and validation."

Infer modes as follows:

- "Recreate this image", "make this editable", "turn this into a slide" with no styling/governance request -> **Quick**.
- "Clean this up", "modernise this", "make a consistent deck from these references", or "create a deck using these colours/fonts" without formal governance -> **Guided**.
- Any explicit design-system, brand-system, token, Lumen, component-library, governance, or reusable-archetype request -> **Governed**.

Do not force design-system setup on Quick or Guided work.

Read `references/modes.md` for the exact capability contract.

## Quick mode

Use the supplied reference as the design authority.

1. Determine canvas ratio and visible composition.
2. Decompose the reference into native text, native geometry, editable connectors, vector candidates, raster-only imagery and background effects.
3. Reconstruct the slide or deck with editable primitives.
4. Preserve the reference's hierarchy, proportions, layout and visual rhythm.
5. Render and compare the result with the reference.
6. Fix geometry rather than flattening editable content to improve fidelity.

Do not load design-system tokens, archetypes or component registries unless the user explicitly asks for them.

## Guided mode

Use lightweight user preferences without requiring a formal Folio design system.

When a reference is supplied:

1. Follow the Quick reconstruction workflow.
2. Establish a local style contract from the reference plus the user's explicit preferences.
3. Apply requested cleanup or adaptation consistently across slides.
4. Reuse recurring reconstructed vectors within the deck.
5. Validate consistency and fidelity.

When no reference is supplied:

1. Model the message and information architecture from the user's brief/content.
2. Establish a local style contract directly from the user's stated preferences, such as typography, palette, logo, density, tone, shape language or layout direction.
3. Use content-driven composition and neutral host defaults only for unspecified low-level details.
4. Keep those choices local to the deck; do not invent formal tokens, archetypes, registries or governance.
5. Validate consistency against the stated preferences and the deck's own local style contract.

Do not silently transform Guided work into Governed work.

## Governed mode

Resolve the design-system source before composing. Read `references/design-system-resolution.md`.

Use this precedence:

1. User-supplied organisational design-system or brand/design resources, whether complete or partial.
2. A user-named design system installed in the Folio plugin.
3. Lumen only when the user requests Folio governance without naming or supplying another system.

For a user-supplied system, inspect and use the supplied rules, tokens, templates, assets, components and examples as the active design authority. Do not substitute Lumen rules or assets into that system unless the user explicitly requests a hybrid.

For an installed Folio system, resolve the plugin root two levels above this skill directory and load `../../design-systems/<system>/system.json` first.

Treat that manifest as authoritative for all further resource discovery. Resolve only paths and resource categories declared by the manifest, relative to the system directory unless the manifest explicitly points elsewhere. Do not assume Lumen filenames, directories, or optional resources for another system.

When declared by the manifest, load resources such as:
- design guidance;
- tokens;
- archetypes;
- system-specific component registry;
- shared component registry;
- catalogue;
- visual-generation and reconstruction prompts.

If the manifest omits a category, treat it as absent/optional unless the requested governed output materially requires it. If the manifest references a resource that cannot be resolved, treat that as a missing governed resource and apply the incomplete-system rules below.

Then:

1. Establish the message and information architecture.
2. Reuse approved components before inventing new primitives when the active system defines component governance.
3. Compose foreground content first, then whitespace, then background atmosphere where the active system requires it.
4. Use image generation only for visual exploration or missing decorative/reference assets.
5. Reconstruct using native editable text, shapes, connectors and canonical SVGs where the active system supplies them.
6. Validate against the active design system's rules and available resources.
7. Apply candidate/approval lifecycle rules only when the active system defines them.

If a selected or supplied design system is incomplete, identify the missing material that blocks reliable governance. Ask for it when necessary; otherwise validate only the rules actually supplied. Offer Guided mode only as an explicit fallback. Never claim Governed compliance with resources that were not available.

## Common reconstruction rules

Across all modes:

- Produce an editable `.pptx`, not a slide-sized raster image.
- Prefer native PowerPoint text for meaningful text.
- Prefer native shapes for simple geometry.
- Prefer editable lines/connectors for flows.
- Use SVG for reusable vector graphics.
- Keep photographic or intrinsically raster material as raster imagery.
- Never use the complete reference image as the slide background when its functional content can be reconstructed.
- Prefer 16:9 unless the source reference or active design system specifies another ratio.
- Use the host environment's presentation-generation and render/QA tooling.
- Render a preview and inspect it before completion.

For execution details, read `references/workflow.md` and `references/reconstruction.md`. For completion criteria, read `references/acceptance.md`.
