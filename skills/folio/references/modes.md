# Folio capability modes

Folio exposes progressive capability rather than requiring a design system for every task.

## Quick

Use when the user wants a supplied image, screenshot, sketch, or visual reference converted into an editable PowerPoint slide or deck.

Design authority: the supplied reference.

Required behaviour:
- infer canvas ratio from the source;
- recreate meaningful text as editable text;
- recreate simple geometry as native PowerPoint shapes;
- recreate flows as editable lines/connectors where practical;
- recreate suitable illustrations/icons as SVG/vector assets;
- retain intrinsically raster content as raster;
- render and compare against the source.

Do not:
- require a Folio design system;
- apply Lumen automatically;
- replace source styling with Folio styling;
- introduce component governance unless requested.

## Guided

Use when the user wants reference reconstruction or deck creation plus lightweight styling preferences without a formal design system.

Design authority:
- with a reference: the reference plus explicit user preferences;
- without a reference: the user's brief/content plus explicit visual preferences.

Examples:
- "Match this slide but use our navy and teal."
- "Use this reference, Inter, and our logo."
- "Keep the layout but make it cleaner and less dense."
- "Create a deck from this outline using Inter, navy and teal, with sparse editorial layouts."

For reference-free Guided work, derive a local style contract directly from the supplied preferences. Use content-driven composition and neutral host defaults only for unspecified low-level details. Do not require a reference and do not invent a formal token system, component registry or reusable governance layer.

## Governed

Use when the user explicitly requests a Folio design system, names Lumen, supplies an organisational design system, or asks for governed/reusable/brand-controlled output.

Design authority: the active design system, whether supplied by the user or installed with Folio. Supplied references act as composition/content evidence unless the active system says otherwise.

Resolve design-system sources in this order:
1. user-supplied organisational design-system resources, whether complete or partial;
2. a user-named design system installed with Folio;
3. Lumen when governance is requested but no other system is named or supplied.

Do not replace a supplied or named design system with Lumen silently.

Load and enforce the rules that exist for the active system, which may include:
- design rules;
- exact tokens;
- archetypes;
- shared and system-specific component registries;
- approved component catalogue;
- generation/reconstruction prompts;
- design-system acceptance criteria.

When the active system defines component lifecycle rules, novel reusable visuals enter that lifecycle rather than silently becoming approved components.

If supplied resources are incomplete, identify what is missing. Ask only when the missing information prevents reliable governed output. Otherwise enforce and validate the supplied rules without inventing absent ones.

## Mode escalation

A task can move upward during the conversation:
- Quick -> Guided when the user adds lightweight visual preferences.
- Guided -> Governed when the user chooses or supplies a formal design system.

Do not silently move a task downward if the user has requested governance.
