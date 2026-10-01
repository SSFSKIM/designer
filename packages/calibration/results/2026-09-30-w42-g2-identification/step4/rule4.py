#!/usr/bin/env python3.12
"""W42 G2 step 4: rule 4 (clause 9' on the landing path) and clause 7 on the W42 bed.

The improvement-landing addendum (`../improvement-landing-addendum.md`, SHA-256 0398c9c8…), sections
4 and 5, executed as written:

- population: the new bed's web-plannable calibration and validation cells of light active, light
  receded and dark receded, both scales (85 / 92 / 107 cell-passes), each rendered by vitrea with the
  shipped documents and with each candidate (`render.py bed`);
- reading: the declared instrument (`instrument/regions.py` on `forward.Cell`'s deep masks) on each
  render and on Apple's plurality frame from the archive through step 2's guarded reader
  (`step2/common.py`: pins verified at import, the raw sitting root denied, roles calibration and
  validation only; H is never requested);
- errors: e = rendered - Apple per region statistic and channel, measured when Apple's value lies in
  (5, 250), otherwise censored and entered as the rail deficit of W41 G1's body41.score;
- (a) per stratum (kind x span class, both scales pooled), pooled rms over cells (equal weight, each
  cell's mean of e^2 over its measured statistics and channels) of the candidate <= the shipped
  render's, literally; (b) every statistic and channel within the shipped render's |e| (or deficit)
  plus 2 codes; (c) clause 7, below.

Clause 7 (uniform invariance) on family A: candidate 1's deep median equals its reference within one
code per channel (the shipped render in light active and dark receded; light receded, the `c1ref`
render, E3 with its extended F alone); candidate 2's equals its own T with every spatial gate at its
identity. The runtime reads candidate 2's table only under the law, so that reference cannot be
rendered: it is the table itself, read as `bodyToneTableCodesAt` reads it (the document's levels,
spans and codes, linear in level within a row, linear in span between rows, ends held) at the
backdrop's grey and the cell's span. A grey argument carries no chroma term.

    python3.12 -B rule4.py            -> rule4.json, rule4.txt, SCRATCH/rule4-statistics.json.gz
"""
import gzip
import hashlib
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'step2'))
import common as C  # noqa: E402  (verifies the pins; denies the raw sitting root)

import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

R = C.R
SCRATCH = Path(os.environ.get('W42_STEP4_SCRATCH', '/tmp/w42-g2-step4'))
ADDENDUM_SHA = '0398c9c85509729d7d3be73ac12bafe6af477b62d2b194820762f9a06cf5911f'
EPS = ('light-rest', 'light-inactive', 'dark-inactive')
CANDIDATES = ('c1', 'c2')
KIND = {'A': 'uniform', 'B': 'grey checker', "B'": 'grey checker', 'E': 'colour checker',
        'C': 'patch / impulse', 'D': 'step'}
KIND_ORDER = ('uniform', 'grey checker', 'patch / impulse', 'step', 'colour checker')
SPANS = ('t=0', 's=80', 's=96', 's=128', 's=160')
TOLERANCE = 2.0

# The addendum's section 5, cell-passes per stratum; the derivation below must reproduce it.
EXPECTED = {
    'light-rest': {('uniform', 't=0'): 13, ('uniform', 's=96'): 12, ('uniform', 's=128'): 3,
                   ('uniform', 's=160'): 4, ('grey checker', 't=0'): 7, ('grey checker', 's=80'): 1,
                   ('grey checker', 's=96'): 9, ('grey checker', 's=128'): 3, ('grey checker', 's=160'): 8,
                   ('patch / impulse', 's=96'): 6, ('patch / impulse', 's=128'): 1,
                   ('patch / impulse', 's=160'): 5, ('step', 't=0'): 1, ('step', 's=96'): 4,
                   ('step', 's=160'): 2, ('colour checker', 's=96'): 4, ('colour checker', 's=160'): 2},
    'light-inactive': {('uniform', 't=0'): 13, ('uniform', 's=96'): 12, ('uniform', 's=128'): 3,
                       ('uniform', 's=160'): 4, ('grey checker', 't=0'): 9, ('grey checker', 's=80'): 1,
                       ('grey checker', 's=96'): 9, ('grey checker', 's=128'): 2,
                       ('grey checker', 's=160'): 4, ('patch / impulse', 't=0'): 4,
                       ('patch / impulse', 's=96'): 7, ('patch / impulse', 's=128'): 1,
                       ('patch / impulse', 's=160'): 5, ('step', 't=0'): 3, ('step', 's=96'): 11,
                       ('colour checker', 's=96'): 4},
    'dark-inactive': {('uniform', 't=0'): 13, ('uniform', 's=80'): 3, ('uniform', 's=96'): 12,
                      ('uniform', 's=128'): 3, ('uniform', 's=160'): 4, ('grey checker', 't=0'): 9,
                      ('grey checker', 's=80'): 1, ('grey checker', 's=96'): 9, ('grey checker', 's=128'): 2,
                      ('grey checker', 's=160'): 4, ('patch / impulse', 't=0'): 4,
                      ('patch / impulse', 's=96'): 11, ('patch / impulse', 's=128'): 5,
                      ('patch / impulse', 's=160'): 5, ('step', 't=0'): 3, ('step', 's=96'): 15,
                      ('colour checker', 's=96'): 4},
}


def span_class(s):
    return 't=0' if s <= 64 else f's={s}'


def pass_key(ep, scale):
    scheme, pose = ep.split('-')
    return f'{scale}x-{scheme}-{"active" if pose == "rest" else "receded"}'


DOCS = json.loads((HERE / 'documents/documents.json').read_text())


def expected_documents(name, ep):
    """(active sha12, receded sha12) every capture of this set and endpoint must name."""
    scheme = ep.split('-')[0]
    if name == 'shipped':
        p = C.P.REPO / 'packages/calibration/profiles'
        return tuple(hashlib.sha256((p / f'apple-macos-27.0-1x-{scheme}-standard-glass0.5{s}.json')
                                    .read_bytes()).hexdigest()[:12] for s in ('', '-receded'))
    s = DOCS['sets'][name]
    return s[scheme]['sha256'], s[f'{scheme}Receded']['sha256']


def render(name, ep, scale, cid):
    sid = C.sid(cid, ep)
    d = SCRATCH / 'bed' / name / pass_key(ep, scale) / sid
    cell = json.loads((d / 'cell__webgpu.json').read_text())
    want = expected_documents(name, ep)
    named = re.findall(r'(materialProfile|recededProfile)=\S+ sha256:([0-9a-f]{12})', cell['capturePath'])
    if dict(named) != {'materialProfile': want[0], 'recededProfile': want[1]}:
        raise SystemExit(f'{d}: names {named}, not the {name} documents {want}')
    if cell['renderer'] != 'webgpu' or not cell['deterministic'] or cell['sceneId'] != sid:
        raise SystemExit(f'{d}: not a deterministic WebGPU capture of {sid}')
    if cell['pixelSize'] != [320 * scale, 200 * scale]:
        raise SystemExit(f'{d}: pixel size {cell["pixelSize"]}')
    with Image.open(d / f'{sid}__webgpu.png') as im:
        return np.asarray(im.convert('RGB'), dtype=np.float64)


def gap_of(cell, stratum):
    """Where a failing cell falls against the addendum's section 7 named gaps. A DESCRIPTION for the
    report only: rule 4 (b) has no exemption, and nothing here changes a verdict."""
    scale, cid = cell.split(' ', 1)
    if scale == '1x' and cid == 'bp-p1-c8-rrect-lg':
        return 'gap 1, class (a): the 1x pitch-8 rrect-lg checker'
    if stratum.startswith('colour checker'):
        return 'gap 5: family E chroma'
    if cid.endswith('rrect-ml') or cid.endswith('rrect-lg'):
        return 'gap 1, class (b): rrect-ml / rrect-lg span growth'
    return 'outside the named gaps'


def masked_stats(c, img):
    y = np.full(img.shape, np.nan)
    y[c.mask] = img[c.mask]
    return R.statistics(c, y, R.populations(c))


def deficit(pred, apple):
    return max(pred - 5.0, 0.0) if apple <= 5 else max(250.0 - pred, 0.0)


def table_read(levels, spans, rows, level, span):
    """bodyToneTableCodesAt on a grey argument (no chroma term), in codes."""
    def row_at(r):
        return float(np.interp(level, levels, r))
    if span <= spans[0]:
        f = row_at(rows[0])
    elif span >= spans[-1]:
        f = row_at(rows[-1])
    else:
        k = int(np.searchsorted(spans, span, side='left')) - 1
        u = (span - spans[k]) / (spans[k + 1] - spans[k])
        f = row_at(rows[k]) + u * (row_at(rows[k + 1]) - row_at(rows[k]))
    return min(255.0, max(0.0, f))


def c2_table(ep):
    doc = 'light' if ep == 'light-rest' else ('lightReceded' if ep == 'light-inactive' else 'darkReceded')
    patch = json.loads((C.P.REPO / DOCS['sets']['c2'][doc]['path']).read_text())['patch']
    return patch['bodyToneTableLevels'], patch['bodyToneTableSpans'], patch['bodyToneTableCodes']


def main():
    if hashlib.sha256((HERE.parent / 'improvement-landing-addendum.md').read_bytes()).hexdigest() != ADDENDUM_SHA:
        raise SystemExit('the addendum moved')
    _, wave, reader = C.open_reader()          # the archive copy verified by digest; cal/val roles only
    assert set(reader.allowed) and not any(wave.roles[s] == 'holdout' for s in reader.allowed)
    full, summary, clause7 = [], {}, {}
    lines = ['W42 G2 step 4: rule 4 (improvement-landing addendum sections 4-5) and clause 7 on the W42 bed',
             f'addendum {ADDENDUM_SHA}; archive inventory {reader.generation}; scratch {SCRATCH}', '']
    for ep in EPS:
        strata = defaultdict(lambda: dict(cells=[], **{n: [] for n in ('shipped',) + CANDIDATES}))
        failures = {n: [] for n in CANDIDATES}
        counts = defaultdict(int)
        c7 = {n: [] for n in CANDIDATES}
        levels, spans, rows = c2_table(ep)
        for scale in (2, 1):
            for c in C.cells(ep, scale, ('calibration', 'validation')):
                stratum = (KIND[c.letter], span_class(c.geometry['shortSide']))
                counts[stratum] += 1
                apple = C.native_stats(c)
                imgs = {n: render(n, ep, scale, c.bed_id) for n in ('shipped',) + CANDIDATES}
                st = {n: masked_stats(c, imgs[n]) for n in imgs}
                cell_sq = {n: [] for n in imgs}
                for k, nv in apple.items():
                    measured = 5 < nv < 250
                    row = dict(ep=ep, scale=scale, cell=c.bed_id, role=c.role, stratum=list(stratum), stat=k,
                               apple=nv, measured=measured)
                    for n in imgs:
                        pv = st[n][k]
                        row[n] = pv
                        if measured:
                            cell_sq[n].append((pv - nv) ** 2)
                    s_err = abs(st['shipped'][k] - nv) if measured else deficit(st['shipped'][k], nv)
                    for n in CANDIDATES:
                        c_err = abs(st[n][k] - nv) if measured else deficit(st[n][k], nv)
                        row[f'{n}Worse'] = c_err - s_err
                        if c_err > s_err + TOLERANCE:
                            failures[n].append(dict(cell=f'{scale}x {c.bed_id}', role=c.role,
                                                    stratum=' '.join(stratum), stat=k,
                                                    kind='measured' if measured else 'censored', apple=nv,
                                                    shipped=st['shipped'][k], candidate=st[n][k],
                                                    shippedError=s_err, candidateError=c_err,
                                                    worseBy=c_err - s_err))
                    full.append(row)
                entry = strata[stratum]
                entry['cells'].append(f'{scale}x {c.bed_id}')
                for n in imgs:
                    entry[n].append(float(np.mean(cell_sq[n])) if cell_sq[n] else None)
                if c.letter == 'A':
                    grey = float(c.bg_spec['srgb'][0])
                    t2 = table_read(levels, spans, rows, grey, float(c.geometry['shortSide']))
                    deep = {n: [st[n][f'deep|{ch}'] for ch in 'RGB'] for n in imgs}
                    ref1 = deep['shipped']
                    if ep == 'light-inactive':
                        ref1 = [masked_stats(c, render('c1ref', ep, scale, c.bed_id))[f'deep|{ch}'] for ch in 'RGB']
                    c7['c1'].append(dict(cell=f'{scale}x {c.bed_id}', reference=ref1, candidate=deep['c1'],
                                         worst=max(abs(a - b) for a, b in zip(deep['c1'], ref1))))
                    c7['c2'].append(dict(cell=f'{scale}x {c.bed_id}', grey=grey, span=c.geometry['shortSide'],
                                         reference=[t2] * 3, candidate=deep['c2'],
                                         worst=max(abs(a - t2) for a in deep['c2'])))
        got = dict(counts)
        if got != EXPECTED[ep]:
            raise SystemExit(f'{ep}: strata {got} are not the addendum\'s {EXPECTED[ep]}')
        out = dict(strata=[], failures={}, clause7={}, verdict={})
        lines.append(f'== {C.EP_NAME[ep]} ({ep}): {sum(got.values())} cell-passes, {len(got)} strata')
        lines.append(f'   {"stratum":28s} {"n":>3s} {"shipped":>8s} {"c1":>8s} {"c2":>8s}  (pooled rms, codes; '
                     'measured statistics)')
        a_fail = {n: [] for n in CANDIDATES}
        for kind in KIND_ORDER:
            for span in SPANS:
                key = (kind, span)
                if key not in strata:
                    continue
                e = strata[key]
                pooled = {}
                for n in ('shipped',) + CANDIDATES:
                    vals = [v for v in e[n] if v is not None]
                    pooled[n] = float(np.sqrt(np.mean(vals))) if vals else None
                flags = ''
                for n in CANDIDATES:
                    if pooled[n] is not None and pooled[n] > pooled['shipped']:
                        a_fail[n].append(f'{kind} {span}')
                        flags += f' {n}:FAIL(a)'
                out['strata'].append(dict(kind=kind, span=span, cells=e['cells'], pooledRms=pooled,
                                          cellMeanSquares={n: e[n] for n in ('shipped',) + CANDIDATES}))
                fmt = lambda v: f'{v:8.3f}' if v is not None else '       -'
                lines.append(f'   {kind + " " + span:28s} {len(e["cells"]):3d} {fmt(pooled["shipped"])} '
                             f'{fmt(pooled["c1"])} {fmt(pooled["c2"])}{flags}')
        for n in CANDIDATES:
            worst7 = max(r['worst'] for r in c7[n])
            c7_fail = [r for r in c7[n] if r['worst'] > 1.0]
            out['clause7'][n] = dict(cells=len(c7[n]), worst=worst7, failing=c7_fail, rows=c7[n])
            fb = sorted(failures[n], key=lambda r: -r['worseBy'])
            out['failures'][n] = fb
            out['verdict'][n] = dict(a=not a_fail[n], aFailingStrata=a_fail[n], b=not fb,
                                     bFailingStatistics=len(fb),
                                     bFailingCells=sorted({r['cell'] for r in fb}),
                                     c=not c7_fail, passes=not a_fail[n] and not fb and not c7_fail)
            v = out['verdict'][n]
            lines.append(f'   {n}: (a) {"pass" if v["a"] else "FAIL " + ", ".join(v["aFailingStrata"])}; '
                         f'(b) {"pass" if v["b"] else f"FAIL {len(fb)} statistic(s) on {len(v["bFailingCells"])} cell(s)"}; '
                         f'(c) clause 7 worst {worst7:.2f} code over {len(c7[n])} uniform cells '
                         f'{"pass" if v["c"] else "FAIL"}  => rule 4 {"PASSES" if v["passes"] else "FAILS"}')
            for r in fb[:12]:
                lines.append(f'      (b) {r["cell"]} [{r["stratum"]}] {r["stat"]} {r["kind"]}: Apple {r["apple"]:.1f}, '
                             f'shipped {r["shipped"]:.1f} (err {r["shippedError"]:.2f}), {n} {r["candidate"]:.1f} '
                             f'(err {r["candidateError"]:.2f}), worse by {r["worseBy"]:.2f}')
            if len(fb) > 12:
                lines.append(f'      ... {len(fb) - 12} more in rule4.json')
            gaps = defaultdict(lambda: [0, 0.0, set()])
            for r in fb:
                g = gaps[gap_of(r['cell'], r['stratum'])]
                g[0] += 1
                g[1] = max(g[1], r['worseBy'])
                g[2].add(r['cell'])
            out['verdict'][n]['bFailuresByNamedGap'] = {
                k: dict(statistics=v[0], worstWorseBy=v[1], cells=sorted(v[2])) for k, v in gaps.items()}
            for k, v in sorted(gaps.items()):
                lines.append(f'      (b) against section 7: {k}: {v[0]} statistic(s) on {len(v[2])} cell(s), '
                             f'worst {v[1]:.2f} worse than shipped: {", ".join(sorted(v[2]))}')
            for r in c7_fail[:6]:
                lines.append(f'      (c) {r["cell"]}: reference {np.round(r["reference"], 2).tolist()}, '
                             f'{n} {np.round(r["candidate"], 2).tolist()}')
        lines.append('')
        summary[ep] = out
    value = dict(schema='w42-g2-step4-rule4-1', addendum=ADDENDUM_SHA, archiveInventory=reader.generation,
                 tolerance=TOLERANCE, documents={n: DOCS['sets'][n] for n in ('c1', 'c2', 'c1ref')},
                 endpoints=summary,
                 statistics=dict(path=str(SCRATCH / 'rule4-statistics.json.gz')))
    raw = json.dumps(full, sort_keys=True).encode()
    (SCRATCH / 'rule4-statistics.json.gz').write_bytes(gzip.compress(raw, mtime=0))
    value['statistics']['sha256'] = hashlib.sha256(raw).hexdigest()
    value['statistics']['rows'] = len(full)
    C.save(HERE / 'rule4.json', value)
    (HERE / 'rule4.txt').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
