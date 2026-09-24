"""Exercise L1's actual owner cases with scratch inputs (§5.180 clause 8)."""
import copy
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
CAL = HERE.parent.parent
scratch = CAL.parent.parent / '.vitrea-tmp/w36-g2-l1'
scratch.mkdir(parents=True, exist_ok=True)
original = json.loads((CAL / 'results/matrix.json').read_text())
cut = json.loads((HERE / 'l1-cut.json').read_text())
chosen = next(r for r in cut['cells'] if r['error'] is not None and r['error'] < 0.02)
records = []
for mode in ['absolute', 'growth', 'unmeasured']:
    matrix = copy.deepcopy(original)
    matrix_path = scratch / f'{mode}-matrix.json'
    record_path = scratch / f'{mode}-cut.json'
    if mode != 'unmeasured':
        c = next(c for c in matrix['cells'] if c['key']['profileKey'] + '/' + c['key']['sceneId'] == chosen['cell'] and c['key']['web']['renderer'] == 'webgpu')
        target = 0.056 if mode == 'absolute' else chosen['error'] + 0.006
        c['material']['interiorMeanWeb']['value'] = chosen['native'] + target
        matrix_path.write_text(json.dumps(matrix))
        subprocess.run(['python3', str(HERE / 'l1-cut.py'), '--matrix', str(matrix_path),
                        '--out', str(record_path)], check=True)
        pattern = 'L1: absolute error' if mode == 'absolute' else 'L1: error growth'
        env = dict(VITREA_MATRIX_PATH=str(matrix_path), VITREA_L1_CUT=str(record_path))
        detail = dict(cell=chosen['cell'], baselineError=chosen['error'], mutatedError=target,
                      regeneratedRecord=True)
    else:
        mutated = copy.deepcopy(cut)
        mutated['measured'] += 1
        row = next(r for r in mutated['cells'] if r['status'] == 'UNMEASURED')
        row.update(status='MEASURED', error=0, growth=0)
        record_path.write_text(json.dumps(mutated))
        pattern = 'guards the declared population'
        env = dict(VITREA_L1_CUT=str(record_path))
        detail = dict(cell=row['cell'], measuredBefore=136, measuredAfter=137)
    with (HERE / f'discrimination-{mode}.txt').open('x') as log:
        result = subprocess.run(['pnpm', 'exec', 'vitest', 'run', 'test/adopted-thresholds.test.ts',
                                 '-t', pattern], cwd=CAL, env={**os.environ, **env},
                                stdout=log, stderr=subprocess.STDOUT)
    assert result.returncode != 0, mode + ' did not discriminate'
    text = (HERE / f'discrimination-{mode}.txt').read_text()
    assert 'AssertionError' in text and '1 failed' in text, text
    records.append(dict(mutation=mode, exitCode=result.returncode, owner=pattern, **detail))
with (HERE / 'discriminations.json').open('x') as f:
    json.dump(records, f, indent=2)
    f.write('\n')
print(json.dumps(records, indent=2))
