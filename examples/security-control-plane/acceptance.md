# Security Control Plane acceptance fixture

This is Folio's first end-to-end reconstruction fixture.

## Input

The test input is the reviewed Security Control Plane visual reference. Add it as `visual-reference.png` when the canonical source image is ready for the repository.

The reference contains a complete security architecture with:

- policy information points on the left;
- invariants, PAP and PDP through the centre;
- assertions and decisions crossing the policy plane;
- hot-path and cold-path enforcement flows;
- tools and integrations on the right;
- protected resources across the bottom.

## Expected output

Generate `final.pptx` and `final.png`.

The PowerPoint must preserve the reference composition while reconstructing:

- all meaningful text as native PowerPoint text;
- simple panels and containers as native shapes;
- arrows and flows as editable lines/connectors where practical;
- reusable icons and illustrations as canonical SVG components;
- background atmosphere independently from functional foreground content.

## Acceptance

Apply the Folio acceptance criteria in `skills/folio/references/acceptance.md`.

This fixture additionally requires:

- the complete Security Control Plane to remain legible at 16:9 presentation size;
- the hot path and cold path to remain visually distinct;
- policy inputs and decisions to preserve their directionality;
- the full architecture to remain editable without requiring the source reference image as a slide background.
