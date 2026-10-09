"""Stdlib-first live edge route; no dependency on the sealed current-only instrument."""
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]


def checked(path, digest):
    path = Path(path)
    if not path.is_absolute() or path.resolve() != path:
        raise ValueError('Noncanonical live Python source')
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != digest:
        raise ValueError('Changed live Python source/config')
    return raw


def edge_images(request, inputs, snapshot):
    """No blanket PNG permission: one candidate and its source-owned same-cell references."""
    profile, scene = request['identity']
    key = f'{profile}/webgpu/{scene}'
    records = [record for bundle in (snapshot['gateCaptures'], snapshot['exposureCaptures'])
               for record in bundle['captures'] if record.get('sceneSource') == 'canonical'
               and record.get('lane') == 'candidate' and record.get('profile') == profile
               and record.get('scene') == scene and record.get('renderer') == 'webgpu']
    def identity(item):
        return (str((ROOT/item['path']).resolve()), item['sha256'])
    if len(records) != 1 or identity(records[0]['candidate']) not in map(identity, snapshot['cohort']):
        raise ValueError('Edge image lacks a unique same-cohort candidate record')
    current = inputs['captures'][key]
    reference = inputs['referenceCaptures'][key] if profile.endswith('-glass0.25') else current
    expected = {'native': current['native'], 'current': reference['web'],
                'candidate': records[0]['artifacts']['png']}
    if any(request.get(role) != item for role, item in expected.items()):
        raise ValueError('Edge image pin differs from same-cell frozen/candidate authority')
    admitted = {}
    for item in expected.values():
        checked(item['path'], item['sha256'])
        admitted[item['path']] = item['sha256']
    return admitted


def main():
    edge = HERE.parent/'owner/edge.py'
    if sys.argv[1:4] != ['-I', '-B', str(edge)] or sys.argv[4:] not in ([], ['--contracts']):
        raise ValueError('Live Python only admits the fixed source-owned edge entrypoint')
    config = json.loads(checked(os.environ['W50_OWNER_LIVE_CONFIG'],
                               os.environ['W50_OWNER_LIVE_CONFIG_SHA256']))
    if config['python'] != str(HERE/'live-python-shim') or not sys.flags.isolated:
        raise ValueError('Live Python shim/isolated mode changed')
    interpreter = config['interpreter']
    checked(interpreter['path'], interpreter['sha256'])
    launch, prefix = config['pythonLaunch'], config['pythonPrefix']
    if not isinstance(launch, str) or not os.path.isabs(launch) \
            or os.path.normpath(launch) != launch or Path(launch).resolve() != Path(interpreter['path']) \
            or sys.executable != launch or os.environ['W50_OWNER_LIVE_PYTHON'] != launch:
        raise ValueError('Live Python launch differs from prospective config')
    venv_config = config['pythonVenvConfig']
    checked(venv_config['path'], venv_config['sha256'])
    if not isinstance(prefix, str) or not os.path.isabs(prefix) \
            or str(Path(prefix).resolve()) != prefix or Path(launch).parent != Path(prefix)/'bin' \
            or venv_config['path'] != str(Path(prefix)/'pyvenv.cfg') \
            or sys.prefix != prefix or sys.prefix == sys.base_prefix:
        raise ValueError('Live Python prefix/config differs from prospective config')
    closure_pin = config['runtimeClosure']
    closure = json.loads(checked(closure_pin['path'], closure_pin['sha256']))
    if closure.get('exercise') != 'synthetic source-only':
        raise ValueError('Live Python requires the separately exercised Node/edge closure')
    sources = {}
    for item in closure['sources']:
        rel = item['path']
        if Path(rel).is_absolute() or '..' in Path(rel).parts or rel in sources:
            raise ValueError('Malformed live Python runtime closure')
        checked(ROOT/rel, item['sha256']); sources[rel] = item['sha256']
    def source(path):
        return checked(path, sources[str(path.relative_to(ROOT))])
    source(Path(__file__).resolve()); source(HERE/'live-python-shim')
    guard_path = HERE.parent/'execution/guard.py'
    guard = types.ModuleType('w50_owner_live_edge_guard')
    guard.__file__ = str(guard_path)
    exec(compile(source(guard_path), str(guard_path), 'exec', dont_inherit=True), guard.__dict__)
    guard.enforce(ROOT, sources)
    if int(os.environ['W50_OWNER_LIVE_NODE_PID']) != os.getppid():
        raise ValueError('Edge child is not owned by the live Node bootstrap')
    images = {}
    if sys.argv[4:] != ['--contracts']:
        snapshot = json.loads(checked(os.environ['W50_OWNER_LIVE_SNAPSHOT'],
                                     os.environ['W50_OWNER_LIVE_SNAPSHOT_SHA256']))
        if snapshot['config'] != {'path': os.environ['W50_OWNER_LIVE_CONFIG'],
                                  'sha256': os.environ['W50_OWNER_LIVE_CONFIG_SHA256']}:
            raise ValueError('Edge snapshot config changed')
        inputs_pin = config['ownerInputs']
        inputs = json.loads(checked(inputs_pin['path'], inputs_pin['sha256']))
        request = json.load(sys.stdin)
        images = edge_images(request, inputs, snapshot)
        sys.stdin = io.StringIO(json.dumps(request, allow_nan=False))
    # Import enforcement alone misses historical AST readers. Check repository Python
    # source opens too, before importing edge.py, numpy or PIL. Data reads remain data.
    active = False
    def read_guard(name, args):
        nonlocal active
        if active or name != 'open' or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        path = Path(os.fsdecode(args[0])).resolve()
        image = path.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp')
        if not image and (not path.is_relative_to(ROOT) or path.suffix not in ('.py', '.pyc', '.so')):
            return
        active = True
        try:
            if image:
                if str(path) not in images:
                    raise ValueError('Unadmitted live edge image')
                checked(path, images[str(path)])
            elif path.suffix != '.py':
                raise ValueError('Unsealed compiled Python source')
            else:
                source(path)
        finally:
            active = False
    sys.addaudithook(read_guard)
    if guard.environment() != config['pythonEnvironment']:
        raise ValueError('Live edge numerical Python environment changed')
    sys.argv = [str(edge), *sys.argv[4:]]
    exec(compile(source(edge), str(edge), 'exec', dont_inherit=True),
         {'__name__': '__main__', '__file__': str(edge)})


if __name__ == '__main__':
    main()
