#!/Users/new/vitrea-w49/py/bin/python -I
"""Executable prospective template: seal a batch and exercised import closure, then bind launch.

The next wave's ROOT declaration must pin this contract AND its .sha256 before any render.
The probe must import the registered renderer and dry-exercise its planner and measurement
routes. Closure verification refuses changed, newly imported or no-longer-exercised sources.
There is no amendment/rehash path and render never substitutes a caller's own finite domain.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('next_closure', HERE / 'closure.py')
K = importlib.util.module_from_spec(spec)
spec.loader.exec_module(K)


def relative(root, path):
    return str(Path(path).resolve().relative_to(Path(root).resolve()))


def helpers():
    return {name: K.sha(HERE / name) for name in ('next_wave.py', 'closure.py')}


def seal(root, batch, probe, renderer, out):
    root, out = Path(root).resolve(), Path(out).resolve()
    sidecar = Path(str(out) + '.sha256')
    if out.exists() or sidecar.exists():
        raise ValueError('Existing prospective seal: no amendment or rehash')
    closure = K.discover(root, probe)
    renderer_rel = relative(root, renderer)
    if renderer_rel not in closure['sources']:
        raise ValueError('Probe must import/dry-exercise the registered renderer')
    doc = {'schema': 'batch-import-closure-1', 'batch': {'path': relative(root, batch), 'sha256': K.sha(batch)},
           'renderer': renderer_rel, 'probe': relative(root, probe), 'closure': closure,
           'guardSources': helpers()}
    text = json.dumps(doc, indent=2, allow_nan=False) + '\n'
    with out.open('x') as handle:
        handle.write(text)
    with sidecar.open('x') as handle:
        handle.write(f'{K.sha(out)}  {out.name}\n')
    return doc


def verify(path, root, supplied):
    path, root = Path(path).resolve(), Path(root).resolve()
    if Path(str(path) + '.sha256').read_text() != f'{K.sha(path)}  {path.name}\n':
        raise ValueError('Contract differs from prospective seal')
    doc = json.loads(path.read_text())
    if doc.get('schema') != 'batch-import-closure-1' or doc.get('guardSources') != helpers():
        raise ValueError('Changed guard/closure helper bytes')
    registered = (root / doc['batch']['path']).resolve()
    if not registered.is_relative_to(root) or K.sha(registered) != doc['batch']['sha256'] or \
            Path(supplied).read_bytes() != registered.read_bytes():
        raise ValueError('Supplied bytes are not the sealed batch')
    for rel, wanted in doc['closure']['sources'].items():
        source = (root / rel).resolve()
        if not source.is_relative_to(root) or K.sha(source) != wanted:
            raise ValueError(f'Changed closure source: {rel}')
    probe = (root / doc['probe']).resolve()
    renderer = (root / doc['renderer']).resolve()
    if not probe.is_relative_to(root) or not renderer.is_relative_to(root):
        raise ValueError('Escaped closure entrypoint')
    actual = K.discover(root, probe, expected=doc['closure']['sources'])
    if actual != doc['closure']:
        raise ValueError('Closure/environment differs from prospective seal')
    return doc, registered, renderer


def render(path, root, supplied, arguments):
    doc, registered, renderer = verify(path, root, supplied)
    # The registered path is supplied as argv[1]. Reject a second batch/argument parser escape;
    # the wave's renderer contract is a single positional batch followed by option arguments.
    if any(arg.split('=', 1)[0] in ('--batch', '--contract') for arg in arguments):
        raise ValueError('A launch cannot override its sealed batch/contract')
    return subprocess.run([str(K.PYTHON), '-I', '-B', str(renderer), str(registered), *arguments],
                          cwd=Path(root).resolve(), check=True).returncode


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('seal', 'verify', 'render'))
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--batch', type=Path, required=True)
    parser.add_argument('--probe', type=Path)
    parser.add_argument('--renderer', type=Path)
    parser.add_argument('--contract', type=Path, required=True)
    args, extra = parser.parse_known_args()
    if args.command != 'render' and extra:
        parser.error('Unexpected arguments')
    if args.command == 'seal':
        if not args.probe or not args.renderer:
            parser.error('seal requires --probe and --renderer')
        seal(args.root, args.batch, args.probe, args.renderer, args.contract)
    elif args.command == 'verify':
        verify(args.contract, args.root, args.batch)
    else:
        arguments = extra[1:] if extra[:1] == ['--'] else extra
        render(args.contract, args.root, args.batch, arguments)
