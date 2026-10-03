#!/usr/bin/env python3
"""Validate Folio versioned semantic contracts and resolve the supported DTCG token profile.

Install the optional validator dependency with: python3 -m pip install -r requirements-schema.txt
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

from folio_preservation import PreservationError, validate_preservation_bundle

SCHEMA_ROOT = Path(__file__).resolve().parents[1] / "schemas"
SCHEMA_PATH = SCHEMA_ROOT / "folio-0.1.0.schema.json"
SUPPORTED_VERSIONS = {"0.1.0", "0.2.0"}
ALIAS = re.compile(r"^\{([A-Za-z0-9_.-]+)\}$")
SUPPORTED_TYPES = {"color", "dimension", "fontFamily", "fontWeight", "number", "typography", "border", "strokeStyle", "shadow", "gradient"}


class ContractError(ValueError):
    pass


def read_json(path: Path) -> dict:
    def reject_constant(value: str) -> None:
        raise ValueError(f"non-finite JSON number: {value}")

    try:
        value = json.loads(path.read_text(encoding="utf-8"), parse_constant=reject_constant)
    except (OSError, ValueError) as exc:
        raise ContractError(f"{path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"{path}: expected JSON object")
    return value


def select_schema(document: dict, schema: dict, where: str) -> dict:
    version = document.get("schemaVersion")
    if version not in SUPPORTED_VERSIONS:
        raise ContractError(f"{where}: unsupported schemaVersion {version!r}")
    if not schema.get("$id", "").endswith(f"folio-{version}.schema.json"):
        schema = read_json(SCHEMA_ROOT / f"folio-{version}.schema.json")
    return schema


def validate_shape(document: dict, schema: dict, where: str) -> None:
    schema = select_schema(document, schema, where)
    kinds = {entry["$ref"].split("/")[-1] for entry in schema["oneOf"]}
    kind = document.get("kind")
    if kind not in kinds:
        raise ContractError(f"{where}: unsupported contract kind {kind!r} for {document['schemaVersion']}")
    # Validate the known kind directly so a failed gate reports its actual field.
    validator = Draft202012Validator({"$ref": f"#/$defs/{kind}", "$defs": schema["$defs"]})
    errors = sorted(validator.iter_errors(document), key=lambda error: tuple(str(part) for part in error.path))
    if errors:
        error = errors[0]
        location = ".".join(str(part) for part in error.path) or "root"
        raise ContractError(f"{where}:{location}: {error.message}")


def resource(root: Path, name: str, directory: bool = False, boundary: Path | None = None) -> Path:
    if not isinstance(name, str) or not name.strip() or Path(name).is_absolute():
        raise ContractError(f"invalid package resource path: {name!r}")
    path = (root / name).resolve()
    if not path.is_relative_to((boundary or root).resolve()):
        raise ContractError(f"resource escapes package: {name}")
    if not (path.is_dir() if directory else path.is_file()):
        raise ContractError(f"missing package resource: {name}")
    return path


def collect_tokens(documents: list[tuple[Path, dict]]) -> dict[str, dict]:
    tokens: dict[str, dict] = {}

    def walk(node: dict, prefix: str, inherited: str | None, source: Path) -> None:
        if "$extends" in node:
            raise ContractError(f"{source}: DTCG group extension is not supported in this profile")
        effective_type = node.get("$type", inherited)
        if "$value" in node:
            if any(not name.startswith("$") for name in node):
                raise ContractError(f"{source}: token {prefix} also contains child tokens")
            if not prefix or prefix in tokens:
                raise ContractError(f"duplicate or empty token path: {prefix}")
            if not effective_type:
                raise ContractError(f"token {prefix} has no $type")
            if effective_type not in SUPPORTED_TYPES:
                raise ContractError(f"token {prefix} has unsupported required type {effective_type}")
            tokens[prefix] = {"type": effective_type, "value": node["$value"], "source": str(source)}
            return
        for name, child in node.items():
            if name.startswith("$"):
                continue
            if not isinstance(child, dict):
                raise ContractError(f"token group {prefix or '<root>'}.{name} must be an object")
            walk(child, f"{prefix}.{name}" if prefix else name, effective_type, source)

    for path, data in documents:
        walk(data, "", None, path)
    return tokens


def resolve_tokens(tokens: dict[str, dict]) -> dict[str, dict]:
    resolved: dict[str, dict] = {}
    visiting: set[str] = set()

    def resolve_value(value: Any) -> Any:
        if isinstance(value, str):
            match = ALIAS.fullmatch(value)
            if match:
                return resolve_token(match.group(1))["value"]
            if value.startswith("{") and value.endswith("}"):
                raise ContractError(f"invalid token alias: {value}")
            return value
        if isinstance(value, list):
            return [resolve_value(item) for item in value]
        if isinstance(value, dict):
            if set(value) == {"$ref"}:
                pointer = value["$ref"]
                if not isinstance(pointer, str) or not pointer.startswith("#/"):
                    raise ContractError(f"unsupported DTCG JSON Pointer: {pointer!r}")
                segments = [part.replace("~1", "/").replace("~0", "~") for part in pointer[2:].split("/")]
                if "$value" not in segments:
                    raise ContractError(f"DTCG pointer must target a token value: {pointer}")
                marker = segments.index("$value")
                name = ".".join(segments[:marker])
                target = resolve_token(name)["value"]
                for segment in segments[marker + 1:]:
                    try:
                        target = target[int(segment)] if isinstance(target, list) else target[segment]
                    except (IndexError, KeyError, ValueError, TypeError) as exc:
                        raise ContractError(f"unresolved DTCG pointer: {pointer}") from exc
                return target
            return {key: resolve_value(item) for key, item in value.items()}
        return value

    def resolve_token(name: str) -> dict:
        if name in resolved:
            return resolved[name]
        if name in visiting:
            raise ContractError(f"token reference cycle at {name}")
        if name not in tokens:
            raise ContractError(f"missing token reference: {name}")
        visiting.add(name)
        entry = tokens[name]
        value = resolve_value(entry["value"])
        check_token_value(name, entry["type"], value)
        resolved[name] = {**entry, "value": value}
        visiting.remove(name)
        return resolved[name]

    for name in tokens:
        resolve_token(name)
    return resolved


def check_token_value(name: str, token_type: str, value: Any) -> None:
    def numeric(item: Any) -> bool:
        return isinstance(item, (int, float)) and not isinstance(item, bool) and math.isfinite(item)

    if token_type == "dimension":
        if not isinstance(value, dict) or not numeric(value.get("value")) or value.get("unit") not in ("px", "rem"):
            raise ContractError(f"{name}: dimension must have numeric value and px/rem unit")
    elif token_type == "color":
        if not isinstance(value, dict) or value.get("colorSpace") != "srgb" or not isinstance(value.get("components"), list) or len(value["components"]) != 3 or any(not numeric(item) or not 0 <= item <= 1 for item in value["components"]):
            raise ContractError(f"{name}: colour must have three sRGB components in 0..1")
        if "hex" in value and (not isinstance(value["hex"], str) or not re.fullmatch(r"#[0-9A-Fa-f]{6}", value["hex"])):
            raise ContractError(f"{name}: invalid hex fallback")
        if "hex" in value:
            hex_components = [int(value["hex"][index:index + 2], 16) for index in (1, 3, 5)]
            if any(abs(component * 255 - hex_component) > 0.5 for component, hex_component in zip(value["components"], hex_components)):
                raise ContractError(f"{name}: hex fallback disagrees with sRGB components")
    elif token_type == "fontFamily":
        if not (isinstance(value, str) and value.strip()) and not (isinstance(value, list) and value and all(isinstance(item, str) and item.strip() for item in value)):
            raise ContractError(f"{name}: invalid font family")
    elif token_type in ("fontWeight", "number"):
        if not numeric(value) and not (token_type == "fontWeight" and isinstance(value, str) and value.strip()):
            raise ContractError(f"{name}: invalid {token_type}")
    elif token_type == "typography":
        required = {"fontFamily", "fontSize", "fontWeight", "letterSpacing", "lineHeight"}
        if not isinstance(value, dict) or not required <= set(value):
            raise ContractError(f"{name}: incomplete typography value")
        for key in ("fontSize", "letterSpacing"):
            check_token_value(f"{name}.{key}", "dimension", value[key])
        check_token_value(f"{name}.fontFamily", "fontFamily", value["fontFamily"])
        check_token_value(f"{name}.fontWeight", "fontWeight", value["fontWeight"])
        if not numeric(value["lineHeight"]) or value["lineHeight"] <= 0:
            raise ContractError(f"{name}: lineHeight must be a multiplier")
    elif token_type in ("border", "strokeStyle", "shadow", "gradient"):
        if not isinstance(value, (dict, list, str)):
            raise ContractError(f"{name}: invalid {token_type} value")


def load_system(system_root: Path, schema: dict) -> tuple[dict, dict, dict[str, dict]]:
    manifest = read_json(system_root / "system.json")
    validate_shape(manifest, schema, "system.json")
    if manifest["id"] != system_root.name:
        raise ContractError("manifest id does not match package directory")
    paths = manifest["resources"]
    for key, value in paths.items():
        if key == "tokens":
            for name in value:
                resource(system_root, name)
        else:
            resource(system_root, value, directory=key == "archetypes")
    token_sources = [(Path(name), read_json(resource(system_root, name))) for name in paths["tokens"]]
    tokens = resolve_tokens(collect_tokens(token_sources))
    profile = read_json(resource(system_root, paths["presentation"]))
    validate_shape(profile, schema, paths["presentation"])
    if profile["id"].split(".")[0] != manifest["id"]:
        raise ContractError("presentation profile id does not belong to system")
    for edge, ref in profile.get("safeArea", {}).items():
        if isinstance(ref, dict) and "token" in ref:
            token = tokens.get(ref["token"])
            if token is None or token["type"] != "dimension" or token["value"]["value"] < 0:
                raise ContractError(f"safeArea.{edge} requires a dimension token")
    gutter = profile.get("grid", {}).get("gutter")
    if isinstance(gutter, dict) and "token" in gutter and (gutter["token"] not in tokens or tokens[gutter["token"]]["type"] != "dimension"):
        raise ContractError("grid.gutter requires a dimension token")
    return manifest, profile, tokens


def validate_document(path: Path, schema: dict) -> dict:
    document = read_json(path)
    schema = select_schema(document, schema, str(path))
    kind = document.get("kind")
    if kind not in schema["$defs"]:
        raise ContractError(f"{path}: unknown contract kind {kind!r}")
    validate_shape(document, schema, str(path))
    if kind == "component":
        try:
            Draft202012Validator.check_schema(document["propertiesSchema"])
        except SchemaError as exc:
            raise ContractError(f"{path}: invalid propertiesSchema: {exc.message}") from exc
        for binding_path in document["bindings"]:
            resource(path.parent, binding_path, boundary=path.parent.parent)
        for slot_name, slot in document["slots"].items():
            if slot["minItems"] > slot["maxItems"]:
                raise ContractError(f"{path}: invalid cardinality for {slot_name}")
            source = slot.get("contentFrom", {}).get("property")
            if source and source not in document["propertiesSchema"].get("properties", {}):
                raise ContractError(f"{path}: slot {slot_name} references missing property {source}")
    if kind == "pattern":
        slots = set(document["slots"])
        for relation in document["relationships"]:
            for endpoint in ("from", "to"):
                if relation[endpoint] not in slots:
                    raise ContractError(f"{path}: relationship references missing slot {relation[endpoint]}")
            if relation.get("when", {}).get("slotPresent", next(iter(slots))) not in slots:
                raise ContractError(f"{path}: condition references missing slot")
        for constraint in document["layout"]["constraints"]:
            references = constraint.get("slots", []) + [constraint[key] for key in ("subject", "reference") if key in constraint]
            if any(name not in slots for name in references):
                raise ContractError(f"{path}: constraint references missing slot")
            if constraint.get("when", {}).get("slotPresent", next(iter(slots))) not in slots:
                raise ContractError(f"{path}: constraint condition references missing slot")
    if kind == "renderer-binding":
            resource(path.parent, document["source"], boundary=path.parent.parent)
    if kind == "scene":
        object_ids = [obj["id"] for obj in document["objects"]]
        if len(object_ids) != len(set(object_ids)):
            raise ContractError(f"{path}: duplicate scene object id")
        for obj_id in document["readingOrder"]:
            if obj_id not in object_ids:
                raise ContractError(f"{path}: reading order references missing object {obj_id}")
        if "compositionRef" in document:
            resource(path.parent, document["compositionRef"], boundary=path.parent.parent)
    if kind == "execution-result" and document["budget"]["repairRoundsUsed"] > document["budget"]["repairRoundsLimit"]:
        raise ContractError(f"{path}: repair budget exceeded")
    return document


def validate_bundle(documents: list[tuple[Path, dict]], tokens: dict[str, dict]) -> None:
    # Bundle callers must not bypass shape checks on the stricter evidence records.
    for path, document in documents:
        if document.get("schemaVersion") == "0.2.0":
            validate_shape(document, read_json(SCHEMA_ROOT / "folio-0.2.0.schema.json"), str(path))
    by_kind_id = {(doc["kind"], doc.get("id")): doc for _, doc in documents if "id" in doc}
    by_path = {path: doc for path, doc in documents}
    for path, doc in documents:
        kind = doc["kind"]
        if kind == "component":
            for name in doc["bindings"]:
                binding_path = resource(path.parent, name, boundary=path.parent.parent)
                if binding_path not in by_path or by_path[binding_path]["kind"] != "renderer-binding":
                    raise ContractError(f"{path}: bundle omits renderer binding {name}")
        elif kind == "renderer-binding":
            component = by_kind_id.get(("component", doc["component"]))
            if not component:
                raise ContractError(f"{path}: bundle omits component {doc['component']}")
            if component["version"] != doc["componentVersion"]:
                raise ContractError(f"{path}: component version mismatch")
            if set(component["anchors"]) - set(doc["anchors"]):
                raise ContractError(f"{path}: binding omits component anchors")
            source_path = resource(path.parent, doc["source"], boundary=path.parent.parent)
            if source_path not in by_path or by_path[source_path]["kind"] != "scene":
                raise ContractError(f"{path}: bundle omits binding scene")
        elif kind == "composition":
            pattern_ref = doc.get("pattern")
            if pattern_ref:
                pattern = by_kind_id.get(("pattern", pattern_ref["id"]))
                if not pattern:
                    raise ContractError(f"{path}: bundle omits pattern {pattern_ref['id']}")
                bound = set(doc["bindings"])
                required = {name for name, slot in pattern["slots"].items() if slot["minItems"]}
                if pattern["version"] != pattern_ref["version"] or not required <= bound or not bound <= set(pattern["slots"]):
                    raise ContractError(f"{path}: pattern version or slot bindings mismatch")
            instance_ids = [value["id"] for value in doc["bindings"].values()]
            if len(instance_ids) != len(set(instance_ids)):
                raise ContractError(f"{path}: duplicate component instance id")
            for binding in doc["bindings"].values():
                component = by_kind_id.get(("component", binding["component"]))
                if not component:
                    raise ContractError(f"{path}: bundle omits component {binding['component']}")
                errors = list(Draft202012Validator(component["propertiesSchema"]).iter_errors(binding["properties"]))
                if errors:
                    raise ContractError(f"{path}: invalid properties for {binding['id']}: {errors[0].message}")
        elif kind == "scene" and "compositionRef" in doc:
            composition_path = resource(path.parent, doc["compositionRef"], boundary=path.parent.parent)
            composition = by_path.get(composition_path)
            if not composition or composition["kind"] != "composition":
                raise ContractError(f"{path}: bundle omits composition")
            instances = {value["id"] for value in composition["bindings"].values()}
            for obj in doc["objects"]:
                if "semanticRef" in obj and obj["semanticRef"] not in instances:
                    raise ContractError(f"{path}: unknown semanticRef {obj['semanticRef']}")
                if obj["type"] == "connector" and "preservation" not in doc and (obj.get("source") not in instances or obj.get("target") not in instances):
                    raise ContractError(f"{path}: connector endpoints do not resolve")

        def check_references(value: Any) -> None:
            if isinstance(value, dict):
                if "token" in value and isinstance(value["token"], str) and value["token"] not in tokens:
                    raise ContractError(f"{path}: missing token {value['token']}")
                for child in value.values():
                    check_references(child)
            elif isinstance(value, list):
                for child in value:
                    check_references(child)

        check_references(doc)

    try:
        validate_preservation_bundle(documents)
    except PreservationError as exc:
        raise ContractError(str(exc)) from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("system_root", type=Path)
    parser.add_argument("documents", nargs="*", type=Path, help="additional Folio contract documents")
    parser.add_argument("--show-tokens", nargs="*", metavar="TOKEN", help="print resolved tokens; omit names for all")
    args = parser.parse_args()
    try:
        schema = read_json(SCHEMA_PATH)
        Draft202012Validator.check_schema(schema)
        manifest, profile, tokens = load_system(args.system_root.resolve(), schema)
        documents = [(path.resolve(), validate_document(path.resolve(), schema)) for path in args.documents]
        validate_bundle(documents, tokens)
        if args.show_tokens is not None:
            names = args.show_tokens or list(tokens)
            selected = {}
            for name in names:
                if name not in tokens:
                    raise ContractError(f"missing token: {name}")
                selected[name] = tokens[name]
            print(json.dumps(selected, indent=2, ensure_ascii=False))
        else:
            print(f"validated {manifest['id']} {manifest['version']}: {len(tokens)} tokens, {len(args.documents)} contracts, profile {profile['id']}")
        return 0
    except (ContractError, ValueError) as exc:
        print(f"Folio schema validation failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
