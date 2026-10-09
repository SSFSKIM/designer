"""DL5r clarifications 1–2: original capture reads, fresh writes, distinct provenances.

The successor context/output is never changed. The three pure validators and the instance-local
external capture _pin_bytes calls receive the original read root. receipt_binding authenticates
the ORIGINAL capture's root/contract/batch, not the new analysis's authority. The LIVE common helper's existing context-keyed cache is seeded by
its own unchanged _repeat_binding first, then holds a facade over that already-validated
helper. This is explicit dependency injection, not a source edit or source-hash substitution.
Every open within those pure calls must be an unchanged, non-symlink artifact from the complete
union. An audit boundary additionally denies writes/rename/unlink/mkdir anywhere in the original
output throughout analysis, including outside the three pure calls. It is role discipline,
not protection against another process with the same user's privileges.
"""
import os
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent


def source(path, name):
    module = types.ModuleType(name); module.__file__ = str(path)
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


W = source(HERE/'witness.py', 'w50_analysis2_read_witness')


def clean_path(path, root):
    path, root = Path(path).absolute(), Path(root).absolute()
    if not path.is_relative_to(root): raise ValueError('Read lies outside original capture root')
    for component in (path, *path.parents):
        if component.is_symlink(): raise ValueError('Capture path has a symlink component')
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('Read resolves outside original capture root')
    return path


class Boundary:
    def __init__(self, original, output, union):
        self.original, self.output = Path(original).absolute(), Path(output).absolute()
        if (self.original == self.output or self.original.is_relative_to(self.output)
                or self.output.is_relative_to(self.original)):
            raise ValueError('Read root and write root must be separate')
        self.allowed = {}
        for row in union['members']:
            for item in [*row['artifacts'], *([row['payload']] if 'payload' in row else [])]:
                path = clean_path(item['path'], self.original)
                if path in self.allowed and self.allowed[path] != item['sha256']:
                    raise ValueError('Union has conflicting artifact pins')
                if not path.is_file() or W.sha(path) != item['sha256']:
                    raise ValueError('Union artifact changed')
                self.allowed[path] = item['sha256']
        if not self.allowed: raise ValueError('Empty capture union')
        self.active = False; self.pure = False; self.hashing = False

    def __enter__(self):
        # Pillow lazily imports its PNG decoder on the first image. Those package-source reads
        # are not capture reads; finish that ordinary import before the strict pure-read scope.
        from PIL import Image
        Image.preinit()
        self.active = True
        sys.addaudithook(self._audit)
        return self

    def __exit__(self, *_): self.active = False

    def _original(self, path):
        if not isinstance(path, (str, bytes, os.PathLike)): return False
        p = Path(os.fsdecode(path)).absolute()
        return p.is_relative_to(self.original) or p.resolve().is_relative_to(self.original.resolve())

    def _audit(self, event, args):
        if not self.active or self.hashing: return
        if event == 'open':
            path, mode, flags = args
            writing = ((isinstance(mode, str) and any(c in mode for c in 'wax+'))
                       or bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)))
            if writing and self._original(path): raise ValueError('Original output is read-only')
            if self.pure:
                if writing: raise ValueError('Pure retained validator cannot write')
                p = clean_path(os.fsdecode(path), self.original)
                if p not in self.allowed: raise ValueError('Read is absent from immutable union')
                self.hashing = True
                try:
                    if W.sha(p) != self.allowed[p]: raise ValueError('Retained read pin changed')
                finally: self.hashing = False
        elif event in ('os.remove', 'os.rmdir', 'os.mkdir', 'os.rename', 'os.link', 'os.symlink',
                       'os.chmod', 'os.truncate', 'os.utime'):
            paths = args[:2] if event in ('os.rename', 'os.link', 'os.symlink') else args[:1]
            if any(self._original(path) for path in paths):
                raise ValueError('Original output is read-only')

    def read(self, callback):
        if not self.active or self.pure: raise ValueError('Invalid retained read scope')
        self.pure = True
        try: return callback()
        finally: self.pure = False


class Admission:
    def __init__(self, original, boundary, dispatcher, context):
        self.original, self.boundary = original, boundary
        self.dispatcher, self.context = dispatcher, context

    def validate_captures(self, batch, captures, output):
        self.dispatcher.require_context(self.context)
        if str(output) != str(self.boundary.output) or batch != self.context['batch']:
            raise ValueError('Retained read changed successor output or batch')
        return self.boundary.read(lambda: self.original.validate_captures(
            batch, captures, self.boundary.original))

    def validate_numerical(self, root, batch):
        self.dispatcher.require_context(self.context)
        return self.original.validate_numerical(root, batch)


class Repeat:
    def __init__(self, helper, boundary, dispatcher, context, capture_authority):
        self.helper, self.boundary = helper, boundary
        self.dispatcher, self.context = dispatcher, context
        self.capture_authority = capture_authority
        # The common pure validators use this module's existing transport/proof machinery.
        self.S = helper.S

    def read_pair(self, context, run, record, pair_pin):
        if context is not self.context: raise ValueError('Not the successor context')
        self.dispatcher.require_context(context)
        self.dispatcher.resolve_capture_run(context, record)
        return self.boundary.read(lambda: self.helper.read_pair(
            {**context, 'output': str(self.boundary.original)}, run, record, pair_pin))

    def retained_proof(self, output, run, record, retained):
        self.dispatcher.require_context(self.context)
        self.dispatcher.resolve_capture_run(self.context, record)
        if str(output) != str(self.boundary.output): raise ValueError('Not the successor output')
        return self.boundary.read(lambda: self.helper.retained_proof(
            self.boundary.original, run, record, retained))

    def receipt_binding(self, context, run, record, config, rows, *, needs_statistics=False):
        if context is not self.context: raise ValueError('Not the successor context')
        self.dispatcher.require_context(context)
        self.dispatcher.resolve_capture_run(context, record)
        original = dict(context)
        if set(self.capture_authority) != {'executionRoot', 'contract', 'batchPath'}:
            raise ValueError('Original capture authority is incomplete')
        for field, item in self.capture_authority.items():
            if W.pin(item['path']) != item: raise ValueError('Original capture authority changed')
            original[field] = item['path']
        return self.helper.receipt_binding(original, run, record, config, rows,
                                           needs_statistics=needs_statistics)

    def verify_pair_semantics(self, *args, **kwargs): return self.helper.verify_pair_semantics(*args, **kwargs)


class PinReader:
    """Instance-local external-capture I/O injection; ordinary/native/reference reads delegate."""
    def __init__(self, original, boundary, dispatcher, context):
        self.original, self.boundary = original, boundary
        self.dispatcher, self.context = dispatcher, context

    def __call__(self, item, root, *, external=False):
        self.dispatcher.require_context(self.context)
        if self.context['phase'] != 'gate': raise ValueError('Recovery is gate-only')
        if external and Path(root).absolute() == self.boundary.output:
            path = clean_path(item['path'], self.boundary.original)
            if self.boundary.allowed.get(path) != item['sha256']:
                raise ValueError('Capture pin is absent from original union')
            return self.boundary.read(lambda: self.original(item, self.boundary.original, external=True))
        return self.original(item, root, external=external)


def install(measurement, boundary, dispatcher, context, capture_authority):
    """Reuse the registered helper/config/inventory admission before seeding its scoped cache."""
    if context['phase'] != 'gate': raise ValueError('Recovery is gate-only')
    common = measurement.P.S.L
    helper, config, inventory = common._repeat_binding(context, dispatcher)
    common._REPEAT.clear()
    common._REPEAT.update(context=context,
        value=(Repeat(helper, boundary, dispatcher, context, capture_authority), config, inventory))
    primitive = measurement.P.S.M
    if isinstance(primitive._pin_bytes, PinReader): raise ValueError('Read adapter already installed')
    primitive._pin_bytes = PinReader(primitive._pin_bytes, boundary, dispatcher, context)
