"""Source-only closure discovery and permanent enforcement, following G0's guard.

Discovery exercises a synthetic probe, not a manifest of guessed imports. Enforcement
is installed in the actual adapter process as well: a late spec_from_file_location or
normal import cannot execute a changed/new repository source, or a stale .pyc. Function
calls also catch repository modules that were already loaded before installation.
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


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def environment():
    if not sys.flags.isolated:
        raise ValueError('Execution requires an isolated interpreter (-I)')
    executable = Path(sys.executable).resolve()
    return {'python': sys.version, 'executable': str(executable),
            'executableSha256': sha(executable), 'architecture': platform.machine(),
            'platform': platform.platform(), 'isolated': True,
            'packages': sorted([d.metadata['Name'], d.version]
                               for d in importlib.metadata.distributions())}


def enforce(repo, expected):
    repo = Path(repo).resolve()
    observed = {}
    prefix = str(repo) + '/'
    old_code = importlib.machinery.SourceFileLoader.get_code

    def check(filename):
        path = Path(filename).resolve()
        if not path.is_relative_to(repo):
            return
        relative = str(path.relative_to(repo))
        if path.suffix != '.py' or expected.get(relative) != sha(path):
            raise ValueError(f'Changed or unsealed executed import: {relative}')
        observed[relative] = expected[relative]

    # Guard bytes themselves are part of the root, not implicitly trusted by discovery.
    check(__file__)

    def source_code(loader, name):
        path = Path(loader.get_filename(name)).resolve()
        if path.is_relative_to(repo):
            check(path)
            return compile(path.read_bytes(), str(path), 'exec', dont_inherit=True)
        return old_code(loader, name)

    importlib.machinery.SourceFileLoader.get_code = source_code

    def event(name, args):
        if name == 'exec' and not args[0].co_filename.startswith('<'):
            check(args[0].co_filename)
    sys.addaudithook(event)

    # Existing modules also join discovery. Per-function hashing would dominate the dense
    # numerical sweep; actual import/exec events above ALWAYS hash, including later loads.
    called_files = set()
    def called(frame, event, arg):
        filename = frame.f_code.co_filename
        if event == 'call' and filename.startswith(prefix) and filename not in called_files:
            check(filename)
            called_files.add(filename)
    sys.setprofile(called)
    return observed


def discover(repo, probe, expected):
    result = subprocess.run([sys.executable, '-I', '-B', str(Path(__file__).resolve()),
                             str(Path(repo).resolve()), str(Path(probe).resolve())],
                            input=json.dumps(expected), capture_output=True, text=True)
    if result.returncode:
        raise ValueError(result.stderr.strip() or result.stdout.strip())
    return json.loads(result.stdout)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repo', type=Path)
    parser.add_argument('probe', type=Path)
    args = parser.parse_args()
    expected = json.loads(sys.stdin.read())
    observed = enforce(args.repo, expected)
    runpy.run_path(str(args.probe), run_name='w50_synthetic_probe')
    if observed != expected:
        raise ValueError(f'Unexercised closure pins: {sorted(set(expected) - set(observed))}')
    print(json.dumps({'sources': dict(sorted(observed.items())), 'environment': environment(),
                      'probeSha256': sha(args.probe), 'exercise': 'synthetic source-only'}))
