"""W42 G0: check the declaration against the stream files, and hash it (charter clause 1).

    python3.12 -B declare.py check    # exit 0 consistent (pending items reported), 1 on any mismatch
    python3.12 -B declare.py hash     # refuses (exit 2) while any pendingUser item has no ruling

`declaration.json` declares every item once and points at the stream file that defines it; its
`sources` pin each of those files by SHA-256 (a path suffixed `@<commit>` is read at that commit,
which is how the charter is pinned at v2.1). `check` re-reads every pin, then re-derives from the
stream files each fact the declaration states as a number or a list (family counts, k's nesting,
candidate 2's ordinate counts, E3's F and its extension levels, the masks, the refraction test's
bars, the gating, the split and H, the bed's counts, the web plan, the sitting's totals, the stops'
populations, the strata, the runner's scope and pin fields) and requires `declaration.md` to carry
every item, each pending item marked pending until its ruling is written into both files.

`hash` runs `check`, refuses while any `pendingUser.ruling` is null, and otherwise writes
`declaration.sha256` and `closure.json` (clauses 6 and 11: the items the one-exposure scorer
implements) and pins both in `bed/exposure/production-pin.json`, leaving G1's inventory fields as
they are. It never overwrites: an existing output, or a production pin already naming a
declaration, refuses. The files it writes must be committed before G1's first capture (clause 1)
and before any production freeze (the runner reads them at HEAD).
"""
import ast
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
REL = HERE.relative_to(ROOT).as_posix()
DECLARATION = HERE / 'declaration.json'
TWIN = HERE / 'declaration.md'
DIGEST = HERE / 'declaration.sha256'
CLOSURE = HERE / 'closure.json'
PIN = HERE / 'bed' / 'exposure' / 'production-pin.json'
ENDPOINTS = ('light-active', 'light-receded', 'dark-active', 'dark-receded')
PASS_OF = {'light-active': '2x-light-active', 'light-receded': '2x-light-receded',
           'dark-active': '2x-dark-active', 'dark-receded': '2x-dark-receded'}

sha = lambda data: hashlib.sha256(data).hexdigest()


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


def instrument():
    sys.path.insert(0, str(HERE / 'instrument'))
    import families, fitting, forward, regions, refraction_order  # noqa: E401 (the instrument's own modules)
    return families, fitting, forward, regions, refraction_order


def structure(c, d):
    items = d['items']
    ids = [it['id'] for it in items]
    c.eq('item ids are unique', len(set(ids)), len(ids))
    used = set()
    for it in items:
        for key in ('id', 'title', 'clause', 'source'):
            c.true(f"{it.get('id')}: no '{key}'", key in it)
        waiting = 'pendingUser' in it and it['pendingUser'].get('ruling') is None
        c.true(f"{it['id']}: a pending item declares nothing yet, and every other item declares its reading",
               ('declared' in it) != waiting)
        c.true(f"{it['id']}: points at no source", bool(it['source']))
        for s in it['source']:
            c.true(f"{it['id']}: source {s} is not pinned in 'sources'", s in d['sources'])
            used.add(s)
    for s in d['sources']:
        c.true(f'sources: {s} is pinned but no item points at it', s in used)
    for key, want in d['sources'].items():
        try:
            c.eq(f'pin {key}', sha(source_bytes(key)), want)
        except (OSError, subprocess.CalledProcessError) as err:
            c.failures.append(f'pin {key}: unreadable ({err})')
    return {it['id']: it for it in items}


def pending(items):
    return [it for it in items.values() if 'pendingUser' in it and it['pendingUser'].get('ruling') is None]


def twin(c, items):
    text = TWIN.read_text()
    heads = re.findall(r'^### (\S+)', text, flags=re.M)
    c.eq('declaration.md: its item headings, in order', heads, list(items))
    sections = dict(zip(heads, re.split(r'^### \S+.*$', text, flags=re.M)[1:]))
    for it in items.values():
        if 'pendingUser' not in it:
            continue
        p, body = it['pendingUser'], sections.get(it['id'], '')
        c.true(f"{it['id']}: pendingUser needs a question, and at least two options or a note saying who "
               "will write them", bool(p.get('question')) and (len(p.get('options', [])) >= 2 or bool(p.get('optionsNote'))))
        ruling = p.get('ruling')
        if ruling is None:
            c.true(f"declaration.md, {it['id']}: not marked PENDING (user)", 'PENDING (user)' in body)
            continue
        c.true(f"{it['id']}: a ruling names its date, who ruled, its Decision Log and the words",
               all(ruling.get(k) for k in ('date', 'by', 'decisionLog', 'words', 'reading')))
        c.true(f"declaration.md, {it['id']}: not marked RULED with the words {ruling.get('words')!r}",
               'RULED' in body and 'PENDING (user)' not in body and str(ruling.get('words')) in body)


def families_and_law(c, items):
    families, fitting, forward, _, _ = instrument()
    F = families.FAMILIES
    declared = {f['name']: f['count'] for f in items['rivals']['declared']['families']}
    expect = {'LT-2k': 'LT-2k', 'free-sn': 'free-sn', 'R1': 'R1', 'W-shape': 'W-shape', 'W-canvas': 'W-canvas',
              'W-tails': 'W-tails', 'K2': 'K2', 'C-linear': 'C-linear', 'knee form': 'knee-luma',
              'LT+bleed-lit-pre': 'LT+bleed-lit-pre', 'LT+bleed-lit-post': 'LT+bleed-lit-post',
              'LT+bleed-lit-own-pre': 'LT+bleed-lit-own-pre', 'LT+bleed-lit-own-post': 'LT+bleed-lit-own-post',
              'LT+bleed': 'LT+bleed', 'LT+bleed-own': 'LT+bleed-own', 'edge-swap': 'edge-swap'}
    for name, key in expect.items():
        c.eq(f'rivals: {name} count', F[key][2], declared.get(name))
    rivals = {k for k, v in F.items() if v[4].startswith('rival')}
    c.eq('rivals: every instrument rival is declared', rivals, set(expect.values()))
    c.eq('law: LT count', F['LT'][2], items['law']['declared']['count'])
    nulls = {k for k, v in F.items() if v[4] == 'null'}
    c.eq('rejectedNulls: the null set', nulls, {n['name'] for n in items['rejectedNulls']['declared']['nulls']})
    c.eq('law: k bounds', tuple(families.K_BOUNDS), (0.8, 4.0))
    c.eq('law: lambda bounds', tuple(fitting.LAM_BOUNDS), (-0.5, 1.6))
    c.eq('law: w', forward.WN, 0.5)
    c.eq("kneeForms: the instrument's LT knee", forward.Family().knee, 'channel')
    c.eq("kneeForms: the instrument's luma rival", F['knee-luma'][0].knee, 'luma')
    width = {'global': 1, 'scheme': 2, 'pose': 2, 'endpoint': 4}
    got = [(name, sum(width[scope] for _, scope in lay) + 4) for name, lay in families.LAYOUTS.items()]
    c.eq('kNesting: layouts and totals, most restricted first', got,
         [(lv['layout'], lv['parametersInTotal']) for lv in items['kNesting']['declared']['levels']])
    return forward


def masks_and_tests(c, items, forward):
    *_, regions, ro = instrument()
    shapes = {'capsule, rrect-sm, rrect-64': (44, 32, 64), 'rrect-80': (80,), 'rrect-md': (96,),
              'rrect-112': (112,), 'rrect-ml': (128,), 'rrect-lg': (160,)}
    want = {'capsule, rrect-sm, rrect-64': 20.0, 'rrect-80': 22.8, 'rrect-md': 25.6, 'rrect-112': 28.4,
            'rrect-ml': 31.2, 'rrect-lg': 36.8}
    for name, spans in shapes.items():
        for s in spans:
            c.eq(f'refractionOrder: primary mask at s = {s}', round(forward.band_d_in(s, 'n'), 6), want[name])
    c.eq('refractionOrder: fallback mask', round(forward.band_d_in(160, 'w'), 6), 53.6)
    c.eq('refractionOrder: band', (forward.BAND_IN, forward.BAND_OUT), (20.0, 19.2))
    c.eq('regionStatistics: receded mask', forward.RECEDED_D_IN, 8.0)
    c.eq('refractionOrder: bins, population, separation, bars, tail',
         (ro.BINS, ro.MIN_BIN_PX, ro.MIN_SEP_PT, ro.BEFORE_BAR, ro.AFTER_BAR, ro.CARRY),
         ((30.0, 38.0, 46.0, 54.0), 200, 16.0, 0.30, 0.15, 3))
    tol = json.loads((HERE / 'instrument' / 'tolerances.json').read_text())
    dv2 = tol['refraction_order_test']['decision_v2']
    c.eq('refractionOrder: decision_v2', (dv2['BEFORE'], dv2['AFTER']), ('D_tail > 0.30 code', 'D_tail < 0.15 code'))
    c.eq('refractionOrder: the declared decision',
         {'BEFORE': dv2['BEFORE'], 'AFTER': dv2['AFTER'],
          'undecided': 'between: reported, the fallback not triggered'},
         items['refractionOrder']['declared']['decision'])
    v3 = tol['refraction_order_test']['v3_2026-09-30']
    c.true('refractionOrder: v3 S1 bars', 'BEFORE > 0.30 code, AFTER < 0.15' in v3['statistics']['S1'])
    c.true('refractionOrder: v3 S2 bars', 'BEFORE if A_hat >= 8 pt, AFTER if A_hat < 4 pt' in ' '.join(v3['statistics']['S2']))
    c.true('refractionOrder: only 2x cells vote', 'Only 2x cells vote' in ' '.join(v3['voters']))
    c.eq('refractionOrder: the declared S2 decision', {'BEFORE': 'A_hat >= 8 pt', 'AFTER': 'A_hat < 4 pt',
         'undecided': 'between'}, items['refractionOrder']['declared']['decisionS2'])
    validity = json.loads((HERE / 'instrument' / 'refraction_order.v3.json').read_text())['validity']
    found = {f"{ep.split('-')[0]} {st}": round(v['P_star'], 3) for key, v in validity.items()
             for ep, st in [key.split('|')]}
    declared = {k: v for k, v in items['refractionOrder']['declared']['pStar'].items() if k != 'reading'}
    c.eq('refractionOrder: P* per scheme and statistic', found, declared)
    rows = json.loads((HERE / 'instrument' / 'resolution.json').read_text())['rows']
    lt = {(r['endpoints'][0], r['quantity']): r['synthetic']['resolution'] for r in rows
          if r['reader'] == 'family fitter: LT (survival resolution)'}
    declared = items['refractionOrderNoCall'].get('declared', {}).get('ltSurvivalResolution')
    if declared is not None:
        c.eq('refractionOrderNoCall: LT survival resolutions', {f"{ep.replace('rest', 'active')}": {q: lt[(ep, q)]
             for q in ('k', 'lam')} for ep in ('light-rest', 'dark-rest')}, declared)
    gating = tol['gating_2026-09-29-revision']
    g = items['instrumentGating']['declared']
    c.eq('instrumentGating: gated and descriptive counts', (len(gating['gated']), len(gating['descriptive'])),
         (len(g['gated']), len(g['descriptive'])))
    c.eq('regionStatistics: constants', (regions.MIN_PX, regions.PATCH_RINGS, regions.PLATEAU_PT),
         (12, (0.0, 2.0, 4.0, 8.0, 16.0, 32.0, 48.0), 48.0))
    c.eq('regionStatistics: step bins', regions.STEP_BINS,
         (-48.0, -32.0, -24.0, -16.0, -8.0, -4.0, -2.0, 0.0, 2.0, 4.0, 8.0, 16.0, 24.0, 32.0, 48.0))


def level(cell):
    return int(cell['background'].split('-')[1])


def bed_and_split(c, items, d):
    bed_path = HERE / 'bed' / 'bed.json'
    bed = json.loads(bed_path.read_text())
    cells, passes = bed['cells'], bed['passes']
    sp = items['split']['declared']
    c.eq('split: bed.json SHA-256', sha(bed_path.read_bytes()), sp['splitSha256'])
    c.eq('split: scenes SHA-256', sha((HERE / 'bed' / 'scenes-w42-body.json').read_bytes()), sp['scenesSha256'])
    c.eq('split: twin audit SHA-256', sha((HERE / 'bed' / 'twin-audit.json').read_bytes()), sp['twinAuditSha256'])
    pins = json.loads((HERE / 'bed' / 'pins.json').read_text())
    c.eq('split: bed/pins.json', pins, {'scenes-w42-body.json': sp['scenesSha256'], 'bed.json': sp['splitSha256'],
                                        'twin-audit.json': sp['twinAuditSha256']})
    holdout = sorted(k for k, v in cells.items() if v['role'] == 'holdout')
    c.eq('split: H cells', holdout, sorted(sp['H']['cells']))
    c.eq('split: H at 1x', sorted(k for k in holdout if any(p.startswith('1x') for p in cells[k]['passes'])),
         sorted(sp['H']['at1x']))
    c.eq('split: H cell-passes', sum(len(cells[k]['passes']) for k in holdout), sp['H']['cellPasses'])
    c.eq('split: s = 112 appears in H only',
         {v['role'] for v in cells.values() if v['geometry'].get('shortSide') == 112}, {'holdout'})
    glass = {p: v['glass'] for p, v in bed['counts'].items()}
    b = items['bed']['declared']
    c.eq('bed: glass cells per pass', glass, b['perPass'])
    c.eq('bed: glass cells', sum(glass.values()), b['glassCells'])
    c.eq('bed: references', sum(v['references'] for v in bed['counts'].values()), b['references'])

    # candidate 2: one ordinate per family-A level and span stratum, on the 2x calibration cells
    strata = {}
    for ep, key in PASS_OF.items():
        seen = set()
        for cid in passes[key]['cells']:
            cell = cells[cid]
            if cell['family'] == 'A' and cell['role'] == 'calibration':
                s = cell['geometry']['shortSide']
                seen.add((level(cell), 0 if s <= 64 else s))
        strata[ep] = len(seen)
    counted = items['candidate2']['declared']['countedByOrdinates']
    c.eq("candidate2: ordinates per endpoint", strata, {ep: counted[ep] for ep in ENDPOINTS})

    # candidate 1, light receded: E3's F unchanged, extended by the capsule's greys above 150
    fit = json.loads((ROOT / 'packages/calibration/results/2026-09-27-w41-g1-identification/body/attempt-1/'
                             'light-inactive-E3-fit.json').read_text())
    lr = items['candidate1']['declared']['lightReceded']
    c.eq("candidate1: E3's F ordinates", fit['neutralOrdinatesCodes'], [150, 157, 164, 171, 178, 188, 197])
    c.true("candidate1: E3's F ordinates as declared", '[150, 157, 164, 171, 178, 188, 197]' in lr['F'])
    ext = sorted(level(cells[cid]) for cid in passes['2x-light-receded']['cells']
                 if cells[cid]['family'] == 'A' and cells[cid]['role'] == 'calibration'
                 and cells[cid]['component'] == 'capsule-button' and level(cells[cid]) > 150)
    c.eq('candidate1: the extension levels on the capsule', ext, [160, 176, 192, 208, 224, 240, 255])
    c.eq('candidate1: the extension count', len(ext), lr['extensionFamily']['count'])

    web = json.loads((HERE / 'bed' / 'web-plan.json').read_text())
    c.true('webPlan: every glass cell web-plannable',
           all(v['declared'] == v['plannable'] for v in web['passTotals'].values())
           and sum(v['declared'] for v in web['passTotals'].values()) == b['glassCells'])
    plan = (HERE / 'bed' / 'sitting' / 'dry-plan.txt').read_text()
    totals = json.loads(re.search(r'^totals: (\{.*\})$', plan, flags=re.M).group(1))
    c.eq('sitting: dry-plan totals', totals, {'dumpLaunches': 8, 'dumpScenes': 447, 'captureLaunches': 80,
                                              'glass': 3129, 'references': 264, 'sentinels': 48,
                                              'captures': 3441})
    c.true('sitting: 10.31 h', 'TOTAL      37115.5 s = 10.31 h' in
           (HERE / 'bed' / 'sitting' / 'timing.txt').read_text())
    base = json.loads((HERE / 'bed' / 'runtime-base-sample.json').read_text())
    c.eq('runtimeBase: cells', base['count'], 40)

    probe = sum(len(v['passes']) for v in cells.values() if v['role'] == 'probe')
    runner = ast.parse((HERE / 'bed' / 'exposure' / 'runner.py').read_text())
    fields = next(ast.literal_eval(n.value) for n in runner.body if isinstance(n, ast.Assign)
                  and any(getattr(t, 'id', None) == 'PIN_FIELDS' for t in n.targets))
    c.eq('exposureRunner: pin fields', fields, ('inventoryPath', 'inventorySha256', 'declarationPath',
                                                'declarationSha256', 'closurePath', 'closureSha256'))
    c.eq('exposureRunner: scope', (b['glassCells'] - probe, sp['H']['cellPasses']), (423, 40))


def tinted_failures():
    """The receded tinted L1 failures of round 3's best combination, from its per-cell detail."""
    text = (HERE / 'gate' / 'rehearsal' / 'round3' / 'rehearsal-r3-detail.txt').read_text()
    combo = ep = None
    out = set()
    for line in text.splitlines():
        m = re.match(r'^(r3-\w+) \(', line)
        if m:
            combo, ep = m.group(1), None
            continue
        if line.startswith('(c)'):
            combo = None
        m = re.match(r'^  (light|dark)-(active|receded)\s+(.*)$', line)
        rest = m.group(3) if m else line.strip()
        if m and combo:
            ep = f'{m.group(1)}-{m.group(2)}'
        hit = re.match(r'L1 (\dx) (\S+) web', rest)
        if combo == 'r3-2pgb' and ep and ep.endswith('receded') and hit and '-tint-' in hit.group(2):
            out.add(f"apple-macos-27.0-{hit.group(1)}-{ep.split('-')[0]}-standard-glass0.5 {hit.group(2)}")
    return sorted(out)


def gate(c, items):
    stops = json.loads((HERE / 'gate' / 'stops' / 'stops-declaration.json').read_text())
    c.eq('stops: populations', (len(stops['stopH']['population']['cells']), len(stops['stopP']['population']['cells'])),
         (16, 26))
    strata = HERE / 'gate' / 'sheets' / 'strata.json'
    e = items['eyeStrata']['declared']
    c.eq('eyeStrata: strata.json SHA-256', sha(strata.read_bytes()), e['strataSha256'])
    test = (ROOT / 'packages/calibration/test/adopted-thresholds.test.ts').read_text()
    for name in ('const structureVerdict', 'const chromaStructureNamedMisses', 'readonly native?: number'):
        c.true(f'gateReferees: adopted-thresholds.test.ts carries {name}', name in test)
    tinted = items['l1TintedReceded']['pendingUser']['cells']
    c.eq('l1TintedReceded: the cells against r3-2pgb\'s receded tinted L1 failures', tinted_failures(), sorted(tinted))
    c.eq('l1TintedReceded: the named misses are the cells', items['l1TintedReceded']['declared']['namedMisses'], tinted)
    sys.path.insert(0, str(HERE / 'gate' / 'owner'))
    owner = __import__('importlib').util.spec_from_file_location('run_owner', HERE / 'gate' / 'owner' / 'run-owner.py')
    ro = __import__('importlib').util.module_from_spec(owner)
    owner.loader.exec_module(ro)
    for name, (anchor, _, _) in ro.CLOSURE_ASSERTIONS.items():
        c.eq(f'ownerTest: the {name} assertion the closure step reads, in the committed test', test.count(anchor), 1)
    w41 = json.loads((ROOT / 'packages/calibration/results/2026-09-27-w41-g0-declaration/closure.json').read_text())
    b1 = w41['families']['B1']
    c.eq("candidate2Chroma: E3's g form (W41 G0 closure, B1)",
         (b1['name'], b1['chromaticParametersPerEndpoint'], b1['nodes'], b1['bounds']), ('E3', 3, [63, 93, 118], [0, 3]))


def production_pin(c, digest):
    pin = json.loads(PIN.read_text())
    ours = {'declarationPath': f'{REL}/declaration.json', 'declarationSha256': digest,
            'closurePath': f'{REL}/closure.json'}
    for key, value in ours.items():
        c.true(f'production-pin.json: {key} names another declaration ({pin.get(key)!r})',
               pin.get(key) in (None, value))
    return pin


def check():
    c = Check()
    d = json.loads(DECLARATION.read_text())
    c.eq('schema', d.get('schema'), 'w42-declaration-1')
    items = structure(c, d)
    twin(c, items)
    forward = families_and_law(c, items)
    masks_and_tests(c, items, forward)
    bed_and_split(c, items, d)
    gate(c, items)
    production_pin(c, sha(DECLARATION.read_bytes()))
    return c, d, items


def closure(d, items, digest):
    """What the one-exposure scorer implements (clauses 6 and 11), taken from the hashed items."""
    pick = ('survivalBars', 'regionStatistics', 'nativeT', 'exposureRunner')
    return {'schema': 'w42-closure-1', 'declarationSha256': digest,
            'declaration': f'{REL}/declaration.json',
            'items': {k: items[k]['declared'] for k in pick},
            'rulings': {it['id']: it['pendingUser']['ruling'] for it in items.values() if 'pendingUser' in it}}


def main(argv):
    if len(argv) != 2 or argv[1] not in ('check', 'hash'):
        print(__doc__)
        return 64
    c, d, items = check()
    waiting = pending(items)
    print(f"W42 G0 declaration: {len(items)} items, {len(d['sources'])} pinned sources")
    for f in c.failures:
        print('  MISMATCH', f)
    for it in waiting:
        print(f"  PENDING (user) {it['id']}: {it['pendingUser']['question']}")
    if c.failures:
        print(f'check: {len(c.failures)} mismatch(es)')
        return 1
    print('check: consistent with the stream files' + (f'; {len(waiting)} item(s) pending the user' if waiting else ''))
    if argv[1] == 'check':
        return 0
    if waiting:
        print('hash REFUSES: ' + ', '.join(it['id'] for it in waiting) + ' wait on the user; write each ruling into '
              'declaration.json and declaration.md, then hash')
        return 2
    digest = sha(DECLARATION.read_bytes())
    pin = production_pin(Check(), digest)
    if pin.get('declarationSha256') or DIGEST.exists() or CLOSURE.exists():
        print('hash REFUSES: a declaration is already hashed and pinned; a changed declaration after the first '
              'capture voids the sitting (clause 1), and this tool never overwrites one')
        return 2
    body = json.dumps(closure(d, items, digest), indent=2, sort_keys=True, ensure_ascii=False) + '\n'
    with CLOSURE.open('x') as f:
        f.write(body)
    with DIGEST.open('x') as f:
        f.write(f'{digest}  declaration.json\n')
    pin.update(declarationPath=f'{REL}/declaration.json', declarationSha256=digest,
               closurePath=f'{REL}/closure.json', closureSha256=sha(body.encode()))
    PIN.write_text(json.dumps(pin, indent=2) + '\n')
    print(f'declaration.json sha256 {digest}; closure.json sha256 {pin["closureSha256"]}; pinned in {PIN.relative_to(ROOT)}'
          '; commit all three before the first capture')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
