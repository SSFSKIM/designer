"""Executable witness for declared authority/scope deltas and unchanged numerical bodies."""
import ast
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIT = HERE.parent/'2026-10-08-w50-g1-fit'

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def tree(text): return ast.dump(ast.parse(text), include_attributes=False)


def same_scene(original, local, inputs):
    """A historical location is not a different geometry; both admitted bytes must agree."""
    path, local = Path(original['path']), Path(local)
    if original not in inputs or any(p.resolve() != p.absolute() or
            any(q.is_symlink() for q in (p, *p.parents)) for p in (path, local)):
        raise ValueError('Scene location is not explicitly bound ordinary evidence')
    if sha(path) != original['sha256'] or sha(local) != original['sha256']:
        raise ValueError('Original and current scene bytes differ')


def prospective_tree(text, name, ports):
    parsed = ast.parse(text)
    permitted = ports.DL5_NEW_FUNCTIONS.get(name, {})
    seen = set(); kept = []
    for node in parsed.body:
        if isinstance(node, ast.FunctionDef) and node.name in permitted:
            digest = hashlib.sha256(ast.dump(node, include_attributes=False).encode()).hexdigest()
            if node.name in seen or digest != permitted[node.name]:
                raise ValueError('Prospective '+name+' changed declared DL5 function '+node.name)
            seen.add(node.name)
        else: kept.append(node)
    if seen != set(permitted): raise ValueError('Prospective '+name+' lacks declared DL5 functions')
    parsed.body = kept
    # The judge's overview now describes DL5. All executable nodes remain in the comparison.
    if name == 'judge.py' and isinstance(parsed.body[0], ast.Expr) and \
            isinstance(parsed.body[0].value, ast.Constant) and isinstance(parsed.body[0].value.value, str):
        parsed.body.pop(0)
    return ast.dump(parsed, include_attributes=False)


def verify(*, judge=None, rules=None):
    """Fail closed outside exact DL5 insertions and the prior authority/scope port."""
    import types
    path = HERE/'ports.py'
    ports = types.ModuleType('w51_port_declaration'); ports.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), ports.__dict__)
    originals, made = {}, {}
    for name, (original, expected) in ports.expected().items():
        override = {'judge.py':judge, 'judge_rules.py':rules}.get(name)
        actual = Path(override) if override is not None else HERE/name
        if name in ports.DL5_BASE_SHA256 and sha(original) != ports.DL5_BASE_SHA256[name]:
            raise ValueError('Immutable W50 '+name+' fingerprint changed')
        if name in ports.DL5_NEW_FUNCTIONS:
            parsed = ast.parse(expected)
            if name == 'judge.py': parsed.body.pop(0)
            equal = prospective_tree(actual.read_text(), name, ports) == ast.dump(parsed, include_attributes=False)
        else:
            equal = tree(actual.read_text()) == tree(expected) if name.endswith('.py') else actual.read_text() == expected
        if not equal: raise ValueError('Prospective '+name+' differs beyond declared input/authentication wiring')
        originals[str(original)] = sha(original); made[name] = sha(actual)
    return {'schema':'w51-scientific-differential-1', 'status':'UNCHANGED_NUMERICS_DECLARED_DL5_RULE_AND_SCOPE',
            'originals':originals, 'ports':made, 'declarationSha256':sha(path),
            'deltas':['W51-DL5 exact primary caps, named exceptions and full-population scalar aggregates',
                      'DL5 policy authentication, gate clause-C veto and report wiring',
                      'explicit dataset/population authentication and input import wiring',
                      'canonical scene location by bound byte identity',
                      'W51-DL4 judge frozen operands use unchanged measurement.frozen_scope',
                      'shared target/rules numerical module through prospective imports',
                      'canonical reference authority anchored to completed fit pre-fit band proof or sealed synthetic fixture',
                      'declared per-run scene document through canonical transport',
                      'static exposed native/reference authentication for paired repeats',
                      'numerical argument membership bound to the imported referee inventory on both datasets',
                      'Store write primitive uses atomic no-replace installation; state transitions unchanged']}
