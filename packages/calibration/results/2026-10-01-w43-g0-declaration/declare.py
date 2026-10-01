"""W43 G0: check the declaration against the files that define it, and hash it (charter clause 1).

    python3.12 -B declare.py check    # exit 0 consistent (pending items reported), 1 on any mismatch
    python3.12 -B declare.py hash     # refuses (exit 2) while any item is pending

W42's pattern (`2026-09-29-w42-g0-declaration/declare.py`), not its code. `declaration.json` declares
each item once, points at its source files, and pins every source by SHA-256; a path suffixed
`@<commit>` is read at that commit, which is how the charter is pinned. `check` re-reads every pin,
then re-derives each fact the declaration states as a number or a list:
- the four 0.25 keys and their copied membership in `scenes.json`, and the 562 cells;
- the probe and ladder bed's own generator check, its cells per position and its 1,144 captures, and
  that every cell keeps W42's id and is calibration or validation there;
- G0 (b)'s bridge verdicts, and that `bridge.json` names the `bridge.py` beside it;
- the bridge cells' own generator check, their 168 and 84 captures, and the sentinels' reference
  protocol;
- the declared repeat counts (the canonical bed's seven, the probe and ladder's three) against every
  plan pass that captures them, and probe-bed.json's runs;
- the w-test's supported regions per endpoint from `wtest/support.json`, and its prediction stated in
  all four 2x endpoints at 0.5 (`wtest/prediction.json`);
- both sittings' plans: their generator check, each plan's SHA-256 (the item G0 (d)'s pin-check
  reads, `sitting-<name>`), its totals and hours against its timing, and its sources' bytes;
- that `declaration.md` carries every item in order, each pending item marked `PENDING (<what it
  waits on>)` and no declared item so marked.

A pending item declares nothing yet and names what it waits on; none is pending now. `hash` refuses while one remains. It then writes `declaration.sha256` and `closure.json` (the
items G1a, G1b and G2 implement from the hash) and never overwrites either. Both must be committed
before G1a's first capture; a change after it voids the affected sitting as the bed (clause 1).
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
REL = HERE.relative_to(ROOT).as_posix()
DECLARATION, TWIN = HERE / 'declaration.json', HERE / 'declaration.md'
DIGEST, CLOSURE = HERE / 'declaration.sha256', HERE / 'closure.json'
W42_BED = ROOT / 'packages/calibration/results/2026-09-29-w42-g0-declaration/bed/bed.json'
CLOSURE_ITEMS = ('canonicalBed', 'probeBed', 'bridgeCells', 'repeatsAndBar', 'wTestPrediction', 'wTestStatistic',
                 'ladderReadings', 'sitting-g1a', 'sitting-g1b')

sha = lambda data: hashlib.sha256(data).hexdigest()  # noqa: E731


def source_bytes(key):
    if '@' in key:
        path, commit = key.rsplit('@', 1)
        return subprocess.run(['git', '-C', str(ROOT), 'show', f'{commit}:{path}'], check=True,
                              capture_output=True).stdout
    return (ROOT / key).read_bytes()


class Check:
    def __init__(self):
        self.failures = []

    def eq(self, what, got, want):
        if got != want:
            self.failures.append(f'{what}: found {got!r}, declared {want!r}')

    def true(self, what, ok):
        if not ok:
            self.failures.append(what)


def structure(c, d):
    items = d['items']
    ids = [it['id'] for it in items]
    c.eq('item ids are unique', len(set(ids)), len(ids))
    used = set()
    for it in items:
        for key in ('id', 'title', 'clause', 'source'):
            c.true(f"{it.get('id')}: no '{key}'", key in it)
        c.true(f"{it['id']}: an item either declares its reading or is pending, never both or neither",
               ('declared' in it) != ('pending' in it))
        if 'pending' in it:
            c.true(f"{it['id']}: a pending item names what it waits on", bool(it['pending'].get('on')))
        for s in it['source']:
            c.true(f"{it['id']}: source {s} is not pinned", s in d['sources'])
            used.add(s)
    for s in d['sources']:
        c.true(f'sources: {s} is pinned but no item points at it', s in used)
    for key, want in d['sources'].items():
        try:
            c.eq(f'pin {key}', sha(source_bytes(key)), want)
        except (OSError, subprocess.CalledProcessError) as err:
            c.failures.append(f'pin {key}: unreadable ({err})')
    return {it['id']: it for it in items}


def twin(c, items):
    text = TWIN.read_text()
    heads = re.findall(r'^### (\S+)', text, flags=re.M)
    c.eq('declaration.md: its item headings, in order', heads, list(items))
    sections = dict(zip(heads, re.split(r'^### \S+.*$', text, flags=re.M)[1:]))
    for it in items.values():
        body = sections.get(it['id'], '')
        if 'pending' in it:
            c.true(f"declaration.md, {it['id']}: not marked PENDING ({it['pending']['on']})",
                   f"PENDING ({it['pending']['on']})" in body)
        else:
            c.true(f"declaration.md, {it['id']}: a declared item is marked PENDING", 'PENDING' not in body)


def run(*argv):
    r = subprocess.run([sys.executable, '-B', *map(str, argv)], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def beds(c, items):
    spec = json.loads((ROOT / 'apps/reference-apple/scenes.json').read_text())
    prof = {p['key']: p for p in spec['profiles']}
    cb = items['canonicalBed']['declared']
    c.eq('canonicalBed: scenes.json version', spec['version'], cb['scenesVersion'])
    at025 = sorted(k for k in prof if k.endswith('-glass0.25'))
    c.eq('canonicalBed: the 0.25 keys', at025, sorted(cb['keys']))
    for key in at025:
        twin05 = prof.get(key.replace('-glass0.25', '-glass0.5'))
        c.true(f'canonicalBed: {key} copies its 0.5 counterpart', twin05 is not None and all(
            prof[key][f] == twin05[f] for f in ('scenes', 'colorScheme', 'a11y')))
    c.eq('canonicalBed: cells a round', sum(len(prof[k]['scenes']) for k in at025), cb['cellsPerRound'])
    for scheme, n in cb['perScale'].items():
        c.eq(f'canonicalBed: {scheme} cells per scale', {len(prof[k]['scenes']) for k in at025 if f'-{scheme}-' in k}, {n})

    rc, out = run(HERE / 'bed/declare-probe.py', 'check')
    c.true(f'probeBed: declare-probe.py check ({out.strip()})', rc == 0)
    bed = json.loads((HERE / 'bed/probe-bed.json').read_text())
    pb = items['probeBed']['declared']
    for pos in pb['positions']:
        got = bed['byPosition'][f"{pos['x']:g}"]
        c.eq(f"probeBed: cells per endpoint at x = {pos['x']:g}", got['glassPerEndpoint'], [pos['cellsPerEndpoint']])
        c.eq(f"probeBed: kind at x = {pos['x']:g}", got['kind'], pos['kind'])
    c.eq('probeBed: captures', bed['totals']['captures'], pb['captures'])
    c.eq('probeBed: runs', bed['runs'], pb['runs'])
    w42 = json.loads(W42_BED.read_text())['cells']
    for cid, cell in bed['cells'].items():
        c.true(f'probeBed: {cid} is a W42 cell', cid in w42)
        c.true(f'probeBed: {cid} is calibration or validation in W42', w42.get(cid, {}).get('role') in
               ('calibration', 'validation'))


def bridges(c, items):
    b = json.loads((HERE / 'bridge/bridge.json').read_text())
    be = items['bridgeExisting']['declared']
    c.eq('bridgeExisting: verdicts', b['verdicts'], be['verdicts'])
    c.eq('bridgeExisting: bridge.json names bridge.py', b['tool'], sha((HERE / 'bridge/bridge.py').read_bytes()))
    c.eq('bridgeExisting: archive inventory', b['archive']['inventorySha256'],
         '5481795e0a77ef246f6743d2b6bbe2111a79d858ff9b7a2a4571255595940ed7')
    c.eq('bridgeExisting: roles read', b['roles'], ['probe'])
    rc, out = run(HERE / 'bridges/declare-bridges.py', 'check')
    c.true(f'bridgeCells: declare-bridges.py check ({out.strip()})', rc == 0)
    cells = json.loads((HERE / 'bridges/bridge-cells.json').read_text())
    c.eq('bridgeCells: captures per sitting', {k: v['captures']['total'] for k, v in cells['sittings'].items()},
         items['bridgeCells']['declared']['captures'])
    refs = json.loads((HERE / 'bridges/sentinel-references.json').read_text())
    c.eq('bridgeCells: the sentinels read against the long protocol', refs['referenceProtocol'], 'long')
    c.eq('bridgeCells: every sentinel cell-endpoint has its three long runs',
         {s: p['long']['runs'] for e in refs['byEndpoint'].values() for s, p in e.items()} and
         sorted({p['long']['runs'] for e in refs['byEndpoint'].values() for p in e.values()}), [3])


def sittings(c, items):
    rc, out = run(HERE / 'bed/declare-sittings.py', 'check')
    c.true(f'sittings: declare-sittings.py check ({out.strip()})', rc == 0)
    for s in ('g1a', 'g1b'):
        it = items[f'sitting-{s}']['declared']
        c.eq(f'sitting-{s}: planSha256', sha((HERE / f'bed/sitting-{s}.json').read_bytes()), it['planSha256'])
        timing = json.loads((HERE / f'bed/timing-{s}.json').read_text())
        c.eq(f'sitting-{s}: totals against its timing', timing['priced']['totals'], it['totals'])
        c.eq(f'sitting-{s}: modelled hours', (timing['priced']['totalHours'], timing['priced']['withStopLossHours']),
             (it['modelledHours'], it['withStopLossHours']))
        plan = json.loads((HERE / f'bed/sitting-{s}.json').read_text())
        c.eq(f'sitting-{s}: its sources are the declared files', {k: v['sha256'] for k, v in plan['sources'].items()},
             {k: sha((ROOT / v['path']).read_bytes()) for k, v in plan['sources'].items()})


def wtest(c, items):
    w = items['wTestStatistic']['declared']
    sup = json.loads((HERE / 'wtest/support.json').read_text())['statistics']['median']['declared']
    c.eq('wTestStatistic: supported free-side regions per endpoint',
         {ep: sum(1 for v in cells.values() if 'free' in v) for ep, cells in sup.items()},
         w['support']['supportedRegionsPerEndpoint'])
    pred = json.loads((HERE / 'wtest/prediction.json').read_text())['prediction']
    c.eq('wTestPrediction: stated in every endpoint, r_pred 0.5', {ep: (v['stated'], v['rPred']) for ep, v in pred.items()},
         {ep: (True, 0.5) for ep in pred})
    c.eq('wTestPrediction: the endpoints it is stated in', sorted(items['wTestPrediction']['declared']['statedIn']),
         ['2x-dark-active', '2x-dark-receded', '2x-light-active', '2x-light-receded'])


def repeats(c, items):
    """The declared repeat counts against the plans that capture them (the review of 4cd1cdc4)."""
    g1a = json.loads((HERE / 'bed/sitting-g1a.json').read_text())['passes']
    g1b = json.loads((HERE / 'bed/sitting-g1b.json').read_text())['passes']
    bed = json.loads((HERE / 'bed/probe-bed.json').read_text())
    canonical = {p['runs'] for p in g1a if p['kind'] == 'capture' and p['role'] == 'bed'}
    probe = {p['runs'] for p in g1b if p['kind'] == 'capture' and p['role'] in ('probe', 'ladder')}
    c.eq('canonicalBed: runs against every G1a bed pass', {items['canonicalBed']['declared']['runs']}, canonical)
    c.eq('repeatsAndBar: canonicalRuns against every G1a bed pass', {items['repeatsAndBar']['declared']['canonicalRuns']},
         canonical)
    c.eq('probeBed: runs against every G1b probe and ladder pass', {items['probeBed']['declared']['runs']}, probe)
    c.eq('repeatsAndBar: probeRuns against every G1b probe and ladder pass',
         {items['repeatsAndBar']['declared']['probeRuns']}, probe)
    c.eq('probeBed: runs against probe-bed.json', items['probeBed']['declared']['runs'], bed['runs'])


def check():
    c = Check()
    d = json.loads(DECLARATION.read_text())
    c.eq('schema', d.get('schema'), 'w43-declaration-1')
    items = structure(c, d)
    twin(c, items)
    beds(c, items)
    bridges(c, items)
    sittings(c, items)
    repeats(c, items)
    if 'declared' in items['wTestStatistic']:
        wtest(c, items)
    return c, d, items


def closure(items, digest):
    return {'schema': 'w43-closure-1', 'declarationSha256': digest, 'declaration': f'{REL}/declaration.json',
            'items': {k: items[k]['declared'] for k in CLOSURE_ITEMS}}


def main(argv):
    if len(argv) != 2 or argv[1] not in ('check', 'hash'):
        print(__doc__)
        return 64
    c, d, items = check()
    waiting = [it for it in items.values() if 'pending' in it]
    print(f"W43 G0 declaration: {len(items)} items, {len(d['sources'])} pinned sources")
    for f in c.failures:
        print('  MISMATCH', f)
    for it in waiting:
        print(f"  PENDING ({it['pending']['on']}) {it['id']}: {it['pending']['note']}")
    if c.failures:
        print(f'check: {len(c.failures)} mismatch(es)')
        return 1
    print('check: consistent with its sources' + (f'; {len(waiting)} item(s) pending' if waiting else ''))
    if argv[1] == 'check':
        return 0
    if waiting:
        print('hash REFUSES: ' + ', '.join(it['id'] for it in waiting) + ' are pending')
        return 2
    if DIGEST.exists() or CLOSURE.exists():
        print('hash REFUSES: a declaration is already hashed; a change after the first capture voids the sitting '
              '(clause 1), and this tool never overwrites one')
        return 2
    digest = sha(DECLARATION.read_bytes())
    body = json.dumps(closure(items, digest), indent=2, sort_keys=True, ensure_ascii=False) + '\n'
    with CLOSURE.open('x') as f:
        f.write(body)
    with DIGEST.open('x') as f:
        f.write(f'{digest}  declaration.json\n')
    print(f'declaration.json sha256 {digest}; closure.json sha256 {sha(body.encode())}; commit both before G1a')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
