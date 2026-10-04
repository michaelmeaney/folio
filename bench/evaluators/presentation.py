#!/usr/bin/env python3
"""Evaluation protocol adapter. Go owns execution; legacy Python owns judgment."""
import importlib.util
import json
from pathlib import Path
import sys

spec = importlib.util.spec_from_file_location('folio_legacy_evaluation', Path(__file__).resolve().parents[1] / 'runner.py')
legacy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(legacy)


def practical_review(data, strict):
    """Keep full acceptance evidence while grading the declared practical milestone."""
    trial = Path(data['trialDirectory'])
    review = legacy.load(trial / 'review.json')
    dimensions = {name: [] for name in ('visual-fidelity', 'content-meaning', 'editability', 'accessibility', 'verification')}
    violations, observations = [], []
    regions = {r['id']: r for r in data['reference'].get('regions', [])}

    def assess(identity, item, dimension, advisory=False):
        status = item.get('status', 'unverified')
        if status not in ('pass', 'fail') or not legacy.check_evidence(trial, item):
            status = 'unverified'
        minor = (status == 'fail' and item.get('severity') == 'minor'
                 and dimension == 'visual-fidelity'
                 and regions.get(item.get('region'), {}).get('purpose') == 'illustrative'
                 and item.get('purpose') == 'illustrative')
        if minor:
            observations.append({'id': identity, 'message': item.get('notes', 'Minor illustrative difference')})
            status = 'pass'
        dimensions[dimension].append(status)
        if status == 'fail':
            entry = {'id': identity, 'message': item.get('notes', 'Review requirement needs work')}
            (observations if advisory else violations).append(entry)

    for criterion in data['case']['criteria']:
        assess(criterion['id'], review.get('criteria', {}).get(criterion['id'], {}),
               criterion['dimension'], criterion.get('advisory', False))
    for fact in data['reference']['facts']:
        assess('fact:' + fact['id'], review.get('facts', {}).get(fact['id'], {}), 'content-meaning')
    for message in strict['automaticFailures']:
        if 'runtime' in message or 'model, effort or surface' in message:
            observations.append({'id': 'runtime-verification', 'message': message})
            dimensions['verification'].append('unverified')
        else:
            violations.append({'id': 'automatic', 'message': message})
            dimensions['content-meaning'].append('fail')
    if data['case'].get('requireAttachedConnectors'):
        assess('attached-connectors', review.get('capabilities', {}).get('attachedConnectors', {}), 'editability')
    states = {name: ('needs-work' if 'fail' in items else 'unverified' if not items or 'unverified' in items else 'pass')
              for name, items in dimensions.items()}
    core = [states[name] for name in ('visual-fidelity', 'content-meaning', 'editability')]
    status = 'fail' if violations else 'unverified' if 'unverified' in core else 'pass'
    # Isolation is a harness requirement, independent of presentation quality.
    isolation = [m for m in strict['unverified'] if 'contexts' in m or 'fingerprinted' in m]
    if status == 'pass' and isolation:
        status = 'unverified'
    return status, states, violations, observations


def evaluate(data):
    if data.get('schemaVersion') != 1:
        raise ValueError('Unsupported evaluator input schema')
    record = {'controls': data['controls'], 'systemCanvas': data['systemCanvas']}
    trial = {'path': data['trialPath'], 'repetition': int(Path(data['trialPath']).name[1:])}
    result = legacy.check_trial(Path(data['runDirectory']), record, trial, data['case'], data['reference'])
    statuses = {'accepted': 'pass', 'failed': 'fail', 'partial': 'unverified', 'not-run': 'unverified'}
    response = {'schemaVersion': 1, 'status': statuses[result['status']],
            'violations': [{'id': 'automatic', 'message': message} for message in result['automaticFailures']] +
                          [{'id': gate, 'message': 'Review gate failed'} for gate, state in result['gateResults'].items() if state == 'fail'],
            'diagnostics': result, 'contextIds': result.get('contextIds', []), 'runtime': result.get('runtime')}
    if data['case'].get('reviewPolicy') == 'practical-v1':
        status, dimensions, violations, observations = practical_review(data, result)
        response.update(status=status, dimensions=dimensions, violations=violations, observations=observations,
                        fullAcceptanceStatus=result['status'])
        result['qualityPolicy'] = 'practical-v1'
        result['fullAcceptanceStatus'] = result['status']
    return response


def main():
    try:
        result = evaluate(json.load(sys.stdin))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(str(exc), file=sys.stderr)
        result = {'schemaVersion': 1, 'status': 'error', 'violations': [{'id': 'evaluation-error', 'message': str(exc)}]}
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))


if __name__ == '__main__':
    main()
