#!/usr/bin/env python3.12
"""W43 G0 (b): the bridge on existing evidence (charter clause 3; Design, "The bridges"; X43).

    python3.12 -B bridge.py <w42 archive root> --out <dir> [--deny <path> ...]

Every W43 pixel comes through the W39 side bundle, and the canonical 0.5 bed came through the
original bundle (2026-09-18/19). This reads the one piece of existing evidence that ties them:
W42's family F, four cells captured through the side bundle at slider 0.5 on 2026-09-30, seven
runs each, which W42 declared as bridges to their canonical twins and never read (§5.196 §1).

Inputs, and nothing else:
- `w42-archive` (asset `1e3d6e65…`, inventory `5481795e…`), opened through W42's guarded Reader
  with the `probe` role ONLY. H is never requested, and the raw run root is denied.
- The committed canonical fixtures `apps/reference-apple/fixtures/apple-macos-27.0-*-standard-
  glass0.5/<twin>.png`, where `<twin>` is the bed's `bridge` field plus the pose. Every twin is
  a calibration, validation or probe scene of the canonical split; none is holdout or recorded
  (W42's twin audit, re-checked here against `scenes.json`).

The metric is the charter's: byte identity, or region medians within max(1 code, bar), cell by
cell. Per cell-pass:
1. **Bytes.** The fixture file's SHA-256 against every admitted run's frame SHA-256 (the archive
   keeps the harness's own PNG bytes), and the decoded RGB against every distinct state.
2. **Region medians.** W42's instrument, unchanged: `forward.Cell` on the bed's geometry (an
   active cell at both of ruling 3's masks, `n` and `w`; a receded cell at its one mask) and
   `regions.statistics`, the per-channel medians over the deep-mask populations clause 6 gated
   on. The fixture is read with the same populations as the runs. The bar per statistic and
   channel is W39's, 0.5 + half the largest pairwise separation of the seven run medians,
   recomputed here from the runs and checked equal to G1's published `bar.json.gz`. A statistic
   AGREES when |fixture − plurality run| <= max(1, bar). The parent's later ruling reads every run, so
   `runByRun` also judges each distinct state the runs produced against the fixture the same way.
3. **The verdict, run by run** (the parent's ruling; the review of 4cd1cdc4). AGREE (bytes) when
   every admitted run's state is the fixture's pixels; AGREE (regions) when every run agrees, by
   bytes or by every region statistic; DISAGREE otherwise; NO TWIN when the canonical bed has no
   such scene for the profile. A cell with no region statistic whose runs are not all byte-identical
   is UNMEASURED, never an agreement.

Descriptive, never a verdict: the differing-pixel count and the largest code difference against
the plurality state, and the fixture's position inside the runs' own range. With `--w29-runs`,
also the original bundle's own seven W29 runs of each twin (`~/vitrea-w29-27-run/standard-
{active,inactive}-{1x,2x}/run-N/<profile>/<twin>.png`, the raw tree the canonical fixtures were
plurality-published from; on the capture machine, never committed): their state counts by file
SHA-256, and whether every side-bundle state is one of them.
"""
import argparse
import collections
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
W42 = REPO / 'packages/calibration/results/2026-09-29-w42-g0-declaration'
SITTING = W42 / 'bed/sitting'
G1BAR = REPO / 'packages/calibration/results/2026-09-30-w42-g1-sitting/bar/bar.json.gz'
FIXTURES = REPO / 'apps/reference-apple/fixtures'
SCENES = REPO / 'apps/reference-apple/scenes.json'
sys.path.insert(0, str(W42 / 'instrument'))
import bed as IB  # noqa: E402,F401  W42's instrument, unchanged: loads the pinned bed's backgrounds
import forward as F  # noqa: E402
import regions as R  # noqa: E402

SCHEMA = 'w43-bridge-existing-1'
ARCHIVE = dict(asset='w42-archive-1e3d6e65fa3b9a621f1d0f80fb03cc79ee76c29d9b001174983689a7aed31014.tar.zst',
               sha256='1e3d6e65fa3b9a621f1d0f80fb03cc79ee76c29d9b001174983689a7aed31014',
               inventorySha256='5481795e0a77ef246f6743d2b6bbe2111a79d858ff9b7a2a4571255595940ed7',
               g1BarJsonSha256='a85662f2eacba16613c6470407a5f0d7469569d4a4918f1ab0047ae0c6b8ccf0')


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def decode(raw):
    with Image.open(io.BytesIO(raw)) as image:
        return np.asarray(image.convert('RGB'), dtype=np.int16)


def endpoint(profile, sid):
    return (1 if '-1x-' in profile else 2, 'dark' if '-dark-' in profile else 'light',
            'rest' if sid.endswith('__rest') else 'inactive')


def canonical_roles():
    spec = json.loads(SCENES.read_text())
    roles = {s: r for r, ids in spec['split'].items() if not r.startswith('$') for s in ids}
    members = {p['key']: set(p['scenes']) for p in spec['profiles']}
    return roles, members


def g1_bars():
    raw = gzip.decompress(G1BAR.read_bytes())
    if sha(raw) != ARCHIVE['g1BarJsonSha256']:
        raise ValueError("G1's bar.json is not the published one")
    out = {}
    for row in json.loads(raw)['rows']:
        if row.get('status') == 'measured' and row.get('protocol') == 'normal':
            out[(row['cell'], row['kernel'])] = {k: v['bar'] for k, v in row['statistics'].items()}
    return out


def w29_states(w29, profile, twin, scale, pose):
    """The original bundle's W29 run states of one twin, by file SHA-256 (descriptive)."""
    if w29 is None:
        return None
    base = w29 / f"standard-{'active' if pose == 'rest' else 'inactive'}-{scale}x"
    paths = sorted(base.glob(f'run-*/{profile}/{twin}.png'))
    return dict(runs=len(paths), states=dict(collections.Counter(sha(p.read_bytes())[:12] for p in paths).most_common()))


def bridge_cell(wave, reader, archive, cell, roles, members, published, w29=None):
    profile, sid = cell.split('/', 1)
    cid, pose_tag = sid.rsplit('__', 1)
    bed_cell = wave.bed['cells'][cid]
    scale, scheme, pose = endpoint(profile, sid)
    twin = f"{bed_cell['bridge']}__{pose_tag}"
    row = dict(cell=cell, twin=twin, scale=scale, scheme=scheme, pose=pose)
    if twin not in members[profile]:
        return dict(row, verdict='NO TWIN', reason=f'the canonical bed has no {twin} in {profile}')
    if roles.get(twin) not in ('calibration', 'validation', 'probe'):
        raise PermissionError(f'{twin} is {roles.get(twin)!r} in the canonical split: not readable here')
    path = FIXTURES / profile / f'{twin}.png'
    fixture_raw = path.read_bytes()
    fixture = decode(fixture_raw)
    header, blobs = archive.unbundle(reader.read(cell, 'states'))
    runs = [r for r in header['runs'] if r['protocol'] == 'normal']
    counts = collections.Counter(r['frame'] for r in runs)
    plurality = counts.most_common(1)[0][0]
    states = {k: decode(blobs[k]) for k in counts}
    row.update(twinRole=roles[twin], fixture=str(path.relative_to(REPO)), fixtureSha256=sha(fixture_raw),
               runs=len(runs), states={k[:12]: n for k, n in counts.most_common()}, plurality=plurality[:12],
               shape=list(fixture.shape))
    if any(s.shape != fixture.shape for s in states.values()):
        return dict(row, verdict='DISAGREE', reason='frame dimensions differ')
    file_equal = [k[:12] for k in counts if k == row['fixtureSha256']]
    pixel_equal = [k[:12] for k, img in states.items() if np.array_equal(img, fixture)]
    diff = np.abs(states[plurality] - fixture)
    original = w29_states(w29, profile, twin, scale, pose)
    if original is not None:
        original['everySideStateSeen'] = all(k[:12] in original['states'] for k in counts)
        original['fixtureIsAState'] = row['fixtureSha256'][:12] in original['states']
        row['w29Original'] = original
    row.update(fileIdentical=file_equal, pixelIdentical=pixel_equal,
               againstPlurality=dict(pixelsDiffering=int((diff.max(-1) > 0).sum()), maxCodes=int(diff.max())))
    kernels = ('n', 'w') if pose == 'rest' else ('n',)
    readings, worst, failing, measured = [], 0.0, [], 0
    state_fail = {k: [] for k in states}      # run by run (the parent's ruling): each state against the fixture
    for kernel in kernels:
        c = F.Cell(f'{scale}x|{cid}', wave.scenes[sid]['background'], wave.scenes[sid]['component'], scale, scheme,
                   pose, rgb=True, kernel=kernel)
        if c.mask.sum() == 0:
            readings.append(dict(kernel=kernel, status='empty deep mask'))
            continue
        pops = R.populations(c)
        if not pops:
            readings.append(dict(kernel=kernel, status=f'no region statistic: every population under {R.MIN_PX} px'))
            continue
        per_state = {k: R.statistics(c, img.astype(np.float64), pops) for k, img in states.items()}
        fixed = R.statistics(c, fixture.astype(np.float64), pops)
        mine, theirs = {}, published.get((cell, kernel))
        rows = []
        for name in sorted(fixed):
            values = np.array([per_state[r['frame']][name] for r in runs], float)
            bar = 0.5 + 0.5 * float(values.max() - values.min())
            mine[name] = round(bar, 6)
            tol = max(1.0, bar)
            d = float(fixed[name] - per_state[plurality][name])
            inside = bool(values.min() - 1e-9 <= fixed[name] <= values.max() + 1e-9)
            rows.append(dict(statistic=name, fixture=float(fixed[name]), plurality=float(per_state[plurality][name]),
                             delta=d, bar=round(bar, 6), tolerance=tol, agrees=abs(d) <= tol + 1e-9,
                             insideRunRange=inside))
            worst = max(worst, abs(d))
            if abs(d) > tol + 1e-9:
                failing.append(f'{kernel}:{name} {d:+.1f}')
            for k in states:
                dk = float(fixed[name] - per_state[k][name])
                if abs(dk) > tol + 1e-9:
                    state_fail[k].append(f'{kernel}:{name} {dk:+.1f}')
        measured += len(rows)
        if theirs is not None and theirs != mine:
            raise ValueError(f"{cell} {kernel}: the recomputed bars differ from G1's published bar.json")
        readings.append(dict(kernel=kernel, status='measured', statistics=len(rows),
                             barEqualsG1=theirs is not None, rows=rows))
    row.update(regions=readings, regionStatistics=measured, worstAbsDelta=round(worst, 3), failing=failing)
    by_state = {k[:12]: ('bytes' if k[:12] in pixel_equal else 'regions' if measured and not state_fail[k] else
                         'UNMEASURED' if not measured else 'DISAGREE') for k in states}
    row.update(runByRun=dict(byState=by_state, failingByState={k[:12]: v[:8] for k, v in state_fail.items() if v},
                             everyRunAgrees=all(by_state[r['frame'][:12]] in ('bytes', 'regions') for r in runs)))
    # The parent's ruling: the verdict reads every run. Bytes only when every run's state is the fixture's
    # pixels; regions when every run agrees, some by region statistics; never from the plurality alone.
    states_of_runs = {r['frame'][:12] for r in runs}
    if all(by_state[k] == 'bytes' for k in states_of_runs):
        verdict = 'AGREE (bytes)'
    elif row['runByRun']['everyRunAgrees']:
        verdict = 'AGREE (regions)'
    elif measured == 0:
        verdict = 'UNMEASURED'
    else:
        verdict = 'DISAGREE'
    return dict(row, verdict=verdict)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('archive', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--deny', type=Path, action='append', default=[])
    ap.add_argument('--w29-runs', type=Path, default=None)
    args = ap.parse_args(argv)
    archive = module('w42_archive_for_w43_bridge', SITTING / 'w42_archive.py')
    published = g1_bars()   # read before the denials take effect, from the repository
    for path in args.deny:
        archive.deny(path)
    wave = archive.wave_module().default_wave()
    tree = archive.verify_tree(args.archive)
    if tree['inventorySha256'] != ARCHIVE['inventorySha256']:
        raise ValueError('the archive root is not w42-archive')
    reader = wave.reader(args.archive, roles=('probe',))   # never 'holdout': no receipt is ever made
    roles, members = canonical_roles()
    cells = sorted({r['cell'] for r in reader.report_inventory() if r['kind'] == 'states'
                    and r['cell'].split('/', 1)[1] in reader.allowed
                    and wave.bed['cells'].get(r['cell'].split('/', 1)[1].rsplit('__', 1)[0], {}).get('family') == 'F'})
    rows = [bridge_cell(wave, reader, archive, cell, roles, members, published, args.w29_runs) for cell in cells]
    verdicts = collections.Counter(r['verdict'] for r in rows)
    value = dict(schema=SCHEMA, archive=ARCHIVE, archiveGeneration=reader.generation, roles=['probe'],
                 deniedPaths=[str(p) for p in args.deny], w29Runs=str(args.w29_runs) if args.w29_runs else None,
                 tool=sha(Path(__file__).read_bytes()),
                 instrument={n: sha((W42 / 'instrument' / n).read_bytes()) for n in ('regions.py', 'forward.py',
                                                                                    'geometry.py', 'bed.py')},
                 scenesSha256=sha(SCENES.read_bytes()), cellPasses=len(rows), verdicts=dict(verdicts), rows=rows)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / 'bridge.json').write_text(json.dumps(value, indent=1, sort_keys=True) + '\n')
    lines = [f'W43 G0 (b): the bridge on existing evidence; {len(rows)} family F cell-passes of w42-archive '
             f'(inventory {reader.generation[:12]}), probe role only', '']
    for r in rows:
        head = f"{r['verdict']:16s} {r['cell']}  ->  {r['twin']}"
        if r['verdict'] == 'NO TWIN':
            lines.append(f'{head}  ({r["reason"]})')
            continue
        lines.append(f"{head}  [{r['twinRole']}]")
        lines.append(f"    runs {r['runs']}, states {r['states']}, plurality {r['plurality']}; fixture "
                     f"{r['fixtureSha256'][:12]}; file-identical to {r['fileIdentical'] or 'none'}, pixel-identical "
                     f"to {r['pixelIdentical'] or 'none'}; against the plurality {r['againstPlurality']['pixelsDiffering']} "
                     f"px differ, at most {r['againstPlurality']['maxCodes']} codes")
        if r.get('w29Original'):
            o = r['w29Original']
            lines.append(f"    W29 original-bundle runs: {o['runs']}, states {o['states']}; every side state among them: "
                         f"{o['everySideStateSeen']}; fixture is one of them: {o['fixtureIsAState']}")
        for g in r['regions']:
            if g['status'] != 'measured':
                lines.append(f"    mask {g['kernel']}: {g['status']}")
                continue
            ds = [abs(x['delta']) for x in g['rows']]
            bars = sorted({x['bar'] for x in g['rows']})
            lines.append(f"    mask {g['kernel']}: {g['statistics']} region statistics, bar {bars} "
                         f"(= G1's: {g['barEqualsG1']}), |fixture - plurality| max {max(ds):.1f}, "
                         f"{sum(d > 0 for d in ds)} nonzero, {sum(not x['insideRunRange'] for x in g['rows'])} "
                         f"outside the runs' range")
        if r.get('failing'):
            lines.append(f"    failing: {r['failing'][:12]}")
    lines += ['', 'verdicts: ' + json.dumps(dict(verdicts), sort_keys=True)]
    (args.out / 'bridge.txt').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
