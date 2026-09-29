#!/usr/bin/env python3.12
"""Reproduce W42 G0's capture bed from its declared tables; never tune pixels (charter clause 1).

The W42 charter (docs/doperpowers/specs/2026-09-29-w42-body-spatial-structure.md, v2.1) fixes
the bed's families and counts ("The bed"); this script gives them exact ids, levels, pitches,
offsets and depths, and writes:

- scenes-w42-body.json: the wave-local scenes file the W39 side bundle reads through
  VITREA_SCENES. Its own `split` carries calibration / validation / holdout (H), and `probe`
  for family F's bridges, which the charter keeps out of clause 6's survival rule.
- bed.json: the companion declaration, per pass: every captured cell, its family, role and
  geometry; the no-glass references of run 1; the sentinels; the dump list; the U-items;
  the validation transfer axes; the charter deviations; the counts.
- twin-audit.json: every glass scene against the canonical, W34 and W39 beds.
- pins.json: the SHA-256 of the three files above.

Placement uses `offset` (integer CSS px) and never `position`: the web side's placeComponent
honours `offset` and ignores `position` (component-region.ts), so every glass cell here is
web-plannable. An integer offset is an integer device-pixel translation at 1x and 2x, so the
fractional `.offset` snapping W34 measured (§5.174) cannot arise.

Run it only to reproduce an unchanged declaration, never to choose cells after capture.
"""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
CANVAS = dict(width=320, height=200)
SCENES_FILE = HERE / 'scenes-w42-body.json'
STATES = {'active': 'rest', 'receded': 'inactive'}
PASSES = [(scale, scheme, pose) for scale in (2, 1) for scheme in ('light', 'dark')
          for pose in ('active', 'receded')]
ROLE_ORDER = ('calibration', 'validation', 'holdout', 'probe')
REF_RANK = {'calibration': 0, 'probe': 0, 'validation': 1, 'holdout': 2}


def grey(v):
    return [v, v, v]


# ------------------------------------------------------------------ components

def shape(kind, size, radius=None, offset=None):
    c = dict(kind=kind, size=list(size))
    if radius is not None:
        c['radius'] = radius
    if offset is not None and offset != (0, 0):
        c['offset'] = list(offset)
    return c


BASE = {
    'capsule-button': ('capsule', (120, 44), None),
    'rrect-64': ('rrect', (112, 64), 13.5),
    'rrect-80': ('rrect', (140, 80), 17),
    'rrect-md': ('rrect', (160, 96), 20),
    # The unseen span for H (charter "The bed", H; the parent's call on v2): s = 112,
    # t = 0.5, holding the probe shapes' aspect 1.75 and radius fraction 0.211
    # (scenes.json $comment-probe-components): 196 x 112, radius 23.6 (0.2107).
    'rrect-112': ('rrect', (196, 112), 23.6),
    'rrect-ml': ('rrect', (224, 128), 27),
    'rrect-lg': ('rrect', (280, 160), 34),
}


def component_id(base, offset=(0, 0)):
    if offset == (0, 0):
        return base
    return f'{base}-o{offset[0]:+d}{offset[1]:+d}'


def component(base, offset=(0, 0)):
    kind, size, radius = BASE[base]
    return shape(kind, size, radius, offset)


def centre(base, offset=(0, 0)):
    """The shape's centre in canvas CSS px, image-down: centred, plus the offset."""
    return (CANVAS['width'] / 2 + offset[0], CANVAS['height'] / 2 + offset[1])


def short_side(base):
    return min(BASE[base][1])


# ----------------------------------------------------------------- backgrounds

def checker(cell, a, b):
    return f'checker-{cell}-{a:03d}-{b:03d}', dict(kind='checkerboard', cell=cell, a=grey(a), b=grey(b))


def impulse(fg, bg, size, spacing):
    return (f'impulse-{fg:03d}-on-{bg:03d}-s{size}-g{spacing}',
            dict(kind='impulse', background=grey(bg), foreground=grey(fg), size=size, spacing=spacing))


def split(x, left, right):
    return f'split-x{x}-{left:03d}-{right:03d}', dict(kind='split', **{'from': grey(left), 'to': grey(right)},
                                                    axis='x', position=x)


def solid(v):
    return f'grey-{v:03d}', dict(kind='solid', srgb=grey(v))


# Family E: isoluminant pairs at Rec.709 luma on codes = 128 (memo A: "Luma = Rec.709 on
# codes"), found by an exhaustive integer search around a +-80-code chroma swing.
E_PAIRS = {
    'rg': ([202, 106, 128], [54, 150, 128]),   # luma 127.998 / 128.002
    'by': ([121, 122, 208], [135, 134, 48]),   # luma 127.997 / 128.003
}
PHOTO = ('photo', dict(kind='synthetic-photo', seed=20260825))

# Levels of the patch and step families: P2's pair, 48 / 208 (encoded mean 128, contrast 160).
# Neither side is censored (X21: >= 250 or <= 5) in any endpoint's uniform response: light
# active reads 164 at input 64 and 210 at input 160 (memo D §6), so 208 lands near 232.
LO, HI = 48, 208
POLARITY = {'hi': (HI, LO), 'lo': (LO, HI)}           # patch: (foreground, background)
STEP = {'lohi': (LO, HI), 'hilo': (HI, LO)}            # step: (from, to) about x = position

# The single-patch impulse geometry. Background.swift fills impulses in CoreGraphics space,
# whose origin is the BOTTOM-left: the first patch is at (spacing/2, spacing/2) there, so in
# the image (and SwiftUI, y down) it is at (spacing/2, 200 - spacing/2), repeating every
# `spacing` (verified on the canonical impulse@1x.png: rows 38-41, 102-105, 166-169).
# spacing >= 214 leaves exactly one patch in the 320 x 200 canvas. The shape is moved onto it
# by an integer offset, keeping the active capture footprint (box + 0.35 s or 16 pt, memo D
# §3) inside the canvas on rrect-md and the capsule; that forces the off-centre patches toward
# the TOP edge. rrect-lg's footprint exceeds the canvas at any placement, as on the canonical
# bed; its box stays inside. verify-backgrounds.py reads every patch back from the rasters.
SINGLE = {g: (g // 2, CANVAS['height'] - g // 2) for g in (232, 256, 300, 336)}


# ------------------------------------------------------------------- the cells

class Bed:
    def __init__(self):
        self.backgrounds = {}
        self.components = {'none': dict(kind='none')}
        self.cells = {}          # semantic id -> record

    def bg(self, pair):
        name, spec = pair
        if name in self.backgrounds and self.backgrounds[name] != spec:
            raise ValueError('background id reused for a different raster: ' + name)
        self.backgrounds[name] = spec
        return name

    def cell(self, sid, family, background, base, *, role, passes, offset=(0, 0), geometry=None,
             bridge=None, note=None, uitems=()):
        if sid in self.cells:
            raise ValueError('duplicate cell ' + sid)
        cid = component_id(base, offset)
        self.components[cid] = component(base, offset)
        cx, cy = centre(base, offset)
        geo = dict(shape=base, shortSide=short_side(base), t=round(min(1, max(0, (short_side(base) - 64) / 96)), 6),
                   offset=list(offset), shapeCentre=[cx, cy])
        geo.update(geometry or {})
        self.cells[sid] = dict(id=sid, family=family, background=background, component=cid, role=role,
                               passes=sorted(passes), geometry=geo, bridge=bridge, note=note,
                               uItems=list(uitems))


def everywhere(scale, poses=('active', 'receded'), schemes=('light', 'dark')):
    return {f'{scale}x-{s}-{p}' for s in schemes for p in poses}


def build():
    bed = Bed()
    two, one = everywhere(2), everywhere(1)
    active2 = everywhere(2, ('active',))

    # A: uniform greys (U5). 30 light / 33 dark per 2x pass.
    for v in (0, 64, 128, 160, 176, 192, 208, 224, 240, 255):
        for base in ('capsule-button', 'rrect-md'):
            bed.cell(f'a-g{v:03d}-{base}', 'A', bed.bg(solid(v)), base, role='calibration', passes=two,
                     uitems=('U5', 'R1'))
    for v in (96, 160, 208, 255):
        bed.cell(f'a-g{v:03d}-rrect-lg', 'A', bed.bg(solid(v)), 'rrect-lg', role='calibration', passes=two,
                 uitems=('U5',))
    for v in (160, 208, 255):
        # rrect-64 is the t = 0 stratum's transfer: every s <= 64 is one declared stratum
        # (memo D §7a), so T measured on the capsule predicts it.
        bed.cell(f'a-g{v:03d}-rrect-64', 'A', bed.bg(solid(v)), 'rrect-64', role='validation', passes=two,
                 uitems=('U5',), note='validation: t = 0 stratum transfer (capsule -> rrect-64)')
        bed.cell(f'a-g{v:03d}-rrect-ml', 'A', bed.bg(solid(v)), 'rrect-ml', role='calibration', passes=two,
                 uitems=('U5',))
        bed.cell(f'a-g{v:03d}-rrect-80', 'A', bed.bg(solid(v)), 'rrect-80', role='calibration',
                 passes=everywhere(2, schemes=('dark',)), uitems=('U5',),
                 note="dark only: memo D's MaxLuma transition (the parent's call on v2)")
    # A at 1x: the small body referee, a scale transfer of T (validation).
    for v in (128, 255):
        bed.cell(f'a-g{v:03d}-rrect-md-1x', 'A', bed.bg(solid(v)), 'rrect-md', role='validation', passes=one,
                 uitems=('U5',), note='1x small body referee: validation of T measured at 2x')

    # B: two-level checkers on rrect-md at pitch 16 and 64 (U1, R1, space, lambda).
    for name, (a, b) in dict(p2=(48, 208), p3=(96, 160), p4=(16, 112), p5=(144, 240)).items():
        for cell in (16, 64):
            role = 'validation' if name == 'p3' else 'calibration'
            bed.cell(f'b-{name}-c{cell}-rrect-md', 'B', bed.bg(checker(cell, a, b)), 'rrect-md', role=role,
                     passes=two, uitems=('U1', 'R1') if name in ('p2', 'p4', 'p3', 'p5') else ('U1',),
                     geometry=dict(pitch=cell, levels=[a, b]),
                     note='validation: level-pair transfer (P3, contrast 64 at mean 128)' if role == 'validation'
                     else None)

    # B': P1 0/255 across spans and pitches (U2, U7, the rrect-lg narrow). Pitch 8 is dropped
    # when receded (the review's offset).
    def bprime(pitch, base, passes, role='calibration', note=None, sid=None, offset=(0, 0), uitems=('U2',)):
        bed.cell(sid or f'bp-p1-c{pitch}-{base}', "B'", bed.bg(checker(pitch, 0, 255)), base, role=role,
                 passes=passes, offset=offset, geometry=dict(pitch=pitch, levels=[0, 255]), note=note,
                 uitems=uitems)
    for base in ('capsule-button', 'rrect-ml'):
        bprime(8, base, active2 | one if base == 'capsule-button' else active2)
        bprime(32, base, two)
        bprime(64, base, two)
    bprime(32, 'rrect-64', two, uitems=('U2', 'span knot at 64'))
    bprime(32, 'rrect-80', two, role='validation', uitems=('U2',),
           note='validation: span transfer at t = 1/6, between the knot (64) and rrect-md (96)')
    bprime(8, 'rrect-lg', active2 | one, uitems=('U2', 'U7', 'rrect-lg narrow'))
    bprime(32, 'rrect-lg', two | one, uitems=('U2', 'U7', 'rrect-lg narrow'),
           note='also at 1x, in place of the charter\'s P1 pitch 16 on rrect-lg, which is a twin '
                'of the canonical HOLDOUT checkerboard__rrect-lg (bed.json charterDeviations)')
    # B' at 1x only: the fine pitches (memo D §7g).
    bprime(4, 'capsule-button', one, uitems=('1x sampling',))
    # Calibration, not validation: ignoring placement (the twin audit's conservative rule) it
    # twins the canonical probe checkerboard-4__capsule-button, which memo C and memo E read.
    bprime(4, 'capsule-button', one, sid='bp-p1-c4-capsule-button-odd', offset=(1, 1),
           uitems=('1x sampling',),
           note="the review's odd-offset cell: 1 CSS px = half a backdrop texel of phase at 1x")
    bprime(4, 'rrect-md', one, uitems=('1x sampling', 'memo E worst 1x cells'))
    bprime(4, 'rrect-lg', one, uitems=('1x sampling', 'rrect-lg 0.25 scale'))

    # C: single patches (U1, U4, one k or two, depth grading, units, the halo annulus).
    def patch(sid, fg, bg, size, spacing, base, offset, depth, passes, role='calibration', note=None,
              uitems=('U1', 'U4')):
        name = bed.bg(impulse(fg, bg, size, spacing))
        cx, cy = centre(base, offset)
        if spacing in SINGLE:
            px, py = SINGLE[spacing]
            patches = 1
        else:
            px, py = cx, cy
            patches = 'grid'
        bed.cell(sid, 'C', name, base, role=role, passes=passes, offset=offset, note=note, uitems=uitems,
                 geometry=dict(patchSize=size, patchCentre=[px, py], patchFromShapeCentre=[px - cx, py - cy],
                               depth=depth, levels=dict(foreground=fg, background=bg), impulseSpacing=spacing,
                               patchesInCanvas=patches))
    for pol, (fg, bg) in POLARITY.items():
        for size in (8, 32):
            patch(f'c-s{size}-{pol}-rrect-md', fg, bg, size, 232, 'rrect-md', (-44, -16), 48, two,
                  uitems=('U1', 'U4', 'one k or two'))
        patch(f'c-s16-{pol}-capsule-button', fg, bg, 16, 232, 'capsule-button', (-44, -16), 22, two)
    # The depth sweep, S 8, in the polarity whose detail PASSES the knee: bright on dark in the
    # light scheme (Lighten), dark on bright in the dark scheme (Darken). rrect-md's centre is
    # the S 8 cell above. Active: the declared o(d) grading; receded: a falsification control.
    for scheme, pol in (('light', 'hi'), ('dark', 'lo')):
        fg, bg = POLARITY[pol]
        sweep = everywhere(2, schemes=(scheme,))
        patch(f'c-s8-{pol}-d24-rrect-md', fg, bg, 8, 232, 'rrect-md', (-44, 8), 24, sweep, role='validation',
              uitems=('depth',), note='validation: depth transfer (s/4 between the centre and 4 pt)')
        patch(f'c-s8-{pol}-d4-rrect-md', fg, bg, 8, 256, 'rrect-md', (-32, 16), 4, sweep, uitems=('depth',),
              note='inside the active inner-refraction band (height min(s/4, 20) = 20 pt, memo D §3)')
        patch(f'c-s8-{pol}-d80-rrect-lg', fg, bg, 8, 64, 'rrect-lg', (0, 4), 80, sweep,
              uitems=('depth', 'rrect-lg narrow', 'units'),
              note='NOT single: no single-impulse spacing reaches rrect-lg\'s centre with its box inside '
                   'the canvas; the 64-pt grid (the canonical impulse\'s) puts one patch at the centre, '
                   'its neighbours 64 pt away (bed.json charterDeviations)')
        # rrect-lg's two single patches take the spacing that maximises the box's least
        # clearance to the canvas edge (10 and 12 CSS px; the canonical rrect-lg has 20).
        patch(f'c-s8-{pol}-d40-rrect-lg', fg, bg, 8, 300, 'rrect-lg', (-10, -10), 40, sweep, role='validation',
              uitems=('depth', 'rrect-lg narrow'), note='validation: depth transfer on rrect-lg')
        patch(f'c-s8-{pol}-d4-rrect-lg', fg, bg, 8, 336, 'rrect-lg', (8, 8), 4, sweep,
              uitems=('depth', 'rrect-lg narrow'),
              note='inside the active inner-refraction band (20 pt, memo D §3)')
    # The canonical impulse (0/255, 4 pt every 64 pt) on rrect-ml and rrect-lg; rrect-lg also at 1x.
    canon = bed.bg(impulse(255, 0, 4, 64))
    for base, passes in (('rrect-ml', two), ('rrect-lg', two | one)):
        bed.cell(f'c-impulse-{base}', 'C', canon, base, role='calibration', passes=passes,
                 uitems=('U4', 'units', 'rrect-lg narrow'),
                 geometry=dict(patchSize=4, impulseSpacing=64, levels=dict(foreground=255, background=0),
                               patchesInCanvas='grid'))

    # D: steps under and beside the body (U1, U3, U7). The step is a split at x = 160 + delta
    # (the shape stays centred, so delta is the step's offset from the shape centre).
    def step(sid, x, pol, base, passes, role='calibration', note=None, uitems=('U3',)):
        left, right = STEP[pol]
        cx = centre(base)[0]
        bed.cell(sid, 'D', bed.bg(split(x, left, right)), base, role=role, passes=passes, note=note,
                 uitems=uitems, geometry=dict(stepX=x, stepFromShapeCentre=x - cx,
                                              levels=dict(left=left, right=right)))
    for pol in STEP:
        step(f'd-d0-{pol}-rrect-md', 160, pol, 'rrect-md', two, uitems=('U1', 'U3'))
        step(f'd-d32-{pol}-rrect-md', 192, pol, 'rrect-md', two, uitems=('U1', 'U3'))
        step(f'd-d12-{pol}-rrect-md', 172, pol, 'rrect-md', everywhere(2, ('receded',)), uitems=('U1', 'U3'))
        for out in (8, 16):
            passes = two | one if (out, pol) == (8, 'lohi') else two
            step(f'd-out{out}-{pol}-rrect-md', 240 + out, pol, 'rrect-md', passes, uitems=('U3',),
                 note=f'{out} CSS px outside the rrect-md edge (x = 240); the receded margin is 1 dev')
        step(f'd-d0-{pol}-rrect-lg', 160, pol, 'rrect-lg', active2, uitems=('U7',),
             note="the review's bleed rows (active only)")
    step('d-d0-lohi-capsule-button', 160, 'lohi', 'capsule-button', two, role='validation', uitems=('U3',),
         note='validation: span transfer of the step (s 96 -> 44)')
    step('d-d12-lohi-capsule-button', 172, 'lohi', 'capsule-button', everywhere(2, ('receded',)),
         uitems=('U1', 'U3'))

    # E: isoluminant chroma checkers (U6).
    for pair, (a, b) in E_PAIRS.items():
        for cell in (16, 64):
            name = bed.bg((f'checker-{cell}-{pair}', dict(kind='checkerboard', cell=cell, a=a, b=b)))
            bed.cell(f'e-{pair}-c{cell}-rrect-md', 'E', name, 'rrect-md',
                     role='validation' if (pair, cell) == ('by', 64) else 'calibration', passes=two,
                     uitems=('U6',), geometry=dict(pitch=cell, colours=[a, b], luma709OnCodes=128),
                     note='validation: hue transfer at pitch 64' if (pair, cell) == ('by', 64) else None)

    # F: bridges to the canonical and probe sittings (bar tie only; `probe` role).
    for sid, pair, base, passes, canonical in (
            ('f-checker16-rrect-md', checker(16, 0, 255), 'rrect-md', two, 'checkerboard__rrect-md'),
            ('f-impulse-rrect-md', impulse(255, 0, 4, 64), 'rrect-md', two | one, 'impulse__rrect-md'),
            ('f-photo-rrect-md', PHOTO, 'rrect-md', two, 'photo__rrect-md'),
            ('f-checker64-rrect-lg', checker(64, 0, 255), 'rrect-lg', two | one, 'checkerboard-64__rrect-lg')):
        bed.cell(sid, 'F', bed.bg(pair), base, role='probe', passes=passes, bridge=canonical,
                 uitems=('bar across sittings',))

    # H: the structured holdout, declared before capture.
    hold = dict(role='holdout', uitems=('referee',))
    bed.cell('h-p1-c24-rrect-112', 'H', bed.bg(checker(24, 0, 255)), 'rrect-112', passes=two,
             geometry=dict(pitch=24, levels=[0, 255]), **hold,
             note='the unseen span s = 112 (t = 0.5), subject to the side bundle accepting rrect-112')
    bed.cell('h-p6-c32-rrect-md', 'H', bed.bg(checker(32, 32, 176)), 'rrect-md', passes=two,
             geometry=dict(pitch=32, levels=[32, 176]), **hold)
    left, right = STEP['lohi']
    bed.cell('h-d20-lohi-rrect-md', 'H', bed.bg(split(180, left, right)), 'rrect-md', passes=two,
             geometry=dict(stepX=180, stepFromShapeCentre=20, levels=dict(left=left, right=right)), **hold)
    fg, bg = POLARITY['hi']
    bed.cell('h-s24-hi-rrect-md', 'H', bed.bg(impulse(fg, bg, 24, 232)), 'rrect-md', passes=two, offset=(-44, -16),
             geometry=dict(patchSize=24, patchCentre=list(SINGLE[232]), patchFromShapeCentre=[0, 0], depth=48,
                           levels=dict(foreground=fg, background=bg), impulseSpacing=232, patchesInCanvas=1),
             **hold)
    bed.cell('h-p3-c64-rrect-lg', 'H', bed.bg(checker(64, 96, 160)), 'rrect-lg', passes=two | one,
             geometry=dict(pitch=64, levels=[96, 160]), **hold)
    bed.cell('h-lc-c64-capsule-button', 'H', bed.bg(checker(64, 128, 229)), 'capsule-button', passes=two,
             geometry=dict(pitch=64, levels=[128, 229]), **hold)
    bed.cell('h-g184-rrect-md', 'H', bed.bg(solid(184)), 'rrect-md', passes=two, **hold)
    bed.cell('h-g232-rrect-md', 'H', bed.bg(solid(232)), 'rrect-md', passes=two | one, **hold)
    return bed


# ------------------------------------------------------------------- the files

def pass_key(scale, scheme, pose):
    return f'{scale}x-{scheme}-{pose}'


def profile_key(scale, scheme):
    return f'apple-macos-27.0-{scale}x-{scheme}-standard-glass0.5'


EXPECTED = {pass_key(2, 'light', 'active'): 88, pass_key(2, 'dark', 'active'): 91,
            pass_key(2, 'light', 'receded'): 86, pass_key(2, 'dark', 'receded'): 89,
            **{pass_key(1, s, p): 15 for s in ('light', 'dark') for p in ('active', 'receded')}}
SENTINELS = ('f-impulse-rrect-md', 'f-checker64-rrect-lg')


def documents(bed):
    scenes, split = [], {r: [] for r in ROLE_ORDER}
    passes = {}
    for scale, scheme, pose in PASSES:
        key = pass_key(scale, scheme, pose)
        cells = sorted(c['id'] for c in bed.cells.values() if key in c['passes'])
        if len(cells) != EXPECTED[key]:
            raise ValueError(f'{key}: {len(cells)} cells, charter says {EXPECTED[key]}')
        refs = sorted({bed.cells[c]['background'] for c in cells})
        passes[key] = dict(scale=scale, scheme=scheme, pose=pose, profile=profile_key(scale, scheme),
                           state=STATES[pose], cells=cells, references=refs,
                           sentinels=[s for s in SENTINELS if s in cells])
        if passes[key]['sentinels'] != list(SENTINELS):
            raise ValueError(key + ': a sentinel is not in the pass')
    # Scene entries: one per (cell, pose it is captured in), plus the `rest` twin a
    # receded-only cell needs for dump-layers (which refuses non-rest ids in either pose).
    declared = {}
    for c in bed.cells.values():
        poses = {k.rsplit('-', 1)[1] for k in c['passes']}
        states = {STATES[p] for p in poses} | {'rest'}
        for state in sorted(states):
            sid = f"{c['id']}__{state}"
            dump_only = state == 'rest' and 'active' not in poses
            entry = {'id': sid, 'background': c['background'], 'component': c['component'], 'state': state,
                     '$family': c['family']}
            if dump_only:
                entry['$dumpOnly'] = 'the rest twin dump-layers reads for this receded-only cell; never captured'
            declared[sid] = (entry, c['role'])
    # No-glass references, one per distinct backdrop per pass (run 1 only), role ranked no
    # higher than any dependent's (calibration/probe < validation < holdout).
    dependents = {}
    for key, p in passes.items():
        for cid in p['cells']:
            dependents.setdefault(bed.cells[cid]['background'], set()).add(bed.cells[cid]['role'])
    for bg, roles in dependents.items():
        role = min(roles, key=lambda r: (REF_RANK[r], ROLE_ORDER.index(r)))
        for state in ('rest', 'inactive'):
            if any(bg in p['references'] and p['state'] == state for p in passes.values()):
                sid = f'ref-{bg}__{state}'
                declared[sid] = ({'id': sid, 'background': bg, 'component': 'none', 'state': state,
                                  '$family': 'reference'}, role)
    for sid in sorted(declared):
        entry, role = declared[sid]
        scenes.append(entry)
        split[role].append(sid)
    profiles = []
    for scale in (1, 2):
        for scheme in ('light', 'dark'):
            ids = set()
            for p in passes.values():
                if p['scale'] == scale and p['scheme'] == scheme:
                    ids |= {f'{c}__{p["state"]}' for c in p['cells']}
                    ids |= {f'ref-{b}__{p["state"]}' for b in p['references']}
            profiles.append(dict(key=profile_key(scale, scheme), colorScheme=scheme, a11y='standard',
                                 scenes=sorted(ids)))
    spec = {
        '$comment': [
            'W42 G0: the wave-local capture bed (charter 2026-09-29-w42-body-spatial-structure.md v2.1,',
            '"The bed"; clause 1). Generated by packages/calibration/results/2026-09-29-w42-g0-declaration/',
            'bed/declare-bed.py; never edit by hand. The canonical apps/reference-apple/scenes.json is',
            'untouched and no canonical key, 26.5 key or accessibility pass is declared here (X5).',
            '',
            'split: calibration is the fit support (clause 6); validation is read-only transfer along',
            'the axes bed.json names; holdout is H, sealed behind the one-exposure receipt (clause 11);',
            'probe holds family F, the bridges, read ONLY to tie the repeat bar across sittings (not',
            'under clause 6), and the no-glass references whose only dependents are bridges. recorded',
            'is empty. A scene id ending __rest is captured in the active pose, __inactive in the',
            'receded pose; `$dumpOnly` rest twins exist because dump-layers refuses non-rest ids.',
            '',
            'Placement is by integer `offset` only, which both the native harness and the web side',
            "honour; `position` is not used. Canvas 320x200 as canonical (memo B §8)."],
        'version': 1, 'canvas': CANVAS,
        'backgrounds': dict(sorted(bed.backgrounds.items())),
        'components': dict(sorted(bed.components.items())),
        'tints': {}, 'scenes': scenes, 'profiles': profiles,
        'split': dict(calibration=split['calibration'], validation=split['validation'],
                      holdout=split['holdout'], recorded=[], probe=split['probe']),
    }
    return spec, passes


def semantic(c):
    return {k: v for k, v in c.items() if k in ('kind', 'size', 'radius')}


def audit(bed, spec):
    """Every glass scene against canonical, W34 and W39 scenes: same relative geometry (kind,
    size, radius) AND the same backdrop declaration, ignoring placement, canvas, pose and tint
    (W39 declare-bed.py's conservative rule). Reads declaration files only, never a pixel."""
    sources = [('canonical', ROOT / 'apps/reference-apple/scenes.json'),
               ('W34', ROOT / 'apps/reference-apple/scenes-w34-contour.json'),
               ('W39', ROOT / 'apps/reference-apple/scenes-w39-colour-edge.json')]
    rows, problems = [], []
    for cid, c in sorted(bed.cells.items()):
        mine = semantic(spec['components'][c['component']])
        backdrop = spec['backgrounds'][c['background']]
        matches = []
        for source, path in sources:
            old = json.loads(path.read_text())
            roles = {sid: role for role, ids in old['split'].items() if not role.startswith('$') for sid in ids}
            for s in old['scenes']:
                pc = old['components'][s['component']]
                if pc.get('kind') in ('none', 'group', 'stack', 'column') or pc.get('opaque') or s.get('label'):
                    continue
                strip = {k: v for k, v in old['backgrounds'][s['background']].items() if not k.startswith('$')}
                if semantic(pc) == mine and strip == backdrop and not s.get('tint'):
                    matches.append(dict(source=source, scene=s['id'], role=roles.get(s['id']),
                                        sameCanvas=old['canvas'] == CANVAS))
        rows.append(dict(cell=cid, role=c['role'], family=c['family'], matches=matches))
        if any(m['source'] == 'canonical' and m['role'] == 'holdout' for m in matches):
            problems.append(f'{cid} is a twin of a canonical HOLDOUT scene')
        if c['role'] in ('validation', 'holdout') and matches:
            problems.append(f'{cid} ({c["role"]}) twins a scene read before: {matches}')
        if c['family'] == 'F' and not any(m['source'] == 'canonical' and m['scene'].startswith(c['bridge'] + '__')
                                          for m in matches):
            problems.append(f'{cid}: bridge does not twin its canonical scene {c["bridge"]}')
    if problems:
        raise ValueError('twin audit: ' + '; '.join(problems))
    return dict(schema='w42-twin-audit-1',
                compared=['relative geometry (kind, size, radius)', 'backdrop declaration'],
                ignoredConservatively=['offset/position', 'canvas', 'pose', 'state'],
                sources={s: hashlib.sha256(p.read_bytes()).hexdigest() for s, p in sources},
                rules=['no bed cell twins a canonical holdout scene',
                       'no validation or H cell twins any canonical, W34 or W39 scene',
                       'every F bridge twins its canonical scene'],
                holdoutPixelsOpened=False, rows=rows)


U_ITEMS = {
    'U1': 'the receded one-sided algebra; W reference 16-48 pt: C (S 32 both polarities on rrect-md, S 16 on '
          'capsule), D (delta 0 and 12 on capsule; 0, 12, 32 on rrect-md), B (P2 and P4 at pitch 64 beside 16)',
    'U2': "the receded narrow span law: B', with C's depth sweep as its flat-in-depth control",
    'U3': 'the footprint support and edge mode: D (inside and outside steps), both poses',
    'U4': 'the heavy kernel tails: C, D',
    'U5': 'T at 150-255 per endpoint and span: A',
    'U6': 'per-channel against on-luma knee, chroma kernel: E',
    'U7': "the active bleed: D (rrect-md and rrect-lg active steps), B' (spans >= 80, rrect-lg beside rrect-ml), "
          'C (S 32 on rrect-md)',
    'R1': "T before the fill composite: B's P5 and P3 at pitch 16 and 64 in both receded endpoints, with A's "
          'greys 160-255',
    'one k or two': "C's S 8 against S 32 on rrect-md, both poses",
    'depth': "C's depth sweep on rrect-md and rrect-lg",
    'rrect-lg': "B' on rrect-lg beside rrect-ml; C on rrect-lg",
    'units': "C's rrect-ml / rrect-lg pair (the canonical impulse)",
}

DEVIATIONS = [
    dict(item='1x rrect-lg row: "P1 at pitch 4, 8 and 16 on rrect-lg"',
         finding='P1 pitch 16 on rrect-lg is checkerboard (cell 16, 0/255) on rrect-lg: a semantic twin of the '
                 'canonical HOLDOUT scenes checkerboard__rrect-lg__rest and __inactive (scenes.json split). '
                 'Capturing and fitting it in W42 would read the canonical holdout\'s geometry before G3 '
                 '(clause 14; W39 declare-bed.py\'s twin rule).',
         declared='P1 pitch 32 on rrect-lg at 1x (bp-p1-c32-rrect-lg), a canonical probe twin (calibration '
                  'evidence under X34) that pairs 1x with the 2x B\' cell of the same id; the count stays 15.',
         status='substituted, flagged for the parent\'s ruling'),
    dict(item='C: "S 8 ... at the centre ... on rrect-lg" as a single square',
         finding='Background.swift draws impulses at (g/2 + kg, g/2 + mg). One patch in the 320x200 canvas needs '
                 'g >= 214, placing it at (g/2, g/2); rrect-lg\'s centre can only lie in [140,180] x [80,120] '
                 'with its box inside the canvas, and the single patch sits at (g/2, 200 - g/2) with g/2 >= 107: '
                 'x = g/2 >= 140 forces y = 200 - g/2 <= 60.',
         declared='c-s8-*-d80-rrect-lg uses the 64-pt grid (the canonical impulse\'s spacing) with rrect-lg '
                  'offset (0,+4): one patch exactly at the centre, neighbours 64 pt away (about 4 sigma_w at '
                  'memo E\'s 16-17 pt).',
         status='declared as a grid; the forward model renders the whole raster'),
    dict(item='C depth sweep and D outside steps in the active pose',
         finding='The patch 4 pt from the edge sits inside the declared active inner-refraction band '
                 '(InnerRefractionHeight min(s/4, 20) = 20 pt on rrect-md and rrect-lg), and D\'s steps 8 and '
                 '16 pt outside rrect-md lie within its declared outer-refraction reach (OuterRefractionHeight '
                 'max(16, s/5) = 19.2 pt, amount 24; memo D §3). LT models neither (memo E §5).',
         declared='the cells stand as the charter lists them; the reader must model or exclude refraction '
                  'there. Receded (RefractionOpacity 0) is unaffected.',
         status='flagged for the instrument stream'),
]


def main():
    bed = build()
    spec, passes = documents(bed)
    twin = audit(bed, spec)
    SCENES_FILE.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + '\n')
    web = {}
    for cid, c in bed.cells.items():
        comp = spec['components'][c['component']]
        web[cid] = 'web-plannable: a single shape, centred plus an integer offset' \
            if comp['kind'] in ('capsule', 'rrect') and 'position' not in comp else 'native-only'
    counts = {k: dict(glass=len(p['cells']), references=len(p['references']),
                      byFamily={f: sum(1 for c in p['cells'] if bed.cells[c]['family'] == f)
                                for f in ('A', 'B', "B'", 'C', 'D', 'E', 'F', 'H')},
                      byRole={r: sum(1 for c in p['cells'] if bed.cells[c]['role'] == r) for r in ROLE_ORDER})
              for k, p in passes.items()}
    companion = dict(
        schema='w42-bed-1',
        charter='docs/doperpowers/specs/2026-09-29-w42-body-spatial-structure.md v2.1 (main 0736ed64)',
        scenesFile=str(SCENES_FILE.relative_to(ROOT)),
        canvas=CANVAS,
        levels=dict(patchAndStep=[LO, HI], polarity=dict(hi='208 patch on 48', lo='48 patch on 208'),
                    step=dict(lohi='48 left of the step, 208 right', hilo='208 left, 48 right'),
                    isoluminant=dict(luma='Rec.709 on codes', value=128, pairs=E_PAIRS)),
        singlePatchGeometry={str(g): dict(patchCentre=list(p)) for g, p in SINGLE.items()},
        passes=passes, counts=counts, sentinels=list(SENTINELS),
        runs=dict(normal=7, sentinel=3, referencesIn='run 1 of each pass'),
        cells={cid: {k: v for k, v in c.items() if v not in (None, [], ())} for cid, c in sorted(bed.cells.items())},
        roles={r: sorted(c for c, x in bed.cells.items() if x['role'] == r) for r in ROLE_ORDER},
        validationAxes={cid: c['note'] for cid, c in sorted(bed.cells.items()) if c['role'] == 'validation'},
        uItems=U_ITEMS, charterDeviations=DEVIATIONS, webPlacement=web,
        dumpList={k: sorted(f'{c}__rest' for c in p['cells']) for k, p in passes.items()},
    )
    (HERE / 'bed.json').write_text(json.dumps(companion, indent=2, ensure_ascii=False) + '\n')
    (HERE / 'twin-audit.json').write_text(json.dumps(twin, indent=2, ensure_ascii=False) + '\n')
    pins = {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
            for name in ('scenes-w42-body.json', 'bed.json', 'twin-audit.json')}
    (HERE / 'pins.json').write_text(json.dumps(pins, indent=2) + '\n')
    print(json.dumps(dict(scenes=len(spec['scenes']), backgrounds=len(spec['backgrounds']),
                          components=len(spec['components']),
                          split={r: len(v) for r, v in spec['split'].items()},
                          passes={k: (v['glass'], v['references']) for k, v in counts.items()}), indent=1))


if __name__ == '__main__':
    main()
