#!/Users/new/vitrea-w49/py/bin/python -I
"""Prospective, source-bound W50 native reader. No real contract is installed by this file.

After approval, `run.py seal BATCH` creates one write-once execution contract and native
instrument root, using unchanged G0 next_wave.seal. The G1/pre-fit root must pin both documents
and sidecars. A read is `run.py BATCH --root-sha256 REGISTERED_ROOT_HASH --out FRESH_JSON`.
It cannot override its fixed contract, source closure, role roots, role index hashes or G0
inputs. An external root hash is required: a self-consistent replacement sidecar is not trust.

Until bootstrap finishes this file imports only stdlib. Every root/G0/source pin is checked
before helper execution; the unchanged source-only closure guard stays live in the actual
reader process. Discovery/probe uses synthetic arrays only and never opens the registered
exports. Failed sealing may leave evidence files: inspect them, never reseal or overwrite.
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
PACK = HERE.parents[1]/'2026-10-08-w50-g1-sitting/pack.json'
CONTRACT = HERE/'execution-contract.json'
INSTRUMENT = HERE/'instrument-root.json'
PROBE = HERE/'probe.py'
# These are the assembled immutable G0 seals, not fitted values or export hashes.
PART_ONE_SHA256 = 'bb185d87d850d12fd3b0019cbe9d0db65c541b73c14690035192131e30a00b86'
PART_TWO_SHA256 = 'bdd1050ed6ad9671676b0551c33a685e3093a5548652b04662fb81d4a29adb85'
TRUSTED_SOURCES = None


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def valid_hash(value):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
        raise ValueError('Expected a complete lowercase SHA-256')
    return value


def relative(path):
    return str(Path(path).resolve().relative_to(ROOT.resolve()))


def checked_path(path):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT/path
    if not path.is_relative_to(ROOT) or '..' in path.parts:
        raise ValueError('Root pin escapes the repository')
    current = ROOT
    for part in path.relative_to(ROOT).parts:
        current /= part
        if current.is_symlink():
            raise ValueError('Root/source symlinks are refused')
    if not path.is_file():
        raise ValueError('Missing root/source file: '+str(path))
    return path


def pin(path):
    path = checked_path(path)
    return {'path': relative(path), 'sha256': sha(path)}


def check_pin(value):
    if not isinstance(value, dict) or set(value) != {'path', 'sha256'} \
            or not isinstance(value['path'], str) or Path(value['path']).is_absolute():
        raise ValueError('Malformed root/source pin')
    path = checked_path(value['path'])
    if sha(path) != valid_hash(value['sha256']):
        raise ValueError('Changed root/source bytes: '+value['path'])
    return path


def source_module(name, path):
    path = checked_path(path)
    if TRUSTED_SOURCES is not None and TRUSTED_SOURCES.get(relative(path)) != sha(path):
        raise ValueError('Changed or unsealed source before helper execution: '+relative(path))
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


def load_reader():
    return source_module('w50_native_bound_reader', HERE/'reader.py')


def batch_inputs(batch):
    """Stdlib-only validation: identity metadata and pinned source bytes, never export contents."""
    if batch.get('schema') != 'w50-native-read-batch-1':
        raise ValueError('Unknown native read batch schema')
    exports = batch.get('exports')
    if not isinstance(exports, list) or len(exports) != 2 \
            or [e.get('role') for e in exports] != ['calibration', 'validation']:
        raise ValueError('Native batch must contain exactly calibration then validation; blind is closed')
    roots = []
    for export in exports:
        if set(export) != {'role', 'root', 'indexSha256'} or not isinstance(export['root'], str) \
                or not Path(export['root']).is_absolute():
            raise ValueError('Native export must have one absolute supplied root and registered index hash')
        valid_hash(export['indexSha256'])
        # Resolve names only; do not inspect even index.json during prospective sealing/probe.
        roots.append(Path(export['root']).resolve())
    if roots[0] == roots[1] or roots[0].is_relative_to(roots[1]) or roots[1].is_relative_to(roots[0]):
        raise ValueError('Native calibration/validation export roots must be independent')
    expected = {'declaration': G0/'declaration.json',
                'declarationSidecar': G0/'declaration.sha256',
                'fitDeclaration': G0/'fit-declaration.json',
                'fitDeclarationSidecar': G0/'fit-declaration.sha256',
                'manifest': G0/'bed/manifest.json', 'scenes': G0/'bed/scenes-w50.json', 'pack': PACK}
    inputs = batch.get('inputs')
    if not isinstance(inputs, dict) or set(inputs) != set(expected):
        raise ValueError('Native batch must pin G0 parts, sidecars, bed and committed G1 pack source')
    for name, path in expected.items():
        if inputs[name].get('path') != relative(path) or check_pin(inputs[name]) != path:
            raise ValueError('Native batch substituted a G0/pack input')
    if inputs['declaration']['sha256'] != PART_ONE_SHA256 \
            or inputs['fitDeclaration']['sha256'] != PART_TWO_SHA256:
        raise ValueError('Native batch names another immutable G0 declaration')
    for name, sidecar in (('declaration', 'declarationSidecar'),
                          ('fitDeclaration', 'fitDeclarationSidecar')):
        path = expected[name]
        if expected[sidecar].read_text() != f'{sha(path)}  {path.name}\n':
            raise ValueError('G0 declaration sidecar mismatch')
    one = json.loads(expected['declaration'].read_bytes())
    two = json.loads(expected['fitDeclaration'].read_bytes())
    if one.get('schema') != 'w50-declaration-1' or two.get('schema') != 'w50-fit-declaration-1' \
            or two.get('partOneSha256') != PART_ONE_SHA256:
        raise ValueError('G0 declaration pair identity mismatch')
    declared_sources = []
    for part in (one, two):
        items = part.get('sources', [])
        mapping = {p['path']: p['sha256'] for p in items}
        if len(items) != len(mapping):
            raise ValueError('Duplicate G0 source pin')
        declared_sources.append(mapping)
    guard_pins = {}
    for path in (G0/'bed/manifest.json', G0/'bed/scenes-w50.json',
                 G0/'audit/next_wave.py', G0/'audit/closure.py'):
        rel, actual = relative(path), sha(checked_path(path))
        if any(sources.get(rel) != actual for sources in declared_sources):
            raise ValueError('G0 source differs from its immutable declaration: '+rel)
        if path.suffix == '.py':
            guard_pins[rel] = actual
    pack = json.loads(PACK.read_bytes())
    if pack.get('declarationSha256') != PART_ONE_SHA256 or pack.get('exportIndexSha256') != \
            {e['role']: e['indexSha256'] for e in exports}:
        raise ValueError('Registered role index hashes differ from the pinned G1 pack metadata')
    return guard_pins


def read_batch(path):
    path = checked_path(path)
    doc = json.loads(path.read_bytes())
    guards = batch_inputs(doc)
    return doc, guards


def check_sidecar(path):
    sidecar = checked_path(str(path)+'.sha256')
    if sidecar.read_text() != f'{sha(path)}  {path.name}\n':
        raise ValueError('Native instrument/contract sidecar mismatch')
    return sidecar


def bootstrap(supplied_batch, expected_root_sha256):
    """Check every root/source byte before execution, then install in-process import enforcement."""
    global TRUSTED_SOURCES
    valid_hash(expected_root_sha256)
    if sha(checked_path(INSTRUMENT)) != expected_root_sha256:
        raise ValueError('Native instrument root differs from the externally registered hash')
    check_sidecar(INSTRUMENT)
    root_doc = json.loads(INSTRUMENT.read_bytes())
    if root_doc.get('schema') != 'w50-native-instrument-root-1':
        raise ValueError('Unknown native instrument root schema')
    registered = check_pin(root_doc['batch'])
    supplied = Path(supplied_batch)
    if not supplied.is_file() or supplied.is_symlink() or supplied.read_bytes() != registered.read_bytes():
        raise ValueError('Supplied bytes are not the sealed native batch')
    batch, guards = read_batch(registered)
    if root_doc.get('inputs') != batch['inputs']:
        raise ValueError('Native root and batch name different G0/pack input pins')
    if check_pin(root_doc['contract']) != CONTRACT \
            or check_pin(root_doc['contractSidecar']) != Path(str(CONTRACT)+'.sha256'):
        raise ValueError('Native root registers another execution contract')
    check_sidecar(CONTRACT)
    sources = root_doc.get('sources')
    if not isinstance(sources, dict) or not sources:
        raise ValueError('Native root lacks its exercised source closure')
    for rel, wanted in sources.items():
        check_pin({'path': rel, 'sha256': wanted})
    contract = json.loads(CONTRACT.read_bytes())
    expected_sources = dict(contract['closure']['sources'])
    expected_sources.update(guards)
    if sources != expected_sources or contract.get('renderer') != relative(Path(__file__)) \
            or contract.get('probe') != relative(PROBE) or contract.get('batch') != root_doc['batch'] \
            or contract.get('guardSources') != {Path(rel).name: wanted for rel, wanted in guards.items()}:
        raise ValueError('Native root/contract source closure or entrypoint mismatch')
    for required in (Path(__file__), PROBE, HERE/'reader.py', HERE/'statistics.py',
                     HERE.parents[1]/'2026-10-03-w44-g0-declaration/port/interior.py'):
        if relative(required) not in contract['closure']['sources']:
            raise ValueError('Native root omitted a required exercised source')
    TRUSTED_SOURCES = sources
    closure = source_module('w50_native_live_closure', G0/'audit/closure.py')
    closure.enforce(ROOT, sources)
    next_wave = source_module('w50_native_next_wave', G0/'audit/next_wave.py')
    _, verified_batch, renderer = next_wave.verify(CONTRACT, ROOT, registered)
    if verified_batch != registered or renderer != Path(__file__).resolve():
        raise ValueError('Native prospective contract binds another entrypoint/batch')
    return batch, root_doc


def dry_exercise():
    """Pure synthetic reader/statistics/geometry exercise used by the source-closure probe."""
    reader = load_reader()
    np = reader.np
    canvas = {'width': 128, 'height': 128}
    component = {'kind': 'rrect', 'size': [112, 96], 'radius': 20.4}
    bg = np.zeros((128, 128, 3), dtype=np.uint8)
    bg[62:66, 62:66] = 255
    runs = []
    for run in (1, 2, 3):
        rgb = np.full(bg.shape, 70+(run == 2), dtype=np.uint8)
        read = reader.S.read_frame(rgb, bg, component, canvas, 1,
                                   impulse=True, include_structured=True)
        mask = reader.S.decode_support(read['supports']['full-silhouette'])
        reader.S.read_frame(rgb, bg, component, canvas, 1, impulse=True,
                            include_structured=True, silhouette_mask=mask)
        runs.append({'run': run, 'readings': read})
    result = reader.aggregate_runs(runs)
    if result['deep8-channel-median']['value'] != [70., 70., 70.] \
            or not result['deep8-channel-median']['repeat']['passes']:
        raise ValueError('Synthetic native instrument exercise failed')
    return result


def seal_native(batch_path):
    """Prospective only: invoke after independent bootstrap review and approval, never at import."""
    if any(p.exists() for p in (CONTRACT, Path(str(CONTRACT)+'.sha256'),
                               INSTRUMENT, Path(str(INSTRUMENT)+'.sha256'))):
        raise ValueError('Native contract/root exists: no amendment or rehash')
    batch_path = checked_path(batch_path)
    batch, guards = read_batch(batch_path)
    # Check the unchanged helpers against both G0 parts, then make next_wave's own import of
    # closure.py source-only too. A valid source hash cannot authenticate a stale pyc cache.
    closure = source_module('w50_native_sealing_closure', G0/'audit/closure.py')
    closure.enforce(ROOT, guards)
    next_wave = source_module('w50_native_sealing_next_wave', G0/'audit/next_wave.py')
    contract = next_wave.seal(ROOT, batch_path, PROBE, Path(__file__).resolve(), CONTRACT)
    sources = dict(contract['closure']['sources']); sources.update(guards)
    root_doc = {'schema': 'w50-native-instrument-root-1', 'inputs': batch['inputs'],
                'batch': pin(batch_path), 'contract': pin(CONTRACT),
                'contractSidecar': pin(Path(str(CONTRACT)+'.sha256')), 'sources': sources}
    raw = (json.dumps(root_doc, indent=2, allow_nan=False)+'\n').encode()
    with INSTRUMENT.open('xb') as handle:
        handle.write(raw); handle.flush(); os.fsync(handle.fileno())
    with Path(str(INSTRUMENT)+'.sha256').open('x') as handle:
        handle.write(f'{sha(INSTRUMENT)}  {INSTRUMENT.name}\n')
        handle.flush(); os.fsync(handle.fileno())
    return {'instrumentRootSha256': sha(INSTRUMENT), 'instrumentRoot': relative(INSTRUMENT),
            'contract': relative(CONTRACT), 'batchSha256': sha(batch_path)}


def execute_batch(batch, root_doc, expected_root_sha256, output):
    """Read both independently verified exports only after bootstrap; write one fresh report."""
    output = Path(output)
    if output.exists() or output.is_symlink():
        raise ValueError('Output exists; never overwrite native analytical evidence')
    resolved = output.resolve()
    if any(resolved.is_relative_to(Path(e['root']).resolve()) for e in batch['exports']):
        raise ValueError('Analytical output cannot modify an export tree')
    reader = load_reader()
    manifest = json.loads(check_pin(batch['inputs']['manifest']).read_bytes())
    scenes = json.loads(check_pin(batch['inputs']['scenes']).read_bytes())
    roles = []
    for export in batch['exports']:
        roles.append(reader.read_role_export(export['root'], export['indexSha256'], export['role'],
            manifest, scenes, expected_declaration_sha256=batch['inputs']['declaration']['sha256']))
    report = {'schema': 'w50-native-batch-read-1', 'ready': all(r['ready'] for r in roles),
              'instrumentRootSha256': expected_root_sha256, 'batch': root_doc['batch'],
              'contract': root_doc['contract'], 'inputs': batch['inputs'], 'exports': batch['exports'],
              'sourcePins': root_doc['sources'], 'roles': roles}
    report['status'] = 'READY' if report['ready'] else 'STOP_NATIVE_READINESS'
    raw = (json.dumps(report, indent=2, allow_nan=False)+'\n').encode()
    # Serialization precedes creation; exclusive creation prevents concurrent overwrites.
    with output.open('xb') as handle:
        handle.write(raw); handle.flush(); os.fsync(handle.fileno())
    return report


def main(argv=None):
    import sys
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ['seal']:
        parser = argparse.ArgumentParser(description='Prospective native instrument seal after approval')
        parser.add_argument('batch', type=Path)
        args = parser.parse_args(argv[1:])
        print(json.dumps(seal_native(args.batch), allow_nan=False))
        return 0
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('batch', type=Path)
    parser.add_argument('--root-sha256', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    batch, root_doc = bootstrap(args.batch, args.root_sha256)
    report = execute_batch(batch, root_doc, args.root_sha256, args.out)
    print(json.dumps({'ready': report['ready'], 'status': report['status'], 'out': str(args.out)}))
    return 0 if report['ready'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
