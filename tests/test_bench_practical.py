"""Practical review policy tests use the synthetic benchmark fixture."""
import importlib.util
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
import test_folio_bench as fixtures
bench = fixtures.bench
spec = importlib.util.spec_from_file_location('presentation_evaluator', ROOT / 'bench/evaluators/presentation.py')
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)

class PracticalTests(unittest.TestCase):
    setUp = fixtures.BenchmarkTests.setUp
    prepare = fixtures.BenchmarkTests.prepare
    deliver = fixtures.BenchmarkTests.deliver
    approve = fixtures.BenchmarkTests.approve
    def practical(self):
        self.deliver(); self.approve()
        self.case['reviewPolicy'] = 'practical-v1'
        for c in self.case['criteria']:
            c['dimension'] = {'copy':'content-meaning','layout':'visual-fidelity','style':'accessibility','runtime':'verification','editing':'editability'}[c['id']]
            c['advisory'] = c['id'] in ('style','runtime')
        self.reference['regions'] = [{'id':'drawing','purpose':'illustrative'}, {'id':'system','purpose':'technical'}]
        return {'schemaVersion':1, 'runDirectory':str(self.run), 'trialDirectory':str(self.trial), 'trialPath':'cases/quick-convert/r01', 'case':self.case, 'reference':self.reference, 'controls':{'model':'test-model','effort':'medium','surface':'test'}, 'systemCanvas':[16,9]}

    def change(self, key, **fields):
        r = bench.load(self.trial/'review.json')
        r['criteria'][key].update(fields)
        bench.write(self.trial/'review.json', r)

    def test_minor_illustration_and_accessibility_are_separate(self):
        data = self.practical()
        self.change('layout', status='fail', severity='minor', purpose='illustrative', region='drawing')
        self.change('style', status='fail')
        r = adapter.evaluate(data)
        self.assertEqual(r['status'], 'pass')
        self.assertEqual(r['dimensions']['visual-fidelity'], 'pass')
        self.assertEqual(r['dimensions']['accessibility'], 'needs-work')
        self.assertEqual(r['diagnostics']['fullAcceptanceStatus'], 'failed')
        self.assertEqual(len(r['observations']), 2)

    def test_technical_failure_cannot_be_minor_illustration(self):
        data = self.practical()
        self.change('layout', status='fail', severity='minor', purpose='illustrative', region='system')
        self.assertEqual(adapter.evaluate(data)['status'], 'fail')

    def test_connector_attachment_opt_in(self):
        data = self.practical()
        self.assertEqual(adapter.evaluate(data)['status'], 'pass')
        data['case']['requireAttachedConnectors'] = True
        self.assertEqual(adapter.evaluate(data)['status'], 'unverified')

    def test_missing_source_text_still_blocks(self):
        data = self.practical()
        from test_folio_bench import pptx
        pptx(self.trial/'output/deck.pptx', text='missing content')
        self.approve()
        self.assertEqual(adapter.evaluate(data)['status'], 'fail')

    def test_stale_review_cannot_pass(self):
        data = self.practical()
        (self.trial/'output/evidence.md').write_text('changed')
        self.assertEqual(adapter.evaluate(data)['status'], 'unverified')
