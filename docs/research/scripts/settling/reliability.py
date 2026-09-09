#!/usr/bin/env python3
"""Agreement and interval statistics for the quality instrument (spec: 2026-09-09-quality-instrument.md).

    python3 reliability.py --selftest     check every estimator against published or hand-worked values

Standard library only. analyze.py has to run wherever the settling scripts run, and a reliability
number that depends on a scientific stack being installed is a number nobody can reproduce; numpy
and scipy are never imported here, not even optionally, because the formulas below are short enough
to read and check by hand.

    krippendorff_alpha(units, metric)     units is {unit: {rater: value}}, a missing rating simply absent
    spearman(xs, ys)                      rank correlation, average ranks for ties
    bootstrap_mean_ci(values, n, seed)    the mean and its percentile 95 % interval
    within_one(pairs)                     the share of (a, b) pairs within one scale point
    exact_agreement(pairs)                the share of (a, b) pairs that repeated exactly
"""
import sys, math, random, itertools
from collections import Counter


# ---------- Krippendorff's alpha ----------

def _nominal_distance(values, counts):
    """The nominal difference function: any two unequal values disagree by the same amount."""
    return lambda a, b: 0.0 if a == b else 1.0


def _ordinal_distance(values, counts):
    """Krippendorff's ordinal difference function. Two ranks are as far apart as the observations
    that lie between them: the sum of the marginal frequencies from one to the other, counting each
    endpoint's own frequency by half, squared. It is why 2 against 5 is a worse disagreement than 2
    against 3, and why the distance depends on how the raters used the scale rather than on the
    numbers printed on it."""
    index = {v: i for i, v in enumerate(values)}
    cum = [0.0] * (len(values) + 1)                       # cum[i] = frequencies below values[i]
    for i, v in enumerate(values):
        cum[i + 1] = cum[i] + counts[v]

    def d(a, b):
        i, j = sorted((index[a], index[b]))
        between = cum[j + 1] - cum[i]                     # n_i + … + n_j inclusive
        return (between - (counts[values[i]] + counts[values[j]]) / 2.0) ** 2
    return d


METRICS = {"nominal": _nominal_distance, "ordinal": _ordinal_distance}


def krippendorff_alpha(units, metric="ordinal"):
    """Krippendorff's α over `units`, a {unit: {rater: value}} map in which a rater that did not
    rate a unit is simply absent from it. Units carrying fewer than two ratings hold no pairable
    observation and drop out, exactly as they do from the coincidence matrix.

    α = 1 − D_o / D_e, where D_o is the mean squared difference within units (each unit's ordered
    pairs weighted by 1 / (m − 1), so a unit rated by many raters does not outweigh one rated by
    two) and D_e is the same statistic over all pairs of the pooled ratings — the disagreement
    chance alone would produce. 1 is perfect agreement, 0 is chance, negative is systematic
    disagreement.

    Returns None when nothing is pairable, and 1.0 when every pairable rating is the same value:
    there is then no variation for chance to explain, and the raters did agree.
    """
    if metric not in METRICS:
        raise ValueError(f"metric must be one of {sorted(METRICS)}, not {metric!r}")
    observed = [list(u.values()) for u in units.values() if len(u) >= 2]
    if not observed:
        return None
    counts = Counter(v for vs in observed for v in vs)     # the coincidence matrix's marginals n_c
    n = sum(counts.values())
    if n < 2:
        return None
    values = sorted(counts)
    if len(values) < 2:
        return 1.0
    delta = METRICS[metric](values, counts)

    # Observed disagreement: every ordered pair within a unit, divided by that unit's m − 1.
    d_o = 0.0
    for vs in observed:
        m = len(vs)
        for a, b in itertools.permutations(vs, 2):
            d_o += delta(a, b) / (m - 1)
    d_o /= n

    # Expected disagreement: every ordered pair of the pooled ratings, drawing without replacement.
    d_e = 0.0
    for a in values:
        for b in values:
            if a != b:                                     # delta(a, a) is zero for both metrics
                d_e += counts[a] * counts[b] * delta(a, b)
    d_e /= n * (n - 1)
    return 1.0 if d_e == 0 else 1.0 - d_o / d_e


# ---------- rank correlation, intervals, retest ----------

def _ranks(xs):
    """Average ranks, so a run of tied values all take the mean of the ranks they occupy."""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        mean_rank = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            r[order[k]] = mean_rank
        i = j + 1
    return r


def spearman(xs, ys):
    """Spearman's ρ: Pearson's correlation of the average ranks. None when there are fewer than
    three pairs or when one side is constant and has no ranking to correlate."""
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    if len(pairs) < 3:
        return None
    rx, ry = _ranks([p[0] for p in pairs]), _ranks([p[1] for p in pairs])
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    sxy = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sxx = sum((a - mx) ** 2 for a in rx)
    syy = sum((b - my) ** 2 for b in ry)
    return None if sxx == 0 or syy == 0 else sxy / math.sqrt(sxx * syy)


def bootstrap_mean_ci(values, n=2000, seed=0, level=0.95):
    """The mean of `values` and its percentile bootstrap interval: n resamples of the same size
    drawn with replacement, the 2.5th and 97.5th percentiles of their means. Seeded, so the same
    data prints the same interval on every run. Returns (None, None, None) when empty and the
    value itself as a degenerate interval when there is one observation."""
    vals = [v for v in values if v is not None]
    if not vals:
        return (None, None, None)
    mean = sum(vals) / len(vals)
    if len(vals) == 1:
        return (mean, mean, mean)
    rng = random.Random(seed)
    means = []
    for _ in range(n):
        s = [vals[rng.randrange(len(vals))] for _ in range(len(vals))]
        means.append(sum(s) / len(s))
    means.sort()
    lo = means[max(0, int(round((1 - level) / 2 * n)) - 1)]
    hi = means[min(n - 1, int(round((1 + level) / 2 * n)) - 1)]
    return (mean, lo, hi)


def within_one(pairs):
    """The share of (first rating, second rating) pairs that landed within one scale point — the
    retest statistic the spec's acceptance reads. None when there are no pairs."""
    ps = [(a, b) for a, b in pairs if a is not None and b is not None]
    return None if not ps else sum(1 for a, b in ps if abs(a - b) <= 1) / len(ps)


def exact_agreement(pairs):
    """The share of pairs that repeated exactly — the retest statistic for the 0/1 defect items."""
    ps = [(a, b) for a, b in pairs if a is not None and b is not None]
    return None if not ps else sum(1 for a, b in ps if a == b) / len(ps)


# ---------- selftest ----------

# Krippendorff, "Computing Krippendorff's Alpha-Reliability" (2011), section C: the paper's own
# worked matrix of four observers by twelve units, a dot where an observer did not rate the unit.
# The paper computes alpha_nominal = 0.743 from it (section C, step 4) and alpha_ordinal = 0.815
# from the same data read as ranks (section D).
KRIPPENDORFF_2011_C = [
    "1 2 3 3 2 1 4 1 2 . . .",
    "1 2 3 3 2 2 4 1 2 5 . 3",
    ". 3 3 3 2 3 4 2 2 5 1 .",
    "1 2 3 3 2 4 4 1 2 5 1 .",
]

# The canonical three-coder, fifteen-unit example (Wikipedia's Krippendorff's alpha article, after
# Krippendorff 2011/2013), whose published nominal alpha is 0.691. It is a harder missing-data
# case: two units hold no rating at all and one holds a single unpairable rating.
KRIPPENDORFF_3CODER = [
    ". . . . . 3 4 1 2 1 1 3 3 . 3",
    "1 . 2 1 3 3 4 3 . . . . . . .",
    ". . 2 1 3 4 4 . 2 1 1 3 3 . 4",
]


def _units_from_matrix(rows):
    """A {unit: {rater: value}} map from rows of space-separated values, '.' meaning not rated."""
    units = {}
    for r, row in enumerate(rows):
        for u, v in enumerate(row.split()):
            if v != ".":
                units.setdefault(u, {})[r] = int(v)
    return units


def selftest():
    checks = []

    def check(name, got, want, tol=5e-4):
        ok = got is not None and abs(got - want) <= tol
        checks.append(ok)
        print(f"{'PASS' if ok else 'FAIL'}  {name}: got {got if got is None else round(got, 6)}, want {want}")

    published = _units_from_matrix(KRIPPENDORFF_2011_C)
    check("alpha nominal, Krippendorff 2011 section C", krippendorff_alpha(published, "nominal"), 0.743, 5e-4)
    check("alpha ordinal, Krippendorff 2011 section C", krippendorff_alpha(published, "ordinal"), 0.815, 5e-4)
    three = _units_from_matrix(KRIPPENDORFF_3CODER)
    check("alpha nominal, three-coder canonical example", krippendorff_alpha(three, "nominal"), 0.691, 5e-4)

    # Perfect agreement over a scale that is actually used: no disagreement to correct for.
    perfect = {"p1": {"a": 1, "b": 1, "c": 1}, "p2": {"a": 7, "b": 7, "c": 7}, "p3": {"a": 4, "b": 4}}
    check("alpha nominal, perfect agreement", krippendorff_alpha(perfect, "nominal"), 1.0)
    check("alpha ordinal, perfect agreement", krippendorff_alpha(perfect, "ordinal"), 1.0)

    # Hand-worked nominal case: two raters, four units, values 0/0, 0/0, 0/1, 1/1. Pooled n = 8
    # with n_0 = 5 and n_1 = 3, so D_o = 2/8 and D_e = (5·3 + 3·5)/(8·7), and α = 1 − 0.25/(30/56).
    hand = {"u1": {"a": 0, "b": 0}, "u2": {"a": 0, "b": 0}, "u3": {"a": 0, "b": 1}, "u4": {"a": 1, "b": 1}}
    check("alpha nominal, hand-worked 4-unit case", krippendorff_alpha(hand, "nominal"), 1 - 0.25 / (30 / 56))

    # Systematic disagreement: two raters who reverse each other score below chance.
    reversed_ = {"u1": {"a": 0, "b": 1}, "u2": {"a": 1, "b": 0}}
    check("alpha nominal, systematic disagreement", krippendorff_alpha(reversed_, "nominal"), -0.5)

    # Hand-worked ordinal case: values 1/1, 1/2, 3/3. Marginals n_1 = 3, n_2 = 1, n_3 = 2 give
    # delta(1,2)² = 4, delta(1,3)² = 12.25, delta(2,3)² = 2.25; D_o = 8/6 and D_e = 180/30 = 6.
    ordinal = {"u1": {"a": 1, "b": 1}, "u2": {"a": 1, "b": 2}, "u3": {"a": 3, "b": 3}}
    check("alpha ordinal, hand-worked 3-unit case", krippendorff_alpha(ordinal, "ordinal"), 1 - (8 / 6) / 6)

    # Unpairable data has no alpha rather than a misleading one.
    checks.append(krippendorff_alpha({}, "ordinal") is None)
    print(f"{'PASS' if checks[-1] else 'FAIL'}  alpha of no data is None")
    checks.append(krippendorff_alpha({"u1": {"a": 3}}, "ordinal") is None)
    print(f"{'PASS' if checks[-1] else 'FAIL'}  alpha of single-rater units is None")

    check("spearman, exact reversal", spearman([1, 2, 3, 4, 5], [5, 4, 3, 2, 1]), -1.0)
    check("spearman, with a tie", spearman([1, 2, 2, 3], [1, 2, 3, 4]), 4.5 / math.sqrt(4.5 * 5.0))

    m, lo, hi = bootstrap_mean_ci([2.0] * 20)
    check("bootstrap mean of a constant", m, 2.0)
    check("bootstrap interval of a constant collapses", hi - lo, 0.0)
    m, lo, hi = bootstrap_mean_ci([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], n=4000, seed=1)
    check("bootstrap mean of 1..10", m, 5.5)
    checks.append(lo < 5.5 < hi and 3.0 < lo and hi < 8.0)
    print(f"{'PASS' if checks[-1] else 'FAIL'}  bootstrap interval of 1..10 brackets the mean: "
          f"{round(lo, 2)}–{round(hi, 2)}")

    check("within_one", within_one([(1, 2), (1, 3)]), 0.5)
    check("exact_agreement", exact_agreement([(0, 0), (1, 0), (1, 1), (0, 0)]), 0.75)

    print(f"\n{sum(checks)}/{len(checks)} checks passed.")
    return 0 if all(checks) else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    print(__doc__)
