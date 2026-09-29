"""W42 G0 instrument: the declared families as forward-model configurations, with their parameter counts
(charter Design, "The rival families", MARKED: declared with their counts in G0, before any pixel).

Counts are per endpoint unless the layout shares a parameter across endpoints; w is fixed at 0.5 throughout
(memo D: Normal is the slider, attested 0.5). Everything not counted is declared: the radii 5 and 8, the
opacity law o(s, d, pose), R_fp and its margin, the 0.8-device-px floor (1.6 on rrect-lg), the edge modes
and native T in identification.

The scale k is declared at three nested levels (the parent's brief), plus the charter's pose-shared rival
between the first two:
  'k@global'    one k across all four endpoints (the most restricted; a renderer's radius-to-sigma mapping
                is a constant, so the parent expects it primary): 1 + 4 lam = 5 parameters in total;
  'k@scheme'    one k per scheme, shared by both poses (the rival "k shared across poses"): 2 + 4 = 6;
  'k@endpoint'  one k per endpoint shared by both radii (memo E's LT-1k): 4 x 2 = 8;
  'k2@endpoint' a separate k for the narrow and the wide radius (LT-2k): 4 x 3 = 12.
"""
from forward import Family

K_BOUNDS = (0.8, 4.0)
LAYOUTS = {
    'k@global': [('k', 'global')],
    'k@scheme': [('k', 'scheme')],
    'k@endpoint': [('k', 'endpoint')],
    'k2@endpoint': [('k_n', 'endpoint'), ('k_w', 'endpoint')],
}
FREE_SPANS = (64, 80, 96, 128, 160)


def free_layout(pose):
    return [('k', 'endpoint')] + [(f'sn_{pose}_{s}', 'endpoint') for s in FREE_SPANS]


# name: (Family, extra outer parameters beyond k [(name, bounds)], count per endpoint, what differs, status)
FAMILIES = {
    'LT': (Family('LT'), [], 2, 'the primary family: k and lam; everything else declared', 'primary'),
    'LT-2k': (Family('LT-2k'), [], 3, 'a separate scale for each radius (k_n, k_w)', 'rival'),
    'free-sn': (Family('free-sn', narrow='free'), [], 2 + len(FREE_SPANS),
                'sigma_n a free span law per pose (5 ordinates at s <= 64, 80, 96, 128, 160; flat in depth; '
                'linear in s between, clamped outside) instead of k * 5 * o', 'rival'),
    'R1': (Family('R1', order='before'), [], 2, 'T applied to C and W before the fill composite', 'rival'),
    'W-shape': (Family('W-shape', support='shape'), [('mu', (-8.0, 40.0))], 3,
                "W's support the rounded shape expanded by a margin mu (pt), normalised", 'rival'),
    'W-canvas': (Family('W-canvas', support='canvas', edge='clamp'), [], 2,
                 "W (and C) on the whole canvas, clamp-to-edge at the canvas: the support rival memo C's "
                 'active capsule preferred', 'rival'),
    'W-tails': (Family('W-tails', wkind='tails'), [('s2', (17.0, 80.0)), ('a', (0.0, 0.6))], 4,
                'W a mixture of two Gaussians: (1 - a) G(k * 8) + a G(s2)', 'rival'),
    'K2': (Family('K2', fills=2), [('sk', (2.0, 40.0))], 3,
           'two fills: the knee against Wk = G(sk) * S, the normal mix toward W = G(k * 8) * S', 'rival'),
    'C-linear': (Family('C-linear', space_c='lin'), [], 2,
                 'the narrow term averaged in linear light, W encoded (a discrete choice)', 'rival'),
    'knee-luma': (Family('knee-luma', knee='luma'), [], 2,
                  'the hinge decided on encoded luma and applied to the whole colour, against per channel',
                  'rival'),
    'LT+bleed': (Family('LT+bleed', bleed='shared'), [], 2,
                 "the dump's active bleed layer: radius k * 0.35 s, opacity 0.5t light / 0.8t dark (s > 64); "
                 'its matrix enters as a structural weight beta = ob (white - black) / (1 - ob + ob (white - '
                 'black)), its affine part absorbed by native T read on uniform greys', 'rival'),
    'LT+bleed-own': (Family('LT+bleed-own', bleed='own'), [('k_b', K_BOUNDS)], 3,
                     'as LT+bleed with the bleed radius on its own scale k_b', 'rival'),
    'edge-swap': (Family('edge-swap', edge='swap'), [], 2,
                  "R_fp's edge mode swapped (normalised when active, clamp when receded): memo E's 0.23-code "
                  'dark-active choice', 'rival (discrete)'),
    'null-mix': (Family('null-mix', narrow='mix'), [], 2,
                 'C = (1 - o) S + o G(k * 5) * S, ruling 9 framing (REJECTED null, memo E §2c)', 'null'),
    'null-texel': (Family('null-texel', units='texel'), [], 2, 'radii in backdrop texels (REJECTED null)', 'null'),
    'null-dev': (Family('null-dev', units='dev'), [], 2, 'radii in device px (REJECTED null)', 'null'),
    'null-R2': (Family('null-R2', order='blurlast'), [], 2,
                'the fill on the sharp capture, the narrow blur last (REJECTED null, memo E §3b)', 'null'),
    'null-boxfloor': (Family('null-boxfloor', floor='box'), [], 2,
                      'a literal f x f box decimation of the capture instead of the 0.8-dev floor (REJECTED null)',
                      'null'),
}

# The configurations the proofs render as truths: memo E's readings (k per endpoint, LT-1k) and memo C's knee.
TRUTH_K = {'light-rest': 1.983, 'light-inactive': 2.035, 'dark-rest': 2.094, 'dark-inactive': 2.074}
TRUTH_LAM = {'light-rest': 0.88, 'light-inactive': 0.80, 'dark-rest': 0.90, 'dark-inactive': 0.80}
TRUTH_EXTRA = {
    'LT-2k': {'k_n': 1.75, 'k_w': 2.10},
    'free-sn': {'rest': {64: 0.3, 80: 1.5, 96: 2.2, 128: 4.0, 160: 4.5},
                'inactive': {64: 4.25, 80: 4.8, 96: 5.4, 128: 6.5, 160: 7.5}},
    'W-shape': {'mu': 4.0},
    'W-tails': {'s2': 40.0, 'a': 0.25},
    'K2': {'sk': 12.0},
    'LT+bleed-own': {'k_b': 2.0},
}
