"""Source-bound E2 reader. Imports no historical result modules or measured artifacts.

Only the named geometry functions and the original cut_e2 function execute. Dependencies
are explicit: images and one-cell membership are supplied by the caller, not loaded by an
old wave's bed. The outer referee owns population and hash/descriptor validation.
"""
import ast
import builtins
import hashlib
import io
import json
from pathlib import Path
import symtable
import sys
from types import SimpleNamespace

CAL = Path(__file__).resolve().parents[3]
SOURCES = {
    'old': ('results/2026-09-25-w37-g0-edge-identification/canonical.py',
            'fa68f6521c21d549c05e395cbba98b14c187ad0f4a3daefecffafeaca29755aa'),
    'repair': ('results/2026-09-25-w37-g0b-edge-identification/canonical.py',
               'ed3f937b37fb9375f089a42b069ae677d881b527bed1bb465ad5d9b996948ca9'),
    'edge': ('results/2026-09-25-w38-g0-rim-axis-cut/e2.py',
             '4ee7e31e12987507d47d7e976cc04fbbfdec31923779b7954e7db68c58a0558a'),
    'cut': ('results/2026-10-06-w47-g0-operators/cuts/cuts.py',
            '7ea1fd1ae039cc86bddc43f41539c7c0675725f0d1c9b2406c75ecaf09c86577'),
}


def bind(text, expected_hash, names, dependencies):
    if hashlib.sha256(text.encode()).hexdigest() != expected_hash:
        raise ValueError('E2 source hash changed')
    tree = ast.parse(text)
    selected = []
    for name in names:
        matches = [node for node in tree.body
                   if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name)
                   or (isinstance(node, ast.Assign) and any(
                       isinstance(t, ast.Name) and t.id == name for t in node.targets))]
        if len(matches) != 1:
            raise ValueError('missing/ambiguous E2 source symbol ' + name)
        selected.append(matches[0])
    module = ast.Module(body=selected, type_ignores=[])
    # Postpone annotation evaluation; old bed type names are not runtime dependencies.
    code = 'from __future__ import annotations\n' + ast.unparse(module)
    table = symtable.symtable(code, '<E2-closure>', 'exec')
    allowed = set(names) | set(dependencies) | set(vars(builtins))
    def check(t):
        for s in t.get_symbols():
            if s.is_global() and s.is_referenced() and s.get_name() not in allowed:
                raise ValueError('unbound E2 dependency ' + s.get_name())
        for child in t.get_children():
            check(child)
    check(table)
    namespace = dict(dependencies)
    exec(compile(code, '<E2-closure>', 'exec'), namespace)
    return SimpleNamespace(**{name: namespace[name] for name in names})


def source(key, names, dependencies):
    path, digest = SOURCES[key]
    return bind((CAL / path).read_text(), digest, names, dependencies)


def measure(native, current, candidate, component, scale, identity):
    import numpy as np
    if native.shape != current.shape or native.shape != candidate.shape:
        raise ValueError('E2 image dimension mismatch')
    if len(native.shape) != 3 or native.shape[2] != 3:
        raise ValueError('E2 requires RGB arrays')
    if component['kind'] == 'group' and (len(component['items']) != 3 or any(
            i['kind'] != 'capsule' or i['size'] != [44, 44] for i in component['items'])):
        raise ValueError('E2 grouped geometry changed; estimator undeclared')
    old = source('old', ['geometry'], {'np': np})
    repaired = source('repair', ['geometry'], {'np': np, 'old': old})
    edge = source('edge', ['group_geometry', 'single_geometry'], {'np': np, 'repaired': repaired})
    key = tuple(identity)
    cut = source('cut', ['E2_NAMED_CODES', 'E2_MIN_PIXELS', 'cut_e2'], {
        'np': np,
        'B': SimpleNamespace(scale_of=lambda _: scale,
                             SCENES=SimpleNamespace(component=lambda _: component)),
        'e2_module': lambda: edge,
        'e2_population': lambda *args: ({key: {}}, []),
        'native': lambda *args: native,
        'capture': lambda root, *args: (candidate if root == 'candidate' else current, None),
        'labels': lambda keys: list(keys),
        'qualified': lambda *args, **kwargs: 'reported',
    })
    result = cut.cut_e2(None, 'candidate', None, 'current', 'webgpu')
    cell = result['perCell'][0]
    if cell['status'] == 'UNMEASURED':
        return {'state': 'UNMEASURED', 'reason': 'No E2 bins with four pixels', 'bins': 0}
    return {'state': 'MEASURED', 'verdict': 'reported', 'bins': cell['bins'],
            'candidate': cell['meanAbsCodes'], 'current': cell['prefitMeanAbsCodes'],
            'growth': cell['change'], 'worstBinDelta': cell['worstBinDelta'],
            'namedMissBins': result['namedMissBins'], 'sources': SOURCES,
            'noNewTrade': 'Error growth is reported. No new numeric E2 gate is authorised.'}


def read_image(pin):
    import numpy as np
    from PIL import Image
    raw = Path(pin['path']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != pin['sha256']:
        raise ValueError('E2 image hash changed')
    return np.asarray(Image.open(io.BytesIO(raw)).convert('RGB'), dtype=float)


def contracts():
    """Expose only source identities and the original diagnostic constants, never pixels."""
    pins = {}
    for key, (path, expected) in SOURCES.items():
        file = CAL / path
        if hashlib.sha256(file.read_bytes()).hexdigest() != expected:
            raise ValueError('E2 source hash changed: ' + path)
        pins[key] = {'path': str(file), 'sha256': expected}
    constants = source('cut', ['E2_MIN_PIXELS', 'E2_NAMED_CODES'], {})
    return {'sources': pins, 'minimumBinPixels': constants.E2_MIN_PIXELS,
            'namedBinGrowthCodes': constants.E2_NAMED_CODES}


if __name__ == '__main__':
    if sys.argv[1:] == ['--contracts']:
        print(json.dumps(contracts(), allow_nan=False))
    else:
        request = json.load(sys.stdin)
        print(json.dumps(measure(*(read_image(request[k]) for k in ('native', 'current', 'candidate')),
                                 request['component'], request['scale'], request['identity']), allow_nan=False))
