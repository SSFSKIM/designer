#!/usr/bin/env python3
"""W39 identification roles, payload access, launcher and one-exposure receipt (§5.184).

Derived from W34 G0's `wave.py` (§5.174), which stays untouched. The same
procedural boundary, not encryption: producers may archive every state,
including holdout, but publish only inventory, hashes and admission; readers
check identification membership before opening any pixel, crop or statistic,
and the fixture's broad `probe` role is never an analytical permission.

What W39 adds, each because the bed needs it:

- The split names each glass cell's DEPENDENCIES (its no-glass reference and its
  opaque control) explicitly, because W39's references are not recoverable by
  W34's naming convention (the colour `none` references exist in run 1 only; the
  colour cells borrow the grey-128 centre opaque as path registration). A
  dependency never ranks above its dependent (calibration < validation <
  holdout), so no calibration payload carries holdout pixels; a true pair (same
  background, same geometry) shares one role; any other borrow is calibration.
- The launcher excludes, with a reason per scene, every cell the web side would
  draw somewhere else than the native side does: `component-region.ts` knows
  neither `position` nor `column` and centres every shape, so an off-centre,
  column or fractional-size cell is native-only identification material.
- The preflight scenes file is pinned beside the bed and refused: its captures
  are never identification material, and no preflight id may appear in the bed.
"""
import argparse
from contextlib import contextmanager
import datetime
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import runpy
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ROLES = ('calibration', 'validation', 'holdout')
RANK = {role: i for i, role in enumerate(ROLES)}
SPLIT_SCHEMA = 'w39-split-1'
SHAPES = ('capsule', 'capsule-circular', 'rrect')
# Outputs a probe run may never reach: the canonical fixtures, matrix and capture
# trees, and the homes of superseded generations (CLAUDE.md, W30 G1, W32 G0b).
CANONICAL = ['apps/reference-apple/fixtures', 'packages/calibration/results/matrix.json',
             'packages/calibration/results/superseded', 'packages/calibration/web-captures',
             'packages/calibration/web-captures-superseded']


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def stamp(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def stable(value): return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def members(component):
    kind = component['kind']
    if kind == 'group' or kind == 'column': return list(component['items'])
    if kind == 'stack': return [component['base'], component['over']]
    return [component]


def native_only(component):
    if component['kind'] == 'none': return True
    return any(m.get('opaque') is True for m in members(component))


def geometry_key(component):
    """The component with its fill stripped: what a glass cell and its opaque twin share."""
    def strip(shape): return {k: v for k, v in shape.items() if k not in ('opaque', 'fillSRGB')
                              and not k.startswith('$')}
    if component['kind'] in ('group', 'column'):
        return stable({**strip(component), 'items': [strip(m) for m in component['items']]})
    if component['kind'] == 'stack':
        return stable({**strip(component), 'base': strip(component['base']),
                       'over': strip(component['over'])})
    return stable(strip(component))


def js_round(x): return math.floor(x + 0.5)


def web_placement_refusal(component, canvas):
    """Why the web instrument would draw this glass cell elsewhere, or None.

    Mirrors `place()` in `packages/calibration/src/component-region.ts`: a lone
    shape centred with `Math.round`, plus `offset`; no `position`, no `column`.
    """
    if component['kind'] == 'column':
        return 'column: two independent surfaces; the web side has no column kind'
    if component['kind'] not in SHAPES:
        return component['kind'] + ': not a single shape this bed launches on the web side'
    width, height = component['size']
    if width != int(width) or height != int(height):
        return 'fractional size %gx%g: web layout of a fractional size is unattested' % (width, height)
    if 'offset' in component:
        return 'offset: W39 shapes are placed by position only'
    left = js_round((canvas['width'] - width) / 2)
    top = js_round((canvas['height'] - height) / 2)
    if 'position' in component:
        x, y = component['position']
        if (x - width / 2, y - height / 2) != (left, top):
            return 'position (%g, %g): web side centres the shape at (%g, %g)' % (
                x, y, left + width / 2, top + height / 2)
    return None


class Wave:
    def __init__(self, scenes, split, pins, preflight=None):
        self.scenes_path, self.split_path = Path(scenes), Path(split)
        pinned = json.loads(Path(pins).read_text())
        self.scenes_sha, self.split_sha = digest(scenes), digest(split)
        if self.scenes_sha != pinned['scenesSha256']: raise ValueError('scenes hash mismatch')
        if self.split_sha != pinned['splitSha256']: raise ValueError('split hash mismatch')
        self.spec = json.loads(self.scenes_path.read_text())
        self.split = json.loads(self.split_path.read_text())
        if self.split.get('schema') != SPLIT_SCHEMA: raise ValueError('split schema is not ' + SPLIT_SCHEMA)
        self.scenes = {s['id']: s for s in self.spec['scenes']}
        assigned = [s for role in ROLES for s in self.split[role]]
        if len(self.scenes) != len(self.spec['scenes']) or len(assigned) != len(set(assigned)) \
                or set(assigned) != set(self.scenes):
            raise ValueError('identification membership must be complete, unique and disjoint')
        fixture = self.spec['split']
        if set(fixture.get('probe', [])) != set(self.scenes) or any(
                fixture.get(role, []) for role in ['calibration', 'validation', 'holdout', 'recorded']):
            raise ValueError('fixture membership must be probe only')
        self.roles = {s: role for role in ROLES for s in self.split[role]}
        self.cells, self.profiles_of = set(), {}
        for profile in self.spec['profiles']:
            ids = self.scenes if profile['scenes'] == 'all' else profile['scenes']
            for sid in ids:
                if sid not in self.scenes: raise ValueError('profile membership names unknown scene')
                self.cells.add(profile['key'] + '/' + sid)
                self.profiles_of.setdefault(sid, set()).add(profile['key'])
        self.dependencies = self._dependencies()
        self.preflight_ids = set()
        if preflight is not None:
            if digest(preflight) != pinned.get('preflightScenesSha256'):
                raise ValueError('preflight scenes hash mismatch')
            self.preflight_ids = {s['id'] for s in json.loads(Path(preflight).read_text())['scenes']}
            if self.preflight_ids & set(self.scenes):
                raise ValueError('preflight scenes are never identification material; ids overlap the bed')

    def component(self, sid): return self.spec['components'][self.scenes[sid]['component']]

    def _dependencies(self):
        declared = self.split.get('dependencies')
        if not isinstance(declared, dict): raise ValueError('split must declare dependencies')
        glass = {s for s in self.scenes if not native_only(self.component(s))}
        if set(declared) != glass:
            raise ValueError('dependencies must name exactly the glass scenes')
        for sid, deps in declared.items():
            if set(deps) != {'noGlass', 'opaque'}: raise ValueError('dependency must be {noGlass, opaque}')
            scene, reference, opaque = self.scenes[sid], deps['noGlass'], deps['opaque']
            if reference not in self.scenes or opaque not in self.scenes:
                raise ValueError('dependency names unknown scene')
            if self.component(reference)['kind'] != 'none':
                raise ValueError('noGlass dependency must be a none scene')
            if self.component(opaque)['kind'] == 'none' or not native_only(self.component(opaque)):
                raise ValueError('opaque dependency must be an opaque control')
            if self.scenes[reference]['background'] != scene['background']:
                raise ValueError('noGlass dependency must share the glass cell background')
            for dep in (reference, opaque):
                if self.scenes[dep].get('state') != scene.get('state'):
                    raise ValueError('dependency pose differs from its dependent')
                if not self.profiles_of.get(sid, set()) <= self.profiles_of.get(dep, set()):
                    raise ValueError('dependency is absent from a profile its dependent is in')
                if RANK[self.roles[dep]] > RANK[self.roles[sid]]:
                    raise PermissionError('dependency role ranks above its dependent: ' + dep)
            pair = self.scenes[opaque]['background'] == scene['background'] and \
                geometry_key(self.component(opaque)) == geometry_key(self.component(sid))
            if pair and self.roles[opaque] != self.roles[sid]:
                raise ValueError('glass/control pair must share one role: ' + sid)
            if not pair and self.roles[opaque] != 'calibration':
                raise ValueError('a borrowed opaque control must be calibration: ' + sid)
        return declared

    def select(self, roles=('calibration', 'validation'), authorization=None):
        if not roles or any(r not in ROLES for r in roles): raise ValueError('unknown identification role')
        if 'holdout' in roles:
            if authorization is None: raise PermissionError('holdout requires the wave receipt')
            authorization.check(self)
        return sorted(s for s, r in self.roles.items() if r in roles)

    def launch_plan(self, roles=('calibration', 'validation'), authorization=None):
        """The compare.ts allowlist and every selected scene left out of it, with its reason."""
        included, excluded = [], {}
        for sid in self.select(roles, authorization):
            component = self.component(sid)
            if native_only(component):
                excluded[sid] = 'native-only control (none or opaque)'; continue
            refusal = web_placement_refusal(component, self.spec['canvas'])
            if refusal: excluded[sid] = refusal
            else: included.append(sid)
        return included, excluded

    def launch_scenes(self, roles=('calibration', 'validation'), authorization=None):
        return self.launch_plan(roles, authorization)[0]

    def reader(self, root, roles=('calibration', 'validation'), authorization=None):
        return Reader(self, root, roles, authorization)


class Reader:
    def __init__(self, wave, root, roles, authorization):
        self.wave, self.root = wave, Path(root).resolve()
        self.allowed = set(wave.select(roles, authorization))
        self.authorization = authorization
        raw_inventory = (self.root / 'inventory.json').read_bytes()
        self.generation = hashlib.sha256(raw_inventory).hexdigest()
        if 'holdout' in roles: authorization.check(wave, self.generation)
        inventory = json.loads(raw_inventory)
        if inventory.get('scenesSha256') != wave.scenes_sha or inventory.get('splitSha256') != wave.split_sha:
            raise ValueError('evidence generation does not name this pinned declaration')
        self.entries = {}
        for row in inventory['entries']:
            cell = row['cell']
            if cell not in wave.cells: raise ValueError('inventory names undeclared cell')
            sid = cell.split('/', 1)[1]
            parts = Path(row['path']).parts
            if not parts or parts[0] != wave.roles[sid] or '..' in parts or Path(row['path']).is_absolute():
                raise ValueError('payload placement disagrees with identification role')
            key = (cell, row['kind'])
            if key in self.entries: raise ValueError('duplicate payload identity')
            self.entries[key] = row

    def read(self, cell, kind):
        if cell not in self.wave.cells: raise ValueError('undeclared cell')
        sid = cell.split('/', 1)[1]
        if sid not in self.allowed:
            raise PermissionError(self.wave.roles[sid] + ' payload is outside authorised identification roles')
        if self.wave.roles[sid] == 'holdout': self.authorization.check(self.wave, self.generation)
        row = self.entries[(cell, kind)]
        path = (self.root / row['path']).resolve()
        if self.root not in path.parents: raise ValueError('payload escaped evidence root')
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != row['sha256']: raise ValueError('payload hash mismatch')
        return raw

    def report_inventory(self):
        # Never read or deserialise payload here, even for admitted holdout cells.
        return [{k: r[k] for k in ['cell', 'kind', 'sha256', 'path']} for r in self.entries.values()]


class _Authorization:
    def __init__(self, configuration):
        self.configuration, self.active = configuration, True

    def check(self, wave, generation=None):
        if not self.active: raise PermissionError('inactive exposure receipt')
        if self.configuration['scenes'] != wave.scenes_sha or self.configuration['split'] != wave.split_sha:
            raise PermissionError('receipt does not authorise this declaration')
        if generation is not None and generation not in self.configuration['generation']:
            raise PermissionError('receipt does not authorise this evidence generation')


class Receipt:
    def __init__(self, log, configuration):
        self.log, self.configuration = Path(log), configuration
        if not {'scenes', 'split', 'generation', 'instrument', 'closure', 'candidate'} <= set(configuration):
            raise ValueError('incomplete identification configuration')
        generations = configuration['generation']
        if not isinstance(generations, list) or not generations or any(
                not isinstance(g, str) or len(g) != 64 or any(c not in '0123456789abcdef' for c in g)
                for g in generations):
            raise ValueError('generation must freeze the permitted inventory SHA-256 hashes')
        self.sha = hashlib.sha256(stable(configuration).encode()).hexdigest()

    def append(self, event):
        self.log.parent.mkdir(parents=True, exist_ok=True)
        with self.log.open('a') as f:
            f.write(stable(dict(at=stamp(), event=event, configurationSha256=self.sha,
                                configuration=self.configuration)) + '\n')
            f.flush(); os.fsync(f.fileno())

    @contextmanager
    def expose(self):
        lock = self.log.with_suffix(self.log.suffix + '.lock')
        try: fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError: raise PermissionError('exposure already active or interrupted')
        os.close(fd)
        token = None
        try:
            # The entire wave is spent, not just an individual candidate digest.
            # A failed attempt and a process killed after begin both consume it.
            if self.log.exists() and self.log.stat().st_size:
                raise PermissionError('wave holdout exposure already spent; changed candidates do not reset it')
            self.append('begin')
            token = _Authorization(self.configuration)
            try:
                yield token
            except BaseException:
                self.append('failed'); raise
            else: self.append('complete')
        finally:
            if token is not None: token.active = False
            lock.unlink()


def committed(path):
    path = Path(path).resolve()
    relative = path.relative_to(ROOT)
    saved = subprocess.check_output(['git', '-C', str(ROOT), 'show', 'HEAD:' + str(relative)],
                                    stderr=subprocess.PIPE)
    if saved != path.read_bytes(): raise ValueError('configuration input is not committed: ' + str(path))
    return hashlib.sha256(saved).hexdigest()


def configuration(wave, inventories, candidate, runner):
    return dict(scenes=wave.scenes_sha, split=wave.split_sha, generation=sorted({digest(p) for p in inventories}),
                instrument={str(p.relative_to(ROOT)): committed(p) for p in
                            [HERE / 'w39_readers.py', HERE / 'w39_archive.py', HERE / 'wave.py',
                             Path(runner).resolve()]},
                closure=committed(HERE / 'closure.json'),
                candidate=dict(sha256=committed(candidate), document=json.loads(Path(candidate).read_text())))


def default_wave():
    return Wave(ROOT / 'apps/reference-apple/scenes-w39-colour-edge.json', HERE / 'split.json',
                HERE / 'pins.json', ROOT / 'apps/reference-apple/scenes-w39-preflight.json')


def refuse_canonical(*paths):
    canonical = [(ROOT / c).resolve() for c in CANONICAL]
    for path in paths:
        resolved = Path(path).resolve()
        if any(resolved == c or c in resolved.parents or resolved in c.parents for c in canonical):
            raise ValueError('wave launcher refuses canonical fixture or output paths: ' + str(path))


def compare_command(wave, ids, fixtures, out_matrix, captures):
    refuse_canonical(fixtures, out_matrix, captures)
    command = ['pnpm', '--dir', str(ROOT), '--filter', '@vitrea/calibration', '--fail-if-no-match',
               'run', 'compare', '--', '--set', 'probe', '--scene', ','.join(ids), '--renderer', 'webgpu',
               '--out-matrix', str(Path(out_matrix).resolve()), '--write-partial']
    env = {'VITREA_SCENES': str(wave.scenes_path.resolve()), 'VITREA_FIXTURES': str(Path(fixtures).resolve()),
           'VITREA_WEB_CAPTURES': str(Path(captures).resolve())}
    return command, env


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='action', required=True)
    plan = sub.add_parser('plan', help='print (and with --execute run) the compare.ts launch')
    plan.add_argument('--roles', default='calibration,validation')
    plan.add_argument('--fixtures', type=Path, required=True)
    plan.add_argument('--out-matrix', type=Path, required=True)
    plan.add_argument('--captures', type=Path, required=True)
    plan.add_argument('--execute', action='store_true')
    report = sub.add_parser('inventory', help='inventory, hashes and paths only; no payload')
    report.add_argument('root', type=Path)
    expose = sub.add_parser('expose', help='the once-only holdout exposure on a receipt')
    expose.add_argument('--inventory', type=Path, action='append', required=True)
    expose.add_argument('--candidate', type=Path, required=True)
    expose.add_argument('--runner', type=Path, required=True)
    args = ap.parse_args(argv); wave = default_wave()
    if args.action == 'inventory':
        print(json.dumps(wave.reader(args.root).report_inventory(), indent=2))
    elif args.action == 'plan':
        # No receipt exists on this path, so a holdout role is refused by select().
        ids, excluded = wave.launch_plan(args.roles.split(','))
        if not ids: raise ValueError('no web-placeable glass scenes selected')
        command, env = compare_command(wave, ids, args.fixtures, args.out_matrix, args.captures)
        print(json.dumps(dict(roles=args.roles.split(','), scenes=ids, excluded=excluded,
                              command=command, environment=env), indent=2))
        if args.execute: subprocess.run(command, env={**os.environ, **env}, check=True)
    else:
        if any(importlib.util.find_spec(name) is None for name in ['numpy', 'PIL']):
            raise SystemExit('expose needs Python3.12 with numpy/PIL; no receipt was spent')
        config = configuration(wave, args.inventory, args.candidate, args.runner)
        with Receipt(HERE / 'wave-identification-receipt.jsonl', config).expose() as token:
            runpy.run_path(str(args.runner), init_globals={'W39_WAVE': wave, 'W39_AUTHORIZATION': token},
                           run_name='__main__')


if __name__ == '__main__': main()
