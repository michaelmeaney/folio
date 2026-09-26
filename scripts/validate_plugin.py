#!/usr/bin/env python3
"""Validate the Folio Codex plugin package using only the Python standard library."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
PLUGIN_NAME = re.compile(r"^[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*$")
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
    "skills/folio/references/design-system-resolution.md",
    "components/shared/registry.json",
    "design-systems/lumen/system.json",
    "design-systems/lumen/DESIGN.md",
    "design-systems/lumen/tokens.json",
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

    system = load_json(root / "design-systems" / "lumen" / "system.json", errors)
    if system is not None:
        lumen_root = root / "design-systems" / "lumen"
        for field in ("design", "tokens", "componentRegistry", "catalogue"):
            rel = system.get(field)
            if not isinstance(rel, str) or not (lumen_root / rel).exists():
                errors.append(
                    f"Lumen system.json field {field!r} does not resolve "
                    "to an existing resource"
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
