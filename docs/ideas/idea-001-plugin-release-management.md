---
title: "Plugin release management"
type: idea
status: proposed
number: "001"
date: "2026-09-28"
owner: folio-maintainers
updated: "2026-09-29"
supersedes: null
superseded_by: null
related:
  - ../README.md
  - ../plans/plan-002-release-please-plugin-releases.md
tags:
  - plugin
  - release
  - distribution
---

# Plugin release management

## Opportunity

Folio needs a predictable way to publish one reviewed plugin revision to its installation channels. A commit on `main` identifies source state, but it does not by itself establish release notes, compatibility expectations or a reliable update signal for every plugin host.

## Evidence considered

- A manual Claude plugin release skill demonstrates useful checks around changelogs, manifest versions and tags, but assumes its own `package.json`, version branches and migration registry. Those are not Folio requirements.
- [Release Please](https://github.com/googleapis/release-please) can maintain a release pull request from Conventional Commits, update arbitrary JSON version fields, generate a changelog, and create a tag and GitHub Release when the release pull request merges. Its `simple` release type fits a plugin that is not an npm package.
- A marketplace release-manager pattern is useful when one repository contains several independently released plugins. Folio currently has one canonical plugin with host-specific packaging, so independent plugin release streams would add complexity without a current use case.

## Proposed direction

- Use Release Please to prepare an on-demand release pull request for the single Folio plugin release stream. The pull request contains the proposed SemVer bump, `CHANGELOG.md` update and synchronized version-bearing host manifests.
- Treat merge of the reviewed release pull request as the publishing decision. Release Please then creates the matching `v<version>` tag and GitHub Release from `main`; ordinary feature pull requests do not publish releases directly.
- Use `.codex-plugin/plugin.json` as a required version target. Add the tracked Claude plugin manifest as another target if Folio adopts a Claude manifest version field. Both host adapters describe the same canonical `skills/folio/` payload and should resolve to the same released Folio revision.
- Derive release intent from Conventional Commit types, preferably through squash-merge pull-request titles: `fix` requests a patch, `feat` requests a minor release, and a breaking-change marker requests a major release. Documentation and maintenance changes should not force a release unless deliberately marked.
- Publish only after the repository validator, change-integrity checks and documented install/update checks pass for every supported host. Release automation does not deploy unrelated sites or infrastructure.
- Keep schema, design-system package and catalogue contract versions independent from the Folio plugin version. Release notes identify any included contract changes and provide migration guidance for breaking changes.
- Supersede a faulty release with a corrective patch and clear release notes. Do not move an already-published tag; keep the previous working tag and installation instructions discoverable.

## Constraints

- Pin the Release Please action to an immutable commit SHA that satisfies the repository's seven-day minimum-age policy, and verify it with `pinact`.
- Grant only the workflow permissions required by the selected configuration. If release pull requests must trigger normal validation workflows, use an appropriately scoped GitHub App or fine-grained token because events created by the default `GITHUB_TOKEN` do not start further workflow runs.
- Bootstrap Release Please from verified existing tags, releases and manifest versions. Do not infer release history solely from the current manifest.

## Next step

Follow [plan 002](../plans/plan-002-release-please-plugin-releases.md) to validate the current release baseline, introduce Release Please through review, and prove the first release end to end. Add a short maintainer runbook after the workflow has been exercised successfully. This proposal does not itself change the current distribution configuration.
