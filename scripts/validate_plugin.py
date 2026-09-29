#!/usr/bin/env python3
"""Validate Folio's Codex and Claude Code plugin packages."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
PLUGIN_NAME = re.compile(r"^[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*$")
CLAUDE_PLUGIN_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")

ALLOWED_TOP = {
    "id", "name", "version", "description", "skills", "apps", "mcpServers",
    "interface", "author", "homepage", "repository", "license", "keywords",
}
REQUIRED_INTERFACE = {
    "displayName", "shortDescription", "longDescription",
    "developerName", "category", "capabilities",
}
REQUIRED_RESOURCES = [
    "skills/folio/references/modes.md",
    "skills/folio/references/composition-contract.md",
    "skills/folio/references/design-system-resolution.md",
    "components/shared/registry.json",
    "design-systems/registry.json",
    "design-systems/lumen/system.json",
    "design-systems/lumen/DESIGN.md",
    "design-systems/lumen/tokens.json",
    "design-systems/lumen/tokens/core.tokens.json",
    "design-systems/lumen/presentation.json",
    "schemas/folio-0.1.0.schema.json",
    "schemas/folio-0.2.0.schema.json",
    "scripts/folio_preservation.py",
    "design-systems/lumen/archetypes/reference-constrained.yaml",
    "design-systems/lumen/components/registry.json",
    "design-systems/lumen/prompts/visual-generation.md",
    "design-systems/lumen/prompts/reconstruction.md",
]


def load_json(path: Path, errors: list[str]):
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing {path}")
        return None
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON in {path}: {exc}")
        return None

    if not isinstance(value, dict):
        errors.append(f"{path} must contain a JSON object")
        return None
    return value


def skill_frontmatter(path: Path, errors: list[str]):
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"missing {path}")
        return None, ""

    if not text.startswith("---\n"):
        errors.append(f"{path} must start with YAML frontmatter")
        return None, text

    end = text.find("\n---", 4)
    if end < 0:
        errors.append(f"{path} frontmatter is not closed")
        return None, text

    fields = {}
    for line in text[4:end].splitlines():
        if ":" not in line or line.startswith((" ", "\t")):
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip("\"'")

    return fields, text


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    claude_manifest_path = root / ".claude-plugin" / "plugin.json"
    claude_manifest = load_json(claude_manifest_path, errors)
    if claude_manifest is not None:
        claude_name = claude_manifest.get("name")
        if (
            not isinstance(claude_name, str)
            or not CLAUDE_PLUGIN_NAME.fullmatch(claude_name)
        ):
            errors.append("Claude Code plugin.json name must be kebab-case")
        if claude_name != "folio":
            errors.append(
                "Claude Code plugin.json name must match the Folio package name 'folio'"
            )
        for key in ("description", "homepage", "repository"):
            if (
                not isinstance(claude_manifest.get(key), str)
                or not claude_manifest[key].strip()
            ):
                errors.append(
                    f"Claude Code plugin.json field {key!r} must be a non-empty string"
                )
        author = claude_manifest.get("author")
        if (
            not isinstance(author, dict)
            or not isinstance(author.get("name"), str)
            or not author["name"].strip()
        ):
            errors.append("Claude Code plugin.json author.name is required")

    marketplace_path = root / ".claude-plugin" / "marketplace.json"
    marketplace = load_json(marketplace_path, errors)
    if marketplace is not None:
        if (
            not isinstance(marketplace.get("description"), str)
            or not marketplace["description"].strip()
        ):
            errors.append(
                "Claude Code marketplace.json description must be a non-empty string"
            )
        marketplace_plugins = marketplace.get("plugins")
        if not isinstance(marketplace_plugins, list):
            errors.append("Claude Code marketplace.json plugins must be an array")
        elif not any(
            isinstance(entry, dict)
            and entry.get("name") == "folio"
            and entry.get("source") == "./"
            for entry in marketplace_plugins
        ):
            errors.append("Claude Code marketplace.json must list Folio with source './'")

    manifest_path = root / ".codex-plugin" / "plugin.json"
    manifest = load_json(manifest_path, errors)
    if manifest is None:
        return errors

    unknown = sorted(set(manifest) - ALLOWED_TOP)
    if unknown:
        errors.append(f"unsupported plugin.json fields: {', '.join(unknown)}")

    for key in ("name", "version", "description"):
        if not isinstance(manifest.get(key), str) or not manifest[key].strip():
            errors.append(f"plugin.json field {key!r} must be a non-empty string")

    name = manifest.get("name")
    if isinstance(name, str) and not PLUGIN_NAME.fullmatch(name):
        errors.append("plugin.json name has invalid characters")

    version = manifest.get("version")
    if isinstance(version, str) and not SEMVER.fullmatch(version):
        errors.append("plugin.json version must be strict semver")

    author = manifest.get("author")
    if (
        not isinstance(author, dict)
        or not isinstance(author.get("name"), str)
        or not author["name"].strip()
    ):
        errors.append("plugin.json author.name is required")

    skills = manifest.get("skills")
    if (
        not isinstance(skills, str)
        or skills.rstrip("/").removeprefix("./") != "skills"
    ):
        errors.append("plugin.json skills must resolve to ./skills/")

    interface = manifest.get("interface")
    if not isinstance(interface, dict):
        errors.append("plugin.json interface must be an object")
    else:
        for key in REQUIRED_INTERFACE:
            value = interface.get(key)
            if key == "capabilities":
                if (
                    not isinstance(value, list)
                    or not value
                    or not all(isinstance(item, str) and item.strip() for item in value)
                ):
                    errors.append(
                        "interface.capabilities must be a non-empty array of strings"
                    )
            elif not isinstance(value, str) or not value.strip():
                errors.append(f"interface.{key} must be a non-empty string")

        prompts = interface.get("defaultPrompt", interface.get("default_prompt"))
        if (
            not isinstance(prompts, list)
            or not prompts
            or not all(isinstance(item, str) and item.strip() for item in prompts)
        ):
            errors.append(
                "interface.defaultPrompt must be a non-empty array of strings"
            )
        else:
            if len(prompts) > 3:
                errors.append("interface.defaultPrompt may contain at most 3 prompts")
            if any(len(item) > 128 for item in prompts):
                errors.append(
                    "interface.defaultPrompt entries must be <=128 characters"
                )

        color = interface.get("brandColor")
        if color is not None and (
            not isinstance(color, str) or not HEX.fullmatch(color)
        ):
            errors.append("interface.brandColor must use #RRGGBB")

    skill_path = root / "skills" / "folio" / "SKILL.md"
    frontmatter, _ = skill_frontmatter(skill_path, errors)
    if frontmatter is not None:
        if frontmatter.get("name") != "folio":
            errors.append("Folio Skill frontmatter name must be 'folio'")
        if not frontmatter.get("description"):
            errors.append("Folio Skill frontmatter description is required")

    agent_path = root / "skills" / "folio" / "agents" / "openai.yaml"
    try:
        agent_text = agent_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"missing {agent_path}")
        agent_text = ""

    for marker in ("interface:", "display_name:", "short_description:"):
        if marker not in agent_text:
            errors.append(f"{agent_path} is missing {marker.rstrip(':')}")

    for rel in REQUIRED_RESOURCES:
        if not (root / rel).is_file():
            errors.append(f"missing required Folio resource: {rel}")

    registry_path = root / "design-systems" / "registry.json"
    registry = load_json(registry_path, errors)
    if registry is not None:
        systems = registry.get("systems")
        if not isinstance(systems, list) or not systems:
            errors.append("design-systems/registry.json systems must be a non-empty array")
        else:
            seen_ids: set[str] = set()
            for entry in systems:
                if not isinstance(entry, dict):
                    errors.append("design-systems/registry.json system entries must be objects")
                    continue
                system_id = entry.get("id")
                manifest_rel = entry.get("manifest")
                if not isinstance(system_id, str) or not system_id.strip():
                    errors.append("registered design system id must be a non-empty string")
                    continue
                if system_id in seen_ids:
                    errors.append(f"duplicate registered design system id: {system_id}")
                seen_ids.add(system_id)
                if not isinstance(manifest_rel, str) or not manifest_rel.strip():
                    errors.append(f"registered design system {system_id!r} must declare manifest")
                    continue

                system_manifest_path = root / "design-systems" / manifest_rel
                if not system_manifest_path.is_file():
                    errors.append(
                        f"registered design system {system_id!r} manifest does not resolve to a file"
                    )
                    continue
                system = load_json(system_manifest_path, errors)
                if system is None:
                    continue
                if system.get("id") != system_id:
                    errors.append(
                        f"registered design system {system_id!r} manifest id does not match"
                    )

                system_root = system_manifest_path.parent
                if system.get("schemaVersion") == "0.1.0":
                    if system.get("kind") != "design-system" or system.get("tokenFormat") != {"name": "dtcg", "version": "2025.10"}:
                        errors.append(f"{system_id} has invalid schema metadata")
                    resources = system.get("resources")
                    if not isinstance(resources, dict):
                        errors.append(f"{system_id} must declare schema resources")
                    else:
                        for key in ("tokens", "presentation"):
                            if key not in resources:
                                errors.append(f"{system_id} missing schema resource {key}")
                        for key, value in resources.items():
                            if key == "tokens" and not isinstance(value, list):
                                errors.append(f"{system_id} schema tokens must be a list")
                                continue
                            values = value if key == "tokens" and isinstance(value, list) else [value]
                            if not values or any(
                                not isinstance(rel, str)
                                or not rel.strip()
                                or Path(rel).is_absolute()
                                or not (system_root / rel).resolve().is_relative_to(system_root.resolve())
                                or not ((system_root / rel).is_dir() if key == "archetypes" else (system_root / rel).is_file())
                                for rel in values
                            ):
                                errors.append(f"{system_id} schema resource {key!r} is missing or outside package")
                for field in ("design", "tokens"):
                    rel = system.get(field)
                    if (
                        not isinstance(rel, str)
                        or not rel.strip()
                        or not (system_root / rel).is_file()
                    ):
                        errors.append(
                            f"{system_id} system.json field {field!r} does not resolve "
                            "to a file"
                        )

                optional_resources = {
                    "archetypes": "directory",
                    "componentRegistry": "file",
                    "catalogue": "directory",
                    "sharedComponentRegistry": "file",
                }
                for field, resource_type in optional_resources.items():
                    rel = system.get(field)
                    if rel is None:
                        continue
                    if not isinstance(rel, str) or not rel.strip():
                        resolves = False
                    else:
                        resource_path = system_root / rel
                        resolves = (
                            resource_path.is_dir()
                            if resource_type == "directory"
                            else resource_path.is_file()
                        )
                    if not resolves:
                        errors.append(
                            f"{system_id} system.json field {field!r} does not resolve "
                            f"to a {resource_type}"
                        )

                prompts = system.get("prompts")
                if prompts is not None:
                    if not isinstance(prompts, dict):
                        errors.append(f"{system_id} system.json prompts must be an object")
                    else:
                        for prompt_name, rel in prompts.items():
                            prompt_path = (
                                system_root / rel if isinstance(rel, str) else None
                            )
                            if (
                                not isinstance(rel, str)
                                or not rel.strip()
                                or prompt_path is None
                                or not prompt_path.is_file()
                            ):
                                errors.append(
                                    f"{system_id} system.json prompt {prompt_name!r} "
                                    "does not resolve to a file"
                                )

            default_id = registry.get("default")
            if default_id is not None and default_id not in seen_ids:
                errors.append(
                    "design-systems/registry.json default must reference a registered id"
                )

    for path in (manifest_path, skill_path, agent_path):
        if path.is_file() and "[TODO:" in path.read_text(encoding="utf-8"):
            errors.append(f"{path} contains an unresolved TODO placeholder")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Folio Codex plugin package"
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Folio repository/plugin root",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors = validate(root)

    if errors:
        print("Folio plugin validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Folio plugin validation passed: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
