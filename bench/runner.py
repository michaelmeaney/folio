#!/usr/bin/env python3
"""Prepare, execute, inspect and compare repeatable Folio presentation benchmarks."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import posixpath
import re
import shutil
import signal
import statistics
import struct
import subprocess
import sys
import time
import unicodedata
import uuid
import zipfile
import zlib
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

BENCH = Path(__file__).resolve().parent
EXCLUDED = {'.git', '.venv', '__pycache__', 'node_modules', 'bench', 'outputs', 'tmp', 'dist', '.DS_Store'}
NS = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}


class BenchError(ValueError):
    pass


def load(path):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError) as exc:
        raise BenchError(f'{path}: {exc}') from exc


def write(path, data):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + '\n')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_digest(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


def stamp():
    return datetime.now(timezone.utc).isoformat()


def safe_file(root, relative):
    path = (root / relative).resolve()
    if Path(relative).is_absolute() or not path.is_relative_to(root.resolve()) or not path.is_file():
        raise BenchError(f'Missing or escaping file: {relative}')
    return path


def snapshot(source, destination):
    destination.mkdir()
    hashes = {}
    for path in sorted(source.rglob('*')):
        relative = path.relative_to(source)
        if any(part in EXCLUDED for part in relative.parts) or path.suffix == '.pyc':
            continue
        if path.is_symlink():
            raise BenchError(f'Plugin snapshot does not permit symlinks: {relative}')
        if path.is_file():
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            hashes[str(relative)] = digest(target)
    return hashes


def review_template(case, reference):
    pending = lambda: {'status': 'unverified', 'notes': '', 'evidence': []}
    return {'reviewer': '', 'contexts': {'generation': {'id': '', 'inheritance': ''}, 'review': {'id': '', 'inheritance': ''}}, 'runtime': {key: '' for key in ['model', 'effort', 'surface', 'renderer', 'application']},
            'deckSha256': '', 'renderSha256': {},
            'criteria': {criterion['id']: pending() for criterion in case['criteria']},
            'facts': {fact['id']: pending() for fact in reference['facts']}}


def selected_canvas(plugin, system):
    registry = load(plugin / 'design-systems/registry.json')
    match = next((entry for entry in registry['systems'] if entry['id'] == system), None)
    if not match:
        raise BenchError(f'Design system {system!r} is not registered in the tested plugin')
    manifest_path = safe_file(plugin / 'design-systems', match['manifest'])
    manifest = load(manifest_path)
    profile = manifest.get('resources', {}).get('presentation')
    if profile:
        canvas = load(safe_file(manifest_path.parent, profile))['canvas']
        return [canvas['width'], canvas['height']]
    tokens = load(safe_file(manifest_path.parent, manifest['tokens']))
    return [tokens['canvas']['widthIn'], tokens['canvas']['heightIn']]


def prepare(args):
    suite = load(BENCH / 'suite.json')
    reference = load(BENCH / suite['reference'])
    source = (Path(args.reference).expanduser().resolve() if args.reference else BENCH / reference['file'])
    if not source.is_file() or digest(source) != reference['sha256']:
        raise BenchError('Reference missing or changed. Supply the original --reference file; a new fixture needs a new benchmark version and reviewed ground truth.')
    raw = source.read_bytes()
    if raw[:8] != b'\x89PNG\r\n\x1a\n' or struct.unpack('>II', raw[16:24]) != (reference['width'], reference['height']):
        raise BenchError('Reference dimensions do not match the fixture')
    plugin = Path(args.plugin_root).expanduser().resolve()
    package = load(plugin / '.codex-plugin/plugin.json')
    if package.get('name') != 'folio':
        raise BenchError('The plugin under test must be Folio')
    cases = [case for case in suite['cases'] if not args.case or case['id'] in args.case]
    if not cases or (args.case and set(args.case) != {case['id'] for case in cases}):
        raise BenchError('Unknown or empty benchmark case selection')
    if not 1 <= args.repetitions <= 10:
        raise BenchError('Use 1 to 10 repetitions')
    canvas = selected_canvas(plugin, args.design_system) if any(c['mode'] == 'governed' for c in cases) else None
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
    run = Path(args.output).expanduser().resolve() if args.output else BENCH / 'runs' / run_id
    if run.is_relative_to(plugin) and not any(part in EXCLUDED for part in run.relative_to(plugin).parts):
        raise BenchError('Place results outside the tested plugin or under bench/runs to avoid recursive snapshots')
    if args.timeout <= 0:
        raise BenchError('Timeout must be positive')
    if run.exists():
        raise BenchError(f'Run already exists; use a fresh directory: {run}')
    run.mkdir(parents=True)
    inputs = run / 'inputs'
    inputs.mkdir()
    plugin_hashes = snapshot(plugin, inputs / 'plugin')
    shutil.copy2(source, inputs / 'reference.png')
    write(inputs / 'reference.json', reference)
    write(inputs / 'suite.json', suite)
    shutil.copy2(Path(__file__), inputs / 'runner.py')
    prompts = {case['id']: (BENCH / case['prompt']).read_text() for case in suite['cases']}
    write(inputs / 'prompts.json', prompts)
    commit = subprocess.run(['git', '-C', str(plugin), 'rev-parse', 'HEAD'], capture_output=True, text=True)
    trials = []
    for case in cases:
        for repetition in range(1, args.repetitions + 1):
            relative = f"cases/{case['id']}/r{repetition:02d}"
            trial = run / relative
            (trial / 'output').mkdir(parents=True)
            instruction = prompts[case['id']].replace('{{design_system}}', args.design_system)
            prompt = f'''# Folio benchmark: {case['id']}, repetition {repetition}

Read and execute the Folio Skill at {inputs / 'plugin/skills/folio/SKILL.md'}.
Use that frozen plugin copy and its declared resources as the version under test. Record any unavoidable fallback. Do not substitute another installed Folio version.
Reference image: {inputs / 'reference.png'}
Output directory: {trial / 'output'}

{instruction}
The operation, mode, selected system (where applicable), slide count and permissions in this benchmark brief are confirmed. Ask only if a genuine conflict blocks execution; record any intervention.

Start with fresh context and no inherited conversation (Codex subagents: fork_turns=none). Record your actual context ID and inheritance setting in execution notes. Do not inspect other trials, previous version outputs, reference.json, suite.json, review.json or this benchmark's reviewer answer key. Analyse the actual image before composing and preserve your analysis for review. Do not modify frozen inputs.
Produce output/deck.pptx and one actual rendered PNG at least 1280 pixels wide per slide at output/render/slide-01.png, slide-02.png, etc. Paths here are relative to {trial}.
Keep useful source-to-object metadata and reconstruction scripts in output/. Record actual model, effort, surface, renderer/application versions, repair rounds, interventions, time/token/cost observations when available, and unresolved issues in output/execution-notes.md. Mark unavailable measurements unobserved rather than estimating them. Do not fill in review.json or claim that benchmark acceptance follows from creating files.
'''
            (trial / 'prompt.md').write_text(prompt)
            review_prompt = f'''# Independent Folio benchmark review: {case['id']}, repetition {repetition}

Start a fresh review context with no inherited conversation. Evaluate only this trial.
Read {inputs / 'plugin/skills/folio/references/acceptance.md'}, the criterion descriptions in {inputs / 'suite.json'} for {case['id']}, and the answer key {inputs / 'reference.json'}.
Inspect the actual source image {inputs / 'reference.png'}, PowerPoint {trial / 'output/deck.pptx'}, every PNG in {trial / 'output/render'}, and execution evidence under {trial / 'output'}.
Fill {trial / 'review.json'} with observed results. Record actual generation and review context IDs and inheritance=none only when verified; they must be distinct. Verify the generation context and runtime from execution records, not prepared controls alone.
Set reviewer identity, actual model/effort/surface/renderer/application, and SHA-256 fingerprints of the delivered deck and renders. Each criterion and source fact needs pass/fail/unverified, concrete notes and evidence files with matching hashes. Evidence paths are relative to {trial}.
Test real application opening, rendering and claimed editing operations on a copy; record unavailable checks as unverified. Inspect visible text, relationships, composition, accessibility and narrative directly. Do not change the delivered deck to make it pass or treat generator claims as acceptance. Do not inspect other trial outputs or previous version results. Store review evidence under output/review/.
'''
            (trial / 'review-prompt.md').write_text(review_prompt)
            write(trial / 'review.json', review_template(case, reference))
            trials.append({'case': case['id'], 'repetition': repetition, 'path': relative,
                           'promptSha256': digest(trial / 'prompt.md'), 'reviewPromptSha256': digest(trial / 'review-prompt.md')})
    input_hashes = {str(p.relative_to(inputs)): digest(p) for p in inputs.rglob('*') if p.is_file() and 'plugin' not in p.relative_to(inputs).parts}
    record = {'schemaVersion': 1, 'id': run_id, 'createdAt': stamp(),
              'benchmark': {'id': suite['id'], 'version': suite['version'], 'sha256': canonical_digest({'suite':suite,'reference':reference,'prompts':prompts,'runner':digest(Path(__file__))})},
              'plugin': {'version': package['version'], 'source': str(plugin), 'commit': commit.stdout.strip() if commit.returncode == 0 else None,
                         'sha256': canonical_digest(plugin_hashes), 'files': plugin_hashes},
              'controls': {'model':args.model, 'effort':args.effort, 'surface':args.surface, 'context':'fresh',
                           'designSystem':args.design_system if canvas else None, 'repetitions':args.repetitions,
                           'timeoutSeconds':args.timeout, 'cases':[c['id'] for c in cases]},
              'systemCanvas': canvas, 'inputs': input_hashes, 'trials': trials}
    write(run / 'run.json', record)
    (run / 'run.sha256').write_text(digest(run / 'run.json') + '\n')
    print(json.dumps({'run': str(run), 'trials':len(trials), 'pluginVersion':package['version'], 'status':'prepared'}, indent=2))
    return 0


def verify_run(run):
    run = run.resolve()
    if digest(run / 'run.json') != (run / 'run.sha256').read_text().strip():
        raise BenchError('Run metadata changed after preparation')
    record = load(run / 'run.json')
    if record.get('schemaVersion') != 1:
        raise BenchError('Unsupported benchmark run format')
    for name, expected in record['inputs'].items():
        if digest(safe_file(run / 'inputs', name)) != expected:
            raise BenchError(f'Frozen input changed: {name}')
    root = run / 'inputs/plugin'
    if any(p.is_symlink() for p in root.rglob('*')):
        raise BenchError('Frozen plugin contains a symlink')
    actual = {str(p.relative_to(root)): digest(p) for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.relative_to(root).parts and p.suffix != '.pyc'}
    if actual != record['plugin']['files']:
        raise BenchError('Plugin under test changed after preparation')
    for trial in record['trials']:
        if digest(safe_file(run, trial['path'] + '/prompt.md')) != trial['promptSha256']:
            raise BenchError('Execution brief changed after preparation')
        if trial.get('reviewPromptSha256') and digest(safe_file(run, trial['path'] + '/review-prompt.md')) != trial['reviewPromptSha256']:
            raise BenchError('Review brief changed after preparation')
    return record


def stop_process(process):
    if os.name == 'posix':
        os.killpg(process.pid, signal.SIGKILL)
    else:
        process.kill()
    process.wait()


def execute(args):
    run = Path(args.run).resolve()
    record = verify_run(run)
    command = args.executor[1:] if args.executor[:1] == ['--'] else args.executor
    if not command:
        raise BenchError('Provide an executor argv after --; the prompt is sent on stdin')
    trials = [t for t in record['trials'] if not args.case or t['case'] == args.case]
    if not trials:
        raise BenchError('Unknown case')
    for item in trials:
        trial = run / item['path']
        if (trial / 'execution.json').exists() or any((trial / 'output').iterdir()):
            raise BenchError('Refusing to overwrite an attempted trial; prepare a new run')
    failures = 0
    for item in trials:
        verify_run(run)
        trial = run / item['path']
        replacements = {'{prompt}':str(trial/'prompt.md'), '{reference}':str(run/'inputs/reference.png'),
                        '{plugin}':str(run/'inputs/plugin'), '{output}':str(trial/'output')}
        argv = list(command)
        for key, value in replacements.items():
            argv = [arg.replace(key, value) for arg in argv]
        started, start_time = stamp(), time.monotonic()
        exit_code, timed_out = None, False
        with (trial/'stdout.log').open('w') as stdout, (trial/'stderr.log').open('w') as stderr:
            try:
                process = subprocess.Popen(argv, cwd=trial/'output', stdin=subprocess.PIPE, stdout=stdout, stderr=stderr,
                                           text=True, start_new_session=os.name == 'posix')
                try:
                    process.communicate((trial/'prompt.md').read_text(), timeout=record['controls']['timeoutSeconds'])
                    exit_code = process.returncode
                except subprocess.TimeoutExpired:
                    timed_out = True
                    stop_process(process)
                except KeyboardInterrupt:
                    stop_process(process)
                    write(trial/'execution.json', {'status':'cancelled','startedAt':started,'elapsedSeconds':time.monotonic()-start_time})
                    raise
            except OSError as exc:
                stderr.write(str(exc))
        execution = {'status':'completed' if exit_code == 0 else 'failed', 'startedAt':started, 'endedAt':stamp(),
                     'elapsedSeconds':round(time.monotonic()-start_time,3), 'exitCode':exit_code, 'timedOut':timed_out,
                     'command':argv, 'tokenUsage':None, 'cost':None, 'repairRounds':None, 'humanInterventions':None}
        write(trial/'execution.json', execution)
        failures += execution['status'] != 'completed'
        verify_run(run)
        print(f"{item['case']} r{item['repetition']}: {execution['status']} ({execution['elapsedSeconds']}s); acceptance requires review")
    return 1 if failures else 0


def normalise(text):
    return re.sub(r'[\W_]+', '', unicodedata.normalize('NFKC', text).casefold())


def inspect_pptx(path):
    try:
        with zipfile.ZipFile(path) as deck:
            if sum(info.file_size for info in deck.infolist()) > 250_000_000:
                raise BenchError('PowerPoint exceeds benchmark inspection size limit')
            presentation = ET.fromstring(deck.read('ppt/presentation.xml'))
            size = presentation.find('p:sldSz', NS)
            canvas = [int(size.attrib['cx']), int(size.attrib['cy'])]
            rels = ET.fromstring(deck.read('ppt/_rels/presentation.xml.rels'))
            targets = {r.attrib['Id']:r.attrib['Target'] for r in rels if r.attrib.get('Type','').endswith('/slide') and r.attrib.get('TargetMode') != 'External'}
            slides = []
            for sld in presentation.findall('p:sldIdLst/p:sldId', NS):
                target = targets[sld.attrib['{'+NS['r']+'}id']]
                name = posixpath.normpath('ppt/' + target) if not target.startswith('/') else target.lstrip('/')
                if not name.startswith('ppt/slides/'):
                    raise BenchError('Invalid slide relationship target')
                xml = ET.fromstring(deck.read(name))
                texts = [''.join(t.text or '' for t in p.findall('.//a:t', NS)) for p in xml.findall('.//a:p', NS)]
                text_shapes = sum(bool(sp.findall('.//a:t',NS)) for sp in xml.findall('.//p:sp',NS))
                connectors = xml.findall('.//p:cxnSp',NS)
                attached = sum(c.find('.//a:stCxn',NS) is not None and c.find('.//a:endCxn',NS) is not None for c in connectors)
                pictures = xml.findall('.//p:pic',NS)
                full_canvas = 0
                for picture in pictures:
                    ext = picture.find('.//a:xfrm/a:ext',NS)
                    if ext is not None and int(ext.attrib['cx']) * int(ext.attrib['cy']) >= .9 * canvas[0] * canvas[1]:
                        full_canvas += 1
                slides.append({'text':'\n'.join(texts), 'nativeTextShapes':text_shapes,
                               'nativeShapes':len(xml.findall('.//p:sp',NS)), 'connectors':len(connectors),
                               'attachedConnectors':attached, 'pictures':len(pictures), 'fullCanvasPictures':full_canvas})
            if not slides or min(canvas) <= 0:
                raise BenchError('PowerPoint has no slides or invalid canvas')
            return {'canvas':canvas, 'slideCount':len(slides), 'slides':slides}
    except (OSError, KeyError, AttributeError, ValueError, zipfile.BadZipFile, ET.ParseError) as exc:
        raise BenchError(f'Cannot inspect PowerPoint: {exc}') from exc


def inspect_png(path):
    data=Path(path).read_bytes()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise BenchError('Invalid PNG signature')
    offset, dimensions, image_data = 8, None, False
    while offset + 12 <= len(data):
        length=struct.unpack('>I',data[offset:offset+4])[0]
        kind=data[offset+4:offset+8]
        payload=data[offset+8:offset+8+length]
        end=offset+12+length
        if end>len(data) or zlib.crc32(kind+payload)&0xffffffff != struct.unpack('>I',data[end-4:end])[0]:
            raise BenchError('Invalid PNG chunk')
        if kind==b'IHDR':
            if offset!=8 or length!=13:
                raise BenchError('Invalid PNG header')
            dimensions=struct.unpack('>II',payload[:8])
        if kind==b'IDAT':
            image_data=True
        if kind==b'IEND':
            if dimensions and min(dimensions)>0 and image_data and end==len(data):
                return dimensions
            break
        offset=end
    raise BenchError('Incomplete PNG')


def check_evidence(trial, item):
    evidence = item.get('evidence', [])
    if not evidence or not item.get('notes','').strip():
        return False
    for entry in evidence:
        try:
            if digest(safe_file(trial, entry['path'])) != entry['sha256']:
                return False
        except (BenchError, KeyError, TypeError):
            return False
    return True


def check_trial(run, record, trial_entry, case, reference):
    trial = run / trial_entry['path']
    deck = trial / 'output/deck.pptx'
    execution = load(trial/'execution.json') if (trial/'execution.json').exists() else {}
    result = {'case':case['id'],'repetition':trial_entry['repetition'], 'status':'not-run',
              'automaticFailures':[], 'unverified':[], 'gateResults':{}, 'elapsedSeconds':execution.get('elapsedSeconds'),
              'tokenUsage':execution.get('tokenUsage'), 'cost':execution.get('cost'), 'runtime':None}
    review = load(trial/'review.json')
    runtime=review.get('runtime',{})
    if all(runtime.get(k,'').strip() for k in ['model','effort','surface','renderer','application']):
        if any(runtime[k] != record['controls'][k] for k in ['model','effort','surface']):
            result['automaticFailures'].append('Actual runtime differs from the controlled run')
        elif review.get('criteria',{}).get('runtime',{}).get('status')=='pass' and check_evidence(trial,review['criteria']['runtime']):
            result['runtime']=runtime
    if not deck.exists():
        if execution:
            result['status']='failed'
            result['automaticFailures'].append('Execution produced no output/deck.pptx')
        return result
    failures = result['automaticFailures']
    if execution and execution.get('status') != 'completed':
        failures.append('Executor did not complete successfully')
    try:
        metrics = inspect_pptx(deck)
    except BenchError as exc:
        result.update(status='failed',automaticFailures=[str(exc)])
        return result
    result['metrics'] = metrics
    if metrics['slideCount'] != case['slides']:
        failures.append(f"Expected {case['slides']} slides, found {metrics['slideCount']}")
    expected_canvas = [reference['width'], reference['height']] if case['mode']=='quick' else record['systemCanvas']
    if abs(metrics['canvas'][0]/metrics['canvas'][1] - expected_canvas[0]/expected_canvas[1]) > .0001:
        failures.append('Output canvas ratio differs from the case contract')
    if not all(s['nativeTextShapes'] for s in metrics['slides']):
        failures.append('Every slide must contain native editable text')
    if case['exactCopy']:
        text = normalise('\n'.join(s['text'] for s in metrics['slides']))
        missing = [block['id'] for block in reference['textBlocks'] if text.count(normalise(block['text'])) < block['minOccurrences']]
        if missing:
            failures.append('Missing native source text: '+', '.join(missing))
    renders = {f'output/render/slide-{i:02d}.png':trial/f'output/render/slide-{i:02d}.png' for i in range(1,case['slides']+1)}
    for path in renders.values():
        try:
            width,height=inspect_png(path)
            if width<1280 or abs(width/height - expected_canvas[0]/expected_canvas[1]) > .01:
                failures.append('Render resolution or aspect ratio differs from the case contract')
        except (OSError,BenchError):
            failures.append('Missing or invalid per-slide PNG render: '+path.name)
    review = load(trial/'review.json')
    contexts=review.get('contexts',{})
    ids=[contexts.get(role,{}).get('id','').strip() for role in ['generation','review']]
    if not all(ids) or any(contexts.get(role,{}).get('inheritance')!='none' for role in ['generation','review']):
        result['unverified'].append('Fresh generation and independent review contexts are required')
    elif ids[0]==ids[1]:
        failures.append('Generation and review reused the same context')
    result['contextIds']=ids
    required_runtime = ['model','effort','surface','renderer','application']
    if not review.get('reviewer','').strip() or not all(review.get('runtime',{}).get(k,'').strip() for k in required_runtime):
        result['unverified'].append('Reviewer identity and actual runtime are required')
    elif any(review['runtime'][k] != record['controls'][k] for k in ['model','effort','surface']):
        failures.append('Actual model, effort or surface differs from the controlled run')
    if review.get('deckSha256') != digest(deck) or any(review.get('renderSha256',{}).get(name) != digest(path) for name,path in renders.items() if path.is_file()):
        result['unverified'].append('Review is not fingerprinted to the delivered PowerPoint and renders')
    for gate in ['content','composition','treatment','artefact']:
        entries = [(c['id'],review.get('criteria',{}).get(c['id'],{})) for c in case['criteria'] if c['gate']==gate]
        if gate=='content':
            entries += [('fact:'+f['id'], review.get('facts',{}).get(f['id'],{})) for f in reference['facts']]
        statuses = []
        for identity, item in entries:
            status = item.get('status','unverified')
            if status == 'pass' and not check_evidence(trial,item):
                status='unverified'
            if status not in ('pass','fail'):
                status='unverified'
                result['unverified'].append(identity)
            statuses.append(status)
        result['gateResults'][gate] = 'fail' if 'fail' in statuses else 'unverified' if 'unverified' in statuses else 'pass'
    result['status'] = ('failed' if failures or 'fail' in result['gateResults'].values() else
                        'partial' if result['unverified'] else 'accepted')
    return result


def report(run):
    record=verify_run(run)
    suite=load(run/'inputs/suite.json')
    reference=load(run/'inputs/reference.json')
    cases={c['id']:c for c in suite['cases']}
    results=[check_trial(run,record,t,cases[t['case']],reference) for t in record['trials']]
    seen={}
    for result in results:
        for context_id in result.get('contextIds',[]):
            if context_id:
                seen.setdefault(context_id,[]).append(result)
    for rows in seen.values():
        if len(rows)>1:
            for result in rows:
                result['status']='failed'
                result['automaticFailures'].append('A context was reused across benchmark tasks')
    summary={}
    for case in record['controls']['cases']:
        trials=[r for r in results if r['case']==case]
        times=[r['elapsedSeconds'] for r in trials if r['status']=='accepted' and r['elapsedSeconds'] is not None]
        summary[case]={'accepted':sum(t['status']=='accepted' for t in trials),'total':len(trials),
                       'medianAcceptedSeconds':statistics.median(times) if times else None}
    result={'run':record['id'],'pluginVersion':record['plugin']['version'],'generatedAt':stamp(),'results':results,'summary':summary}
    write(run/'report.json',result)
    write_html(run,record,result)
    return record,result


def write_html(run, record, result):
    escape=html.escape
    sections=[]
    for trial, row in zip(record['trials'],result['results']):
        images=[]
        for png in sorted((run/trial['path']/'output/render').glob('slide-*.png')):
            images.append(f'<img src="{escape(png.relative_to(run).as_posix(),quote=True)}" alt="{escape(png.stem)}">')
        deck=trial['path']+'/output/deck.pptx'
        sections.append(f'<section><h2>{escape(row["case"])} · repetition {row["repetition"]} · {escape(row["status"])}</h2><a href="{escape(deck,quote=True)}">PowerPoint</a><p>{escape("; ".join(row["automaticFailures"]))}</p>{"".join(images)}<details><summary>Gate results and missing evidence</summary><pre>{escape(json.dumps({"gates":row["gateResults"],"unverified":row["unverified"]},indent=2))}</pre></details></section>')
    document='<!doctype html><meta charset="utf-8"><title>Folio benchmark</title><style>body{font:16px system-ui;max-width:1200px;margin:40px auto;padding:0 24px;color:#18212b}img{width:100%;height:auto;border:1px solid #bbb}section{margin:40px 0;border-top:1px solid #aaa}pre{white-space:pre-wrap}a{color:#174d9c}</style>'
    document+=f'<h1>Folio {escape(record["plugin"]["version"])} benchmark</h1><p>{escape(record["id"])} · Actual output and reviewer evidence determine acceptance.</p><h2>Source reference</h2><img src="inputs/reference.png" alt="Benchmark source">'+''.join(sections)
    (run/'report.html').write_text(document)


def check(args):
    _, result=report(Path(args.run).resolve())
    print(json.dumps(result['summary'],indent=2))
    return 0 if all(r['status']=='accepted' for r in result['results']) else 1


def compare(args):
    left, before=report(Path(args.baseline).resolve())
    right, after=report(Path(args.candidate).resolve())
    if left['benchmark'] != right['benchmark'] or left['controls'] != right['controls']:
        raise BenchError('Runs are not comparable: benchmark, source, prompts or controlled settings differ')
    if any(r['status'] in ('not-run','partial') for r in before['results']+after['results']):
        raise BenchError('Complete execution and review before comparing plugin versions')
    for case in left['controls']['cases']:
        profiles=[]
        for report_data in [before,after]:
            rows=[r for r in report_data['results'] if r['case']==case]
            if any(r['runtime'] is None for r in rows):
                raise BenchError('Verify actual runtime for every attempted trial, including failures')
            profiles.append({canonical_digest(r['runtime']) for r in rows})
        if len(profiles[0]) != 1 or profiles[0] != profiles[1]:
            raise BenchError('Actual runtime/renderer/application differ within or between runs')
    comparisons={key:{'baseline':before['summary'][key],'candidate':after['summary'][key],
                      'acceptedDelta':after['summary'][key]['accepted']-before['summary'][key]['accepted']} for key in before['summary']}
    print(json.dumps({'baseline':left['plugin']['version'],'candidate':right['plugin']['version'], 'cases':comparisons},indent=2))
    return 1 if any(row['acceptedDelta']<0 for row in comparisons.values()) else 0


def parser():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='command',required=True)
    prep=sub.add_parser('prepare',help='Freeze inputs and prepare isolated trial briefs; does not call a model')
    prep.add_argument('--plugin-root',required=True)
    prep.add_argument('--reference')
    prep.add_argument('--output')
    prep.add_argument('--model',required=True)
    prep.add_argument('--effort',required=True)
    prep.add_argument('--surface',required=True)
    prep.add_argument('--design-system',default='lumen')
    prep.add_argument('--repetitions',type=int,default=1)
    prep.add_argument('--timeout',type=int,default=1200)
    prep.add_argument('--case',action='append',choices=['quick-convert','governed-restyle','governed-story'])
    prep.set_defaults(handler=prepare)
    run=sub.add_parser('run',help='Launch one fresh executor process per trial; takes prompt on stdin')
    run.add_argument('run')
    run.add_argument('--case',choices=['quick-convert','governed-restyle','governed-story'])
    run.add_argument('--executor',nargs=argparse.REMAINDER,required=True)
    run.set_defaults(handler=execute)
    chk=sub.add_parser('check',help='Inspect actual decks and evidence; emit report.json')
    chk.add_argument('run');chk.set_defaults(handler=check)
    comp=sub.add_parser('compare',help='Compare fully reviewed runs with identical controls')
    comp.add_argument('baseline');comp.add_argument('candidate');comp.set_defaults(handler=compare)
    return p


def main():
    args=parser().parse_args()
    try:
        return args.handler(args)
    except (BenchError,OSError,KeyError,TypeError,ValueError) as exc:
        print(f'Benchmark error: {exc}',file=sys.stderr)
        return 2


if __name__=='__main__':
    raise SystemExit(main())
