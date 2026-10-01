"""W43 G0: check the declaration against the files that define it, and hash it (charter clause 1).

    python3.12 -B declare.py check    # exit 0 consistent (pending items reported), 1 on any mismatch
    python3.12 -B declare.py hash     # refuses (exit 2) while any item is pending
    python3.12 -B declare.py amend --reason TEXT --cause COMMIT PIN [PIN ...]   # re-pin moved sources, after the hash

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

A pending item declares nothing yet and names what it waits on; none is pending now. `hash` refuses
while one remains. It then writes `declaration.sha256` and `closure.json` (the items G1a, G1b and G2
implement from the hash) and never overwrites either. Both must be committed before G1a's first
capture; a change after it voids the affected sitting as the bed (clause 1).

**Amendments** (the parent's ruling, 2026-10-01: an amendment, not a rewrite, and only while no 0.25
pixel exists). `amend` re-pins the named sources at their current bytes and changes nothing else. It
refuses unless:
- the declaration is hashed and its chain verifies;
- every named pin has moved;
- no other pin has moved;
- the same pins are not amended again without a new reason;
- no capture or archive exists for this declaration (`capture_evidence`).

It appends a record to `amendments.json`: the superseded hash, the reason, the cause, and each pin's
from and to. It writes the amended `declaration.json`, then appends the amended hash to
`declaration.sha256` beneath the earlier ones; no line is ever replaced. `closure.json` keeps naming
the original hash, because an amendment changes no item.

`check` verifies the whole chain. Each line of `declaration.sha256` is the hash of the declaration
that line names: the first is the original, each later line one amendment's, and the last the
current bytes. Each earlier declaration is rebuilt from the current one by putting back its
amendments' `from` pins. Its bytes must hash to the line recorded for it, so an amendment that moved
anything but its named pins cannot verify.
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
AMENDMENTS = HERE / 'amendments.json'
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


def serialise(d):
    """declaration.json's own form, so a rebuilt declaration hashes as the file it once was."""
    return (json.dumps(d, indent=2, ensure_ascii=False) + '\n').encode()


def digest_lines():
    return [ln.split()[0] for ln in DIGEST.read_text().splitlines() if ln.strip()] if DIGEST.exists() else []


def amendments():
    return json.loads(AMENDMENTS.read_text())['amendments'] if AMENDMENTS.exists() else []


def chain(c, d):
    """The hash chain: original, each amendment, the current bytes (the module docstring, Amendments)."""
    lines, record, raw = digest_lines(), amendments(), DECLARATION.read_bytes()
    if not lines:
        c.true('chain: amendments.json exists but the declaration was never hashed', not record)
        return
    c.true('chain: declaration.json is not in its own serialised form', serialise(d) == raw)
    c.eq('chain: declaration.sha256 lines against amendments', len(lines), 1 + len(record))
    c.eq('chain: the last line names the current declaration.json', lines[-1], sha(raw))
    if CLOSURE.exists():
        c.eq('chain: closure.json names the original hash', json.loads(CLOSURE.read_text()).get('declarationSha256'),
             lines[0])
    state = json.loads(raw)
    for i in range(len(record) - 1, -1, -1):
        a = record[i]
        c.eq(f'chain: amendment {i + 1} number', a.get('n'), i + 1)
        c.eq(f'chain: amendment {i + 1} names the hash it made', a.get('declarationSha256'), lines[i + 1])
        c.eq(f'chain: amendment {i + 1} names the hash it supersedes', a.get('supersedes'), lines[i])
        c.true(f'chain: amendment {i + 1} states a reason and a cause', bool(a.get('reason')) and bool(a.get('cause')))
        c.true(f'chain: amendment {i + 1} re-pins at least one source', bool(a.get('pins')))
        for path, move in (a.get('pins') or {}).items():
            c.eq(f'chain: amendment {i + 1} pin {path} as amended', state['sources'].get(path), move.get('to'))
            state['sources'][path] = move.get('from')
        c.eq(f'chain: the declaration before amendment {i + 1}, rebuilt, hashes as recorded', sha(serialise(state)),
             lines[i])
    seen = {}
    for a in record:
        key = (tuple(sorted(a.get('pins') or {})), a.get('reason'))
        c.true(f"chain: amendment {a.get('n')} repeats amendment {seen.get(key)}'s pins and reason", key not in seen)
        seen[key] = a.get('n')


def capture_evidence():
    """Anything that would mean a capture or an archive exists for this declaration: the published 0.25
    fixture trees, a G1a or G1b evidence directory, the sittings' run roots, or a W43 archive tag."""
    found = []
    found += [str(p.relative_to(ROOT)) for p in sorted((ROOT / 'apps/reference-apple/fixtures').glob('*glass0.25*'))]
    found += [str(p.relative_to(ROOT)) for p in sorted((ROOT / 'packages/calibration/results').glob('*w43-g1[ab]*'))]
    found += [str(p) for p in (Path.home() / 'vitrea-w43/g1a', Path.home() / 'vitrea-w43/g1b') if p.exists()]
    tags = subprocess.run(['git', '-C', str(ROOT), 'tag', '-l', 'w43-archive*'], capture_output=True, text=True)
    found += [f'tag {t}' for t in tags.stdout.split()]
    return found


def check():
    c = Check()
    d = json.loads(DECLARATION.read_text())
    c.eq('schema', d.get('schema'), 'w43-declaration-1')
    chain(c, d)
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


def amend(argv):
    """The parent's amendment verb: re-pin the named moved sources, record why, append the new hash."""
    import argparse
    ap = argparse.ArgumentParser(prog='declare.py amend')
    ap.add_argument('--reason', required=True)
    ap.add_argument('--cause', required=True, help='the commit that moved the pins')
    ap.add_argument('pins', nargs='+')
    args = ap.parse_args(argv)
    lines = digest_lines()
    if not lines:
        print('amend REFUSES: the declaration is not hashed; before the hash it is simply edited and re-checked')
        return 2
    evidence = capture_evidence()
    if evidence:
        print('amend REFUSES: a capture or archive exists for this declaration, so the bed is fixed: ' +
              ', '.join(evidence[:6]))
        return 2
    record = amendments()
    key = (tuple(sorted(args.pins)), args.reason)
    if any((tuple(sorted(a['pins'])), a['reason']) == key for a in record):
        print('amend REFUSES: these pins were amended before for this same reason; a second amendment needs a new one')
        return 2
    d = json.loads(DECLARATION.read_text())
    unknown = [p for p in args.pins if p not in d['sources'] or '@' in p]
    if unknown:
        print(f'amend REFUSES: not a pinned working-tree source: {unknown}')
        return 2
    c, _, _ = check()
    named = {f'pin {p}' for p in args.pins}
    other = [f for f in c.failures if not any(f.startswith(n + ':') for n in named)]
    if other:
        print('amend REFUSES: the check fails outside the named pins, and an amendment changes nothing else:')
        for f in other:
            print('  MISMATCH', f)
        return 2
    moves = {}
    for p in args.pins:
        now = sha(source_bytes(p))
        if now == d['sources'][p]:
            print(f'amend REFUSES: {p} has not moved; there is nothing to re-pin')
            return 2
        moves[p] = {'from': d['sources'][p], 'to': now}
        d['sources'][p] = now
    raw = serialise(d)
    digest = sha(raw)
    entry = {'n': len(record) + 1, 'supersedes': lines[-1], 'declarationSha256': digest, 'reason': args.reason,
             'cause': args.cause, 'pins': moves,
             'captureEvidenceAtAmendment': 'none (capture_evidence: the 0.25 fixture trees, G1a/G1b evidence '
                                           'directories, ~/vitrea-w43/g1a and g1b, w43-archive tags)'}
    body = {'schema': 'w43-declaration-amendments-1', 'amendments': record + [entry]}
    AMENDMENTS.write_text(json.dumps(body, indent=2, ensure_ascii=False) + '\n')
    DECLARATION.write_bytes(raw)
    with DIGEST.open('a') as f:
        f.write(f'{digest}  declaration.json\n')
    c, _, _ = check()
    if c.failures:
        for f in c.failures:
            print('  MISMATCH', f)
        print('amend: written, but the check fails; inspect before committing')
        return 1
    print(f'amended: declaration.json sha256 {digest} supersedes {lines[-1]} (amendment {entry["n"]}); '
          'the chain verifies; commit declaration.json, amendments.json and declaration.sha256')
    return 0


def main(argv):
    if len(argv) >= 2 and argv[1] == 'amend':
        return amend(argv[2:])
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
