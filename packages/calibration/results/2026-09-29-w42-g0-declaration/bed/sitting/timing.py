#!/usr/bin/env python3.12
"""Recompute the W42 sitting's length from REAL timings, not W39's 9.53 s/capture model.

Inputs, all measured and read-only:
- W39 G1's committed attestations (packages/calibration/results/2026-09-26-w39-g1-colour-edge-
  sitting/attest/<pass>/runs.json, run-*/attest.open.json and attest.close.json): for every
  admitted run, its fixture count, first and last capture time and its opening and closing
  machine reads. A run's wall time is close - open; its capture interval is (last - first) /
  (n - 1); a per-run fixed cost is fitted as wall = a + b n by least squares per protocol
  and scale; the gap between runs and between passes is open(next) - close(previous).
- memo D's dump attestations (~/vitrea-w42/grounding/dumps/runs/*/attest.open|close): 24
  scenes at settle 8 and 4 scenes at settle 16, which separate the per-scene cost from the
  per-launch cost.
- W42's counts: bed/sitting/pass-spec.py plan over the bed files.

W39's runs captured both schemes in one process; W42's capture one. The per-capture interval
is a property of the harness's per-cell protocol (settle, dwell, reset interstitial) and is
carried over; the run count and per-run cost are W42's.
"""
import datetime
import importlib.util
import json
from pathlib import Path
import re
import statistics

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
W39 = REPO / 'packages/calibration/results/2026-09-26-w39-g1-colour-edge-sitting/attest'
MEMO_D = Path('/Users/new/vitrea-w42/grounding/dumps/runs')
CHARTER_MODEL_SECONDS = 31367.8


def when(text):
    return datetime.datetime.fromisoformat(text.replace('Z', '+00:00')).timestamp()


def w39_runs():
    rows = []
    for pdir in sorted(p for p in W39.iterdir() if p.is_dir() and not p.name.startswith('preflight')):
        runs = json.loads((pdir / 'runs.json').read_text())
        for r in runs:
            if not r.get('admitted') or 'firstCapture' not in r:
                continue
            d = pdir / r['run']
            o = json.loads((d / 'attest.open.json').read_text())['recordedAt']
            c = json.loads((d / 'attest.close.json').read_text())['recordedAt']
            scale = 1 if '-1x' in pdir.name else 2
            rows.append(dict(passName=pdir.name, run=r['run'], scale=scale,
                             protocol='long' if pdir.name.endswith('sentinel') else 'normal',
                             n=r['fixtures'], open=when(o), close=when(c),
                             first=when(r['firstCapture']), last=when(r['lastCapture'])))
    return sorted(rows, key=lambda r: r['open'])


def fit(rows):
    """wall = a + b n, least squares; plus the capture interval's median."""
    xs = [r['n'] for r in rows]
    ys = [r['close'] - r['open'] for r in rows]
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx if sxx else None
    a = my - b * mx if b is not None else None
    intervals = [(r['last'] - r['first']) / (r['n'] - 1) for r in rows if r['n'] > 1]
    overheads = [(r['close'] - r['open']) - (r['last'] - r['first']) for r in rows]
    return dict(runs=len(rows), captures=sum(xs), wallSeconds=round(sum(ys), 1),
                perCaptureFit=None if b is None else round(b, 4), perRunFit=None if a is None else round(a, 2),
                intervalMedian=round(statistics.median(intervals), 4),
                intervalMean=round(statistics.fmean(intervals), 4),
                overheadMedian=round(statistics.median(overheads), 2),
                secondsPerCaptureAllIn=round(sum(ys) / sum(xs), 4))


def gaps(rows):
    within, between = [], []
    for prev, nxt in zip(rows, rows[1:]):
        g = nxt['open'] - prev['close']
        (within if prev['passName'] == nxt['passName'] else between).append(
            dict(after=f"{prev['passName']}/{prev['run']}", before=f"{nxt['passName']}/{nxt['run']}", seconds=round(g, 1)))
    return within, between


def memo_d_dumps():
    rows = []
    for d in sorted(MEMO_D.iterdir()):
        o = re.search(r'^at=(.+)$', (d / 'attest.open').read_text(), re.M)[1]
        c = re.search(r'^at=(.+)$', (d / 'attest.close').read_text(), re.M)[1]
        rows.append(dict(run=d.name, scenes=len(list((d / 'json').glob('*.json'))),
                         settle=16 if d.name.endswith('settle16') else 8, wall=when(c) - when(o)))
    a8 = [r for r in rows if r['settle'] == 8]
    a16 = [r for r in rows if r['settle'] == 16]
    w8, n8 = statistics.fmean(r['wall'] for r in a8), a8[0]['scenes']
    w16, n16 = statistics.fmean(r['wall'] for r in a16), a16[0]['scenes']
    # wall = launch + scenes (settle + c): two settles solve launch and c.
    c = ((w8 - w16) - (n8 * 8 - n16 * 16)) / (n8 - n16)
    launch = w8 - n8 * (8 + c)
    return dict(runs=rows, meanWall24AtSettle8=round(w8, 2), meanWall4AtSettle16=round(w16, 2),
                perSceneBeyondSettle=round(c, 3), perLaunch=round(launch, 2), settle=8,
                perSceneAtSettle8=round(8 + c, 3))


def main():
    spec = importlib.util.spec_from_file_location('w42_pass_spec_timing', HERE / 'pass-spec.py')
    P = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(P)
    plan = P.plan()
    rows = w39_runs()
    fits = {}
    for protocol in ('normal', 'long'):
        for scale in (1, 2):
            sel = [r for r in rows if r['protocol'] == protocol and r['scale'] == scale]
            if sel:
                fits[f'{protocol}-{scale}x'] = fit(sel)
    within, between = gaps(rows)
    within_med = statistics.median(g['seconds'] for g in within)
    between_list = [g['seconds'] for g in between]
    dumps = memo_d_dumps()
    # W42 arithmetic, pass by pass: each run costs a + b n from its protocol-scale fit.
    passes, total_capture, total_runs = [], 0.0, 0
    for p in plan['passes']:
        if p['kind'] == 'dump':
            n = p['runsDetail'][0]['scenes']
            secs = dumps['perLaunch'] + n * dumps['perSceneAtSettle8']
            passes.append(dict(name=p['name'], kind='dump', scenes=n, seconds=round(secs, 1)))
            continue
        f = fits[('long' if p['kind'] == 'sentinel' else 'normal') + f'-{p["scale"]}x']
        # A run costs its measured overhead (wall - capture span: machine reads, backgrounds,
        # launch, the first cell's settle) plus (n - 1) measured capture intervals. This is
        # used for every pass: W39's runs were 206-332 cells, so the a + b n fit (kept as a
        # cross-check, crossCheckSeconds) extrapolates to W42's 15-25-cell 1x runs, and every
        # W39 sentinel run had 4 cells, so b is not identified there at all.
        secs = sum(f['overheadMedian'] + f['intervalMedian'] * (r['cells'] - 1) for r in p['runsDetail'])
        if f['perCaptureFit'] is not None:
            cross = sum(f['perRunFit'] + f['perCaptureFit'] * r['cells'] for r in p['runsDetail'])
        else:
            cross = None
        total_runs += len(p['runsDetail'])
        total_capture += secs
        passes.append(dict(name=p['name'], kind=p['kind'], runs=len(p['runsDetail']), captures=p['captures'],
                           seconds=round(secs, 1), crossCheckSeconds=None if cross is None else round(cross, 1)))
    dump_seconds = sum(q['seconds'] for q in passes if q['kind'] == 'dump')
    launches = total_runs + 8
    gap_seconds = within_med * (launches - 1)
    mode_switches = 4
    switch_seconds = mode_switches * statistics.median(between_list)
    total = total_capture + dump_seconds + gap_seconds + switch_seconds
    value = dict(
        schema='w42-sitting-timing-1',
        sources=dict(w39Attest=str(W39.relative_to(REPO)), memoDDumps=str(MEMO_D),
                     w39AdmittedRuns=len(rows)),
        w39Fits=fits, w39GapBetweenRunsMedian=within_med,
        w39GapBetweenPasses=between, memoDDumps=dumps,
        w42=dict(passes=passes, captureSeconds=round(total_capture, 1), dumpSeconds=round(dump_seconds, 1),
                 launches=launches, interRunGapSeconds=round(gap_seconds, 1),
                 modeSwitches=mode_switches, modeSwitchSeconds=round(switch_seconds, 1),
                 totalSeconds=round(total, 1), totalHours=round(total / 3600, 2),
                 captureHours=round(total_capture / 3600, 2), dumpHours=round(dump_seconds / 3600, 2)),
        charter=dict(modelSeconds=CHARTER_MODEL_SECONDS, modelHours=round(CHARTER_MODEL_SECONDS / 3600, 2),
                     dumpModelSeconds=3450, modelTotalHours=round((CHARTER_MODEL_SECONDS + 3450) / 3600, 2)),
        excludes='waiting for HID idle beyond the measured gaps, quarantines and continuations, the grant '
                 'switch and the pre-sitting rehearsal')
    (HERE / 'timing.json').write_text(json.dumps(value, indent=1) + '\n')
    n2, n1, l2, l1 = fits['normal-2x'], fits['normal-1x'], fits['long-2x'], fits['long-1x']
    lines = [
        'W42 sitting length from real timings (timing.py; timing.json has every input)',
        '',
        f'W39 G1 admitted runs read: {len(rows)} (bed and sentinel; preflight excluded).',
        'A run is modelled as its measured overhead (wall - capture span) + (n - 1) capture intervals.',
        f'Normal 2x: overhead {n2["overheadMedian"]} s, interval {n2["intervalMedian"]} s '
        f'(cross-check fit wall = {n2["perRunFit"]} s + {n2["perCaptureFit"]} s x n)',
        f'Normal 1x: overhead {n1["overheadMedian"]} s, interval {n1["intervalMedian"]} s '
        f'(cross-check fit wall = {n1["perRunFit"]} s + {n1["perCaptureFit"]} s x n)',
        f'Long 2x / 1x: overhead {l2["overheadMedian"]} / {l1["overheadMedian"]} s, interval '
        f'{l2["intervalMedian"]} / {l1["intervalMedian"]} s',
        f'Normal 2x: wall = {n2["perRunFit"]} s + {n2["perCaptureFit"]} s x n  '
        f'(interval median {n2["intervalMedian"]} s; {n2["runs"]} runs, {n2["captures"]} captures)',
        f'Normal 1x: wall = {n1["perRunFit"]} s + {n1["perCaptureFit"]} s x n  '
        f'(interval median {n1["intervalMedian"]} s; {n1["runs"]} runs)',
        f'Long 2x / 1x (sentinels, 4 cells a run): all-in {l2["secondsPerCaptureAllIn"]} / '
        f'{l1["secondsPerCaptureAllIn"]} s per capture; interval median {l2["intervalMedian"]} / {l1["intervalMedian"]} s',
        f'Gap between runs (next open - previous close), median: {within_med} s; between passes: '
        f'{sorted(between_list)} s',
        f'memo D dumps: {dumps["perSceneAtSettle8"]} s per scene at settle 8 + {dumps["perLaunch"]} s per launch '
        f'(24 scenes {dumps["meanWall24AtSettle8"]} s; 4 scenes at settle 16 {dumps["meanWall4AtSettle16"]} s)',
        '',
        f'W42 (pass-spec.py plan: {plan["totals"]["glassCaptures"]:,} glass + {plan["totals"]["referenceCaptures"]:,} '
        f'references + {plan["totals"]["sentinelCaptures"]} sentinel captures; {plan["totals"]["dumpScenes"]} dump scenes):',
    ]
    for q in passes:
        lines.append(f'  {q["name"]:28s} {q.get("captures", q.get("scenes")):5d} '
                     f'{"scenes" if q["kind"] == "dump" else "captures"}  {q["seconds"]:9.1f} s')
    lines += ['',
              f'captures {total_capture:9.1f} s = {total_capture / 3600:.2f} h',
              f'dumps    {dump_seconds:9.1f} s = {dump_seconds / 3600:.2f} h',
              f'gaps     {gap_seconds:9.1f} s ({launches - 1} gaps x {within_med} s)',
              f'switches {switch_seconds:9.1f} s ({mode_switches} display mode switches at the W39 pass-gap median)',
              f'TOTAL    {total:9.1f} s = {total / 3600:.2f} h',
              '',
              f'Charter v2.1 model: {CHARTER_MODEL_SECONDS} s capture ({CHARTER_MODEL_SECONDS / 3600:.2f} h) + about '
              f'3,450 s dumps = {(CHARTER_MODEL_SECONDS + 3450) / 3600:.2f} h.',
              'Excluded: idle waits beyond the measured gaps, quarantines, the grant switch and the rehearsal.']
    (HERE / 'timing.txt').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
