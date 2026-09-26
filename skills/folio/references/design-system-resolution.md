# Design-system resolution

Use this reference only in Governed mode.

## Source precedence

Resolve the active design system in this order:

1. User-supplied organisational design-system resources in the current task.
2. A user-named design system installed with Folio.
3. Lumen when the user asks for governed Folio output but does not name or supply another system.

Never silently replace a supplied or named system with Lumen.

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

For an installed system, load `../../design-systems/<system>/system.json` first. Treat that manifest as authoritative for all further resource discovery.

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

For Lumen, the current manifest resolves `DESIGN.md`, `tokens.json`, archetypes, component registries, catalogue and generation/reconstruction prompts.

## Incomplete systems

A system is incomplete only when missing information prevents the requested governed result.

- Ask for missing resources when the missing rule is material to the requested output.
- Continue with the supplied rules when the missing category is not material, and state the validation boundary.
- Offer Guided mode as an explicit fallback when full governance cannot be established.
- Never claim full design-system compliance for rules or assets that were unavailable.
