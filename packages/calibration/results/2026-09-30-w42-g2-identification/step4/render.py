#!/usr/bin/env python3.12
"""W42 G2 step 4: every browser launch of the landing read, and nothing else.

    render.py base-proof                     clause 8: the 40-cell runtime-base sample, shipped documents
    render.py bed <set> [<pass> ...]         the W42 bed's web-plannable cal/val cells (step 3, clause 7)
    render.py canon <set> [<profile> ...]    the canonical bed through `compare` into scratch (clause 10)

<set> is `shipped` or a set of documents/documents.json (c1, c2, c1ref). Every launch is logged in
runs.jsonl beside this file (argv, environment overrides, X6's facts, exit, times); its console goes
to SCRATCH/logs. Outputs are scratch only (SCRATCH, default /tmp/w42-g2-step4): no file under
profiles/, results/generations/, results/matrix.json or any canonical capture tree is written, and
the main checkout's canonical tree is only read.

A launch waits while SCRATCH/PAUSE exists (the parent's pause between renders), and never starts a
job whose output already exists. Two capture processes run at once, each on its own scene-server
port. Reduce Transparency and Increase Contrast must read 0 and the glass slider 0.5 before each
launch (X6's three settings facts); the foreign-process census and idle time are recorded, not
enforced, because these renders are byte-deterministic web captures and every one is checked over
two loads by capture-web itself.
"""
import concurrent.futures
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
REPO = CAL.parents[1]
SCRATCH = Path(os.environ.get('W42_STEP4_SCRATCH', '/tmp/w42-g2-step4'))
CANONICAL_TREE = Path('/Users/new/Developer/GitHub/designer/packages/calibration/web-captures')
DECL = CAL / 'results/2026-09-29-w42-g0-declaration'
BED = DECL / 'bed'
FIXTURES = SCRATCH / 'fixtures'
SIDE_BACKGROUNDS = Path('/Users/new/vitrea-w42/g0-bed-scratch/side-check-v5/fixtures/backgrounds')
LOCK = threading.Lock()

_spec = importlib.util.spec_from_file_location(
    'w41_x6', CAL / 'results/2026-09-27-w41-g1-identification/x6/observe.py')
x6 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(x6)

SHIPPED = {s: (f'packages/calibration/profiles/apple-macos-27.0-1x-{s}-standard-glass0.5.json',
               f'packages/calibration/profiles/apple-macos-27.0-1x-{s}-standard-glass0.5-receded.json')
           for s in ('light', 'dark')}


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def documents(name):
    """{scheme: (active, receded)} repo-relative paths for a document set."""
    if name == 'shipped':
        return dict(SHIPPED)
    sets = json.loads((HERE / 'documents/documents.json').read_text())['sets']
    s = sets[name]
    return {'light': (s['light']['path'], s['lightReceded']['path']),
            'dark': (s['dark']['path'], s['darkReceded']['path'])}


def log(row):
    with LOCK, (HERE / 'runs.jsonl').open('a') as f:
        f.write(json.dumps(row, sort_keys=True) + '\n')


def wait_unpaused(label):
    said = False
    while (SCRATCH / 'PAUSE').exists():
        if not said:
            print(f'PAUSED before {label}', flush=True)
            said = True
        time.sleep(10)


def gate(label):
    observation = x6.observe()
    v = observation['verdict']
    facts = v['facts']
    enforced = {k: facts[k] for k in ('reduceTransparency', 'increaseContrast', 'NSGlassTintAmount')}
    log(dict(label=label, at=observation['recordedAt'], x6=v, enforced=enforced,
             foreign=len(observation['foreignProcesses'])))
    if not all(enforced.values()):
        raise SystemExit(f'X6 settings refused before {label}: {enforced}')


def launch(label, argv, env_extra, port, cwd=CAL):
    wait_unpaused(label)
    gate(label)
    env = {k: v for k, v in os.environ.items() if not k.startswith('VITREA_')}
    env.update(env_extra)
    env['VITREA_SCENE_SERVER_PORT'] = str(port)
    (SCRATCH / 'logs').mkdir(parents=True, exist_ok=True)
    started = now()
    with (SCRATCH / 'logs' / (label.replace('/', '__') + '.txt')).open('w') as out:
        result = subprocess.run(argv, cwd=cwd, env=env, stdout=out, stderr=subprocess.STDOUT)
    log(dict(label=label, started=started, completed=now(), exitCode=result.returncode, argv=argv,
             env={k: v for k, v in env_extra.items()}, port=port))
    print(label, 'exit', result.returncode, flush=True)
    return result.returncode


def capture(label, scenes, scheme, scale, active, receded, out, env_extra, port):
    argv = ['pnpm', 'exec', 'tsx', 'scripts/capture-web.ts', *scenes, '--renderer', 'webgpu',
            '--color-scheme', scheme, '--scale', str(scale), '--material-profile', str(REPO / active),
            '--receded-profile', str(REPO / receded), '--out', str(out)]
    return launch(label, argv, env_extra, port)


def run_jobs(jobs, workers=2):
    ports = iter(range(5301, 5399))
    with concurrent.futures.ThreadPoolExecutor(workers) as pool:
        futures = [pool.submit(job, port) for job, port in zip(jobs, ports)]
        codes = [f.result() for f in futures]
    return codes


# ----------------------------------------------------------------------------------- clause 8

def base_proof():
    sample = json.loads((BED / 'runtime-base-sample.json').read_text())
    out_root = SCRATCH / 'runtime-base'
    by_profile = {}
    for c in sample['cells']:
        by_profile.setdefault(c['profile'], []).append(c)
    jobs = []
    for profile, cells in sorted(by_profile.items()):
        scheme = 'dark' if '-dark-' in profile else 'light'
        scale = 2 if '-2x-' in profile else 1
        out = out_root / profile
        if out.exists():
            continue
        a, r = SHIPPED[scheme]
        jobs.append(lambda port, p=profile, cs=cells, s=scheme, k=scale, o=out, a=a, r=r:
                    capture(f'base-proof/{p}', [c['scene'] for c in cs], s, k, a, r, o, {}, port))
    run_jobs(jobs)
    rows = []
    for c in sample['cells']:
        mine = out_root / c['profile'] / c['scene'] / f"{c['scene']}__webgpu.png"
        canonical = CANONICAL_TREE / c['png']
        cell = json.loads((mine.parent / 'cell__webgpu.json').read_text())
        rows.append(dict(profile=c['profile'], scene=c['scene'], kind=c['kind'], pose=c['pose'],
                         mine=sha(mine), canonical=sha(canonical), sha256AtG0=c['sha256AtG0'],
                         identical=sha(mine) == sha(canonical), renderer=cell['renderer'],
                         adapter=cell['gpuAdapter'], engine=cell['engineVersion'],
                         deterministic=cell['deterministic']))
    head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=REPO, capture_output=True, text=True).stdout.strip()
    value = dict(clause='charter clause 8; X37 (bed/runtime-base-sample.json, 40 WebGPU cells), repeated at '
                        'the merged implementation (w42-g2-impl b92bfb1f merged as d012ac6a)',
                 base=f'w42-g2-identification at {head} (the shipped documents; every W42 leaf at its identity)',
                 tree=str(CANONICAL_TREE) + ' (read only)',
                 checkCaptureTree=(SCRATCH / 'check-capture-tree.txt').read_text().strip().splitlines()[-2:],
                 identical=sum(r['identical'] for r in rows), cells=len(rows),
                 engines=sorted({r['engine'] for r in rows}), adapters=sorted({r['adapter'] for r in rows}),
                 renderers=sorted({r['renderer'] for r in rows}),
                 deterministic=all(r['deterministic'] for r in rows),
                 verdict='byte-identical' if all(r['identical'] for r in rows) else 'DIFFERS', rows=rows)
    (HERE / 'runtime-base.json').write_text(json.dumps(value, indent=1) + '\n')
    print(value['verdict'], value['identical'], '/', value['cells'])


# ----------------------------------------------------------------------------------- the W42 bed

def fixtures():
    """The scratch fixture root the page serves the W42 backgrounds from: the side bundle's own
    `backgrounds` output (G0 side-check-v5), each raster checked against the committed
    backgrounds-verification.json before it is copied, with a manifest in the canonical schema."""
    if (FIXTURES / 'manifest.json').exists():
        return
    rows = json.loads((BED / 'side-check/backgrounds-verification.json').read_text())
    assert rows['scenesSha256'] == sha(BED / 'scenes-w42-body.json')
    (FIXTURES / 'backgrounds').mkdir(parents=True)
    manifest = {}
    for r in rows['rows']:
        src = SIDE_BACKGROUNDS / r['png']
        raw = src.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == r['sha256'], r['png']
        (FIXTURES / 'backgrounds' / r['png']).write_bytes(raw)
        manifest[f"{r['background']}@{r['scale']}x"] = f"backgrounds/{r['png']}"
    (FIXTURES / 'manifest.json').write_text(json.dumps(dict(
        schemaVersion=2, backgrounds=manifest,
        provenance='W42 G2 step 4 scratch: the side bundle backgrounds of bed/side-check, checked against '
                   'backgrounds-verification.json'), indent=1, sort_keys=True) + '\n')


PASSES = ('2x-light-active', '2x-light-receded', '2x-dark-receded',
          '1x-light-active', '1x-light-receded', '1x-dark-receded')


def bed_scenes(pass_key, families=None):
    plan = json.loads((BED / 'web-plan.json').read_text())
    p = plan['passes'][pass_key]
    return p['profile'], sorted(r['scene'] for r in p['cells'].values()
                                if r['role'] in ('calibration', 'validation') and r['plannable']
                                and (families is None or r['family'] in families))


def bed(name, passes, families=None):
    fixtures()
    docs = documents(name)
    env = dict(VITREA_SCENES=str(BED / 'scenes-w42-body.json'), VITREA_FIXTURES=str(FIXTURES))
    jobs = []
    for pk in passes or PASSES:
        profile, scenes = bed_scenes(pk, families)
        scale, scheme = int(pk[0]), pk.split('-')[1]
        out = SCRATCH / 'bed' / name / pk
        if out.exists():
            continue
        a, r = docs[scheme]
        jobs.append(lambda port, pk=pk, sc=scenes, s=scheme, k=scale, o=out, a=a, r=r:
                    capture(f'bed/{name}/{pk}', sc, s, k, a, r, o, env, port))
    return run_jobs(jobs)


# ----------------------------------------------------------------------------------- the canonical bed

CANON_PROFILES = ('apple-macos-27.0-1x-light-standard-glass0.5', 'apple-macos-27.0-2x-light-standard-glass0.5',
                  'apple-macos-27.0-1x-light-reduced-transparency-glass0.5',
                  'apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5',
                  'apple-macos-27.0-1x-dark-standard-glass0.5', 'apple-macos-27.0-2x-dark-standard-glass0.5')


def canon_membership(profile):
    """The current generation's non-holdout WebGPU membership of a profile: what a stage replaces."""
    index = json.loads((CAL / 'results/generations/index.json').read_text())
    cells = json.loads((CAL / 'results/generations' / index['currentByProfile'][profile]).read_text())['cells']
    rows = [c for c in cells if c['key']['profileKey'] == profile and c['key']['web']['renderer'] == 'webgpu']
    return sorted((c['fixtureSet'], c['key']['sceneId']) for c in rows)


def canon(name, profiles):
    docs = documents(name)
    jobs = []
    for profile in profiles or CANON_PROFILES:
        members = [m for m in canon_membership(profile) if m[0] != 'holdout']
        scheme = 'dark' if '-dark-' in profile else 'light'
        out = SCRATCH / 'canon' / name
        matrix = out / 'matrices' / f'{profile}.json'
        if matrix.exists():
            continue
        matrix.parent.mkdir(parents=True, exist_ok=True)
        a, r = docs[scheme]
        sets = sorted({m[0] for m in members})
        argv = ['pnpm', 'run', '-s', 'compare', '--', '--profile', profile, '--renderer', 'webgpu',
                '--set', ','.join(sets), '--scene', ','.join(m[1] for m in members),
                '--material-profile', str(REPO / a), '--receded-profile', str(REPO / r),
                '--alpha', '--write-partial', '--out-matrix', str(matrix)]
        env = dict(VITREA_WEB_CAPTURES=str(out / 'captures'))
        jobs.append(lambda port, p=profile, argv=argv, env=env: launch(f'canon/{name}/{p}', argv, env, port))
    return run_jobs(jobs)


# ----------------------------------------------------------------------------------- the sheets' looks

TEXT_UNROWED = ('hc-text__rrect-sm__rest', 'hc-text__rrect-lg__rest', 'hc-text__rrect-sm__inactive')
GRADIENT = ('v270-c-c44__inactive', 'v270-c-c44__rest', 'v90-c-c44__inactive', 'v90-c-c44__rest')
W39_FIXTURES = Path('/Users/new/vitrea-w41/g1/packages/calibration/results/2026-09-27-w41-g1-identification/'
                    'baseline/generated-backdrops')


def looks(name):
    """What the eye sheets read that no stage row holds (gate/sheets/README.txt): the three probe
    hc-text scenes with no current row, and the W39 bed's 16 web-plannable gradient cells, at the
    set's documents on this base (`shipped` re-renders the sheets' shipped column here)."""
    docs = documents(name)
    jobs = []
    for profile in CANON_PROFILES[:2] + CANON_PROFILES[4:]:
        scheme = 'dark' if '-dark-' in profile else 'light'
        scale = 2 if '-2x-' in profile else 1
        a, r = docs[scheme]
        for kind, scenes, env in (
                ('text', TEXT_UNROWED, {}),
                ('gradient', GRADIENT, dict(VITREA_SCENES=str(REPO / 'apps/reference-apple/scenes-w39-colour-edge.json'),
                                            VITREA_FIXTURES=str(W39_FIXTURES)))):
            out = SCRATCH / 'looks' / name / kind / profile
            if out.exists():
                continue
            jobs.append(lambda port, k=kind, p=profile, sc=scenes, s=scheme, sk=scale, o=out, a=a, r=r, e=env:
                        capture(f'looks/{name}/{k}/{p}', list(sc), s, sk, a, r, o, e, port))
    return run_jobs(jobs)


def main():
    SCRATCH.mkdir(parents=True, exist_ok=True)
    mode = sys.argv[1]
    if mode == 'looks':
        print(looks(sys.argv[2]))
        return
    if mode == 'base-proof':
        base_proof()
    elif mode == 'bed':
        args = sys.argv[3:]
        families = None
        if args and args[0].startswith('--families='):
            families = set(args[0].split('=', 1)[1].split(','))
            args = args[1:]
        print(bed(sys.argv[2], args, families))
    elif mode == 'canon':
        print(canon(sys.argv[2], sys.argv[3:]))
    else:
        raise SystemExit(__doc__)


if __name__ == '__main__':
    main()
