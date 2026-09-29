"""W42 G0 instrument: the output transfer T every forward model ends in and every reader inverts.

Identification inverts through NATIVE T measured on family A per endpoint (charter X35). Family A does not
exist until G1, so the clause-2 proofs use a stand-in with the right shape: memo C's T table (native deep
medians at span 44 from the W34/W39 archives plus canonical solids, with its span corrections and its dark
trust limits), copied verbatim from `~/vitrea-w42/grounding/probe/reader.py` (SHA-256 a5d6b1cb…, listed in the
grounding's scratch manifest). It is a KNOWN function in the proofs: a synthetic render goes through it and a
reader inverts it, so what the proofs measure is the reader, not the table. G2 replaces it with family A's
curve by constructing `TableT` from the measured ordinates; nothing else changes.

`SrgbAffineT` is vitrea's own transfer for the known-kernel control (proof 3): the shipped body is affine in
LINEAR light and then encoded (memo B §1), so a reader of vitrea's captures inverts the sRGB encode and fits
the affine in linear light.
"""
import numpy as np


def srgb_to_lin(c):
    """Encoded codes 0..255 -> linear light 0..1."""
    c = np.asarray(c, dtype=np.float64) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((np.maximum(c, 0) + 0.055) / 1.055) ** 2.4)


def lin_to_srgb(v):
    """Linear light 0..1 -> encoded codes 0..255 (unclipped above 1 is clipped)."""
    v = np.clip(np.asarray(v, dtype=np.float64), 0, 1)
    return 255.0 * np.where(v <= 0.0031308, 12.92 * v, 1.055 * np.power(v, 1 / 2.4) - 0.055)


# memo C's table (probe/reader.py T_TAB, T_SPAN, TRUST), verbatim.
T_TAB = {
    'light-inactive': [(0, 133), (28.1, 145.1), (32, 147), (40, 150), (56, 157), (64, 161), (69, 163), (72, 164),
                       (88, 171), (96, 175), (104, 178), (128, 188), (150, 197), (160, 202), (242.4, 235.3),
                       (255, 240)],
    'light-rest': [(0, 132), (28.1, 146.1), (32, 148), (40, 152), (56, 160), (64, 164), (72, 168), (88, 176),
                   (96, 179), (104, 183), (128, 195), (150, 205), (160, 210), (242.4, 247.4), (255, 253)],
    'dark-rest': [(0, 32), (28.1, 58.2), (32, 62), (40, 69), (56, 83), (64, 89), (72, 96), (88, 108), (96, 113),
                  (104, 119), (128, 134), (150, 146), (160, 151), (255, 184)],
    'dark-inactive': [(0, 20), (28.1, 48.2), (32, 52), (40, 60), (56, 74), (64, 81), (72, 87), (88, 100),
                      (96, 106), (104, 111), (128, 127), (140, 135), (150, 140), (160, 146), (242.4, 177.4),
                      (255, 180)],
}
T_SPAN = {
    'light-rest': {32: [(0, -1), (28.1, -1), (69, -1.5), (242.4, -2), (255, -2)],
                   96: [(0, 2), (28.1, 2), (69, 2.5), (128, 3), (242.4, 1), (255, 1)],
                   128: [(0, 4), (28.1, 4), (69, 5), (242.4, 2), (255, 2)],
                   160: [(0, 5), (28.1, 5), (69, 6.5), (128, 6), (242.4, 3), (255, 3)]},
    'dark-rest': {32: [(0, 0), (28.1, 0), (69, -1.4), (242.4, 0.7), (255, 0.7)],
                  96: [(0, -1.1), (28.1, -1.1), (69, -5.4), (128, -13), (255, -50)],
                  128: [(0, -3.1), (28.1, -3.1), (69, -7.4), (128, -15), (242.4, -53), (255, -54)],
                  160: [(0, -5), (28.1, -5), (69, -9.4), (128, -16), (242.4, -55.4), (255, -57)]},
    'dark-inactive': {96: [(0, -0.1), (28.1, -0.1), (69, -3.75), (128, -13), (242.4, -51), (255, -53)],
                      128: [(0, -0.1), (28.1, -0.1), (69, -4.25), (140, -20.7), (242.4, -58.3), (255, -60)],
                      160: [(0, -0.1), (28.1, -0.1), (69, -4.75), (140, -20.7), (242.4, -58.3), (255, -60)]},
}
TRUST = {'dark-rest': {96: 128, 128: 128, 160: 128}, 'dark-inactive': {96: 128, 128: 140, 160: 140}}
T_SPANS = (32, 44, 96, 128, 160)


class TableT:
    """A monotone piecewise-linear transfer M (encoded input codes) -> y (output codes), with its inverse, its
    slope and the input limit above which it is not trusted (a clamp that carries no information)."""

    def __init__(self, xs, ys, trust_below=None, name=''):
        self.xs, self.ys = np.asarray(xs, float), np.asarray(ys, float)
        self.trust_below = trust_below
        self.name = name
        self._slope = np.diff(self.ys) / np.diff(self.xs)

    def __call__(self, M):
        return np.interp(M, self.xs, self.ys)

    def inv(self, y):
        return np.interp(y, self.ys, self.xs)

    def slope(self, M):
        i = np.clip(np.searchsorted(self.xs, M, side='right') - 1, 0, len(self._slope) - 1)
        return self._slope[i]

    def trusted(self, y):
        """Pixels whose inverted input lies where T is measured and invertible."""
        if self.trust_below is None:
            return np.ones(np.shape(y), bool)
        return self.inv(y) < self.trust_below


def memo_c_T(endpoint, span):
    """memo C's native-T stand-in for an endpoint ('light-rest', 'light-inactive', 'dark-rest',
    'dark-inactive') at a surface short side `span`, snapped to the nearest tabulated span as memo C did."""
    tspan = min(T_SPANS, key=lambda v: abs(v - span))
    xs, ys = np.array(T_TAB[endpoint], float).T
    if endpoint in T_SPAN and tspan in T_SPAN[endpoint]:
        cx, cy = np.array(T_SPAN[endpoint][tspan], float).T
        ys = ys + np.interp(xs, cx, cy)
    trust = TRUST.get(endpoint, {}).get(tspan)
    return TableT(xs, ys, trust, name=f'memoC:{endpoint}@{tspan}')


class SrgbAffineT:
    """vitrea's transfer for the known-kernel control: y = enc(a + b * lin(M)) with (a, b) free per cell.
    `fit_affine` projects them out by least squares in linear light (variable projection), as memo C's
    `fit_vit` did."""
    name = 'srgb-affine'
    trust_below = None

    @staticmethod
    def project(M_lin, y):
        X = np.stack([np.ones_like(M_lin), M_lin], 1)
        cf, *_ = np.linalg.lstsq(X, srgb_to_lin(y), rcond=None)
        return lin_to_srgb(X @ cf), cf
