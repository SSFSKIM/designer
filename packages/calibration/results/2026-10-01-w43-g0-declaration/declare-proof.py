"""W43 G0: declare.py proved red and green on scratch copies (writes declare-proof.txt).

    python3.12 -B declare-proof.py

Each case copies this directory to a sibling scratch directory at the same depth (so every pinned
source still resolves), mutates one thing, runs `declare.py`, and removes the copy. The committed
files are never touched.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = []


def case(name, mutate, verb, want_rc, want_text):
    tmp = HERE.parent / f'_w43-declare-proof-{name}'
    shutil.rmtree(tmp, ignore_errors=True)
    shutil.copytree(HERE, tmp, ignore=shutil.ignore_patterns('x41', '__pycache__'))
    try:
        mutate(tmp)
        r = subprocess.run([sys.executable, '-B', str(tmp / 'declare.py'), verb], capture_output=True, text=True)
        out = r.stdout + r.stderr
        ok = r.returncode == want_rc and want_text in out
        extra = ''
        if name == 'green-hash':
            r2 = subprocess.run([sys.executable, '-B', str(tmp / 'declare.py'), 'hash'], capture_output=True, text=True)
            ok = ok and (tmp / 'declaration.sha256').exists() and (tmp / 'closure.json').exists() \
                and r2.returncode == 2 and 'never overwrites' in r2.stdout
            extra = ' and a second hash refuses'
        RESULTS.append((name, ok, f'rc {r.returncode}{extra}', out.strip().splitlines()[-1] if out.strip() else ''))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def edit_json(path, fn):
    d = json.loads(path.read_text())
    fn(d)
    path.write_text(json.dumps(d, indent=2, ensure_ascii=False) + '\n')


def item(d, iid):
    return next(i for i in d['items'] if i['id'] == iid)


def make_pending(tmp, marked=True):
    """Return one declared item to pending (as before memo F), its twin marked or not."""
    def fn(d):
        it = item(d, 'ladderReadings')
        del it['declared']
        it['pending'] = {'on': 'memo F', 'note': 'proof only'}
    edit_json(tmp / 'declaration.json', fn)
    if marked:
        md = (tmp / 'declaration.md').read_text()
        md = md.replace('These readings are descriptive and gated by nothing', '**PENDING (memo F).** These readings')
        (tmp / 'declaration.md').write_text(md)


def main():
    case('green-check', lambda t: None, 'check', 0, 'consistent with its sources')
    case('red-hash-while-pending', make_pending, 'hash', 2, 'hash REFUSES')
    case('red-pin', lambda t: edit_json(t / 'declaration.json', lambda d: d['sources'].update(
        {next(iter(d['sources'])): '0' * 64})), 'check', 1, 'mismatch')
    case('red-verdicts', lambda t: edit_json(t / 'declaration.json', lambda d: item(d, 'bridgeExisting')['declared'][
        'verdicts'].update({'NO TWIN': 3})), 'check', 1, 'mismatch')
    case('red-captures', lambda t: edit_json(t / 'declaration.json', lambda d: item(d, 'probeBed')['declared'].update(
        captures=1000)), 'check', 1, 'mismatch')
    case('red-cells', lambda t: edit_json(t / 'declaration.json', lambda d: item(d, 'canonicalBed')['declared'].update(
        cellsPerRound=561)), 'check', 1, 'mismatch')
    case('red-twin-order', lambda t: (t / 'declaration.md').write_text((t / 'declaration.md').read_text().replace(
        '### probeBed', '### probeBedX')), 'check', 1, 'mismatch')
    case('red-unmarked-pending', lambda t: make_pending(t, marked=False), 'check', 1, 'mismatch')
    case('red-support-count', lambda t: edit_json(t / 'declaration.json', lambda d: item(d, 'wTestStatistic')['declared'][
        'support']['supportedRegionsPerEndpoint'].update({'dark-inactive': 3})), 'check', 1, 'mismatch')
    case('red-plan-sha', lambda t: edit_json(t / 'declaration.json', lambda d: item(d, 'sitting-g1b')['declared'].update(
        planSha256='0' * 64)), 'check', 1, 'mismatch')
    case('red-neither', lambda t: edit_json(t / 'declaration.json', lambda d: item(d, 'memoF').pop('declared')), 'check',
         1, 'mismatch')
    case('red-bed-edited', lambda t: (t / 'bed/probe-bed.json').write_text(
        (t / 'bed/probe-bed.json').read_text().replace('"runs": 3', '"runs": 4', 1)), 'check', 1, 'mismatch')
    case('green-hash', lambda t: None, 'hash', 0, 'commit both before G1a')
    lines = [f'declare.py proof: {sum(ok for _, ok, *_ in RESULTS)} of {len(RESULTS)} cases hold', '']
    lines += [f"{'PASS' if ok else 'FAIL'}  {n:24s} {rc}  | {last}" for n, ok, rc, last in RESULTS]
    (HERE / 'declare-proof.txt').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))
    return 0 if all(ok for _, ok, *_ in RESULTS) else 1


if __name__ == '__main__':
    sys.exit(main())
