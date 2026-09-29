---
title: Lumen functional contrast
type: design
status: in-progress
number: 1
date: 2026-09-29
---

# Lumen functional contrast

## Problem

In a reviewed architecture slide, pale Lumen panels and their borders blended into the near-white canvas. Muted labels and small attribution text were also difficult to read. A different pale fill does not make a functional box distinguishable.

## Decision

- Use text colours that reach at least 4.5:1 for normal text on both Lumen's default and alternate backgrounds. Large text may use the 3:1 threshold. Check the final rendered pair, including transparency and imagery.
- Give boundaries and connectors needed to understand a diagram at least 3:1 against adjacent fills. Use the functional border token for pale containers.
- Keep light accents and washes available for decoration and fills, but do not use them as small text on light backgrounds.
- Preserve contrast in progressive builds instead of dimming meaningful content with opacity.
- Apply these checks in every Folio mode without importing Lumen styling into Quick, Guided, or another governed system.

The thresholds follow WCAG 2.1's text and non-text contrast criteria, applied to presentation documents using W3C's informative WCAG2ICT guidance. Passing these checks alone does not establish that a deck is accessible.

## Implementation

The Lumen canonical and compatibility tokens, its design guidance and prompts, the progressive-build archetype, and the all-mode acceptance criteria implement this decision. Review a rendered architecture slide at presentation size and verify its exported PowerPoint reading order and text alternatives separately.
