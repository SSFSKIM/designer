#!/Users/new/vitrea-w49/py/bin/python -I
"""Prospective source-bound canonical REFERENCE reader, not a coefficient/candidate tool.

Fixed batch/config paths and the exact canonical subset of immutable G0 references.json
are registered by one write-once contract/root. No caller row/source selection is admitted.
After review/approval, `run.py seal BATCH` prospectively seals synthetic-only source discovery.
A real read requires `run.py BATCH --root-sha256 EXTERNAL_REGISTERED_HASH --out FRESH_JSON`.
The permanent source-only guard is installed before measurement helpers execute. Sealing
and its probe never read historical source trees. `metadata BATCH` checks identities/source
metadata only and NEVER opens a PNG, gzipped cell statistics or computes measurements.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
G0 = HERE.parents[1]/'2026-10-08-w50-g0-declaration'
BATCH = HERE/'read-batch.json'
CONFIG = HERE/'read-config.json'
CONTRACT = HERE/'execution-contract.json'
INSTRUMENT = HERE/'instrument-root.json'
PROBE = HERE/'probe.py'
ONE = 'bb185d87d850d12fd3b0019cbe9d0db65c541b73c14690035192131e30a00b86'
TWO = 'bdd1050ed6ad9671676b0551c33a685e3093a5548652b04662fb81d4a29adb85'
KEY = ('profile', 'renderer', 'scene', 'statistic')
TRUSTED = None


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(path): return str(Path(path).resolve().relative_to(ROOT))


def checked_path(path):
    path = Path(path); path = path if path.is_absolute() else ROOT/path
    if not path.is_relative_to(ROOT) or '..' in path.parts:
        raise ValueError('Reference source/root path escapes repository')
    current = ROOT
    for item in path.relative_to(ROOT).parts:
        current /= item
        if current.is_symlink(): raise ValueError('Reference source/root symlinks are refused')
    if not path.is_file(): raise ValueError('Missing reference source/root: '+str(path))
    return path


def pin(path): return {'path': relative(path), 'sha256': sha(path)}


def checked(item):
    if not isinstance(item, dict) or set(item) != {'path', 'sha256'} \
            or not isinstance(item['path'], str) or Path(item['path']).is_absolute() \
            or not re.fullmatch('[0-9a-f]{64}', item.get('sha256', '')):
        raise ValueError('Missing full reference root/source pin')
    path = checked_path(item['path'])
    if sha(path) != item['sha256']: raise ValueError('Changed reference source/root: '+item['path'])
    return path


def load(path): return json.loads(Path(path).read_bytes())


def source(name, path):
    path = checked_path(path)
    if TRUSTED is not None and TRUSTED.get(relative(path)) != sha(path):
        raise ValueError('Changed or unsealed reference source before helper execution')
    module = types.ModuleType(name); module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


def canonical_subset(inventory):
    result = [r for r in inventory['cells'] if r.get('role') in
        ('gate', 'historical-prediction-check', 'reference-only') and r.get('statistic') in
        ('T1-low', 'T1-full-silhouette', 'low-end-path-level') and
        re.fullmatch(r'apple-macos-27\.0-[12]x-dark-standard-glass(?:0\.25|0\.5)', r.get('profile', ''))]
    keys = [tuple(r[k] for k in KEY) for r in result]
    if not result or len(keys) != len(set(keys)): raise ValueError('Missing/duplicate canonical G0 subset')
    return result


def batch_metadata(path):
    """Stdlib-only fixed input/root/source admission, without historical PNG/metadata reads."""
    path = checked_path(path)
    if path != BATCH: raise ValueError('Reference batch must use its fixed registered pathname')
    doc = load(path)
    expected = {'partOne': G0/'declaration.json', 'partTwo': G0/'fit-declaration.json',
                'inventory': G0/'references.json', 'config': CONFIG}
    if doc.get('schema') != 'w50-canonical-reference-batch-1' or set(doc.get('inputs', {})) != set(expected):
        raise ValueError('Unknown/incomplete reference batch')
    for name, target in expected.items():
        if checked(doc['inputs'][name]) != target:
            raise ValueError('Reference batch substituted its fixed G0/config input')
    if doc['inputs']['partOne']['sha256'] != ONE or doc['inputs']['partTwo']['sha256'] != TWO:
        raise ValueError('Reference batch names another immutable G0 declaration')
    one, two = load(expected['partOne']), load(expected['partTwo'])
    if one.get('schema') != 'w50-declaration-1' or two.get('schema') != 'w50-fit-declaration-1' \
            or two.get('partOneSha256') != ONE:
        raise ValueError('Reference G0 declaration pair identity mismatch')
    sources = []
    for name, part in (('partOne', one), ('partTwo', two)):
        p = expected[name]
        if p.with_suffix('.sha256').read_text() != f'{sha(p)}  {p.name}\n':
            raise ValueError('Changed G0 declaration sidecar')
        if (p.parent/part['references']).resolve() != expected['inventory'] \
                or doc['inputs']['inventory'] not in part['sources']:
            raise ValueError('Reference inventory differs from immutable G0 selection')
        sources.append({p['path']: p['sha256'] for p in part['sources']})
    guards = {}
    for name in ('next_wave.py', 'closure.py'):
        p = checked_path(G0/'audit'/name); wanted = sha(p)
        if any(s.get(relative(p)) != wanted for s in sources):
            raise ValueError('Changed immutable G0 reference guard source')
        guards[relative(p)] = wanted
    inventory = load(expected['inventory']); rows = canonical_subset(inventory)
    if doc.get('selectedKeys') != [[r[k] for k in KEY] for r in rows]:
        raise ValueError('Caller-selected/withheld reference subset differs from exact G0 canonical keys')
    config = load(CONFIG)
    if config.get('schema') != 'w50-canonical-reference-config-1' \
            or set(config)-{'currentCompletion','currentComposition'} != \
                {'schema', 'scenes', 'publishedManifest', 'fixtureRoot', 'w29', 'w43'} \
            or {'currentCompletion','currentComposition'} <= set(config):
        raise ValueError('Unknown or mutually conflicting canonical reference source config')
    composition = config.get('currentComposition')
    if 'currentComposition' in config:
        if not isinstance(composition,dict) or set(composition) != {'path','sha256'} or \
                not isinstance(composition.get('path'),str) or Path(composition['path']).is_absolute() or \
                '..' in Path(composition['path']).parts or \
                not re.fullmatch('[0-9a-f]{64}',composition.get('sha256','')):
            raise ValueError('Current composition needs one same-repository full content pin')
    completion = config.get('currentCompletion')
    if completion is not None:
        if not isinstance(completion, dict) or set(completion) != {'instrument', 'results'} \
                or not isinstance(completion['results'], list) or not completion['results']:
            raise ValueError('Current completion needs a content-pinned instrument and fixed result list')
        for item in [completion['instrument'], *completion['results']]:
            if not isinstance(item, dict) or set(item) != {'path', 'sha256'} \
                    or Path(item['path']).is_absolute() or not re.fullmatch('[0-9a-f]{64}', item['sha256']):
                raise ValueError('Current completion pins must be same-repository paths and full hashes')
    # External content pins are fixed by CONFIG, not caller arguments; source evidence is
    # checked by canonical.py after bootstrap. Probe/seal deliberately does not open it.
    for item in (config['scenes'], config['publishedManifest'], config['w29']['provenance'], config['w43']['fetch']):
        if not isinstance(item, dict) or set(item) != {'path', 'sha256'} \
                or not Path(item['path']).is_absolute() or not re.fullmatch('[0-9a-f]{64}', item['sha256']):
            raise ValueError('Reference config needs exact absolute content-pinned metadata paths')
    for name in ('fixtureRoot',):
        if not Path(config[name]).is_absolute(): raise ValueError('Reference config source roots must be absolute')
    for name in ('w29', 'w43'):
        if not Path(config[name]['root']).is_absolute(): raise ValueError('Reference source root must be explicit')
    return doc, config, rows, guards


def dry_exercise():
    source('w50_reference_probe_reader', HERE/'canonical.py').source_probe()
    config = load(CONFIG) if CONFIG.is_file() else {}
    if config.get('currentComposition') is not None:
        source('w50_reference_probe_composed_completion', HERE/'composed_completion.py').source_probe(
            config['currentComposition'], repo=ROOT)
    else:
        source('w50_reference_probe_completion', HERE/'completion.py').source_probe(
            config.get('currentCompletion'), repo=ROOT)


def sealed_sidecar(path):
    p = checked_path(str(path)+'.sha256')
    if p.read_text() != f'{sha(path)}  {path.name}\n': raise ValueError('Reference prospective seal mismatch')
    return p


def bootstrap(batch, root_hash):
    global TRUSTED
    if not re.fullmatch('[0-9a-f]{64}', root_hash) or sha(checked_path(INSTRUMENT)) != root_hash:
        raise ValueError('Reference instrument root differs from external registered hash')
    sealed_sidecar(INSTRUMENT); root_doc = load(INSTRUMENT)
    if root_doc.get('schema') != 'w50-reference-instrument-root-1': raise ValueError('Unknown reference instrument root')
    registered = checked(root_doc['batch'])
    if Path(batch).is_symlink() or Path(batch).read_bytes() != registered.read_bytes():
        raise ValueError('Supplied bytes are not the registered canonical reference batch')
    doc, config, rows, guards = batch_metadata(registered)
    if root_doc['inputs'] != doc['inputs'] or checked(root_doc['contract']) != CONTRACT \
            or checked(root_doc['contractSidecar']) != Path(str(CONTRACT)+'.sha256'):
        raise ValueError('Reference root/contract inputs differ')
    sealed_sidecar(CONTRACT); contract = load(CONTRACT)
    expected = dict(contract['closure']['sources']); expected.update(guards)
    if root_doc.get('sources') != expected or contract['renderer'] != relative(Path(__file__)) \
            or contract['probe'] != relative(PROBE) or contract['batch'] != root_doc['batch'] \
            or contract['guardSources'] != {Path(k).name: v for k, v in guards.items()}:
        raise ValueError('Reference source closure/entrypoint binding mismatch')
    for name, wanted in expected.items(): checked({'path': name, 'sha256': wanted})
    completion_source = HERE/('composed_completion.py' if config.get('currentComposition') is not None else 'completion.py')
    for p in (Path(__file__), PROBE, HERE/'canonical.py', HERE/'statistics.py', completion_source,
              HERE.parent/'native/statistics.py', HERE.parents[1]/'2026-10-03-w44-g0-declaration/port/interior.py',
              HERE.parents[1]/'2026-10-01-w43-g0-declaration/bed/sitting/w43_archive.py'):
        if relative(p) not in contract['closure']['sources']:
            raise ValueError('Required reference source absent from exercised closure')
    TRUSTED = expected
    closure = source('w50_reference_live_guard', G0/'audit/closure.py'); closure.enforce(ROOT, expected)
    next_wave = source('w50_reference_contract', G0/'audit/next_wave.py')
    _, bound, renderer = next_wave.verify(CONTRACT, ROOT, registered)
    if bound != registered or renderer != Path(__file__).resolve(): raise ValueError('Reference contract binds another entrypoint')
    return doc, config, rows, root_doc


def seal_reference(batch):
    if any(p.exists() for p in (CONTRACT, Path(str(CONTRACT)+'.sha256'), INSTRUMENT, Path(str(INSTRUMENT)+'.sha256'))):
        raise ValueError('Existing reference seal: no amendment/rehash')
    doc, _, _, guards = batch_metadata(batch)
    closure = source('w50_reference_seal_guard', G0/'audit/closure.py'); closure.enforce(ROOT, guards)
    next_wave = source('w50_reference_seal_contract', G0/'audit/next_wave.py')
    contract = next_wave.seal(ROOT, BATCH, PROBE, Path(__file__).resolve(), CONTRACT)
    sources = dict(contract['closure']['sources']); sources.update(guards)
    root_doc = {'schema': 'w50-reference-instrument-root-1', 'batch': pin(BATCH), 'inputs': doc['inputs'],
                'contract': pin(CONTRACT), 'contractSidecar': pin(Path(str(CONTRACT)+'.sha256')), 'sources': sources}
    write_once(INSTRUMENT, root_doc)
    with Path(str(INSTRUMENT)+'.sha256').open('x') as handle:
        handle.write(f'{sha(INSTRUMENT)}  {INSTRUMENT.name}\n'); handle.flush(); os.fsync(handle.fileno())
    return {'instrumentRootSha256': sha(INSTRUMENT), 'instrumentRoot': relative(INSTRUMENT), 'batchSha256': sha(BATCH)}


def write_once(path, value):
    raw = (json.dumps(value, indent=2, allow_nan=False)+'\n').encode()
    with Path(path).open('xb') as handle:
        handle.write(raw); handle.flush(); os.fsync(handle.fileno())


def execute(doc, config, rows, root_doc, root_hash, out):
    out = Path(out)
    if out.exists() or out.is_symlink(): raise ValueError('Reference result exists; never overwrite evidence')
    target = out.resolve()
    protected = [Path(config['fixtureRoot']).resolve(), Path(config['w29']['root']).resolve(), Path(config['w43']['root']).resolve()]
    if target.is_relative_to(ROOT) or any(target.is_relative_to(p) for p in protected):
        raise ValueError('Reference result must be fresh external scratch, outside source trees')
    reader = source('w50_bound_canonical_reference', HERE/'canonical.py')
    projection = None
    original_rows = rows
    if config.get('currentCompletion') is not None:
        completion = source('w50_bound_current_completion', HERE/'completion.py')
        projection = completion.complete_current_projection(ROOT, rows, config['currentCompletion'],
            scenes=reader.json_pin(config['scenes']))
        rows = projection['rows']
    elif config.get('currentComposition') is not None:
        completion = source('w50_bound_composed_completion', HERE/'composed_completion.py')
        projection = completion.complete_current_projection(ROOT, rows, config['currentComposition'],
            scenes=reader.json_pin(config['scenes']))
        rows = projection['rows']
    report = reader.read_references(rows, config)
    report['originalReferences'] = original_rows
    report['currentArtifactProjection'] = projection
    report.update(inputs=doc['inputs'], selectedKeys=doc['selectedKeys'], instrumentRootSha256=root_hash,
                  batch=root_doc['batch'], contract=root_doc['contract'], sourcePins=root_doc['sources'])
    write_once(out, report)
    return report


def metadata_compatibility(batch):
    """Identity/source-only diagnostic: NEVER PNG bytes, cell records or measured statistics."""
    doc, config, rows, _ = batch_metadata(batch)
    reader = source('w50_reference_metadata_check', HERE/'canonical.py')
    scenes = reader.json_pin(config['scenes']); published = reader.json_pin(config['publishedManifest'])
    backgrounds = published.get('backgrounds', {})
    profiles = {p['profileKey']: p for p in published['profiles']}
    report = {'schema': 'w50-reference-metadata-compatibility-1', 'inputs': doc['inputs'],
              'selectedKeys': doc['selectedKeys'], 'missingCurrentKeys': [], 'issues': [],
              'pixels': 'NONE: metadata only, no PNG/cell statistic reads', 'sources': {}}
    for row in rows:
        key = [row[k] for k in KEY]
        if row.get('currentEvidence') is None: report['missingCurrentKeys'].append(key)
        scene = next((s for s in scenes['scenes'] if s['id'] == row['scene']), None)
        entry = next((f for f in profiles.get(row['profile'], {}).get('fixtures', []) if f['sceneId'] == row['scene']), None)
        if scene is None or entry is None: report['issues'].append({'key': key, 'reason': 'missing declared/published identity'}); continue
        expected = Path(config['fixtureRoot'])/entry['file']
        if row.get('nativeEvidence', {}).get('path') != str(expected):
            report['issues'].append({'key': key, 'reason': 'G0 native path differs from fixtureRoot/index'})
        scale = int(re.search(r'-([12])x-', row['profile'])[1])
        if f'{scene["background"]}@{scale}x' not in backgrounds:
            report['issues'].append({'key': key, 'reason': 'missing explicit indexed same-scale background'})
    try:
        w29 = reader.verify_w29_source(config['w29'])
        report['sources']['w29'] = {'runs': len(w29['runs']), 'metadataPins': w29['runs'],
                                   'frameHashBinding': w29['frameHashBinding']}
    except (ValueError, KeyError, OSError) as error:
        report['issues'].append({'source': 'w29', 'reason': str(error)})
    try:
        fetch = reader.json_pin(config['w43']['fetch'])
        index = reader.json_pin({'path': str(Path(config['w43']['root'])/'inventory.json'),
                                 'sha256': fetch['inventorySha256']})
        if index.get('schema') != reader.A.SCHEMA or index.get('sitting') != 'g1a':
            raise ValueError('Wrong W43 metadata index/source')
        report['sources']['w43'] = {'fetch': config['w43']['fetch'], 'inventorySha256': fetch['inventorySha256'],
                                   'assetSha256': fetch['sha256'], 'cells': len(index['cells']), 'runs': len(index['runs'])}
        identities = {c['cell']: c for c in index['cells']}
        for row in rows:
            if row['profile'].endswith('-glass0.25'):
                own = identities.get(row['profile']+'/'+row['scene'])
                if own is None or own.get('runs', 0) < 7:
                    report['issues'].append({'key': [row[k] for k in KEY], 'reason': 'missing W43 native repeat identity'})
    except (ValueError, KeyError, OSError) as error:
        report['issues'].append({'source': 'w43', 'reason': str(error)})
    return report


def main(argv=None):
    import sys
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] in (['seal'], ['metadata']):
        command = argv[0]; parser = argparse.ArgumentParser()
        parser.add_argument('batch', type=Path); args = parser.parse_args(argv[1:])
        print(json.dumps(seal_reference(args.batch) if command == 'seal' else metadata_compatibility(args.batch), allow_nan=False))
        return 0
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('batch', type=Path); parser.add_argument('--root-sha256', required=True)
    parser.add_argument('--out', required=True, type=Path); args = parser.parse_args(argv)
    doc, config, rows, root_doc = bootstrap(args.batch, args.root_sha256)
    report = execute(doc, config, rows, root_doc, args.root_sha256, args.out)
    return 0 if all(r['status'] == 'MEASURED' for v in report['partitions'].values() for r in v) else 1


if __name__ == '__main__': raise SystemExit(main())
