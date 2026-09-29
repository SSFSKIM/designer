"""W41 G2 — the port's proof: every ported referee reproduces the W36 cut it replaces.

Runs each script in published mode on the current (pre-W41) union and the canonical
capture tree, with W36's inputs (M2's W33 reference, W36's claims labels), into a scratch
directory, and compares with the committed W36 cut: byte for byte, or field by field with
every difference named. E2's regression must reproduce its frozen baseline bin for bin.

The pre-W41 light rows name receded 30fbe05986ae, and W41 G2's seal (f5760e17) moved that
file on disk. Every cut keeps W36's shipped-document guard, so the reproduction runs from a
checkout where the rows' documents ARE the files on disk — the pre-seal main, 4f43d2dc,
whose generation store is byte-identical to the seal's — with this directory copied in.
At the seal itself the guards refuse the pre-W41 light rows, which is the seal interval.

    python3.12 -B reproduce.py --out /tmp/DIR     # from a 4f43d2dc checkout
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
ROOT = CAL.parent.parent
W36 = CAL / 'results/2026-09-24-w36-g1-black-branch'
W36G2 = CAL / 'results/2026-09-24-w36-g2-landing'
E2 = CAL / 'results/2026-09-25-w38-g0-rim-axis-cut'
RECEDED = 'packages/calibration/profiles/apple-macos-27.0-1x-light-standard-glass0.5-receded.json'
W36_CHROMA_CLAIMS = ('c9a §5.179; W32 Decision Log 4; adopted at §5.165 §1, declared at §5.161 '
                     '§7 (b), fitted at §5.164 §4')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(out, script, *args):
    env = dict(os.environ, OPENBLAS_NUM_THREADS='1', VECLIB_MAXIMUM_THREADS='1')
    env.pop('VITREA_MATRIX_PATH', None)
    with (out / f'{Path(script).stem}.txt').open('w') as log:
        code = subprocess.run([sys.executable, '-B', str(HERE / script), *args], stdout=log,
                              stderr=subprocess.STDOUT, env=env).returncode
    if code:
        raise SystemExit(f'{script} exited {code}; see {out}/{Path(script).stem}.txt')


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--out', type=Path, required=True)
    out = parser.parse_args().out.resolve()
    live = sha(ROOT / RECEDED)[:12]
    if live != '30fbe05986ae':
        raise SystemExit(f'reproduce: {RECEDED} is {live} here, not the pre-W41 30fbe05986ae; '
                         'run from the pre-seal checkout (4f43d2dc) with this directory copied in')
    out.mkdir(parents=True, exist_ok=False)
    report = {}

    run(out, 'chroma-cut.py', '--out', str(out / 'chroma-cut.json'),
        '--reference', 'light=6e509c7f76cc:45acb6d916b9',
        '--reference', 'dark=eab099cc6698:4e68f81869f6', '--claims', W36_CHROMA_CLAIMS)
    new, raw = json.loads((out / 'chroma-cut.json').read_text()), (W36 / 'chroma-cut.json').read_text()
    old = json.loads(raw)
    differing = sorted(k for k in set(new) | set(old) if new.get(k) != old.get(k))
    new['generatedAt'] = old['generatedAt']
    receded = {s: g.pop('recededDocumentSha256') for s, g in new['referenceGeneration'].items()}
    report['chroma-cut'] = dict(
        w36=str((W36 / 'chroma-cut.json').relative_to(CAL)), w36Sha256=sha(W36 / 'chroma-cut.json'),
        portSha256=sha(out / 'chroma-cut.json'), differingTopLevelFields=differing,
        explained=dict(generatedAt='a wall-clock stamp, different on every run',
                       referenceGeneration='gains recededDocumentSha256 per scheme ' + json.dumps(
                           receded) + ': W40 generations are pairs; post-W41 the light active '
                           'hash owns two files'),
        bytesEqualWithThoseTwoRestored=json.dumps(new, indent=2) + '\n' == raw)

    run(out, 'm2-rebaseline.py', '--cut', str(W36 / 'chroma-cut.json'),
        '--out', str(out / 'm2-rebaseline-on-w36-cut.json'), '--claims', 'c9a §5.179')
    run(out, 'm2-rebaseline.py', '--cut', str(out / 'chroma-cut.json'),
        '--out', str(out / 'm2-rebaseline.json'), '--claims', 'c9a §5.179')
    m2, raw = json.loads((out / 'm2-rebaseline.json').read_text()), (W36 / 'm2-rebaseline.json').read_text()
    for g in m2['referenceGeneration'].values():
        g.pop('recededDocumentSha256')
    report['m2-rebaseline'] = dict(
        w36Sha256=sha(W36 / 'm2-rebaseline.json'),
        onW36CutByteIdentical=sha(out / 'm2-rebaseline-on-w36-cut.json') == sha(W36 / 'm2-rebaseline.json'),
        onPortedCutBytesEqualWithoutRecededField=json.dumps(m2, indent=2) + '\n' == raw)

    run(out, 'exterior-cut.py', '--out', str(out))
    new, raw = json.loads((out / 'exterior-cut.json').read_text()), (W36 / 'exterior-cut.json').read_text()
    old = json.loads(raw)
    differing = sorted(k for k in set(new) | set(old) if new.get(k) != old.get(k))
    source = new['source']
    new['source'] = old['source']
    report['exterior-cut'] = dict(
        w36Sha256=sha(W36 / 'exterior-cut.json'), portSha256=sha(out / 'exterior-cut.json'),
        differingTopLevelFields=differing,
        explained=dict(source=f'W36 recorded its worktree path {old["source"]!r}; the port '
                              f'records {source!r}'),
        bytesEqualWithSourceRestored=json.dumps(new, indent=1) + '\n' == raw)

    run(out, 'l1-cut.py', '--out', str(out / 'l1-cut.json'), '--claims', 'c9a §5.180')
    report['l1-cut'] = dict(w36Sha256=sha(W36G2 / 'l1-cut.json'), portSha256=sha(out / 'l1-cut.json'),
                            byteIdentical=sha(W36G2 / 'l1-cut.json') == sha(out / 'l1-cut.json'))

    run(out, 'black-cut.py', '--out', str(out / 'black-cut.json'))
    report['black-cut'] = dict(w36Sha256=sha(W36 / 'black-cut.json'),
                               portSha256=sha(out / 'black-cut.json'),
                               byteIdentical=sha(W36 / 'black-cut.json') == sha(out / 'black-cut.json'))

    run(out, 'e2-regression.py', '--out', str(out / 'e2-regression.json'),
        '--bins', str(out / 'e2-regression-bins.json.gz'))
    e2 = json.loads((out / 'e2-regression.json').read_text())
    report['e2-regression'] = dict(
        baselineSha256=e2['baseline']['sha256'], summarySha256=sha(out / 'e2-regression.json'),
        binsSha256=sha(out / 'e2-regression-bins.json.gz'),
        **{k: e2[k] for k in ('cells', 'pngs', 'rowsIdenticalExceptGeneration', 'bins',
                              'worstDelta', 'holds', 'e2SummaryEqualsPinned')})

    report['allReproduce'] = all([
        report['chroma-cut']['bytesEqualWithThoseTwoRestored'],
        report['chroma-cut']['differingTopLevelFields'] == ['generatedAt', 'referenceGeneration'],
        report['m2-rebaseline']['onW36CutByteIdentical'],
        report['m2-rebaseline']['onPortedCutBytesEqualWithoutRecededField'],
        report['exterior-cut']['bytesEqualWithSourceRestored'],
        report['exterior-cut']['differingTopLevelFields'] == ['source'],
        report['l1-cut']['byteIdentical'], report['black-cut']['byteIdentical'],
        e2['holds'], e2['e2SummaryEqualsPinned'], e2['pngs']['identical'] == 212,
        e2['rowsIdenticalExceptGeneration'] == 212, e2['bins']['FAIL'] == 0,
        e2['worstDelta']['worstDelta'] == 0])
    (out / 'reproduction.json').write_text(json.dumps(report, indent=1) + '\n')
    print(json.dumps(report, indent=1))
    return 0 if report['allReproduce'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
