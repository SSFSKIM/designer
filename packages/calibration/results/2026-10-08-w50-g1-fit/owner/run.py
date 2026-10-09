#!/Users/new/vitrea-w49/py/bin/python -I
"""Prospective owner launcher; no root, seal verb, or measurement is created by this source.

A separately reviewed root fixes one bridge request, complete PrepareInputs, original G0
640-cell membership, source closure, numerical environment, Node executable and fresh external
stdout path. Invocation requires its EXTERNALLY registered full SHA-256. Bootstrap is stdlib
only, including every source/input check. Node and the Python edge child install live guards
before helper imports. A discovery closure is not a root or authorization to run this command.

Run only after the missing immutable inputs and root have been independently admitted:
  python -I -B owner/run.py ROOT --root-sha256 REGISTERED_HASH
There are no request, output, interpreter or row overrides. Failed execution retains its
exclusively reserved output file; inspect it rather than deleting it and retrying invisibly.
"""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
G0 = 'packages/calibration/results/2026-10-08-w50-g0-declaration'
INVENTORY = ROOT/G0/'references.json'
INVENTORY_SHA256 = 'a666c1b00f4b1aff48bddeca9dacc1c1bc05dcf83bf908efddbe46c24c322d0c'
METADATA_SHA256 = '093ea234780182665100b59a6aca5f35b44b1be2d5f661afdab5700bd354c684'
PYTHON = '/Users/new/vitrea-w49/py/bin/python'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
        raise ValueError('Expected full lowercase SHA-256')
    return value


def file_path(value):
    path = Path(value)
    if not path.is_absolute() or str(path) != value or '..' in path.parts:
        raise ValueError('Expected canonical absolute path')
    if path.resolve() != path or not path.is_file():
        raise ValueError('Missing file or source/input symlink: '+value)
    return path


def check_pin(pin):
    if not isinstance(pin, dict) or set(pin) != {'path', 'sha256'}:
        raise ValueError('Expected complete content pin')
    path = file_path(pin['path'])
    if sha(path) != digest(pin['sha256']):
        raise ValueError('Changed pinned bytes: '+str(path))
    return path


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON key: '+key)
            result[key] = value
        return result
    def invalid(value):
        raise ValueError('Nonfinite JSON: '+value)
    return json.loads(Path(path).read_bytes(), object_pairs_hook=unique, parse_constant=invalid)


def required_sources():
    owner = ['run.py', 'edge-launch.py', 'python-shim', 'node-guard.mjs', 'discover.mjs',
             'bridge.ts', 'witness.ts', 'api.ts', 'referee.ts', 'source.ts', 'intrinsic.ts', 'edge.py',
             'metadata.py', 'byte_witness.py']
    return [*(HERE/name for name in owner), HERE.parent/'web/node-guard.mjs',
            HERE.parent/'web/vite-guard.mjs', ROOT/G0/'audit/closure.py',
            ROOT/'pnpm-lock.yaml', ROOT/'package.json', ROOT/'tsconfig.base.json',
            ROOT/'packages/calibration/package.json',
            ROOT/'packages/calibration/test/adopted-thresholds.test.ts',
            ROOT/'packages/calibration/results/2026-10-07-w49a-g0-declaration/seal/seal.ts',
            *(ROOT/'packages/calibration'/path for path in [
                'results/2026-09-25-w37-g0-edge-identification/canonical.py',
                'results/2026-09-25-w37-g0b-edge-identification/canonical.py',
                'results/2026-09-25-w38-g0-rim-axis-cut/e2.py',
                'results/2026-10-06-w47-g0-operators/cuts/cuts.py'])]


def input_pins(value):
    """Check nested fixed pins without executing any decoder, AST reader or numerical helper."""
    if isinstance(value, dict):
        if 'path' in value or 'sha256' in value:
            check_pin(value)
        else:
            for child in value.values():
                input_pins(child)
    elif isinstance(value, list):
        for child in value:
            input_pins(child)


def output_path(value, occupied=False):
    path = Path(value)
    if not path.is_absolute() or str(path) != value or path.parent.resolve() != path.parent \
            or not path.parent.is_dir() or '..' in path.parts or path.is_relative_to(ROOT):
        raise ValueError('Output must be canonical fresh external scratch')
    if not occupied and (path.exists() or path.is_symlink()):
        raise ValueError('Output exists; no overwrite or retry')
    return path


def validate_witness(doc, config, sources):
    witness = read_json(check_pin(doc['inputWitness']))
    if witness.get('schema') != 'w50-owner-byte-witness-1' or witness.get('resolvedInputs') != doc['config'] \
            or witness.get('metadataConfig') != {'path': str(HERE/'inputs-metadata.json'),
                                                 'sha256': METADATA_SHA256}:
        raise ValueError('Byte witness does not bind resolved inputs and frozen original metadata')
    metadata = read_json(check_pin(witness['metadataConfig']))
    if metadata.get('schema') != 'w50-owner-inputs-metadata-1' \
            or metadata.get('inventoryPin') != doc['inventory'] or metadata.get('ownerKeys') != doc['ownerKeys']:
        raise ValueError('Original metadata membership mismatch')
    requirements = {item['path']: item for item in metadata['witnessRequirements']}
    fresh = {item['path']: item for item in witness['fresh']}
    if len(requirements) != len(metadata['witnessRequirements']) or len(fresh) != len(witness['fresh']) \
            or set(requirements) != set(fresh):
        raise ValueError('Incomplete or duplicate fresh witness population')
    for path, item in fresh.items():
        requirement = requirements[path]
        if item.get('historicalCaptureTimePin') is not False or item.get('witnessKind') != 'prospective-byte-only' \
                or any(item.get(k) != requirement.get(k) for k in ('kind', 'cells', 'authority')):
            raise ValueError('Changed fresh witness provenance')
        check_pin({'path': path, 'sha256': item['sha256']})
    def complete(value):
        if isinstance(value, dict):
            if set(value) == {'path', 'sha256'} and value['sha256'] is None:
                if value['path'] not in fresh:
                    raise ValueError('Missing fresh witness for unresolved pin')
                return {'path': value['path'], 'sha256': fresh[value['path']]['sha256']}
            return {key: complete(child) for key, child in value.items()}
        if isinstance(value, list):
            return [complete(child) for child in value]
        return value
    if complete(metadata['inputs']) != config:
        raise ValueError('Resolved inputs rewrite original metadata beyond missing byte pins')
    for pin in witness['originalVerified']:
        check_pin(pin)
    for pin in witness['sourcePins'].values():
        path = check_pin(pin)
        if not path.is_relative_to(ROOT) or sources.get(str(path.relative_to(ROOT))) != pin['sha256']:
            raise ValueError('Byte witness producer missing from source closure')


def validate(instrument, expected_hash, *, occupied=False):
    """Authenticate everything before any nonstdlib/helper code executes. No real root ships."""
    instrument = file_path(str(instrument))
    if sha(instrument) != digest(expected_hash):
        raise ValueError('Owner root differs from externally registered hash')
    doc = read_json(instrument)
    fields = {'schema', 'request', 'config', 'inventory', 'ownerKeys', 'closure', 'output',
              'node', 'pythonEnvironment', 'inputWitness'}
    if set(doc) != fields or doc['schema'] != 'w50-owner-instrument-root-1':
        raise ValueError('Unknown owner root shape')
    output_path(doc['output'], occupied)
    if doc['inventory'] != {'path': str(INVENTORY), 'sha256': INVENTORY_SHA256}:
        raise ValueError('Root must bind the original inventory')
    inventory = read_json(check_pin(doc['inventory']))
    if inventory.get('schema') != 'w50-reference-inventory-1':
        raise ValueError('Unknown original inventory schema')
    keys = []
    for cell in inventory['cells']:
        if cell.get('statistic') == 'owner-contracts':
            parts = [cell.get(key) for key in ('profile', 'renderer', 'scene')]
            if any(not isinstance(p, str) or not p or '/' in p for p in parts):
                raise ValueError('Invalid original owner identity')
            keys.append('/'.join(parts))
    if len(keys) != 640 or len(set(keys)) != 640 or doc['ownerKeys'] != sorted(keys):
        raise ValueError('Owner membership differs from exact original640')
    config = read_json(check_pin(doc['config']))
    if set(config) != {'declaration', 'current', 'references', 'captures', 'referenceCaptures', 'python'} \
            or config['python'] != str(HERE/'python-shim'):
        raise ValueError('Expected complete fixed PrepareInputs and guarded Python shim, not BLOCKED metadata')
    request = read_json(check_pin(doc['request']))
    mode = request.get('mode')
    fields = {'contracts': {'mode', 'python'}, 'prepare': {'mode', 'inputsPin'},
              'project-current-batch': {'mode', 'inputsPin', 'completedReferencesPin',
                                        'contractsPin', 'inventoryPin'}}
    if mode not in fields or set(request) != fields[mode]:
        raise ValueError('Unsupported fixed owner request; no raw report or row selectors')
    if (mode == 'contracts' and request['python'] != config['python']) or \
            (mode != 'contracts' and request['inputsPin'] != doc['config']):
        raise ValueError('Fixed request config mismatch')
    if mode == 'project-current-batch' and request['inventoryPin'] != doc['inventory']:
        raise ValueError('Fixed request inventory mismatch')
    input_pins(config)
    input_pins({k: v for k, v in request.items() if k.endswith('Pin')})
    closure = read_json(check_pin(doc['closure']))
    sources = {}
    for pin in closure['sources']:
        rel = pin['path']
        if Path(rel).is_absolute() or '..' in Path(rel).parts or rel in sources:
            raise ValueError('Invalid or duplicate source closure member')
        path = check_pin({'path': str(ROOT/rel), 'sha256': pin['sha256']})
        sources[rel] = pin['sha256']
        # Module format and TS compiler resolution can change without source bytes moving.
        for directory in [path.parent, *path.parent.parents]:
            if not directory.is_relative_to(ROOT):
                break
            for name in ('package.json', 'tsconfig.json'):
                manifest = directory/name
                if manifest.exists() and str(manifest.relative_to(ROOT)) not in \
                        {p['path'] for p in closure['sources']}:
                    raise ValueError('Unsealed package/type boundary: '+str(manifest))
    if any(str(path.relative_to(ROOT)) not in sources for path in required_sources()):
        raise ValueError('Owner closure omits required bootstrap/import/dynamic reader sources')
    validate_witness(doc, config, sources)
    return doc, request, sources


def environment():
    if str(Path(sys.executable).absolute()) != PYTHON or not sys.flags.isolated \
            or platform.machine() != 'arm64':
        raise ValueError('Requires pinned arm64 interpreter with -I')
    return {'python': sys.version, 'executable': PYTHON,
            'executableSha256': sha(Path(PYTHON).resolve()), 'architecture': platform.machine(),
            'platform': platform.platform(), 'isolated': True,
            'packages': {name: importlib.metadata.version(name) for name in ('numpy', 'scipy', 'Pillow')}}


def live_python_guard(sources):
    """Check dynamic source reads too: edge.py extracts old AST functions without importing them."""
    import importlib.machinery
    active = False
    def checked(path):
        nonlocal active
        if active or not isinstance(path, (str, bytes, os.PathLike)):
            return
        path = Path(os.fsdecode(path)).resolve()
        if not path.is_relative_to(ROOT):
            return
        if path.suffix not in ('.py', '.pyc', '.so'):
            return
        active = True
        try:
            if path.suffix != '.py' or sources.get(str(path.relative_to(ROOT))) != sha(path):
                raise ValueError('Changed or unsealed Python source: '+str(path))
        finally:
            active = False
    previous = importlib.machinery.SourceFileLoader.get_code
    def source_code(loader, name):
        path = Path(loader.get_filename(name)).resolve()
        if path.is_relative_to(ROOT):
            checked(path)
            return compile(path.read_bytes(), str(path), 'exec', dont_inherit=True)
        return previous(loader, name)
    importlib.machinery.SourceFileLoader.get_code = source_code
    def event(name, args):
        if name == 'open':
            checked(args[0])
        elif name == 'exec' and not args[0].co_filename.startswith('<'):
            checked(args[0].co_filename)
    sys.addaudithook(event)


def child_environment(instrument, expected_hash, closure):
    """Pass OS storage locations, not ambient compiler, loader or executable overrides.

    A blacklist cannot enumerate future tool escape hatches. Node and Python are absolute
    pinned executables; the shim's OS utilities use a fixed system PATH. Disable tsx's
    transformed-source cache so execution derives from admitted source on each launch.
    """
    env = {key: os.environ[key] for key in ('HOME', 'TMPDIR', 'TMP', 'TEMP') if key in os.environ}
    env.update({'PATH': '/usr/bin:/bin:/usr/sbin:/sbin', 'LC_ALL': 'C', 'TSX_DISABLE_CACHE': '1',
                'W50_OWNER_INSTRUMENT': str(instrument), 'W50_OWNER_ROOT_SHA256': expected_hash,
                'W50_WEB_ROOT': str(ROOT), 'W50_WEB_CLOSURE': closure['path'],
                'W50_WEB_CLOSURE_SHA256': closure['sha256']})
    return env


def execute(instrument, expected_hash):
    doc, request, sources = validate(instrument, expected_hash)
    if environment() != doc['pythonEnvironment']:
        raise ValueError('Python numerical environment differs from root')
    node = check_pin(doc['node'])
    live_python_guard(sources)
    env = child_environment(instrument, expected_hash, doc['closure'])
    # Reserve before helpers execute. A concurrent launcher cannot both read and overwrite it.
    with output_path(doc['output']).open('xb') as output:
        process = subprocess.run([str(node), '--import', str(HERE/'node-guard.mjs'),
            '--import', 'tsx', str(HERE/'bridge.ts')], cwd=ROOT/'packages/calibration',
            env=env, input=json.dumps(request).encode(), capture_output=True)
        if process.returncode:
            raise ValueError('Guarded owner bridge failed: '+process.stderr.decode(errors='replace'))
        # Parsing validates one JSON value; preserve the bridge stdout bytes, not a caller report.
        json.loads(process.stdout, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
        output.write(process.stdout); output.flush(); os.fsync(output.fileno())
    return {'output': doc['output'], 'sha256': sha(doc['output']), 'rootSha256': expected_hash,
            'mode': request['mode']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('instrument', type=Path)
    parser.add_argument('--root-sha256', required=True)
    args = parser.parse_args()
    print(json.dumps(execute(args.instrument, args.root_sha256)))


if __name__ == '__main__':
    main()
