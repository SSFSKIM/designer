#!/usr/bin/env python3.12
"""W42 identification roles, payload access and web launcher (charter clause 1: the split,
"enforced by the wave reader and launcher"; clause 11's receipt; X26 as carried).

Derived from W39 G0's `wave.py` (§5.184), which stays untouched and whose `Receipt` and
`_Authorization` this module reuses by import: the same procedural boundary, not
encryption. Producers may archive every state, holdout included, but publish only
inventory, hashes and admission; a reader checks identification membership before opening
any payload; the holdout opens only inside the one receipt.

What W42 changes, each because the bed needs it:

- The split lives IN the scenes file (scenes-w42-body.json `split`): calibration,
  validation, holdout (H) and probe. `probe` holds family F's bridges and the references
  whose only dependents are bridges: read only to tie the repeat bar across sittings,
  never fit support and never a clause 6 survival cell. `recorded` must be empty.
  bed.json repeats the roles per cell; the two must agree, and both are pinned.
- A glass cell's one dependency is its no-glass reference `ref-<background>__<state>`
  (run 1 of its pass); there are no opaque controls. A reference never ranks above a
  dependent (calibration/probe < validation < holdout).
- The launcher admits `offset`: component-region.ts's place() centres a shape with
  Math.round and adds an offset, exactly as SceneSpec.swift's frame(in:) does for an
  integer offset on this canvas. `position`, columns, groups, stacks and fractional sizes
  or offsets are refused with a reason (none is declared in this bed).
"""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
W39 = ROOT / 'packages/calibration/results/2026-09-26-w39-g0-colour-edge-bed/wave.py'
_spec = importlib.util.spec_from_file_location('w39_wave_for_w42', W39)
w39 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(w39)
Receipt = w39.Receipt                 # reused unmodified: begin/complete/failed, spent forever
refuse_canonical = w39.refuse_canonical
digest, stable = w39.digest, w39.stable

ROLES = ('calibration', 'validation', 'holdout')
FIXTURE_ROLES = ROLES + ('probe',)
RANK = {'calibration': 0, 'probe': 0, 'validation': 1, 'holdout': 2}
SHAPES = ('capsule', 'capsule-circular', 'rrect')
SCENES = HERE / 'scenes-w42-body.json'
BED = HERE / 'bed.json'
PINS = HERE / 'pins.json'
RECEIPT_LOG = HERE / 'wave-identification-receipt.jsonl'
SAMPLING_PADDING = 24   # DEFAULT_GROUP_SAMPLING.samplingPadding, packages/core (reported, not refused)


def members(component):
    kind = component['kind']
    if kind in ('group', 'column'):
        return list(component['items'])
    if kind == 'stack':
        return [component['base'], component['over']]
    return [component]


def native_only(component):
    if component['kind'] == 'none':
        return True
    return any(m.get('opaque') is True for m in members(component))


def js_round(x):
    return math.floor(x + 0.5)


def web_placement_refusal(component, canvas):
    """Why the web instrument would draw this glass cell somewhere else, or None.

    Mirrors place() in packages/calibration/src/component-region.ts (a lone shape centred
    with Math.round, plus `offset`) against SceneSpec.swift's frame(in:) (centred, plus
    `offset`, unrounded).
    """
    kind = component['kind']
    if kind in ('column', 'group', 'stack'):
        return kind + ': not a single shape; the W42 bed declares single shapes only'
    if kind not in SHAPES:
        return kind + ': not a shape this bed launches on the web side'
    if 'position' in component:
        return 'position: component-region.ts ignores it and would centre the shape'
    width, height = component['size']
    if width != int(width) or height != int(height):
        return 'fractional size %gx%g: web layout of a fractional size is unattested' % (width, height)
    dx, dy = component.get('offset', [0, 0])
    if dx != int(dx) or dy != int(dy):
        return 'fractional offset: the native .offset snaps fractional translations (W34 §5.174)'
    native = ((canvas['width'] - width) / 2 + dx, (canvas['height'] - height) / 2 + dy)
    web = (js_round((canvas['width'] - width) / 2) + dx, js_round((canvas['height'] - height) / 2) + dy)
    if native != web:
        return 'origin %s natively, %s on the web' % (native, web)
    return None


def clearance(component, canvas):
    """The box's least distance to the canvas edge, in CSS px (a note, not a refusal)."""
    width, height = component['size']
    dx, dy = component.get('offset', [0, 0])
    left, top = (canvas['width'] - width) / 2 + dx, (canvas['height'] - height) / 2 + dy
    return min(left, top, canvas['width'] - left - width, canvas['height'] - top - height)


class Wave:
    def __init__(self, scenes=SCENES, bed=BED, pins=PINS):
        self.scenes_path, self.split_path = Path(scenes), Path(bed)
        pinned = json.loads(Path(pins).read_text())
        self.scenes_sha, self.split_sha = digest(scenes), digest(bed)
        if self.scenes_sha != pinned[Path(scenes).name]:
            raise ValueError('scenes hash mismatch')
        if self.split_sha != pinned[Path(bed).name]:
            raise ValueError('bed declaration hash mismatch')
        self.spec = json.loads(self.scenes_path.read_text())
        self.bed = json.loads(self.split_path.read_text())
        self.scenes = {s['id']: s for s in self.spec['scenes']}
        if len(self.scenes) != len(self.spec['scenes']):
            raise ValueError('duplicate scene id')
        split = self.spec['split']
        if split.get('recorded'):
            raise ValueError('the W42 bed records nothing: recorded must be empty')
        assigned = [s for role in FIXTURE_ROLES for s in split.get(role, [])]
        if len(assigned) != len(set(assigned)) or set(assigned) != set(self.scenes):
            raise ValueError('identification membership must be complete, unique and disjoint')
        self.roles = {s: role for role in FIXTURE_ROLES for s in split.get(role, [])}
        for cid, cell in self.bed['cells'].items():
            for sid in self.scenes:
                if sid.rsplit('__', 1)[0] == cid and self.roles[sid] != cell['role']:
                    raise ValueError(f'bed.json and the scenes split disagree on {sid}')
        self.cells, self.profiles_of = set(), {}
        for profile in self.spec['profiles']:
            ids = self.scenes if profile['scenes'] == 'all' else profile['scenes']
            for sid in ids:
                if sid not in self.scenes:
                    raise ValueError('profile membership names unknown scene')
                self.cells.add(profile['key'] + '/' + sid)
                self.profiles_of.setdefault(sid, set()).add(profile['key'])
        self.dependencies = self._dependencies()

    def component(self, sid):
        return self.spec['components'][self.scenes[sid]['component']]

    def _dependencies(self):
        out = {}
        for sid, scene in self.scenes.items():
            if native_only(self.component(sid)) or sid not in self.profiles_of:
                continue
            ref = f"ref-{scene['background']}__{scene['state']}"
            if ref not in self.scenes or self.component(ref)['kind'] != 'none':
                raise ValueError('glass scene without its no-glass reference: ' + sid)
            if self.scenes[ref]['background'] != scene['background'] or self.scenes[ref]['state'] != scene['state']:
                raise ValueError('reference must share background and pose: ' + sid)
            if not self.profiles_of[sid] <= self.profiles_of.get(ref, set()):
                raise ValueError('reference absent from a profile its dependent is in: ' + sid)
            if RANK[self.roles[ref]] > RANK[self.roles[sid]]:
                raise PermissionError('reference role ranks above its dependent: ' + ref)
            out[sid] = dict(noGlass=ref)
        return out

    def select(self, roles=('calibration', 'validation'), authorization=None):
        if not roles or any(r not in FIXTURE_ROLES for r in roles):
            raise ValueError('unknown identification role')
        if 'holdout' in roles:
            if authorization is None:
                raise PermissionError('holdout requires the wave receipt')
            authorization.check(self)
        return sorted(s for s, r in self.roles.items() if r in roles)

    def launch_plan(self, roles=('calibration', 'validation'), authorization=None):
        """The web allowlist and every selected scene left out of it, with its reason."""
        included, excluded = [], {}
        for sid in self.select(roles, authorization):
            if sid not in self.profiles_of:
                excluded[sid] = 'dump-only rest twin: captured in no pass'
                continue
            component = self.component(sid)
            if native_only(component):
                excluded[sid] = 'native-only (no-glass reference)'
                continue
            refusal = web_placement_refusal(component, self.spec['canvas'])
            if refusal:
                excluded[sid] = refusal
            else:
                included.append(sid)
        return included, excluded

    def launch_scenes(self, roles=('calibration', 'validation'), authorization=None):
        return self.launch_plan(roles, authorization)[0]

    def reader(self, root, roles=('calibration', 'validation'), authorization=None):
        return Reader(self, root, roles, authorization)


class Reader(w39.Reader):
    """W39's reader over a W42 archive inventory: payload paths begin with the cell's role.

    W42 adds one guarded section (the bed review's B-M2): `holdoutOperational`, each capture
    run's WHOLE manifest and capture log, whose held-out fixtures carry pixel statistics
    (deltaFromBackground, chromaShift, repeatNoise). The public operational copies are redacted
    for H; the whole ones open only with an active receipt for this declaration and generation.
    """

    def read_holdout_operational(self, path):
        if self.authorization is None:
            raise PermissionError('the whole capture manifests are holdout-role payload: read only inside the '
                                  'one receipt')
        self.authorization.check(self.wave, self.generation)
        inventory = json.loads((self.root / 'inventory.json').read_bytes())
        if hashlib.sha256((self.root / 'inventory.json').read_bytes()).hexdigest() != self.generation:
            raise ValueError('inventory changed under the reader')
        rows = [r for r in inventory.get('holdoutOperational', []) if r['path'] == path]
        if len(rows) != 1 or not path.startswith('holdout/operational/'):
            raise ValueError('not a holdout operational entry: ' + path)
        target = (self.root / path).resolve()
        if self.root not in target.parents:
            raise ValueError('payload escaped evidence root')
        raw = target.read_bytes()
        if hashlib.sha256(raw).hexdigest() != rows[0]['sha256']:
            raise ValueError('payload hash mismatch')
        return raw


def default_wave():
    return Wave()


def web_plan(wave):
    """The W42 web plan: which declared glass cells vitrea can pose, by pass and family.

    Holdout membership is public declaration metadata; listing it opens no payload and needs
    no receipt (W41 runner.cells_for), so the plan is computed from the scenes file directly.
    """
    canvas = wave.spec['canvas']
    passes = {}
    for key, p in wave.bed['passes'].items():
        rows = {}
        for cid in p['cells']:
            sid = f"{cid}__{p['state']}"
            component = wave.component(sid)
            refusal = web_placement_refusal(component, canvas)
            cell = wave.bed['cells'][cid]
            rows[cid] = dict(scene=sid, family=cell['family'], role=wave.roles[sid],
                             plannable=refusal is None, reason=refusal,
                             clearanceCss=clearance(component, canvas))
        by_family = {}
        for r in rows.values():
            f = by_family.setdefault(r['family'], dict(declared=0, plannable=0))
            f['declared'] += 1
            f['plannable'] += r['plannable']
        passes[key] = dict(profile=p['profile'], cells=rows, byFamily=by_family,
                           declared=len(rows), plannable=sum(r['plannable'] for r in rows.values()),
                           belowSamplingPadding=sorted(c for c, r in rows.items()
                                                       if r['clearanceCss'] < SAMPLING_PADDING))
    return passes


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='action', required=True)
    plan = sub.add_parser('plan', help='the W42 web plan (metadata only); --out writes web-plan.json')
    plan.add_argument('--out', type=Path)
    report = sub.add_parser('inventory', help='inventory, hashes and paths only; no payload')
    report.add_argument('root', type=Path)
    args = ap.parse_args(argv)
    wave = default_wave()
    if args.action == 'inventory':
        print(json.dumps(wave.reader(args.root).report_inventory(), indent=2))
        return
    passes = web_plan(wave)
    included, excluded = wave.launch_plan(('calibration', 'validation', 'probe'))
    total = {k: dict(declared=v['declared'], plannable=v['plannable']) for k, v in passes.items()}
    families = {}
    for p in passes.values():
        for f, v in p['byFamily'].items():
            agg = families.setdefault(f, dict(declared=0, plannable=0))
            agg['declared'] += v['declared']
            agg['plannable'] += v['plannable']
    value = dict(
        schema='w42-web-plan-1', scenesSha256=wave.scenes_sha, bedSha256=wave.split_sha,
        derivedFrom=['packages/calibration/web/scene.ts (backgrounds are fixture rasters of any kind; '
                     'scene.state inactive -> runtime receded pose; texture sampling)',
                     'packages/calibration/web/scenes.ts + src/component-region.ts (single shapes, '
                     'Math.round centring plus offset; position ignored; none/opaque native-only)'],
        rule='a glass cell is web-plannable iff it is a single capsule/rrect whose native frame '
             '(centred + offset) equals the web frame (Math.round centred + offset)',
        passTotals=total, familyTotals=families, passes=passes,
        preExposureLaunch=dict(roles=['calibration', 'validation', 'probe'], scenes=included,
                               excluded=excluded,
                               environment=dict(VITREA_SCENES=str(wave.scenes_path.relative_to(ROOT)),
                                                VITREA_FIXTURES='<the G1 materialised W42 fixture root, outside '
                                                                'the repository>')),
        holdout='H cells are posed only inside the one receipt (clause 11); their plannability above is '
                'declaration metadata, and their blind rendered predictions are frozen before it',
    )
    text = json.dumps(value, indent=1) + '\n'
    if args.out:
        args.out.write_text(text)
    print(json.dumps(dict(passTotals=total, familyTotals=families), indent=1))


if __name__ == '__main__':
    main()
