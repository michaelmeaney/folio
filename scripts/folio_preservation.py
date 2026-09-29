"""Semantic checks for Folio 0.2 preservation and evidence records.

These checks establish internal consistency, not visual quality or host editing support.
"""
from __future__ import annotations

import hashlib
import json
import re
import zipfile
from pathlib import Path


class PreservationError(ValueError):
    pass


def baseline_digest(document: dict) -> str:
    """Hash canonical JSON so formatting changes do not invalidate a baseline."""
    return hashlib.sha256(json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_file(owner: Path, name: str, boundary: Path | None = None) -> Path:
    if not name or Path(name).is_absolute():
        raise PreservationError(f"{owner}: evidence/reference must be a relative local path: {name}")
    target = (owner.parent / name).resolve()
    if not target.is_relative_to((boundary or owner.parent.parent).resolve()) or not target.is_file():
        raise PreservationError(f"{owner}: missing or escaping evidence/reference: {name}")
    return target


def unique(items: list[dict], field: str, label: str) -> dict:
    result = {item[field]: item for item in items}
    if len(result) != len(items):
        raise PreservationError(f"duplicate {label}")
    return result


def check_intent(intent: dict) -> None:
    permissions = intent['permissions']
    if any(permissions.values()) and not intent.get('authorizationRef'):
        raise PreservationError('structural/copy permissions require authorisation')
    if intent['operation'] == 'convert' and any(permissions.values()):
        raise PreservationError('Convert cannot authorise treatment, content or structural changes')
    if intent['mode'] == 'quick' and intent['operation'] != 'convert':
        raise PreservationError('Quick requires Convert; styling/Redesign requires Guided or Governed')
    if intent['operation'] == 'restyle' and permissions['recompose']:
        raise PreservationError('recomposition requires Redesign intent')
    if intent['operation'] == 'redesign' and not intent.get('authorizationRef'):
        raise PreservationError('Redesign requires explicit authorisation')


def check_specification(spec: dict) -> None:
    check_intent(spec['intent'])
    if spec['slideIndex'] > spec['sourceSlideCount']:
        raise PreservationError('source slide index exceeds source slide count')
    regions = unique(spec['regions'], 'id', 'source region')
    relationships = unique(spec['relationships'], 'id', 'source relationship')
    deviations = unique(spec['deviations'], 'id', 'deviation')
    if set(regions) & set(relationships):
        raise PreservationError('region and relationship IDs must be distinct')
    functional = {key for key, region in regions.items() if region['role'] != 'whitespace'}
    hierarchy = spec['hierarchy']
    if set(hierarchy['readingOrder']) != functional:
        raise PreservationError('reading order must cover every functional source region')
    if hierarchy['primaryRegion'] not in functional:
        raise PreservationError('primary region does not resolve')
    for region in regions.values():
        f = region['frame']
        if f['x'] + f['width'] > 1 + 1e-9 or f['y'] + f['height'] > 1 + 1e-9:
            raise PreservationError(f"source region {region['id']} exceeds normalised canvas")
        if region['role'] == 'whitespace' and region['text']:
            raise PreservationError('whitespace cannot contain visible text')
    for relation in relationships.values():
        if relation['from'] not in functional or relation['to'] not in functional:
            raise PreservationError(f"relationship {relation['id']} endpoints do not resolve")
    for deviation in deviations.values():
        if not spec['intent']['permissions'][deviation['permission']]:
            raise PreservationError(f"deviation {deviation['id']} lacks permission")
        if not set(deviation['sourceIds']) <= set(regions) | set(relationships):
            raise PreservationError(f"deviation {deviation['id']} references unknown source IDs")


def permitted(spec: dict, permission: str, source_id: str) -> bool:
    return spec['intent']['permissions'][permission] and any(
        d['permission'] == permission and source_id in d['sourceIds'] for d in spec['deviations']
    )


def union_frame(objects: list[dict], canvas: dict) -> dict:
    frames = [o['frame'] for o in objects]
    x, y = min(f['x'] for f in frames), min(f['y'] for f in frames)
    right = max(f['x'] + f['width'] for f in frames)
    bottom = max(f['y'] + f['height'] for f in frames)
    return {'x': x / canvas['width'], 'y': y / canvas['height'],
            'width': (right - x) / canvas['width'], 'height': (bottom - y) / canvas['height']}


def math_isclose(first: float, second: float) -> bool:
    return abs(first - second) <= 1e-6


def intersection_area(first: dict, second: dict) -> float:
    width = max(0, min(first['x'] + first['width'], second['x'] + second['width']) - max(first['x'], second['x']))
    height = max(0, min(first['y'] + first['height'], second['y'] + second['height']) - max(first['y'], second['y']))
    return width * height


def contains(outer: dict, inner: dict) -> bool:
    return (outer['x'] <= inner['x'] + 1e-9 and outer['y'] <= inner['y'] + 1e-9
            and outer['x'] + outer['width'] >= inner['x'] + inner['width'] - 1e-9
            and outer['y'] + outer['height'] >= inner['y'] + inner['height'] - 1e-9)


def check_preservation(spec: dict, scenes: list[dict]) -> None:
    regions = {r['id']: r for r in spec['regions']}
    expected = {r['id']: r for r in spec['relationships']}
    represented, actual_relations = {}, {}
    for scene in scenes:
        trace = scene['preservation']
        if trace['baselineSha256'] != baseline_digest(spec):
            raise PreservationError('scene baseline digest differs from frozen source contract')
        objects = unique(scene['objects'], 'id', 'scene object')
        region_map = unique(trace['regions'], 'regionId', 'region mapping')
        relation_map = unique(trace['relationships'], 'relationshipId', 'relationship mapping')
        if not set(region_map) <= set(regions) or not set(relation_map) <= set(expected):
            raise PreservationError('trace references unknown source region or relationship')
        if set(represented) & set(region_map) or set(actual_relations) & set(relation_map):
            raise PreservationError('source item mapped more than once across output slides')
        represented.update(region_map)
        actual_relations.update(relation_map)
        if not math_isclose(scene['canvas']['width'] / scene['canvas']['height'], spec['sourceDimensions']['width'] / spec['sourceDimensions']['height']) and not all(permitted(spec, 'recompose', rid) for rid in regions if regions[rid]['role'] != 'whitespace'):
            raise PreservationError('canvas ratio changed without scoped recomposition permission')
        used = set()
        actual_frames = {}
        for rid, mapping in region_map.items():
            source = regions[rid]
            ids = mapping['objectIds']
            if not set(ids) <= set(objects):
                raise PreservationError(f'{rid}: mapping references missing object')
            if any(objects[oid].get('decorative', False) for oid in ids):
                raise PreservationError(f'{rid}: functional source mapped to decorative object')
            shared = used & set(ids)
            if shared and not permitted(spec, 'consolidate', rid):
                raise PreservationError(f'{rid}: unauthorised region consolidation')
            used.update(ids)
            if source['role'] == 'whitespace':
                if ids:
                    raise PreservationError('whitespace region must remain unoccupied by mapped content')
                continue
            if not ids:
                if not permitted(spec, 'omitContent', rid):
                    raise PreservationError(f'{rid}: unauthorised omission')
                continue
            if scene['slideIndex'] != spec['slideIndex'] and not permitted(spec, 'splitSlides', rid):
                raise PreservationError(f'{rid}: visible content moved to another slide without permission')
            mapped = [objects[oid] for oid in ids]
            actual = union_frame(mapped, scene['canvas'])
            actual_frames[rid] = actual
            drift = any(abs(actual[key] - source['frame'][key]) > source['tolerance'][key] + 1e-9 for key in actual)
            if drift and not permitted(spec, 'recompose', rid):
                raise PreservationError(f'{rid}: composition geometry exceeds source tolerance')
            actual_text = ' '.join(o.get('text', '') for o in mapped if o['type'] == 'text')
            if ' '.join(actual_text.split()) != ' '.join(source['text'].split()) and not permitted(spec, 'rewriteCopy', rid):
                raise PreservationError(f'{rid}: visible content changed without rewrite permission')
        primary = trace['primaryRegion']
        if primary not in regions or primary not in region_map or not region_map[primary]['objectIds']:
            raise PreservationError('output primary region must be visibly represented on its slide')
        if primary != spec['hierarchy']['primaryRegion'] and not permitted(spec, 'replacePrimaryVisual', spec['hierarchy']['primaryRegion']):
            raise PreservationError('primary visual replaced without permission')
        for rid, region in regions.items():
            if region['role'] == 'whitespace' and not permitted(spec, 'recompose', rid):
                for occupied in actual_frames.values():
                    if intersection_area(region['frame'], occupied) > 1e-9:
                        raise PreservationError(f'{rid}: important whitespace occupied by functional content')
        for rel_id, mapping in relation_map.items():
            relation = expected[rel_id]
            if relation['type'] in ('technical', 'illustrative', 'annotation') and used & set(mapping['objectIds']) and not permitted(spec, 'consolidate', rel_id):
                raise PreservationError(f'{rel_id}: unauthorised relationship consolidation')
            if not set(mapping['objectIds']) <= set(objects):
                raise PreservationError('relationship mapping references missing object')
            wanted = {k: relation[k] for k in ('from', 'to', 'type', 'directed', 'label')}
            visual_relations = []
            rendered_labels = []
            for oid in mapping['objectIds']:
                output = objects[oid]
                if output['type'] == 'text' and not output.get('decorative', False):
                    rendered_labels.append(output.get('text', ''))
                    used.add(oid)
                    continue
                visual_relations.append(output)
                if output.get('decorative', False) or output.get('relationship') != wanted:
                    raise PreservationError(f'{rel_id}: relationship meaning, direction or label changed')
                if relation['type'] in ('technical', 'illustrative', 'annotation'):
                    if output['type'] not in ('line', 'connector'):
                        raise PreservationError(f'{rel_id}: relationship requires a line or connector')
                    for endpoint, source_id in (('source', relation['from']), ('target', relation['to'])):
                        if output.get(endpoint) not in region_map.get(source_id, {}).get('objectIds', []):
                            raise PreservationError(f'{rel_id}: actual connector endpoint differs from source relationship')
                if output.get('text'):
                    rendered_labels.append(output['text'])
                used.add(oid)
            if not visual_relations or ' '.join(' '.join(rendered_labels).split()) != ' '.join(relation['label'].split()):
                raise PreservationError(f'{rel_id}: relationship label or visual representation missing')
            first, second = actual_frames.get(relation['from']), actual_frames.get(relation['to'])
            if first is None or second is None:
                raise PreservationError(f'{rel_id}: relationship endpoint region is not visible')
            if relation['type'] == 'contains' and not contains(first, second):
                raise PreservationError(f'{rel_id}: containment relationship lost')
            if relation['type'] == 'overlaps' and intersection_area(first, second) <= 0:
                raise PreservationError(f'{rel_id}: overlap relationship lost')
            if relation['type'] == 'aligned-with':
                aligned = any(abs(first[axis] + fraction * first[size] - second[axis] - fraction * second[size]) <= max(regions[relation['from']]['tolerance'][axis], regions[relation['to']]['tolerance'][axis]) + 1e-9 for axis, size in [('x', 'width'), ('y', 'height')] for fraction in [0, .5, 1])
                if not aligned:
                    raise PreservationError(f'{rel_id}: alignment relationship lost')
        functional = {oid for oid, output in objects.items() if not output.get('decorative', False)}
        if used != functional:
            raise PreservationError('functional output objects lack source traceability')
        # Collapse object-level order back to source regions. One-to-many mappings are valid.
        actual_order = []
        for oid in scene['readingOrder']:
            for rid, mapping in region_map.items():
                if oid in mapping['objectIds'] and rid not in actual_order:
                    actual_order.append(rid)
        wanted_order = [rid for rid in spec['hierarchy']['readingOrder'] if rid in region_map and region_map[rid]['objectIds']]
        if set(actual_order) != set(wanted_order):
            raise PreservationError('reading order omits a visible source region')
        if actual_order != wanted_order and not all(permitted(spec, 'recompose', rid) for rid in wanted_order):
            raise PreservationError('reading order changed without scoped recomposition permission')
    if set(represented) != set(regions) or set(actual_relations) != set(expected):
        raise PreservationError('source region or relationship omitted from output trace')


def check_evidence(owner: Path, evidence: dict, boundary: Path) -> Path:
    target = local_file(owner, evidence['path'], boundary)
    if file_digest(target) != evidence['sha256']:
        raise PreservationError(f'{owner}: evidence digest mismatch: {evidence["path"]}')
    return target


def check_execution(path: Path, result: dict, by_path: dict) -> None:
    check_intent(result['intent'])
    scenes = []
    for name in result['scenes']:
        target = local_file(path, name, path.parent)
        doc = by_path.get(target)
        if not doc or doc['kind'] != 'scene' or doc['schemaVersion'] != '0.2.0':
            raise PreservationError('execution requires bundled 0.2.0 scenes')
        scenes.append((target, doc))
    if len({target for target, _ in scenes}) != len(scenes):
        raise PreservationError('duplicate execution scene reference')
    provenance = result['provenance']
    sources = {check_evidence(path, evidence, path.parent): evidence['sha256'] for evidence in provenance['sources']}
    for gate in result['gates'].values():
        for evidence in gate['evidence']:
            check_evidence(path, evidence, path.parent)
    for check in result['editingChecks']:
        for evidence in check['evidence']:
            check_evidence(path, evidence, path.parent)
    artefacts = {key: local_file(path, name, path.parent) for key, name in result['artefacts'].items()}
    if result['status'] != 'accepted':
        return
    indices = [scene['slideIndex'] for _, scene in scenes]
    if sorted(indices) != list(range(1, len(indices) + 1)):
        raise PreservationError('accepted execution requires contiguous unique output slide indices')
    specs = {}
    for scene_path, scene in scenes:
        preservation = scene.get('preservation')
        if not preservation:
            if result['intent']['operation'] != 'create':
                raise PreservationError('reference execution scene omits preservation contract')
            continue
        spec_path = local_file(scene_path, preservation['visualSpecificationRef'])
        spec = by_path.get(spec_path)
        if not spec or spec['intent'] != result['intent']:
            raise PreservationError('execution intent differs from source contract')
        specs[spec_path] = spec
    for spec_path, spec in specs.items():
        if any(item['ambiguity'].strip() for item in spec['regions'] + spec['relationships']):
            raise PreservationError('material source ambiguity prevents acceptance')
        if len(scenes) != spec['sourceSlideCount'] and not spec['intent']['permissions']['splitSlides']:
            raise PreservationError('source slide count changed without permission')
        # Revalidate only the scenes actually delivered by this execution.
        selected = [scene for scene_path, scene in scenes if scene.get('preservation') and local_file(scene_path, scene['preservation']['visualSpecificationRef']) == spec_path]
        check_preservation(spec, selected)
    if specs:
        source_counts = {spec['sourceSlideCount'] for spec in specs.values()}
        source_indices = [spec['slideIndex'] for spec in specs.values()]
        if len(source_counts) != 1 or sorted(source_indices) != list(range(1, next(iter(source_counts)) + 1)):
            raise PreservationError('execution omits a source slide baseline')
    expected_differences = {(sp, d['id']) for sp, spec in specs.items() for d in spec['deviations']}
    actual_differences = {(local_file(path, d['specificationRef'], path.parent), d['deviationId']) for d in result['differences']}
    if actual_differences != expected_differences or len(actual_differences) != len(result['differences']):
        raise PreservationError('execution differences do not account for scoped deviations')
    if result['intent']['mode'] == 'governed' and not provenance['designSystemRevision']:
        raise PreservationError('Governed acceptance requires design-system revision')
    if any(sources.get(local_file(sp, spec['source'])) != spec['sourceSha256'] for sp, spec in specs.items()):
        raise PreservationError('execution provenance omits source digest')
    claimed = {op for _, scene in scenes for output in scene['objects'] for op in output.get('editing', [])}
    if any(output['type'] == 'text' for _, scene in scenes for output in scene['objects']):
        claimed.add('text')
    tested = {check['operation'] for check in result['editingChecks'] if check['status'] == 'pass'}
    if not claimed <= tested:
        raise PreservationError('claimed editing operations lack host editing tests')
    artefact_evidence = {local_file(path, evidence['path'], path.parent) for evidence in result['gates']['artefact']['evidence']}
    comparison_evidence = {local_file(path, evidence['path'], path.parent) for evidence in result['gates']['composition']['evidence']}
    if not {artefacts['pptx'], artefacts['render']} <= artefact_evidence:
        raise PreservationError('artefact gate must fingerprint the delivered PowerPoint and render')
    if not {artefacts['render'], *sources} <= comparison_evidence:
        raise PreservationError('composition gate must reference source and final render together')
    if artefacts['render'] in sources:
        raise PreservationError('source image cannot also stand in for final render evidence')
    if artefacts['pptx'].suffix.lower() != '.pptx':
        raise PreservationError('accepted output requires a PowerPoint artefact')
    try:
        with zipfile.ZipFile(artefacts['pptx']) as deck:
            if '[Content_Types].xml' not in deck.namelist() or 'ppt/presentation.xml' not in deck.namelist():
                raise PreservationError('PowerPoint artefact lacks required package parts')
            slides = [name for name in deck.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml', name)]
            if len(slides) != len(scenes):
                raise PreservationError('PowerPoint slide count differs from execution scenes')
    except zipfile.BadZipFile as exc:
        raise PreservationError('PowerPoint artefact is not an Office ZIP package') from exc


def validate_preservation_bundle(documents: list[tuple[Path, dict]]) -> None:
    by_path = {p.resolve(): doc for p, doc in documents}
    specifications, attached = {}, {}
    for path, doc in documents:
        if doc['schemaVersion'] != '0.2.0':
            continue
        if doc['kind'] == 'visual-specification':
            check_specification(doc)
            source = local_file(path, doc['source'])
            if file_digest(source) != doc['sourceSha256']:
                raise PreservationError('source image digest mismatch')
            specifications[path.resolve()] = doc
        elif doc['kind'] == 'scene':
            objects = unique(doc['objects'], 'id', 'scene object')
            if not set(doc['readingOrder']) <= set(objects):
                raise PreservationError('reading order references unknown object')
            for output in objects.values():
                if 'attachConnectors' in output.get('editing', []) and output['type'] != 'connector':
                    raise PreservationError('only a connector may claim attachConnectors; editable lines are distinct')
                if 'attachConnectors' in output.get('editing', []) and (output.get('source') not in objects or output.get('target') not in objects):
                    raise PreservationError('attached connector claims require explicit local object endpoints')
            if 'preservation' not in doc:
                continue
            target = local_file(path, doc['preservation']['visualSpecificationRef'])
            attached.setdefault(target, []).append(doc)
    for path, scenes in attached.items():
        spec = specifications.get(path)
        if spec is None:
            raise PreservationError('bundle omits 0.2.0 source composition contract')
        check_preservation(spec, scenes)
    for path, doc in documents:
        if doc['schemaVersion'] == '0.2.0' and doc['kind'] == 'execution-result':
            check_execution(path, doc, by_path)
