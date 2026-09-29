# Lumen Presentation Design System

Version: 0.1.0
Canvas: 16:9
Dimensions: 13.333 x 7.5 in

Lumen is a minimal, modern editorial presentation system built around strong typography, generous whitespace, restrained vector graphics and soft atmospheric depth.

## Principles

- One primary idea per slide.
- Prefer whitespace over containers.
- Prefer typography, alignment and spatial hierarchy over decoration.
- Use progressive disclosure for new composition or explicitly authorised redesign.
- Do not automatically shrink typography to conceal overflow. Select appropriate approved tokens during composition.
- Reuse approved components before creating new ones.
- Do not introduce unregistered fonts, colours, effects or component styles.

## Reference-constrained composition

Apply Lumen within the reference composition contract for Restyle. Preserve content, geometry, grouping, reading order, relative hierarchy, functional visuals and visible content per slide. Default archetypes, grid alignment and editorial whitespace preferences must fit that contract.

Fonts, palette, line treatment and the 11 pt minimum are treatment constraints. The declared canvas and safe areas are constraints too: if they conflict with the source, surface that conflict and obtain an explicit exception or permission to redesign. Do not quietly violate a mandatory rule or recompose to satisfy it.

Explanatory diagrams, convergence paths, component relationships and visual metaphors that organise the argument are functional content. Preserve their explanatory role and relative weight; simplify treatment only. An integrated architecture diagram can express one primary idea even when it contains many labels.

## Colour

### Core
- Background: `#FAFBFC`
- Background alternate: `#F5F7FA`
- Foreground: `#4B556D`
- Foreground strong: `#374151`
- Foreground muted: `#626D80`
- Foreground faint: `#656F81`
- Functional border: `#818B9B`

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

Keep meaningful text at 4.5:1 against its actual background, or 3:1 for large text. Muted and faint text tokens meet the normal-text threshold on the default and alternate backgrounds; do not lower their opacity. Light accent and wash tokens are for fills or decoration, not text on a light canvas. Keep essential shape boundaries and connectors at 3:1 against every adjacent fill. A pale panel fill alone does not establish a distinguishable box. Check final rendered colours when transparency, imagery or atmosphere changes the background.

## Typography

Primary font: Inter. Fallback: Aptos, then Arial.

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

Choose a typography token that fits the reference's visual role and allocated region. A slide title need not use h1, and a component heading need not use h3. Check the title-to-primary-visual relationship with realistic text measurements. Selecting an appropriate approved token is expected; automatic font shrinking after overflow is not.

Use 600 or 700 for emphasis. Use italics only for editorial subheads or questions. Do not use heading all-caps. Do not use text below 11 pt.

## Layout

Safe area: left/right 0.75 in; top 0.55 in; bottom 0.50 in. Use a 12-column grid with a 0.20 in gutter. Spacing scale: 0.10, 0.20, 0.30, 0.40, 0.60, 0.80, 1.20 in.

Prefer asymmetrical editorial composition. Normal density ceiling: one headline, one supporting statement, one primary visual and roughly three supporting concepts. For new composition or Redesign with explicit splitting permission, split material when needed for comprehension. For Convert or Restyle, preserve source slide structure; a density preference cannot move content to new slides or speaker notes. If approved typography cannot fit readably, surface the conflict.

## Icons and vectors

Use SVG for reusable graphics. Default icon stroke is 1.5 pt, dark foreground, with round caps and joins. Normal icon size is 0.35-0.60 in; hero icons 0.75-1.10 in. Do not mix icon families.

## Lines and connectors

Standard line: foreground, 1.25 pt. Process connector: foreground, 1.5 pt, simple arrowhead.

## Containers

Containers are exceptional. Prefer proximity and alignment. When required use transparent/background-alt fill, the `#818B9B` functional border at no less than 0.75 pt, visually equivalent 8 px radius, and no shadow by default. The border, not the slight difference between the two pale fills, defines a meaningful container.

## Background atmosphere

Background atmosphere is a compositional component, not decoration.

Layer order: 0 canvas; 10 atmosphere; 20 decorative geometry; 50 foreground visuals; 60 foreground text; 70 annotations.

Compose foreground first. Identify negative-space regions second. Only then select and place atmosphere.

Atmosphere must prefer edges/corners, occupy genuine negative space, counterbalance foreground composition, remain subordinate, permit slide-edge cropping and preserve clean whitespace. It must not fill the canvas uniformly, sit behind body copy merely for colour, overlap detailed primary visuals, reduce text contrast or create accidental containers.

Typical opacity: 8-24%. Typical blur: 80-160 px equivalent. Typical scale: 20-45% of slide width. Maximum three atmosphere fields per slide.

- `BG.ATMOSPHERE.*`: heavily defocused colour/depth fields.
- `BG.OBJECT.*`: recognisable soft 3D geometry used as a background object.

## Imagery

Prefer abstract dimensional forms, simple geometry, diffused lighting, soft materials and shallow depth of field. Avoid stock-photo aesthetics and decorative imagery unrelated to the narrative. Generated imagery is a reference artefact unless explicitly declared a final asset.

## Progressive builds

Maintain stable component positions across build slides. Do not redesign already introduced components. Reveal only what the current narrative stage requires. Keep previously introduced meaningful text and diagram boundaries at their required contrast; de-emphasise with hierarchy or position rather than opacity. Restore the complete composition on the final reveal.

## Prohibited patterns

Do not use generic card grids, coloured header strips, arbitrary gradients, excessive rounded rectangles, tiny text, decorative icons beside every bullet, random colours, inconsistent SVG styles, raster text, or flattened diagrams when native/vector construction is practical. When content does not fit, apply the operation-specific conflict and splitting rules above.
