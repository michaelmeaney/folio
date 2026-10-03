---
title: "Repeatable presentation benchmark"
type: prd
status: approved
number: "002"
date: "2026-09-29"
---

# Repeatable presentation benchmark

## Purpose

Evaluate new Folio versions against the same real reference, distinguishing faithful conversion, composition-preserving restyling and narrative redesign. This extends the [composition preservation decision](../architecture/adr-001-composition-preserving-transformations.md) with observable presentation outcomes.

## Requirements

1. Quick Convert produces one editable slide preserving source content, composition and styling without a governed system.
2. Governed Restyle produces one editable slide applying a selected system without silently changing the source composition or meaning.
3. Governed Redesign produces five editable slides with a coherent story, explicit permission to split and rewrite, and all material source facts retained visibly.
4. Source, prompts, rubric, runner and plugin files are frozen per run. Model, reasoning effort, execution surface, selected system, repetition count and timeout are explicit controls. Actual renderer/application versions are verified during review.
5. Independent fresh contexts prevent previous outputs or the reviewer answer key from influencing generation. A command adapter supports automation without hard-coding a model provider.
6. Structural checks inspect the delivered PowerPoint and renders. Separate evidence-backed reviews assess content, composition, treatment and real application editing. Missing evidence cannot pass.
7. Release comparisons use identical benchmark controls and runtime profiles. Report per-case acceptance counts and measured timing, retaining failures and unobserved measurements.
8. The reference and unreviewed outputs stay local. Reviewed examples require separate publication approval.

## Initial scope

The initial fixture is the supplied AI Architecture Review Agent slide. Lumen is the default selected system; other registered systems can be selected. One repetition supports a smoke run; three repetitions are recommended for comparisons. This single fixture is a regression benchmark, not broad proof of presentation quality across domains.

## Delivery

See [implementation 004](../implementation/implementation-004-presentation-benchmark.md) and [operating instructions](../../bench/README.md). A prepared run is not an executed or accepted result.
