"""W42 G2, the pre-read addendum's reference: native T at any span from family A's ordinates.

The rule is `native-t-addendum.md` (beside this directory), written and committed BEFORE any family-A
pixel is read, because the declared path is silent on it (see that note's §1). This module is its
executable form; the addendum's text governs where the two could be read differently.

Per endpoint, from family A's measured ordinates, each an (encoded input level, output code) pair:

  full rows    F0 (the t = 0 stratum: every s <= 64, read on the capsule) and F96, each the piecewise-linear
               curve through its ten ordinates, held at its ends;
  base         B(L, s): F0 for s <= 64, F96 for s >= 96, linear in t = clamp((s - 64)/96, 0, 1) between;
  sparse rows  for a stratum sigma with fewer ordinates (dark 80; 128; 160): residuals r_i = y_i - B(L_i, sigma)
               at its own measured levels, R(L) piecewise linear through them and held beyond the first
               and the last (the convention of the instrument's stand-in, `tone.memo_c_T`), T_sigma = B + R,
               then the monotone guard;
  between      linear in t between the two strata that bracket s; s <= 64 is F0, s >= 160 the 160 row;
  s = 112      t = 1/2, midway between the 96 stratum (t = 1/3) and the 128 stratum (t = 2/3):
               T(L, 112) = (T_96(L) + T_128(L)) / 2.

No parameter is chosen: every number the rule uses is a measured ordinate, a declared stratum span or t.

    python3.12 -B native_t.py        # the self-check on the stand-in ordinates (memo C's table)
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..', '2026-09-29-w42-g0-declaration', 'instrument')))

FULL_STRATA = (64, 96)
STRATA = {'light': (64, 96, 128, 160), 'dark': (64, 80, 96, 128, 160)}
GRID_SPANS = (64, 80, 96, 128, 160)                      # the runtime table's rows (bodyToneTableSpans)
GRID_LEVELS = (0, 64, 96, 128, 160, 176, 192, 208, 224, 240, 255)   # bodyToneTableLevels
# family A's declared levels per stratum (bed/bed.json, the 2x calibration cells)
DECLARED_LEVELS = {64: (0, 64, 128, 160, 176, 192, 208, 224, 240, 255),
                   96: (0, 64, 128, 160, 176, 192, 208, 224, 240, 255),
                   80: (160, 208, 255), 128: (160, 208, 255), 160: (96, 160, 208, 255)}


class NonMonotone(ValueError):
    """Measured ordinates that decrease: a finding for the parent, never repaired by the rule."""


def t_of(s):
    return min(max((s - 64.0) / 96.0, 0.0), 1.0)


def _curve(points):
    xs = np.array(sorted(points), float)
    ys = np.array([points[x] for x in sorted(points)], float)
    return lambda L: np.interp(L, xs, ys)


def _check_monotone(name, points):
    ys = [points[x] for x in sorted(points)]
    if any(b < a for a, b in zip(ys, ys[1:])):
        raise NonMonotone(f'{name}: measured ordinates decrease {ys}')


class NativeT:
    """Native T for one endpoint. `ordinates` maps a stratum span (64 for the t = 0 stratum) to
    {level: code}; 64 and 96 are required and full."""

    def __init__(self, ordinates, scheme):
        self.scheme = scheme
        for s, pts in ordinates.items():
            _check_monotone(f'{scheme} s={s}', pts)
        self.F0, self.F96 = _curve(ordinates[64]), _curve(ordinates[96])
        self.rows = {64: self.F0(np.array(GRID_LEVELS, float)), 96: self.F96(np.array(GRID_LEVELS, float))}
        self.measured = ordinates
        for s in STRATA[scheme]:
            if s in FULL_STRATA:
                continue
            self.rows[s] = self._sparse_row(s, ordinates[s])

    def base(self, L, s):
        a = t_of(s) / t_of(96) if s < 96 else 1.0
        return (1 - a) * self.F0(L) + a * self.F96(L)

    def _sparse_row(self, s, pts):
        Ls = np.array(sorted(pts), float)
        r = np.array([pts[x] for x in sorted(pts)], float) - self.base(Ls, s)
        grid = np.array(GRID_LEVELS, float)
        v = self.base(grid, s) + np.interp(grid, Ls, r)
        # The monotone guard: between two consecutive measured levels a < b, each computed ordinate is
        # raised to its predecessor and capped at y_b, walking upward. Below the first and above the last
        # measured level the row is B + a constant, monotone because B is; measured ordinates are kept.
        y = {float(x): float(pts[x]) for x in pts}
        for j in range(1, len(grid)):
            L = grid[j]
            if L in y:
                continue
            above = [m for m in Ls if m > L]
            below = [m for m in Ls if m < L]
            if above and below:
                v[j] = min(max(v[j], v[j - 1]), y[float(above[0])])
        for m, val in y.items():
            v[list(grid).index(m)] = val
        return v

    def row(self, s):
        """The runtime table's row at a grid span: a stratum's own row, or (light 80) the t-interpolation."""
        return self.rows[s] if s in self.rows else self._between(s)

    def _between(self, s):
        spans = STRATA[self.scheme]
        s = min(max(s, spans[0]), spans[-1])
        if s in self.rows:
            return self.rows[s]
        hi = next(x for x in spans if x > s)
        lo = max(x for x in spans if x < s)
        a = (t_of(s) - t_of(lo)) / (t_of(hi) - t_of(lo))
        return (1 - a) * self.rows[lo] + a * self.rows[hi]

    def __call__(self, L, s):
        """T(L, s), evaluated by the rule directly (rows in L, then t between strata)."""
        return np.interp(L, GRID_LEVELS, self._between(s))

    def table(self):
        """The runtime grid (bodyToneTableCodes): one row per GRID_SPANS entry."""
        return np.array([self.row(s) for s in GRID_SPANS])


def grid_eval(table, L, s):
    """The shader's evaluation of the grid: piecewise linear in L within a row, linear in t between rows."""
    s = min(max(s, GRID_SPANS[0]), GRID_SPANS[-1])
    rows = [np.interp(L, GRID_LEVELS, table[i]) for i in range(len(GRID_SPANS))]
    ts = [t_of(x) for x in GRID_SPANS]
    return np.array([np.interp(t_of(s), ts, [r[k] for r in rows]) for k in range(len(np.atleast_1d(L)))])


def stand_in(ep, scheme):
    """Memo C's table (the instrument's stand-in) sampled at family A's declared levels and strata: a
    synthetic native T with the right shape, used only by the self-check."""
    from tone import memo_c_T
    span_of = {64: 44, 80: 80, 96: 96, 128: 128, 160: 160}
    return {s: {L: float(memo_c_T(ep, span_of[s])(np.array([float(L)]))[0]) for L in DECLARED_LEVELS[s]}
            for s in STRATA[scheme]}


def self_check():
    out = []
    for ep in ('light-rest', 'light-inactive', 'dark-rest', 'dark-inactive'):
        scheme = ep.split('-')[0]
        pts = stand_in(ep, scheme)
        nt = NativeT(pts, scheme)
        tab = nt.table()
        # 1. every measured ordinate is reproduced, by the rule and by the grid
        worst = max(abs(nt(np.array([float(L)]), s)[0] - y) for s, row in pts.items() for L, y in row.items())
        worst_g = max(abs(grid_eval(tab, np.array([float(L)]), s)[0] - y) for s, row in pts.items()
                      for L, y in row.items())
        # 2. monotone in L at every span, 3. the grid is the rule at every span and level
        Ls = np.linspace(0, 255, 511)
        mono, gap = True, 0.0
        for s in np.linspace(32, 200, 169):
            a = nt(Ls, s)
            mono &= bool(np.all(np.diff(a) >= -1e-9))
            gap = max(gap, float(np.abs(a - grid_eval(tab, Ls, s)).max()))
        # 4. the full rows are reproduced exactly (no residual there)
        full = max(float(np.abs(nt(Ls, s) - (nt.F0(Ls) if s <= 64 else nt.F96(Ls))).max()) for s in (40, 64, 96))
        # 5. s = 112 is the mean of the 96 and 128 rows
        mid = float(np.abs(nt(Ls, 112) - 0.5 * (np.interp(Ls, GRID_LEVELS, nt.rows[96]) +
                                                   np.interp(Ls, GRID_LEVELS, nt.rows[128]))).max())
        # descriptive: the completion against the stand-in's own values where the sparse strata have none
        from tone import memo_c_T
        comp = {s: float(np.abs(nt(np.array([0.0, 64.0, 128.0]), s) -
                                memo_c_T(ep, s)(np.array([0.0, 64.0, 128.0]))).max()) for s in (128, 160)}
        out.append(f'{ep:15s} measured {worst:.1e} (grid {worst_g:.1e})  monotone {mono}  grid==rule {gap:.1e}  '
                   f'full rows {full:.1e}  s=112 mean {mid:.1e}  | completion vs stand-in at 0/64/128: '
                   f's=128 {comp[128]:.1f}, s=160 {comp[160]:.1f} codes')
    # 6. the guard, on a constructed case where base + residual overshoots between two measured ordinates
    lv = DECLARED_LEVELS[64]
    f96 = dict(zip(lv, (40, 80, 120, 150, 170, 170, 171, 180, 190, 200)))
    pts = {64: dict(zip(lv, (40, 80, 120, 150, 170, 170, 171, 180, 190, 200))), 96: f96,
           128: {160: 150.0, 208: 151.0, 255: 190.0}, 160: {96: 100.0, 160: 150.0, 208: 151.0, 255: 190.0}}
    nt = NativeT(pts, 'light')
    raw = nt.base(np.array([176.0]), 128)[0] + np.interp(176.0, [160, 208, 255], [0.0, 151.0 - 171.0, 0.0])
    guarded = nt(np.array([176.0]), 128)[0]
    Ls = np.linspace(0, 255, 511)
    mono = all(bool(np.all(np.diff(nt(Ls, s)) >= -1e-9)) for s in np.linspace(32, 200, 169))
    out.append(f'guard case     base + residual at 176 on s=128 reads {raw:.2f} above the next measured 151; '
               f'guarded {guarded:.2f}; monotone everywhere {mono}; measured kept '
               f'{nt(np.array([160.0, 208.0]), 128).tolist()}')
    return '\n'.join(out)


if __name__ == '__main__':
    print(self_check())
