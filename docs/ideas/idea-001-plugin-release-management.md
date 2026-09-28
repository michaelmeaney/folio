---
title: "Plugin release management"
type: idea
status: draft
number: "001"
date: "2026-09-28"
owner: folio-maintainers
updated: "2026-09-28"
supersedes: null
superseded_by: null
related:
  - ../README.md
tags:
  - plugin
  - release
  - distribution
---

# Plugin release management

## Opportunity

Folio needs a predictable way to publish one reviewed plugin revision to its installation channels. A commit on `main` identifies source state, but it does not by itself establish release notes, compatibility expectations, or a reliable update signal for every plugin host.

## Starter proposal

- Use a reviewed, versioned release commit on `main`, followed by a matching Git tag and GitHub Release with concise changes and upgrade notes.
- Bump `.codex-plugin/plugin.json` for every published plugin update. Codex may retain a cached installation when the manifest version stays the same after a marketplace refresh.
- Keep the canonical `skills/folio/` content shared across hosts. Record how Claude Code selects and updates a Git-hosted revision; decide whether its package metadata should carry the same release version.
- Publish only after package validation and a documented installation/update check for each supported host.
- Record breaking schema or design-system changes separately from plugin packaging changes, even when they ship in the same release.

## Questions before a release policy is approved

1. Should releases follow a fixed cadence or be cut when reviewed changes are ready?
2. Should installation track `main`, a release tag, or a stable release branch in each host?
3. Which checks and compatibility fixtures must pass before tagging, and who approves the tag?
4. How will a faulty release be withdrawn or superseded, and how will users find the previous working version?
5. Should the plugin, schema, design-system packages and catalogue share a number or remain independently versioned?

## Next step

Turn the agreed answers into a release plan and short maintainer runbook. This idea does not change the current distribution configuration.
