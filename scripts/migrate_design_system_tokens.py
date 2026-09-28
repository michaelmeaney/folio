#!/usr/bin/env python3
"""Bootstrap schema resources or maintain a derived legacy compatibility file."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

PIXELS_PER_INCH = 96
POINTS_PER_INCH = 72
EXTENSION = "io.github.michaelmeaney.folio"


def dimension(value: float, unit: str) -> dict:
    if unit not in ("in", "pt", "px"):
        raise ValueError(f"unsupported source unit: {unit}")
    px = value * (PIXELS_PER_INCH if unit == "in" else PIXELS_PER_INCH / POINTS_PER_INCH if unit == "pt" else 1)
    return {
        "$type": "dimension",
        "$value": {"value": px, "unit": "px"},
        "$extensions": {EXTENSION: {"legacyValue": value, "legacyUnit": unit}},
    }


def convert(legacy: dict, system_id: str) -> tuple[dict, dict]:
    if legacy.get("name") != system_id:
        raise ValueError(f"legacy token name does not match system {system_id}")
    colors = {}
    for name, value in legacy["color"].items():
        if not isinstance(value, str) or len(value) != 7 or not value.startswith("#"):
            raise ValueError(f"invalid hex colour: {name}")
        components = [int(value[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        colors[name] = {"$type": "color", "$value": {"colorSpace": "srgb", "components": components, "hex": value}}
    fonts = {}
    for name, value in legacy["font"].items():
        if name == "fallback":
            continue
        fonts[name] = {"$type": "fontFamily", "$value": [value, *legacy["font"].get("fallback", [])]}
    typography = {}
    for name, style in legacy["type"].items():
        size_pt, line_pt = style["sizePt"], style["lineHeightPt"]
        typography[name] = {
            "$type": "typography",
            "$value": {
                "fontFamily": "{font.mono}" if name == "code" and "mono" in fonts else "{font.primary}",
                "fontSize": {"value": size_pt * 4 / 3, "unit": "px"},
                "fontWeight": style["weight"],
                "letterSpacing": {"value": 0, "unit": "px"},
                "lineHeight": line_pt / size_pt,
            },
            "$extensions": {EXTENSION: {"legacySizePt": size_pt, "legacyLineHeightPt": line_pt}},
        }
    layout = legacy["layout"]
    spacing = {
        "safeArea": {edge: dimension(value, "in") for edge, value in layout["safeAreaIn"].items()},
        "gutter": dimension(layout["gutterIn"], "in"),
        "scale": {f"step{index:02d}": dimension(value, "in") for index, value in enumerate(layout["spacingIn"], 1)},
    }
    lines = {name[:-2]: dimension(value, "pt") for name, value in legacy.get("line", {}).items() if name.endswith("Pt")}
    shapes = {}
    for name, value in legacy.get("shape", {}).items():
        unit = "pt" if name.endswith("Pt") else "px" if name.endswith("Px") else None
        if unit is None:
            raise ValueError(f"unknown shape unit: {name}")
        shapes[name[:-2]] = dimension(value, unit)
    tokens = {"color": colors, "font": fonts, "typography": typography, "spacing": spacing}
    semantic = {
        "canvas": {"$type": "color", "$value": "{color.background}"},
        "text": {"$type": "color", "$value": "{color.foreground}"},
    }
    muted = "foregroundMuted" if "foregroundMuted" in colors else "muted" if "muted" in colors else None
    if muted:
        semantic["mutedText"] = {"$type": "color", "$value": f"{{color.{muted}}}"}
    focus = next((name for name in ("primary", "accent", "brand") if name in colors), None)
    if focus:
        semantic["focus"] = {"$type": "color", "$value": f"{{color.{focus}}}"}
    statuses = {name: {"$type": "color", "$value": f"{{color.{name}}}"} for name in ("success", "warning", "danger") if name in colors}
    if statuses:
        semantic["status"] = statuses
    tokens["semantic"] = semantic
    if lines:
        tokens["line"] = lines
    if shapes:
        tokens["shape"] = shapes
    canvas = legacy["canvas"]
    presentation = {
        "schemaVersion": "0.1.0", "kind": "presentation-profile", "id": f"{system_id}.wide",
        "canvas": {"width": canvas["widthIn"] * PIXELS_PER_INCH, "height": canvas["heightIn"] * PIXELS_PER_INCH, "unit": "px"},
        "units": {"pixelsPerInch": PIXELS_PER_INCH, "pointsPerInch": POINTS_PER_INCH, "rootFontSizePx": 16},
        "grid": {"columns": layout["columns"], "gutter": {"token": "spacing.gutter"}},
        "safeArea": {edge: {"token": f"spacing.safeArea.{edge}"} for edge in ("left", "right", "top", "bottom")},
        "layers": legacy.get("layers", {}),
        "textOverflow": {"allowTruncation": False, "allowUnapprovedRewrite": False},
        "extensions": {EXTENSION: {"legacyVersion": legacy["version"], "legacyCanvasRatio": canvas["ratio"]}},
    }
    if "atmosphere" in legacy:
        presentation["atmosphere"] = legacy["atmosphere"]
    return tokens, presentation


def legacy_from_schema(tokens: dict, profile: dict, system_id: str) -> dict:
    """Rebuild the compatibility file from canonical DTCG/profile values."""
    def source_dimension(token: dict) -> float:
        original = token["$extensions"][EXTENSION]
        unit = original["legacyUnit"]
        px = token["$value"]["value"]
        converted = px / (PIXELS_PER_INCH if unit == "in" else PIXELS_PER_INCH / POINTS_PER_INCH if unit == "pt" else 1)
        return round(converted, 10)

    metadata = profile["extensions"][EXTENSION]
    font = {name: token["$value"][0] for name, token in tokens["font"].items()}
    font["fallback"] = tokens["font"]["primary"]["$value"][1:]
    typography = {}
    for name, token in tokens["typography"].items():
        value = token["$value"]
        typography[name] = {
            "sizePt": round(value["fontSize"]["value"] * POINTS_PER_INCH / PIXELS_PER_INCH, 10),
            "lineHeightPt": round(value["lineHeight"] * value["fontSize"]["value"] * POINTS_PER_INCH / PIXELS_PER_INCH, 10),
            "weight": value["fontWeight"],
        }
    layout = {
        "safeAreaIn": {edge: source_dimension(token) for edge, token in tokens["spacing"]["safeArea"].items()},
        "columns": profile["grid"]["columns"],
        "gutterIn": source_dimension(tokens["spacing"]["gutter"]),
        "spacingIn": [source_dimension(token) for _, token in sorted(tokens["spacing"]["scale"].items())],
    }
    legacy = {
        "name": system_id,
        "version": metadata["legacyVersion"],
        "canvas": {"ratio": metadata["legacyCanvasRatio"], "widthIn": round(profile["canvas"]["width"] / PIXELS_PER_INCH, 10), "heightIn": round(profile["canvas"]["height"] / PIXELS_PER_INCH, 10)},
        "font": font,
        "color": {name: token["$value"]["hex"] for name, token in tokens["color"].items()},
        "type": typography,
        "layout": layout,
    }
    if profile.get("layers"):
        legacy["layers"] = profile["layers"]
    if "shape" in tokens:
        legacy["shape"] = {name + ("Pt" if token["$extensions"][EXTENSION]["legacyUnit"] == "pt" else "Px"): source_dimension(token) for name, token in tokens["shape"].items()}
    if "line" in tokens:
        legacy["line"] = {name + "Pt": source_dimension(token) for name, token in tokens["line"].items()}
    if "atmosphere" in profile:
        legacy["atmosphere"] = profile["atmosphere"]
    return legacy


def serialized(value: dict) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("system_root", type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="check the legacy compatibility file against canonical schema resources")
    mode.add_argument("--sync-legacy", action="store_true", help="refresh the legacy compatibility file from canonical schema resources")
    mode.add_argument("--from-legacy", action="store_true", help="bootstrap schema resources from an unmigrated legacy file; overwrites schema resources")
    args = parser.parse_args()
    root = args.system_root.resolve()
    legacy_path = root / "tokens.json"
    if args.check or args.sync_legacy:
        tokens = json.loads((root / "tokens" / "core.tokens.json").read_text(encoding="utf-8"))
        profile = json.loads((root / "presentation.json").read_text(encoding="utf-8"))
        expected = legacy_from_schema(tokens, profile, root.name)
        if args.check:
            if json.loads(legacy_path.read_text(encoding="utf-8")) != expected:
                print(f"legacy compatibility file differs: {legacy_path}")
                return 1
            return 0
        legacy_path.write_text(serialized(expected), encoding="utf-8")
        print(legacy_path)
        return 0
    legacy = json.loads(legacy_path.read_text(encoding="utf-8"))
    tokens, profile = convert(legacy, root.name)
    for path, value in {root / "tokens" / "core.tokens.json": tokens, root / "presentation.json": profile}.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(serialized(value), encoding="utf-8")
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
