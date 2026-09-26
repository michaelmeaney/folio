# Folio project documentation

`docs/` is the authoritative working record for Folio project decisions and delivery. It follows the same intent-to-implementation chain as the Sophie portfolio reference while keeping Folio's own terminology and scope.

## Delivery chain

Read and update the relevant documents in this order:

1. **Vision** defines the enduring purpose, audience and boundaries.
2. **Ideas** explores possible directions before they become commitments.
3. **PRDs** turn an accepted direction into testable product requirements.
4. **Architecture** records the technical decisions and constraints that satisfy those requirements.
5. **Plans** sequence implementation, migration, release and operations work.
6. **Implementation** maps requirements and decisions to source, verification and current gaps.

The [design](design/README.md) documents are cross-cutting. Read them for any visual, interaction, typography, colour or content-presentation change.

## Start here

| Area | Question it answers | Location |
| --- | --- | --- |
| Vision | Why does this project exist and what is out of scope? | [vision](vision/) |
| Ideas | What possibilities are being considered? | [ideas](ideas/) |
| PRDs | What must the plugin do? | [PRDs](prds/) |
| Architecture | How does it work and why? | [architecture](architecture/) |
| Design | What visual and interaction rules govern the experience? | [design](design/) |
| Plans | In what order is work delivered and operated? | [plans](plans/) |
| Implementation | What is shipped, how is it verified and what remains? | [implementation](implementation/) |
| Template | What metadata and structure does a new document require? | [project-work template](templates/project-work.md) |

## File naming

Project-work documents use a type slug, a zero-padded number and a lowercase kebab-case title:

```text
<type>-<nnn>-<kebab-case-title>.md
```

Examples:

- `vision-001-folio.md`
- `idea-001-editable-preview-catalogue.md`
- `adr-001-plugin-packaging.md`
- `plan-001-worker-deployment.md`

Use these controlled type slugs where they fit: `vision`, `idea`, `prd`, `adr`, `design`, `plan`, `implementation`, `debt` and `runbook`. Add a new type only when an existing type cannot express the document's purpose. Numbers are unique within a type, are never reused, and should remain stable once referenced.

## Front matter and lifecycle

Every project-work document must begin with YAML front matter. At minimum, include `title`, `type`, `status`, `number` and `date`. Use the lowercase controlled statuses below:

| Status | Meaning |
| --- | --- |
| `draft` | Work in progress and not ready for review or reliance. |
| `proposed` | Ready for review; not an accepted commitment. |
| `approved` | Accepted as the current direction or requirement. |
| `in-progress` | Approved work is actively being delivered. |
| `implemented` | Delivered and verified against its stated acceptance or evidence. |
| `rejected` | Considered and deliberately not accepted. |
| `superseded` | Replaced by a newer document; link the successor. |
| `retired` | No longer applicable, retained for historical context. |

When one document replaces another, set the older document to `superseded` and add `superseded_by`; set `supersedes` on the new document. Do not silently rewrite the rationale of an approved or superseded ADR.

The documents in `docs/` should be evidence-based and internally linked. Root-level guidance may summarise them, but must not contradict them. If a material requirement or decision is missing, record it in the relevant document or as a `debt` document under [implementation](implementation/README.md) rather than inventing it in code.
