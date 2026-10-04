---
name: folio
description: Create editable PowerPoint presentations from reference images, briefs, diagrams, architecture, or reports using Folio. Use for quick image-to-slide reconstruction with native text/shapes/vectors, guided creation or reconstruction with lightweight visual preferences, or governed presentation generation using an installed or user-supplied design system with tokens, archetypes, component registries, and validation.
---

# Folio

Treat supplied or generated imagery as a visual specification, not the final presentation artefact.

## Confirm transformation intent

Establish transformation intent separately from the capability mode. For a supplied reference:

| Intent | Changes | Protected by default |
| --- | --- | --- |
| Convert | Representation becomes editable | Content, composition and visual treatment |
| Restyle | Fonts, palette, strokes, surfaces and illustration treatment | Content, relationships, composition, relative hierarchy and slide structure |
| Redesign | Explicitly authorised composition or story structure | Meaning, facts and any protected relationships or regions |

Naming a design system authorises a change in visual treatment, not a change in composition. Default reference work with requested styling to Restyle. Recomposition, simplification, copy rewriting, consolidation, replacing a primary visual or splitting slides each needs explicit scope. A request for Redesign does not automatically authorise every structural change.

Select the capability mode independently:

- Convert without styling or governance: **Quick**.
- Lightweight preferences or an ungoverned brief: **Guided**, including Restyle or explicitly scoped Redesign.
- A named, selected or supplied formal design system: **Governed**, normally Restyle for references. Governed Convert is possible only if the source treatment already satisfies the system; surface conflicts.
- A brief without a reference: new composition in Guided or Governed mode; do not invent a preservation baseline.

Play back intent, selected system or local preferences, preservation scope and slide count together, and obtain confirmation before generation. Existing explicit confirmation remains valid; do not ask the user to select a system already named or supplied. Ask about genuine ambiguity or conflicts together in one concise question.

For example: "I'll preserve this reference's composition, relationships and one-slide structure, rebuild it as editable PowerPoint, and apply Lumen's visual treatment."

When Governed mode is requested without a selected system, read `references/design-system-resolution.md`, offer registered systems or user-supplied resources, and obtain a selection. Do not infer Governed mode merely from the word Redesign or choose a system on the user's behalf. A standalone Skill can use supplied resources even when the plugin registry is absent.

Read `references/modes.md` for mode boundaries and `references/composition-contract.md` for authority, preservation and conflict rules.

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

If Governed mode is requested without a selected system, present the registered Folio options plus the option to supply an alternative repository/link, then wait for the user's choice. Do not default to Lumen.

For a user-supplied system, inspect and use the supplied rules, tokens, templates, assets, components and examples as the visual-treatment authority within the confirmed transformation. Do not substitute Lumen rules or assets into that system unless the user explicitly requests a hybrid.

For installed Folio systems, use `../../design-systems/registry.json` when it is present in the plugin installation. Treat it as the canonical inventory for discovery, listing and ID/name resolution. If the user asks which installed systems are available and the registry is absent, explain that the standalone Skill bundle does not include the plugin's inventory; do not infer available systems from directories. After selecting a registered system, follow its `manifest` path and load that `system.json` first. Without the registry, continue with user-supplied design-system resources and do not attempt plugin-relative system discovery.

Treat that manifest as authoritative for all further resource discovery. Resolve only paths and resource categories declared by the manifest, relative to the system directory unless the manifest explicitly points elsewhere. Do not assume Lumen filenames, directories, or optional resources for another system.

When the selected manifest declares `schemaVersion: 0.1.0`, use `resources.tokens` as its canonical DTCG token source and `resources.presentation` for presentation rules. Top-level `tokens` is a compatibility path for older consumers, not a second token source. Resolve references and report invalid or missing values before claiming governed compliance.

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

1. Establish the message and information architecture; for reference work, freeze the source composition contract before building output.
2. Reuse approved components before inventing new primitives when the active system defines component governance.
3. Compose foreground content first, then whitespace, then background atmosphere where the active system requires it.
4. Use image generation only for visual exploration or missing decorative/reference assets.
5. Reconstruct using native editable text, shapes, connectors and canonical SVGs where the active system supplies them.
6. Validate all four acceptance gates, including composition preservation as well as the active design system's rules and available resources.
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

For reference work, establish the composition contract before choosing an archetype; an archetype must fit protected geometry. Functional diagrams and explanatory illustrations retain their visual weight. Surface mandatory system conflicts instead of silently splitting or recomposing.

For execution details, read `references/workflow.md` and `references/reconstruction.md`. For completion criteria, read `references/acceptance.md`.

## Benchmark execution

For a requested plugin benchmark or version comparison, read `references/benchmark.md`. Dispatch each generation trial and each independent review into a fresh context. Keep coordination in the parent; provide only the fixed task inputs to each worker. This applies to benchmark runs, not every ordinary presentation request.
