"""Exercise the numerical layer against owner SOURCE functions on synthetic inputs only.

Run with python3 -I source_probe.py. AST extraction excludes source modules' imports, top-level
execution and data loaders; only the named arithmetic and literal constants are executed.
No capture, inventory JSON, matrix, archive, coefficient or measured-statistic file is opened.
"""
import ast
import importlib.util
import math
from pathlib import Path
import statistics
import sys

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]


def source_functions(path, names, constants=()):
    tree = ast.parse(path.read_text(), filename=str(path))
    chosen = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    if {n.name for n in chosen} != set(names):
        raise AssertionError('Owner source no longer exposes the expected arithmetic')
    env = {'math': math, 'statistics': statistics}
    for name in constants:
        assignments = [node for node in tree.body if isinstance(node, ast.Assign)
                       and any(isinstance(t, ast.Name) and t.id == name for t in node.targets)]
        if len(assignments) != 1:
            raise AssertionError(f'Owner constant changed shape: {name}')
        env[name] = ast.literal_eval(assignments[0].value)
    exec(compile(ast.Module(body=chosen, type_ignores=[]), str(path), 'exec'), env)
    return env


def run():
    spec = importlib.util.spec_from_file_location('w50_judge_probe_numerical', HERE / 'numerical.py')
    j = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = j
    spec.loader.exec_module(j)
    owner = source_functions(CAL / 'results/2026-10-05-w46-g0-declaration/cuts/rule.py',
                             ('log_error', 'target_aggregate'))
    t1 = source_functions(CAL / 'results/2026-10-03-w44-g1-refit/cuts/t1.py',
                         ('classify',), ('RATIO_CLAUSE', 'EQUAL'))
    history = source_functions(CAL / 'results/2026-10-08-w50-g0-declaration/references.py',
                               ('historical_cap',))
    current_pair = j.DocumentPair('a'*64, 'b'*64)
    historical_pair = j.DocumentPair('1'*64, '2'*64)
    candidate_pair = j.DocumentPair('f'*64, '0'*64)

    def reading(value, pair):
        return j.Reading('MEASURED', 'linear-luma', value, j.Evidence('c'*64, 'd'*64, pair))

    compared = 0
    # Nonidentical epsilons and odd/even memberships catch median/denominator substitutions.
    for scale in (1, 2):
        for count in (1, 2, 3, 4):
            cells, reads = [], []
            for i in range(count):
                n, c, k, h = i/32, (i+2)/32, (i+3)/32, (i+1)/32
                code, bar = (i+1)/256, (i+1)/256
                B = max(code, 2*bar)
                key = j.RowIdentity(f'apple-macos-27.0-{scale}x-dark-standard-glass0.25',
                                    'webgpu', f'checkerboard-synthetic-{i}__rrect-md__rest',
                                    'T1-full-silhouette', 'native-silhouette')
                ref = j.Reference(key, 'e'*64, reading(n, None), reading(c, current_pair), code, bar, B)
                candidate = j.Candidate(key, reading(k, candidate_pair))
                old = reading(h, historical_pair)
                cells.append(j.AggregateCell(ref, candidate, old))
                reads.append(dict(n=n, c=h, k=k, code=code))
                expected = t1['classify'](n, c, k, bar, code)
                actual = j.t1_growth(ref, candidate).components[0]
                assert actual.bound == expected['B']
                assert actual.growth == expected['growth']
                cap, frozen_in_B = history['historical_cap'](n, c, h, B)
                hist = j.Historical(old, abs(c-n)-abs(h-n), False)
                got = j.historical_growth(ref, candidate, hist).components[0]
                assert math.isclose(got.bound/B, cap, rel_tol=1e-14)
                assert math.isclose(hist.frozen_current_growth/B, frozen_in_B, rel_tol=1e-14)
                compared += 2
            expected = owner['target_aggregate'](reads)
            actual = j.target_aggregate('C rest', scale, cells,
                                        expected_keys=tuple(c.reference.identity for c in cells))
            assert actual.candidate == expected['A']
            assert actual.w48_reference == expected['referenceA']
            assert (actual.status == 'WITHIN') == expected['halved']
            compared += 1
    print(f'SOURCE_PROBE: {compared} synthetic comparisons agree with owner arithmetic; no measured data read')


if __name__ == '__main__':
    run()
