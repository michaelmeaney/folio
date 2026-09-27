# Design-system resolution

Use this reference only in Governed mode.

## Source precedence

When Governed mode is selected, the user must choose the active design system before composition begins. Do not silently select Lumen or any other system.

When `../../design-systems/registry.json` is available in a plugin installation, offer:
1. the installed Folio systems listed in that registry; or
2. an alternative design system supplied by the user, including a repository link containing the design-system resources.

In a standalone Skill installation, the plugin registry may be absent. In that case, offer the user-supplied system option without attempting plugin-level discovery. A request that explicitly names or supplies an external design system remains Governed and does not depend on the installed-system registry.

Present installed options using their registry names and summaries. If the user asks which installed systems are available while the registry is absent, explain that the standalone Skill bundle does not include the plugin inventory and ask them to provide a design-system repository/resources if they want to use one. If the user provides a repository link, inspect the design-system resources available there and establish the authority map before generation.

Never silently replace a supplied or selected system with another system.

## User-supplied systems

A user-supplied system may arrive as design-token files, brand/design documentation, a template deck, component/vector assets, example slides, or a combination of these.

Inspect the supplied material and establish an authority map for the rules it actually defines, for example:

- canvas/aspect ratio;
- typography;
- colour;
- spacing/grid/layout;
- shape, line and icon language;
- imagery;
- components/assets;
- slide archetypes or templates;
- layering/background rules;
- component lifecycle or approval status;
- accessibility or validation requirements.

Use supplied canonical assets directly when available. Do not replace them with Folio/Lumen equivalents solely because Folio has a corresponding component.

If a category is absent, do not invent an organisational rule for it. Use a neutral implementation choice only when it does not create a false governance claim.

## Installed Folio systems

When present in a plugin installation, load `../../design-systems/registry.json` before resolving an installed system. This is the canonical inventory of bundled Folio systems. The standalone Skill bundle may not include it; absent registry means installed Folio systems cannot be listed or resolved from that bundle.

- Use the registry when available and the user asks which systems are installed or asks to choose among bundled systems.
- Resolve names and IDs only from registered entries; do not infer availability from directories.
- The registry's `default` entry is metadata only; do not use it to bypass explicit user selection.
- After selection, follow the registered `manifest` path and load that system's `system.json`.
- A design-system directory that is not registered is not considered installed/discoverable.

Treat the selected system manifest as authoritative for all further resource discovery.

Resolve each manifest-declared path relative to the system directory unless the manifest explicitly points elsewhere. Load only resource categories present in the manifest. Do not assume another system uses Lumen's filenames, directories, or optional categories.

Typical manifest fields may identify:
- design guidance;
- tokens;
- archetypes;
- component registry;
- shared component registry;
- catalogue;
- visual-generation and reconstruction prompts.

A missing optional field is not itself an error. A field that is present but points to an unavailable resource is a missing governed resource and should be handled under the incomplete-system rules.

The bundled registry currently exposes Lumen, Aperture, Meridian, Mosaic, Gridline and Werk. Lumen's manifest additionally resolves archetypes, component registries, catalogue and generation/reconstruction prompts; other systems may intentionally declare fewer optional resource categories.

## Incomplete systems

A system is incomplete only when missing information prevents the requested governed result.

- Ask for missing resources when the missing rule is material to the requested output.
- Continue with the supplied rules when the missing category is not material, and state the validation boundary.
- Offer Guided mode as an explicit fallback when full governance cannot be established.
- Never claim full design-system compliance for rules or assets that were unavailable.
