#!/usr/bin/env python3
"""Evaluation protocol adapter. Go owns execution; legacy Python owns judgment."""
import importlib.util
import json
from pathlib import Path
import sys

spec = importlib.util.spec_from_file_location('folio_legacy_evaluation', Path(__file__).resolve().parents[1] / 'runner.py')
legacy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(legacy)


def evaluate(data):
    if data.get('schemaVersion') != 1:
        raise ValueError('Unsupported evaluator input schema')
    record = {'controls': data['controls'], 'systemCanvas': data['systemCanvas']}
    trial = {'path': data['trialPath'], 'repetition': int(Path(data['trialPath']).name[1:])}
    result = legacy.check_trial(Path(data['runDirectory']), record, trial, data['case'], data['reference'])
    statuses = {'accepted': 'pass', 'failed': 'fail', 'partial': 'unverified', 'not-run': 'unverified'}
    return {'schemaVersion': 1, 'status': statuses[result['status']],
            'violations': [{'id': 'automatic', 'message': message} for message in result['automaticFailures']] +
                          [{'id': gate, 'message': 'Review gate failed'} for gate, state in result['gateResults'].items() if state == 'fail'],
            'diagnostics': result, 'contextIds': result.get('contextIds', []), 'runtime': result.get('runtime')}


def main():
    try:
        result = evaluate(json.load(sys.stdin))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(str(exc), file=sys.stderr)
        result = {'schemaVersion': 1, 'status': 'error', 'violations': [{'id': 'evaluation-error', 'message': str(exc)}]}
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))


if __name__ == '__main__':
    main()
