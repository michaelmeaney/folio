---
title: "Release Please plugin releases"
type: plan
status: proposed
number: "002"
date: "2026-09-29"
owner: folio-maintainers
updated: "2026-09-29"
supersedes: null
superseded_by: null
related:
  - ../ideas/idea-001-plugin-release-management.md
  - ../README.md
tags:
  - plugin
  - release
  - automation
  - distribution
---

# Release Please plugin releases

## Context and outcome

The [plugin release-management idea](../ideas/idea-001-plugin-release-management.md) proposes Release Please as the coordinator for Folio's single plugin release stream. Folio needs one reviewed release identity across its supported host adapters, a reliable Codex update signal, useful release notes and a recoverable record of published versions.

The intended result is an on-demand workflow in which changes merge normally to `main`, Release Please maintains a release pull request, and merging that pull request creates a `v<version>` tag and GitHub Release.

## Scope and dependencies

- The release unit is the canonical Folio plugin payload, including `skills/folio/` and the resources it declares.
- `.codex-plugin/plugin.json` is a required synchronized version target. The tracked `.claude-plugin/plugin.json` becomes a second target if Folio adopts a Claude manifest version field.
- Schema and design-system package versions remain independent contracts. Their compatibility impact is summarized in the plugin release notes when they ship together.
- Implementation starts in the authoritative plugin repository on a clean branch. Existing conflicts or archived checkouts are not a release baseline.
- Release Please uses Conventional Commit semantics. Folio can preserve normal pull-request development by enforcing the convention on squash-merge titles rather than every intermediate commit.

## Work sequence

### 0. Establish the release baseline

**Owner:** Folio maintainers. **Dependency:** authoritative repository and release access.

1. Inventory tracked Codex and Claude manifests, marketplace metadata, current versions, tags and GitHub Releases.
2. Reconcile the current `0.2.3` Codex manifest version with actual published history. Record the last valid release version and commit; decide whether `0.2.3` is an existing release or only a development version.
3. Confirm the supported installation and update commands for Codex and Claude. Replace any local-worktree marketplace source with the intended Git source before calling the channel releasable.
4. Decide the bootstrap commit that bounds Release Please's history scan. Record it in configuration when older commits should not be interpreted as unreleased changes.

**Exit:** one documented baseline identifies the last release, its commit, its host manifests and the commands used to install or update it.

### 1. Define release semantics

**Owner:** Folio maintainers. **Dependency:** phase 0.

1. Adopt SemVer for the Folio plugin while it is pre-1.0: `fix` produces a patch, `feat` produces a minor release, and a breaking-change marker produces a major release. Document how pre-1.0 breaking changes are called out.
2. Configure repository merge policy or contributor guidance so squash-merge pull-request titles carry a valid Conventional Commit type. Do not make documentation-only or maintenance-only changes publish a plugin release by default.
3. Define the release note sections and the information required for host behavior, schema/design-system compatibility, migration steps and known limitations.
4. Define withdrawal behavior: retain immutable published tags, mark a faulty GitHub Release clearly, publish a corrective patch, and keep the previous working installation reference available.

**Exit:** contributors can determine the expected release impact of a pull request before it merges.

### 2. Configure Release Please

**Owner:** release automation maintainer. **Dependency:** phases 0 and 1.

1. Add a root-package Release Please manifest initialized to the verified last release version.
2. Add a `simple` release configuration for package path `.`. Use `v<version>` tags without a component prefix and update `.codex-plugin/plugin.json` through `extra-files`. Add a version to the Claude plugin manifest only after confirming it against the native validator and marketplace behavior; if adopted, update it through the same release pull request.
3. Add a workflow triggered by changes to `main`, with concurrency that prevents two release runs from racing. Pin `googleapis/release-please-action` to an immutable SHA selected through `pinact run --update --min-age 7`, then verify it with the repository's required `pinact` check.
4. Scope permissions to `contents: write` and `pull-requests: write`, adding `issues: write` only if lifecycle labels are retained and require it. Configure the repository setting that permits Actions to create pull requests.
5. Choose the release credential deliberately. If validation workflows must run automatically on the generated release pull request, use a narrowly scoped GitHub App or fine-grained token whose events can trigger those workflows; document its ownership and rotation. Otherwise, define an explicit maintainer-run validation gate before merge.

**Exit:** a reviewed workflow can open or update one release pull request without publishing a release, changing unrelated files or widening permissions beyond its configuration.

### 3. Gate the release pull request

**Owner:** release maintainer and reviewers. **Dependency:** phase 2.

1. Require `python3 scripts/validate_plugin.py .` and `git diff --check` on the release pull request.
2. Run the native Claude plugin validator. If the Claude manifest gains a version field, verify that it matches the Codex manifest and Release Please manifest.
3. Perform the documented install/update smoke checks for each supported host against the release candidate. Confirm that the installed plugin reports the proposed version and loads the canonical Folio Skill.
4. Review the generated changelog for user-facing accuracy, compatibility notes and migration guidance. Keep generated presentation and preview artefacts out of the release unless separately reviewed and declared.
5. Protect merge of the release pull request with the required checks and maintainer review. Merging this pull request is the explicit publish action.

**Exit:** the release pull request shows synchronized versions, accurate notes, passing package validation and successful host update evidence.

### 4. Publish and verify the first automated release

**Owner:** release maintainer. **Dependency:** phase 3 approval.

1. Merge the approved release pull request and observe the Release Please run through completion.
2. Verify that the tag points to the intended commit, the GitHub Release uses the same version and the release notes match the reviewed changelog.
3. Refresh each supported marketplace and run the documented update command. Verify the active installed version and inspect a basic Folio invocation rather than relying only on manifest contents.
4. Record the release URL, tag, source commit, validation runs and installation evidence in an implementation record.
5. Write a short maintainer runbook from the exercised process, including how to hold a release PR, force an intentional version, supersede a faulty release and diagnose missing release PRs caused by commit types.

**Exit:** one release has been created and installed through every supported channel from the same reviewed source commit.

## Acceptance gates

| Gate | Required evidence |
| --- | --- |
| Baseline integrity | Published tags, GitHub Releases and manifest versions are reconciled before bootstrapping. |
| Version coherence | The Release Please and Codex manifests carry the same Folio plugin version; any adopted Claude manifest version matches them. |
| Reviewability | The version bump and changelog are reviewed in a pull request before publication. |
| Repository safety | The action is SHA-pinned, passes the seven-day `pinact` policy and uses documented least-privilege permissions. |
| Package quality | Folio validation and each supported host's native validation and update smoke check pass. |
| Publication integrity | Tag, GitHub Release, source commit and installed marketplace versions agree. |
| Recovery | A maintainer can identify the previous working tag and publish a corrective release without rewriting an existing tag. |

## Operational limits

- Do not merge a release pull request merely to test the workflow; merging is the publication trigger.
- Do not let Release Please version independently released schemas or design-system packages through the Folio plugin version field.
- Do not add version branches, placeholder migrations or a `package.json` solely to satisfy release automation.
- Do not publish from a dirty, conflicted or archived checkout.
