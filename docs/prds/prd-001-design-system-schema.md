---
title: "Folio Design System Schema"
subtitle: "Semantic presentation components, multimodal composition and editable artefacts"
type: prd
status: draft
number: "001"
date: "2026-09-28"
version: "0.3.0"
proposed_schema_version: "0.2.0"
updated: "2026-09-29"
owner: "Folio maintainers"
supersedes: null
superseded_by: null
related:
  - ../plans/plan-001-design-system-schema-foundation.md
  - ../implementation/implementation-002-design-system-schema.md
tags:
  - design-system
  - schema
  - tokens
---

# Folio Design System Schema

## Document status and revision notes

This is the updated product requirements document, not a declaration that every capability described below has been implemented. It preserves the original token / primitive / component / pattern / archetype model and extends it with the multimodal workflow discussed subsequently.

**Central proposition:** use visual generation to explore appearance, structured reasoning to recover and preserve meaning, reusable assets to avoid repeating solved work, and a controlled rendering pipeline to produce editable presentations.

### Composition preservation revision

Transformation intent is independent of governance mode. Convert preserves content, composition and treatment. Restyle applies selected treatment within the reference composition. Redesign permits only explicitly authorised structural changes. Naming a system selects Governed and defaults reference work to Restyle. Confirm intent, system/preferences, protected scope and slide count together; use a system already named or supplied.

For Restyle, the reference controls content, relationships and composition; the selected system controls treatment; the user authorises structural changes. Mandatory system conflicts require a specific exception or redesign permission. Default archetypes and density preferences cannot overwrite protected composition.

The 0.2.0 preservation contracts require source-derived regions and normalised geometry, hierarchy, typed relationships, ambiguity and permissions before generation. Scenes retain a digest of that baseline and map source regions and relationships to output objects. Accepted results require four independent evidence-backed gates: content, composition, treatment, and artefact/editability. Unknown or unperformed mandatory checks remain unverified and produce partial results.

See [ADR 001](../architecture/adr-001-composition-preserving-transformations.md), the [schema migration guide](../../schemas/README.md) and [implementation 003](../implementation/implementation-003-composition-preservation.md). The wire examples in later sections retain their illustrative 0.1.0 shape unless explicitly versioned; they do not establish the newer acceptance guarantees.

### Changes from v0.1

- Adds an optional **visual-specification stage**: a supplied or generated image can guide composition without becoming the final presentation or the authority for facts.
- Distinguishes a reusable **pattern**, an instantiated **composition**, and a resolved **scene** containing renderable geometry.
- Makes native text, native geometry, SVG and raster **purpose-specific representations**, rather than treating all vector content as equally editable.
- Adds model-role separation, artefact contracts, reference-driven reconstruction, bounded repair loops, failure records and evaluation requirements.
- Separates the open specification, reference implementation, conformance suite and reusable catalogue.
- Corrects the earlier standards examples: no invented DTCG schema URL; no `in` or `pt` inside DTCG dimension values; explicit unit conversion; and an explicitly experimental OpenUI adapter rather than an unsupported claim of universal compatibility.

The standards corrections are grounded in the references cited below. The proposed Folio contracts, thresholds and workflows are product design decisions. Performance benefits remain hypotheses until measured.

Examples describe the proposed wire format. Their file paths and package names are illustrative unless an implementation record links them to shipped contracts.

---

## 1. Summary

Folio requires a portable, machine-readable model for producing semantically meaningful, visually coherent and appropriately editable presentations.

The model must support a simple request such as "turn this image into an editable slide" without requiring the user to understand design-system infrastructure. The same underlying system must support organisational tokens, approved assets, reusable components, patterns, archetypes and validation policies when those capabilities are requested.

The principal abstractions remain:

```text
Design tokens -> Primitives -> Components -> Patterns -> Archetypes -> Slides -> Decks
```

This is an abstraction hierarchy, not a rigid execution sequence. Tokens can style every layer. A composition can be assembled directly, instantiated from a pattern, or reconstructed from a visual reference.

The execution architecture is:

```text
Brief / supplied reference / structured content
                    |
          Content and design authority
                    |
       +------------+----------------+
       |                             |
Reuse and compose             Explore visually
known structures              when useful
       |                             |
       |                 Accepted visual specification
       |                             |
       +---------- Semantic composition
                              |
                Resolve components and layout
                              |
                      Editable scene
                              |
                  Render -> Inspect -> Repair
                              |
                 Presentation + evidence report
```

**The generated image can be the visual specification. The editable presentation is the product.** The content specification and active design system remain authoritative where an image is ambiguous or contradictory.

## 2. Problem

A presentation pipeline that repeatedly generates raw geometry must rediscover familiar objects, layout relationships and editing behaviour. A pipeline that returns a single attractive image avoids some structural work but does not provide useful editing of its text, data or relationships.

The project discussion identified a progression from raster output, through extensive native reconstruction, towards a hybrid representation and reusable components. This is the architectural rationale for the proposal, not a controlled experiment proving one model or modality superior.

The problems to address are:

1. **Repeated work:** recreating common objects and arrangements rather than reusing reviewed implementations.
2. **Representation mismatch:** visually plausible output that loses editable text, data, anchors or component structure.
3. **Authority drift:** an attractive reconstruction silently changes source content or the selected design system.
4. **Unbounded execution:** additional reasoning or repair consumes resources without producing an acceptable artefact.
5. **Weak evidence:** a file parses successfully, but its content, appearance or editing behaviour is wrong.

Folio should raise the level at which an agent works, while retaining access to lower-level drawing when the task genuinely requires it.

## 3. Product Vision

Folio should provide an open semantic visual language and a working presentation-engineering implementation.

The catalogue analogy is **an icon and component library for presentations**, extending beyond individual icons to editable cards, diagram objects, connection points and reusable arrangements. Components provide vocabulary; patterns provide reusable structures for combining that vocabulary; archetypes organise the whole slide.

The adoption path is progressive:

| User need | Experience | Required knowledge |
| --- | --- | --- |
| Recreate a supplied slide image | Quick | The requested output and reference |
| Apply fonts, colours or selected resources | Guided | The preferences to apply |
| Use an existing organisational system | Governed | Which system is authoritative |
| Integrate presentation generation into tooling | Developer / platform | Contracts, adapters and validation profiles |
| Publish reusable components or implement another engine | Ecosystem | Specification and conformance requirements |

The sophisticated implementation must not make the first use case harder.

## 4. Design Principles

### 4.1 Standards before invention

Use DTCG for design tokens, SVG for applicable vector assets, JSON Schema for Folio contract validation, and existing presentation formats at the output boundary. Keep Folio-specific meaning in Folio contracts rather than inventing new token types or treating a backend API as the semantic model.

### 4.2 Semantics before geometry

Prefer `infrastructure.database` to an ad hoc cylinder when the component fits the requirement. Prefer a reviewed process pattern to repeated manual arrow placement. Do not force a catalogue match when it changes meaning or violates reference fidelity.

### 4.3 Appropriate representation, not maximum object count

Text should remain text. Relationships should remain identifiable relationships. Photographs need not become thousands of shapes. Complex vector artwork need not become a fragile collection of crude primitives merely to increase an editability score.

### 4.4 Semantic identity is independent of appearance

A database component retains its identity across design systems. Visual bindings may differ. A shared identity does not guarantee that any arbitrary icon can be restyled into every design language.

### 4.5 Composition over repeated generation

Retrieve and parameterise reviewed structures where appropriate. Use generation for novel material and candidate assets. Publication to a canonical catalogue requires review; repetition alone is not approval.

### 4.6 Visual feedback is part of the workflow

Inspect the rendered result, not just the source representation. Repairs must address identified failures and preserve already-correct content and geometry.

### 4.7 Models are replaceable capabilities

Do not depend on one provider, product name or undocumented model architecture. Planning, visual generation, reconstruction and critique may use different models or share one model where appropriate.

### 4.8 No unsupported success claims

Parsing is not visual acceptance. SVG is not automatically native editability. A model critique is not a conformance certificate. A proposed schema is not an adopted industry standard.

## 5. Conceptual Model

| Abstraction | Meaning | Example |
| --- | --- | --- |
| Token | Reusable visual decision | Colour, type style, spacing |
| Primitive | Basic rendering construct | Text, rectangle, connector |
| Component definition | Reusable semantic object contract | Database, customer, metric card |
| Component instance | A use of a component with content | A database labelled "Customer records" |
| Pattern | Reusable arrangement with roles and relationships | Control flow, timeline, hub-and-spoke |
| Composition | Instantiated component and relationship graph | This customer -> control -> application flow |
| Archetype | Whole-slide structure and content roles | Architecture with title and supporting narrative |
| Visual specification | Accepted visual target and constraints | Supplied screenshot or selected generated concept |
| Scene | Resolved renderable objects and geometry | Positioned text, native shapes and assets |
| Slide / deck | Presentation content and sequencing | A validated editable output |

Keep three artefacts distinct: **meaning** in the composition, **appearance guidance** in the visual specification, and **resolved geometry** in the scene. A raster image does not replace the semantic contract.

## 6. Layer 1 - Design Tokens

### 6.1 Standard and scope

DTCG 2025.10 is the canonical token format. It is a stable Community Group specification, not a W3C Recommendation. Adopt its typing, references and extensions rather than redefining them. [DTCG Format][dtcg-format]

Folio's initial rendering profile should cover colour, dimension, font family, font weight, number, typography, border, stroke style, shadow and gradient. Additional types may be preserved without being renderable; unsupported required features must fail explicitly.

A renderer support profile is not a claim of complete DTCG implementation.

### 6.2 Token example

The following is a compact illustrative token file, not the migrated Lumen palette. Colour objects follow the DTCG Color module. [DTCG Color][dtcg-color]

```json
{
  "color": {
    "surface": {
      "$type": "color",
      "$value": { "colorSpace": "srgb", "components": [1, 1, 1] }
    },
    "ink": {
      "$type": "color",
      "$value": { "colorSpace": "srgb", "components": [0.2, 0.2, 0.2] }
    },
    "text": {
      "$type": "color",
      "$value": "{color.ink}"
    }
  },
  "font": {
    "body": {
      "$type": "fontFamily",
      "$value": ["Inter", "Aptos", "Arial"]
    }
  },
  "spacing": {
    "slideEdge": {
      "$type": "dimension",
      "$value": { "value": 72, "unit": "px" }
    },
    "componentGap": {
      "$type": "dimension",
      "$value": { "value": 24, "unit": "px" }
    }
  },
  "typography": {
    "body": {
      "$type": "typography",
      "$value": {
        "fontFamily": "{font.body}",
        "fontSize": { "value": 24, "unit": "px" },
        "fontWeight": 400,
        "letterSpacing": { "value": 0, "unit": "px" },
        "lineHeight": 1.4
      }
    }
  }
}
```

### 6.3 Units, references and extensions

DTCG dimensions use `px` or `rem`, not `in` or `pt`; typography `lineHeight` is a multiplier. The earlier draft's physical-unit token example was invalid. Unknown extension data must survive token round trips. No authoritative JSON Schema URL is asserted here. [DTCG Format][dtcg-format]

Folio adopts an explicit presentation conversion policy: 96 logical pixels per inch and 72 points per inch, matching the CSS absolute-unit relationship. Thus 72 logical pixels map to 0.75 inches, and 24 logical pixels map to 18 points. `rem` requires a declared root font size. [CSS Units][css-units]

Conversion occurs at the rendering boundary, not through new DTCG types. Preserve source values and sufficient precision; do not silently round a migrated design system.

A proposed extension key is `io.github.michaelmeaney.folio`. Token-associated metadata belongs there; scene graphs and layout programmes do not.

DTCG aliases remain DTCG aliases. Folio files outside a token document use a separate typed reference, for example `{"token":"color.text"}`.

### 6.4 Multiple sources and modes

For MVP, merge declared token sources into one resolved context, rejecting duplicate leaf paths rather than silently choosing a winner. This assembly rule is a Folio policy, not a new DTCG merge specification.

Where contextual resolution is required, adopt the DTCG Resolver module through a version-pinned adapter. Do not claim theme support merely because several token files are present. [DTCG Resolver][dtcg-resolver]

## 7. Layer 2 - Primitives

Initial primitives are `shape`, `text`, `line`, `connector`, `image`, `vector` and `group`.

| Primitive | Required payload | Important behaviour |
| --- | --- | --- |
| Shape | Named geometry, frame and style | Native geometry where appropriate |
| Text | Content reference, frame and text style | Editable text; measured overflow |
| Line | Endpoints and stroke | No implied semantic connection |
| Connector | Source and destination instance/anchor references | Routing and attachment semantics |
| Image | Asset reference, frame and crop policy | Raster permitted by object role |
| Vector | Asset reference, frame and rendering profile | SVG support is capability-dependent |
| Group | Child objects and local coordinate frame | Stable child IDs and transforms |

Each primitive has an instance ID. Scene coordinates use logical pixels, top-left origin, positive x rightwards and positive y downwards. Group children use local coordinates. Rotation and transforms must be defined by the scene profile, never inferred from a screenshot's pixel density.

### 7.1 Shape example

```json
{
  "id": "control-container",
  "type": "shape",
  "geometry": "rounded-rectangle",
  "frame": { "x": 360, "y": 180, "width": 240, "height": 160 },
  "style": {
    "fill": { "token": "color.surface" },
    "stroke": { "token": "color.ink" }
  }
}
```

### 7.2 Boolean geometry

Do not require the union/subtraction history of an asset. A reviewed compound form can be a reusable component or vector asset. Retain parametric construction only where it provides useful editing behaviour.

### 7.3 Text and connectors

Text contracts must specify wrapping, alignment, overflow policy and a minimum acceptable size. Shrinking text is not an unrestricted escape hatch.

Connector endpoints reference component instances and named anchors. In the native PowerPoint profile, an attached connector must remain attached during the supported editing tests. A visually touching line is not equivalent to an attached connector.

Native charts and tables are specialised component/rendering bindings in the initial model. Their data must remain separate from appearance. They are not silently reduced to generic illustrations.

## 8. Layer 3 - Components

A component is a semantic contract with one or more approved implementations. It may consist of one primitive, a native group, an SVG, or a hybrid group containing native labels and a vector illustration.

Initial categories remain people, infrastructure, cloud, security, business, devices and flow. The catalogue is not security-specific; security examples exercise relationships and boundaries that generalise to other domains.

The component definition owns identity, properties, slots and semantic connection roles. A visual binding owns asset choice, geometry, token mappings and the editing capabilities it actually supports.

## 9. OpenUI Alignment

"OpenUI" here means the component-description draft at **openuispec.org**, currently labelled `draft-01`. It is distinct from the **W3C Open UI Community Group**, whose stated remit is web controls. Neither is adopted as Folio's presentation scene model. [OpenUI draft][openui-spec] [W3C Open UI][w3c-open-ui]

Folio will use an experimental adapter for the overlapping component-description layer: identity, descriptions, properties, enumerations, defaults and examples. The draft's `openui.json` format provides that projection. [OpenUI draft][openui-spec]

The adapter must pin a source revision, export fixtures and report losses. Anchors, slot constraints, renderer capabilities and presentation layout remain in Folio. Import must not invent them. An export must not be described as lossless unless its retained information is demonstrably sufficient for round-trip reconstruction.

Illustrative projection:

```json
{
  "name": "Folio Core Components",
  "version": "0.1.0",
  "description": "Semantic presentation objects",
  "components": {
    "Database": {
      "description": "A persistent data store",
      "props": {
        "label": {
          "type": "string",
          "description": "Visible label",
          "required": true
        },
        "variant": {
          "type": "string",
          "description": "Storage model",
          "enum": ["generic", "relational", "document", "object"],
          "default": "generic"
        }
      }
    }
  }
}
```

The canonical Folio property contract uses JSON Schema. Its export adapter, not the OpenUI draft, determines which Folio fields can be projected.

## 10. Initial Component Schema

All Folio definitions use a common envelope: `schemaVersion`, `kind`, `id`, `version`, `name` and `description`. Component `propertiesSchema` is a JSON Schema 2020-12 schema, not a bespoke `type: enum` language. [JSON Schema][json-schema]

```json
{
  "schemaVersion": "0.1.0",
  "kind": "component",
  "id": "infrastructure.database",
  "version": "0.1.0",
  "name": "Database",
  "description": "Represents a persistent data store",
  "tags": ["database", "datastore", "persistence"],
  "propertiesSchema": {
    "type": "object",
    "additionalProperties": false,
    "required": ["label"],
    "properties": {
      "label": { "type": "string", "minLength": 1, "maxLength": 120 },
      "variant": {
        "type": "string",
        "enum": ["generic", "relational", "document", "object"],
        "default": "generic"
      }
    }
  },
  "slots": {
    "label": {
      "accepts": ["text"],
      "minItems": 1,
      "maxItems": 1,
      "contentFrom": { "property": "label" }
    }
  },
  "anchors": {
    "input": { "role": "input" },
    "output": { "role": "output" }
  },
  "bindings": ["bindings/database.native.json", "bindings/database.svg.json"]
}
```

Schema validation must be followed by semantic validation. For example, `contentFrom.property` must exist, property defaults must satisfy their constraints, and each required anchor must be implemented by the selected binding.

Defaults are applied in an explicit normalisation stage; do not assume a JSON Schema validator inserts them.

## 11. Component Renderers

A renderer binding associates a semantic component with an implementation. Its contract declares the component version, design-system applicability, source asset or primitive scene, token bindings, anchor geometry and supported operations.

```json
{
  "schemaVersion": "0.1.0",
  "kind": "renderer-binding",
  "id": "core.database.native",
  "version": "0.1.0",
  "component": "infrastructure.database",
  "componentVersion": "0.1.0",
  "target": "powerpoint",
  "representation": "native-group",
  "source": "../scenes/database.scene.json",
  "anchors": {
    "input": { "x": 0, "y": 0.5 },
    "output": { "x": 1, "y": 0.5 }
  },
  "capabilities": {
    "editText": true,
    "editGeometry": true,
    "recolour": true,
    "resize": "uniform",
    "attachConnectors": true,
    "editData": false
  }
}
```

Capabilities are claims that require target-specific test evidence. A requested capability and a verified capability are separate values.

**Do not publish one universal `editable: true` flag.** A useful editing contract distinguishes editable text, shape geometry, colours, data, grouping, resizing and connector attachment.

An embedded SVG may remain a single graphic. Microsoft documents SVG editing and conversion features, but those features do not establish identical behaviour for every asset and target application. Test the actual output. [Microsoft SVG editing][microsoft-svg]

Selection order is constrained rather than absolute: preserve meaning and required edits first, then choose the approved representation with the best supported fidelity. Do not replace a strong vector asset with visibly inferior primitives simply to claim native output.

## 12. Component Variants

Variants describe meaningful differences such as generic versus relational storage, a warning state, or a person versus service identity. Pure colour changes normally belong in tokens. Design-system-specific appearance belongs in bindings.

Avoid multiplying semantic IDs into `database-blue`, `database-purple` and `database-lumen`. Conversely, do not hide a meaningful semantic difference behind an interchangeable colour variant.

A stateful presentation object may expose a `state` property, but the base schema does not introduce web event handling or interactive UI behaviour.

## 13. Component Slots

Slots define controlled composition points: title, subtitle, icon, value, status or nested content.

Each slot declares accepted content kinds and cardinality. Where a slot is sourced from a property, the same content must not be independently supplied through a competing binding. Resolve one canonical source.

A component may expose layout expectations for a slot through its visual binding. Content-length limits are input constraints, not substitutes for measuring rendered text.

## 14. Component Anchors

Semantic anchors identify useful attachment roles such as `input`, `output`, `telemetry` or `control`. A visual binding maps those roles to normalised local coordinates or a declared geometry operation.

The layout engine transforms anchors into scene coordinates. Changing a component's frame must update dependent routes. It must not require rediscovering connection locations from pixels.

An anchor alone does not determine what a connection means. Relationship type, direction and label belong in the composition. A security boundary line must not imply an enforcement guarantee absent from the source content.

## 15. Layer 4 - Patterns

A pattern is a reusable component arrangement with typed slots, relationships and layout constraints. It is not a screenshot or a rigid set of coordinates.

Examples include `process.linear`, `process.cycle`, `architecture.hub-spoke`, `architecture.layered`, `security.control-flow`, `comparison.before-after`, `business.metric-row` and `timeline.milestones`.

A pattern may be nested in another pattern, provided expansion is finite and acyclic. The pattern must document its intended use, inappropriate uses, tested content limits and supported alternative layouts.

## 16. Initial Pattern Schema

```json
{
  "schemaVersion": "0.1.0",
  "kind": "pattern",
  "id": "security.control-flow",
  "version": "0.1.0",
  "name": "Security Control Flow",
  "description": "A source reaches a destination through a control, with optional evidence output",
  "slots": {
    "source": { "accepts": ["component"], "minItems": 1, "maxItems": 1 },
    "control": { "accepts": ["component"], "minItems": 1, "maxItems": 1 },
    "destination": { "accepts": ["component"], "minItems": 1, "maxItems": 1 },
    "evidence": { "accepts": ["component"], "minItems": 0, "maxItems": 1 }
  },
  "relationships": [
    { "from": "source", "to": "control", "type": "flow", "direction": "forward" },
    { "from": "control", "to": "destination", "type": "flow", "direction": "forward" },
    {
      "from": "control", "to": "evidence", "type": "telemetry", "direction": "forward",
      "when": { "slotPresent": "evidence" }
    }
  ],
  "layout": {
    "strategy": "constraint",
    "constraints": [
      { "op": "row", "slots": ["source", "control", "destination"], "strength": "required" },
      { "op": "gap", "slots": ["source", "control", "destination"], "value": { "token": "spacing.componentGap" }, "strength": "preferred" },
      { "op": "below", "subject": "evidence", "reference": "control", "strength": "preferred", "when": { "slotPresent": "evidence" } }
    ]
  },
  "overflow": { "policy": ["reflow", "alternate-layout", "split-slide", "fail"] }
}
```

The condition language is deliberately declarative. MVP permits `slotPresent`; it must not execute JavaScript or arbitrary expressions from a package.

Initial layout operations are `row`, `column`, `align`, `gap`, `below`, `inside`, `non-overlap` and `preserve-frame`. Their exact semantics and deterministic tie-breaks must be documented before a conforming solver is released. Unknown required operations must fail.

## 17. Pattern Instantiation

A composition binds real component instances to pattern roles. Catalogue IDs and instance IDs are different: two applications on one slide may use the same component definition while retaining distinct instance identities.

```json
{
  "schemaVersion": "0.1.0",
  "kind": "composition",
  "id": "customer-authentication",
  "pattern": { "id": "security.control-flow", "version": "0.1.0" },
  "bindings": {
    "source": {
      "id": "customer",
      "component": "people.customer",
      "properties": { "label": "Customer" }
    },
    "control": {
      "id": "authentication",
      "component": "security.identity-provider",
      "properties": { "label": "Authentication" }
    },
    "destination": {
      "id": "application",
      "component": "architecture.application",
      "properties": { "label": "Application" }
    },
    "evidence": {
      "id": "audit",
      "component": "observability.telemetry",
      "properties": { "label": "Audit events" }
    }
  }
}
```

After expansion, the resolved composition records concrete relationship endpoints and component versions. The final scene retains links back to those instance IDs.

A direct composition without a pattern is valid. Reusable grammar is helpful, not mandatory for novel work.

## 18. Patterns as Presentation Grammar

The vocabulary / grammar analogy describes reuse, not a claim that the system understands every domain represented in a diagram.

A pattern must preserve the relationships supplied by the author. It cannot insert a control, reverse causality, or infer data ownership merely because the arrangement looks more balanced.

**Pattern** means reusable definition. **Composition** means a bound instance. **Scene** means resolved drawable objects. These names are normative within the proposed Folio vocabulary.

## 19. Layer 5 - Archetypes

An archetype defines whole-slide roles, hierarchy and spatial constraints. It can accept components, patterns or direct compositions.

Initial archetypes remain hero, section-divider, comparison, architecture, timeline, metric-story, dashboard, process, capability-map, quote and image-led, with phased implementation rather than a claim that all exist already.

Archetypes must distinguish hard requirements from stylistic preferences. A preferred visual-to-narrative proportion is not a reason to discard content. An unsatisfiable composition must produce a diagnostic or an explicitly permitted split.

## 20. Initial Archetype Schema

```json
{
  "schemaVersion": "0.1.0",
  "kind": "archetype",
  "id": "architecture",
  "version": "0.1.0",
  "name": "Architecture",
  "description": "A dominant technical composition with a title and optional narrative",
  "regions": {
    "title": { "role": "heading", "accepts": ["text"], "minItems": 1, "maxItems": 1 },
    "narrative": { "role": "supporting-text", "accepts": ["text"], "minItems": 0, "maxItems": 1 },
    "visual": { "role": "composition", "accepts": ["composition"], "minItems": 1, "maxItems": 1 }
  },
  "layout": {
    "visualPriority": "dominant",
    "preferredBodyFractions": { "visual": 0.72, "narrative": 0.28 },
    "respectSafeArea": true
  },
  "overflow": { "policy": ["reflow", "split-slide", "fail"] }
}
```

Fractions apply only to the body area and only when both regions are populated. Empty optional regions release their space. Archetype resolution must not introduce an implicit organisational design rule in Quick or Guided work.

## 21. Presentation Configuration

The presentation profile contains canvas geometry, the unit policy, grid topology, layer order, safe-area bindings and presentation behaviour. Reusable visual magnitudes may still be tokens; their use as layout rules belongs here.

```json
{
  "schemaVersion": "0.1.0",
  "kind": "presentation-profile",
  "id": "example.wide",
  "canvas": { "width": 1280, "height": 720, "unit": "px" },
  "units": { "pixelsPerInch": 96, "pointsPerInch": 72, "rootFontSizePx": 16 },
  "grid": { "columns": 12, "gutter": { "token": "spacing.componentGap" } },
  "safeArea": {
    "left": { "token": "spacing.slideEdge" },
    "right": { "token": "spacing.slideEdge" },
    "top": { "token": "spacing.slideEdge" },
    "bottom": { "token": "spacing.slideEdge" }
  },
  "layers": { "canvas": 0, "atmosphere": 10, "backgroundObject": 20, "visual": 50, "text": 60, "annotation": 70 },
  "atmosphere": { "placeAfterForeground": true, "respectExclusionZones": true },
  "textOverflow": { "allowTruncation": false, "allowUnapprovedRewrite": false }
}
```

This example is not a replacement for any existing system's exact measurements. Foreground composition establishes occupied and excluded areas before background atmosphere is placed.

Progressive builds must preserve stable instance IDs. Unchanged objects retain geometry unless the author explicitly approves reflow.

## 22. Design System Package

A design-system package supplies authority and visual bindings. Shared semantic definitions may live in independent catalogue packages.

```text
package/
  system.json
  presentation.json
  tokens/
    primitives.tokens.json
    semantic.tokens.json
    components.tokens.json
  components/
    registry.json
    bindings/
  patterns/
    registry.json
    definitions/
  archetypes/
    registry.json
    definitions/
  assets/
    svg/
    raster/
  prompts/
  catalogue/
  adapters/
    openui.json
  tests/
    fixtures/
```

The tree is a convention, not a required discovery algorithm. The manifest declares resources. A partial external design system can omit categories it does not govern; an explicitly declared but missing resource is an error.

Prompts and generated previews are not alternative sources of truth for token values or component contracts.

## 23. System Manifest

```json
{
  "schemaVersion": "0.1.0",
  "kind": "design-system",
  "id": "lumen",
  "name": "Lumen",
  "version": "0.2.0",
  "tokenFormat": { "name": "dtcg", "version": "2025.10" },
  "resources": {
    "design": "DESIGN.md",
    "tokens": ["tokens/primitives.tokens.json", "tokens/semantic.tokens.json", "tokens/components.tokens.json"],
    "presentation": "presentation.json",
    "components": "components/registry.json",
    "patterns": "patterns/registry.json",
    "archetypes": "archetypes/registry.json"
  },
  "dependencies": [
    { "package": "folio-core-components", "version": "0.1.0" }
  ],
  "adapters": {
    "openui": { "status": "experimental", "specification": "draft-01", "export": "adapters/openui.json" }
  }
}
```

Versions above are proposed examples, not published releases. Resolve relative paths against the package root. External dependencies must be explicitly identified, approved and locked by digest in the resolved package lock.

User selection determines the active system. Registry defaults are discovery metadata, not permission to silently select Lumen or replace another supplied system.

## 24. Shared Component Catalogue

The shared catalogue owns semantic definitions, not a compulsory aesthetic. Each approved design system can bind those definitions to its own assets and tokens.

Resolution order is explicit: selected system binding, then an approved shared binding, then a disclosed alternative. A missing governed binding must not silently fall back to another brand's artwork.

The catalogue should be useful without adopting the Folio agent. Independent consumers must be able to discover contracts, load assets and understand supported capabilities from documented files.

The visual catalogue is derived documentation: preview, semantic ID, variants, intended use, tested bounds and available representations. Its previews are not canonical component implementations.

## 25. Catalogue Namespaces

Use semantic identifiers such as `people.customer`, `infrastructure.database`, `security.trust-boundary`, `architecture.service`, `business.metric` and `observability.telemetry`.

Resolve identity using **package + definition ID + version**. An instance has a separate local ID. Reject ambiguous matches rather than accepting whichever package happens to load first.

Definition IDs are stable across implementation revisions. Renaming an ID requires an explicit alias or migration record. DTCG token naming rules are separate from Folio component ID rules.

## 26. Search and Agent Discovery

Each catalogue entry should expose name, description, tags, aliases, intended use, unsupported uses, variants, package version, review status and preview references.

Discovery should be progressive: search a small index, retrieve candidate contracts, then load only the selected implementations. Do not inject the entire catalogue into every prompt.

Search rank is not approval. Review metadata must be checked against the trusted catalogue state, not accepted merely because an untrusted package labels itself "approved".

Descriptions, examples and asset metadata are task data. They must not override the executing agent's instructions or authorise external actions.

## 27. Agent Behaviour

The agent should prefer an existing suitable pattern, then a composition of existing components, then primitives, then new artwork or geometry. Suitability includes semantics, design authority, editing requirements and the transformation requested.

For faithful conversion, the supplied reference may outrank a convenient pattern. For redesign, the chosen design system may legitimately change composition. These are different contracts, not different names for the same operation.

Before execution, establish the request, transformation, content authority, design authority, required editing operations and any material missing resources. Use an explicit request as the decision where it already resolves the choice; do not ask the user repeatedly.

Retrieve known assets. Generate genuinely missing ones. Record any substitution or approximation. Never repair a discrepancy by silently flattening the whole slide.

## 28. Promotion Lifecycle

Generated content is a candidate, not a catalogue entry.

```text
Ad hoc result -> Candidate -> Semantic review -> Representation review
             -> Editing tests -> Visual fixtures -> Approved release
```

Component promotion requires a stable purpose, clean inputs, documented slots and anchors, licence/provenance metadata, at least one tested representation and useful examples. Pattern promotion additionally requires tested content ranges, relationship semantics, layout alternatives and failure fixtures.

A repeated arrangement can suggest a pattern. The reviewer must still determine whether it generalises, duplicates an existing pattern, or simply reflects one slide's incidental geometry.

Retain rejected candidates and their reasons where appropriate. Do not let every generated object expand the supported public API.

## 29. Validation

Validation consists of independent gates:

| Gate | Checks | What passing does not prove |
| --- | --- | --- |
| Syntax | JSON parsing and schema shape | Correct references or appearance |
| Semantics | IDs, slots, types, aliases, graph expansion and constraints | Correct rendering |
| Package | Paths, dependency locks, integrity and resource availability | Trustworthiness of arbitrary code |
| Content | Required text, numbers, labels, relationships and source attribution | Visual quality |
| Design | Applicable tokens, approved assets and governed constraints | Full compliance with absent rules |
| Geometry | Bounds, overlaps, text measurements, anchors and routes | Aesthetically good composition |
| Representation | Text, data, geometry and connection editing requirements | Identical behaviour in every application |
| Visual | Hierarchy, fidelity, legibility and authorised differences | Semantic correctness by itself |
| Target application | Open/render/edit tests on declared targets | Untested cross-platform compatibility |

Each gate reports `pass`, `fail`, `not-run` or `not-applicable`, with evidence and scope. Required gates cannot be skipped while reporting overall acceptance.

A visual judge may identify a suspected defect. Hard content, schema and policy checks should be deterministic where feasible. A second model's opinion must not override a failed content-preservation rule.

## 30. Compatibility and Versioning

Version the PRD, Folio schema, catalogue entries, design systems and renderer implementations independently. This document is PRD `0.2.0`; the initial proposed wire contract remains `0.1.0`.

Use Semantic Versioning for released contracts and packages, with an explicit compatibility policy during pre-1.0 development. Do not infer compatibility from similar filenames. [Semantic Versioning][semver]

A resolved run records schema versions, package versions, asset digests, token context, font environment and renderer version. Unknown required features fail. Unknown optional namespaced metadata is preserved where the relevant contract requires it.

Breaking changes need migration fixtures and release notes. A native editing capability removed by a renderer update is a compatibility change even if the slide still looks the same.

## 31. Non-Goals

The first specification does not replace the entire PowerPoint object model, reproduce every SmartArt algorithm, define arbitrary interactive UI behaviour, mandate Boolean construction histories, or provide universal raster-to-vector conversion.

It does not claim a novel industry standard merely because it combines useful abstractions. It does not establish that no other tool has solved similar problems. Existing format standards remain relevant: OOXML defines presentation packaging and vocabularies, while Folio proposes a higher-level authoring and execution contract. [ECMA-376][ecma-376]

It also does not claim that an image model is always the best layout engine, that more reasoning is always wasteful, or that generated visual targets inherently improve reconstruction. Those are evaluation questions.

## 32. Initial MVP

The MVP must exercise the complete path on a small, reviewed catalogue before expanding breadth.

**Contract and interoperability baseline:** DTCG token ingestion for the declared profile, JSON Schema validation, explicit units, safe SVG handling, basic OpenUI description export, stable component identities and resolved package locks.

**Rendering baseline:** the seven primitives, native text, native shapes/groups, native connector bindings where required, SVG assets and role-limited raster content.

**Pilot catalogue:** enough objects to build a customer/control/application flow, a labelled data store, a metric card, a callout and a basic process. Cover native and hybrid bindings, not just icons.

**Initial pattern target:** linear process, cycle, hub-and-spoke, layered architecture, control flow, before/after comparison, milestone timeline and metric row. Release these incrementally with test evidence.

**Initial archetype target:** hero, comparison, architecture, process, timeline, metric-story and dashboard. The wider set in Section 19 remains a follow-on catalogue goal.

**Execution baseline:** faithful reference conversion, direct structured composition, one optional visual-generation path, rendered inspection, bounded repair and a machine-readable acceptance report.

A useful end-to-end path takes precedence over a large but untested catalogue.

## 33. Migration of Existing Folio Design Systems

The migration scope established in the original PRD is Lumen, Aperture, Meridian, Mosaic, Gridline and Werk. Track actual conversion and verification status in the linked implementation record.

Split the existing combined configuration into DTCG tokens, presentation behaviour, semantic definitions and visual bindings. Preserve existing appearance and content unless an intentional revision is separately approved.

Migration requirements:

1. Inventory consumers and canonical resources before changing filenames. Include legacy references such as `design/tokens.json` where still present.
2. Convert colour, type, spacing and stroke values without losing their original meaning. Convert physical units explicitly; retain the original measurements in migration fixtures.
3. Move canvas, grid topology, layer ordering and behaviour into the presentation profile. Reference tokenised magnitudes rather than duplicating them.
4. Introduce a versioned compatibility reader or a deliberate breaking release. Never let two editable token files become competing canonical sources.
5. Update manifests, registries, instructions, prompts and validators together.
6. Render representative slides before and after migration. Review text metrics, line heights, safe areas, connectors, fonts and colour conversions.
7. Record all intentional differences and any unsupported feature. Do not describe a partial migration as full standards conformance.

For old typography, compute the proposed line-height multiplier from the existing line height and font size, then verify rendering. A mathematically equivalent number is not sufficient evidence of identical application behaviour.

## 34. Strategic Outcome

An agent should be able to request an architecture slide, select a control-flow pattern, bind its roles to customer, identity, application and telemetry components, and obtain an editable result without manually describing every rectangle, label and connection.

For a novel reference, the system should still be able to infer a composition, use catalogue assets selectively and reconstruct the remainder without forcing the source into an unsuitable template.

The intended outcome is **semantic composition against an executable design system**, with visible evidence of what was preserved, approximated, substituted and tested.

## 35. Longer-Term Direction

Publish four separable products: the specification, machine-readable schemas and conformance fixtures, the Folio reference implementation, and the component/pattern catalogue.

Support an independent reader or renderer before claiming interoperability. Test shared examples against it and document any loss of meaning, appearance or editing capability.

Specification governance should include public proposals, versioned decisions, compatibility rules and contribution review. Licensing for specification text, implementation code and catalogue assets must be stated explicitly; this PRD does not change existing licences or assume that all third-party assets share one licence.

Standardisation is a possible consequence of independent adoption, not an MVP acceptance criterion. Keep the interfaces implementable without the Folio runtime or a particular model provider.

---

## 36. Multimodal Composition and Visual-Specification Workflow

### 36.1 Capability roles

The architecture separates roles, not necessarily services:

| Role | Input | Output | Responsibility |
| --- | --- | --- | --- |
| Planner | Brief, content, authority map | Content structure and task plan | Preserve intent and select a workflow |
| Visual proposer | Approved content, visual constraints and assets | Candidate visual specification | Explore appearance and hierarchy |
| Reconstructor | Accepted reference and authoritative content | Semantic composition and layout observations | Recover usable structure |
| Resolver / renderer | Composition, tokens, bindings and constraints | Scene and presentation | Produce the appropriate representations |
| Evaluator | Source contracts, scene and rendered output | Findings with evidence | Assess acceptance gates |
| Repair agent | Findings and current artefacts | Bounded changes | Correct defects without unrelated drift |

Visual generation is optional. A supplied screenshot is already a potential visual target. A reviewed pattern may need no generated reference. A model that proposes a visual target must not approve its own output without subsequent checks.

### 36.2 Three execution paths

**Reference conversion:** supplied image -> establish content and fidelity requirements -> decompose -> resolve components -> reconstruct -> render -> compare -> repair.

**Visual-led creation or redesign:** brief and design authority -> composition candidates -> select an acceptable visual target -> reconstruct with authoritative content -> render -> validate -> repair.

**Structured composition:** brief or graph -> select archetype/pattern/components -> resolve layout -> render -> validate -> repair. Bypass image generation when it adds no useful information.

All three converge on the same semantic composition, scene and acceptance contracts. Model choice is an execution binding, not a property of a database component or a design token.

### 36.3 Authority and conflict handling

User instructions and approved source content govern meaning. The selected design system governs the categories it actually defines. A visual reference governs appearance only within the authorised transformation.

In **Convert**, preserve supplied content, composition and treatment. In **Restyle**, preserve composition, semantic relationships, relative hierarchy and visible content per slide while applying requested treatment. In **Redesign**, preserve meaning while applying explicitly permitted structural changes; a formal system is optional and determines mode independently. If a request combines incompatible fidelity and governance requirements, surface the conflict rather than silently choosing.

A generated image may omit text, alter numbers, invent labels or suggest the wrong relationships. Reconstruct exact content from the content specification, not from generated lettering. Any authorised content rewrite needs a traceable content revision.

### 36.4 Visual-specification contract

A visual specification records its source, acceptance state, content revision, authority map, relevant assets and a small set of visual constraints. Acceptance may come from the user or from a permitted automated selection gate; record which occurred.

```json
{
  "schemaVersion": "0.1.0",
  "kind": "visual-specification",
  "id": "auth-flow-reference-01",
  "source": {
    "type": "generated-image",
    "assetId": "asset-auth-flow-reference",
    "generationRunId": "visual-run-01"
  },
  "contentRef": "content/auth-flow.json",
  "contentRevision": "1",
  "designSystem": { "id": "lumen", "version": "0.2.0" },
  "acceptance": { "status": "accepted", "method": "user" },
  "authority": {
    "content": "content-specification",
    "visualLayout": "reference",
    "tokens": "design-system"
  },
  "constraints": {
    "preserveHierarchy": true,
    "preserveRelativePlacement": true,
    "allowTextCorrectionFromSource": true,
    "allowFullSlideRasterOutput": false
  }
}
```

The asset record, not the model, supplies a verified digest. Rejected or superseded references remain identifiable so later comparisons do not accidentally use the wrong target.

### 36.5 Why this is an architectural choice

The proposal allocates visual exploration, semantic reasoning and precise editing to different stages. It does not depend on assumptions about whether a particular image model uses diffusion, autoregression, a spatial latent representation or another undisclosed architecture.

The working hypothesis is that suitable visual targets and reviewed components can reduce reconstruction effort and improve output. Test that hypothesis; do not treat it as a property guaranteed by a model name.

## 37. Semantic Composition and Scene Contracts

### 37.1 Semantic intermediate representation

The semantic composition records instances, content bindings, relationships, required editing operations, source references and any pattern/archetype selection. It remains independent of PptxGenJS, python-pptx or another backend.

It can contain inferred structure, but inferred relationships and uncertain readings must be identified. Resolve material uncertainty before declaring the slide accepted. A screenshot rarely reveals all of its original authoring structure; Folio is producing a useful reconstruction, not recovering an unknowable source file exactly.

### 37.2 Resolved scene

The scene records the renderer-neutral geometry and chosen representation for each object. Each node links to its semantic instance or is explicitly decorative. It also records reading order, text source, asset reference, layer and any supported connector endpoints.

```json
{
  "schemaVersion": "0.1.0",
  "kind": "scene",
  "id": "auth-flow-scene-01",
  "compositionRef": "compositions/customer-authentication.json",
  "canvas": { "width": 1280, "height": 720, "unit": "px" },
  "objects": [
    {
      "id": "customer-label",
      "semanticRef": "customer",
      "type": "text",
      "contentRef": "content/auth-flow.json#/customerLabel",
      "frame": { "x": 120, "y": 360, "width": 160, "height": 48 },
      "style": { "typography": { "token": "typography.body" }, "fill": { "token": "color.text" } },
      "layer": "text"
    }
  ],
  "readingOrder": ["customer-label"]
}
```

This small scene illustrates the contract, not a complete authentication diagram. In a complete scene, every required visible item and relationship must be represented or explicitly accounted for.

### 37.3 Constraints and exact geometry

Reusable patterns express layout intent; resolved scenes necessarily contain coordinates. "Semantics before geometry" does not mean eliminating geometry.

Required constraints include protected content, safe areas where applicable, minimum text size, required anchors and explicitly forbidden overlaps. Preferred constraints include balance, spacing rhythm and alignment preferences.

An unsatisfiable required set must return an actionable diagnostic. Soft constraints may be relaxed with a record of the trade-off. Arbitrary scalar scores must not obscure which requirements failed.

### 37.4 Reconstruction and repair locality

Preserve instance IDs between iterations. A repair should target the smallest relevant group of objects. Reflow dependent connectors when a node moves, but do not regenerate unrelated artwork or rewrite already-correct text.

Keep source observations separate from chosen geometry. For example, an observed text box may be approximately located, while its reconstructed frame becomes exact after measurement.

### 37.5 Determinism and round trips

Given a frozen composition, resolved tokens, assets, fonts, renderer and configuration, the rendering stage should be reproducible within declared tolerances. Model planning and image generation are not assumed deterministic.

Manual edits in PowerPoint remain valuable even without synchronisation back to Folio. MVP must not promise lossless PowerPoint -> semantic composition round trips. Re-rendering from a stale composition may overwrite manual edits; the workflow must warn about that boundary.

## 38. Representation Policy and Bounded Evaluation Loop

### 38.1 Representation policy

| Object | Preferred representation | Acceptance concern |
| --- | --- | --- |
| Heading, paragraph, diagram label | Native text | Content and editing must survive |
| Simple geometric object | Native shape | Geometry and styling remain practical to edit |
| Diagram relationship | Native connector where required | Endpoints, direction and labels are preserved |
| Reviewed icon or complex vector | SVG or native geometry, according to binding | Correct appearance with honest capability reporting |
| Composite card or diagram node | Native/hybrid group | Slots and anchors remain usable |
| Photograph or texture | Raster asset | Correct crop, resolution and rights |
| Decorative atmosphere | Suitable vector or raster layer | Cannot obscure required content |
| Chart or table | Native/data-backed binding where required | Numbers and labels cannot be inferred from a generated picture |

Raster is not inherently a defect. Unapproved loss of required semantics or editability is the defect. No full-slide raster substitution may be used to disguise failed reconstruction.

### 38.2 Loop contract

```text
Render candidate
    -> Run deterministic gates
    -> Inspect rendered appearance
    -> Produce object-level findings
    -> Accept OR repair within budget OR stop with diagnostics
```

A finding identifies severity, rule, object/region, evidence and proposed repair. Repairs create a new scene revision. Preserve the last acceptable checkpoint and the history of failed attempts.

A partial result must be labelled partial. A generated preview is not a completed editable presentation.

### 38.3 Budget and stop conditions

A job declares maximum visual candidates, repair rounds, elapsed time and model usage/cost ceilings where measurable. It stops on acceptance, exhausted budget, repeated non-improvement, missing material information or an unrecoverable renderer error.

Suggested starting defaults are one selected visual target, up to three repair rounds and a separately configured total time/cost limit. These are tunable product defaults, not validated optimum values.

Reserve capacity for compilation and validation instead of allowing planning to consume the entire job budget. When usage APIs do not expose a reasoning breakdown, record it as unavailable rather than pretending total output tokens equal emitted SVG or code.

### 38.4 Result contract

```json
{
  "schemaVersion": "0.1.0",
  "kind": "execution-result",
  "runId": "folio-run-01",
  "status": "partial",
  "artefacts": {
    "presentation": "output/deck.pptx",
    "scene": "output/scene.json",
    "preview": "output/preview.png",
    "validation": "output/validation.json"
  },
  "budget": { "repairRoundsUsed": 3, "repairRoundsLimit": 3 },
  "stopReason": "repair-budget-exhausted",
  "unresolved": [
    { "rule": "text-overflow", "objectId": "supporting-note", "severity": "error" }
  ]
}
```

Allowed overall states are `accepted`, `partial`, `failed` and `cancelled`. Unproduced artefacts are omitted, not represented by invented paths. No suitable artefact means `failed`, not `partial` merely because tokens were consumed.

## 39. Failure-Mode Catalogue and Conformance

Publish failure knowledge alongside the implementation. The following are **required test categories**, not claims that each has already been reproduced in Folio.

| ID | Failure category | Required handling |
| --- | --- | --- |
| FM-001 | Generated image changes text or a number | Restore from authoritative content; fail unresolved ambiguity |
| FM-002 | Attractive output is one flattened slide | Reject when required editing operations are absent |
| FM-003 | SVG treated as native editable geometry | Report actual capabilities; use a tested binding |
| FM-004 | Font substitution changes text metrics | Record substitution; remeasure and revalidate |
| FM-005 | Resizing breaks labels or anchors | Test supported resize modes and dependent routes |
| FM-006 | Connector crosses or detaches from a component | Reroute and verify attachment where required |
| FM-007 | Pattern exceeds its tested content capacity | Reflow, choose an approved alternative, split or fail |
| FM-008 | Required constraints contradict one another | Return the conflicting constraints; do not silently violate them |
| FM-009 | Missing token, reference cycle or invalid unit | Fail resolution before rendering |
| FM-010 | Missing governed asset replaced without disclosure | Stop or request an explicitly approved alternative |
| FM-011 | Repair loop never converges | Enforce budget and report the unresolved defect |
| FM-012 | Model returns no usable artefact | Mark stage failure; bounded retry/fallback only |
| FM-013 | Decorative layer obscures meaning | Respect exclusions and contrast/legibility checks |
| FM-014 | Progressive reveal moves unchanged objects | Preserve instance frames unless reflow is authorised |
| FM-015 | Output behaves differently across target applications | Scope compatibility to tested application/version |
| FM-016 | Package carries active or externally fetched content | Reject or sandbox according to the approved asset profile |

Each verified failure record should include a minimal reproducer, source and rendered artefacts where permitted, relevant versions, expected/actual behaviour, resolution, regression fixture and status.

Conformance must separate **format support**, **semantic support**, **renderer capabilities** and **visual acceptance**. One badge must not imply all four.

## 40. Evaluation and Evidence

### 40.1 Questions to test

Does a visual target improve composition? Does component reuse reduce cost and correction effort? Does reference-driven reconstruction preserve meaning and editing better than direct generation? Which models and effort settings work reliably for each stage?

These are separate questions and require separate comparisons.

### 40.2 Evaluation arms

Compare at least:

- Text-only direct generation without a reference or catalogue.
- Reference-driven reconstruction without a reusable catalogue.
- Reference-driven reconstruction with a bounded render/inspection loop.
- Structured composition with reviewed components and patterns.
- Visual-led composition followed by catalogue-aware reconstruction and validation.

Keep task content, required edits, relevant model settings and total budget comparable. Report reference availability and tools explicitly. A text-only SVG illustration benchmark is not directly equivalent to reference-driven editable slide reconstruction.

### 40.3 Metrics

Measure required-content accuracy, relationship accuracy, design-rule compliance, editable-object coverage by required operation, overflow and connection defects, blinded visual preference, completion rate, repair rounds, elapsed time and total cost per accepted artefact.

Count all stages, including image generation, inspection, retries and rendering. Distinguish emitted artefact tokens from hidden/reasoning tokens where the provider exposes them. Otherwise disclose the missing breakdown.

Report denominators and failures, not just successful examples. Repeated trials are required for any comparative model claim; a single attractive output is a case study.

### 40.4 Evaluation corpus

Use a fixed, versioned corpus with simple diagrams, crowded process flows, long labels, multilingual text, sparse editorial slides, photographs, complex vectors, data-backed charts and progressive reveals.

Include difficult and unsatisfiable cases. Keep some tasks outside the development set. Human review should be blinded to model identity where practicable.

Target renderers, font environments and preview resolution must be recorded. Pixel similarity alone is insufficient: a screenshot can match perfectly while failing all native editing requirements.

## 41. Security, Privacy and Provenance

Treat uploaded images, documents, component metadata, SVGs and packages as untrusted inputs. Separate interpretation of content from permission to execute instructions or access external resources.

The asset profile must reject or safely handle active SVG content, external references, path traversal, unsafe archive contents and excessive resource consumption. Dependencies and assets are resolved from approved sources; renderer execution is isolated and bounded.

Do not upload private presentation material to a model or external service unless that execution route is permitted. Record content classification, approved provider route and retention policy where applicable. Redact sensitive content from diagnostic telemetry.

Catalogue publication requires explicit approval of rights and provenance. Keep author, source, licence, modifications, approval state and asset digest. Never assume a user-supplied reference grants redistribution rights to an extracted component.

Fonts require declared availability and an explicit substitution policy. Do not bundle font files merely because they are installed in an execution environment.

## 42. Delivery Phases and Acceptance Criteria

### Phase 1 - Contracts and migration

Deliver schema definitions, examples, validation, DTCG migration fixtures, the package manifest, explicit unit conversion and the experimental OpenUI projection.

**Exit:** representative migrated systems resolve without missing references; all shipped examples pass structural and semantic tests; before/after changes are reviewed; unsupported features are reported.

### Phase 2 - Components and native output

Deliver a small reviewed catalogue, pattern expansion, scene generation, PowerPoint bindings and target-specific editing tests.

**Exit:** a labelled control flow and metric slide can be generated, opened, edited and rerendered. Labels remain native text. Required connections and data semantics survive the declared editing operations.

### Phase 3 - Visual-led reconstruction

Deliver visual-specification records, source authority, reference observations, bounded repairs, representation policies and execution evidence.

**Exit:** both supplied-reference and generated-reference paths reach the same output contracts. Budget exhaustion terminates cleanly. Failed or partial results are accurately labelled.

### Phase 4 - Independent consumption and evidence

Deliver public examples, documented failure fixtures, a second consumer or reference adapter, and the versioned evaluation corpus.

**Exit:** an independent implementation can load and interpret the semantic contracts without relying on undocumented Folio behaviour. Losses and unsupported features are explicit.

### Cross-cutting acceptance criteria

| ID | Requirement |
| --- | --- |
| AC-01 | Every required content item has a traceable source and appears correctly, or acceptance fails. |
| AC-02 | No required native text is replaced by raster or outlined glyphs without explicit authorisation. |
| AC-03 | Every reference resolves; duplicate identities, cycles and invalid units are rejected. |
| AC-04 | Component slots and defaults are validated before rendering. |
| AC-05 | Required editing capabilities pass tests on named target applications. |
| AC-06 | No unapproved full-slide raster fallback or design-system substitution is accepted. |
| AC-07 | Repairs stop at the declared limit and retain usable checkpoints and diagnostics. |
| AC-08 | Frozen resolved inputs produce reproducible scene/output behaviour within declared tolerances. |
| AC-09 | Unknown required capabilities fail; optional unsupported features are disclosed. |
| AC-10 | Governed claims cover only supplied, resolved and tested rules. |
| AC-11 | Comparative performance claims include failed runs and full-pipeline cost. |
| AC-12 | A new user can complete reference conversion without understanding schemas, registries or token formats. |

The numerical tolerances for layout, colour conversion and rendering are versioned test-profile decisions. Do not invent pass thresholds after inspecting the result.

## 43. Open Decisions

The following require implementation decisions and recorded rationale before the first stable schema release:

1. The precise constraint vocabulary, solver tie-breaks and error format.
2. The minimum DTCG rendering profile and the extent of Resolver support in the first release.
3. The native PowerPoint compatibility matrix and the SVG subset permitted by each binding.
4. The mechanism for preserving semantic IDs in output files and handling manual edits.
5. The package identity, publishing location and licence boundaries for specification, code and assets.
6. The OpenUI adapter's pinned source revision and documented projection losses.
7. The initial visual-acceptance rubric and the conditions permitting automated reference selection.

These decisions do not block a useful prototype. They do block an unqualified claim of interoperable, stable conformance.

## 44. Sources and Interpretation

Primary external sources below were consulted on 28 September 2026. They support the specific standards and product-behaviour statements where cited. They do not validate Folio's proposed architecture or performance.

- [DTCG Format Module 2025.10][dtcg-format]: format, types, reference handling, units and extensions.
- [DTCG Color Module 2025.10][dtcg-color]: colour representation.
- [DTCG Resolver Module 2025.10][dtcg-resolver]: contextual token resolution.
- [OpenUI draft-01][openui-spec]: the experimental component-description projection.
- [W3C Open UI][w3c-open-ui]: disambiguation from the separate web-controls initiative.
- [JSON Schema 2020-12][json-schema]: Folio schema dialect.
- [CSS Values and Units][css-units]: physical/logical unit relationship adopted by the renderer policy.
- [SVG 2][svg]: vector-format reference; Folio must publish its tested subset rather than imply universal feature support.
- [Microsoft SVG editing guidance][microsoft-svg]: editing and conversion behaviour must be distinguished from native object guarantees.
- [ECMA-376][ecma-376]: the existing Office Open XML format boundary.
- [Semantic Versioning 2.0.0][semver]: released contract/package versioning convention.

The architectural narrative, component taxonomy, example graphs, workflow requirements and acceptance criteria are the proposed Folio design developed in the preceding discussion. Screenshots of model comparisons are not used here as verified pricing, performance or architectural evidence.

[dtcg-format]: https://www.designtokens.org/tr/2025.10/format/
[dtcg-color]: https://www.designtokens.org/tr/2025.10/color/
[dtcg-resolver]: https://www.designtokens.org/tr/2025.10/resolver/
[openui-spec]: https://openuispec.org/spec
[w3c-open-ui]: https://open-ui.org/
[json-schema]: https://json-schema.org/draft/2020-12
[css-units]: https://www.w3.org/TR/css-values-4/#absolute-lengths
[svg]: https://www.w3.org/TR/SVG2/
[microsoft-svg]: https://support.microsoft.com/en-us/office/graphics-visuals/edit-svg-images-in-microsoft-365
[ecma-376]: https://ecma-international.org/publications-and-standards/standards/ecma-376/
[semver]: https://semver.org/spec/v2.0.0.html
