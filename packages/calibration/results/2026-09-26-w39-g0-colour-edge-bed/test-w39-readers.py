#!/usr/bin/env python3.12
"""w39_readers: synthetic contracts, then W37's numbers reproduced on the W34 archive.

The archive half opens W34 calibration cells only, through W34's guarded
`wave.Reader` (default roles); the refusal test proves a holdout-role cell is
refused before any payload opens. No W34 holdout directory is named here.
"""
import json
import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import w39_readers as R

K = 0.5522847498  # circular-arc cubic handle; a stand-in continuous path, not Apple's


def rrect_elements(w, h, r):
    """A rounded-rect CGPath element list (lines + cubics) in the harness's export form."""
    e = [dict(type=0, points=[[r, 0]])]
    line = lambda x, y: e.append(dict(type=1, points=[[x, y]]))
    cubic = lambda *p: e.append(dict(type=3, points=[list(q) for q in p]))
    if w - r > r: line(w - r, 0)
    cubic((w - r + K * r, 0), (w, r - K * r), (w, r))
    if h - r > r: line(w, h - r)
    cubic((w, h - r + K * r), (w - r + K * r, h), (w - r, h))
    if w - r > r: line(r, h)
    cubic((r - K * r, h), (0, h - r + K * r), (0, h - r))
    if h - r > r: line(0, r)
    cubic((0, r - K * r), (r - K * r, 0), (r, 0))
    e.append(dict(type=4, points=[]))
    return e


def single(kind, size, origin, elements=(), opaque=False, **extra):
    return dict(kind=kind, size=list(size), **extra, suppliedPaths=[dict(
        kind=kind, frameOrigin=list(origin), rect=[0, 0, *size], opaque=opaque, elements=list(elements))])


def area_image(shape, scale, hw, inside, outside, quad=16):
    """Supersampled coverage render of a circular stadium: an exact-enough raster."""
    h, w = hw
    x0, y0, x1, y1 = shape.rect(scale); r = min(shape.size) / 2 * scale
    u = (np.arange(quad) + .5) / quad
    y, x = np.mgrid[:h, :w].astype(float)
    cover = np.zeros(hw)
    for dy in u:
        for dx in u: cover += R.I.stadium(x + dx, y + dy, [x0, y0, x1, y1], r)[0] <= 0
    cover = np.repeat((cover / (quad * quad))[..., None], 3, -1)
    return np.rint(cover * inside + (1 - cover) * outside).astype(np.uint8)


class Synthetic(unittest.TestCase):
    def test_bins_are_exhaustive_and_absent_sides_explicit(self):
        for scale in [1, 2]:
            shapes = R.shapes_of(single('capsule-circular', (120, 44), (100, 118)))
            geo = R.geometry((280 * scale, 320 * scale), shapes, scale)
            bins, labels = R.edge_bins(geo)
            shells = [b for b in bins if b['part'] != 'boundary']
            self.assertEqual(len(shells), 18 * scale * 20)
            self.assertEqual({b['shell'] for b in shells}, set(range(-14 * scale, 4 * scale)))
            for b in shells:
                if b['part'] == 'straight' and b['side'] in ('left', 'right'):
                    self.assertEqual((b['status'], b['pixels'], b['reason']), ('UNMEASURED', 0, 'absent bin'))
                if b['part'] == 'straight' and b['side'] in ('top', 'bottom'):
                    self.assertEqual(b['pixels'], 76 * scale)
            # Integer origin: nothing straddles the path, so the boundary stratum is empty.
            self.assertTrue(all(b['pixels'] == 0 for b in bins if b['part'] == 'boundary'))
            self.assertLess(labels.max(), len(bins))

    def test_depth_labels_match_w37(self):
        geo = R.geometry((560, 640), R.shapes_of(single('capsule-circular', (200, 44), (60, 118))), 2)
        depth = {b['shell']: b['depthCss'] for b in R.edge_bins(geo)[0] if b['part'] == 'straight'}
        self.assertEqual((depth[-12], depth[-11], depth[0], depth[7]), (5.75, 5.25, -.25, -3.75))

    def test_fractional_origin_moves_pixels_into_the_boundary_stratum(self):
        geo = R.geometry((280, 320), R.shapes_of(single('capsule-circular', (120, 44), (100, 118.25))), 1)
        bins, _ = R.edge_bins(geo)
        top = {(b['part'], b['shell']): b for b in bins if b['side'] == 'top'}
        self.assertEqual(top[('boundary', None)]['pixels'], 76)
        # Shells are indexed by the pixel centre's distance: the straddling row (d=-0.25)
        # leaves shell -1 empty and explicit, and the first whole row (d=-1.25) is shell -2.
        self.assertEqual((top[('straight', -1)]['pixels'], top[('straight', -1)]['status']), (0, 'UNMEASURED'))
        self.assertEqual(top[('straight', -2)]['pixels'], 76)

    def test_deep_and_population_are_unmeasured_not_dropped(self):
        geo = R.geometry((40, 40), R.shapes_of(single('capsule-circular', (10, 6), (15, 17))), 1)
        self.assertEqual(R.deep_body(np.zeros((40, 40, 3)), geo)['status'], 'UNMEASURED')
        read = R.read_bins(np.zeros((40, 40, 3)), *R.edge_bins(geo), None)
        self.assertTrue(any(r['status'] == 'UNMEASURED' and r['pixels'] > 0 for r in read))
        pairs = R.paired_top_bottom(read)
        self.assertTrue(all(p['status'] == 'UNMEASURED' or p['differenceRGB'] is not None for p in pairs))

    def test_top_bottom_pair_reads_a_signed_difference_at_equal_depth(self):
        shapes = R.shapes_of(single('capsule-circular', (200, 44), (60, 118)))
        geo = R.geometry((280, 320), shapes, 1)
        img = np.full((280, 320, 3), 253.)
        img[(geo.d < 0) & (geo.ny < 0) & (geo.d > -8)] = 250
        read = R.read_bins(img, *R.edge_bins(geo), R.deep_body(img, geo))
        pair = next(p for p in R.paired_top_bottom(read) if p['shell'] == -6)
        self.assertEqual((pair['depthCss'], pair['pixels'], pair['meanRGB']), (5.5, [156, 156], [[250.] * 3, [253.] * 3]))
        self.assertEqual(pair['differenceRGB'], [-3.] * 3)

    def test_column_members_have_their_own_body_and_bins(self):
        comp = dict(kind='column', items=[dict(kind='capsule-circular', size=[120, 44]),
                                          dict(kind='capsule-circular', size=[120, 44])],
                    suppliedPaths=[dict(kind='capsule-circular', frameOrigin=[100, 48], rect=[0, 0, 120, 44],
                                        opaque=False, elements=[]),
                                   dict(kind='capsule-circular', frameOrigin=[100, 188], rect=[0, 0, 120, 44],
                                        opaque=False, elements=[])])
        geo = R.geometry((280, 320), R.shapes_of(comp), 1)
        img = np.full((280, 320, 3), 128.)
        img[(geo.member == 0) & (geo.d < 0)] = 200; img[(geo.member == 1) & (geo.d < 0)] = 60
        self.assertEqual(R.deep_body(img, geo, 0)['medianRGB'], [200.] * 3)
        self.assertEqual(R.deep_body(img, geo, 1)['medianRGB'], [60.] * 3)
        for m in [0, 1]:
            top = [b for b in R.edge_bins(geo, m)[0] if b['part'] == 'straight' and b['side'] == 'top']
            self.assertTrue(all(b['pixels'] == 76 for b in top))

    def test_path_solved_rrect_straights_and_apex(self):
        for scale in [1, 2]:
            shape = R.shapes_of(single('rrect', (120, 64), (100, 108), rrect_elements(120, 64, 22), radius=22))[0]
            runs = R.straight_extents(shape, scale)
            self.assertEqual(runs['top'], (122 * scale, 198 * scale))
            self.assertEqual(runs['left'], (130 * scale, 150 * scale))
            geo = R.geometry((280 * scale, 320 * scale), [shape], scale)
            # On a straight the supplied-path distance is exact.
            self.assertAlmostEqual(float(geo.d[108 * scale + 3, 160 * scale]), -3.5, places=12)
            stadium = R.I.stadium(np.array([160 * scale + .5]), np.array([108 * scale + 3.5]),
                                  shape.rect(scale), 22 * scale)[0]
            self.assertAlmostEqual(float(stadium[0]), -3.5, places=12)
        # A 44-high radius-22 path has no straight end: the transect falls to the apex band.
        shape = R.shapes_of(single('rrect', (120, 44), (100, 118), rrect_elements(120, 44, 22), radius=22))[0]
        p = R.straight_profile(np.zeros((280, 320, 3), np.uint8), shape, 1, 'right')
        self.assertEqual((p['mode'], p['status'], p['band'], p['inward'], p['pathEdge']),
                         ('apex', 'measured', [138, 139, 140, 141], -1, 220.0))
        self.assertEqual(p['raw'].shape, (4, len(p['coords']), 3))

    def test_empty_band_is_unmeasured(self):
        shape = R.shapes_of(single('capsule-circular', (120, 44), (100, 118)))[0]
        p = R.straight_profile(np.zeros((280, 320, 3), np.uint8), shape, 1, 'top', inner_css=60)
        self.assertEqual(p['mode'], 'apex')
        self.assertEqual(p['status'], 'measured')
        tiny = R.Shape('rrect', (4., 4.), (10., 10.), tuple(json.dumps(e, sort_keys=True) for e in
                        [dict(type=0, points=[[2, 0]]), dict(type=3, points=[[4, 0], [4, 4], [2, 4]]),
                         dict(type=3, points=[[0, 4], [0, 0], [2, 0]]), dict(type=4, points=[])]))
        q = R.straight_profile(np.zeros((40, 40, 3), np.uint8), tiny, 1, 'left')
        self.assertIn(q['status'], ('measured', 'UNMEASURED'))
        if q['status'] == 'UNMEASURED': self.assertIsNone(q['raw'])

    def test_coverage_recovers_a_subpixel_edge_and_phase_states(self):
        states = []
        for scale in [1, 2]:
            for phase in [0, .25, .5, .75]:
                w = 120 + phase / scale
                shape = R.shapes_of(single('capsule-circular', (w, 44), (100, 118)))[0]
                img = area_image(shape, scale, (280 * scale, 320 * scale), 0., 255.)
                alpha = R.opaque_coverage(img, 255., 0.)
                far = R.coverage_profile(alpha, shape, scale, 'right')
                near = R.straight_profile(img, shape, scale, 'left')
                states.append((scale, phase, far['offset'], near['raw'].tobytes(),
                               R.straight_profile(img, shape, scale, 'right')['raw'].tobytes()))
                self.assertEqual(far['pathEdge'], 220 * scale + phase)
        for scale in [1, 2]:
            s = [x for x in states if x[0] == scale]
            self.assertEqual(len({x[3] for x in s}), 1)          # near edge byte-identical
            self.assertEqual(len({x[4] for x in s}), 4)          # far edge four states
            offsets = [x[2] for x in s]
            self.assertLess(max(offsets) - min(offsets), .02)   # the apex reading is phase-invariant

    def test_calibrate_opaque_uses_its_own_levels(self):
        shape = R.shapes_of(single('capsule-circular', (120, 44), (100, 118), opaque=True))[0]
        img = area_image(shape, 1, (280, 320), 255., 128.)
        geo = R.geometry((280, 320), [shape], 1)
        cal = R.calibrate_opaque(img, geo)
        self.assertEqual(cal['fillRGB'], [255.] * 3)
        self.assertEqual(cal['background'].tolist(), [128.] * 3)

    def test_ramp_reproduces_w37_consistency_check(self):
        # §5.182 §1: width-1.4 ramp, amplitude 37.6 -> 24.171429 at 1x, 17.457143 / 30.885714 at 2x,
        # the 1x integral exactly the 2x pair's mean.
        one = R.integrate_ramp([118], 118, 1, 1.4, 37.6)
        two = R.integrate_ramp([237, 236], 236, 2, 1.4, 37.6)
        self.assertEqual(np.round(one, 6).tolist(), [24.171429])
        self.assertEqual(np.round(two, 6).tolist(), [17.457143, 30.885714])
        self.assertAlmostEqual(float(one[0]), float(two.mean()), places=12)
        down = R.integrate_ramp([161], 162, 1, 1.4, 37.6, inward=-1)
        self.assertAlmostEqual(float(down[0]), float(one[0]), places=12)
        g = R.area_average([0, 1], .5, 1, lambda u: (u >= 0).astype(float), 1)
        self.assertEqual(g.tolist(), [.5, 1.])

    def test_shapes_refuse_disagreement(self):
        with self.assertRaises(ValueError): R.shapes_of(dict(kind='capsule-circular', size=[120, 44]))
        bad = single('capsule-circular', (120, 44), (100, 118)); bad['size'] = [121, 44]
        with self.assertRaises(ValueError): R.shapes_of(bad)
        self.assertEqual(R.shapes_of(dict(kind='none')), [])

    def test_analyse_is_deterministic_on_read_only_frames_and_json_metadata(self):
        comp = single('capsule-circular', (120, 44), (100, 118))
        shape = R.shapes_of(comp)[0]
        rgb = area_image(shape, 1, (280, 320), 190., 128.)
        opaque = area_image(shape, 1, (280, 320), 255., 128.)
        bg = np.full_like(rgb, 128)
        frozen = lambda a: np.frombuffer(a.tobytes(), np.uint8).reshape(a.shape)
        oc = single('capsule-circular', (120, 44), (100, 118), opaque=True, fillSRGB=[255, 255, 255])
        payload = dict(rgb=rgb, noGlass=bg, opaque=opaque, opaqueNoGlass=bg, component=comp, scale=1,
                       scheme='light', pose='active', backgroundKind='solid', sceneId='x', unknownKey=1,
                       dependencies=dict(opaque=dict(sceneId='x-opaque', component=oc),
                                         opaqueNoGlass=dict(sceneId='x-ref', component=dict(kind='none'))))
        again = dict(payload, rgb=frozen(rgb), noGlass=frozen(bg), opaque=frozen(opaque), opaqueNoGlass=frozen(bg),
                     component=json.loads(json.dumps(comp)), dependencies=json.loads(json.dumps(payload['dependencies'])))
        a, b = R.analyse(payload), R.analyse(again)
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))
        self.assertEqual(a['members'][0]['deep']['medianRGB'], [190.] * 3)
        self.assertEqual((a['members'][0]['coverage']['source'], a['members'][0]['coverage']['controlSceneId'],
                          a['members'][0]['coverage']['controlReferenceSceneId']),
                         ('opaque control', 'x-opaque', 'x-ref'))
        # A native-only opaque cell (noGlass, no opaque) and a none reference.
        o = R.analyse(dict(rgb=opaque, noGlass=bg, opaque=None, component=oc, scale=1))
        self.assertEqual(o['members'][0]['coverage']['source'], 'cell')
        self.assertNotIn('deep', o['members'][0])
        n = R.analyse(dict(rgb=bg, component=dict(kind='none'), scale=1))
        self.assertEqual(n['reference']['medianRGB'], [128.] * 3)


    def test_borrowed_control_is_read_on_its_own_geometry_and_reference(self):
        # Review P1-3: a colour glass cell borrows a white-over-grey-128 control whose
        # attested origin differs from the glass's. Its coverage must equal the
        # control's own native-only reading, whatever the glass cell's background.
        comp = single('capsule-circular', (120, 44), (100, 118))
        oc = single('capsule-circular', (120, 44), (100.25, 118.5), opaque=True, fillSRGB=[255, 255, 255])
        colour = np.broadcast_to(np.array([69, 61, 63], np.uint8), (280, 320, 3)).copy()
        grey = np.full((280, 320, 3), 128, np.uint8)
        rgb = area_image(R.shapes_of(comp)[0], 1, (280, 320), 190., np.array([69., 61., 63.]))
        control = area_image(R.shapes_of(oc)[0], 1, (280, 320), 255., 128.)
        own = R.analyse(dict(rgb=control, noGlass=grey, component=oc, scale=1))['members'][0]['coverage']
        deps = dict(opaque=dict(sceneId='g-opaque', component=oc), opaqueNoGlass=dict(sceneId='g-ref'))
        glass = R.analyse(dict(rgb=rgb, noGlass=colour, opaque=control, opaqueNoGlass=grey, component=comp,
                               scale=1, dependencies=deps))['members'][0]['coverage']
        for key in ('fillRGB', 'backgroundRGB', 'bins', 'edges', 'frameOriginCss'):
            self.assertEqual(glass[key], own[key], key)
        self.assertEqual(glass['backgroundRGB'], [128.] * 3)
        outside = [b['alpha'] for b in glass['bins'] if b['part'] != 'boundary' and b['shell'] >= 0
                   and b['alpha'] is not None]
        self.assertTrue(outside and all(a == 0 for a in outside))
        # No reference and no component: never the dependent's.
        without = R.analyse(dict(rgb=rgb, noGlass=colour, opaque=control, component=comp, scale=1,
                                 dependencies=dict(opaque=dict(sceneId='g-opaque', component=oc))))
        self.assertEqual(without['members'][0]['coverage']['backgroundRGB'], [128.] * 3)
        with self.assertRaisesRegex(ValueError, 'own component'):
            R.analyse(dict(rgb=rgb, noGlass=colour, opaque=control, opaqueNoGlass=grey, component=comp, scale=1))
        with self.assertRaisesRegex(ValueError, 'not opaque'):
            R.analyse(dict(rgb=rgb, opaque=control, component=comp, scale=1,
                           dependencies=dict(opaque=dict(component=comp))))


class HarnessPaths(unittest.TestCase):
    """The harness's exported preflight paths (radius-22 continuous rrects), read as attested."""

    def test_preflight_bands_are_phase_invariant_and_edges_attested(self):
        path = HERE / 'preflight-supplied-paths.json'
        if not path.exists(): self.skipTest('no exported preflight paths')
        components = json.loads(path.read_text())['components']
        for scale in [1, 2]:
            img = np.zeros((280 * scale, 320 * scale, 3), np.uint8)
            read = lambda name, side: R.straight_profile(
                img, R.shape_from_supplied(components[f'preflight-{scale}x-{name}'][0]), scale, side)
            for axis, near, far, grow in [('x', 'left', 'right', 0), ('y', 'top', 'bottom', 1)]:
                phases = ['zero'] + [f'{axis}{i}' for i in (1, 2, 3)]
                for side in (near, far):
                    bands = {tuple(read(n, side)['band']) for n in phases}
                    self.assertEqual(len(bands), 1, (scale, axis, side))
                    self.assertEqual(read('zero', side)['status'], 'measured')
                self.assertEqual({read(n, near)['pathEdge'] for n in phases}, {(100., 118.)[grow] * scale})
                edges = [read(n, far)['pathEdge'] for n in phases]
                self.assertEqual(edges, [((220., 162.)[grow] + i / 4 / scale) * scale for i in range(4)])
            self.assertEqual(read('zero', 'right')['mode'], 'apex')
            self.assertEqual(read('zero', 'bottom')['mode'], 'straight')


class W34Archive(unittest.TestCase):
    """W37's reported numbers, to the code, from W34 calibration cells."""

    @classmethod
    def setUpClass(cls): cls.wave = R.w34_wave()

    def cell(self, profile, scene):
        p = R.w34_payload(profile + '/' + scene, self.wave)
        self.assertEqual(p['role'], 'calibration')
        return p

    def test_holdout_is_refused_before_any_payload(self):
        with self.assertRaises(PermissionError):
            R.w34_payload('apple-macos-27.0-1x-light-standard-glass0.5/grey-128__circular-160__rest', self.wave)

    def test_grey255_witness_250_253(self):
        for scale, shells, pixels in [(1, [-6], 156), (2, [-12, -11], 312)]:
            p = self.cell(f'apple-macos-27.0-{scale}x-light-standard-glass0.5', 'grey-255__circular-200__rest')
            a = R.analyse(p); m = a['members'][0]
            self.assertEqual(m['deep']['medianRGB'], [253.] * 3)
            pairs = {q['shell']: q for q in m['topBottom']}
            for sh in shells:
                q = pairs[sh]
                self.assertEqual((q['status'], q['pixels'], q['meanRGB']), ('measured', [pixels] * 2, [[250.] * 3, [253.] * 3]))
            # The same rows under W37's recorded alignment translation.
            geo = R.geometry(p['rgb'].shape[:2], R.shapes_of(p['component']), p['scale'], p['translationDevicePx'])
            read = R.read_bins(p['rgb'], *R.edge_bins(geo), R.deep_body(p['rgb'], geo))
            again = {q['shell']: q for q in R.paired_top_bottom(read)}
            for sh in shells: self.assertEqual(again[sh]['meanRGB'], pairs[sh]['meanRGB'])
            print(f'\n  grey-255 circular-200 light active {scale}x top/bottom by depth (CSS px):')
            for q in m['topBottom']:
                if q['shell'] < 0 and q['status'] == 'measured':
                    print(f"    {q['depthCss']:5.2f}  top {q['meanRGB'][0]}  bottom {q['meanRGB'][1]}  n={q['pixels'][0]}")

    def test_w37_record_matches(self):
        record = json.loads((HERE.parent / '2026-09-25-w37-g0b-edge-identification/form-obstruction.json').read_text())
        for w in record['witnesses']:
            profile, scene = w['cell'].split('/')
            m = R.analyse(self.cell(profile, scene))['members'][0]
            bins = {(b['side'], b['shell']): b for b in m['bins'] if b['part'] == 'straight'}
            for pair in w['pair']:
                b = bins[(pair['side'], pair['shell'])]
                self.assertEqual((b['pixels'], b['meanRGB'], -b['depthCss']),
                                 (pair['pixels'], pair['nativeRGB'], pair['distanceCss']))

    def test_grey128_top_rows(self):
        # §5.181 §4: identical top rows across circular120, circular200, continuous120 and the
        # radius-12 rectangle: 24/30 light/dark at 1x; 18,31 / 22,39 G at 2x.
        expected = {('light', 1): [24], ('dark', 1): [30], ('light', 2): [18, 31], ('dark', 2): [22, 39]}
        deep = {'light': 195., 'dark': 134.}
        for (scheme, scale), rows in expected.items():
            for scene in ['circular-120', 'circular-200', 'capsule-button', 'rectangle-120']:
                p = self.cell(f'apple-macos-27.0-{scale}x-{scheme}-standard-glass0.5', f'grey-128__{scene}__rest')
                m = R.analyse(p)['members'][0]
                self.assertEqual(m['deep']['medianRGB'], [deep[scheme]] * 3)
                top = {b['shell']: b for b in m['bins'] if b['part'] == 'straight' and b['side'] == 'top'}
                got = [top[sh]['excessRGB'][1] for sh in range(-scale, 0)]
                self.assertEqual(got, rows, (scheme, scale, scene))
                self.assertTrue(all(top[sh]['status'] == 'measured' for sh in range(-scale, 0)))


if __name__ == '__main__':
    unittest.main(verbosity=2)
