#!/Users/new/vitrea-w49/py/bin/python -I
"""Discover executed/imported Python source closure in an isolated, source-only subprocess.

The probe is an executable dry exercise of the instrument, not a list of guessed imports.
Git mode checks repository code BEFORE execution. Expected mode does the same against a
prospective closure. Source-only loading excludes stale repository bytecode caches.
"""
import argparse
import hashlib
import importlib.machinery
import importlib.metadata
import json
from pathlib import Path
import platform
import runpy
import subprocess
import sys

PYTHON = Path('/Users/new/vitrea-w49/py/bin/python')
HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def environment():
    if Path(sys.executable).absolute() != PYTHON or not sys.flags.isolated or platform.machine() != 'arm64':
        raise ValueError('Requires pinned arm64 interpreter with -I')
    return {'python': sys.version, 'executable': str(PYTHON),
            'executableSha256': sha(PYTHON.resolve()), 'architecture': platform.machine(),
            'platform': platform.platform(), 'isolated': True,
            'packages': {name: importlib.metadata.version(name) for name in ('numpy', 'scipy', 'Pillow')}}


def git_bytes(root, commit, relative):
    result = subprocess.run(['git', '-C', str(root), 'show', f'{commit}:{relative}'],
                            capture_output=True)
    if result.returncode:
        raise ValueError(f'No seal bytes for {relative} at {commit}')
    return result.stdout


def collect(root, probe, commit=None, expected=None):
    root, probe = Path(root).resolve(), Path(probe).resolve()
    sources, checked, seen_paths = {}, set(), set()
    harness_files = {str(HERE / 'closure.py')}
    if commit and probe.is_relative_to(HERE):
        # The post-seal dry probe is additive harness code, reported separately by its hash.
        # Prospective mode includes a wave's probe in the closure it is about to seal.
        harness_files.add(str(probe))
    root_prefix = str(root) + '/'

    def check(path):
        raw_path = str(path)
        if raw_path in seen_paths:
            return
        path = Path(path).resolve()
        seen_paths.add(raw_path)
        if not path.is_relative_to(root) or str(path) in harness_files:
            return
        relative = str(path.relative_to(root))
        if path.suffix != '.py':
            raise ValueError(f'Non-source repository execution: {relative}')
        if relative not in checked:
            digest = sha(path)
            if commit and hashlib.sha256(git_bytes(root, commit, relative)).hexdigest() != digest:
                raise ValueError(f'Changed seal bytes: {relative}')
            if expected is not None and expected.get(relative) != digest:
                raise ValueError(f'Changed or unsealed closure source: {relative}')
            sources[relative] = digest
            checked.add(relative)

    old_code = importlib.machinery.SourceFileLoader.get_code

    def source_code(loader, name):
        file = Path(loader.get_filename(name)).resolve()
        if file.is_relative_to(root):
            check(file)
            return compile(file.read_bytes(), str(file), 'exec', dont_inherit=True)
        return old_code(loader, name)

    importlib.machinery.SourceFileLoader.get_code = source_code

    def event(name, args):
        if name == 'exec':
            filename = args[0].co_filename
            if not filename.startswith('<'):
                check(filename)

    sys.addaudithook(event)
    # Function calls also name importlib-loaded modules absent from sys.modules.
    def called(frame, event, arg):
        filename = frame.f_code.co_filename
        if event == 'call' and filename.startswith(root_prefix) and filename not in harness_files:
            check(filename)
    sys.setprofile(called)
    try:
        runpy.run_path(str(probe), run_name='closure_probe')
        for module in list(sys.modules.values()):
            path = getattr(module, '__file__', None)
            if path and Path(path).suffix == '.py':
                check(path)
    finally:
        sys.setprofile(None)
        importlib.machinery.SourceFileLoader.get_code = old_code
    if expected is not None and sources != expected:
        raise ValueError('Executed/imported closure membership differs from seal')
    return {'sources': dict(sorted(sources.items())), 'environment': environment(),
            'probeSha256': sha(probe), 'discovery': 'source-only imports + exec audit + function calls',
            'pixels': 'NONE: synthetic instrument exercise'}


def enforce(root, expected):
    """Install the prospective closure gate in the ACTUAL renderer/reader process.

    A preflight dry probe discovers a closure; it cannot silently authorise another import
    branch on the real run. Check every later repository module before it executes, including
    spec_from_file_location loads. The guard is intentionally permanent for this process.
    """
    root = Path(root).resolve()
    helper = Path(__file__).resolve()
    helper_sha = sha(helper)
    previous = importlib.machinery.SourceFileLoader.get_code

    def checked(path):
        path = Path(path).resolve()
        if not path.is_relative_to(root):
            return
        relative = str(path.relative_to(root))
        wanted = helper_sha if path == helper else expected.get(relative)
        if wanted is None or path.suffix != '.py' or sha(path) != wanted:
            raise ValueError(f'Changed or unsealed executed import: {relative}')

    def source_code(loader, name):
        path = Path(loader.get_filename(name)).resolve()
        if path.is_relative_to(root):
            checked(path)
            return compile(path.read_bytes(), str(path), 'exec', dont_inherit=True)
        return previous(loader, name)

    importlib.machinery.SourceFileLoader.get_code = source_code

    def event(name, args):
        if name == 'exec' and not args[0].co_filename.startswith('<'):
            checked(args[0].co_filename)
    sys.addaudithook(event)


def discover(root, probe, commit=None, expected=None):
    args = [str(PYTHON), '-I', '-B', str(HERE / 'closure.py'), '--root', str(root), '--probe', str(probe)]
    if commit:
        args += ['--commit', commit]
    result = subprocess.run(args, input=json.dumps(expected), capture_output=True, text=True)
    if result.returncode:
        raise ValueError(result.stderr.strip() or result.stdout.strip())
    return json.loads(result.stdout)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--probe', type=Path, required=True)
    parser.add_argument('--commit')
    args = parser.parse_args()
    expected = json.loads(sys.stdin.read())
    print(json.dumps(collect(args.root, args.probe, args.commit, expected), indent=2))
