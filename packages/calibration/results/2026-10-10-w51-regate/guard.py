"""One permanent import/exec guard, installed before roles and retained through publication.

A source-only discovery process records exercised modules. Runtime enforcement never widens
that set, never trusts cached bytecode, and does not install a capture-only I/O boundary.
"""
import hashlib
import importlib.machinery
import importlib.metadata
import platform
from pathlib import Path
import sys


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def environment():
    if not sys.flags.isolated: raise ValueError('Execution requires Python -I')
    executable = Path(sys.executable).resolve()
    return {'python':sys.version, 'executable':str(executable), 'executableSha256':sha(executable),
            'platform':platform.platform(), 'architecture':platform.machine(),
            'packages':sorted([d.metadata['Name'],d.version] for d in importlib.metadata.distributions())}


def enforce(repo, expected):
    repo = Path(repo).resolve(); observed = {}; called_files = set()
    prefix = str(repo)+'/'
    old_code = importlib.machinery.SourceFileLoader.get_code

    def check(filename):
        path = Path(filename).resolve()
        if not path.is_relative_to(repo): return
        relative = str(path.relative_to(repo)); actual = sha(path)
        if path.suffix != '.py' or (expected is not None and expected.get(relative) != actual):
            raise ValueError('Changed or unsealed executed import: '+relative)
        observed[relative] = actual

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

    def called(frame, event, argument):
        filename = frame.f_code.co_filename
        if event == 'call' and filename.startswith(prefix) and filename not in called_files:
            check(filename); called_files.add(filename)
    sys.setprofile(called)
    return observed


def external_reads(repo, inputs, protected_roots):
    """Historical scientific files are exact static evidence, never an old execution tree.

    The root verifies their content before admission. This boundary disallows any other open
    beneath the listed historical/native roots, and disallows every write there. Source opens
    inside the current checkout remain under the permanent source guard, not this data policy.
    """
    repo = Path(repo).resolve()
    allowed = {str((repo/item['path']).absolute()):item['sha256'] for item in inputs}
    roots = [Path(p).absolute() for p in protected_roots]
    for filename, digest in allowed.items():
        p = Path(filename)
        if p.resolve() != p or any(q.is_symlink() for q in (p,*p.parents)) or sha(p) != digest:
            raise ValueError('Changed external scientific input')

    def event(name, args):
        if name != 'open' or not isinstance(args[0], (str,bytes)): return
        path = Path(args[0]).absolute()
        if not any(path.is_relative_to(root) for root in roots): return
        mode, flags = args[1], args[2]
        writing = (isinstance(mode,str) and any(c in mode for c in 'wax+')) or bool(flags & 3)
        if writing or str(path) not in allowed or path.resolve() != path:
            raise ValueError('Unbound historical/static evidence access')
    sys.addaudithook(event)
