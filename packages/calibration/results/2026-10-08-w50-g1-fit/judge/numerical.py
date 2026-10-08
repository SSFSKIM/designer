"""W50's bounded numerical comparisons, not a landing gate or evidence authenticator.

The adapter supplies pre-fit reference rows and candidate statistics after verifying their
hashes, document pairs, support, membership and admission. These frozen contracts carry those
identities; constructing one checks shape/range only, NEVER authenticates caller-supplied data.
There is no JSON/map-to-evidence conversion, filesystem access, dispatcher or owner-axis proxy.
WITHIN means only this numerical comparison, never whole-gate PASS.

Source semantics:
* W50 charter fixed landing rule / G0 fit-declaration.json: channel and support intersections,
  CSS error growth, T1 current and own-history caps, and the six target/scale comparisons.
* test/adopted-thresholds.test.ts, t1Classify/t1Cut: B=max(code,2*bar), linear T1 units,
  T1-low regression (T1-fine fidelity). W50 adds no absolute T1 or E2 gate.
* results/2026-10-05-w46-g0-declaration/cuts/rule.py, target_aggregate, used by W48:
  A=median(abs(log((web+code)/(native+code)))); epsilon is EACH cell's linear code step,
  not B, a group epsilon, or the unregularised selection metric. P pools poses per profile.
  W48 halving compares its original d0219/full-pair reference. W50's named misses compare
  frozen W49a current, strictly, without the older group-rule tau.

Native input64 is only a reported held-join control. The CPU/shader identity and monotonicity
referees are separate; a native-error comparison here cannot certify numerical identity.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import re
from statistics import median
from typing import Literal, Sequence

Number = float | int
Value = Number | tuple[Number, Number, Number]
UNITS = ('encoded-RGB-codes', 'encoded-luma-codes', 'linear-luma')
# The statistic is central8-channel-median; center8 names its geometric support only.
CHANNELS = ('deep8-channel-median', 'central8-channel-median')
LUMA = ('deep8-far24-luma-mean', 'deep8-far24-luma-median')
T1_REGRESSION = ('T1-full-silhouette', 'T1-low')


def _number(value, name, low, high):
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise ValueError(f'{name}: finite number required')
    if not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f'{name}: expected finite value in [{low}, {high}]')


def _hash(value):
    if not isinstance(value, str) or re.fullmatch('[0-9a-f]{64}', value) is None:
        raise ValueError('Identity requires a full lowercase SHA-256, not an alias')


def _values(value, rgb):
    if rgb:
        if isinstance(value, tuple) and len(value) == 3:
            return value
        return (value, value, value)
    if isinstance(value, tuple):
        raise ValueError('Scalar statistic cannot carry channel values')
    return (value,)


@dataclass(frozen=True)
class DocumentPair:
    active_sha256: str
    receded_sha256: str

    def __post_init__(self):
        _hash(self.active_sha256)
        _hash(self.receded_sha256)


@dataclass(frozen=True)
class Evidence:
    """A typed source identity plus its derived statistic's evidence digest.

    source_sha256 names PNG bytes, an admitted native three-run cohort, or an immutable
    frozen-reference record according to source_kind. Non-PNG sources never acquire a
    capture identity by conversion. The adapter supplies the kind; validation is structural,
    not authentication. Existing actual PNG callers may use the explicit PNG default.
    """
    source_sha256: str
    statistic_sha256: str
    document_pair: DocumentPair | None
    source_kind: Literal['png', 'native-three-run-cohort', 'frozen-reference-record'] = 'png'

    def __post_init__(self):
        _hash(self.source_sha256)
        _hash(self.statistic_sha256)
        if self.source_kind not in ('png', 'native-three-run-cohort', 'frozen-reference-record'):
            raise ValueError('Unknown evidence source kind')
        if self.document_pair is not None and not isinstance(self.document_pair, DocumentPair):
            raise ValueError('Document identity must be a full DocumentPair')


@dataclass(frozen=True)
class RowIdentity:
    profile: str
    renderer: str
    scene: str
    statistic: str
    support: str

    def __post_init__(self):
        if any(not isinstance(v, str) or not v.strip()
               for v in (self.profile, self.scene, self.statistic, self.support)):
            raise ValueError('Nonempty row identity and support required')
        if self.renderer not in ('webgpu', 'css'):
            raise ValueError('Unknown renderer')


@dataclass(frozen=True)
class Reading:
    status: str
    units: str
    value: Value | None
    evidence: Evidence | None
    reason: str = ''

    def __post_init__(self):
        if self.units not in UNITS:
            raise ValueError('Unknown statistic units')
        if self.status != 'MEASURED':
            if self.status not in ('UNMEASURED', 'UNMEASURED_EMPTY_SUPPORT',
                                    'UNMEASURED_TINY_SUPPORT') or self.value is not None or not self.reason:
                raise ValueError('Unmeasured reading requires null value and an explicit reason')
            return
        if not isinstance(self.evidence, Evidence):
            raise ValueError('Measured reading must carry evidence identities (not authentication)')
        rgb = self.units == 'encoded-RGB-codes'
        if rgb and not (isinstance(self.value, tuple) and len(self.value) == 3):
            raise ValueError('RGB statistic requires three channel values')
        for v in _values(self.value, rgb):
            _number(v, 'statistic', 0, 1 if self.units == 'linear-luma' else 255)


@dataclass(frozen=True)
class FrozenT1Budget:
    """Preserved original canonical0.25 budget, distinct from a fresh native repeat reading.

    This structural witness does not authenticate its inventory bytes; the live adapter does.
    It never changes the code-step used by aggregates or manufactures a replacement bar.
    """
    identity: RowIdentity
    inventory_sha256: str
    value: Number

    def __post_init__(self):
        _hash(self.inventory_sha256)
        _number(self.value, 'Frozen canonical T1 B', 0, 2)
        if (not isinstance(self.identity, RowIdentity) or self.identity.renderer != 'webgpu' or
                re.fullmatch(r'apple-macos-27\.0-[12]x-dark-standard-glass0\.25', self.identity.profile) is None or
                self.identity.statistic not in T1_REGRESSION or self.identity.scene.startswith('cell-') or
                self.value <= 0):
            raise ValueError('Frozen budgets belong only to original canonical dark0.25 WebGPU T1')


@dataclass(frozen=True)
class Reference:
    identity: RowIdentity
    inventory_sha256: str
    native: Reading
    current: Reading
    code: Value | None
    bar: Value | None
    budget: Value | None
    frozen_t1_budget: FrozenT1Budget | None = None

    def __post_init__(self):
        if not isinstance(self.identity, RowIdentity):
            raise TypeError('RowIdentity required')
        _hash(self.inventory_sha256)
        if not isinstance(self.native, Reading) or not isinstance(self.current, Reading):
            raise TypeError('Reading contracts required, not numeric maps')
        if self.native.units != self.current.units:
            raise ValueError('Native/current units disagree')
        if self.native.status == 'MEASURED' and self.native.evidence.document_pair is not None:
            raise ValueError('Native evidence cannot name a web document pair')
        if self.current.status == 'MEASURED' and self.current.evidence.document_pair is None:
            raise ValueError('Current web evidence requires full document pair')
        frozen = self.frozen_t1_budget
        if frozen is not None and (not isinstance(frozen, FrozenT1Budget) or
                frozen.identity != self.identity or frozen.inventory_sha256 != self.inventory_sha256 or
                frozen.value != self.budget or self.native.units != 'linear-luma'):
            raise ValueError('Frozen T1 budget must name this exact row, inventory, units and B')
        if any(v is None for v in (self.code, self.bar, self.budget)):
            if any(v is not None for v in (self.code, self.bar, self.budget)):
                raise ValueError('Missing budget must leave code/bar/budget all null')
            return
        rgb = self.native.units == 'encoded-RGB-codes'
        for code, bar, budget in zip(_values(self.code, rgb), _values(self.bar, rgb),
                                     _values(self.budget, rgb)):
            ceiling = 1 if self.native.units == 'linear-luma' else 255
            _number(code, 'code', 0, ceiling)
            _number(bar, 'bar', 0, ceiling)
            _number(budget, 'B', 0, 2 * ceiling)
            if code <= 0 or bar < code / 2 or (frozen is None and budget != max(code, 2 * bar)):
                raise ValueError('Expected positive code, bar >= half-code and B=max(code,2*bar) unless explicitly frozen')
            if self.native.units != 'linear-luma' and code != 1:
                raise ValueError('Encoded output budgets use one encoded code')


@dataclass(frozen=True)
class Candidate:
    identity: RowIdentity
    reading: Reading

    def __post_init__(self):
        if not isinstance(self.identity, RowIdentity) or not isinstance(self.reading, Reading):
            raise TypeError('Typed candidate identity and reading required')
        if self.reading.status == 'MEASURED' and self.reading.evidence.document_pair is None:
            raise ValueError('Candidate web evidence requires a full document pair')


@dataclass(frozen=True)
class Historical:
    reading: Reading
    frozen_current_growth: Number | None
    repaired: bool

    def __post_init__(self):
        if not isinstance(self.reading, Reading) or type(self.repaired) is not bool:
            raise TypeError('Historical reading and explicit repaired flag required')
        if self.reading.status == 'MEASURED' and self.reading.evidence.document_pair is None:
            raise ValueError('Historical web evidence requires full document pair')
        if self.frozen_current_growth is not None:
            _number(self.frozen_current_growth, 'Frozen historical growth (statistic units)', -1, 1)


@dataclass(frozen=True)
class Component:
    name: str
    status: str
    error: float
    current_error: float | None
    growth: float | None
    bound: float | None


@dataclass(frozen=True)
class Comparison:
    identity: RowIdentity
    status: str
    units: str
    components: tuple[Component, ...] = ()
    reason: str = ''


def _match(ref, candidate):
    if not isinstance(ref, Reference) or not isinstance(candidate, Candidate):
        raise TypeError('Reference and Candidate contracts required; numeric maps are not evidence')
    if ref.identity != candidate.identity or ref.native.units != candidate.reading.units:
        raise ValueError('Candidate/reference identity, support or units differ')


def _missing(ref, candidate, *, current=False, budget=True, extra=()):
    readings = (ref.native, candidate.reading) + ((ref.current,) if current else ()) + extra
    reasons = [f'{r.status}: {r.reason}' for r in readings if r.status != 'MEASURED']
    if budget and ref.budget is None:
        reasons.append('UNMEASURED: pre-fit budget absent')
    return Comparison(ref.identity, 'UNMEASURED', ref.native.units, reason='; '.join(reasons)) if reasons else None


def _compare(ref, candidate, *, growth=False, bounds=None, baseline=None, diagnostic=False):
    rgb = ref.native.units == 'encoded-RGB-codes'
    ns, ks = _values(ref.native.value, rgb), _values(candidate.reading.value, rgb)
    cs = _values(baseline.value, rgb) if baseline is not None else (None,) * len(ns)
    bs = (None,) * len(ns) if diagnostic else _values(bounds, rgb)
    names = ('R', 'G', 'B') if rgb else (ref.identity.statistic,)
    components = []
    for name, n, c, k, bound in zip(names, ns, cs, ks, bs):
        error = abs(k - n)
        old = None if c is None else abs(c - n)
        delta = None if old is None else error - old
        status = 'DIAGNOSTIC' if diagnostic else 'WITHIN' if (delta if growth else error) <= bound else 'EXCEEDS'
        components.append(Component(name, status, error, old, delta, bound))
    status = 'DIAGNOSTIC' if diagnostic else 'EXCEEDS' if any(c.status == 'EXCEEDS' for c in components) else 'WITHIN'
    return Comparison(ref.identity, status, ref.native.units, tuple(components))


def diagnostic_reading(reference: Reference, candidate: Candidate) -> Comparison:
    """One authenticated statistic reported without any bound or gate verdict.

    The rule router, not this mathematical layer, selects diagnostic populations such as
    DL5j's input64 controls, the exact DL5a reported keys and the T1-fine companion.
    """
    _match(reference, candidate)
    return _missing(reference, candidate, budget=False) or _compare(reference, candidate, diagnostic=True)


def channel_level(reference: Reference, candidate: Candidate) -> Comparison:
    """Independent RGB median bounds for a declared deep8 or center8 row."""
    _match(reference, candidate)
    if reference.identity.statistic not in CHANNELS or reference.native.units != 'encoded-RGB-codes':
        raise ValueError('Channel level requires an encoded RGB deep8/center8 median')
    return _missing(reference, candidate) or _compare(reference, candidate, bounds=reference.budget)


def _same_cell(a, ka, b, kb):
    _match(a, ka)
    _match(b, kb)
    if (a.identity.profile, a.identity.renderer, a.identity.scene, a.inventory_sha256) != (
            b.identity.profile, b.identity.renderer, b.identity.scene, b.inventory_sha256):
        raise ValueError('Independent statistics must describe the same cell and inventory')
    for left, right in ((a.native, b.native), (a.current, b.current), (ka.reading, kb.reading)):
        if left.status == right.status == 'MEASURED':
            le, re = left.evidence, right.evidence
            if (le.source_kind, le.source_sha256, le.document_pair) != (
                    re.source_kind, re.source_sha256, re.document_pair):
                raise ValueError('Paired statistics must come from the same typed source and documents')


def uniform_levels(input_code: Number, deep: Reference, deep_candidate: Candidate,
                   center: Reference, center_candidate: Candidate) -> tuple[Comparison, Comparison]:
    """Intersect deep and center separately. Input64 reports errors with NO native bound."""
    _number(input_code, 'Uniform input', 0, 64)
    if 40 < input_code < 64:
        raise ValueError('Only declared uniform closure inputs 0..40 and held control64 are admitted')
    _same_cell(deep, deep_candidate, center, center_candidate)
    if deep.identity.statistic != CHANNELS[0] or center.identity.statistic != CHANNELS[1]:
        raise ValueError('Uniform closure requires deep8 AND center8 channel medians')
    if input_code != 64:
        return channel_level(deep, deep_candidate), channel_level(center, center_candidate)
    out = []
    for ref, candidate in ((deep, deep_candidate), (center, center_candidate)):
        _match(ref, candidate)
        if ref.native.units != 'encoded-RGB-codes':
            raise ValueError('Held uniform control requires encoded RGB medians')
        out.append(_missing(ref, candidate, budget=False) or _compare(ref, candidate, diagnostic=True))
    return tuple(out)


def luma_level(reference: Reference, candidate: Candidate) -> Comparison:
    """One original encoded-luma mean or median key, with its own declared bound."""
    _match(reference, candidate)
    if reference.identity.statistic not in LUMA or reference.native.units != 'encoded-luma-codes':
        raise ValueError('Expected a deep8/far24 encoded-luma mean or median')
    return _missing(reference, candidate) or _compare(reference, candidate, bounds=reference.budget)


def luma_levels(mean: Reference, mean_candidate: Candidate,
                median_ref: Reference, median_candidate: Candidate) -> tuple[Comparison, Comparison]:
    """Encoded-luma mean AND median, not mean-channel luma or an averaged error."""
    _same_cell(mean, mean_candidate, median_ref, median_candidate)
    out = []
    for ref, candidate, statistic in ((mean, mean_candidate, LUMA[0]),
                                       (median_ref, median_candidate, LUMA[1])):
        _match(ref, candidate)
        if ref.identity.statistic != statistic or ref.native.units != 'encoded-luma-codes':
            raise ValueError('Expected separate deep8/far24 encoded-luma mean and median')
        out.append(luma_level(ref, candidate))
    return tuple(out)


def css_level_growth(reference: Reference, candidate: Candidate) -> Comparison:
    """Price each supplied encoded level statistic at <=1 code ERROR growth."""
    _match(reference, candidate)
    expected_units = 'encoded-RGB-codes' if reference.identity.statistic in CHANNELS else 'encoded-luma-codes'
    if (reference.identity.renderer != 'css' or reference.identity.statistic not in CHANNELS + LUMA
            or reference.native.units != expected_units):
        raise ValueError('CSS growth requires a priced encoded channel/luma level row')
    return _missing(reference, candidate, current=True, budget=False) or _compare(
        reference, candidate, growth=True, bounds=1, baseline=reference.current)


def _t1(reference, candidate):
    _match(reference, candidate)
    if (reference.identity.renderer != 'webgpu' or reference.native.units != 'linear-luma'
            or reference.identity.statistic not in T1_REGRESSION):
        raise ValueError('T1 regression requires linear full-silhouette or T1-low, never fine')


def t1_growth(reference: Reference, candidate: Candidate) -> Comparison:
    """No absolute texture gate: |candidate-native|-|current-native| <= sealed B."""
    _t1(reference, candidate)
    return _missing(reference, candidate, current=True) or _compare(
        reference, candidate, growth=True, bounds=reference.budget, baseline=reference.current)


def newbed_structured_t1_growth(reference: Reference, candidate: Candidate) -> Comparison:
    """DL5i: new structured-bed texture growth applies to BOTH declared renderer tiers.

    The live reader still authenticates original bed membership/support; this shape check
    cannot promote canonical cells or neutral span controls into the structured population.
    Canonical and own-history T1 retain their separate WebGPU-only contracts above/below.
    """
    _match(reference, candidate)
    if (reference.native.units != 'linear-luma' or
            reference.identity.statistic != 'T1-full-silhouette' or
            re.fullmatch(r'cell-(impulse-sparse|checker-low)-s\d{3}__(rest|inactive)',
                         reference.identity.scene) is None):
        raise ValueError('New-bed structured T1 requires its declared full-silhouette linear statistic')
    return _missing(reference, candidate, current=True) or _compare(
        reference, candidate, growth=True, bounds=reference.budget, baseline=reference.current)


def historical_from_frozen_in_b(reference: Reference, reading: Reading, *,
                                frozen_current_growth_in_b: Number, repaired: bool) -> Historical:
    """Verify G0's original normalized witness before retaining its exact raw-unit growth.

    G0 stored (abs(current-native)-abs(historical-native))/B without rounding. Multiplying
    that quotient back by B can lose an ulp. Repeating the ORIGINAL division and requiring
    equality proves the witness instead; no tolerance, candidate input or re-baseline enters.
    """
    if (not isinstance(reference, Reference) or not isinstance(reading, Reading) or
            reference.identity.renderer != 'webgpu' or reference.native.units != 'linear-luma' or
            reading.units != 'linear-luma' or reference.identity.statistic not in T1_REGRESSION):
        raise ValueError('Normalized history requires its canonical WebGPU T1 reference')
    _number(frozen_current_growth_in_b, 'Frozen normalized historical growth', -math.inf, math.inf)
    if reference.budget is None or any(r.status != 'MEASURED' for r in (reference.native, reference.current, reading)):
        return Historical(reading, None, repaired)
    raw = abs(reference.current.value-reference.native.value)-abs(reading.value-reference.native.value)
    if raw / reference.budget != frozen_current_growth_in_b:
        raise ValueError('Frozen normalized historical growth differs from its original readings')
    return Historical(reading, raw, repaired)


def historical_growth(reference: Reference, candidate: Candidate, historical: Historical) -> Comparison:
    """Own-row cap max(B,frozen current growth); repaired entries stay <=B, without rounding."""
    _t1(reference, candidate)
    if not isinstance(historical, Historical) or historical.reading.units != 'linear-luma':
        raise ValueError('Own historical T1 reading required in linear units')
    missing = _missing(reference, candidate, current=True, extra=(historical.reading,))
    if missing:
        return missing
    if historical.frozen_current_growth is None:
        return Comparison(reference.identity, 'UNMEASURED', reference.native.units,
                          reason='UNMEASURED: frozen current historical growth absent')
    n, c, h = reference.native.value, reference.current.value, historical.reading.value
    frozen = abs(c - n) - abs(h - n)
    # This is a consistency check, not added scientific tolerance or permission to rebase.
    if frozen != historical.frozen_current_growth:
        raise ValueError('Frozen current historical growth disagrees with supplied own-row readings')
    if historical.repaired and frozen > reference.budget:
        raise ValueError('A repaired row cannot have current historical growth above B')
    cap = reference.budget if historical.repaired else max(reference.budget, frozen)
    return _compare(reference, candidate, growth=True, bounds=cap, baseline=historical.reading)


@dataclass(frozen=True)
class AggregateCell:
    reference: Reference
    candidate: Candidate
    w48_reference: Reading | None = None


@dataclass(frozen=True)
class AggregateComparison:
    target: str
    scale: int
    rule: str
    status: str
    candidate: float | None = None
    current: float | None = None
    w48_reference: float | None = None
    bound: float | None = None
    units: str = 'dimensionless-natural-log'
    reason: str = ''


def target_aggregate(target: str, scale: int, cells: Sequence[AggregateCell], *,
                     expected_keys: Sequence[RowIdentity]) -> AggregateComparison:
    """One declared target/scale, with explicit membership; missing cells are not dropped.

    The adapter binds expected_keys to the admitted phase and checks each target's membership.
    It must authenticate w48_reference as d0219cd684bf/f0b36a71772a, NOT the W48 landing or
    W49a current, and authenticate current as the sealed W49a pair. This pure function checks
    full-pair consistency, not which generation a supplied hash actually represents.
    """
    if target not in ('C rest', 'F inactive', 'P') or type(scale) is not int or scale not in (1, 2):
        raise ValueError('Only the declared W50 targets and scales are admitted')
    halving = target == 'C rest' or (target == 'F inactive' and scale == 1)
    rule = 'w48-reference-halving' if halving else 'current-nonworsening'
    keys = tuple(c.reference.identity for c in cells)
    if len(set(keys)) != len(keys) or len(set(expected_keys)) != len(expected_keys):
        raise ValueError('Duplicate aggregate member')
    if set(keys) - set(expected_keys):
        raise ValueError('Unexpected aggregate member')
    profile = f'apple-macos-27.0-{scale}x-dark-standard-glass0.25'
    if any(k.profile != profile or k.renderer != 'webgpu' for k in expected_keys):
        raise ValueError('Aggregate cannot mix profiles, scales, tiers or positions')
    missing = []
    signatures = set()
    terms = []
    for cell in cells:
        ref, candidate = cell.reference, cell.candidate
        _match(ref, candidate)
        if ref.native.units != 'linear-luma' or ref.identity.statistic != 'T1-full-silhouette':
            raise ValueError('These F/C/P targets use full-silhouette linear T1')
        old = cell.w48_reference
        if old is not None and (not isinstance(old, Reading) or old.units != 'linear-luma'
                                or (old.status == 'MEASURED' and old.evidence.document_pair is None)):
            raise ValueError('W48 target reference needs linear units and full document pair')
        absent = _missing(ref, candidate, current=True, extra=(old,) if halving and old else ())
        if absent or (halving and old is None):
            missing.append(absent.reason if absent else 'W48 reference absent')
            continue
        signatures.add((ref.inventory_sha256, ref.current.evidence.document_pair,
                        candidate.reading.evidence.document_pair,
                        old.evidence.document_pair if halving else None))
        n, c, k, eps = ref.native.value, ref.current.value, candidate.reading.value, ref.code
        def error(value):
            return abs(math.log((value + eps) / (n + eps)))
        terms.append((error(k), error(c), error(old.value) if halving else None))
    if len(signatures) > 1:
        raise ValueError('Aggregate mixes inventories, current/candidate pairs or historical pairs')
    if not expected_keys or set(keys) != set(expected_keys) or missing:
        return AggregateComparison(target, scale, rule, 'UNMEASURED',
                                   reason='Missing aggregate members/readings: ' + '; '.join(missing))
    candidate_a = median(t[0] for t in terms)
    current_a = median(t[1] for t in terms)
    old_a = median(t[2] for t in terms) if halving else None
    bound = .5 * old_a if halving else current_a
    return AggregateComparison(target, scale, rule, 'WITHIN' if candidate_a <= bound else 'EXCEEDS',
                               candidate_a, current_a, old_a, bound)
