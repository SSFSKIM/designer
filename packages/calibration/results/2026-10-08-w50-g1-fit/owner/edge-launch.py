"""Fixed bridge subprocess entry. Stdlib bootstrap precedes edge.py and numpy/PIL imports."""
import hashlib
import json
import os
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]


def checked(path, expected):
    path = Path(path)
    if not path.is_absolute() or path.resolve() != path:
        raise ValueError('Noncanonical Python bootstrap pin')
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError('Changed Python bootstrap source/root')
    return raw


def main():
    args = sys.argv[1:]
    if args[:3] != ['-I', '-B', str(HERE/'edge.py')] or args[3:] not in ([], ['--contracts']):
        raise ValueError('Guarded Python accepts only the fixed owner edge entrypoint')
    instrument = os.environ['W50_OWNER_INSTRUMENT']
    registered = os.environ['W50_OWNER_ROOT_SHA256']
    doc = json.loads(checked(instrument, registered))
    closure = json.loads(checked(doc['closure']['path'], doc['closure']['sha256']))
    sources = {}
    for pin in closure['sources']:
        rel = pin['path']
        if Path(rel).is_absolute() or '..' in Path(rel).parts or rel in sources:
            raise ValueError('Malformed Python source closure')
        checked(ROOT/rel, pin['sha256'])
        sources[rel] = pin['sha256']
    run = HERE/'run.py'
    raw = checked(run, sources[str(run.relative_to(ROOT))])
    module = types.ModuleType('owner_bootstrap')
    module.__file__ = str(run)
    exec(compile(raw, str(run), 'exec', dont_inherit=True), module.__dict__)
    validated, _, sources = module.validate(instrument, registered, occupied=True)
    if module.environment() != validated['pythonEnvironment']:
        raise ValueError('Changed edge Python numerical environment')
    module.live_python_guard(sources)
    # No edge or nonstdlib code has executed before the live guard is installed.
    edge = HERE/'edge.py'
    sys.argv = [str(edge), *args[3:]]
    namespace = {'__name__': '__main__', '__file__': str(edge)}
    exec(compile(edge.read_bytes(), str(edge), 'exec', dont_inherit=True), namespace)


if __name__ == '__main__':
    main()
