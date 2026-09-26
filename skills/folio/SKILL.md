---
name: folio
description: Create editable PowerPoint presentations from reference images, briefs, diagrams, architecture, or reports using Folio. Use for quick image-to-slide reconstruction with native text/shapes/vectors, guided creation or reconstruction with lightweight visual preferences, or governed presentation generation using an installed or user-supplied design system with tokens, archetypes, component registries, and validation.
---

# Folio

Treat supplied or generated imagery as a visual specification, not the final presentation artefact.

## Confirm transformation intent

Before starting presentation generation, establish and play back the requested transformation. Presentation generation is a multi-step workflow, so do not begin expensive execution while the transformation intent is ambiguous.

For a supplied reference image, distinguish:

1. **Convert** — recreate the reference as an editable PowerPoint slide/deck while preserving its existing visual design. This maps to **Quick** mode.
2. **Redesign** — use the reference as content/composition evidence and recreate it using a formal design system. This maps to **Governed** mode.

If the request does not already make this distinction unambiguous, ask:

"How should I use this reference?
1. Convert it — preserve the existing design and recreate it as editable PowerPoint.
2. Redesign it — recreate the content using a design system."

Then play back the interpretation in plain language and obtain confirmation before generation. State the consequence rather than relying on internal mode names.

Examples:
- "I'll recreate this reference as editable PowerPoint while preserving its existing visual design. I won't apply a Folio design system."
- "I'll use the reference for its content and structure, then recreate it using a design system rather than reproducing the reference styling."

Even when the original request appears explicit, play back the interpreted transformation before execution so the user has an opportunity to correct it. Do not start generation until the transformation is confirmed.

An explicit request to use a named, selected or supplied design system is **Governed** mode. In a plugin installation, load `../../design-systems/registry.json` when it is available and treat each registered system name or ID as an explicit Governed request. A standalone Skill installation may not include that plugin-level registry; do not make registry lookup a prerequisite for classifying or using a user-supplied system.

If the user chooses **Redesign** without already naming or supplying a design system, do not select one on their behalf. Read `references/design-system-resolution.md`, present installed Folio options from the canonical registry when it is available, and offer the option to provide a repository link containing an alternative design system. If the registry is absent in a standalone Skill installation, explain that the installed-system inventory is unavailable and offer the supplied-system option. Obtain their selection before composing.

Guided mode remains available when the user explicitly asks for lightweight adaptation such as "clean this up", "modernise this", "use these colours/fonts", or similar preferences without a formal design system. Play back that interpretation and confirm it before execution.

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

Resolve the active design authority only after the user's selection is explicit:

1. User-supplied organisational design-system or brand/design resources, whether complete or partial.
2. A user-selected design system installed in the Folio plugin.

If Governed mode or Redesign is requested without a selected system, present the registered Folio options plus the option to supply an alternative repository/link, then wait for the user's choice. Do not default to Lumen.

For a user-supplied system, inspect and use the supplied rules, tokens, templates, assets, components and examples as the active design authority. Do not substitute Lumen rules or assets into that system unless the user explicitly requests a hybrid.

For installed Folio systems, use `../../design-systems/registry.json` when it is present in the plugin installation. Treat it as the canonical inventory for discovery, listing and ID/name resolution. If the user asks which installed systems are available and the registry is absent, explain that the standalone Skill bundle does not include the plugin's inventory; do not infer available systems from directories. After selecting a registered system, follow its `manifest` path and load that `system.json` first. Without the registry, continue with user-supplied design-system resources and do not attempt plugin-relative system discovery.

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
