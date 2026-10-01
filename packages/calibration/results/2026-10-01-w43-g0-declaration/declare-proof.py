"""W43 G0: declare.py proved red and green on scratch copies (writes declare-proof.txt).

    python3.12 -B declare-proof.py

Each case copies this directory to a sibling scratch directory at the same depth (so every pinned
source still resolves), mutates one thing, runs `declare.py`, and removes the copy. The committed
files are never touched.

The amendment cases (the parent's ruling) first rewind the copy to the declaration as hashed. They
rebuild it from the copy's own chain, so they prove this exact amendment whether or not it has been
made. One proof capture directory is created in the repository for one case and always removed.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
REL = HERE.relative_to(ROOT).as_posix()
RESULTS = []
X41 = [f'{REL}/x41/x41.ts', f'{REL}/x41/sha256.txt']
REASON = ('the X41 pins moved by review fix b213d4a4 (X41 projects scenes.json by unit, 911 entries), merged '
          'after the hash')
CAUSE = 'b213d4a4'
CAPTURE = ROOT / 'packages/calibration/results/_w43-g1a-declare-proof-capture'


def run(tmp, *args):
    r = subprocess.run([sys.executable, '-B', str(tmp / 'declare.py'), *args], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


ONLY = sys.argv[1:]          # name fragments: run only the matching cases, and write no record


def case(name, mutate, verb, want_rc, want_text, after=None):
    if ONLY and not any(o in name for o in ONLY):
        return
    tmp = HERE.parent / f'_w43-declare-proof-{name}'
    shutil.rmtree(tmp, ignore_errors=True)
    shutil.copytree(HERE, tmp, ignore=shutil.ignore_patterns('x41', '__pycache__'))
    try:
        mutate(tmp)
        rc, out = run(tmp, *([verb] if isinstance(verb, str) else verb))
        ok = rc == want_rc and want_text in out
        extra = ''
        if name == 'green-hash':
            r2, out2 = run(tmp, 'hash')
            ok = ok and (tmp / 'declaration.sha256').exists() and (tmp / 'closure.json').exists() \
                and r2 == 2 and 'never overwrites' in out2
            extra = ' and a second hash refuses'
        if after:
            more, extra = after(tmp)
            ok = ok and more
        RESULTS.append((name, ok, f'rc {rc}{extra}', out.strip().splitlines()[-1] if out.strip() else ''))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        shutil.rmtree(CAPTURE, ignore_errors=True)


def rewind(tmp):
    """The declaration as hashed, before any amendment, rebuilt from the copy's own chain."""
    am = tmp / 'amendments.json'
    if not am.exists():
        return
    d = json.loads((tmp / 'declaration.json').read_text())
    for a in reversed(json.loads(am.read_text())['amendments']):
        for path, move in a['pins'].items():
            d['sources'][path] = move['from']
    (tmp / 'declaration.json').write_text(json.dumps(d, indent=2, ensure_ascii=False) + '\n')
    (tmp / 'declaration.sha256').write_text((tmp / 'declaration.sha256').read_text().splitlines()[0] + '\n')
    am.unlink()


def amended(tmp):
    """The copy carrying this exact amendment, made by the tool itself from the rewound declaration."""
    rewind(tmp)
    rc, out = run(tmp, 'amend', '--reason', REASON, '--cause', CAUSE, *X41)
    if rc != 0:
        raise SystemExit(f'the green amendment did not go through: {out}')


def unhashed(tmp):
    for f in ('declaration.sha256', 'closure.json', 'amendments.json'):
        (tmp / f).unlink(missing_ok=True)


def green_amend_after(tmp):
    """After the amendment: check verifies the chain, the first line is untouched, and the hash is the one
    committed beside this proof (when the real amendment exists)."""
    rc, out = run(tmp, 'check')
    lines = (tmp / 'declaration.sha256').read_text().splitlines()
    first = (HERE / 'declaration.sha256').read_text().splitlines()[0]
    real = HERE / 'amendments.json'
    same = (not real.exists()) or json.loads(real.read_text())['amendments'][0]['declarationSha256'] == lines[1].split()[0]
    return (rc == 0 and len(lines) == 2 and lines[0] == first and same,
            f'; check {rc}, {len(lines)} lines, the first untouched, the hash the committed one: {same}')


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
    case('red-hash-while-pending', lambda t: (unhashed(t), make_pending(t)), 'hash', 2, 'hash REFUSES')
    case('red-pin', lambda t: edit_json(t / 'declaration.json', lambda d: d['sources'].update(
        {next(iter(d['sources'])): '0' * 64})), 'check', 1, 'mismatch')
    case('red-verdicts', lambda t: edit_json(t / 'declaration.json', lambda d: item(d, 'bridgeExisting')['declared'][
        'verdicts'].update({'NO TWIN': 3})), 'check', 1, 'mismatch')
    case('red-captures', lambda t: edit_json(t / 'declaration.json', lambda d: item(d, 'probeBed')['declared'].update(
        captures=1000)), 'check', 1, 'mismatch')
    case('red-cells', lambda t: edit_json(t / 'declaration.json', lambda d: item(d, 'canonicalBed')['declared'].update(
        cellsPerRound=561)), 'check', 1, 'mismatch')
    case('red-runs', lambda t: edit_json(t / 'declaration.json', lambda d: item(d, 'canonicalBed')['declared'].update(
        runs=99)), 'check', 1, 'mismatch')
    case('red-probe-runs', lambda t: edit_json(t / 'declaration.json', lambda d: item(d, 'repeatsAndBar')['declared'].update(
        probeRuns=7)), 'check', 1, 'mismatch')
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
    case('green-hash', unhashed, 'hash', 0, 'commit both before G1a')
    amend_args = ['amend', '--reason', REASON, '--cause', CAUSE, *X41]
    case('green-amend', rewind, amend_args, 0, 'the chain verifies', after=green_amend_after)
    case('red-amend-other-pin', lambda t: (rewind(t), edit_json(t / 'declaration.json', lambda d: d['sources'].update(
        {f'{REL}/memo-f/MEMO.md': '0' * 64}))), amend_args, 2, 'outside the named pins')
    case('red-amend-unmoved-pin', rewind, amend_args + [f'{REL}/memo-f/MEMO.md'], 2, 'has not moved')
    case('red-amend-same-reason', amended, amend_args, 2, 'needs a new one')
    case('red-amend-capture', lambda t: (rewind(t), CAPTURE.mkdir(), (CAPTURE / 'run-1.png').write_bytes(b'')),
         amend_args, 2, 'a capture or archive exists')
    case('red-amend-unhashed', unhashed, amend_args, 2, 'not hashed')
    case('red-chain-first-line', lambda t: (amended(t), (t / 'declaration.sha256').write_text(
        '0' * 64 + (t / 'declaration.sha256').read_text()[64:])), 'check', 1, 'mismatch')
    case('red-chain-from', lambda t: (amended(t), edit_json(t / 'amendments.json', lambda d: d['amendments'][0]['pins'][
        X41[0]].update({'from': '0' * 64}))), 'check', 1, 'mismatch')
    lines = [f'declare.py proof: {sum(ok for _, ok, *_ in RESULTS)} of {len(RESULTS)} cases hold', '']
    lines += [f"{'PASS' if ok else 'FAIL'}  {n:24s} {rc}  | {last}" for n, ok, rc, last in RESULTS]
    if not ONLY:
        (HERE / 'declare-proof.txt').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))
    return 0 if all(ok for _, ok, *_ in RESULTS) else 1


if __name__ == '__main__':
    sys.exit(main())
