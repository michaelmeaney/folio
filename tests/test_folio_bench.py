"""Harness tests use synthetic files, never the private benchmark reference."""
import argparse
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('folio_bench', ROOT / 'bench/runner.py')
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)


def png(path, width=1600, height=900):
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress((b'\0' + b'\xff' * width * 3) * height)) + chunk(b'IEND', b''))


def pptx(path, text='Required source text', native=True):
    p, a, r = (bench.NS[k] for k in ('p', 'a', 'r'))
    with zipfile.ZipFile(path, 'w') as deck:
        deck.writestr('ppt/presentation.xml', f'<p:presentation xmlns:p="{p}" xmlns:r="{r}"><p:sldIdLst><p:sldId id="256" r:id="rId1"/></p:sldIdLst><p:sldSz cx="16000000" cy="9000000"/></p:presentation>')
        deck.writestr('ppt/_rels/presentation.xml.rels', f'<Relationships><Relationship Id="rId1" Type="{r}/slide" Target="slides/slide2.xml"/></Relationships>')
        body = f'<p:sp><p:txBody><a:p><a:r><a:t>{text}</a:t></a:r></a:p></p:txBody></p:sp>' if native else '<p:pic><p:spPr><a:xfrm><a:ext cx="16000000" cy="9000000"/></a:xfrm></p:spPr></p:pic>'
        deck.writestr('ppt/slides/slide2.xml', f'<p:sld xmlns:p="{p}" xmlns:a="{a}"><p:cSld><p:spTree>{body}</p:spTree></p:cSld></p:sld>')
        deck.writestr('ppt/slides/slide99.xml', 'orphan must not be counted')


class BenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.fixture = self.root / 'bench'
        self.fixture.mkdir()
        png(self.fixture / 'source.png')
        self.reference = {'file':'source.png', 'sha256':bench.digest(self.fixture/'source.png'), 'width':1600, 'height':900,
                          'facts':[{'id':'fact','statement':'Required source text'}],
                          'textBlocks':[{'id':'text','text':'Required source text','minOccurrences':1}]}
        self.case = {'id':'quick-convert','mode':'quick','slides':1,'exactCopy':True,'prompt':'prompt.md',
                     'criteria':[{'id':key,'gate':gate} for key,gate in [('copy','content'),('layout','composition'),('style','treatment'),('runtime','artefact'),('editing','artefact')]]}
        bench.write(self.fixture/'reference.json', self.reference)
        bench.write(self.fixture/'suite.json', {'id':'test','version':'1','reference':'reference.json','cases':[self.case]})
        (self.fixture/'prompt.md').write_text('Convert the source.')
        self.plugin = self.root/'plugin'
        (self.plugin/'.codex-plugin').mkdir(parents=True)
        (self.plugin/'skills/folio').mkdir(parents=True)
        bench.write(self.plugin/'.codex-plugin/plugin.json', {'name':'folio','version':'1.0.0'})
        (self.plugin/'skills/folio/SKILL.md').write_text('Synthetic test skill')
        self.run = self.root/'run'
        self.patcher = patch.object(bench, 'BENCH', self.fixture)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.prepare(self.run)
        self.trial = self.run/'cases/quick-convert/r01'

    def prepare(self, output):
        args=argparse.Namespace(reference=None,plugin_root=str(self.plugin),case=None,repetitions=1,design_system='lumen',output=str(output),timeout=2,model='test-model',effort='medium',surface='test')
        with contextlib.redirect_stdout(io.StringIO()):
            bench.prepare(args)

    def result(self):
        return bench.report(self.run)[1]['results'][0]

    def deliver(self):
        pptx(self.trial/'output/deck.pptx')
        png(self.trial/'output/render/slide-01.png')

    def approve(self):
        review=bench.load(self.trial/'review.json')
        evidence=self.trial/'output/evidence.md'
        evidence.write_text('Synthetic test review evidence, not a real presentation acceptance.')
        review.update(reviewer='test reviewer',contexts={'generation':{'id':str(self.trial)+'-generation','inheritance':'none'},'review':{'id':str(self.trial)+'-review','inheritance':'none'}},runtime={'model':'test-model','effort':'medium','surface':'test','renderer':'test 1','application':'test 1'},deckSha256=bench.digest(self.trial/'output/deck.pptx'),renderSha256={'output/render/slide-01.png':bench.digest(self.trial/'output/render/slide-01.png')})
        for group in ('criteria','facts'):
            for key in review[group]:
                review[group][key]={'status':'pass','notes':'Test evidence','evidence':[{'path':'output/evidence.md','sha256':bench.digest(evidence)}]}
        bench.write(self.trial/'review.json',review)

    def test_prepared_is_not_run(self):
        self.assertEqual(self.result()['status'],'not-run')

    def test_outputs_without_review_are_partial(self):
        self.deliver()
        self.assertEqual(self.result()['status'],'partial')

    def test_evidence_required_and_stale_evidence_rejected(self):
        self.deliver(); self.approve()
        self.assertEqual(self.result()['status'],'accepted')
        (self.trial/'output/evidence.md').write_text('changed')
        self.assertEqual(self.result()['status'],'partial')

    def test_each_gate_is_independent(self):
        self.deliver(); self.approve()
        review=bench.load(self.trial/'review.json')
        review['criteria']['layout']['status']='fail'
        bench.write(self.trial/'review.json',review)
        self.assertEqual(self.result()['status'],'failed')

    def test_missing_native_copy_fails(self):
        self.deliver()
        pptx(self.trial/'output/deck.pptx', text='Missing required facts')
        self.approve()
        self.assertEqual(self.result()['status'],'failed')

    def test_image_only_fails_and_orphans_are_ignored(self):
        self.deliver()
        pptx(self.trial/'output/deck.pptx',native=False)
        result=self.result()
        self.assertEqual(result['status'],'failed')
        self.assertEqual(result['metrics']['slideCount'],1)
        self.assertEqual(result['metrics']['slides'][0]['fullCanvasPictures'],1)

    def test_plugin_and_prompt_are_frozen(self):
        frozen=self.run/'inputs/plugin/skills/folio/SKILL.md'
        original=frozen.read_text()
        frozen.write_text('changed')
        with self.assertRaises(bench.BenchError): bench.verify_run(self.run)
        frozen.write_text(original)
        (self.trial/'prompt.md').write_text('changed')
        with self.assertRaises(bench.BenchError): bench.verify_run(self.run)

    def test_png_crc_and_truncation(self):
        path=self.fixture/'source.png'
        self.assertEqual(bench.inspect_png(path),(1600,900))
        path.write_bytes(path.read_bytes()[:-8])
        with self.assertRaises(bench.BenchError): bench.inspect_png(path)

    def test_evidence_cannot_escape_trial(self):
        item={'notes':'test','evidence':[{'path':'../../../inputs/reference.png','sha256':bench.digest(self.run/'inputs/reference.png')}]}
        self.assertFalse(bench.check_evidence(self.trial,item))

    def test_executor_exit_zero_does_not_mean_acceptance_and_no_overwrite(self):
        args=argparse.Namespace(run=str(self.run),case=None,executor=[sys.executable,'-c','import sys; assert "Convert the source" in sys.stdin.read()'])
        with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(bench.execute(args),0)
        self.assertEqual(self.result()['status'],'failed')
        with self.assertRaises(bench.BenchError): bench.execute(args)

    def test_reused_or_missing_context_is_not_accepted(self):
        self.deliver(); self.approve()
        review=bench.load(self.trial/'review.json')
        review['contexts']['review']['id']=review['contexts']['generation']['id']
        bench.write(self.trial/'review.json',review)
        self.assertEqual(self.result()['status'],'failed')
        review['contexts']={}
        bench.write(self.trial/'review.json',review)
        self.assertEqual(self.result()['status'],'partial')

    def test_review_brief_is_frozen(self):
        (self.trial/'review-prompt.md').write_text('changed')
        with self.assertRaises(bench.BenchError): bench.verify_run(self.run)

    def test_external_evaluator_preserves_legacy_judgment(self):
        adapter_spec=importlib.util.spec_from_file_location('presentation_adapter',ROOT/'bench/evaluators/presentation.py')
        adapter=importlib.util.module_from_spec(adapter_spec)
        adapter_spec.loader.exec_module(adapter)
        data={'schemaVersion':1,'runDirectory':str(self.run),'trialDirectory':str(self.trial),
              'trialPath':'cases/quick-convert/r01','case':self.case,'reference':self.reference,
              'controls':bench.load(self.run/'run.json')['controls'],'systemCanvas':[16,9]}
        self.deliver()
        self.assertEqual(adapter.evaluate(data)['status'],'unverified')
        self.approve()
        self.assertEqual(adapter.evaluate(data)['status'],'pass')
        review=bench.load(self.trial/'review.json')
        review['criteria']['layout']['status']='fail'
        bench.write(self.trial/'review.json',review)
        self.assertEqual(adapter.evaluate(data)['status'],'fail')

    def test_wrong_runtime_fails(self):
        self.deliver(); self.approve()
        review=bench.load(self.trial/'review.json')
        review['runtime']['model']='different-model'
        bench.write(self.trial/'review.json',review)
        self.assertEqual(self.result()['status'],'failed')

    def test_compare_rejects_incomplete_and_detects_regression(self):
        candidate=self.root/'candidate'
        self.prepare(candidate)
        args=argparse.Namespace(baseline=str(self.run),candidate=str(candidate))
        with self.assertRaises(bench.BenchError): bench.compare(args)
        self.deliver(); self.approve()
        oldtrial=self.trial
        self.trial=candidate/'cases/quick-convert/r01'
        self.deliver(); self.approve()
        with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(bench.compare(args),0)
        review=bench.load(self.trial/'review.json')
        review['criteria']['editing']['status']='fail'
        bench.write(self.trial/'review.json',review)
        with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(bench.compare(args),1)
        self.trial=oldtrial


if __name__ == '__main__':
    unittest.main()
