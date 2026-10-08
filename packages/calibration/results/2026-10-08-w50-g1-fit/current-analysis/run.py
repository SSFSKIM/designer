#!/usr/bin/env python3
"""Prospective completed-current reader. No live context, rendering or numerical admission.

build_template(current, native_reports, output) runs only AFTER both authorised current
batches complete, verifies their full chains and returns a concrete config (never dummy pins).
Write that config once to CONFIG, review it, then seal_config(). Sealing discovers/exercises
sources on synthetic data only. execute(root_sha256) requires the externally admitted root
hash and writes the fixed external result once. None of these acts happens on import.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import types

HERE = Path(__file__).resolve().parent
FIT = HERE.parent
REPO = HERE.parents[4]
G0 = FIT.parent/'2026-10-08-w50-g0-declaration'
CONFIG = HERE/'read-config.json'
INSTRUMENT = HERE/'instrument-root.json'
PROBE = HERE/'probe.py'
GUARD = G0/'audit/closure.py'
KEY = ('profile', 'renderer', 'scene', 'statistic')


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    def invalid(value): raise ValueError('Nonfinite JSON: '+value)
    return json.loads(Path(path).read_bytes(), parse_constant=invalid)


def pin(repo, path):
    return {'path': str(Path(path).relative_to(repo)), 'sha256': sha(path)}


def pin_shape(item):
    if not isinstance(item, dict) or set(item) != {'path', 'sha256'} or \
            not isinstance(item['path'], str) or not re.fullmatch('[0-9a-f]{64}', item.get('sha256', '')):
        raise ValueError('Missing exact full content pin')


def ordinary(path):
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('Ordinary absolute path required')
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('Source and evidence symlinks are refused')
    return path


def checked(repo, item):
    pin_shape(item)
    relative = Path(item['path'])
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('Repository pin escapes its root')
    path = ordinary(Path(repo)/relative)
    if not path.is_file() or sha(path) != item['sha256']:
        raise ValueError('Changed or missing pinned bytes: '+item['path'])
    return path


def sidecar(path):
    path = ordinary(Path(path)); side = ordinary(Path(str(path)+'.sha256'))
    if side.read_text() != f'{sha(path)}  {path.name}\n':
        raise ValueError('Changed prospective sidecar')
    return side


def source(path, name):
    value = types.ModuleType(name); value.__file__ = str(path)
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), value.__dict__)
    return value


def write_once(path, value):
    raw = (json.dumps(value, indent=2, allow_nan=False)+'\n').encode()
    with ordinary(Path(path)).open('xb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())


def metadata(config):
    """Stdlib input/source identity checks; never open native reports or capture artifacts."""
    if set(config) != {'schema', 'current', 'native', 'originals', 'output'} or \
            config['schema'] != 'w50-completed-current-config-1':
        raise ValueError('Unknown completed-current config')
    current = config['current']
    if set(current) != {'instrument', 'results'} or len(current['results']) != 2:
        raise ValueError('Both fixed completed current result pins are required')
    root_path = checked(REPO, current['instrument']); root = load(root_path)
    sidecar(root_path)
    if root.get('schema') != 'w50-g1-current-instrument-root-1' or root.get('repo') != str(REPO) \
            or len(root.get('currentBatches', [])) != 2:
        raise ValueError('A same-repository authorised current-only root is required')
    bootstrap = checked(REPO, root['bootstrap'])
    if bootstrap != root_path.parent/'dispatch.py':
        raise ValueError('Current root bootstrap differs from its sibling source interface')
    sources = root['closure']['sources']
    for path, digest in sources.items(): checked(REPO, {'path': path, 'sha256': digest})
    for item in (root['bootstrap'], root['probe']):
        checked(REPO, item)
        if sources.get(item['path']) != item['sha256']:
            raise ValueError('Current bootstrap/probe is outside its sealed closure')
    for result in current['results']: pin_shape(result)
    native = config['native']
    if set(native) != {'instrument', 'contract', 'batch', 'reports'} or \
            set(native['reports']) != {'calibration', 'validation'}:
        raise ValueError('Only the exact two exposed native role reports are admitted')
    for role_pin in native['reports'].values():
        pin_shape(role_pin)
        if Path(role_pin['path']).is_absolute() or '..' in Path(role_pin['path']).parts \
                or not role_pin['path'].endswith('.json.gz'):
            raise ValueError('Native role report needs an exact repository gzip pin')
    for name, filename in (('instrument', 'instrument-root.json'), ('contract', 'execution-contract.json'),
                           ('batch', 'read-batch.json')):
        if checked(REPO, native[name]) != FIT/'native'/filename:
            raise ValueError('Original native run contract/batch selection changed')
    nroot = load(checked(REPO, native['instrument']))
    contract = load(checked(REPO, native['contract']))
    batch = load(checked(REPO, native['batch']))
    sidecar(FIT/'native/instrument-root.json'); sidecar(FIT/'native/execution-contract.json')
    if nroot.get('schema') != 'w50-native-instrument-root-1' or nroot['batch'] != native['batch'] \
            or nroot['contract'] != native['contract'] or nroot['inputs'] != batch['inputs'] \
            or contract['batch'] != native['batch']:
        raise ValueError('Native contract/root/batch chain differs')
    for path, digest in nroot['sources'].items(): checked(REPO, {'path': path, 'sha256': digest})
    if not all(nroot['sources'].get(path) == digest for path, digest in contract['closure']['sources'].items()):
        raise ValueError('Native source contract differs from its root')
    if [(e['role']) for e in batch['exports']] != ['calibration', 'validation']:
        raise ValueError('Blind native I/O is not admitted')
    originals = config['originals']
    expected = {'references': root['references'], 'scenes': batch['inputs']['scenes']}
    for name, item in expected.items():
        if originals.get(name) != item: raise ValueError('Original G0 selection changed')
    if set(originals) != {'references', 'scenes', 'canonicalScenes'}:
        raise ValueError('Incomplete original G0 reference/scene pins')
    for item in originals.values(): checked(REPO, item)
    if checked(REPO, originals['canonicalScenes']) != REPO/'apps/reference-apple/scenes.json':
        raise ValueError('Canonical scene source changed')
    for part_name in ('partOne', 'partTwo'):
        part = load(checked(REPO, root[part_name]))
        if any(item not in part['sources'] for item in originals.values()):
            raise ValueError('Original reference/scene pins absent from immutable G0')
    output = ordinary(Path(config['output']))
    protected = [REPO, *[ordinary(Path(e['root'])) for e in batch['exports']]]
    if any(output.is_relative_to(p) for p in protected):
        raise ValueError('Result must be external scratch outside every source tree')
    return root_path, root, batch


def discover(current=None):
    """Exercise the configured root's actual bootstrap; the default is synthetic development only."""
    bootstrap, probe = FIT/'execution/dispatch.py', FIT/'current_probe.py'
    if current is not None:
        root_path = checked(REPO, current['instrument']); root = load(root_path)
        bootstrap = checked(REPO, root['bootstrap']); probe = checked(REPO, root['probe'])
        if bootstrap != root_path.parent/'dispatch.py':
            raise ValueError('Current root bootstrap selection differs')
        for path, digest in root['closure']['sources'].items():
            checked(REPO, {'path': path, 'sha256': digest})
        for item in (root['bootstrap'], root['probe']):
            if root['closure']['sources'].get(item['path']) != item['sha256']:
                raise ValueError('Current bootstrap/probe is outside its sealed closure')
    guard = source(GUARD, 'w50_current_discovery')
    selection = {'W50_CURRENT_ANALYSIS_BOOTSTRAP': str(bootstrap),
                 'W50_CURRENT_ANALYSIS_PROBE': str(probe)}
    previous = {name: os.environ.get(name) for name in selection}
    try:
        os.environ.update(selection)
        result = guard.discover(REPO, PROBE)
    finally:
        for name, value in previous.items():
            if value is None: os.environ.pop(name, None)
            else: os.environ[name] = value
    for path in (bootstrap, probe):
        if result['sources'].get(str(path.relative_to(REPO))) != sha(path):
            raise ValueError('Selected current bootstrap/probe was not exercised')
    result['sources'][str(GUARD.relative_to(REPO))] = sha(GUARD)
    return result


def enforce(closure):
    for path, digest in closure['sources'].items(): checked(REPO, {'path': path, 'sha256': digest})
    guard = source(GUARD, 'w50_current_guard')
    if guard.environment() != closure['environment']:
        raise ValueError('Completed-current interpreter/package environment changed')
    guard.enforce(REPO, closure['sources'])


def build_template(current, native_reports, output):
    """Build real prospective pins only from a complete verified current result chain.

    This is a later read operation, not an operation to run while capture is in progress.
    Native report pins are supplied explicitly; no report/path discovery or latest selection.
    The returned config is not a seal. No native report, export or PNG is decoded here.
    """
    closure = discover(current); enforce(closure)
    root = load(checked(REPO, current['instrument']))
    batch_pin = pin(REPO, FIT/'native/read-batch.json'); batch = load(checked(REPO, batch_pin))
    part = load(checked(REPO, root['partOne']))
    canonical = next(p for p in part['sources'] if p['path'] == 'apps/reference-apple/scenes.json')
    config = dict(schema='w50-completed-current-config-1', current=current,
        native=dict(instrument=pin(REPO, FIT/'native/instrument-root.json'),
            contract=pin(REPO, FIT/'native/execution-contract.json'), batch=batch_pin, reports=native_reports),
        originals=dict(references=root['references'], scenes=batch['inputs']['scenes'], canonicalScenes=canonical),
        output=str(output))
    root_path, _, _ = metadata(config)
    reader = source(HERE/'analysis.py', 'w50_current_template_reader')
    reader.completed(config, root_path)
    return config


def seal_config():
    """Prospective source-only seal; deliberately never invoked in the implementation tests."""
    if INSTRUMENT.exists() or Path(str(INSTRUMENT)+'.sha256').exists():
        raise ValueError('Existing analysis root; no reseal')
    config = load(ordinary(CONFIG)); metadata(config)
    closure = discover(config['current'])
    root = dict(schema='w50-completed-current-root-1', config=pin(REPO, CONFIG),
                entrypoint=pin(REPO, Path(__file__)), probe=pin(REPO, PROBE), closure=closure)
    write_once(INSTRUMENT, root)
    with Path(str(INSTRUMENT)+'.sha256').open('x') as stream:
        stream.write(f'{sha(INSTRUMENT)}  {INSTRUMENT.name}\n'); stream.flush(); os.fsync(stream.fileno())
    return {'instrumentRootSha256': sha(INSTRUMENT)}


def admit_root(path, external_sha256, *, repo=REPO):
    path = ordinary(Path(path))
    if not re.fullmatch('[0-9a-f]{64}', external_sha256) or sha(path) != external_sha256:
        raise ValueError('Analysis root differs from external registered hash')
    sidecar(path); root = load(path)
    if root.get('schema') != 'w50-completed-current-root-1': raise ValueError('Unknown analysis root')
    guard_relative = str(GUARD.relative_to(REPO))
    if guard_relative not in root.get('closure', {}).get('sources', {}):
        raise ValueError('Analysis root omitted its source-only guard pin')
    for item in (root['config'], root['entrypoint'], root['probe']): checked(repo, item)
    for name, digest in root['closure']['sources'].items(): checked(repo, {'path': name, 'sha256': digest})
    for item in (root['entrypoint'], root['probe']):
        if root['closure']['sources'].get(item['path']) != item['sha256']:
            raise ValueError('Bootstrap entrypoint/probe absent from exercised closure')
    return root


def execute(external_sha256):
    root = admit_root(INSTRUMENT, external_sha256)
    if checked(REPO, root['config']) != CONFIG or checked(REPO, root['entrypoint']) != Path(__file__) \
            or checked(REPO, root['probe']) != PROBE:
        raise ValueError('Analysis root substituted its fixed config/entrypoint/probe')
    config = load(CONFIG); root_path, _, _ = metadata(config)
    output = ordinary(Path(config['output']))
    if output.exists(): raise ValueError('Completed-current evidence result exists')
    enforce(root['closure'])
    reader = source(HERE/'analysis.py', 'w50_completed_current_reader')
    result = reader.read_completed(config, root_path)
    result.update(instrumentRootSha256=external_sha256, config=root['config'], sourcePins=root['closure']['sources'])
    write_once(output, result)
    return {'status': result['status'], 'output': str(output), 'sha256': sha(output)}


def source_probe(bootstrap, probe):
    # Execute the root's content-pinned dry exercise, not a guessed sibling import list.
    # Loading its dispatcher does not invoke root_doc or read replacement-attempt evidence.
    source(bootstrap, 'w50_current_probe_dispatch')
    source(probe, 'w50_current_probe_original')
    native = source(FIT/'native/run.py', 'w50_current_probe_native_contract')
    native.dry_exercise()
    source(G0/'audit/next_wave.py', 'w50_current_probe_native_referee')
    source(HERE/'analysis.py', 'w50_current_probe_analysis').source_probe()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('probe', 'seal', 'read'))
    parser.add_argument('--root-sha256')
    args = parser.parse_args()
    if args.command == 'probe': result = discover()
    elif args.command == 'seal': result = seal_config()
    elif args.root_sha256: result = execute(args.root_sha256)
    else: parser.error('read requires the external --root-sha256')
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__': main()
