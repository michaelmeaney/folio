"""Contract tests for token migration and semantic validation."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from folio_schema import ContractError, collect_tokens, load_system, read_json, resolve_tokens, validate_bundle, validate_document  # noqa: E402
from migrate_design_system_tokens import legacy_from_schema  # noqa: E402


class TokenMigrationTests(unittest.TestCase):
    def test_six_systems_preserve_legacy_values(self):
        schema = read_json(ROOT / "schemas" / "folio-0.1.0.schema.json")
        for root in sorted((ROOT / "design-systems").iterdir()):
            if not (root / "tokens.json").is_file():
                continue
            with self.subTest(system=root.name):
                legacy = read_json(root / "tokens.json")
                tokens = read_json(root / "tokens" / "core.tokens.json")
                profile = read_json(root / "presentation.json")
                self.assertEqual(legacy_from_schema(tokens, profile, root.name), legacy)
                for name, original in legacy["color"].items():
                    self.assertEqual(tokens["color"][name]["$value"]["hex"], original)
                for name, original in legacy["type"].items():
                    converted = tokens["typography"][name]["$value"]
                    self.assertAlmostEqual(converted["fontSize"]["value"] * 3 / 4, original["sizePt"])
                    self.assertAlmostEqual(converted["lineHeight"] * original["sizePt"], original["lineHeightPt"])
                self.assertAlmostEqual(profile["canvas"]["width"] / 96, legacy["canvas"]["widthIn"])
                _, _, resolved = load_system(root, schema)
                self.assertEqual(resolved["semantic.canvas"]["value"], resolved["color.background"]["value"])
                self.assertEqual(resolved["semantic.text"]["value"], resolved["color.foreground"]["value"])

    def test_alias_and_json_pointer_resolve(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "tokens.json"
            source.write_text("{}")
            data = {
                "spacing": {
                    "base": {"$type": "dimension", "$value": {"value": 24, "unit": "px"}},
                    "alias": {"$type": "dimension", "$value": "{spacing.base}"},
                    "pointer": {"$type": "dimension", "$value": {"$ref": "#/spacing/base/$value"}},
                }
            }
            resolved = resolve_tokens(collect_tokens([(source, data)]))
            self.assertEqual(resolved["spacing.alias"]["value"], resolved["spacing.base"]["value"])
            self.assertEqual(resolved["spacing.pointer"]["value"], resolved["spacing.base"]["value"])

    def test_cycles_missing_references_and_invalid_units_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "tokens.json"
            for data in (
                {"a": {"$type": "dimension", "$value": "{b}"}, "b": {"$type": "dimension", "$value": "{a}"}},
                {"a": {"$type": "dimension", "$value": "{missing}"}},
                {"a": {"$type": "dimension", "$value": {"value": 1, "unit": "pt"}}},
            ):
                with self.subTest(data=data), self.assertRaises(ContractError):
                    resolve_tokens(collect_tokens([(source, data)]))

    def test_duplicate_paths_fail(self):
        with self.assertRaisesRegex(ContractError, "duplicate"):
            collect_tokens([
                (Path("one.json"), {"color": {"ink": {"$type": "color", "$value": {"colorSpace": "srgb", "components": [0, 0, 0]}}}}),
                (Path("two.json"), {"color": {"ink": {"$type": "color", "$value": {"colorSpace": "srgb", "components": [1, 1, 1]}}}}),
            ])


class ContractBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = read_json(ROOT / "schemas" / "folio-0.1.0.schema.json")
        _, _, cls.tokens = load_system(ROOT / "design-systems" / "lumen", cls.schema)
        cls.paths = sorted((ROOT / "schemas" / "examples").rglob("*.json"))

    def test_connected_examples_validate(self):
        documents = [(path, validate_document(path, self.schema)) for path in self.paths]
        validate_bundle(documents, self.tokens)

    def test_invalid_component_property_is_rejected(self):
        documents = [(path, validate_document(path, self.schema)) for path in self.paths]
        for _, document in documents:
            if document["kind"] == "composition":
                document["bindings"]["source"]["properties"]["label"] = ""
        with self.assertRaisesRegex(ContractError, "invalid properties"):
            validate_bundle(documents, self.tokens)

    def test_missing_system_resource_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "lumen"
            root.mkdir()
            manifest = read_json(ROOT / "design-systems" / "lumen" / "system.json")
            (root / "system.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ContractError, "missing package resource"):
                load_system(root, self.schema)


if __name__ == "__main__":
    unittest.main()
