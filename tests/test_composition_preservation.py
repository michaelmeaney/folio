"""Synthetic regression tests: these do not claim to render or edit a PowerPoint."""
from __future__ import annotations

import copy
import json
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from jsonschema import Draft202012Validator
from folio_schema import ContractError, read_json, validate_bundle, validate_document
from folio_preservation import baseline_digest, file_digest


class CompositionPreservationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / 'run'
        shutil.copytree(ROOT / 'tests/fixtures/composition', self.root)
        self.schema = read_json(ROOT / 'schemas/folio-0.1.0.schema.json')
        self.spec = read_json(self.root / 'specification.json')
        self.scene = read_json(self.root / 'scene.json')
        self.result = read_json(self.root / 'result.json')
        self.tokens = {'color.background': {}, 'typography.body': {}}

    def validate(self, refresh_baseline=False):
        if refresh_baseline:
            self.scene['preservation']['baselineSha256'] = baseline_digest(self.spec)
        docs = []
        for name, value in [('specification', self.spec), ('scene', self.scene), ('result', self.result)]:
            path = self.root / (name + '.json')
            path.write_text(json.dumps(value))
            docs.append((path, validate_document(path, self.schema)))
        validate_bundle(docs, self.tokens)

    def output(self, identity):
        return next(o for o in self.scene['objects'] if o['id'] == identity)

    def authorise(self, permission, source_ids):
        self.spec['intent']['permissions'][permission] = True
        self.spec['intent']['authorizationRef'] = 'confirmed-user-request'
        self.spec['deviations'].append({'id':permission, 'permission':permission, 'sourceIds':source_ids,
                                     'reason':'Explicit test scope', 'authorizationRef':'confirmed-user-request'})
        self.result['intent'] = copy.deepcopy(self.spec['intent'])

    def accepted_record(self):
        # Fabricated package/evidence for validator unit tests only. No host claim is made.
        with zipfile.ZipFile(self.root / 'deck.pptx', 'w') as deck:
            for name in ['[Content_Types].xml', 'ppt/presentation.xml', 'ppt/slides/slide1.xml']:
                deck.writestr(name, '<synthetic-unit-test/>')
        (self.root / 'final.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
        (self.root / 'review.txt').write_text('Synthetic test evidence, not an actual visual or editing review.')
        def evidence(name):
            return {'path':name,'sha256':file_digest(self.root / name)}
        self.result.update(status='accepted', unresolved=[], artefacts={'pptx':'deck.pptx','render':'final.svg'})
        for gate in self.result['gates'].values():
            gate.update(status='pass', evidence=[evidence('review.txt')])
        self.result['gates']['composition']['evidence'] += [evidence('source.svg'), evidence('final.svg')]
        self.result['gates']['artefact']['evidence'] += [evidence('deck.pptx'), evidence('final.svg')]
        self.result['editingChecks'] = [{'operation':op,'status':'pass','application':'synthetic-test-host','version':'0',
                                        'evidence':[evidence('review.txt')]} for op in ['text','shapeGeometry','attachConnectors']]

    def test_schema_snapshots_are_valid(self):
        for version in ['0.1.0', '0.2.0']:
            Draft202012Validator.check_schema(read_json(ROOT / 'schemas' / f'folio-{version}.schema.json'))

    def test_restyle_preserves_integrated_architecture(self):
        self.validate()

    def test_empty_reference_analysis_is_rejected(self):
        self.spec['regions'] = []
        with self.assertRaises(ContractError):
            self.validate(True)

    def test_title_expansion_and_primary_visual_shrink_are_rejected(self):
        for identity, size in [('title-shape', 250), ('architecture-shape', 40)]:
            with self.subTest(identity=identity):
                saved = copy.deepcopy(self.scene)
                self.output(identity)['frame']['height'] = size
                if identity.startswith('architecture'):
                    self.output('architecture-label')['frame']['height'] = 20
                with self.assertRaisesRegex(ContractError, 'geometry'):
                    self.validate()
                self.scene = saved

    def test_one_to_many_native_objects_are_valid(self):
        clone = copy.deepcopy(self.output('architecture-shape'))
        clone['id'] = 'architecture-detail'
        clone['frame'] = {'x':500,'y':200,'width':50,'height':50}
        self.scene['objects'].append(clone)
        next(r for r in self.scene['preservation']['regions'] if r['regionId']=='architecture')['objectIds'].append(clone['id'])
        self.validate()

    def test_parallel_route_omission_is_rejected(self):
        self.scene['preservation']['relationships'] = [r for r in self.scene['preservation']['relationships'] if r['relationshipId']!='inference-route']
        self.scene['objects'] = [o for o in self.scene['objects'] if o['id'] not in ('inference-route','inference-route-label')]
        with self.assertRaisesRegex(ContractError, 'omitted'):
            self.validate()

    def test_distinct_source_routes_cannot_collapse_onto_one_connector(self):
        relation = copy.deepcopy(self.spec['relationships'][0])
        relation['id'] = 'second-structured-route'
        self.spec['relationships'].append(relation)
        mapping = copy.deepcopy(self.scene['preservation']['relationships'][0])
        mapping['relationshipId'] = relation['id']
        self.scene['preservation']['relationships'].append(mapping)
        with self.assertRaisesRegex(ContractError, 'relationship consolidation'):
            self.validate(True)

    def test_resolving_connector_can_still_express_wrong_relationship(self):
        self.output('inference-route')['target'] = 'editable-shape'
        with self.assertRaisesRegex(ContractError, 'endpoint differs'):
            self.validate()

    def test_relationship_direction_type_and_labels_are_protected(self):
        for key, value in [('directed',False), ('type','illustrative'), ('label','invented')]:
            with self.subTest(key=key):
                saved = copy.deepcopy(self.scene)
                self.output('inference-route')['relationship'][key] = value
                with self.assertRaisesRegex(ContractError, 'meaning'):
                    self.validate()
                self.scene = saved
        self.output('inference-route-label')['text'] = ''
        with self.assertRaisesRegex(ContractError, 'label'):
            self.validate()

    def test_visible_text_cannot_move_to_notes_or_detail_slides(self):
        self.output('architecture-label')['text'] = ''
        with self.assertRaisesRegex(ContractError, 'visible content'):
            self.validate()
        self.output('architecture-label')['text'] = 'Architecture canvas'
        self.scene['slideIndex'] = 2
        with self.assertRaisesRegex(ContractError, 'another slide'):
            self.validate()

    def test_unattached_line_cannot_claim_connector_attachment(self):
        self.output('inference-route')['type'] = 'line'
        with self.assertRaisesRegex(ContractError, 'only a connector'):
            self.validate()

    def test_editable_line_with_honest_capability_is_valid(self):
        self.output('inference-route')['type'] = 'line'
        self.output('inference-route')['editing'] = []
        self.validate()

    def test_authorised_redesign_can_move_regions(self):
        self.spec['intent']['operation'] = 'redesign'
        self.authorise('recompose',['structured'])
        self.output('structured-shape')['frame']['x'] += 30
        self.output('structured-label')['frame']['x'] += 30
        self.validate(True)

    def test_redesign_without_scoped_deviation_does_not_waive_fidelity(self):
        self.spec['intent'].update(operation='redesign',authorizationRef='confirmed-user-request')
        self.spec['intent']['permissions']['recompose'] = True
        self.output('structured-shape')['frame']['x'] += 100
        with self.assertRaisesRegex(ContractError, 'geometry'):
            self.validate(True)

    def test_restyle_cannot_silently_enable_recomposition(self):
        self.authorise('recompose',['structured'])
        with self.assertRaisesRegex(ContractError, 'Redesign intent'):
            self.validate(True)

    def test_baseline_cannot_be_rewritten_after_generation(self):
        self.spec['regions'][0]['tolerance']['height'] = 1
        with self.assertRaisesRegex(ContractError, 'baseline digest'):
            self.validate()

    def test_source_image_cannot_change_after_analysis(self):
        (self.root/'source.svg').write_text('changed')
        with self.assertRaisesRegex(ContractError, 'source image digest'):
            self.validate()

    def test_missing_trace_and_duplicate_region_ids_are_rejected(self):
        self.spec['regions'].append(copy.deepcopy(self.spec['regions'][0]))
        with self.assertRaisesRegex(ContractError, 'duplicate source region'):
            self.validate(True)

    def test_functional_output_cannot_be_added_without_trace(self):
        extra = copy.deepcopy(self.output('title-shape'));extra['id']='extra'
        self.scene['objects'].append(extra)
        with self.assertRaisesRegex(ContractError, 'lack source traceability'):
            self.validate()

    def test_reading_order_changes_are_rejected(self):
        self.scene['readingOrder'].reverse()
        with self.assertRaisesRegex(ContractError, 'reading order changed'):
            self.validate()

    def test_new_primary_visual_requires_permission(self):
        self.scene['preservation']['primaryRegion']='editable'
        with self.assertRaisesRegex(ContractError, 'primary visual replaced'):
            self.validate()

    def test_missing_host_tests_remain_partial(self):
        self.validate()
        self.result['status']='accepted'
        with self.assertRaises(ContractError):
            self.validate()

    def test_all_four_gates_are_non_compensating(self):
        self.accepted_record()
        for name in self.result['gates']:
            with self.subTest(gate=name):
                self.result['gates'][name]['status']='unverified'
                with self.assertRaises(ContractError):
                    self.validate()
                self.result['gates'][name]['status']='pass'

    def test_accepted_bookkeeping_requires_current_evidence_and_host_claims(self):
        self.accepted_record()
        self.validate()
        self.result['editingChecks'] = [c for c in self.result['editingChecks'] if c['operation']!='attachConnectors']
        with self.assertRaisesRegex(ContractError, 'lack host editing tests'):
            self.validate()
        self.accepted_record()
        (self.root/'review.txt').write_text('stale evidence')
        with self.assertRaisesRegex(ContractError, 'evidence digest mismatch'):
            self.validate()

    def test_accepted_output_requires_actual_artefact_references(self):
        self.accepted_record()
        (self.root/'deck.pptx').unlink()
        with self.assertRaisesRegex(ContractError, 'missing or escaping'):
            self.validate()

    def test_accepted_comparison_includes_source_and_render(self):
        self.accepted_record()
        self.result['gates']['composition']['evidence'] = self.result['gates']['composition']['evidence'][:1]
        with self.assertRaisesRegex(ContractError, 'source and final render'):
            self.validate()

    def test_accepted_output_cannot_hide_material_source_ambiguity(self):
        self.accepted_record()
        self.spec['relationships'][0]['ambiguity']='Could be illustrative or technical'
        with self.assertRaisesRegex(ContractError, 'ambiguity'):
            self.validate(True)

    def test_accepted_output_cannot_drop_a_source_slide(self):
        self.accepted_record()
        self.spec['sourceSlideCount']=2
        with self.assertRaisesRegex(ContractError, 'slide count'):
            self.validate(True)

    def test_legacy_records_remain_readable(self):
        validate_document(ROOT/'schemas/examples/visual-specification.json',self.schema)
        validate_document(ROOT/'schemas/examples/execution-result.json',self.schema)

    def test_mixed_versions_resolve_from_either_entry_schema(self):
        newer = read_json(ROOT/'schemas/folio-0.2.0.schema.json')
        validate_document(ROOT/'schemas/examples/components/database.json', newer)
        validate_document(self.root/'specification.json', self.schema)

    def test_unknown_schema_version_is_rejected(self):
        self.spec['schemaVersion']='9.0.0'
        with self.assertRaisesRegex(ContractError, 'unsupported schemaVersion'):
            self.validate()


if __name__ == '__main__':
    unittest.main()
