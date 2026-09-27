# Folio

**An open, model-independent presentation engineering harness for AI agents.**

Folio turns content, visual references and organisational design systems into editable presentation artefacts.

> **Bring your agent. Bring your design system. Folio builds the presentation.**

Folio is not another presentation model or proprietary slide editor. It is the harness around capable agents and multimodal models: the workflow, design authority, representation rules, reconstruction process and validation needed to turn generative visual reasoning into a normal editable PowerPoint.

> **The generated image is the visual specification. The editable PowerPoint is the product.**

Better models make Folio better. Organisations can keep their existing agents, design systems, component libraries and PowerPoint workflows rather than moving presentation work into another proprietary platform.

## Start simple. Scale as far as you need.

Folio is intended to be equally useful to someone who installs the Skill in ChatGPT and immediately asks for a slide, and to an organisation running a tailored presentation-engineering workflow with its own design system, component libraries, agents and validation policy.

**Complexity is opt-in. Capability is not.**

You do not need to understand Folio's internal machinery to get a useful result. As your requirements mature, the same harness exposes progressively more control.

| Experience | Start here | Add when useful | Typical use |
| --- | --- | --- | --- |
| **Simple — Use** | Install Folio and ask naturally | A brief, reference image or existing slide | Recreate a reference, create a deck, produce editable PowerPoint |
| **Intermediate — Customise** | Keep the same natural workflow | Colours, fonts, logos, reference decks, selected design systems and component libraries | Reusable team presentation patterns and stronger visual consistency |
| **Advanced — Integrate & automate** | Treat Folio as presentation engineering infrastructure | Organisational design systems, private components, MCP, custom archetypes, agent workflows, validation and CI/CD | Governed enterprise presentation production |

The adoption path is deliberately progressive:

```text
Install → Use → Customise → Integrate → Automate
```

A simple invocation can still use sophisticated capabilities internally. The difference is how much configuration and control the user chooses to expose.

For example:

```text
Simple
"Use Folio to turn this screenshot into an editable slide."

Intermediate
"Create this deck using our colours, Inter, Phosphor icons and these
reference slides."

Advanced
"Use Corporate Design System 4.2, our private component catalogue and
Architecture archetype v3. Execute through our presentation agent and
fail the build on governance violations."
```

### Execution profiles

Internally, Folio currently expresses that progression through three execution profiles:

- **Quick** — the supplied reference is the design authority. Optimise for faithful editable reconstruction without requiring design-system knowledge.
- **Guided** — add lightweight visual preferences or reusable resources as a local style contract.
- **Governed** — resolve and enforce an installed or supplied organisational design system, including partial systems with an explicit validation boundary.

These are execution semantics, not prerequisites a new user must learn before using Folio. The public experience should favour the simplest path that satisfies the request and progressively disclose the deeper controls.

Before presentation generation, Folio plays back the interpreted transformation and obtains confirmation. For reference-image work, the primary choice is **Convert** (preserve the reference design) or **Redesign** (recompose it using a design system).

For Governed execution, the user explicitly selects either an installed Folio design system or supplies an alternative design-system repository/link. Folio does not silently choose Lumen or another system.

## What Folio provides

A capable model can reason about content and explore composition. Folio makes that process repeatable and governable.

```text
Content / brief / reference
        ↓
Semantic decomposition
        ↓
Design authority
        ↓
Archetype + component resolution
        ↓
Visual composition
        ↓
Visual specification
        ↓
Deterministic reconstruction
        ↓
Validation
        ↓
Editable presentation artefact
```

Folio supplies the presentation-engineering contract around that flow:

- **Agent/runtime adapters** — execute Folio from capable agent environments.
- **Design systems** — define visual authority, tokens, archetypes and presentation rules.
- **Component providers** — resolve reusable vectors and higher-order presentation semantics.
- **Reconstruction rules** — choose the correct editable representation for each object.
- **Validation** — check structure, fidelity, overflow, governance and editability.
- **Renderers** — PowerPoint is the first output target.

The core principle is simple: **use the native representation appropriate to the thing being represented.**

```text
text          → native text
simple form   → native shape
relationship  → editable connector
illustration  → SVG / vector
photograph    → raster image
```

Folio does not flatten a reconstructable slide into a picture, and it does not force expressive illustrations into hundreds of crude PowerPoint primitives merely to claim editability.

## Bring your own design system

Folio is a framework for presentation design systems, not a fixed Folio aesthetic.

An organisation can add its own design authority and use Folio as the execution layer:

```text
Organisational design system
├── brand tokens
├── typography
├── assets
├── components
├── archetypes
├── layout rules
└── validation rules
              ↓
            Folio
              ↓
      agent + model stack
              ↓
   governed editable PPTX
```

A design system may be complete or partial. Governed execution uses the resources actually supplied and makes the validation boundary explicit rather than silently substituting Folio defaults.

The adapter model is intentionally open: organisational resources may originate from repositories, design-token files, presentation templates, asset libraries or systems such as Figma. Folio should make an existing design system executable, not require designers to maintain another source of truth.

**Lumen** is Folio's first bundled design system and reference implementation. It demonstrates the design-system contract; it is not "the Folio look".

## Why a harness?

Presentation generation is more than slide drawing.

A model may be excellent at composition but still needs repeatable instructions for design-system resolution, component selection, representation, reconstruction and acceptance testing. Folio separates those concerns from the underlying model.

```text
Agent / host
     ↓
Folio harness
     ├── workflow
     ├── execution profile
     ├── design authority
     ├── component resolution
     ├── reconstruction
     └── validation
     ↓
Multimodal model + presentation tooling
     ↓
Editable artefact
```

**Folio defines the process. The agent executes it.**

This creates a natural evaluation boundary. The same presentation task, design system and acceptance criteria can eventually be executed across different model/runtime combinations to measure how well each executes the presentation-engineering contract.

## Repository layout

```text
folio/
├── .codex-plugin/
├── skills/folio/
├── design-systems/
├── components/
├── examples/
├── docs/
├── scripts/
└── catalogue/
```

This repository contains the Folio plugin and its canonical design systems, components, examples and validation tooling. It is designed to evolve towards independently pluggable design systems, component providers, agent adapters and renderers while keeping Folio Core model-independent.

## Plugin and Skill packaging

Folio is currently packaged as a Codex plugin. The plugin manifest lives at `.codex-plugin/plugin.json` and exposes the Folio orchestration Skill from `skills/folio/`.

The Skill is a control plane rather than a copy of the design system. When installed as part of the plugin it resolves Lumen and future design systems from the plugin root, keeping tokens, archetypes, components and catalogues canonical.

The same `skills/folio/` directory is also valid as a standalone Skill bundle. The lowest-friction path needs no plugin-level design system. Users can progressively add lightweight preferences, reusable resources and finally complete or partial organisational design systems without changing the fundamental interaction model.

Agent-specific packaging is an adapter to Folio, not the definition of Folio itself. The framework should remain usable by other capable agent runtimes as adapters are added.

## Design systems

Each installed Folio design system can be self-contained: visual rules, exact tokens, archetypes, system-specific component variants, generation instructions and a multimodal catalogue.

Lumen is a minimal, modern editorial reference system built around strong typography, generous whitespace, restrained vector graphics and soft atmospheric depth.

## Components and providers

Folio components provide stable presentation semantics such as actors, resources, security concepts, architecture zones and connectors.

Commodity visual primitives do not need to be reinvented. Folio can resolve approved external vector libraries while retaining its own higher-order semantic identities and design-system styling.

A design system may provide its own visual variant while retaining a stable semantic ID. Shared therefore means **shared semantics**, not necessarily one SVG for every visual language.

## Component lifecycle

```text
Need visual
    ↓
Existing component? ── yes ──→ reuse canonical asset
    │
    no
    ↓
Generate candidate
    ↓
Reconstruct / vectorise
    ↓
Review
    ↓
Promote to component library
    ↓
Available to future presentations
```

The visual catalogue acts as visual API documentation for humans and multimodal models. Stable IDs allow reconstruction to resolve a visual concept to its canonical vector asset.

## Composition model

Foreground content owns the slide.

```text
Content
  → foreground composition
  → whitespace map
  → background composition
```

Blurred geometry and atmospheric colour can be first-class background components rather than arbitrary decoration. They are selected only after the functional composition exists and placed primarily into genuine negative space.

## Progressive presentation design

Complex ideas should be revealed rather than compressed. Progressive builds preserve component positions while successive slides introduce the relevant parts of the final composition.

```text
Ideate → Create & refine → Decompose → Assemble → Reveal → Design system
```

## Repository and artefact model

**GitHub is canonical.** Design rules, tokens, prompts, archetypes, vector components, metadata, catalogues and reference implementations belong here.

Reviewed `.pptx` files and preview images may additionally be published to Google Drive for convenient human consumption.

## Model compatibility and execution reliability

Folio is model-independent as a harness, but individual models must be verified against the complete presentation workflow before compatibility is claimed.

Compatibility is tracked by **model, reasoning effort, execution surface and Folio workflow**. In ChatGPT Chat, **GPT-6 Astra at Medium reasoning** is currently verified; **GPT-6 Luna** and **GPT-6 Sol** remain test-required. **ChatGPT Work is currently test-required across the listed models**. Context pressure is also tested independently because a clean execution and a heavily loaded conversation can produce materially different workflow reliability.

See [Model compatibility](docs/implementation/implementation-001-model-compatibility.md) for the test matrix and [Troubleshooting and Q&A](docs/implementation/runbook-001-folio-execution-troubleshooting.md) for known operational failure modes, including context exhaustion and when to start presentation execution in a fresh chat.

## Validation

Run `python3 scripts/validate_plugin.py .` from the repository root before publishing or installing a plugin revision. The validator checks the manifest, Skill entrypoint/metadata, required Folio resources and starter-prompt constraints.

The standalone Folio Skill is additionally validated and packaged with the OpenAI Skill Creator tooling.

## Licensing

Folio is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

The intent is to keep Folio, its modifications and derivative versions open under the terms of the AGPL, including the licence's provisions for modified versions used over a network.

Presentations and other output artefacts created using Folio are **not automatically licensed under the AGPL merely because Folio was used to create them**. Users remain responsible for rights in the content and assets they supply.

See [LICENSE](LICENSE) for the governing licence text. If this README and the licence differ, the licence controls.

## Current status

Folio has an installable plugin structure, a packaged orchestration Skill and the Lumen reference design system. Reference-image reconstruction has been exercised end-to-end through editable PowerPoint generation and validation.

The project is now evolving from that working path into a broader **model-independent presentation engineering harness**: additional agent adapters, organisational design-system ingestion, component providers, evaluation fixtures and richer validation.
