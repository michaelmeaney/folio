# Folio Presentation Design System

Version: 0.1.0
Canvas: 16:9
Dimensions: 13.333 x 7.5 in

## Principles

- One primary idea per slide.
- Prefer whitespace over containers.
- Prefer typography, alignment and spatial hierarchy over decoration.
- Use progressive disclosure for complex concepts.
- Do not shrink typography to fit excess content.
- Reuse approved components before creating new ones.
- Do not introduce unregistered fonts, colours, effects or component styles.

## Colour

### Core
- Background: `#FAFBFC`
- Background alternate: `#F5F7FA`
- Foreground: `#4B556D`
- Foreground strong: `#374151`
- Foreground muted: `#8A93A5`
- Foreground faint: `#C5CAD4`

### Primary
- Primary: `#7657E8`
- Primary light: `#B8A7FF`
- Primary wash: `#EEEAFE`

### Secondary
- Secondary: `#35D39A`
- Secondary light: `#91EDCC`
- Secondary wash: `#E7FAF3`

### Supporting
- Blue: `#5B8DEF`
- Blue wash: `#EAF1FD`
- Pink: `#D76BD8`
- Pink wash: `#F8EAF8`
- Orange: `#F29A5B`
- Orange wash: `#FDF0E7`

### Semantic
- Success: `#35A978`
- Warning: `#E39A3B`
- Danger: `#D95C5C`

Use the background token by default. Use foreground for body text and foreground-strong for dominant headings. Do not invent intermediate colours. Use at most two chromatic accent families on a normal slide.

## Typography

Primary font: Inter.
Fallback: Aptos, then Arial.

| Token | Size | Line height | Weight |
| --- | ---: | ---: | ---: |
| display | 54 pt | 58 pt | 700 |
| h1 | 40 pt | 44 pt | 700 |
| h2 | 30 pt | 34 pt | 700 |
| h3 | 22 pt | 26 pt | 600 |
| body-lg | 20 pt | 28 pt | 400 |
| body | 17 pt | 24 pt | 400 |
| body-sm | 14 pt | 19 pt | 400 |
| caption | 11 pt | 15 pt | 400 |
| label | 12 pt | 16 pt | 600 |

Use 600 or 700 for emphasis. Use italics only for editorial subheads or questions. Do not use heading all-caps. Do not use text below 11 pt.

## Layout

Safe area:
- left/right: 0.75 in
- top: 0.55 in
- bottom: 0.50 in

Use a 12-column grid with a 0.20 in gutter.

Spacing scale: 0.10, 0.20, 0.30, 0.40, 0.60, 0.80, 1.20 in.

Prefer asymmetrical editorial composition. Typical layouts are large statement + visual, title + narrative, hero visual, sparse process, progressive build, and component catalogue.

Normal density ceiling: one headline, one supporting statement, one primary visual and roughly three supporting concepts. Split denser material across slides.

## Icons and vectors

Use SVG for reusable graphics. Default icon stroke is 1.5 pt, dark foreground, with round caps and joins. Normal icon size is 0.35-0.60 in; hero icons 0.75-1.10 in. Do not mix icon families.

## Lines and connectors

Standard line: foreground, 1.25 pt.
Process connector: foreground, 1.5 pt, simple arrowhead.

## Containers

Containers are exceptional. Prefer proximity and alignment.

When required:
- fill: transparent or background-alt;
- border: `#E1E5EB`, 0.75 pt;
- corner radius: visually equivalent to 8 px;
- no drop shadow by default.

## Background atmosphere

Background atmosphere is a compositional component, not decoration.

Required layer order:
- 0 canvas background
- 10 background atmosphere
- 20 background decorative geometry
- 50 foreground visuals and diagrams
- 60 foreground text
- 70 annotations and emphasis

Compose foreground content first. Then identify negative-space regions. Only then select and place background atmosphere.

Atmosphere must:
- prefer edges and corners;
- occupy genuine negative space;
- counterbalance foreground composition;
- remain subordinate to content;
- allow cropping beyond the slide boundary;
- preserve clean whitespace around text and diagrams.

Atmosphere must not:
- fill the canvas uniformly;
- sit behind body copy merely to add colour;
- overlap detailed primary visuals;
- reduce text contrast;
- create accidental containers.

Typical atmosphere opacity: 8-24%.
Typical visual blur: 80-160 px equivalent.
Typical scale: 20-45% of slide width.
Maximum: three atmosphere fields per slide.

Distinguish:
- `BG.ATMOSPHERE.*`: heavily defocused colour/depth fields.
- `BG.OBJECT.*`: recognisable soft 3D geometry used as a background object.

Both remain behind functional foreground content.

## Imagery

Prefer abstract dimensional forms, simple geometry, diffused lighting, soft materials and shallow depth of field. Avoid stock-photo aesthetics and decorative imagery unrelated to the narrative.

Generated imagery is a reference artefact unless explicitly declared a final asset.

## Progressive builds

Maintain stable component positions across build slides. Do not redesign already introduced components. Reveal only what the current narrative stage requires. Earlier content may reduce to 40-60% opacity when focus moves. Restore the complete composition on the final reveal.

## Prohibited patterns

Do not use generic card grids, coloured header strips, arbitrary gradients, excessive rounded rectangles, tiny text, decorative icons beside every bullet, random colours, inconsistent SVG styles, raster text, or flattened diagrams when native/vector construction is practical.

When content does not fit, create another slide.
