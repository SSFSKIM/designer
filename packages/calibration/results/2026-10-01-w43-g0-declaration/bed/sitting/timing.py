#!/usr/bin/env python3.12
"""A W43 sitting's length, derived from its DECLARED plan and W42 G1's measured rates (G0 (d)).

Derived from W42 G0's timing.py, which stays untouched. W42's model read W42's own bed
(pass-spec.py over bed.json) and W39 G1's runs, so it could price no other membership. This one
prices whatever plan pass-spec.py reads, pass by pass, and takes every rate from W42 G1's
committed attestations (packages/calibration/results/2026-09-30-w42-g1-sitting/attest/): the
same machine, the same side bundle, the same driver and protocols, nine days before W43.

From every ADMITTED run there (runs.json, run-N/attest.open.json and attest.close.json):
- a capture run's wall = close read - open read; its capture span = last - first capture;
  per protocol and scale, the run OVERHEAD (wall - span: machine reads, backgrounds, launch,
  the first cell's settle, the harness's exit) and the capture INTERVAL ((span) / (n - 1)) are
  medians, and a least-squares wall = a + b n is kept as a cross-check;
- a dump launch's wall is fitted as a + b scenes over W42 G1's eight dump launches (87, 92, 101,
  107, 14, 16, 14, 16 scenes), the only dumps on this bundle under this driver;
- the gap between consecutive runs of a pass, between passes at one display mode, and across
  a display-mode change (each median); a gap over STOP_GAP seconds is a stop and its
  continuation (W42 G1 had two inside 2x-light-receded), never a rate.

A run costs overhead + interval (n - 1); a pass costs its runs plus (runs - 1) in-pass gaps; a
dump costs a + b scenes; each boundary between passes costs the between-pass gap, or the
mode-switch gap where the display mode changes, plus SLIDER_WRITE_SECONDS where the slider
position changes. W42 never wrote the slider inside a sitting, so that cost is an ASSUMPTION (a
`defaults write`, its read-back and two process-table reads), stated, not measured.

Excluded: idle waits beyond the measured gaps (the user's touch before a launch), quarantines,
stops and their continuations (the charter adds 10 % for them separately), the orchestrator's
start (pin check, Universal Control report, the as-found slider), the trap's restore and any
grant swap.

    timing.py --sitting g1a|g1b   # the declared plan (pass-spec.plan_path); writes timing-<sitting>.*
    timing.py --stand-in          # stand_in.build(): a REHEARSAL on a G1a-shaped stand-in
"""
import argparse
import datetime
import importlib.util
import json
from pathlib import Path
import statistics

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
W42_G1 = REPO / 'packages/calibration/results/2026-09-30-w42-g1-sitting/attest'
STOP_GAP = 60.0                  # seconds; a longer gap between runs is a stop, not a rate
SLIDER_WRITE_SECONDS = 1.0       # ASSUMED: defaults write + read-back + two process tables
CHARTER_G1A = dict(captures=4103, modelledHours=11.26, atMacHours=12.4,
                   source='charter Design, "The two sittings": G1a total, W42 G0\'s model rates')
_MODULES = {}


def module(name, path):
    if name not in _MODULES:
        spec = importlib.util.spec_from_file_location(name, path)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        _MODULES[name] = m
    return _MODULES[name]


def pass_spec():
    return module('w43_pass_spec_timing', HERE / 'pass-spec.py')


def when(text):
    return datetime.datetime.fromisoformat(text.replace('Z', '+00:00')).timestamp()


# ---------------------------------------------------------------- the measurement

def w42_runs(attest=W42_G1):
    """Every admitted W42 G1 run (captures and dumps), in the order the sitting took them."""
    rows = []
    for pdir in sorted(p for p in Path(attest).iterdir() if p.is_dir()):
        for r in json.loads((pdir / 'runs.json').read_text()):
            d = pdir / r['run']
            if not r['run'].startswith('run-') or not (d / 'admission.json').is_file():
                continue
            admission = json.loads((d / 'admission.json').read_text())
            read = dict(line.split('=', 1) for line in (d / 'attest.read').read_text().splitlines() if '=' in line)
            row = dict(passName=pdir.name, run=r['run'], mode=read['displayplacerMode'],
                       open=when(json.loads((d / 'attest.open.json').read_text())['recordedAt']),
                       close=when(json.loads((d / 'attest.close.json').read_text())['recordedAt']))
            if admission.get('protocol') == 'dump':
                row.update(kind='dump', scenes=admission['scenes'], elapsed=admission['timing']['elapsedSeconds'])
            else:
                row.update(kind='capture', protocol=admission['protocol'], scale=1 if read['displayplacerMode'] == '69' else 2,
                           n=r['fixtures'], first=when(r['firstCapture']), last=when(r['lastCapture']))
            rows.append(row)
    return sorted(rows, key=lambda r: r['open'])


def line_fit(xs, ys):
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    if not sxx:
        return None, None
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    return my - b * mx, b


def measure(attest=W42_G1):
    """The rates, each with the runs it was read off."""
    rows = w42_runs(attest)
    captures = {}
    for protocol in ('normal', 'long'):
        for scale in (1, 2):
            sel = [r for r in rows if r['kind'] == 'capture' and r['protocol'] == protocol and r['scale'] == scale]
            if not sel:
                continue
            walls = [r['close'] - r['open'] for r in sel]
            spans = [r['last'] - r['first'] for r in sel]
            a, b = line_fit([r['n'] for r in sel], walls)
            captures[f'{protocol}-{scale}x'] = dict(
                runs=len(sel), captures=sum(r['n'] for r in sel), cells=sorted({r['n'] for r in sel}),
                overheadSeconds=round(statistics.median(w - s for w, s in zip(walls, spans)), 3),
                intervalSeconds=round(statistics.median((r['last'] - r['first']) / (r['n'] - 1) for r in sel), 4),
                crossCheckFit=None if b is None else dict(perRunSeconds=round(a, 2), perCaptureSeconds=round(b, 4)),
                wallSeconds=round(sum(walls), 1))
    dumps = [r for r in rows if r['kind'] == 'dump']
    a, b = line_fit([r['scenes'] for r in dumps], [r['close'] - r['open'] for r in dumps])
    ea, eb = line_fit([r['scenes'] for r in dumps], [r['elapsed'] for r in dumps])
    within, between, switch, stops = [], [], [], []
    for prev, nxt in zip(rows, rows[1:]):
        gap = nxt['open'] - prev['close']
        tag = dict(after=f'{prev["passName"]}/{prev["run"]}', before=f'{nxt["passName"]}/{nxt["run"]}',
                   seconds=round(gap, 1))
        if gap > STOP_GAP:
            stops.append(tag)
        elif prev['passName'] == nxt['passName']:
            within.append(gap)
        elif prev['mode'] != nxt['mode']:
            switch.append(gap)
        else:
            between.append(gap)
    return dict(
        source=str(Path(attest).relative_to(REPO)) if Path(attest).is_relative_to(REPO) else str(attest),
        admittedRuns=len(rows), captureRates=captures,
        dump=dict(launches=len(dumps), scenes=[r['scenes'] for r in dumps], perLaunchSeconds=round(a, 2),
                  perSceneSeconds=round(b, 4), elapsedFit=dict(perLaunchSeconds=round(ea, 2),
                                                               perSceneSeconds=round(eb, 4))),
        gapWithinPassSeconds=round(statistics.median(within), 2), gapWithinPassCount=len(within),
        gapBetweenPassesSeconds=round(statistics.median(between), 2), gapBetweenPassesCount=len(between),
        modeSwitchSeconds=round(statistics.median(switch), 2), modeSwitches=[round(g, 1) for g in switch],
        excludedStopGaps=stops,
        sliderWriteSeconds=SLIDER_WRITE_SECONDS,
        sliderWriteNote='ASSUMED, not measured: W42 never wrote the slider inside a sitting')


def self_check(rates, attest=W42_G1):
    """The model applied to W42 G1's own admitted runs and boundaries, against their measured
    wall (first open to last close, less the stop gaps). In-sample: it checks the arithmetic and
    how much the medians lose, not a prediction."""
    rows = w42_runs(attest)
    model = 0.0
    for r in rows:
        model += dump_seconds(rates, r['scenes']) if r['kind'] == 'dump' else \
            run_seconds(rates, r['protocol'], r['scale'], r['n'])
    for prev, nxt in zip(rows, rows[1:]):
        if nxt['open'] - prev['close'] > STOP_GAP:
            continue
        model += rates['gapWithinPassSeconds'] if prev['passName'] == nxt['passName'] else (
            rates['modeSwitchSeconds'] if prev['mode'] != nxt['mode'] else rates['gapBetweenPassesSeconds'])
    measured = rows[-1]['close'] - rows[0]['open'] - sum(s['seconds'] for s in rates['excludedStopGaps'])
    return dict(measuredSeconds=round(measured, 1), modelledSeconds=round(model, 1),
                differenceSeconds=round(model - measured, 1))


# --------------------------------------------------------------------- the model

def run_seconds(rates, protocol, scale, cells):
    r = rates['captureRates'][f'{protocol}-{scale}x']
    return r['overheadSeconds'] + r['intervalSeconds'] * (cells - 1)


def dump_seconds(rates, scenes):
    return rates['dump']['perLaunchSeconds'] + rates['dump']['perSceneSeconds'] * scenes


def price(plan, sources, rates):
    """Every pass's cost and every boundary's, from the plan's own membership."""
    P = pass_spec()
    counts = {row['name']: row for row in P.plan_counts(plan, sources)['passes']}
    passes, boundaries = [], []
    prev = None
    for p in P.pass_order(plan):
        row = counts[p['name']]
        if p['kind'] == 'dump':
            secs = dump_seconds(rates, len(p['scenes']))
            passes.append(dict(name=p['name'], kind='dump', glass=p['glass'], mode=p['mode'], scenes=len(p['scenes']),
                               seconds=round(secs, 1), exactSeconds=secs))
        else:
            runs = [run_seconds(rates, p['protocol'], p['scale'], n) for n in row['cellsPerRun']]
            secs = sum(runs) + (len(runs) - 1) * rates['gapWithinPassSeconds']
            passes.append(dict(name=p['name'], kind='capture', glass=p['glass'], mode=p['mode'], runs=len(runs),
                               protocol=p['protocol'], captures=row['captures'], seconds=round(secs, 1),
                               exactSeconds=secs))
        if prev is not None:
            switch = p['mode'] != prev['mode']
            slider = p['glass'] != prev['glass']
            secs = (rates['modeSwitchSeconds'] if switch else rates['gapBetweenPassesSeconds']) \
                + (rates['sliderWriteSeconds'] if slider else 0.0)
            boundaries.append(dict(after=prev['name'], before=p['name'], modeSwitch=switch, sliderWrite=slider,
                                   exactSeconds=secs))
        prev = p
    total = sum(q['exactSeconds'] for q in passes) + sum(b['exactSeconds'] for b in boundaries)
    capture_s = sum(q['exactSeconds'] for q in passes if q['kind'] == 'capture')
    dump_s = sum(q['exactSeconds'] for q in passes if q['kind'] == 'dump')
    return dict(passes=passes, boundaries=boundaries, totals=P.plan_counts(plan, sources)['totals'],
                captureSeconds=round(capture_s, 1), dumpSeconds=round(dump_s, 1),
                boundarySeconds=round(sum(b['exactSeconds'] for b in boundaries), 1),
                totalSeconds=round(total, 1), totalHours=round(total / 3600, 2),
                withStopLossHours=round(total * 1.1 / 3600, 2), exactTotalSeconds=total)


def report(plan, sources, rates, label, rehearsal):
    priced = price(plan, sources, rates)
    check = self_check(rates)
    t = priced['totals']
    c = rates['captureRates']
    lines = [f'W43 {label} sitting length (timing.py; timing-{label}.json has every input)']
    if rehearsal:
        lines += ['REHEARSAL on the G1a-shaped STAND-IN (stand_in.py), not the declared plan: its bridge cells and',
                  'dump scenes are stand_in.py\'s arbitrary picks. The declared plan is priced by --sitting g1a.']
    lines += ['', f'Rates, from W42 G1\'s {rates["admittedRuns"]} admitted runs ({rates["source"]}):']
    for k, r in sorted(c.items()):
        fit = r['crossCheckFit']
        lines.append(f'  {k:10s} overhead {r["overheadSeconds"]:7.2f} s + interval {r["intervalSeconds"]:.4f} s x (n - 1)'
                     f'   [{r["runs"]} runs, n {r["cells"][0]}..{r["cells"][-1]}'
                     + (f'; fit {fit["perRunSeconds"]} + {fit["perCaptureSeconds"]} n' if fit else '; fit unidentified')
                     + ']')
    d = rates['dump']
    lines += [f'  dump       {d["perLaunchSeconds"]} s + {d["perSceneSeconds"]} s x scenes   [{d["launches"]} launches, '
              f'scenes {d["scenes"]}]',
              f'  gaps       {rates["gapWithinPassSeconds"]} s between runs of a pass, {rates["gapBetweenPassesSeconds"]} s '
              f'between passes, {rates["modeSwitchSeconds"]} s across a display switch {rates["modeSwitches"]}',
              f'  slider     {rates["sliderWriteSeconds"]} s a write ({rates["sliderWriteNote"]})',
              f'  excluded   {len(rates["excludedStopGaps"])} stop gap(s) over {STOP_GAP:g} s: '
              + ', '.join(f'{s["after"]} -> {s["before"]} {s["seconds"]} s' for s in rates['excludedStopGaps']),
              f'  self-check the model on W42 G1\'s own runs: {check["modelledSeconds"]} s against a measured '
              f'{check["measuredSeconds"]} s ({check["differenceSeconds"]:+} s; in-sample, the medians\' loss)',
              '', f'Membership ({plan["sitting"]}): {t["captures"]:,} captures in {t["captureLaunches"]} capture launches, '
              f'{t["dumpScenes"]} dump scenes in {t["dumpLaunches"]} dump launches, {t["sliderWrites"]} slider writes, '
              f'{t["modeSwitches"]} display switches; {t["publishedCells"]} cells published', '']
    for q in priced['passes']:
        what = f'{q["scenes"]:5d} scenes' if q['kind'] == 'dump' else f'{q["captures"]:5d} captures ({q["runs"]} runs, {q["protocol"]})'
        lines.append(f'  {q["name"]:32s} x={q["glass"]:<5g} mode {q["mode"]}  {what:32s} {q["seconds"]:9.1f} s')
    lines += ['',
              f'captures   {priced["captureSeconds"]:9.1f} s = {priced["captureSeconds"] / 3600:.2f} h',
              f'dumps      {priced["dumpSeconds"]:9.1f} s = {priced["dumpSeconds"] / 3600:.2f} h',
              f'boundaries {priced["boundarySeconds"]:9.1f} s ({len(priced["boundaries"])}: gaps, display switches, '
              'slider writes)',
              f'TOTAL      {priced["totalSeconds"]:9.1f} s = {priced["totalHours"]:.2f} h; '
              f'{priced["withStopLossHours"]:.2f} h with the charter\'s 10 % stop loss']
    if rehearsal or plan['sitting'] == 'g1a':
        lines += ['', f'Charter G1a model: {CHARTER_G1A["captures"]:,} captures, {CHARTER_G1A["modelledHours"]} h modelled, '
                  f'about {CHARTER_G1A["atMacHours"]} h at the Mac ({CHARTER_G1A["source"]}). This plan: '
                  f'{t["captures"]:,} captures, {priced["totalHours"]:.2f} h '
                  f'({priced["totalHours"] - CHARTER_G1A["modelledHours"]:+.2f} h).']
    lines += ['Excluded: idle waits beyond the measured gaps, quarantines, stops and their continuations, the',
              'orchestrator\'s start and restore, and any grant swap.']
    value = dict(schema='w43-sitting-timing-1', sitting=plan['sitting'], label=label, rehearsal=rehearsal,
                 rates=rates, selfCheck=check, priced={k: v for k, v in priced.items() if k != 'exactTotalSeconds'},
                 charterG1a=CHARTER_G1A if (rehearsal or plan['sitting'] == 'g1a') else None)
    return value, '\n'.join(lines) + '\n'


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    which = ap.add_mutually_exclusive_group(required=True)
    which.add_argument('--sitting', choices=('g1a', 'g1b'))
    which.add_argument('--stand-in', action='store_true')
    args = ap.parse_args(argv)
    P = pass_spec()
    if args.stand_in:
        S = module('w43_stand_in_timing', HERE / 'stand_in.py')
        canonical, w42, plan = S.build()
        sources = S.sources_of(plan, canonical, w42)
        P.validate_plan(plan, sources)
        label = 'stand-in'
    else:
        plan, sources = P.load(P.plan_path(args.sitting))
        label = args.sitting
    value, text = report(plan, sources, measure(), label, args.stand_in)
    (HERE / f'timing-{label}.json').write_text(json.dumps(value, indent=1) + '\n')
    (HERE / f'timing-{label}.txt').write_text(text)
    print(text, end='')


if __name__ == '__main__':
    main()
