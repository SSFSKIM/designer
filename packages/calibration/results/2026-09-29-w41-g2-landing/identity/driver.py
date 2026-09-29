"""W41 G2 step 1 (c9a §5.193): the SHIPPED documents render G1's frozen predictions.

Charter G2: "No rendered prediction moves between G1's freeze and G2's seal". This renders
the same 600 W39 web cells G1 froze (536 calibration/validation and 64 blind held-out) with
the same producer (scripts/capture-web.ts), scenes, generated public backdrops, renderer and
flags, changing exactly one input: the four material documents are the sealed files under
packages/calibration/profiles/ instead of G1's scratch copies. Every PNG must equal G1's frozen
PNG byte for byte; the projection is a pure function of the PNG (baseline.project), so PNG
equality is projection equality. A single moved PNG is a STOP (the law returns to
identification); nothing here retries, retunes or re-seals.

Only web pixels are produced. No native payload, receipt, matrix or canonical tree is touched.
Each browser process gets its own fresh X6 four-fact observation immediately before launch;
a refusal launches nothing and is recorded.

  python3.12 -B driver.py plan      # no browser: writes plan.json from G1's process records
  python3.12 -B driver.py capture   # one Chromium per batch, X6 before each
  python3.12 -B driver.py compare   # no browser: byte comparison, writes comparison.json
"""
import datetime
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
ROOT = CAL.parents[1]
G1 = CAL / 'results/2026-09-27-w41-g1-identification'
ATTEMPT = G1 / 'candidate-capture/attempt-1'
OUT = Path('/Users/new/vitrea-w41/g2-captures/identity')
PROFILES = CAL / 'profiles'
DOCS = {
    'light': ('apple-macos-27.0-1x-light-standard-glass0.5.json',
              'apple-macos-27.0-1x-light-standard-glass0.5-receded.json'),
    'dark': ('apple-macos-27.0-1x-dark-standard-glass0.5.json',
             'apple-macos-27.0-1x-dark-standard-glass0.5-receded.json'),
}

spec = importlib.util.spec_from_file_location('w41_x6', G1 / 'x6/observe.py')
x6 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(x6)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def write_once(path, obj):
    with Path(path).open('x') as stream:
        json.dump(obj, stream, indent=1, sort_keys=True)
        stream.write('\n')


def plan():
    batches = []
    for process in sorted((ATTEMPT / 'processes').iterdir()):
        started = json.loads((process / 'started.json').read_text())
        argv = started['argv']
        i = argv.index('scripts/capture-web.ts')
        flags = argv.index('--renderer')
        scenes = argv[i + 1:flags]
        opts = dict(zip(argv[flags::2], argv[flags + 1::2]))
        phase, profile = process.name.split('-', 1)
        scheme = opts['--color-scheme']
        active, receded = DOCS[scheme]
        batches.append(dict(name=process.name, phase=phase, profile=profile, scenes=scenes,
                            renderer=opts['--renderer'], scheme=scheme, scale=opts['--scale'],
                            g1Documents=[opts['--material-profile'], opts['--receded-profile']],
                            documents=['packages/calibration/profiles/' + active,
                                       'packages/calibration/profiles/' + receded],
                            g1Environment=started['environment']))
    rendered = json.loads((ATTEMPT / 'rendered.json').read_text())['cells']
    cells = sorted(b['profile'] + '/' + s for b in batches for s in b['scenes'])
    if cells != sorted(rendered) or len(cells) != 600:
        raise ValueError('G1 process records do not cover the 600 frozen cells')
    docs = {rel: sha(ROOT / rel) for b in batches for rel in b['documents']}
    write_once(HERE / 'plan.json', dict(
        claims='c9a §5.193', batches=batches, cells=len(cells),
        frozen=dict(rendered=str((ATTEMPT / 'rendered.json').relative_to(ROOT)),
                    renderedSha256=sha(ATTEMPT / 'rendered.json'),
                    frozenSha256=sha(ATTEMPT / 'frozen.json')),
        shippedDocuments=docs,
        change='only the four documents: sealed profiles/ files instead of G1 scratch copies'))
    print(json.dumps(dict(batches=len(batches), cells=len(cells), documents=docs), indent=1))


def capture():
    record = json.loads((HERE / 'plan.json').read_text())
    for rel, digest in record['shippedDocuments'].items():
        if sha(ROOT / rel) != digest:
            raise ValueError('document moved since plan: ' + rel)
    runs = HERE / 'runs'
    runs.mkdir(exist_ok=True)
    for batch in record['batches']:
        done = runs / (batch['name'] + '.complete.json')
        if done.exists():
            continue
        if (runs / (batch['name'] + '.started.json')).exists():
            raise RuntimeError('a started batch without completion is a STOP: ' + batch['name'])
        observation = x6.observe()
        tag = now().replace(':', '').replace('+', 'Z')
        write_once(runs / f"{batch['name']}.x6-{tag}.json", observation)
        if not observation['verdict']['passes']:
            print('X6 REFUSED', batch['name'], observation['verdict']['refusals'], flush=True)
            return 3
        out = OUT / batch['phase'] / batch['profile']
        argv = ['pnpm', '--dir', str(CAL), 'exec', 'tsx', 'scripts/capture-web.ts',
                *batch['scenes'], '--renderer', batch['renderer'],
                '--color-scheme', batch['scheme'], '--scale', batch['scale'], '--out', str(out),
                '--material-profile', str(ROOT / batch['documents'][0]),
                '--receded-profile', str(ROOT / batch['documents'][1])]
        env = {k: v for k, v in os.environ.items() if not k.startswith('VITREA_')}
        g1env = batch['g1Environment']
        env.update(VITREA_ALLOW_FALLBACK_ADAPTER='0',
                   VITREA_FIXTURES=str(G1 / 'baseline/generated-backdrops'),
                   VITREA_SCENES=str(ROOT / 'apps/reference-apple/scenes-w39-colour-edge.json'),
                   VITREA_WEB_CAPTURES=str(OUT / batch['phase']))
        if Path(g1env['VITREA_FIXTURES']).name != 'generated-backdrops':
            raise ValueError('unexpected G1 fixture root')
        write_once(runs / (batch['name'] + '.started.json'),
                   dict(at=now(), argv=argv, environment={k: v for k, v in env.items()
                                                          if k.startswith('VITREA_')}))
        with (runs / (batch['name'] + '.log.txt')).open('x') as log:
            result = subprocess.run(argv, cwd=CAL, env=env, stdout=log, stderr=subprocess.STDOUT)
        write_once(done, dict(at=now(), exitCode=result.returncode))
        print(batch['name'], 'exit', result.returncode, flush=True)
        if result.returncode != 0:
            return 1
    return 0


def compare():
    record = json.loads((HERE / 'plan.json').read_text())
    frozen = json.loads((ATTEMPT / 'rendered.json').read_text())['cells']
    rows, moved, absent = {}, [], []
    for batch in record['batches']:
        for scene in batch['scenes']:
            cell = batch['profile'] + '/' + scene
            png = OUT / batch['phase'] / batch['profile'] / scene / f'{scene}__webgpu.png'
            if not png.exists():
                absent.append(cell)
                rows[cell] = dict(status='ABSENT')
                continue
            now_sha = sha(png)
            same = now_sha == frozen[cell]['pngSha256']
            if not same:
                moved.append(cell)
            rows[cell] = dict(status='identical' if same else 'MOVED', pngSha256=now_sha,
                              frozenPngSha256=frozen[cell]['pngSha256'],
                              frozenProjectionSha256=frozen[cell]['projectionSha256'])
    summary = dict(cells=len(rows), identical=sum(r['status'] == 'identical' for r in rows.values()),
                   moved=moved, absent=absent,
                   verdict='NO PREDICTION MOVED' if not moved and not absent else 'STOP')
    write_once(HERE / 'comparison.json', dict(summary=summary, cells=rows))
    print(json.dumps(summary, indent=1))
    return 0 if summary['verdict'] == 'NO PREDICTION MOVED' else 2


if __name__ == '__main__':
    mode = sys.argv[1]
    sys.exit({'plan': plan, 'capture': capture, 'compare': compare}[mode]() or 0)
