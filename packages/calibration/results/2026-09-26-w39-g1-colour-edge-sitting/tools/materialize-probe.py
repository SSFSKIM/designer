#!/usr/bin/env python3.12
"""W39 G1: materialise the probe bed from the four seven-run passes, partitioned by role (§5.185).

Derived from W34 G0's `materialize-producer.py` (untouched). Each pass's seven admitted normal
runs go through the canonical `cli/materialize.ts --set probe --frequency-settle --apply` into
a private staging root, and the staged bed is then partitioned by IDENTIFICATION role (G0's
`split.json`) into `<out>/{calibration,validation,holdout}/<profile>/`. It runs only after the
archive of record exists, and refuses a run that archive does not name.

Two W39 differences, both explicit:

- Run 1 of every pass reads a DIFFERENT declaration from runs 2-7: `pass-spec.derive` adds the
  colour `none` references to run 1 alone (the charter's cost ruling), and on every cell they
  share the two declarations are identical (scenes, components, backgrounds, canvas; checked by
  `test-g1-tools.py` against pass-spec for all four passes). `materialize.ts` refuses runs that
  read two declaration digests (`run-provenance.ts` rule 6), rightly by its own terms, and it is
  canonical tooling this gate does not edit. So it resolves the six runs 2-7, which read ONE
  declaration, and run 1 is then FOLDED in here as the seventh vote on each shared cell
  (`fold_first_run`): where run 1 holds the published state, the cell is recorded as seven runs
  agreeing on it; where run 1 differs, the cell is kept only if runs 2-7 were unanimous (six
  against one, which no seven-run plurality could overturn) and the difference is recorded; any
  other disagreement refuses, for a ruling, because a seventh vote could change it. The cells
  run 1 alone captured (the references) are then added from run 1's own bytes and manifest
  entry, marked `singleRun: true`; they are not a plurality and do not claim to be one, and the
  archive of record holds that one state. Every run, run 1 included, is in the archive and in
  the repeat bar; this concerns only which bytes the probe bed publishes.
- The preflight verdict admitted no phase axis, so the declared phase variants were never
  captured. The published membership must equal every declared cell minus exactly those.

Holdout: PNGs and full metadata are written under `<out>/holdout/` (the guarded reader's
procedural boundary, as in W34); its PUBLIC manifest entries keep inventory and admission
fields only; the staged full manifest and the materialiser logs stay under `<out>/holdout/`,
because the logs name state frequencies. stdout carries counts and hashes only.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

G0 = Path(__file__).resolve().parents[2] / '2026-09-26-w39-g0-colour-edge-bed'
sys.path.insert(0, str(G0))
from wave import ROOT, default_wave  # noqa: E402

PASSES = ('active-1x', 'active-2x', 'inactive-1x', 'inactive-2x')
HOLDOUT_PUBLIC = ['sceneId', 'fixtureSet', 'captureMethod', 'materialRendered', 'width', 'height',
                  'presentedActive', 'presentation', 'deterministic']   # never firstRun / frequencies


def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def cells_of(manifest):
    return {(p['profileKey'], f['sceneId']) for p in manifest['profiles'] for f in p['fixtures']}


def staged_cells(stage):
    return cells_of(json.loads((stage / 'manifest.json').read_text()))


def check_run(root, name, n, archived, protocol='normal'):
    """An admitted run n of `name`, named by the archive, captured under its own declaration."""
    admission = json.loads((root / 'admission.json').read_text())
    if admission.get('admitted') is not True or admission.get('pass') != name or admission.get('run') != n \
            or admission.get('protocol') != protocol:
        raise ValueError(f'not an admitted {protocol} run {n} of {name}: {root}')
    manifest_sha = digest(root / 'manifest.json')
    if manifest_sha != admission.get('manifestSha256'):
        raise ValueError(f'admission names a different manifest: {root}')
    if archived is not None and manifest_sha not in archived:
        raise ValueError(f'run is absent from the pre-plurality archive: {root}')
    fields = dict(line.split('=', 1) for line in (root / 'attest.read').read_text().splitlines() if '=' in line)
    if fields.get('passSpecSha256') != digest(root.parent / f'scenes-run-{n}.json'):
        raise ValueError(f'run declaration does not match its pass: {root}')


def stage_stub(stage, first_manifest):
    stub = {k: v for k, v in first_manifest.items() if k not in ('bedProvenance', 'caveats')}
    stub['profiles'] = []; stub['backgrounds'] = {}
    (stage / 'manifest.json').write_text(json.dumps(stub, indent=2) + '\n')
    (stage / 'backgrounds').mkdir(exist_ok=True)   # materialize.ts copies the rasters into it


def materialize_pass(name, others, stage, scenes, logs):
    """materialize.ts over `others` (runs 2..N, one declaration) into `stage`; its exit code.

    Labels are positional so a run directory's name never collides; the logs, which name state
    frequencies, stay private.
    """
    command = ['pnpm', '--dir', str(ROOT), '--filter', '@vitrea/calibration', '--fail-if-no-match',
               'exec', 'tsx', 'cli/materialize.ts', '--set', 'probe', '--frequency-settle', '--apply']
    for i, root in enumerate(others, 2): command += ['--run', f'run-{i}={Path(root).resolve()}']
    env = {**os.environ, 'VITREA_SCENES': str(Path(scenes).resolve()), 'VITREA_FIXTURES': str(stage)}
    (logs / f'{name}-command.json').write_text(json.dumps(command, indent=2) + '\n')
    with (logs / f'{name}.txt').open('w') as f:
        return subprocess.run(command, env=env, stdout=f, stderr=subprocess.STDOUT).returncode


def fold_first_run(stage, run1, others, cells):
    """Run 1 as the seventh vote on each shared cell the six-run materialisation published.

    Returns one record per cell (first run agrees / differs). Refuses when run 1 differs from a
    published state that runs 2..N were not unanimous on: a seventh vote could change that
    plurality, so it is a ruling, not a fold.
    """
    manifest = json.loads((stage / 'manifest.json').read_text())
    one = {(p['profileKey'], f['sceneId']): f for p in json.loads((run1 / 'manifest.json').read_text())['profiles']
           for f in p['fixtures']}
    runs = [{(p['profileKey'], f['sceneId']): f for p in json.loads((r / 'manifest.json').read_text())['profiles']
             for f in p['fixtures']} for r in others]
    folded = []
    for profile in manifest['profiles']:
        for entry in profile['fixtures']:
            key = (profile['profileKey'], entry['sceneId'])
            if key not in cells: continue
            published = digest(stage / entry['file'])
            first = digest(run1 / one[key]['file'])
            states = [digest(r / m[key]['file']) for r, m in zip(others, runs)]
            if first == published:
                verdict = 'agrees'
            elif all(s == published for s in states):
                verdict = 'differs'
            else:
                raise ValueError(f'{"/".join(key)}: run 1 differs from a state runs 2..{len(others) + 1} '
                                 f'were not unanimous on; a seventh vote could change it — a ruling, not a fold')
            entry['firstRun'] = dict(run=run1.name, verdict=verdict, sha256=first)
            entry['runsVoting'] = len(others) + 1
            folded.append(dict(cell='/'.join(key), verdict=verdict))
    (stage / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return folded


def add_first_run_only(stage, run1, run2, admissible):
    """Copy the cells run 1 captured and run 2 did not, from run 1's own bytes and entry.

    `admissible(sceneId)` must hold for each one (in the bed: a `none` reference); a cell that
    materialize.ts already published is a contradiction and refuses.
    """
    manifest = json.loads((stage / 'manifest.json').read_text())
    staged = cells_of(manifest)
    one = json.loads((run1 / 'manifest.json').read_text())
    later = cells_of(json.loads((run2 / 'manifest.json').read_text()))
    added = []
    for profile in one['profiles']:
        target = next(p for p in manifest['profiles'] if p['profileKey'] == profile['profileKey'])
        for entry in profile['fixtures']:
            key = (profile['profileKey'], entry['sceneId'])
            if key in later: continue
            if key in staged: raise ValueError(f'run-1-only cell was already materialised: {key}')
            if not admissible(entry['sceneId']):
                raise ValueError(f'a run-1-only cell is not admissible as a single-run reference: {key}')
            (stage / entry['file']).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(run1 / entry['file'], stage / entry['file'])
            target['fixtures'].append({**entry, 'fixtureSet': 'probe', 'singleRun': True,
                                       'materializedFrom': run1.name})
            added.append('/'.join(key))
        target['fixtures'].sort(key=lambda f: f['sceneId'])
    # A raster only run 1 composited over is indexed and copied from run 1, and one the bed
    # already indexes must be the same bytes (materialize.ts's own rule for backgrounds).
    for id_, path in (one.get('backgrounds') or {}).items():
        indexed = manifest['backgrounds'].get(id_)
        if indexed is None:
            (stage / path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(run1 / path, stage / path); manifest['backgrounds'][id_] = path
        elif indexed != path or digest(stage / indexed) != digest(run1 / path):
            raise ValueError(f'background {id_}: run 1 composited over other bytes than the bed indexes')
    (stage / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return added


def partition(stage, target, roles, expected, declaration, excluded=()):
    """Publish the staged bed by identification role; refuse any membership but `expected`."""
    manifest = json.loads((stage / 'manifest.json').read_text())
    cells = [p['profileKey'] + '/' + f['sceneId'] for p in manifest['profiles'] for f in p['fixtures']]
    if set(cells) != set(expected) or len(cells) != len(set(cells)):
        raise ValueError(f'published membership must be the expected cells once each: '
                         f'{len(set(expected) - set(cells))} missing, {len(set(cells) - set(expected))} extra, '
                         f'{len(cells) - len(set(cells))} repeated')
    target.mkdir(parents=True)
    public = copy.deepcopy(manifest)
    for key in ['bedProvenance', 'caveats']: public.pop(key, None)   # carry holdout frequencies
    inventory = []
    if (stage / 'backgrounds').exists(): shutil.copytree(stage / 'backgrounds', target / 'backgrounds')
    for profile in public['profiles']:
        profile.pop('caveats', None)
        fixtures = []
        for entry in profile['fixtures']:
            sid = entry['sceneId']; cell = profile['profileKey'] + '/' + sid
            role = roles[sid]; base = Path(role) / profile['profileKey']
            (target / base).mkdir(parents=True, exist_ok=True)
            image, meta = base / (sid + '.png'), base / (sid + '.metadata.json')
            shutil.copyfile(stage / entry['file'], target / image)
            (target / meta).write_text(json.dumps(entry, indent=2) + '\n')
            for kind, path in [('png', image), ('metadata', meta)]:
                inventory.append(dict(cell=cell, role=role, kind=kind, path=str(path),
                                      sha256=digest(target / path), admitted=True))
            if role == 'holdout':
                entry = {k: entry[k] for k in HOLDOUT_PUBLIC if k in entry}
            fixtures.append({**entry, 'file': str(image)})
        profile['fixtures'] = fixtures
    (target / 'manifest.json').write_text(json.dumps(public, indent=2) + '\n')
    (target / 'inventory.json').write_text(json.dumps(dict(
        schema='w39-probe-inventory-1', **declaration, excludedScenes=sorted(excluded),
        entries=inventory), indent=2) + '\n')
    (target / 'holdout').mkdir(exist_ok=True)
    (target / 'holdout/full-materializer-manifest.json').write_bytes((stage / 'manifest.json').read_bytes())
    per_role = {}
    for row in inventory:
        if row['kind'] == 'png': per_role[row['role']] = per_role.get(row['role'], 0) + 1
    return dict(admitted=True, cells=len(inventory) // 2, perRole=per_role,
                inventorySha256=digest(target / 'inventory.json'))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', type=Path, required=True, help='the sitting root holding the four passes')
    ap.add_argument('--archive-inventory', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args(argv)
    wave = default_wave()
    out = args.out.resolve()
    if out.exists(): raise ValueError('output already exists; never rewrite recorded evidence')
    if out == ROOT or ROOT in out.parents: raise ValueError('the probe bed is produced outside the repository')
    evidence = json.loads(args.archive_inventory.read_text())
    if evidence.get('scenesSha256') != wave.scenes_sha or evidence.get('splitSha256') != wave.split_sha:
        raise ValueError('the archive does not identify this declaration')
    archived = set(evidence.get('sourceManifests', []))
    spec = importlib.util.spec_from_file_location('w39_sitting', G0 / 'sitting.py')
    sitting = importlib.util.module_from_spec(spec); spec.loader.exec_module(sitting)
    pin = json.loads((args.root / 'verdict-pin.json').read_text())
    unadmitted = sitting.phase_scenes(('x', 'y')) - sitting.phase_scenes(tuple(pin['reachableAxes']))
    runs = {name: [args.root / name / f'run-{n}' for n in range(1, 8)] for name in PASSES}
    for name, roots in runs.items():
        for n, root in enumerate(roots, 1): check_run(root, name, n, archived)
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='w39-materialize-', dir=out.parent) as tmp:
        stage = Path(tmp) / 'bed'; logs = Path(tmp) / 'producer-logs'
        stage.mkdir(); logs.mkdir()
        stage_stub(stage, json.loads((runs[PASSES[0]][1] / 'manifest.json').read_text()))
        single, folded = [], []
        for name, roots in runs.items():
            before = staged_cells(stage)
            if materialize_pass(name, roots[1:], stage, wave.scenes_path, logs):
                failed = out.with_name(out.name + '-FAILED') / 'holdout/producer-logs'
                shutil.copytree(logs, failed)
                raise SystemExit(f'{name}: materialise refused; diagnostics kept behind the holdout boundary '
                                 f'at {failed}')
            folded += fold_first_run(stage, roots[0], roots[1:], staged_cells(stage) - before)
            single += add_first_run_only(stage, roots[0], roots[1],
                                         lambda sid: wave.component(sid)['kind'] == 'none')
        (logs / 'first-run-fold.json').write_text(json.dumps(folded, indent=2) + '\n')
        expected = {c for c in wave.cells if c.split('/', 1)[1] not in unadmitted}
        result = partition(stage, out, wave.roles, expected,
                           dict(scenesSha256=wave.scenes_sha, splitSha256=wave.split_sha), unadmitted)
        shutil.copytree(logs, out / 'holdout/producer-logs')
    print(json.dumps({**result, 'unadmittedPhaseScenes': len(unadmitted), 'singleRunReferences': len(single),
                      'firstRunFolded': len(folded),
                      'firstRunDiffers': sum(f['verdict'] == 'differs' for f in folded)}, indent=2))


if __name__ == '__main__':
    main()
